# -*- coding: utf-8 -*-
r"""封面 D「这是AI！」——用户 2026-10-03 点名的版式：用他贴的那张成片截图（Griffin 发布视频里 Vanessa 竖大拇指那一帧，成片 29.63 s）
+ 粉色大箭头指向 Vanessa + 大字“这是AI！”。前三版 A / B / C（make_covers.py）用户都不满意，不再用。

  python make_cover_ai.py            出 封面_D_16x9.png（1920×1080）和 封面_D_4x3.png（1440×1080），并复制成 封面_选定_*.png

做法：
 1. 截图里的画面 = 引擎里 D1 场景的第 463 帧（素材 gr 的 27.85 s + 463/30 = 43.28 s，裁掉烧录字幕和左右各 4.87%）。成片里这块画面是 1474×829，
    直接放大会糊，所以回原片（1920×1080）抽同一帧，按封面里要的大小 lanczos 缩好，再用引擎页面（index.html，renderAt）渲出“方框 + 官方演示小标签 + 画面来源”，
    把图换成高清的那张，截 #demo 元素（设备像素比按封面里的缩放来，字和边框都是原生清晰度）。
 2. 封面页：奶油点阵底 + 方框（硬投影）+ 粉色箭头（硬投影）+ 粉色衬线大字（墨黑描边 + 硬投影）。箭头对准 Vanessa 的脸（OpenCV 在成片帧上检出：脸中心 (857, 468)，宽 265，
    都是 #demo 里的坐标）。
 B 站首页卡片会把 16:9 裁成 16:10（左右各切约 96 px）：方框收在 x 96–1824 之内，小标签、字、箭头都不会被切；4:3 单独排版（字在上、方框在下）。
素材 / 成品都是 Tavus 官方画面，_src 和成品 png 不进 git。
"""
import math
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from make_covers import CSS, GF

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
ENGINE = HERE.parent / "00_整片" / "index.html"
SRC_VIDEO = EP / "素材" / "X平台视频" / "tavus_2105704169009246248.mp4"
SRC_DIR = HERE / "_src"

# 用户截图 = 引擎 D1 场景的第 463 帧（D1：时间轴 9.39–26.49 s，素材 in = 27.85 s，30 fps）；TL_T = 24.82 s 是引擎时间轴上的时刻（成片里再加 4.8 s 片头 = 29.63 s）
D1_IN, D1_FRAME, TL_T = 27.85, 463, 9.39 + 463 / 30
CROP = "crop=iw*0.90260:ih*0.90280:iw*0.04870:ih*0.00000"   # = common.SRC_CROP["gr"]
FRAME_W, FRAME_H = 1508, 863                              # #demo 的页面尺寸（边框 3 + 内边距 14 + 内容 1474×829）
FACE = (857, 468)                                         # Vanessa 的脸中心（#demo 坐标）；脸宽 265；发际线最高 y≈295，右侧头发到 x≈1000（y 470）、≈1075（y 620）

# 版式（每种比例一套）：card_w = 方框在封面里的宽；card_xy = 方框左上角；shadow = 方框硬投影；
# text = 大字：cx = 字（含描边）的水平中心，top = 字（含描边、不含投影）的上沿，fs = 字号（量字的墨迹框来摆，不靠猜行高）；
# arrow：gap = 箭头尖离脸中心多远，length / shaft / head_w / head_l = 箭身长 / 粗、箭头宽 / 长（#demo 坐标的数，按缩放换算），ang = 箭身的倾角
LAYOUTS = {
    "16x9": dict(size=(1920, 1080), card_w=1728, card_xy=(96, 39), text=dict(cx=1110, top=160, fs=184), shadow=14,
                 arrow=dict(gap=186, length=318, shaft=52, head_w=134, head_l=108, ang=-10.5)),
    "4x3": dict(size=(1440, 1080), card_w=1320, card_xy=(60, 306), text=dict(cx=720, top=22, fs=236), shadow=11,
                arrow=dict(gap=186, length=318, shaft=52, head_w=134, head_l=108, ang=-10.5)),
}


