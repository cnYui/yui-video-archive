"""Put the UE intro in front of a video and the UE outro after it, keeping the video's own quality.

  python add_to_video.py <input.mp4> [-o output.mp4] [--outro-data data.json] [--intro-data data.json]
                         [--no-music] [--series D:/大疆/AI科普]

For videos that are NOT made with this pipeline (e.g. real-footage clips); an episode made here gets its
intro / outro from assemble.py instead. So this tool takes a video file, not an episode folder.

- Intro / outro come from SERIES/片头片尾/intro|outro/index.html (data defaults: that folder's data.json)
  and are rendered at the input's own resolution and frame rate
  (a 3840x2160 input is rendered with device scale 2, not upscaled from 1080p). An input wider than 16:9
  (e.g. 2340x1080 = 19.5:9, 3120x1440) gets a page as wide as its aspect (canvas W x 1080, device scale h / 1080,
  passed to the page as "canvas"): the intro / outro lay themselves out centred on it, background, grain, crop marks
  and the closing ink across the full width -- no stretching, no blank side bars. Narrower inputs (4:3, portrait)
  keep the 1920x1080 page scaled to the input size, as before.
- The main video is NOT re-encoded: all three parts are converted to MPEG-TS with identical audio
  settings and joined with stream copy, so the original picture is untouched.
- Under the intro / outro goes a short piece of the series BGM (SERIES/素材/音频/bgm.wav),
  levelled about 7 dB below the input's speech loudness; --no-music gives silence instead.
- The outro credits (--outro-data items / closing) must be confirmed with the user for every video.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
SERIES_DEFAULT = Path(r"D:/大疆/AI科普")
PACK = SERIES_DEFAULT / "片头片尾"              # replaced from --series in main()
BGM = SERIES_DEFAULT / "素材" / "音频" / "bgm.wav"
sys.stdout.reconfigure(encoding="utf-8")

SEEK_JS = """(t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (typeof window.renderAt === 'function') window.renderAt(t);
}"""


def run(cmd, **kw):
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format",
                                   str(path)]).decode("utf-8")
    info = json.loads(out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["avg_frame_rate"].split("/"))
    return dict(w=int(v["width"]), h=int(v["height"]), fps=round(num / den, 3), vcodec=v["codec_name"],
                profile=v.get("profile", "High"), level=v.get("level", 52), pix_fmt=v["pix_fmt"],
                sr=int(a["sample_rate"]) if a else 48000, ch=int(a["channels"]) if a else 2,
                duration=float(info["format"]["duration"]))


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    for line in reversed(err.splitlines()):
        if line.strip().startswith("I:"):
            return float(line.split()[1])
    return -16.0


def page_geometry(meta):
    """(page width, page height, device scale) for the intro / outro pages at the input's size.
    16:9 or narrower: the 1920x1080 page scaled by w / 1920 (as before). Wider than 16:9: a canvas of the input's
    aspect at height 1080 (2340x1080 -> 2340 wide, scale 1; 4680x2160 -> 2340 wide, scale 2)."""
    w, h = meta["w"], meta["h"]
    if w * 1080 <= h * 1920:                       # 16:9 or narrower
        return 1920, 1080, w / 1920
    scale = h / 1080
    return max(1920, round(w / scale)), 1080, scale


def render_part(html, data, seconds, meta, out_path):
    """Render an HTML animation at the input's resolution / fps to an H.264 clip (no audio)."""
    from playwright.sync_api import sync_playwright
    pw_, ph_, scale = page_geometry(meta)
    if pw_ != 1920:                                # the page lays itself out on the wider canvas
        data = dict(data, canvas=[pw_, ph_])
    fps = meta["fps"]
    level = str(meta["level"] / 10) if isinstance(meta["level"], int) and meta["level"] > 9 else str(meta["level"])
    # -filter_threads 1: ffmpeg 8.0's multithreaded yuvj420p -> yuv420p conversion puts black ticks on the left edge of
    # 2340-wide frames (every 72 rows); one filter thread avoids it (see render_parallel.py FILTER_1T)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-filter_threads", "1",
           "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-vf", f"scale={meta['w']}:{meta['h']}:flags=lanczos,format={meta['pix_fmt']}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-profile:v", "high", "-level:v", level,
           "-r", str(fps), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", str(out_path)]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": pw_, "height": ph_}, device_scale_factor=scale)
        page.add_init_script(f"window.__CAPTURE__ = true; window.__CANVAS__ = [{pw_}, {ph_}]; "
                             f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};")
        page.goto(Path(html).resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_function("window.__READY__ !== false", timeout=15000)
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = round(seconds * fps)
        for i in range(n):
            page.evaluate(SEEK_JS, i / fps)
            ff.stdin.write(page.screenshot(type="jpeg", quality=95, animations="allow"))
        ff.stdin.close()
        if ff.wait() != 0:
            sys.exit("ffmpeg failed while encoding " + str(out_path))
        browser.close()


def page_duration(html, data):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.add_init_script(f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};")
        page.goto(Path(html).resolve().as_uri())
        page.wait_for_load_state("networkidle")
        d = float(page.evaluate("window.DURATION"))
        browser.close()
    return d


def mux_with_audio(video, seconds, meta, music_offset, fade_in, fade_out, gain_db, music, out_ts):
    """Attach an audio track (music snippet or silence) and write MPEG-TS with the input's audio format."""
    if music and BGM.exists():
        af = (f"atrim=start={music_offset}:duration={seconds},asetpts=PTS-STARTPTS,"
              f"afade=t=in:st=0:d={fade_in},afade=t=out:st={max(0, seconds - fade_out)}:d={fade_out},volume={gain_db}dB")
        audio_in = ["-i", BGM]
    else:
        af = f"atrim=duration={seconds}"
        audio_in = ["-f", "lavfi", "-i", f"anullsrc=r={meta['sr']}:cl={'stereo' if meta['ch'] == 2 else 'mono'}"]
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, *audio_in, "-map", "0:v", "-map", "1:a",
         "-af", af + f",aresample={meta['sr']}", "-ac", meta["ch"], "-c:v", "copy", "-bsf:v", "h264_mp4toannexb",
         "-c:a", "aac", "-b:a", "192k", "-ar", meta["sr"], "-t", f"{seconds:.3f}", "-f", "mpegts", out_ts])


