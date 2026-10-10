# -*- coding: utf-8 -*-
"""整片_v1.mp4 → 加悠一片头片尾 → 成片 + 手机预览 + 响度报告 + 三份 SRT。

  python finish.py              加片头片尾（正片不重编码，只拼接）、出手机预览、报响度、导出 SRT
  python finish.py --srt-only   只导出 SRT（不渲染；时间 = timeline.json 的 subs 显示区间 + 片头 INTRO_SEC）

输出名取台本 录制稿.json 的 "slug"：<slug>_成片.mp4 / <slug>_手机预览.mp4 / <slug>_双语字幕.srt / _中文字幕.srt / _英文字幕.srt。
片尾清单用 outro.json（按规矩每期都要用户确认）。SRT 内容和烧进画面的字幕一致，时间只对得上加完片头片尾的成片
（B 站投稿页的字幕上传、YouTube 都可以直接用；烧进画面的那份是主要的）。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from common import EP, HERE, INTRO_SEC

sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
import bilingual_std as B  # noqa: E402

SLUG = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["slug"]
SRC = HERE / "整片_v1.mp4"
OUT = EP / f"{SLUG}_成片.mp4"
PREV = EP / f"{SLUG}_手机预览.mp4"
ADD = Path(r"D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py")


def export_srt(intro):
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    rows = [(x["a"] + intro, x["b"] + intro, (x["who"] + "：" if x.get("who") else "") + x["zh"], x["en"]) for x in T["subs"]]
    B.write_srts(str(EP / SLUG), rows)
    print(f"三份 SRT：{EP / SLUG}_双语字幕.srt / _中文字幕.srt / _英文字幕.srt（{len(rows)} 条，时间含片头 {intro:.2f} s）")


def main():
    if "--srt-only" in sys.argv:
        export_srt(INTRO_SEC)
        return
    r = subprocess.run([sys.executable, str(ADD), str(SRC), "-o", str(OUT), "--outro-data", str(HERE / "outro.json")], check=True, capture_output=True, text=True)
    print(r.stdout.strip())
    m = re.search(r"intro: ([0-9.]+)s rendered", r.stdout)
    export_srt(float(m.group(1)) if m else INTRO_SEC)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT), "-vf", "scale=1560:720:flags=lanczos", "-c:v", "libx264", "-crf", "27", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(PREV)], check=True)
    for p in (OUT, PREV):
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True).stdout)
        err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-vn", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
        i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]
        lra = re.findall(r"LRA:\s+([\d.]+) LU", err)[-1]
        tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]
        print(f"{p.name}: {dur:.2f} s，{p.stat().st_size / 1e6:.1f} MB，{i} LUFS，LRA {lra}，真峰值 {tp} dBFS")


if __name__ == "__main__":
    main()
