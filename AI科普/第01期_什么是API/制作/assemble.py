"""Render intro + main + outro at 30 fps, join them, mux the final mix, and write the SRT.

usage: python assemble.py [--skip-main] [--workers 6]
Output: ../第01期_什么是API_成片.mp4, ../第01期_什么是API_字幕.srt, ../第01期_什么是API_章节.txt
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
EP = HERE.parent
PACK = HERE.parent.parent / "片头片尾"      # sibling folder: AI科普/片头片尾
BUILD = HERE / "build"
FPS = 30
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "60",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709"]


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd)[:200], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(tl, path):
    rows, i = [], 1
    for s in tl["segments"]:
        for ln in s["lines"]:
            a, b = tl["intro"] + ln["start"], tl["intro"] + ln["end"]
            rows.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{ln['text']}\n")
            i += 1
    path.write_text("\n".join(rows), encoding="utf-8")


def reencode(src, dst):
    """Normalise a clip to the common encoding (30 fps, same x264 settings) so parts concat cleanly."""
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-r", FPS, *ENC, "-an", dst])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-main", action="store_true", help="reuse build/main.mp4")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    tl = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    BUILD.mkdir(exist_ok=True)

    # intro / outro rendered straight at 30 fps from their HTML sources
    for name in ("intro", "outro"):
        out = BUILD / f"{name}_raw.mp4"
        run([sys.executable, PACK / "render.py", PACK / name / "index.html", "--data", PACK / name / "data.json",
             "--fps", FPS, "-o", out])
        reencode(out, BUILD / f"{name}.mp4")

    if not args.skip_main:
        run([sys.executable, HERE / "render_parallel.py", HERE / "engine" / "index.html", "--data", HERE / "timeline.json",
             "--fps", FPS, "--workers", args.workers, "-o", BUILD / "main.mp4"])

    lst = BUILD / "concat.txt"
    lst.write_text("".join(f"file '{(BUILD / n).as_posix()}'\n" for n in ("intro.mp4", "main.mp4", "outro.mp4")),
                   encoding="utf-8")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", BUILD / "video.mp4"])

    final = EP / "第01期_什么是API_成片.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", BUILD / "video.mp4", "-i", BUILD / "mix.wav",
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", final])

    write_srt(tl, EP / "第01期_什么是API_字幕.srt")
    shutil.copy2(HERE / "chapters_bilibili.txt", EP / "第01期_什么是API_章节.txt")
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height,r_frame_rate",
                                     "-of", "compact", str(final)]).decode()
    print(probe)
    print("expected total", tl["total_duration"])


if __name__ == "__main__":
    main()
