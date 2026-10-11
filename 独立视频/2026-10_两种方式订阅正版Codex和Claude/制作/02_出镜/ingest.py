# -*- coding: utf-8 -*-
r"""出镜录像入库（SD 卡 H:\DCIM\DJI_001，只读，原片不复制）。做法照《从0到1用WorkBuddy上线一个微信小程序》的 ingest.py。

  python ingest.py audio [编号…]   → audio/<编号>.wav（48 kHz 立体声，混音用）、audio16/<编号>.wav（16 kHz 单声道，识别用）
  python ingest.py proxy [编号…]   → proxy/<编号>.mp4（1280×720、30 fps；HLG 10-bit 不做色彩转换直接转 8-bit，肤色最自然）

编号 = DJI 文件名最后 4 位。0163：2026-10-01 13:53 录的开场出镜（89 s）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SD = Path(r"H:\DCIM\DJI_001")
CAM = ["0163"]


def src_of(i):
    m = sorted(SD.glob(f"DJI_*_{i}_D.MP4"))
    assert len(m) == 1, (i, m)
    return m[0]


def run(args):
    subprocess.run(args, check=True, capture_output=True)


def audio(ids):
    (HERE / "audio").mkdir(exist_ok=True)
    (HERE / "audio16").mkdir(exist_ok=True)
    for i in ids:
        s = src_of(i)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-map", "0:a:0", "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(HERE / "audio" / f"{i}.wav")])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(s), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(HERE / "audio16" / f"{i}.wav")])
        print("audio", i, s.name, flush=True)


def proxy(ids):
    (HERE / "proxy").mkdir(exist_ok=True)
    for i in ids:
        s = src_of(i)
        run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", str(s), "-map", "0:v:0", "-map", "0:a:0",
             "-vf", "fps=30,scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", str(HERE / "proxy" / f"{i}.mp4")])
        print("proxy", i, flush=True)


if __name__ == "__main__":
    cmd, ids = sys.argv[1], sys.argv[2:] or CAM
    (audio if cmd == "audio" else proxy)(ids)