def hires_frame(w, h):
    """从原片抽第 463 帧（先裁掉烧录字幕），lanczos 缩到 w×h，返回 png 路径。"""
    SRC_DIR.mkdir(exist_ok=True)
    big = SRC_DIR / "gr_d1_463_crop.png"
    if not big.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{D1_IN}", "-i", str(SRC_VIDEO), "-vf", f"fps=30,select='eq(n\\,{D1_FRAME})',{CROP}",
                        "-frames:v", "1", str(big)], check=True)
    out = SRC_DIR / f"gr_d1_463_{w}x{h}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(big), "-vf", f"scale={w}:{h}:flags=lanczos", str(out)], check=True)
    return out


def render_frame(browser, card_w):
    """引擎页面按 card_w/1508 的设备像素比渲出 #demo（小标签、画面来源都是引擎自己画的），画面换成高清帧。"""
    s = card_w / FRAME_W
    iw, ih = round(1474 * s), round(829 * s)
    img = hires_frame(iw, ih)
    pg = browser.new_page(viewport={"width": 2340, "height": 1080}, device_scale_factor=s)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(ENGINE.as_uri())
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.evaluate(f"renderAt({TL_T})")
    pg.evaluate("""async (u) => { const im = document.getElementById('scrimg');
        await new Promise((ok, bad) => { im.onload = ok; im.onerror = bad; im.src = u; }); await im.decode(); }""", img.as_uri())
    pg.wait_for_timeout(300)
    out = SRC_DIR / f"demo_{card_w}.png"
    pg.locator("#demo").screenshot(path=str(out))
    e = pg.evaluate("window.__ERR || []")
    pg.close()
    if errs or [x for x in e if "字体" not in x]:
        print("引擎页面报错：", errs, e)
    return out, s


def ink_box(browser, fs):
    """量一下“这是AI！”在字号 fs 下的墨迹框（含描边）：返回 (相对 left 的偏移 x0, 相对 top 的偏移 y0, 宽, 高)。"""
    stroke = round(fs * 0.062)
    pg = browser.new_page(viewport={"width": 2000, "height": 700})
    pg.set_content(f'<meta charset="utf-8"><link rel="stylesheet" href="{GF}"><body style="margin:0;background:transparent">'
                   f'<div style="position:absolute;left:300px;top:200px;{text_css(fs)};color:#FF6183;-webkit-text-stroke:{stroke * 2}px #140206;paint-order:stroke fill">{TEXT}</div></body>')
    pg.wait_for_timeout(500)
    pg.evaluate("""async () => { await document.fonts.load('900 100px "Noto Serif SC"', '这是AI！'); await document.fonts.ready; }""")
    pg.wait_for_timeout(300)
    png = pg.screenshot(omit_background=True)
    pg.close()
    from io import BytesIO
    from PIL import Image
    x0, y0, x1, y1 = Image.open(BytesIO(png)).getchannel("A").getbbox()
    return x0 - 300, y0 - 200, x1 - x0, y1 - y0


TEXT = "这是AI！"


def text_css(fs):
    return f"font-size:{fs}px;line-height:1.05;white-space:nowrap;font-family:'Noto Serif SC',serif;font-weight:900;letter-spacing:-.01em"


def arrow_svg(cx, cy, s, a, shadow):
    """块状箭头（直角，官网风格）。tip = 脸中心沿 -方向退 gap；方向角 ang：从箭尾指向箭头的方向，0 = 朝左，负 = 朝右上来的。返回 svg 片段（含硬投影）。"""
    ang = math.radians(a["ang"])
    ux, uy = -math.cos(ang), math.sin(ang)           # 从箭尾指向箭头：朝左，ang<0 → 箭尾在右上
    # 朝向脸中心：箭头方向 = 单位向量 (ux, uy)；tip = face - u * gap（贴着脸，留一点空）
    tipx, tipy = cx - ux * a["gap"] * s, cy - uy * a["gap"] * s
    L, t, w, hl = (a[k] * s for k in ("length", "shaft", "head_w", "head_l"))
    local = [(0, 0), (-hl, w / 2), (-hl, t / 2), (-L, t / 2), (-L, -t / 2), (-hl, -t / 2), (-hl, -w / 2)]
    nx, ny = -uy, ux

    def pts(dx, dy):
        return " ".join(f"{tipx + x * ux + y * nx + dx:.1f},{tipy + x * uy + y * ny + dy:.1f}" for x, y in local)
    sw = 9
    return (f'<polygon points="{pts(shadow, shadow)}" fill="#140206" stroke="#140206" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<polygon points="{pts(0, 0)}" fill="#FF6183" stroke="#140206" stroke-width="{sw}" stroke-linejoin="round"/>')


