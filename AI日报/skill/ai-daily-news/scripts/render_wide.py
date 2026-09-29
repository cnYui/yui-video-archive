# AI每日日报宽屏版：从《原LAI如此》scripts/render.py 复制，只改了画面尺寸（原文件不动）。
"""Deterministic frame-by-frame renderer: HTML animation -> MP4 / MOV / stills.

The page must set `window.DURATION` (seconds). Every frame, the renderer pauses all
CSS/Web Animations and seeks them to t, then calls `window.renderAt(t)` if defined.
JSON passed with --data is exposed to the page as `window.__DATA__` before any script runs.

A page error or a font that failed to load makes the script exit with code 2 (after writing output).
This is a low-level tool (it takes an HTML file, not an episode folder); assemble.py calls it for the
intro / outro, render_parallel.py reuses its page-opening code for the main body.

Examples (paths relative to the episode folder; S = SERIES/片头片尾):
  python render.py 制作/engine/index.html --data 制作/timeline.json --stills 10,60,120 --stills-dir 制作/build/stills
  python render.py 制作/engine/index.html --data 制作/timeline.json --sheet 制作/build/check_sheet.png
  python render.py S/outro/index.html -o out/outro.mp4 --data S/outro/data.json --fps 30
  python render.py S/outro/index.html -o out/outro_alpha.mov --alpha        # ProRes 4444 with transparency
"""
import argparse
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
W, H = 2340, 1080          # AI每日日报：iPhone 全面屏 19.5:9（用户 2026-09-27 定）
FONT_CANDIDATES = [Path(__file__).resolve().parent / "fonts" / "JetBrainsMono.ttf",
                   Path(r"D:/大疆/AI科普/素材/字体/JetBrainsMono.ttf")]   # contact-sheet labels only

SEEK_JS = """(t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (typeof window.renderAt === 'function') window.renderAt(t);
}"""


# 图片加载失败的判定（2026-09-28 从《原LAI如此》render.py 移植）：引擎会重试失败的图片（core.js loadImg），
# 救回来的那些 Chromium 照样打 'Failed to load resource'，不算错；重试完还失败的才算页面错误（带文件地址）。
LOAD_FAILED = "Failed to load resource"   # Chromium's console line for a failed request (the text itself has no URL)


def url_key(url):
    """A request URL without query / fragment, percent-decoded (the engine retries an image as <src>?r=N)."""
    s = urlsplit(url or "")
    return unquote(urlunsplit((s.scheme, s.netloc, s.path, "", "")))


def judge_load_failures(lines, requests, retried, failed):
    """Failed loads while the page was opening -> (errors, recovered).
    lines     [(text, url)]  Chromium's 'Failed to load resource: net::…' console lines; url = the message location
                             (Playwright reports the failed resource there; '' if not)
    requests  [(url, why)]   'requestfailed' events
    retried / failed         window.__IMG_RETRIED__ / __IMG_FAILED__ of the engine (None: page without the image retry)
    A failed load is recovered when its URL without the query is in retried and not in failed. errors: one line per
    unrecovered URL (with the URL and how often it failed); recovered: {url: failed attempts}."""
    ok = {url_key(u) for u in retried or []} - {url_key(u) for u in failed or []}
    reason = {}                                # url key -> Chromium's error name (net::ERR_FAILED …)
    for u, w in requests:
        reason.setdefault(url_key(u), w)
    bad, recovered, no_url = Counter(), Counter(), []
    for text, url in lines:
        if url:
            k = url_key(url)
            (recovered if k in ok else bad)[k] += 1
            reason.setdefault(k, text.split(": ", 1)[-1])
        else:
            no_url.append(text)
    if no_url:        # lines without a URL stand for the failed requests that no line with a URL names
        spare = Counter(url_key(u) for u, _ in requests) - Counter(url_key(u) for _, u in lines if u)
        lost = Counter({k: n for k, n in spare.items() if k not in ok})
        if spare and not lost and len(no_url) <= sum(spare.values()):
            recovered.update(spare)            # every one of them was recovered by the engine
        elif lost:
            bad.update(lost)
        else:                                  # nothing to pin them on: keep Chromium's own text
            bad[""] += len(no_url)
            reason[""] = no_url[0].split(": ", 1)[-1]
    errors = [f"failed to load {k or '(URL unknown)'} ({reason.get(k) or 'failed'}{f', {n}x' if n > 1 else ''})"
              for k, n in bad.items()]
    return errors, dict(recovered)


