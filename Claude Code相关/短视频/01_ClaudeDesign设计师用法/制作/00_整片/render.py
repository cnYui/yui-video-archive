# -*- coding: utf-8 -*-
"""合成：静态层 + 上下两路分镜（圆角）+ 字幕（ASS）+ 配音 → 成片。

  python render.py              # 成片_竖屏_中英字幕.mp4（crf 17）+ 成片_竖屏_无字幕.mp4 + _手机预览.mp4（540×1170）
  python render.py --fast       # 只出一条快速预览 build/preview_fast.mp4（veryfast，crf 23，带字幕）
  python render.py --stills 3 8 15.5 [--dir v2]   # 只在这些秒数抽帧到 build/stills[_v2]/（来自 preview_fast.mp4，不重编码整条）

必须在本目录运行（subtitles 滤镜的路径在 Windows 上带盘符会被冒号弄坏，所以用相对路径：build/bilingual.ass、fonts/）。
图层顺序：bg.png（米白底 + 点阵 + 标题 + 两个外框）→ 上框画面 → 下框画面 → fg.png（来源角标）→ 字幕。
上下两路画面是 972×546 的小片段（render_clips.py 出的 build/top.mp4、bottom.mp4），用 mask_inner.png 做 8 px 圆角再贴进外框。
"""
import json
import subprocess
import sys

import config as C

BUILD = C.HERE / "build"
OUT_SUB = C.EP / "成片_竖屏_中英字幕.mp4"
OUT_RAW = C.EP / "成片_竖屏_无字幕.mp4"
OUT_PRE = C.EP / "成片_竖屏_手机预览.mp4"


def graph(with_subs):
    g = ("[3:v]format=gray,split=2[m1][m2];"
         "[1:v]format=yuv420p[t0];[t0][m1]alphamerge[t];"
         "[2:v]format=yuv420p[b0];[b0][m2]alphamerge[b];"
         f"[0:v][t]overlay={C.BOX_X + C.PAD}:{C.FACE_Y + C.PAD}:format=auto[v1];"
         f"[v1][b]overlay={C.BOX_X + C.PAD}:{C.SCREEN_Y + C.PAD}:format=auto[v2];"
         "[v2][4:v]overlay=0:0:format=auto[v3];")
    g += "[v3]subtitles=build/bilingual.ass:fontsdir=fonts,format=yuv420p[v]" if with_subs else "[v3]format=yuv420p[v]"
    return g


def cmd(total, out, with_subs, crf, preset):
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", str(C.FPS), "-i", "build/bg.png",
            "-i", "build/top.mp4", "-i", "build/bottom.mp4",
            "-loop", "1", "-framerate", str(C.FPS), "-i", "build/mask_inner.png",
            "-loop", "1", "-framerate", str(C.FPS), "-i", "build/fg.png",
            "-i", "build/audio.wav",
            "-filter_complex", graph(with_subs), "-map", "[v]", "-map", "5:a",
            "-t", f"{total:.3f}", "-r", str(C.FPS), "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]


def main():
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    total = tl["frames"] / C.FPS
    if "--fast" in sys.argv:
        subprocess.run(cmd(total, BUILD / "preview_fast.mp4", True, 23, "veryfast"), cwd=C.HERE, check=True)
        print("build/preview_fast.mp4")
        return
    if "--stills" in sys.argv:
        args = sys.argv[sys.argv.index("--stills") + 1:]
        tag = "stills"
        if "--dir" in args:                                    # --dir v2 → build/stills_v2/（不覆盖、不删旧的）
            i = args.index("--dir")
            tag = "stills_" + args[i + 1]
            args = args[:i] + args[i + 2:]
        ts = [float(x) for x in args]
        (BUILD / tag).mkdir(exist_ok=True)
        src = BUILD / "preview_fast.mp4" if (BUILD / "preview_fast.mp4").exists() and "--final" not in sys.argv else OUT_SUB
        for t in ts:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", str(BUILD / tag / f"t{t:06.2f}.png")], check=True)
        print(f"build/{tag}/ 已写", len(ts), "张（来自", src.name, "）")
        return
    subprocess.run(cmd(total, OUT_SUB, True, C.CRF_FINAL, "medium"), cwd=C.HERE, check=True)
    subprocess.run(cmd(total, OUT_RAW, False, C.CRF_FINAL, "medium"), cwd=C.HERE, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT_SUB), "-vf", "scale=540:1170:flags=lanczos", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(OUT_PRE)], check=True)
    for p in (OUT_SUB, OUT_RAW, OUT_PRE):
        print(p.name, round(p.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