def cover(layout, demo_png, s, ink):
    w, h = layout["size"]
    cx0, cy0 = layout["card_xy"]
    cw = layout["card_w"]
    ch = round(FRAME_H * s)
    sh = layout["shadow"]
    fx, fy = FACE
    face_c = (cx0 + fx * s, cy0 + fy * s)
    t = layout["text"]
    fs = t["fs"]
    stroke = round(fs * 0.062)
    off = round(fs * 0.05)
    ix, iy, iw, ih = ink
    tl, tt = t["cx"] - iw / 2 - ix, t["top"] - iy                  # 元素左上角：让墨迹框的中心 / 上沿落在 cx / top
    txt = TEXT
    base = f"left:{tl:.1f}px;top:{tt:.1f}px;{text_css(fs)}"
    return (f'<div class="abs dots" style="left:0;top:0;width:{w}px;height:{h}px"></div>'
            f'<div class="abs" style="left:{cx0}px;top:{cy0}px;width:{cw}px;height:{ch}px;background:#140206;transform:translate({sh}px,{sh}px)"></div>'
            f'<img class="abs" src="{demo_png.as_uri()}" style="left:{cx0}px;top:{cy0}px;width:{cw}px;height:{ch}px;display:block">'
            f'<svg class="abs" style="left:0;top:0" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{arrow_svg(*face_c, s, layout["arrow"], sh)}</svg>'
            f'<div class="abs" style="{base};color:#140206;-webkit-text-stroke:{stroke * 2}px #140206;transform:translate({off}px,{off}px)">{txt}</div>'
            f'<div class="abs" style="{base};color:#FF6183;-webkit-text-stroke:{stroke * 2}px #140206;paint-order:stroke fill">{txt}</div>')


def main():
    want = [a for a in sys.argv[1:] if a in LAYOUTS] or list(LAYOUTS)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for tag in want:
            L = LAYOUTS[tag]
            demo, s = render_frame(b, L["card_w"])
            ink = ink_box(b, L["text"]["fs"])
            w, h = L["size"]
            print(f"{tag}: 字墨迹框 宽 {ink[2]} 高 {ink[3]}（不含投影），方框下沿 {L['card_xy'][1] + round(FRAME_H * s)}，字下沿 {L['text']['top'] + ink[3]}")
            pg = b.new_page(viewport={"width": w, "height": h})
            html = (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{GF}"><style>{CSS}</style>'
                    f'<body><div class="cv" style="width:{w}px;height:{h}px">{cover(L, demo, s, ink)}</div></body>')
            f = HERE / f"_cover_D_{tag}.html"
            f.write_text(html, encoding="utf-8")
            pg.goto(f.as_uri())
            pg.wait_for_timeout(800)
            pg.evaluate("""async () => { await document.fonts.load('900 100px "Noto Serif SC"', '这是AI！'); await document.fonts.ready; }""")
            ok = pg.evaluate("[...document.fonts].filter(f => f.status==='loaded').map(f => f.family.replace(/[\"']/g,''))")
            assert "Noto Serif SC" in ok, f"字体没加载到：{set(ok)}"
            pg.wait_for_timeout(300)
            out = HERE / f"封面_D_{tag}.png"
            pg.screenshot(path=str(out))
            print("->", out.name)
            pg.close()
        b.close()


if __name__ == "__main__":
    main()
