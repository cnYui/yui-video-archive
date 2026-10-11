# -*- coding: utf-8 -*-
r"""列出十期的成片：路径 / 时长 / 分辨率 / 大小 / 响度（ffmpeg ebur128）/ 手机预览和 SRT 在不在。

  python list_outputs.py            表格（markdown）
  python list_outputs.py --no-lufs  不量响度（快）
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT  # noqa: E402


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration,size",
                        "-of", "json", str(p)], capture_output=True, text=True, encoding="utf-8")
    j = json.loads(r.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return float(j["format"]["duration"]), int(j["format"]["size"]), v["width"], v["height"], v["r_frame_rate"], any(s["codec_type"] == "audio" for s in j["streams"])


def lufs(p):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (m[-1] if m else "?"), (tp[-1] if tp else "?")


def main():
    want_lufs = "--no-lufs" not in sys.argv
    print("| 期 | 成片 | 时长 | 画面 | 大小 | 响度 / 峰值 | 手机预览 | SRT |")
    print("|---|---|---|---|---|---|---|---|")
    bad = 0
    for n in sorted(EPISODES):
        d = EPISODES[n]
        ep = EP_ROOT / d["folder"]
        mp4 = ep / f"{d['slug']}_成片.mp4"
        if not mp4.exists():
            print(f"| {n} | **没有成片**：{mp4.name} | | | | | | |")
            bad += 1
            continue
        dur, size, w, h, fps, has_a = probe(mp4)
        lu = tp = "-"
        if want_lufs:
            lu, tp = lufs(mp4)
        prev = "有" if (ep / f"{d['slug']}_手机预览.mp4").exists() else "无"
        srts = sum(1 for _ in ep.glob(f"{d['slug']}*.srt"))
        print(f"| {n} | `{mp4.relative_to(EP_ROOT.parent)}` | {dur:.1f} s | {w}×{h} {fps}{'' if has_a else ' 无音轨'} | {size / 2**20:.1f} MB | {lu} LUFS / {tp} dBFS | {prev} | {srts} |")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
