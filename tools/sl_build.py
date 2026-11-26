"""Append the Acts and Statutory Instruments of Saint Lucia, as printed by the National Printing Corporation
(npc.govt.lc), to the saint-lucia-law repository as git fast-import commits on main.

python -I tools/sl_build.py <repo> [--limit N] [--dry]
Source: state/fetched.json + pdf/ (fetch_runner.py). The PDF text layer only; no OCR is run here.
Layout (STRUCTURE.md): acts/<year>/<NNN>-<slug>/ and statutory-instruments/<year>/<NNN>-<slug>/, one file per
section. One commit per instrument as enacted or made, dated noon America/St_Lucia on its in-force day.
Instruments already committed (Source or Source-sha256 trailer on main) are skipped."""
import json, os, re, subprocess, sys, datetime, unicodedata, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date(2026, 11, 26)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())}); MONTHS["sept"] = 9
HELD = []
EMAIL = "saint-lucia-law@lexifina.com"


def slug(s, n=60):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"^the\s+", "", s.strip())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].strip("-") or "untitled"


def numkey(n):
    m = re.match(r"(\d+)([A-Z]*)", n)
    return (int(m.group(1)), m.group(2))


SEC = re.compile(r"^((?:\d{1,4})[A-Z]{0,2})\s?\.\s*(?:[-—–]+\s*)?(?=[(A-Z\"'“‘\d*])", re.M)
SCHED = re.compile(r"^[^\n]{0,20}?\b(?:(?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+)?"
                   r"SCHEDULE(?:\s+[0-9IVX]+)?(?:\s+TO\s+THE\s+[A-Za-z ]+)?\s*\.?\s*$", re.M)
HEADING_LINE = re.compile(r"^[A-Z(][^\n]{0,90}$")


def move_headings(files):
    """Marginal headings and Part/Division headings printed above a section belong to it, not to the one before."""
    out = [list(f) for f in files]
    for i in range(1, len(out)):
        if not out[i][0].startswith("section-") or not out[i - 1][0].startswith("section-"):
            continue
        lines = out[i - 1][1].rstrip().split("\n")
        k = len(lines)
        while k > 1 and len(lines) - k < 5:
            ln = lines[k - 1].strip()
            if not ln or not HEADING_LINE.match(ln) or re.search(r"[.;:,]$", ln) or len(ln.split()) > 12:
                break
            k -= 1
        if k < len(lines) and k > 1 and re.search(r"[.;:—–\-”’\")\]]\s*$", lines[k - 1].strip() or "."):
            moved = "\n".join(x.strip() for x in lines[k:] if x.strip())
            out[i - 1][1] = "\n".join(lines[:k]).rstrip()
            out[i][1] = moved + "\n" + out[i][1]
    return [tuple(f) for f in out]


def split_sections(text):
    ms = list(SEC.finditer(text))
    starts = [i for i, m in enumerate(ms) if m.group(1) == "1"]
    if not starts:
        return None
    cands = []
    for s in starts:
        seq, last = [ms[s]], numkey("1")
        for m in ms[s + 1:]:
            k = numkey(m.group(1))
            if k > last and k[0] <= last[0] + 3:
                seq.append(m); last = k
        cands.append(seq)
    top = max(len(c) for c in cands)

    def body(c):
        ends = [m.start() for m in c[1:]] + [len(text)]
        return sum(1 for m, e in zip(c, ends) if e - m.start() >= 120)

    seq = max((c for c in cands if len(c) >= 0.6 * top),
              key=lambda c: (body(c), c[-1].start() - c[0].start(), len(c)))
    if len(seq) < 2:
        return None
    files = []
    head = text[:seq[0].start()].strip()
    if head:
        files.append(("front-matter.md", head))
    end_body = len(text)
    sm = [m for m in SCHED.finditer(text) if m.start() > seq[-1].start()]
    if sm:
        end_body = sm[0].start()
    seen = set()
    for i, m in enumerate(seq):
        e = seq[i + 1].start() if i + 1 < len(seq) else end_body
        n = m.group(1)
        name = f"section-{int(re.match(r'[0-9]+', n).group()):03d}{re.sub(r'^[0-9]+', '', n).lower()}.md"
        if name in seen:
            return None
        seen.add(name)
        files.append((name, text[m.start():e].strip()))
    for j, s in enumerate(sm):
        e = sm[j + 1].start() if j + 1 < len(sm) else len(text)
        files.append((f"schedule-{j + 1:02d}.md", text[s.start():e].strip()))
    files = move_headings(files)
    return files


