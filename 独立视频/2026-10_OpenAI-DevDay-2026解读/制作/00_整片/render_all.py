# -*- coding: utf-8 -*-
"""整片渲染：4 路并行（用户 2026-09-28 定的统一标准），每路一段帧，逐帧 renderAt(t) 截图交给 ffmpeg，最后拼接、混入 audio/mix.wav。
从《白宫超级智能协定》的 render_all.py 改的：多了一个 ep 参数，输出 out/<ep>/<ep>_整片.mp4。

用法：
  python render_all.py V1                          → out/V1/V1_整片.mp4（正片，不含片头片尾）
  python render_all.py V1 --stills 12.5 30 …       → out/V1/stills/ 里出这些时刻的静帧 + 联系表
  python render_all.py V1 --stills-segs            → 每段出 3 张（开头、中间、结尾）+ 联系表
  python render_all.py V1 --worker K A B && python render_all.py V1 --concat   → 只重渲第 K 路，再拼接
开渲前先确认没有别的会话在渲染（同一时间只跑一个渲染）。
"""
import argparse
import json
import os
import subprocess
import sys
import time

from common import HERE, out_dir

WORKERS = int(os.environ.get("RENDER_WORKERS", 4))     # 标准是 4 路；别的会话的 whisper 占着内存、空闲 < 6 GB 时设 RENDER_WORKERS=3（--concat 也要带同样的变量）


def tl(od):
    s = (od / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


def open_page(p, ep):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 2340, "height": 1080})
    errors = []
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.goto((HERE / "index.html").as_uri() + f"?ep={ep}")
    page.evaluate("document.fonts.ready.then(() => true)")
    return browser, page, errors


def page_errors(page, errors):
    return errors + page.evaluate("window.__ERR")


def worker(ep, k, a, b):
    from playwright.sync_api import sync_playwright
    parts = out_dir(ep) / "parts"
    parts.mkdir(exist_ok=True)
    out = parts / f"part_{k}.mp4"
    with sync_playwright() as p:
        browser, page, errors = open_page(p, ep)
        fps = page.evaluate("window.META.FPS")
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-filter_threads", "1", "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-r", str(fps), str(out)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(a, b):
            page.evaluate(f"renderAt({i / fps})")
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if (i - a) % 600 == 0:
                print(f"[{ep} w{k}] {i - a}/{b - a} ({time.time() - t0:.0f}s)", flush=True)
        enc.stdin.close()
        enc.wait()
        errs = page_errors(page, errors)
        browser.close()
    (parts / f"part_{k}.json").write_text(json.dumps({"a": a, "b": b, "errors": errs}, ensure_ascii=False), encoding="utf-8")
    print(f"[{ep} w{k}] done {b - a} frames in {time.time() - t0:.0f}s, errors: {len(errs)}", flush=True)


def stills(ep, times, tag=""):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw, ImageFont
    d = out_dir(ep) / "stills"
    d.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser, page, errors = open_page(p, ep)
        for t, label in times:
            page.evaluate(f"renderAt({t})")
            f = d / f"t{t:07.2f}.png"
            page.screenshot(path=str(f))
            files.append((f, label))
        errs = page_errors(page, errors)
        browser.close()
    print("errors:", errs or "none")
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 24)
    W, H, cols = 780, 360, 3
    for n in range(0, len(files), 12):
        chunk = files[n:n + 12]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (W + 10) + 10, rows * (H + 44) + 10), "#C9CDD3")
        dr = ImageDraw.Draw(sheet)
        for j, (f, label) in enumerate(chunk):
            x, y = 10 + (j % cols) * (W + 10), 10 + (j // cols) * (H + 44)
            dr.text((x, y), label, fill="#111", font=font)
            sheet.paste(Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS), (x, y + 34))
        out = d / f"_sheet{tag}_{n // 12 + 1}.png"
        sheet.save(out)
        print("sheet ->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--stills-segs", action="store_true")
    ap.add_argument("--worker", nargs=3, type=int)
    ap.add_argument("--concat", action="store_true")
    args = ap.parse_args()
    ep = args.ep
    od = out_dir(ep)
    T = tl(od)
    if args.worker:
        worker(ep, *args.worker)
        return
    if args.stills:
        stills(ep, [(t, f"{t:.2f}s") for t in args.stills], "_t")
        return
    if args.stills_segs:
        ts = []
        for i, s in enumerate(T["segs"]):
            for f in (0.08, 0.5, 0.92):
                t = round(s["s"] + (s["e"] - s["s"]) * f, 2)
                ts.append((t, f"{s['id']} {s['kind']} {s['title']} @{t:.1f}s"))
        stills(ep, ts, "_segs")
        return
    fps, n = T["fps"], T["frames"]
    cuts = [round(n * i / WORKERS) for i in range(WORKERS + 1)]
    t0 = time.time()
    if not args.concat:
        procs = []
        for k in range(WORKERS):
            procs.append(subprocess.Popen([sys.executable, __file__, ep, "--worker", str(k), str(cuts[k]), str(cuts[k + 1])]))
            time.sleep(0.7)
        for pr in procs:
            pr.wait()
    errs = []
    for k in range(WORKERS):
        info = json.loads((od / "parts" / f"part_{k}.json").read_text(encoding="utf-8"))
        errs += info["errors"]
    if errs:
        print("PAGE ERRORS:", *errs[:20], sep="\n  ")
        sys.exit(1)
    lst = od / "parts" / "list.txt"
    lst.write_text("".join(f"file 'part_{k}.mp4'\n" for k in range(WORKERS)), encoding="utf-8")
    out = od / f"{ep}_整片.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(od / "audio" / "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(out)], check=True)
    print(f"ok -> {out}  ({n} frames, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
