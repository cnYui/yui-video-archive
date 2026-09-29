"""Download recovered history URLs, identify which chunk each belongs to, score every take, pick the best.

usage: python select_takes.py urls_hist.txt
Outputs raw/Cxx_vN.mp3 (new takes), raw/asr_cache.json, selection.json {chunk: {file, score, duration}}.
"""
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
RAW = HERE / "raw"
from fetch_check import norm  # same normalisation as the per-chunk checker

chunks = json.loads((HERE / "chunks.json").read_text(encoding="utf-8"))
refs = {c["chunk"]: norm(c["text"].replace(" ", "")) for c in chunks}
cache_path = RAW / "asr_cache.json"
cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")


def asr(path):
    h = hashlib.md5(path.read_bytes()).hexdigest()
    if h not in cache:
        segs, _ = model.transcribe(str(path), language="zh", initial_prompt="以下是普通话的句子。")
        cache[h] = "".join(s.text for s in segs)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[h]


def score(ref, hyp):
    return difflib.SequenceMatcher(None, ref, norm(hyp)).ratio()


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode().strip())


# 1) recovered history URLs -> identify chunk
if len(sys.argv) > 1:
    hist = RAW / "hist"
    hist.mkdir(exist_ok=True)
    known = {hashlib.md5(p.read_bytes()).hexdigest() for p in RAW.glob("C*_v*.mp3")}
    for url in Path(sys.argv[1]).read_text(encoding="utf-8").split():
        name = url.split("/")[-1].split("?")[0]
        dst = hist / name
        if not dst.exists():
            subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", str(dst), url.split("?")[0]], check=True)
        h = hashlib.md5(dst.read_bytes()).hexdigest()
        if h in known:
            print("dup of existing take:", name)
            continue
        hyp = asr(dst)
        best = max(refs, key=lambda c: score(refs[c], hyp))
        s = score(refs[best], hyp)
        if s < 0.6:
            print("UNMATCHED", name, round(s, 3), hyp[:40])
            continue
        n = 1
        while (RAW / f"{best}_v{n}.mp3").exists():
            n += 1
        dst_named = RAW / f"{best}_v{n}.mp3"
        dst_named.write_bytes(dst.read_bytes())
        known.add(h)
        print(f"{name} -> {dst_named.name} score={s:.3f}")

# 2) score every take of every chunk, pick best
selection = {}
for c in chunks:
    cid = c["chunk"]
    takes = sorted(RAW.glob(f"{cid}_v*.mp3"))
    scored = []
    for p in takes:
        hyp = asr(p)
        scored.append((score(refs[cid], hyp), p.name, duration(p), hyp))
    if not scored:
        print(cid, "NO TAKES")
        continue
    scored.sort(reverse=True)
    s, name, dur, hyp = scored[0]
    selection[cid] = dict(file=name, score=round(s, 3), duration=round(dur, 2), asr=hyp,
                          alternatives=[dict(file=n, score=round(x, 3)) for x, n, _, _ in scored[1:]])
    print(f"{cid}: best {name} score={s:.3f} dur={dur:.1f}s  (of {len(scored)})")
(HERE / "selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=1), encoding="utf-8")
