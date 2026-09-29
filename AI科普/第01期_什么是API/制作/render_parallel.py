"""Render an HTML animation in parallel frame ranges and concatenate the parts losslessly.

usage: python render_parallel.py <html> -o out.mp4 [--data timeline.json] [--fps 30] [--workers 6]
Each worker renders a contiguous frame range with its own headless Chromium + ffmpeg, all with identical
encoder settings, so the parts can be joined with the concat demuxer without re-encoding.
"""
import argparse
import json
import subprocess
import sys
import time
from multiprocessing import Process
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402  (open_page, frame_at)

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "60",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709"]


def worker(html, data_path, fps, f0, f1, out):
    from playwright.sync_api import sync_playwright
    data = json.loads(Path(data_path).read_text(encoding="utf-8")) if data_path else None
    with sync_playwright() as p:
        browser, page, _duration, errors = render.open_page(p, html, data, False)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg",
               "-i", "-", *ENC, str(out)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(f0, f1):
            page.evaluate(render.SEEK_JS, i / fps)
            # JPEG q95 is visually lossless before x264 and ~4x cheaper to encode than a 1080p PNG
            ff.stdin.write(page.screenshot(type="jpeg", quality=95, animations="allow"))
        ff.stdin.close()
        ff.wait()
        browser.close()
    if errors:
        print(f"[{out.name}] PAGE ERRORS: {errors}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--data")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--duration", type=float, help="override page DURATION")
    args = ap.parse_args()

    if args.duration:
        duration = args.duration
    elif args.data:
        d = json.loads(Path(args.data).read_text(encoding="utf-8"))
        duration = d.get("main_duration") or d.get("duration")
    else:
        sys.exit("need --data with main_duration, or --duration")
    total = round(duration * args.fps)
    out = Path(args.out).resolve()
    parts_dir = out.parent / (out.stem + "_parts")
    parts_dir.mkdir(parents=True, exist_ok=True)
    n = max(1, args.workers)
    bounds = [round(total * k / n) for k in range(n + 1)]
    procs, parts = [], []
    t0 = time.time()
    for k in range(n):
        part = parts_dir / f"part_{k:02d}.mp4"
        parts.append(part)
        pr = Process(target=worker, args=(str(Path(args.html).resolve()), str(Path(args.data).resolve()) if args.data else None,
                                          args.fps, bounds[k], bounds[k + 1], part))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = parts_dir / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    print(f"{out}: {total} frames in {time.time() - t0:.0f}s with {n} workers")


if __name__ == "__main__":
    main()
