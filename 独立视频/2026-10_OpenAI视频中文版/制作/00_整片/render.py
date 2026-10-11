# -*- coding: utf-8 -*-
"""原片画面 + 混音 + 双语字幕 → 整片_v1.mp4（H.264 + AAC，1920×1080，保持原片帧率）。

  python render.py [输出文件名] [ASS 文件名]      # 默认 整片_v1.mp4 + bilingual.ass；标准版：python render.py 整片_v2.mp4 bilingual_std.ass

字幕用 libass 直接烧进画面（bilingual.ass，字体放在 fonts/，路径用相对路径，所以工作目录固定在本目录）。
画面逐帧重编码（crf 18），声音是 audio/mix.wav 压成 AAC 192k。
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parents[1] / "素材" / "fHEIw5CcN5U_1080p_video-only.mp4"


def main():
    out = HERE / (sys.argv[1] if len(sys.argv) > 1 else "整片_v1.mp4")
    ASS_NAME = sys.argv[2] if len(sys.argv) > 2 else "bilingual.ass"
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    vf = f"subtitles={ASS_NAME}:fontsdir=fonts"
    if T["extend"] > 0.05:                                    # 配音比画面长：最后一帧定格补齐
        vf = f"tpad=stop_mode=clone:stop_duration={T['extend']:.3f}," + vf
    cmd = ["ffmpeg", "-y", "-hide_banner", "-i", str(VIDEO), "-i", "audio/mix.wav", "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{T['total']:.3f}", str(out)]
    print(" ".join(cmd[:8]), "…", flush=True)
    subprocess.run(cmd, cwd=HERE, check=True)
    print("done", out.name, f"{out.stat().st_size / 1048576:.1f} MiB")


if __name__ == "__main__":
    main()