DAY = r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:day\s+)?(?:of\s+)?([A-Za-z]{3,9})\.?,?\s+(\d{4})"
DAY_US = r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})"


def mkdate(dd, mm, yy):
    mm = mm.lower()
    if mm not in MONTHS:
        return None
    try:
        return datetime.date(int(yy), MONTHS[mm], int(dd))
    except ValueError:
        return None


def find(pat, t, lim=8000, us=False):
    for m in re.finditer(pat, t[:lim], re.I | re.S):
        g = m.groups()[-3:]
        d = mkdate(g[1], g[0], g[2]) if us else mkdate(*g)
        if d:
            return d
    return None


def dating(text, year, is_act):
    ok = lambda d: d and (year is None or -1 <= d.year - year <= 3) and d <= TODAY
    # the enacting formula (Acts) or the power recital (instruments): the head of the text ends there and the body begins
    e = re.search(r"BE\s+IT\s+ENACTED|In\s+exercise\s+of\s+the\s+power|I\s+Assent", text, re.I)
    e = e.start() if e else 8000
    head_end = e + 1500
    body = text[e:e + 15000]
    appointed = re.search(r"(?:come|comes)\s+into\s+(?:operation|force)\s+on\s+(?:such\s+)?(?:a\s+)?(?:date|day)\s+(?:to\s+be\s+)?"
                          r"(?:fixed|appointed|as\s+the|which|that)", body, re.I)
    c = find(r"(?:come|comes|came|shall\s+be\s+deemed\s+to\s+have\s+come)\s+into\s+(?:operation|force|effect)\s+on\s+(?:the\s+)?" + DAY,
             body, 15000)
    if ok(c):
        return c, "commencement day stated in the text"
    b = find(r"\[\s*" + DAY + r"\s*\]", text, head_end)
    if ok(b):
        why = "date printed in square brackets under the long title (the day of publication in the Gazette)"
        if appointed:
            why += "; the text commences on a day to be appointed by Order, which is not recorded here"
        return b, why
    g = find(r"(?:Gazetted|Published\s+in\s+the\s+(?:Official\s+)?Gazette)\D{0,40}?" + DAY, text, head_end)
    if ok(g):
        why = "day of publication in the Gazette printed in the text"
        if appointed:
            why += "; the text commences on a day to be appointed by Order, which is not recorded here"
        return g, why
    if is_act:
        a = find(r"I\s+Assent\W.{0,300}?" + DAY, text, head_end + 400) or \
            find(r"I\s+Assent\W.{0,300}?" + DAY_US, text, head_end + 400, us=True)
        if ok(a):
            return a, "day of the Governor-General's assent printed at the head of the Act (no commencement or Gazette day found)"
        p = find(r"Passed\s+(?:in\s+)?the\s+(?:House\s+of\s+Assembly|Senate).{0,80}?" + DAY, text, 900000)
        if ok(p):
            return p, "day the Act passed Parliament, printed at its end (no commencement, Gazette or assent day found)"
    mde = find(r"(?:MADE|Dated)\s+(?:by.{0,200}?)?(?:this\s+)?" + DAY, text, 900000)
    if ok(mde):
        return mde, "day the instrument was made or dated, as printed in it (no commencement or Gazette day found)"
    return None, None


def ident(r):
    t = r["title"]
    m = re.search(r"(?i)(?:\bNo\.?|\bS\.\s?I\.|\bAct)\s*(\d{1,3})\s*(?:of\s*)?((?:19|20)\d\d)", t)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def demoji(t):
    try:
        return t.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return t


