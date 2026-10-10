# -*- coding: utf-8 -*-
"""日报竖屏版渲染（从短视频技能的 render_all.py 改的）：逐帧 renderAt(t) 截图交给 ffmpeg，N 路并行，最后拼接、混入 audio/mix.wav。

  python render_v.py --check                    量字幕 / 标题 / 要点的真实宽度（中英各 ≤ 940 px，左右各留 ≥ 70 px），报字号被缩小的地方
  python render_v.py --stills 0 5 30 …          出这些时刻的静帧 + 联系表（stills/）
  python render_v.py --stills-segs              每个场景出 3 张
  python render_v.py                            整片 → 整片_v1.mp4（RENDER_WORKERS 路并行，默认 4；空闲内存 < 6 GB 或别的会话在渲染就降）
  python render_v.py --worker K A B && python render_v.py --concat      只重渲第 K 路，再拼接
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "整片_v1.mp4"
WORKERS = int(os.environ.get("RENDER_WORKERS", "4"))


def tl():
    s = (HERE / "tl_v.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


def open_page(p):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 2340})
    errors = []
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.goto((HERE / "index.html").as_uri())
    page.evaluate("window.READY")
    return browser, page, errors


def page_errors(page, errors):
    return errors + page.evaluate("window.__ERR")


def worker(k, a, b):
    from playwright.sync_api import sync_playwright
    parts = HERE / "parts"
    parts.mkdir(exist_ok=True)
    out = parts / f"part_{k}.mp4"
    with sync_playwright() as p:
        browser, page, errors = open_page(p)
        fps = page.evaluate("window.META.FPS")
        enc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-filter_threads", "1", "-vf", "format=yuv420p", "-c:v", "libx264", "-threads", "3", "-crf", "16", "-preset", "medium",
             "-r", str(fps), str(out)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(a, b):
            page.evaluate(f"renderAt({i / fps})")
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if (i - a) % 600 == 0:
                print(f"[w{k}] {i - a}/{b - a} ({time.time() - t0:.0f}s)", flush=True)
        enc.stdin.close()
        enc.wait()
        errs = page_errors(page, errors)
        browser.close()
    (parts / f"part_{k}.json").write_text(json.dumps({"a": a, "b": b, "errors": errs}, ensure_ascii=False), encoding="utf-8")
    print(f"[w{k}] done {b - a} frames in {time.time() - t0:.0f}s, errors: {len(errs)}", flush=True)


def stills(times, tag=""):
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageDraw, ImageFont
    d = HERE / "stills"
    d.mkdir(exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser, page, errors = open_page(p)
        for t, label in times:
            page.evaluate(f"renderAt({t})")
            f = d / f"t{t:07.2f}.png"
            page.screenshot(path=str(f))
            files.append((f, label))
        errs = page_errors(page, errors)
        warn = page.evaluate("window.__WARN")
        browser.close()
    print("errors:", errs or "none", "| 缩小字号的地方:", warn or "无")
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 24)
    W, H, cols = 300, 650, 6
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


def check():
    from playwright.sync_api import sync_playwright
    T = tl()
    with sync_playwright() as p:
        browser, page, errors = open_page(p)
        js = """(subs) => {
          const m = (txt, font) => { const s = document.createElement('span'); s.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + font + ';-webkit-text-stroke:0'; s.textContent = txt; document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return w; };
          return subs.map(x => [m(x.zh, "800 52px 'Noto Sans SC'"), m(x.en, "600 30px 'Noto Sans SC'")]);
        }"""
        widths = page.evaluate(js, T["subs"])
        warn = page.evaluate("window.__WARN")
        errs = page_errors(page, errors)
        browser.close()
    bad = []
    for x, (zw, ew) in zip(T["subs"], widths):
        if zw > 940 or ew > 940:
            bad.append((x["s"], zw, ew, x["zh"], x["en"]))
    mz, me = max(w[0] for w in widths), max(w[1] for w in widths)
    print(f"字幕 {len(widths)} 条：中文最宽 {mz:.0f} px、英文最宽 {me:.0f} px（上限 940）；超宽 {len(bad)} 条")
    for s, zw, ew, zh, en in bad:
        print(f"  {s:7.2f}s 中文 {zw:.0f} / 英文 {ew:.0f}：{zh} / {en}")
    print("缩小字号的地方:", warn or "无")
    print("页面错误:", errs or "无")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--stills-segs", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--worker", nargs=3, type=int)
    ap.add_argument("--concat", action="store_true")
    args = ap.parse_args()
    T = tl()
    if args.check:
        check()
        return
    if args.worker:
        worker(*args.worker)
        return
    if args.stills:
        stills([(t, f"{t:.2f}s") for t in args.stills], "_t")
        return
    if args.stills_segs:
        ts = []
        for s in T["scenes"]:
            for f in (0.06, 0.5, 0.94):
                t = round(s["s"] + (s["e"] - s["s"]) * f, 2)
                ts.append((t, f"{s['id']} {s['kind']} @{t:.1f}s"))
        stills(ts, "_segs")
        return
    fps, n = T["fps"], T["frames"]
    cuts = [round(n * i / WORKERS) for i in range(WORKERS + 1)]
    t0 = time.time()
    if not args.concat:
        procs = []
        for k in range(WORKERS):
            procs.append(subprocess.Popen([sys.executable, __file__, "--worker", str(k), str(cuts[k]), str(cuts[k + 1])]))
            time.sleep(0.7)
        for pr in procs:
            pr.wait()
    errs = []
    for k in range(WORKERS):
        info = json.loads((HERE / "parts" / f"part_{k}.json").read_text(encoding="utf-8"))
        errs += info["errors"]
    if errs:
        print("PAGE ERRORS:", *errs[:20], sep="\n  ")
        sys.exit(1)
    lst = HERE / "parts" / "list.txt"
    lst.write_text("".join(f"file 'part_{k}.mp4'\n" for k in range(WORKERS)), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(HERE / "audio" / "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(OUT)], check=True)
    print(f"ok -> {OUT}  ({n} frames, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
