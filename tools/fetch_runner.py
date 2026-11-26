"""List and download the Acts (2003-2026) and Statutory Instruments (2001-2026) the National Printing Corporation
(npc.govt.lc, the Government Printer of Saint Lucia) publishes, through net.py (adaptive: 1 in flight at ~1 s, up to 5).

python -I tools/fetch_runner.py
Writes catalogue.json, pdf/<sha16>.pdf, state/fetched.json; appends to progress.log. Re-runnable (skips what is
recorded). Stops on 403/429/challenge or 3 unreachable in a row. Stop file: state/fetch.stop."""
import os, sys, json, time, hashlib, re, html, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import net

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "pdf"); os.makedirs(PDF, exist_ok=True)
IDX = os.path.join(ROOT, "state", "fetched.json")
CAT = os.path.join(ROOT, "catalogue.json")
LOG = os.path.join(ROOT, "progress.log")
LK = threading.Lock()


def log(m):
    with LK, open(LOG, "a", encoding="utf8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "fetch " + m + "\n")


net.set_logger(log)


def load(p, d):
    try:
        return json.load(open(p, encoding="utf8"))
    except Exception:
        return d


def save(p, obj):
    with LK:
        s = json.dumps(obj, ensure_ascii=False, indent=0)
    open(p + ".tmp", "w", encoding="utf8").write(s); os.replace(p + ".tmp", p)


WORD = re.compile(r"[A-Za-z]+")
COMMON = set("""the of and to in a be or any by for shall such as is on under this act with person may which section that
not from other an at it all made order minister where his provided court time paragraph""".split())


def textinfo(fn):
    try:
        import pymupdf
        d = pymupdf.open(fn)
        chars = scanned = words = good = 0
        sample = []
        for i, p in enumerate(d):
            t = p.get_text()
            chars += len(t.strip())
            if i < 6:  # kept lean: scans and word quality judged on the first six pages
                sample.append(t)
                for img in p.get_image_info():
                    x0, y0, x1, y1 = img["bbox"]
                    if (x1 - x0) * (y1 - y0) > 0.5 * p.rect.width * p.rect.height:
                        scanned += 1; break
        for t in sample:
            for w in WORD.findall(t):
                words += 1
                lw = w.lower()
                if lw in COMMON or (len(w) > 2 and (w.islower() or w.istitle() or w.isupper()) and re.search(r"[aeiouy]", lw)):
                    good += 1
        meta = " ".join(str(v) for v in (d.metadata or {}).values() if v)
        return d.page_count, chars, scanned, round(good / words, 3) if words else 0, meta
    except Exception:
        return 0, -1, 0, 0, ""


def listing():
    cat = load(CAT, None)
    if cat:
        return cat
    cat, seen = [], set()
    pages = [("act", y, f"https://npc.govt.lc/laws/acts/{y}") for y in range(2003, 2027)] + \
            [("si", y, f"https://npc.govt.lc/laws/si/{y}") for y in range(2001, 2027)]
    for kind, y, u in pages:
        st, b, _ = net.fetch(u)
        if net.blocked(st, b) or st != 200:
            log(f"STOP: listing {u} HTTP {st}"); sys.exit(2)
        h = b.decode("utf8", "replace")
        items = re.findall(r'href="(https://npc\.govt\.lc/laws/download/[^"]+)">([^<]*)<', h)
        for url, t in items:
            if url in seen:
                continue
            seen.add(url)
            cat.append({"id": len(cat), "kind": kind, "list_year": y, "url": url,
                        "title": re.sub(r"\s+", " ", html.unescape(t)).strip(), "listing": u})
        log(f"list {u}: {len(items)}")
    save(CAT, cat)
    return cat


def prio(e):
    t = e["title"]
    if re.search(r"(?i)\bcriminal code\b", t) and not re.search(r"(?i)amendment", t):
        return (0, 0, e["id"])
    if re.search(r"(?i)civil code|code of civil procedure|criminal procedure", t) and not re.search(r"(?i)amendment", t):
        return (0, 1, e["id"])
    return (1 if e["kind"] == "act" else 2, -e["list_year"], e["id"])


def main():
    if os.path.exists(os.path.join(ROOT, "state", "fetch.stop")):
        os.remove(os.path.join(ROOT, "state", "fetch.stop"))
    cat = listing()
    idx = load(IDX, {})
    todo = sorted([e for e in cat if e["url"] not in idx], key=prio)
    log(f"start: {len(cat)} listed, {len(todo)} to fetch, {len(idx)} recorded")
    stop = [None]; unreach = [0]; n = [0]; last = [time.time()]

    def work(e):
        if stop[0] or os.path.exists(os.path.join(ROOT, "state", "fetch.stop")):
            return
        st, b, h = net.fetch(e["url"])
        if net.blocked(st, b):
            stop[0] = f"HTTP {st} or challenge at {e['url']}"; return
        if st == -1:
            unreach[0] += 1
            if unreach[0] >= 3:
                stop[0] = "unreachable 3 times in a row"
            log(f"unreachable {e['title'][:60]}"); return
        unreach[0] = 0
        rec = {"id": e["id"], "kind": e["kind"], "title": e["title"], "status": st, "bytes": len(b),
               "listing": e["listing"], "disposition": h.get("Content-Disposition", "")}
        if st == 200 and b[:5] == b"%PDF-":
            sha = hashlib.sha256(b).hexdigest(); fn = os.path.join(PDF, sha[:16] + ".pdf")
            if not os.path.exists(fn):
                open(fn, "wb").write(b)
            pages, chars, scanned, q, meta = textinfo(fn)
            rec.update(sha256=sha, file=os.path.basename(fn), pages=pages, text_chars=chars, scanned_pages=scanned,
                       word_q=q, meta=meta[:300])
        with LK:
            idx[e["url"]] = rec
            n[0] += 1
        log(f"{n[0]}/{len(todo)} {st} {rec.get('pages')}p {rec.get('text_chars')}ch scan{rec.get('scanned_pages')} "
            f"q{rec.get('word_q')} {e['title'][:70]}")
        if time.time() - last[0] > 30:
            last[0] = time.time(); save(IDX, idx)

    with ThreadPoolExecutor(5) as ex:
        list(ex.map(work, todo))
    save(IDX, idx)
    if stop[0]:
        log("STOP: " + stop[0]); sys.exit(2)
    log("DONE fetch")


if __name__ == "__main__":
    main()
