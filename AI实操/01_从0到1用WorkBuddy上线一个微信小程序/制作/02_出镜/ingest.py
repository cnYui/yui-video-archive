# -*- coding: utf-8 -*-
"""录像入库：出镜（SD 卡 H:\\DCIM\\DJI_001，只读）+ 录屏（素材\\录屏，从“下载”复制来的）。原片不改动。

  python ingest.py audio [编号…]   → audio/<编号>.wav（48 kHz 立体声，混音用）、audio16/<编号>.wav（16 kHz 单声道，识别、对轴用）
  python ingest.py proxy [编号…]   → proxy/<编号>.mp4（出镜 1280×720、30 fps；录屏 1920×1080、30 fps）

编号：出镜 = DJI 文件名最后 4 位；录屏 = R + 录屏文件名里的时分（OpenScreen 文件名里的时间是**停止录制**的时刻）。
本期素材都是 2026-10-01 上午录的（0157 只有 2 s 的 LRF，没有 MP4，是误触）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
SD = Path(r"H:\DCIM\DJI_001")
REC = EP / "素材" / "录屏"

CAM = ["0155", "0156", "0158", "0159", "0160", "0161", "0162"]
SCR = {
    "R0945": "Recording_2026_10_1_09_45_15.mp4",
    "R0948": "Recording_2026_10_1_09_48_52.mp4",
    "R1013": "Recording_2026_10_1_10_13_50.mp4",
    "R1029": "Recording_2026_10_1_10_29_14.mp4",
    "R1036": "Recording_2026_10_1_10_36_21.mp4",
    "R1041": "Recording_2026_10_1_10_41_19.mp4",
    "R1046": "Recording_2026_10_1_10_46_01.mp4",
}
IDS = CAM + list(SCR)


def src_of(i):
    if i in SCR:
        return REC / SCR[i]
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
        # 出镜原片是 HLG 10-bit：不做色彩转换，直接转 8-bit（Way to AGI 02 期试过，这样肤色最自然）
        size = "1920:1080" if i in SCR else "1280:720"
        run(["ffmpeg", "-v", "error", "-y", "-threads", "4", "-i", str(s), "-map", "0:v:0", "-map", "0:a:0",
             "-vf", f"fps=30,scale={size}:flags=lanczos",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18" if i in SCR else "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", str(out)])
        print("proxy", i, flush=True)


if __name__ == "__main__":
    cmd, ids = sys.argv[1], sys.argv[2:]
    if cmd == "audio":
        audio(ids)
    else:
        proxy(ids)