def main():
    global PACK, BGM
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="H.264 input video")
    ap.add_argument("-o", "--output", help="default: <input>_片头片尾.mp4 next to the input")
    ap.add_argument("--intro-data", help="intro JSON {name, tagline} (default: 片头片尾/intro/data.json)")
    ap.add_argument("--outro-data", help="outro JSON {items, closing, signature} (default: 片头片尾/outro/data.json)")
    ap.add_argument("--no-music", action="store_true", help="silence under intro / outro instead of the BGM")
    ap.add_argument("--series", default=str(SERIES_DEFAULT), help=f"系列根目录，默认 {SERIES_DEFAULT}")
    args = ap.parse_args()
    PACK = Path(args.series) / "片头片尾"
    BGM = Path(args.series) / "素材" / "音频" / "bgm.wav"
    args.intro_data = args.intro_data or str(PACK / "intro" / "data.json")
    args.outro_data = args.outro_data or str(PACK / "outro" / "data.json")
    if not BGM.exists() and not args.no_music:
        print(f"[warn] BGM not found: {BGM} -> silence under intro / outro")

    src = Path(args.input)
    out = Path(args.output) if args.output else src.with_name(src.stem + "_片头片尾.mp4")
    meta = probe(src)
    if meta["vcodec"] != "h264":
        sys.exit(f"input video codec is {meta['vcodec']}; this tool stream-copies H.264 only")
    speech = loudness(src)
    gain = (speech - 7) - (-20.0)          # BGM file is mastered at -20 LUFS; sit ~7 dB under the speech
    pw_, ph_, scale = page_geometry(meta)
    print(f"input {meta['w']}x{meta['h']} @ {meta['fps']} fps, {meta['duration']:.1f}s, speech {speech:.1f} LUFS -> music {gain:+.1f} dB; "
          f"intro / outro page {pw_}x{ph_} at scale {scale:g}")

    intro_data = json.loads(Path(args.intro_data).read_text(encoding="utf-8"))
    outro_data = json.loads(Path(args.outro_data).read_text(encoding="utf-8"))
    # work files next to the output, not in the system / session temp folder: a session temp path can be longer
    # than Windows' 260 characters, and Python / ffmpeg then cannot open files there
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="_tmp_add_to_video_", dir=out.parent) as tmp:
        tmp = Path(tmp)
        parts = []
        for name, data, music_offset, fi, fo in (("intro", intro_data, 0.0, 0.4, 0.8), ("outro", outro_data, 60.0, 0.6, 1.2)):
            html = PACK / name / "index.html"
            secs = page_duration(html, data)
            render_part(html, data, secs, meta, tmp / f"{name}.mp4")
            mux_with_audio(tmp / f"{name}.mp4", secs, meta, music_offset, fi, fo, gain, not args.no_music, tmp / f"{name}.ts")
            parts.append((name, tmp / f"{name}.ts", secs))
            print(f"{name}: {secs:.2f}s rendered")
        # main video: stream copy to TS (audio re-encoded only if it is not already AAC at the target format)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "copy",
             "-bsf:v", "h264_mp4toannexb", "-c:a", "copy", "-f", "mpegts", tmp / "main.ts"])
        concat = "concat:" + "|".join(str(p) for p in (parts[0][1], tmp / "main.ts", parts[1][1]))
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", concat, "-c", "copy", "-bsf:a", "aac_adtstoasc",
             "-movflags", "+faststart", out])
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                           str(out)]).decode().strip())
    print(f"-> {out}  ({total:.2f}s = {parts[0][2]:.2f} + {meta['duration']:.2f} + {parts[1][2]:.2f})")


if __name__ == "__main__":
    main()
