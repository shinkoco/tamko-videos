"""Full QA: render every format (some with Tamko, some with the Christmas theme) and check each video.
Usage: python3 qa.py OUTDIR"""
import os, sys, json, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "/tmp/qa")
os.makedirs(OUT, exist_ok=True)
JOBS = [("dup", {"seed": 1}), ("battle", {"seed": 2}, "christmas"), ("race", {"seed": 3, "tamko": True}), ("rings", {"seed": 4}),
        ("survival", {"seed": 5, "tamko": True}), ("ducks", {"seed": 6, "tamko": True}), ("rockets", {"seed": 7}), ("cars", {"seed": 8}),
        ("rps", {"seed": 9}), ("meteors", {"seed": 10, "tamko": True}), ("grow", {"seed": 11}), ("dominoes", {"seed": 12, "shape": "snake"}),
        ("vision", {"seed": 13}), ("escape", {"seed": 14, "rule": "freeze"}), ("press", {"seed": 15}),
        ("melody", {"seed": 16, "song": "Jingle Bells"}, "christmas")]
def run(job):
    fmt, p = job[0], job[1]; theme = job[2] if len(job) > 2 else "default"
    env = dict(os.environ, TP=json.dumps(p), TOUT="qa_" + fmt, OUTDIR=OUT, TAMKO_THEME=theme)
    r = subprocess.run([sys.executable, os.path.join(HERE, "formats", fmt + ".py")], env=env, capture_output=True, text=True, timeout=500)
    if r.returncode: return fmt, "FAIL", r.stderr.strip().splitlines()[-1][:200]
    f = os.path.join(OUT, f"qa_{fmt}.mp4")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", f], capture_output=True, text=True)
    info = json.loads(probe.stdout or "{}"); dur = float(info.get("format", {}).get("duration", 0))
    kinds = {s["codec_type"] for s in info.get("streams", [])}
    ok = dur >= 60 and dur <= 180 and kinds == {"video", "audio"}
    return fmt, "OK" if ok else "BAD", f"{dur:.1f}s streams={sorted(kinds)} theme={theme}"
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(run, JOBS))
for r in sorted(res): print(*r)
print("ALL GOOD" if all(r[1] == "OK" for r in res) else "PROBLEMS FOUND")
