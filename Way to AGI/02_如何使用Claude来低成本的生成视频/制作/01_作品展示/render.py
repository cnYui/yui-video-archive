# -*- coding: utf-8 -*-
"""逐帧渲染作品展示段：Playwright 打开 index.html，每一帧调用 renderAt(t) 再截图，交给 ffmpeg 编码，最后混入 audio/mix.wav。

用法：python render.py                 → 01_作品展示.mp4（2340×1080，30 fps）
      python render.py --stills 0.3 3 5.8 12.5 17.3 20   → 只出这些时刻的静帧到 stills/
"""
import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "01_作品展示.mp4"


def open_page(p):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 2340, "height": 1080})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto((HERE / "index.html").as_uri())
    page.evaluate("document.fonts.ready.then(() => true)")
    return browser, page, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    args = ap.parse_args()

    with sync_playwright() as p:
        browser, page, errors = open_page(p)
        meta = page.evaluate("window.META")
        fps, total = meta["FPS"], meta["TOTAL"]

        if args.stills:
            d = HERE / "stills"
            d.mkdir(exist_ok=True)
            for t in args.stills:
                page.evaluate(f"renderAt({t})")
                page.screenshot(path=str(d / f"t{t:06.2f}.png"))
            browser.close()
            print("stills ->", d, "errors:", errors or "none")
            return

        n = int(round(total * fps))
        silent = HERE / "_video_only.mp4"      # 中间文件（无声），重跑时覆盖
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-filter_threads", "1", "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-r", str(fps), str(silent)],
            stdin=subprocess.PIPE)
        for i in range(n):
            page.evaluate(f"renderAt({i / fps})")
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % 90 == 0:
                print(f"frame {i}/{n}", flush=True)
        enc.stdin.close()
        enc.wait()
        browser.close()
        if errors:
            print("PAGE ERRORS:", errors)
            sys.exit(1)

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(HERE / "audio" / "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(OUT)], check=True)
    print("ok ->", OUT)


if __name__ == "__main__":
    main()
