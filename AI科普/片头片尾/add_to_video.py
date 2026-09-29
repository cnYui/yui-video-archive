"""Put the UE intro in front of a video and the UE outro after it, keeping the video's own quality.

usage: python add_to_video.py <input.mp4> [-o output.mp4] [--outro-data outro/data.json] [--no-music]

- Intro / outro are rendered from their HTML at the input's own resolution and frame rate
  (a 3840x2160 input is rendered with device scale 2, not upscaled from 1080p).
- The main video is NOT re-encoded: all three parts are converted to MPEG-TS with identical audio
  settings and joined with stream copy, so the original picture is untouched.
- Under the intro / outro goes a short piece of the series BGM (../第01期_什么是API/制作/audio/bgm.wav),
  levelled about 7 dB below the input's speech loudness; --no-music gives silence instead.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BGM = HERE.parent / "第01期_什么是API" / "制作" / "audio" / "bgm.wav"
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


def render_part(html, data, seconds, meta, out_path):
    """Render an HTML animation at the input's resolution / fps to an H.264 clip (no audio)."""
    from playwright.sync_api import sync_playwright
    scale = meta["w"] / 1920
    fps = meta["fps"]
    level = str(meta["level"] / 10) if isinstance(meta["level"], int) and meta["level"] > 9 else str(meta["level"])
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
           "-vf", f"scale={meta['w']}:{meta['h']}:flags=lanczos,format={meta['pix_fmt']}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-profile:v", "high", "-level:v", level,
           "-r", str(fps), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", str(out_path)]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
        page.add_init_script(f"window.__CAPTURE__ = true; window.__DATA__ = {json.dumps(data, ensure_ascii=False)};")
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
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--intro-data", default=str(HERE / "intro" / "data.json"))
    ap.add_argument("--outro-data", default=str(HERE / "outro" / "data.json"))
    ap.add_argument("--no-music", action="store_true")
    args = ap.parse_args()

    src = Path(args.input)
    out = Path(args.output) if args.output else src.with_name(src.stem + "_片头片尾.mp4")
    meta = probe(src)
    if meta["vcodec"] != "h264":
        sys.exit(f"input video codec is {meta['vcodec']}; this tool stream-copies H.264 only")
    speech = loudness(src)
    gain = (speech - 7) - (-20.0)          # BGM file is mastered at -20 LUFS; sit ~7 dB under the speech
    print(f"input {meta['w']}x{meta['h']} @ {meta['fps']} fps, {meta['duration']:.1f}s, speech {speech:.1f} LUFS -> music {gain:+.1f} dB")

    intro_data = json.loads(Path(args.intro_data).read_text(encoding="utf-8"))
    outro_data = json.loads(Path(args.outro_data).read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        parts = []
        for name, data, music_offset, fi, fo in (("intro", intro_data, 0.0, 0.4, 0.8), ("outro", outro_data, 60.0, 0.6, 1.2)):
            html = HERE / name / "index.html"
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
