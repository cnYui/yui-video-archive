"""Preview renderer for the 2026-10 intro / outro candidates: HTML animation -> MP4 / contact sheet / stills.

Same contract as ../render.py (window.DURATION, window.renderAt(t), window.__DATA__, window.__READY__), plus
--width so the 2340x1080 (19.5:9) layout can be checked: the page gets window.__CANVAS__ = [width, 1080] exactly
like add_to_video.py / assemble.py pass it.

  python render_preview.py A_鼓励球/intro/index.html --data A_鼓励球/intro/data.json --sheet out/A_intro_sheet.png
  python render_preview.py A_鼓励球/intro/index.html --data A_鼓励球/intro/data.json --stills 1.0,2.5 --stills-dir out/stills
  python render_preview.py A_鼓励球/intro/index.html --data A_鼓励球/intro/data.json -o out/A_intro.mp4 --width 2340
"""
import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
H = 1080
SEEK_JS = """(t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (typeof window.renderAt === 'function') window.renderAt(t);
}"""


def open_page(p, html, data, width):
    browser = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text", "--font-render-hinting=none"])
    page = browser.new_page(viewport={"width": width, "height": H}, device_scale_factor=1)
    init = f"window.__CAPTURE__ = true; window.__CANVAS__ = [{width}, {H}];"
    if data is not None:
        init += f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};"
    page.add_init_script(init)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type in ("error", "warning") and errors.append(f"[{m.type}] {m.text}"))
    page.goto(Path(html).resolve().as_uri())
    page.wait_for_load_state("networkidle")
    page.wait_for_function("window.__READY__ !== false", timeout=20000)
    duration = page.evaluate("window.DURATION")
    if not isinstance(duration, (int, float)) or duration <= 0:
        sys.exit("page must set window.DURATION (seconds)")
    bad_fonts = page.evaluate("[...document.fonts].filter(f => f.status === 'error').map(f => f.family)")
    if bad_fonts:
        errors.append(f"fonts failed to load: {bad_fonts}")
    return browser, page, float(duration), errors


def frame_at(page, t, fmt="png"):
    page.evaluate(SEEK_JS, t)
    return page.screenshot(type=fmt, animations="allow") if fmt == "png" else page.screenshot(type="jpeg", quality=95, animations="allow")


def contact_sheet(frames, path, cols=4, width=1920):
    tw = 480
    th = round(tw * H / width)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(Path(__file__).parent.parent / "fonts" / "JetBrainsMono.ttf"), 18)
    except OSError:
        font = ImageFont.load_default()
    for i, (t, png) in enumerate(frames):
        img = Image.open(io.BytesIO(png)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 28)
        sheet.paste(img, (x, y + 28))
        draw.text((x + 8, y + 4), f"t={t:.2f}s", fill=(230, 230, 230), font=font)
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out", help="output .mp4 (H.264)")
    ap.add_argument("--data", help="JSON file exposed as window.__DATA__")
    ap.add_argument("--width", type=int, default=1920, help="frame width (1920 or 2340); height is 1080")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--sheet", help="write a contact sheet PNG")
    ap.add_argument("--sheet-count", type=int, default=16)
    ap.add_argument("--stills", help="comma-separated times (s) to save as PNG")
    ap.add_argument("--stills-dir", default=".")
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8")) if args.data else None

    with sync_playwright() as p:
        browser, page, duration, errors = open_page(p, args.html, data, args.width)
        print(f"duration={duration}s fps={args.fps} width={args.width}")
        if args.stills:
            out_dir = Path(args.stills_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            for t in (float(s) for s in args.stills.split(",")):
                (out_dir / f"still_{t:.2f}.png").write_bytes(frame_at(page, t))
            print(f"stills -> {out_dir}")
        if args.sheet:
            n = args.sheet_count
            times = [duration * i / (n - 1) for i in range(n)]
            times[-1] = duration - 1 / args.fps
            contact_sheet([(t, frame_at(page, t)) for t in times], args.sheet, width=args.width)
            print(f"sheet -> {args.sheet}")
        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-filter_threads", "1", "-f", "image2pipe", "-framerate", str(args.fps),
                   "-c:v", "mjpeg", "-i", "-", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                   "-r", str(args.fps), "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                   "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-movflags", "+faststart", str(out)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            n = round(duration * args.fps)
            for i in range(n):
                ff.stdin.write(frame_at(page, i / args.fps, "jpeg"))
            ff.stdin.close()
            if ff.wait() != 0:
                sys.exit("ffmpeg failed")
            print(f"video -> {out} ({n} frames)")
        browser.close()
    if errors:
        print("PAGE ERRORS:\n  " + "\n  ".join(errors))
        sys.exit(2)


if __name__ == "__main__":
    main()
