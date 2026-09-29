"""Deterministic frame-by-frame renderer: HTML animation -> MP4 / MOV / stills.

The page must set `window.DURATION` (seconds). Every frame, the renderer pauses all
CSS/Web Animations and seeks them to t, then calls `window.renderAt(t)` if defined.
JSON passed with --data is exposed to the page as `window.__DATA__` before any script runs.

Examples:
  python render.py outro/index.html -o out/outro.mp4 --data outro/data.json
  python render.py intro/index.html --sheet out/intro_sheet.png            # contact sheet only
  python render.py intro/index.html --stills 0.5,1.2,3.0 --stills-dir out/  # individual frames
  python render.py outro/index.html -o out/outro_alpha.mov --alpha         # ProRes 4444 with transparency
"""
import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

W, H = 1920, 1080

SEEK_JS = """(t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (typeof window.renderAt === 'function') window.renderAt(t);
}"""


def open_page(p, html, data, alpha):
    browser = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text", "--font-render-hinting=none"])
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    init = "window.__CAPTURE__ = true;"
    if data is not None:
        init += f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};"
    if alpha:
        init += "window.__ALPHA__ = true;"
    page.add_init_script(init)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.goto(Path(html).resolve().as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready.then(() => true)")
    page.wait_for_function("window.__READY__ !== false", timeout=15000)
    duration = page.evaluate("window.DURATION")
    if not isinstance(duration, (int, float)) or duration <= 0:
        sys.exit("page must set window.DURATION (seconds)")
    # Report any font that failed to load (would silently fall back to a system font).
    bad_fonts = page.evaluate("[...document.fonts].filter(f => f.status === 'error').map(f => f.family)")
    if bad_fonts:
        errors.append(f"fonts failed to load: {bad_fonts}")
    return browser, page, float(duration), errors


def frame_at(page, t, alpha):
    page.evaluate(SEEK_JS, t)
    return page.screenshot(type="png", omit_background=alpha, animations="allow")


def contact_sheet(frames, path, cols=4):
    tw, th = 480, 270
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(Path(__file__).parent / "fonts" / "JetBrainsMono.ttf"), 18)
    except OSError:
        font = ImageFont.load_default()
    for i, (t, png) in enumerate(frames):
        img = Image.open(io.BytesIO(png)).convert("RGBA")
        bg = Image.new("RGBA", img.size, (128, 128, 128, 255))  # grey shows transparency
        img = Image.alpha_composite(bg, img).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + 28)
        sheet.paste(img, (x, y + 28))
        draw.text((x + 8, y + 4), f"t={t:.2f}s", fill=(230, 230, 230), font=font)
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out", help="output .mp4 (H.264) or .mov (ProRes 4444 when --alpha)")
    ap.add_argument("--data", help="JSON file exposed as window.__DATA__")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--alpha", action="store_true", help="transparent background (needs .mov output)")
    ap.add_argument("--audio", help="optional audio file to mux")
    ap.add_argument("--sheet", help="write a contact sheet PNG")
    ap.add_argument("--sheet-count", type=int, default=16)
    ap.add_argument("--stills", help="comma-separated times (s) to save as PNG")
    ap.add_argument("--stills-dir", default=".")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8")) if args.data else None

    with sync_playwright() as p:
        browser, page, duration, errors = open_page(p, args.html, data, args.alpha)
        print(f"duration={duration}s fps={args.fps}")

        if args.stills:
            out_dir = Path(args.stills_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            for t in (float(s) for s in args.stills.split(",")):
                (out_dir / f"still_{t:.2f}.png").write_bytes(frame_at(page, t, args.alpha))
            print(f"stills -> {out_dir}")

        if args.sheet:
            n = args.sheet_count
            times = [duration * i / (n - 1) for i in range(n)]
            times[-1] = duration - 1 / args.fps  # last real frame
            contact_sheet([(t, frame_at(page, t, args.alpha)) for t in times], args.sheet)
            print(f"sheet -> {args.sheet}")

        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(args.fps), "-c:v", "png", "-i", "-"]
            if args.audio:
                cmd += ["-i", args.audio, "-c:a", "aac", "-b:a", "320k", "-shortest"]
            if args.alpha:
                cmd += ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"]
            else:
                cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart"]
            cmd.append(str(out))
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            total = round(duration * args.fps)
            for i in range(total):
                ff.stdin.write(frame_at(page, i / args.fps, args.alpha))
            ff.stdin.close()
            if ff.wait() != 0:
                sys.exit("ffmpeg failed")
            print(f"video -> {out} ({total} frames)")

        browser.close()

    if errors:
        print("PAGE ERRORS:\n  " + "\n  ".join(errors))
        sys.exit(2)


if __name__ == "__main__":
    main()
