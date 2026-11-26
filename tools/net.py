"""Adaptive, polite fetcher (one host at a time per process).

Starts at 1 request in flight, ~1 s between request starts. After every 40 clean responses in a row it allows one more
request in flight (up to 5) and shortens the gap (down to 0.3 s). Any timeout or 5xx drops it back to 1 in flight with a
2 s gap and pauses; 429/503 pause with doubling backoff. 403 and challenge pages are returned to the caller, which stops."""
import time, threading, urllib.request, urllib.parse, urllib.error

UA = "Mozilla/5.0 (compatible; lexifina-law-archive)"
GAPS = [1.0, 0.8, 0.6, 0.45, 0.3]
_cv = threading.Condition()
state = {"limit": 1, "inflight": 0, "gap": 1.0, "last": 0.0, "pause": 0.0, "clean": 0, "backoff": 60}
_log = [None]


def set_logger(f):
    _log[0] = f


def _say(m):
    if _log[0]:
        _log[0](m)


def _acquire():
    with _cv:
        while state["inflight"] >= state["limit"]:
            _cv.wait()
        state["inflight"] += 1
        while True:
            now = time.time()
            d = max(state["last"] + state["gap"], state["pause"]) - now
            if d <= 0:
                break
            _cv.wait(d)
        state["last"] = time.time()


def _release(ok, hard=False):
    with _cv:
        state["inflight"] -= 1
        if ok:
            state["clean"] += 1
            if state["clean"] >= 40 and state["limit"] < 5:
                state["limit"] += 1; state["clean"] = 0
                state["gap"] = GAPS[state["limit"] - 1]; state["backoff"] = 60
                _say(f"rate up: {state['limit']} in flight, gap {state['gap']}s")
        else:
            state["clean"] = 0
            if hard:
                state["limit"] = 1; state["gap"] = 2.0
                state["pause"] = time.time() + state["backoff"]
                _say(f"rate down: 1 in flight, gap 2s, pause {state['backoff']}s")
                state["backoff"] = min(900, state["backoff"] * 2)
        _cv.notify_all()


def fetch(url, tries=4, timeout=180):
    st, b, h = -1, b"", {}
    for t in range(tries):
        _acquire()
        ok = hard = False
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                st, b, h = r.status, r.read(), dict(r.headers)
            ok = True
        except urllib.error.HTTPError as e:
            st, b, h = e.code, b"", {}
            hard = e.code == 429 or e.code >= 500
            ok = not hard
        except Exception:
            st, b, h = -1, b"", {}
            hard = True
        _release(ok, hard)
        if not hard:
            return st, b, h
    return st, b, h


def blocked(st, b):
    head = b[:3000].lower()
    return st in (403, 429) or b"just a moment" in head or b"captcha" in head or b"cf-challenge" in head