def short_title(title):
    t = re.sub(r"\s+", " ", demoji(title)).strip()
    t = re.sub(r"(?i)\s*-?\s*Price\s*\$?\s*[\d.,]+\s*$", "", t)
    t = re.sub(r"(?i)^(?:(?:Act|S\.?\s*I\.?|Statutory Instrument)\s*(?:No\.?)?|No\.?)\s*\d{1,3}\s*(?:of\s*)?(?:(?:19|20)\d\d)?\s*[-–:]?\s*", "", t)
    t = re.sub(r"(?i)\s*\((?:\d+|copy)\)\s*$", "", t).strip(" ,-–")
    t = re.sub(r"(?i)^The\s+", "", t)
    return t or title


HEAD = re.compile(r"^(?:SAINT LUCIA|\d{1,4}|[-–—. ]*\d{1,4}[-–—. ]*|No\.\s*\d+\s*\].*|.*\[\s*(?:19|20)\d\d\s*)$", re.I)


def clean_pdf_text(fn):
    import pymupdf
    d = pymupdf.open(fn)
    pages = [[ln.rstrip() for ln in p.get_text().replace("\r", "").split("\n")] for p in d]
    freq = collections.Counter()
    for pg in pages:
        for ln in set(x.strip() for x in pg[:5] + pg[-3:] if x.strip()):
            freq[ln] += 1
    n = len(pages)
    rh = {ln for ln, c in freq.items() if n >= 3 and c >= 3 and c >= 0.25 * n and len(ln) < 90}
    out = []
    for pi, pg in enumerate(pages):
        keep = []
        for i, ln in enumerate(pg):
            s = ln.strip()
            edge = i < 4 or i >= len(pg) - 3
            if edge and pi > 0 and (s in rh or re.fullmatch(r"\d{1,4}", s) or re.match(r"No\.\s*\d+\s*\]", s)
                                    or re.search(r"\[\s*(?:19|20)\d\d\s*$", s)):
                continue
            keep.append(ln)
        out.append("\n".join(keep))
    t = "\n".join(out)
    nrep = t.count("�")
    # glyphs the text layer does not map: an apostrophe between letters, a dash after a section number
    t = re.sub(r"(?<=[A-Za-z])�(?=[A-Za-z])", "’", t)
    t = re.sub(r"(?:(?<=\d\.)|(?<=\d[A-Z]\.))\s?�", "—", t)
    t = re.sub(r"(?<=[a-z,;:)])\s�\s?(?=[A-Za-z(\n])", " —", t)
    t = re.sub(r"(?<=\))�(?=\()", "—", t)
    t = t.replace("\t", " ")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    meta = " ".join(str(v) for v in (d.metadata or {}).values() if v)
    return t.strip() + "\n", d.page_count, meta, nrep


OCR_META = re.compile(r"(?i)paper capture|abbyy|finereader|omnipage|readiris|\bocr\b|scan|capture|clearscan|tesseract")


def git_when(d, seq):
    t = int(datetime.datetime(d.year, d.month, d.day, 16, 0, tzinfo=datetime.timezone.utc).timestamp())
    return f"{t} -0400"


def done_sources(repo):
    r = subprocess.run(["git", "-C", repo, "log", "--format=%(trailers:key=Source,key=Source-sha256,valueonly,separator=%x0A)",
                        "main"], capture_output=True, text=True, encoding="utf-8")
    return {x.strip() for x in r.stdout.split("\n") if x.strip()}


COMMENCE = {}


def commencements(idx):
    """Whole-Act commencement days appointed by statutory instruments whose title says Commencement."""
    import pymupdf
    for u, r in idx.items():
        if r.get("kind") != "si" or not r.get("file") or not re.search(r"(?i)commencement", r["title"]) \
                or re.search(r"(?i)revocation", r["title"]):
            continue
        num, year = ident(r)
        try:
            t = "".join(p.get_text() for p in pymupdf.open(os.path.join(ROOT, "pdf", r["file"]))[:3])
        except Exception:
            continue
        t = re.sub(r"\s+", " ", t)
        ms = list(re.finditer(r"(?:The\s+)?([A-Z][^.]{3,150}?)\s*,?\s*No\.?\s*(\d{1,3})\s+of\s+((?:19|20)\d\d)\s*,?\s*(?:shall\s+)?"
                              r"(?:comes?|come)\s+into\s+(?:force|operation)\s+on\s+(?:the\s+)?" + DAY, t))
        if len(ms) != 1 or re.search(r"(?i)\bsections?\b|\bparts?\b|except|provisions", ms[0].group(0)):
            continue
        m = ms[0]
        d = mkdate(m.group(4), m.group(5), m.group(6))
        if d:
            COMMENCE.setdefault((int(m.group(2)), int(m.group(3))),
                                (d, f"S.I. No. {num} of {year} ({short_title(r['title'])})"))