def open_page(p, html, data, alpha, label=""):
    """Open the page, wait until it is ready -> (browser, page, duration, errors).
    errors (strings) keep filling while the page is used (JS errors, console.error, failed loads, with URLs); empty = clean.
    label prefixes the info line about image loads the engine recovered (render_parallel_wide: part name).
    If opening fails (e.g. Page.goto timeout) the browser is closed before the exception propagates."""
    browser = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text", "--font-render-hinting=none"])
    try:
        page, duration, errors = _open(browser, html, data, alpha, label)
    except BaseException:
        try:
            browser.close()
        except Exception:  # noqa: BLE001
            pass
        raise
    return browser, page, duration, errors


def _open(browser, html, data, alpha, label):
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    init = "window.__CAPTURE__ = true;"
    if data is not None:
        init += f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};"
    if alpha:
        init += "window.__ALPHA__ = true;"
    page.add_init_script(init)
    errors, load_lines, failed_requests = [], [], []
    opened = []                                # non-empty once the opening is judged: later failed loads are errors

    def on_console(m):
        if m.type != "error":
            return
        if m.text.startswith(LOAD_FAILED):
            url = (m.location or {}).get("url") or ""
            if opened:
                errors.append(f"{m.text} ({unquote(url)})" if url else m.text)
            else:
                load_lines.append((m.text, url))
        else:
            errors.append(m.text)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", on_console)
    page.on("requestfailed", lambda r: failed_requests.append((r.url, r.failure)))
    page.goto(Path(html).resolve().as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready.then(() => true)")
    page.wait_for_function("window.__READY__ !== false", timeout=15000)
    # the engine's image retry is over by now (__READY__ waits for it): judge the failed loads of the opening
    retried, failed = page.evaluate("[window.__IMG_RETRIED__ || null, window.__IMG_FAILED__ || null]")
    load_errors, recovered = judge_load_failures(load_lines, failed_requests, retried, failed)
    errors += load_errors
    opened.append(True)
    if recovered:
        names = ["/".join(k.rsplit("/", 2)[-2:]) for k in recovered]
        print(f"{label}image loads failed and were retried by the engine: {len(recovered)} image(s), "
              f"{sum(recovered.values())} failed attempt(s), all recovered ({', '.join(names[:6])}"
              f"{' …' if len(names) > 6 else ''})", flush=True)
    duration = page.evaluate("window.DURATION")
    if not isinstance(duration, (int, float)) or duration <= 0:
        sys.exit("page must set window.DURATION (seconds)")
    # Report any font that failed to load (would silently fall back to a system font).
    bad_fonts = page.evaluate("[...document.fonts].filter(f => f.status === 'error').map(f => f.family)")
    if bad_fonts:
        errors.append(f"fonts failed to load: {bad_fonts}")
    return page, float(duration), errors


def frame_at(page, t, alpha):
    page.evaluate(SEEK_JS, t)
    return page.screenshot(type="png", omit_background=alpha, animations="allow")


def contact_sheet(frames, path, cols=4):
    tw, th = 480, 270
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(next((f for f in FONT_CANDIDATES if f.exists()), FONT_CANDIDATES[0])), 18)
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
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", help="HTML page that sets window.DURATION (and window.renderAt)")
    ap.add_argument("-o", "--out", help="output .mp4 (H.264) or .mov (ProRes 4444 when --alpha)")
    ap.add_argument("--data", help="JSON file exposed as window.__DATA__")
    ap.add_argument("--fps", type=int, default=60, help="frames per second (default 60; episodes use 30)")
    ap.add_argument("--alpha", action="store_true", help="transparent background (needs .mov output)")
    ap.add_argument("--audio", help="optional audio file to mux")
    ap.add_argument("--sheet", help="write a contact sheet PNG")
    ap.add_argument("--sheet-count", type=int, default=16, help="frames in the contact sheet (default 16)")
    ap.add_argument("--stills", help="comma-separated times (s) to save as PNG")
    ap.add_argument("--stills-dir", default=".", help="folder for --stills PNGs (default: current folder)")
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
            # -filter_threads 1：同 render_parallel_wide.py（2340 宽时多线程转像素格式会在左边缘出黑点）
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-filter_threads", "1", "-f", "image2pipe", "-framerate", str(args.fps), "-c:v", "png", "-i", "-"]
            if args.audio:
                cmd += ["-i", args.audio, "-c:a", "aac", "-b:a", "320k", "-shortest"]
            if args.alpha:
                cmd += ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"]
            else:
                cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                        # also write BT.709 into the H.264 VUI (otherwise primaries/transfer read as "unknown")
                        "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-movflags", "+faststart"]
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
