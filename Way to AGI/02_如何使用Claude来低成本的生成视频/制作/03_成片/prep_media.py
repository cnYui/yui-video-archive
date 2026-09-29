# -*- coding: utf-8 -*-
"""成片素材：出镜画面逐帧、GPT-6 建模全片、四个作品片段（按口播里的出场时刻截取）、片尾动画逐帧。先跑 build_timeline.py。

  python prep_media.py            全部
  python prep_media.py show       只重做作品片段（改了 timeline 的 show 以后）
  python prep_media.py credits    只重做片尾（改了片尾清单以后）
其余图片（表情表、日报截图、调色板、检查图、屏幕录制帧……）直接用 00_整片/media 里的，不再复制。
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                  # 教程_Claude做视频/
SERIES = Path(r"D:\大疆\AI科普")                     # 《原LAI如此》系列目录（第 4 期原片、片尾页）
MEDIA = HERE / "media"
TL = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
FPS = TL["fps"]
INNER_W = 1474                                          # 作品展示画框内宽（和 index.html 一致）

SHOW_SRC = {                                            # 片段来源和起点（第 4 期的起点按窗口长度倒推，让它停在“给到：夯。”之后）
    "gintama": (ROOT / "素材/展示视频/03_银魂_像素风.mp4", 60.5, 16 / 9),
    "naruto": (ROOT / "素材/展示视频/01_火影_像素风.mp4", 228.5, 16 / 9),
    "jojo": (ROOT / "素材/展示视频/02_JoJo第三部_像素风.mp4", 254.5, 16 / 9),
    "ep04": (SERIES / "第04期_大模型从夯到拉/第04期_大模型从夯到拉_成片.mp4", None, 2340 / 1080),
}
EP04_END = 165.6                                        # 第 4 期成片里“给到：夯。”念完（165.27 s）

# 片尾清单：沿用系列片尾的默认三项，剪辑一项改成这期实际用的 Claude Code；签名写“悠一”（待用户确认）
CREDITS = {
    "items": [
        {"label": "拍摄", "value": "Pocket 4P"},
        {"label": "剪辑", "value": "Claude Code"},
        {"label": "视频剪辑模型", "value": "Opus 5.5"},
    ],
    "closing": "感谢大家看到最后",
    "signature": "悠一",
}


def run(args):
    subprocess.run([str(a) for a in args], check=True, capture_output=True)


def show_ss(key, it):
    src, ss, aspect = SHOW_SRC[key]
    if ss is None:
        ss = round(EP04_END - (it["t1"] - it["t0"]), 3)
    return src, ss, aspect


def cam():
    d = MEDIA / "cam"
    d.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", HERE.parent / "02_出镜/edit/facecam.mp4", "-fps_mode", "passthrough", "-q:v", "3", d / "f_%05d.jpg"])
    print("cam:", len(list(d.glob("f_*.jpg"))), "frames")


def gpt6():
    d = MEDIA / "gpt6_full"
    d.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", ROOT / "素材/GPT6建模/GPT6建模_原片30s.mp4",
         "-vf", "fps=30,scale=1200:675:flags=lanczos", "-q:v", "2", d / "f_%03d.jpg"])
    print("gpt6_full:", len(list(d.glob("f_*.jpg"))), "frames")


def show():
    info = {}
    for it in TL["show"]["items"]:
        key = it["key"]
        src, ss, aspect = show_ss(key, it)
        h = round(INNER_W / aspect)
        h += h % 2
        d = MEDIA / "show" / key
        if d.exists() and any(d.iterdir()):                 # 旧帧挪进 media/_旧/，不删
            old = MEDIA / "_旧" / f"show_{key}_{time.strftime('%H%M%S')}"
            old.parent.mkdir(parents=True, exist_ok=True)
            d.rename(old)
        d.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", "-ss", ss, "-t", it["n"] / FPS + 0.5, "-i", src,
             "-vf", f"fps={FPS},scale={INNER_W}:{h}:flags=lanczos", "-frames:v", it["n"], "-q:v", "2", d / "f_%04d.jpg"])
        info[key] = {"ss": ss, "frames": len(list(d.glob("f_*.jpg"))), "size": [INNER_W, h]}
        print("show", key, info[key])
    (MEDIA / "show" / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")


def credits():
    """片尾动画：用系列片尾页面（AI科普/片头片尾/outro），按 2340×1080 逐帧截图（和 add_to_video.py 的 render_part 同一套做法）。"""
    from playwright.sync_api import sync_playwright
    html = SERIES / "片头片尾/outro/index.html"
    d = MEDIA / "credits"
    d.mkdir(parents=True, exist_ok=True)
    seek = """(t) => {
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
      if (typeof window.renderAt === 'function') window.renderAt(t);
    }"""
    data = dict(CREDITS, canvas=[2340, 1080])
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": 2340, "height": 1080})
        page.add_init_script("window.__CAPTURE__ = true; window.__CANVAS__ = [2340, 1080]; "
                             f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};")
        page.goto(html.resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_function("window.__READY__ !== false", timeout=15000)
        dur = float(page.evaluate("window.DURATION"))
        n = round(dur * FPS)
        for i in range(n):
            page.evaluate(seek, i / FPS)
            page.screenshot(path=str(d / f"f_{i + 1:03d}.jpg"), type="jpeg", quality=95, animations="allow")
        browser.close()
    print(f"credits: {n} frames ({dur}s)")


if __name__ == "__main__":
    what = sys.argv[1:] or ["cam", "gpt6", "show", "credits"]
    for w in what:
        {"cam": cam, "gpt6": gpt6, "show": show, "credits": credits}[w]()