def plan(have, used_dirs, limit):
    rows = []
    idx = json.load(open(os.path.join(ROOT, "state", "fetched.json"), encoding="utf-8"))
    commencements(idx)
    groups = collections.defaultdict(list)
    for url, r in idx.items():
        title = re.sub(r"\s+", " ", r["title"]).strip()
        if r.get("status") != 200 or not r.get("file"):
            HELD.append((url, title, f"not fetched (HTTP {r.get('status')}, {r.get('bytes')} bytes)")); continue
        if re.search(r"(?i)\bbill\b", title) and not re.search(r"\bAct\b", title):
            continue
        num, year = ident(r)
        key = (r["kind"], year, num) if num else ("sha", r["sha256"])
        groups[key].append((url, r, title, num, year))
    made = 0
    pri = lambda k, it: (0 if re.search(r"(?i)\bcriminal code\b", it[0][2]) and not re.search(r"(?i)amend", it[0][2]) else 1,
                         0 if k[0] == "act" else 1)
    for key, items in sorted(groups.items(), key=lambda kv: pri(kv[0], kv[1])):
        items.sort(key=lambda x: (x[1].get("text_chars") or 0, -x[1]["id"]), reverse=True)
        url, r, title, num, year = items[0]
        for u2, r2, t2, _, _ in items[1:]:
            if u2 not in have and r2["sha256"] not in have:
                HELD.append((u2, t2, "a second copy of the same instrument (the one with the fuller text layer is used)"))
        if url in have or r["sha256"] in have:
            continue
        pages = max(1, r.get("pages") or 1)
        if (r.get("text_chars") or 0) < 60 * pages:
            HELD.append((url, title, f"no text layer ({r.get('pages')} pages, {r.get('text_chars')} characters): page scans, not OCRed")); continue
        if (r.get("word_q") or 0) < 0.8:
            HELD.append((url, title, f"text layer unreadable (word score {r.get('word_q')})")); continue
        if limit and made >= limit:
            continue
        row = make_row(url, r, title, num, year, used_dirs)
        if row:
            rows.append(row); made += 1
    return rows


