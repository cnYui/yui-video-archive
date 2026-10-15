# -*- coding: utf-8 -*-
"""整片_v1.mp4 → 加悠一片头片尾 → 成片 + 手机预览 + 响度报告。

  python finish.py

片尾清单用 outro.json（按规矩每期都要用户确认）；add_to_video.py 不重编码正片，只拼接。
"""
import re
import subprocess
import sys
from pathlib import Path

from common import EP, HERE

SRC = HERE / "整片_v1.mp4"
OUT = EP / "ClaudeFable5.5模型介绍_成片.mp4"
PREV = EP / "ClaudeFable5.5模型介绍_手机预览.mp4"
ADD = Path(r"D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py")


def main():
    subprocess.run([sys.executable, str(ADD), str(SRC), "-o", str(OUT), "--outro-data", str(HERE / "outro.json")], check=True)
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
