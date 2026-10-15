# -*- coding: utf-8 -*-
"""整片_v1.mp4 → 成片 + 手机预览 + 响度报告 + 三份 SRT。短视频**不加悠一片头片尾**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”）。

  python finish.py              成片（不重编码，只把 moov 挪到前面）、手机预览（540×1170）、报响度、导出 SRT
  python finish.py --srt-only   只导出 SRT（时间 = timeline.json 的 subs 显示区间，没有片头偏移）

输出名取台本 录制稿.json 的 "slug"：<slug>_成片.mp4 / <slug>_手机预览.mp4 / <slug>_双语字幕.srt / _中文字幕.srt / _英文字幕.srt。
烧进画面的字幕是主要的；SRT 给 B 站 / 抖音的字幕上传和存档用。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from common import EP, HERE

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

SLUG = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["slug"]
SRC = HERE / "整片_v1.mp4"
OUT = EP / f"{SLUG}_成片.mp4"
PREV = EP / f"{SLUG}_手机预览.mp4"


def export_srt():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    rows = [(x["a"], x["b"], (x["who"] + "：" if x.get("who") else "") + x["zh"], x["en"]) for x in T["subs"]]
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
        last = lambda pat: (re.findall(pat, err) or ["—"])[-1]          # 整条静音（测试）时峰值是 -inf，取不到就写 —
        i, lra, tp = last(r"I:\s+(-?[\d.]+|-inf) LUFS"), last(r"LRA:\s+([\d.]+) LU"), last(r"Peak:\s+(-?[\d.]+|-inf) dBFS")
        print(f"{p.name}: {info[0]}×{info[1]}，{float(info[-1]):.2f} s，{p.stat().st_size / 1e6:.1f} MB，{i} LUFS，LRA {lra}，真峰值 {tp} dBFS")


if __name__ == "__main__":
    main()
