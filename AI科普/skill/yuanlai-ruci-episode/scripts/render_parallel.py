"""Render an HTML animation in parallel frame ranges and concatenate the parts losslessly.

  python render_parallel.py <html> -o out.mp4 [--data timeline.json] [--fps 30] [--workers 4]
  e.g. (in an episode folder)
  python render_parallel.py 制作/engine/index.html --data 制作/timeline.json --fps 30 --workers 4 -o 制作/build/main.mp4

Each worker renders a contiguous frame range with its own headless Chromium + ffmpeg, all with identical
encoder settings (x264 CRF 16, BT.709), so the parts (in <out>_parts/) are joined with the concat demuxer
without re-encoding. Frames are captured as JPEG q95 (visually lossless before x264, ~4x cheaper than
PNG); all paths are made absolute before the workers start. Low-level tool: assemble.py calls it.
Duration = --duration, else main_duration (or duration) from --data; frames = round(duration * fps).
Frame size = --size WxH, else the canvas in --data (timeline.json episode.canvas, e.g. 2340x1080), else 1920x1080
(render.canvas_size: the same rule as render.py / the engine); the joined output is checked for it.

Robustness (a headless Chromium under 10-way load occasionally hangs in Page.screenshot / Page.goto for 30 s):
  - workers start --stagger seconds apart (default 0.7): ten pages preloading ~1300 character frames at the same
    moment made a few file:// loads fail (net::ERR_FAILED) and one Page.goto time out (2026-09-27, episode 2);
  - a worker that fails mid-range closes what it has, restarts its browser and continues from the failed
    frame (up to --retries restarts); its pieces (or its only piece) become part_NN.mp4;
  - the parent checks every worker's exit code and every part's frame count, re-runs incomplete parts once,
    and checks the frame count of the joined output. Anything still missing -> exit code 1 (never a short video).
  - page errors (JS exceptions, console.error, failed fonts, failed loads the engine did not recover — with their
    URLs, see render.open_page) -> the video is still written, exit code 2 (same convention as render.py). Image
    loads the engine retried successfully are not errors: the worker prints one info line about them.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from multiprocessing import Process
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import render  # noqa: E402  (open_page, SEEK_JS)

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "60",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709"]
# ffmpeg 8.0 (seen 2026-09-27): the multithreaded filter graph that converts the JPEG frames (yuvj420p) to yuv420p
# writes 5-px black ticks at the left edge every 72 rows when the frame is 2340 wide (1920 is fine). One filter
# thread avoids it (the conversion is cheap; x264 keeps its own threads).
FILTER_1T = ["-filter_threads", "1"]
EXIT_INCOMPLETE, EXIT_PAGE_ERRORS = 1, 2
STAGGER = 0.7          # s between worker starts: ten Chromium pages preloading ~1300 frames at once -> ERR_FAILED loads


def frame_size(path):
    """(width, height) of the first video stream, or None"""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        w, h = r.stdout.strip().split(",")[:2]
        return int(w), int(h)
    except ValueError:
        return None


def count_frames(path):
    """Number of video frames (packets) in a file; 0 if it is missing or unreadable."""
    if not Path(path).exists():
        return 0
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                        "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip().split(",")[0])
    except ValueError:
        return 0


def concat(pieces, out):
    lst = Path(str(out) + ".list.txt")
    lst.write_text("".join(f"file '{Path(p).as_posix()}'\n" for p in pieces), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out)], check=True)


def worker(html, data_path, fps, f0, f1, out, retries, size=None):
    """Render frames [f0, f1) into `out` (frame size `size`, see render.canvas_size).
    Exit code 0 = complete, 1 = incomplete, 2 = page errors."""
    from playwright.sync_api import sync_playwright
    out = Path(out)
    data = json.loads(Path(data_path).read_text(encoding="utf-8")) if data_path else None
    pieces, page_errors, nxt, attempt = [], [], f0, 0
    with sync_playwright() as p:
        while nxt < f1 and attempt <= retries:
            piece = out if attempt == 0 else out.with_name(f"{out.stem}_r{attempt}.mp4")
            ff, browser, written, errs = None, None, 0, []
            try:
                browser, page, _duration, errs = render.open_page(p, html, data, False, size, label=f"[{out.name}] ")
                # ffmpeg only once the page is open (a failed Page.goto leaves no empty piece behind)
                ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", *FILTER_1T, "-f", "image2pipe", "-framerate",
                                       str(fps), "-c:v", "mjpeg", "-i", "-", *ENC, str(piece)], stdin=subprocess.PIPE)
                for i in range(nxt, f1):
                    page.evaluate(render.SEEK_JS, i / fps)
                    ff.stdin.write(page.screenshot(type="jpeg", quality=95, animations="allow"))
                    written += 1
            except Exception as e:  # noqa: BLE001  (timeout / crashed browser: restart and resume)
                msg = (str(e).strip().splitlines() or [type(e).__name__])[0]
                print(f"[{out.name}] frame {nxt + written} (t={(nxt + written) / fps:.2f}s): {type(e).__name__}: "
                      f"{msg} -> restart browser, resume", flush=True)
            finally:
                if ff is not None:
                    try:
                        ff.stdin.close()
                    except OSError:
                        pass
                    ff.wait()
                if browser is not None:
                    try:
                        browser.close()
                    except Exception:  # noqa: BLE001
                        pass
            page_errors += [e for e in errs if e not in page_errors]
            if written:
                got = count_frames(piece)
                if got != written:            # ffmpeg lost frames of an interrupted piece: redo them
                    print(f"[{out.name}] piece {piece.name}: {got} of {written} frames encoded", flush=True)
                    written = got
                if written:
                    pieces.append(piece)
            nxt += written
            attempt += 1
    if nxt < f1:
        print(f"[{out.name}] INCOMPLETE: frames {nxt}..{f1 - 1} not rendered after {retries} restarts", flush=True)
        sys.exit(EXIT_INCOMPLETE)
    if len(pieces) > 1:                       # join the resumed pieces into the part file
        joined = out.with_name(f"{out.stem}_joined.mp4")
        concat(pieces, joined)
        os.replace(joined, out)
    elif pieces and Path(pieces[0]) != out:   # the first attempt wrote nothing (e.g. Page.goto timed out): the
        os.replace(pieces[0], out)            # restart's piece is the whole part
    if page_errors:
        print(f"[{out.name}] PAGE ERRORS: {page_errors}", flush=True)
        sys.exit(EXIT_PAGE_ERRORS)


def run_parts(jobs, html, data, fps, retries, size=None, stagger=STAGGER):
    """jobs: [(k, f0, f1, part)] -> {k: exitcode}. Workers start `stagger` seconds apart (spreads the page loads)."""
    procs = []
    for n, (k, f0, f1, part) in enumerate(jobs):
        if n and stagger > 0:
            time.sleep(stagger)
        pr = Process(target=worker, args=(html, data, fps, f0, f1, str(part), retries, size))
        pr.start()
        procs.append((k, pr))
    codes = {}
    for k, pr in procs:
        pr.join()
        codes[k] = pr.exitcode
    return codes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", help="engine page, e.g. 制作/engine/index.html")
    ap.add_argument("-o", "--out", required=True, help="output .mp4")
    ap.add_argument("--data", help="JSON exposed as window.__DATA__ (制作/timeline.json)")
    ap.add_argument("--fps", type=int, default=30, help="default 30")
    ap.add_argument("--workers", type=int, default=4, help="parallel Chromium workers (default 4: the user's standard since 2026-09-28; two 10-worker renders at once ran the 32 GB machine out of memory)")
    ap.add_argument("--duration", type=float, help="override page DURATION")
    ap.add_argument("--retries", type=int, default=3, help="browser restarts per worker after a hang/crash (default 3)")
    ap.add_argument("--size", help="frame size WxH, e.g. 2340x1080 (default: the timeline's canvas, else 1920x1080)")
    ap.add_argument("--stagger", type=float, default=STAGGER,
                    help=f"seconds between worker starts (default {STAGGER}; 0 = all at once)")
    args = ap.parse_args()

    d = json.loads(Path(args.data).read_text(encoding="utf-8")) if args.data else None
    if args.duration:
        duration = args.duration
    elif d is not None:
        duration = d.get("main_duration") or d.get("duration")
    else:
        sys.exit("need --data with main_duration, or --duration")
    size = render.canvas_size(d, render.parse_size(args.size))   # checked here, before any worker starts
    total = round(duration * args.fps)
    out = Path(args.out).resolve()
    html = str(Path(args.html).resolve())
    data = str(Path(args.data).resolve()) if args.data else None
    parts_dir = out.parent / (out.stem + "_parts")
    parts_dir.mkdir(parents=True, exist_ok=True)
    n = max(1, min(args.workers, total))
    bounds = [round(total * k / n) for k in range(n + 1)]
    jobs = [(k, bounds[k], bounds[k + 1], parts_dir / f"part_{k:02d}.mp4") for k in range(n)]
    t0 = time.time()

    codes = run_parts(jobs, html, data, args.fps, args.retries, size, args.stagger)
    page_err = any(c == EXIT_PAGE_ERRORS for c in codes.values())

    def bad_parts():
        return [j for j in jobs if codes.get(j[0]) not in (0, EXIT_PAGE_ERRORS) or count_frames(j[3]) != j[2] - j[1]]

    bad = bad_parts()
    if bad:                                    # second chance for whole parts (crashed process, lost frames)
        print(f"re-rendering incomplete parts: {[j[3].name for j in bad]}", flush=True)
        codes.update(run_parts(bad, html, data, args.fps, args.retries, size, args.stagger))
        page_err = page_err or any(codes[j[0]] == EXIT_PAGE_ERRORS for j in bad)
        bad = bad_parts()
    if bad:
        for k, f0, f1, part in bad:
            print(f"FAILED {part.name}: frames {f0}..{f1 - 1}, got {count_frames(part)} of {f1 - f0} "
                  f"(worker exit code {codes.get(k)})", file=sys.stderr)
        sys.exit(EXIT_INCOMPLETE)

    lst = parts_dir / "list.txt"
    lst.write_text("".join(f"file '{j[3].as_posix()}'\n" for j in jobs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    got = count_frames(out)
    if got != total:
        print(f"FAILED {out}: {got} frames, expected {total}", file=sys.stderr)
        sys.exit(EXIT_INCOMPLETE)
    got_size = frame_size(out)
    if got_size != tuple(size):
        print(f"FAILED {out}: frame size {got_size}, expected {size[0]}x{size[1]}", file=sys.stderr)
        sys.exit(EXIT_INCOMPLETE)
    print(f"{out}: {total} frames {size[0]}x{size[1]} in {time.time() - t0:.0f}s with {n} workers")
    if page_err:
        print("PAGE ERRORS (see the worker lines above): the video was written, but check the page", file=sys.stderr)
        sys.exit(EXIT_PAGE_ERRORS)


if __name__ == "__main__":
    main()
