"""Start a runner detached: no console window, below-normal priority. python -I tools/launch.py <script> [args]"""
import os, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
out = open(os.path.join(ROOT, name + ".out"), "a")
p = subprocess.Popen([sys.executable, "-I", os.path.join(ROOT, "tools", sys.argv[1])] + sys.argv[2:], cwd=ROOT,
                     stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                     creationflags=0x08000000 | 0x00000200 | 0x00004000,
                     env={**os.environ, "PYTHONIOENCODING": "utf8"})
os.makedirs(os.path.join(ROOT, "state"), exist_ok=True)
open(os.path.join(ROOT, "state", name + ".pid"), "w").write(str(p.pid))
print(name, p.pid)
