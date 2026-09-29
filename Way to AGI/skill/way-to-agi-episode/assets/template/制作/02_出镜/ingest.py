# -*- coding: utf-8 -*-
"""出镜录像入库：从 SD 卡（H:\\DCIM\\DJI_001，只读）抽音频，转轻量代理视频。原片不复制、不改动。

  python ingest.py audio     → audio/<编号>.wav（48 kHz 立体声，混音用）、audio16/<编号>.wav（16 kHz 单声道，识别用）
  python ingest.py proxy     → proxy/<编号>.mp4（1280×720、30 fps、H.264，出镜框用）
编号 = DJI 文件名最后的 4 位（0155…0172，用户 2026-09-28 发来的 17 个）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(r"H:\DCIM\DJI_001")
IDS = ["0155", "0156", "0157", "0158", "0159", "0160", "0161", "0162", "0163", "0164", "0165",
       "0167", "0168", "0169", "0170", "0171", "0172"]


def src_of(i):
    m = sorted(SRC.glob(f"DJI_*_{i}_D.MP4"))
    assert len(m) == 1, (i, m)
    return m[0]


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def audio():
    (HERE / "audio").mkdir(exist_ok=True)
    (HERE / "audio16").mkdir(exist_ok=True)
    for i in IDS:
        s = src_of(i)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(HERE / "audio" / f"{i}.wav")])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(HERE / "audio16" / f"{i}.wav")])
        print(i, s.name, flush=True)


def proxy(ids=None):
    (HERE / "proxy").mkdir(exist_ok=True)
    for i in (ids or IDS):
        s = src_of(i)
        out = HERE / "proxy" / f"{i}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", str(s), "-vf", "fps=30,scale=1280:720:flags=lanczos",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(out)])
        print("proxy", i, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "audio":
        audio()
    else:
        proxy(sys.argv[2:])   # 可以只转指定编号
