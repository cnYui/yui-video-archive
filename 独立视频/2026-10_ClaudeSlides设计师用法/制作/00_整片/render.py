# -*- coding: utf-8 -*-
"""把 bilingual.ass 烧进画面：成片_无字幕.mp4 → 成片_中英字幕.mp4（画面重编码 crf 18，声音原样复制；原片 1920×1080、24 fps、H.264 + AAC）。

  python render.py            # 全片
  python render.py 20 30      # 只出 20–30 秒这一段预览到 preview.mp4

必须在本目录运行（subtitles 滤镜的路径在 Windows 上带盘符会被冒号弄坏，所以用相对路径：bilingual.ass、fonts/）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]


def main():
    vf = "subtitles=bilingual.ass:fontsdir=fonts"
    src = EP / "成片_无字幕.mp4"
    if len(sys.argv) == 3:
        ss, to = sys.argv[1], sys.argv[2]
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", ss, "-to", to, "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               "-pix_fmt", "yuv420p", "-c:a", "copy", str(HERE / "preview.mp4")]
    else:
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "copy", "-movflags", "+faststart", str(EP / "成片_中英字幕.mp4")]
    subprocess.run(cmd, cwd=HERE, check=True)
    print("done")


if __name__ == "__main__":
    main()
