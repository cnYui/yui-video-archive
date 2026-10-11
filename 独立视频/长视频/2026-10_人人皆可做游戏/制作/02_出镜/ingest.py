# -*- coding: utf-8 -*-
"""出镜素材入库：SD 卡 H:/DCIM/DJI_001（只读，原片不改动）。

  python ingest.py audio [编号…]   → audio/<编号>.wav（48 kHz 立体声，混音用）、audio16/<编号>.wav（16 kHz 单声道，识别、对轴用）
  python ingest.py proxy [编号…]   → proxy/<编号>.mp4（1920×1080、60 fps，H.264 8-bit，剪辑用；原片是 4K HEVC 10-bit HLG）

编号 = DJI 文件名最后 4 位。2026-10-06 18:27–18:34 录的四条，是《欢迎来到 人人皆可做游戏的 时代》的口播（出镜稿 v1）。
HLG 10-bit：不做色彩转换，直接转 8-bit（Way to AGI 02 期试过，这样肤色最自然）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SD = Path("H:/DCIM/DJI_001")
IDS = ["0190", "0191", "0193", "0194"]


def src_of(i):
    m = sorted(SD.glob(f"DJI_*_{i}_D.MP4"))
    assert len(m) == 1, (i, m)
    return m[0]


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def audio(ids=None):
    (HERE / "audio").mkdir(exist_ok=True)
    (HERE / "audio16").mkdir(exist_ok=True)
    for i in (ids or IDS):
        s = src_of(i)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-map", "0:a:0", "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(HERE / "audio" / f"{i}.wav")])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(HERE / "audio16" / f"{i}.wav")])
        print("audio", i, s.name, flush=True)


def proxy(ids=None):
    (HERE / "proxy").mkdir(exist_ok=True)
    for i in (ids or IDS):
        s = src_of(i)
        out = HERE / "proxy" / f"{i}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-threads", "6", "-i", str(s), "-map", "0:v:0", "-map", "0:a:0",
             "-vf", "scale=1920:1080:flags=lanczos", "-r", "60",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", str(out)])
        print("proxy", i, flush=True)


if __name__ == "__main__":
    cmd, ids = sys.argv[1], sys.argv[2:]
    if cmd == "audio":
        audio(ids or None)
    elif cmd == "proxy":
        proxy(ids or None)
