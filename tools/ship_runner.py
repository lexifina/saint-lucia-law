"""Every ~15 minutes: append newly fetched instruments to saint-lucia-law main in batches of 300 commits (sl_build.py),
push (fast-forward only) after each batch and verify with ls-remote. Stop: touch state/ship.stop."""
import os, sys, subprocess, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "repo")
LOG = os.path.join(ROOT, "progress.log")
NOWIN = 0x08000000
GIT = ["git", "-C", REPO, "-c", "user.name=Lexifina", "-c", "user.email=saint-lucia-law@lexifina.com"]


def log(m):
    with open(LOG, "a", encoding="utf8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "ship " + m + "\n")


def run(*a, **k):
    return subprocess.run(a, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=NOWIN, **k)


def push():
    p = run(*GIT, "push", "-q", "origin", "main:main")
    loc = run(*GIT, "rev-parse", "main").stdout.strip()
    rem = run(*GIT, "ls-remote", "origin", "refs/heads/main").stdout.split()
    ok = bool(rem) and rem[0] == loc
    log(f"push {'OK' if ok else 'MISMATCH'} {loc[:10]} {p.stderr.strip()[-200:]}")
    return ok


while True:
    if os.path.exists(os.path.join(ROOT, "state", "ship.stop")):
        log("stop file"); break
    shipped = False; r = None
    while True:
        r = run(sys.executable, "-I", os.path.join(ROOT, "tools", "sl_build.py"), REPO, "--limit", "300",
                env={**os.environ, "PYTHONIOENCODING": "utf8"})
        log("build: " + (r.stdout.strip() or r.stderr.strip()[-300:]))
        if not ("committed" in r.stdout and "fast-import rc 0" in r.stdout):
            break
        run(*GIT, "reset", "-q", "--hard", "main")
        if not push():
            log("STOP: push not confirmed"); sys.exit(3)
        shipped = True
        if "committed 300;" not in r.stdout:
            break
    src = os.path.join(ROOT, "held.json")
    dst = os.path.join(REPO, "data", "held.json")
    new = open(src, encoding="utf8").read() if os.path.exists(src) else "[]"
    old = open(dst, encoding="utf8").read() if os.path.exists(dst) else ""
    if shipped and new != old:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "w", encoding="utf8", newline="\n").write(new)
        run(*GIT, "add", "data/held.json")
        run(*GIT, "commit", "-q", "-m", "data/held.json: instruments held back (no text layer, no date, a second copy, or not fetched)")
        push()
    done = open(LOG, encoding="utf8").read()
    if "fetch DONE fetch" in done and r is not None and "nothing new" in r.stdout:
        log("all fetched and shipped"); break
    time.sleep(900)
