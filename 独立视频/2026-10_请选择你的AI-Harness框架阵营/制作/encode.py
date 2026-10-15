# -*- coding: utf-8 -*-
"""PNG 序列 + 参考视频的音轨（只有 BGM）→ mp4。台本.json 的 dur 是全片长度：音轨裁到 dur，最后 audio_fade 秒淡出（高码率 AAC 重编码）。

用法：python encode.py [--frames build/frames] [--out 成片.mp4] [--crf 16]
音轨：参考分析/ref.mp4 里的 AAC（BGM，原视频没有人声），裁到 台本.json 的 dur（当前约 75.5 s，在曲子第 160 拍的自然收尾处淡出）。
注意：ffmpeg 8.0 在 2340 宽时多线程转像素格式会在左边缘出黑点，所以加 -filter_threads 1。
"""
import argparse
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "参考分析" / "ref.mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=str(HERE / "build" / "frames"))
    ap.add_argument("--out", default=str(HERE / "build" / "成片_无片头片尾.mp4"))
    ap.add_argument("--crf", default="16")
    ap.add_argument("--preset", default="slow")
    a = ap.parse_args()
    data = json.loads((HERE.parent / "台本" / "台本.json").read_text(encoding="utf-8"))
    dur, fade = data["dur"], data.get("audio_fade", 1.5)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats",
           "-filter_threads", "1", "-filter_complex_threads", "1",
           "-framerate", "30", "-i", f"{a.frames}/f_%05d.png",
           "-i", str(REF),
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "libx264", "-preset", a.preset, "-crf", a.crf, "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-af", f"afade=t=out:st={dur - fade:.3f}:d={fade:.3f}", "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
           "-t", f"{dur:.3f}", "-movflags", "+faststart", a.out]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print("done", a.out)


if __name__ == "__main__":
    main()
