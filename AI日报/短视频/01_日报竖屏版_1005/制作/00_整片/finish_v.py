# -*- coding: utf-8 -*-
"""整片_v1.mp4 → 成片 + 手机预览 + 响度报告 + 三份 SRT（短视频不加片头片尾，SRT 时间从 0 起，没有片头偏移）。照技能 finish.py 改的。

  python finish_v.py              成片（不重编码，只把 moov 挪到前面）、手机预览（540×1170）、报响度、导出 SRT
  python finish_v.py --srt-only   只导出 SRT
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent.parent                       # …\短视频\01_日报竖屏版_1005
SLUG = "AI每日日报_1005_竖屏版"
sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

SRC = HERE / "整片_v1.mp4"
OUT = EP / f"{SLUG}_成片.mp4"
PREV = EP / f"{SLUG}_手机预览.mp4"


def export_srt():
    T = json.loads((HERE / "tl_v.json").read_text(encoding="utf-8"))
    rows = [(x["a"], x["b"], x["zh"], x["en"]) for x in T["subs"]]
    B.write_srts(str(EP / SLUG), rows)
    print(f"三份 SRT：{EP / SLUG}_双语字幕.srt / _中文字幕.srt / _英文字幕.srt（{len(rows)} 条，没有片头偏移）")


def main():
    export_srt()
    if "--srt-only" in sys.argv:
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-c", "copy", "-movflags", "+faststart", str(OUT)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT), "-vf", "scale=540:1170:flags=lanczos", "-c:v", "libx264", "-crf", "27", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(PREV)], check=True)
    for p in (OUT, PREV):
        info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "default=nw=1:nk=1", str(p)],
                              capture_output=True, text=True).stdout.split()
        err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-vn", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        last = lambda pat: (re.findall(pat, err) or ["—"])[-1]
        i, lra, tp = last(r"I:\s+(-?[\d.]+|-inf) LUFS"), last(r"LRA:\s+([\d.]+) LU"), last(r"Peak:\s+(-?[\d.]+|-inf) dBFS")
        print(f"{p.name}: {info[0]}×{info[1]}，{float(info[-1]):.2f} s，{p.stat().st_size / 1e6:.1f} MB，{i} LUFS，LRA {lra}，真峰值 {tp} dBFS")


if __name__ == "__main__":
    main()
