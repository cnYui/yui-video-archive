# -*- coding: utf-8 -*-
"""拼接各段小片 + 烧字幕 + 混音 → 成片。

  python render.py              # 成片_竖屏_中英字幕.mp4（crf 17）+ 成片_竖屏_无字幕.mp4 + 成片_竖屏_手机预览.mp4（540×1170）
  python render.py --fast       # 只出一条快速预览 build/preview_fast.mp4（veryfast，crf 23，带字幕）
  python render.py --stills 3 12.5 40 [--dir v1] [--final]   # 在这些秒数抽帧到 build/stills[_v1]/（默认来自 preview_fast.mp4，加 --final 来自成片）

必须在本目录运行（subtitles 滤镜的路径在 Windows 上带盘符会被冒号弄坏，所以用相对路径：build/bilingual.ass、fonts/）。
各段小片（render_scenes.py 出的 build/scenes/<id>.mp4）编码参数一致，直接 concat（-c copy）成 build/video_nosub.mp4，再一次性烧字幕 + 混音重编码。
"""
import json
import subprocess
import sys

import config as C

TL = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))
OUT_SUB = C.EP / "成片_竖屏_中英字幕.mp4"
OUT_RAW = C.EP / "成片_竖屏_无字幕.mp4"
OUT_PRE = C.EP / "成片_竖屏_手机预览.mp4"


def concat_scenes():
    lst = C.BUILD / "scenes.txt"
    lst.write_text("\n".join(f"file 'scenes/{p['id']}.mp4'" for p in TL["passages"]) + "\n", encoding="utf-8")
    out = C.BUILD / "video_nosub.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)], check=True)
    return out


def encode(video, out, with_subs, crf, preset):
    vf = "subtitles=build/bilingual.ass:fontsdir=fonts,format=yuv420p" if with_subs else "format=yuv420p"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-i", "build/audio.wav", "-map", "0:v", "-map", "1:a", "-vf", vf,
           "-t", f"{TL['frames'] / C.FPS:.3f}", "-r", str(C.FPS), "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, cwd=C.HERE, check=True)


def main():
    if "--stills" in sys.argv:
        args = sys.argv[sys.argv.index("--stills") + 1:]
        tag = "stills"
        if "--dir" in args:
            i = args.index("--dir")
            tag = "stills_" + args[i + 1]
            args = args[:i] + args[i + 2:]
        final = "--final" in args
        args = [a for a in args if a != "--final"]
        ts = [float(x) for x in args]
        (C.BUILD / tag).mkdir(exist_ok=True)
        src = OUT_SUB if final or not (C.BUILD / "preview_fast.mp4").exists() else C.BUILD / "preview_fast.mp4"
        for t in ts:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", str(C.BUILD / tag / f"t{t:06.2f}.png")], check=True)
        print(f"build/{tag}/ 已写 {len(ts)} 张（来自 {src.name}）")
        return
    video = concat_scenes()
    if "--fast" in sys.argv:
        encode(video, C.BUILD / "preview_fast.mp4", True, 23, "veryfast")
        print("build/preview_fast.mp4")
        return
    encode(video, OUT_SUB, True, C.CRF_FINAL, "medium")
    encode(video, OUT_RAW, False, C.CRF_FINAL, "medium")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT_SUB), "-vf", "scale=540:1170:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(OUT_PRE)], check=True)
    for p in (OUT_SUB, OUT_RAW, OUT_PRE):
        print(p.name, round(p.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