def make_row(url, r, title, num, year, used_dirs):
    kind = r["kind"]
    text, npages, meta, nrep = clean_pdf_text(os.path.join(ROOT, "pdf", r["file"]))
    ocr = bool(OCR_META.search(meta)) or (r.get("scanned_pages") or 0) > 0.5 * max(1, min(6, npages))
    tsrc = ("publisher OCR (the publisher's text layer over page scans, as served; no OCR was run here)" if ocr
            else "PDF text layer")
    short = short_title(title)
    yr = year or int(r["listing"].rstrip("/").rsplit("/", 1)[-1])
    d, basis = dating(text, yr, kind == "act")
    if kind == "act" and num and (num, year) in COMMENCE and basis != "commencement day stated in the text":
        cd, si = COMMENCE[(num, year)]
        if cd <= TODAY:
            d, basis = cd, f"day appointed for the whole Act by {si}"
    if d is None:
        HELD.append((url, title, "no commencement, Gazette, assent or making day found in the text layer")); return None
    if d > TODAY:
        HELD.append((url, title, f"in force {d}, after the build day")); return None
    top = "acts" if kind == "act" else "statutory-instruments"
    y = yr or d.year
    folder = f"{top}/{y}/" + (f"{num:03d}-" if num else "") + slug(short)
    files = split_sections(text) or [("text.md", text)]
    if kind == "act":
        author = f"Act No. {num} of {year}" if num else short
        email = f"act-{year}-{num}@npc.govt.lc.invalid" if num else f"{slug(short, 40)}@npc.govt.lc.invalid"
    else:
        author = f"S.I. No. {num} of {year}" if num else short
        email = f"si-{year}-{num}@npc.govt.lc.invalid" if num else f"{slug(short, 40)}@npc.govt.lc.invalid"
    subject = f"{short}: as {'enacted' if kind == 'act' else 'made'}, in force {d.isoformat()}"
    lines = [f"{short} ({author}), as printed by the National Printing Corporation, the Government Printer of Saint Lucia."]
    lines.append(f"{npages} pages. The text is the PDF's text layer as served; marginal notes and headings sit where the "
                 "layer places them" + (" (a text layer the publisher made from page scans, with its recognition errors)."
                                         if ocr else "."))
    if nrep:
        lines.append(f"{nrep} glyphs the text layer leaves unmapped: between letters read as an apostrophe, after a "
                     "section number as a dash; any others are left as U+FFFD.")
    lines.append("One file: no section numbering was found to split on." if len(files) == 1 else
                 f"{len(files)} files: the front matter, one per section and each schedule.")
    if folder in used_dirs:
        base, j = folder, 2
        while folder in used_dirs:
            folder = f"{base}-{j}"; j += 1
    used_dirs.add(folder)
    core = 0 if re.search(r"(?i)\bcriminal code\b", title) and not re.search(r"(?i)amend", title) else 1
    trailers = [("In-force", d.isoformat()), ("In-force-basis", basis), ("Text-source", tsrc),
                ("Source", url), ("Source-sha256", r["sha256"]), ("Source-listing", r["listing"])]
    return dict(order=core, date=d, folder=folder, files=files, author=author, email=email,
                kind="enactment" if kind == "act" else "instrument", subject=subject, lines=lines, trailers=trailers)


def main():
    repo = sys.argv[1]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    have = done_sources(repo)
    ls = subprocess.run(["git", "-C", repo, "ls-tree", "-d", "--name-only", "-r", "main"], capture_output=True, text=True).stdout
    used = set(ls.split())
    rows = plan(have, used, limit)
    rows.sort(key=lambda r: (r["order"], r["date"], r["folder"]))
    json.dump(HELD, open(os.path.join(ROOT, "held.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if "--dry" in sys.argv:
        c = collections.Counter(r["trailers"][1][1][:60] for r in rows)
        for k, v in c.most_common():
            print(v, k)
        print(len(rows), "rows;", len(HELD), "held", collections.Counter(h[2][:25] for h in HELD))
        for r in rows[:: max(1, len(rows) // 25)]:
            print(r["date"], r["folder"], len(r["files"]), r["subject"][:60])
        return
    if not rows:
        print("nothing new"); return
    parent = subprocess.run(["git", "-C", repo, "rev-parse", "main"], capture_output=True, text=True).stdout.strip()
    p = subprocess.Popen(["git", "-C", repo, "fast-import", "--quiet", "--done"], stdin=subprocess.PIPE)
    w = p.stdin

    def data(b):
        w.write(f"data {len(b)}\n".encode()); w.write(b); w.write(b"\n")
    for seq, r in enumerate(rows):
        msg = r["subject"] + "\n\n" + "\n".join(r["lines"]) + "\n\n" + f"Kind: {r['kind']}\n" + \
            "".join(f"{k}: {v}\n" for k, v in r["trailers"])
        when = git_when(r["date"], seq)
        w.write(b"commit refs/heads/main\n")
        w.write(f"author {r['author']} <{r['email']}> {when}\ncommitter Lexifina <{EMAIL}> {when}\n".encode("utf-8"))
        data(msg.encode("utf-8"))
        if seq == 0:
            w.write(f"from {parent}\n".encode())
        for name, txt in r["files"]:
            w.write(f"M 100644 inline {r['folder']}/{name}\n".encode("utf-8")); data((txt.strip() + "\n").encode("utf-8"))
        w.write(b"\n")
    w.write(b"done\n"); w.close(); p.wait()
    print(f"committed {len(rows)}; held {len(HELD)}; fast-import rc {p.returncode}")


if __name__ == "__main__":
    main()
