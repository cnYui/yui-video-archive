# -*- coding: utf-8 -*-
"""量字幕区（画面下方居中）每 0.5 秒的平均亮度 → brightness.json（[[秒, 亮度 0–255], …]），给 make_ass.py 判断哪里要加半透明黑底。

  python brightness.py
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parents[1] / "素材" / "fHEIw5CcN5U_1080p_video-only.mp4"


def main():
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(VIDEO), "-an", "-vf",
                        "fps=2,crop=1300:240:310:780,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    t, out = None, []
    for ln in p.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", ln)
        if m:
            t = float(m.group(1))
        m = re.search(r"YAVG=([\d.]+)", ln)
        if m and t is not None:
            out.append([round(t, 2), round(float(m.group(1)), 1)])
    (HERE / "brightness.json").write_text(json.dumps(out), encoding="utf-8")
    ys = sorted(y for _, y in out)
    q = lambda f: ys[int(f * (len(ys) - 1))]
    print(f"{len(out)} 个采样；亮度分位：10% {q(.1)}  50% {q(.5)}  80% {q(.8)}  90% {q(.9)}  最大 {ys[-1]}")
    hi = [t for t, y in out if y > 140]
    print("亮度 > 140 的时刻（秒）：", " ".join(f"{t:.0f}" for t in hi[:80]))


if __name__ == "__main__":
    main()
