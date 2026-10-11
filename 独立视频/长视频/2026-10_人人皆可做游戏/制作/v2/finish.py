# -*- coding: utf-8 -*-
"""finish.py —— 画面.mp4 + 混音 + 字幕 → 整片_v2.mp4（正片）→ 加悠一片头片尾 → 成片 / 手机预览 / 三份 SRT / 响度。

  python finish.py main        只出正片（烧字幕 + 混音，不含片头片尾）→ 整片_v2.mp4
  python finish.py full        正片 + 片头片尾 → 成片；再出手机预览、三份 SRT（时间含片头）

字幕用 ASS 烧（NSC800 / NSC600 两个字体放在 制作/fonts），中文 52 px + 英文 30 px，y 922 起，见 make_subs.py。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")

import bilingual_std as B  # noqa: E402
import voice  # noqa: E402

SLUG = "欢迎来到人人皆可做游戏的时代"
MAIN = ROOT / "整片_v2.mp4"
OUT = ROOT / f"{SLUG}_成片.mp4"
PREV = ROOT / f"{SLUG}_手机预览.mp4"
ADD = Path(r"D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py")


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def main_cut(with_subs=True):
    total = voice.total(voice.timeline())
    shutil.copy2(ROOT / "字幕.ass", ROOT / "subs.ass")
    vf = "ass=subs.ass:fontsdir=fonts" if with_subs else "null"
    out = MAIN if with_subs else ROOT / "整片_v2_无字幕.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", HERE / "画面.mp4", "-i", ROOT / "音轨" / "混音.wav", "-vf", vf, "-t", "%.4f" % total,
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", out], cwd=str(ROOT))
    print("正片", out)


def export_srt(intro):
    out = _subs()
    rows = [(o["da"] + intro, o["db"] + intro, o["zh"], o["en"]) for o in out]
    B.write_srts(str(ROOT / SLUG), rows)
    print("三份 SRT（含片头 %.2f s）" % intro, len(rows), "条")


def _subs():
    import make_subs
    return make_subs.build()


def loudness(p):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True).stdout)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-vn", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]
    lra = re.findall(r"LRA:\s+([\d.]+) LU", err)[-1]
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]
    print("%s: %.2f s，%.1f MB，%s LUFS，LRA %s，真峰值 %s dBFS" % (p.name, dur, p.stat().st_size / 1e6, i, lra, tp))


def full():
    outro = ROOT / "outro.json"
    r = subprocess.run([sys.executable, str(ADD), str(MAIN), "-o", str(OUT), "--outro-data", str(outro)], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    m = re.search(r"intro: ([0-9.]+)s rendered", r.stdout)
    from pack_info import intro_seconds
    intro = float(m.group(1)) if m else intro_seconds()
    export_srt(intro)
    run(["ffmpeg", "-v", "error", "-y", "-i", OUT, "-vf", "scale=1560:720:flags=lanczos", "-c:v", "libx264", "-crf", "27", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", PREV])
    for p in (OUT, PREV):
        loudness(p)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "main"
    if cmd == "main":
        main_cut(True)
    elif cmd == "nosubs":
        main_cut(False)
    elif cmd == "full":
        full()
