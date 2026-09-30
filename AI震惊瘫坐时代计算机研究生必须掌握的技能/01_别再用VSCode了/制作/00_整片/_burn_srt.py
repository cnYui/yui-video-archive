# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
src = here / "整片_无字幕_v2_出镜版.mp4"
srt = here / "别再用VSCode了_v2_双语字幕.srt"
out = here / "整片_双语字幕_v2_出镜版.mp4"
font_dir = str(Path(r"D:\大疆\AI科普\素材\字体").as_posix())

# Windows ffmpeg subtitles filter 需要把路径里的冒号和反斜杠转义
def ffesc(p):
    return str(Path(p).resolve()).replace("\\", "/").replace(":", r"\:")

vf = (
    f"subtitles='{ffesc(srt)}':fontsdir='{ffesc(font_dir)}':"
    "force_style='FontName=Noto Sans SC,FontSize=28,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,"
    "Outline=2,Shadow=1,Alignment=2,MarginV=40'"
)

cmd = [
    "ffmpeg", "-v", "error", "-y",
    "-i", str(src),
    "-vf", vf,
    "-filter_threads", "1",
    "-c:v", "libx264", "-crf", "16", "-preset", "medium",
    "-c:a", "copy",
    str(out),
]
print("烧录字幕中…")
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if r.returncode != 0:
    print("STDERR:", r.stderr[-3000:])
else:
    sz = out.stat().st_size / 1e6
    print(f"ok -> {out.name}  {sz:.0f} MB")
