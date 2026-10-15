# -*- coding: utf-8 -*-
r"""短视频的竖版封面（3:4，1080×1440）：照长视频横版封面 D（用户 2026-10-03 确认）的文字和设计——奶油点阵底 + 白框墨边硬投影的方框（里面是官方演示截图，带“官方演示 | Griffin 发布视频”
小标签和“画面：@tavus · X（2026-10-01）”来源角标）+ 粉色大箭头指向 Vanessa + 粉色衬线大字“这是AI！”（墨黑描边 + 硬投影）。

  python make_cover_vertical.py            出 cover_D竖_A_整帧_3x4.png、cover_D竖_B_特写_3x4.png（都是 1080×1440）

两个候选（用户选）：
  A 整帧：和横版封面 D 同一帧（43.28 s，Vanessa 竖大拇指，左上 Hassaan 的小窗，抖动纹理边框），整帧放进方框；竖屏放不下一整行大字 + 大方框，字拆成两行“这是 / AI！”放大。
  B 特写：安静的帧（41.2 s，Vanessa 闭嘴微笑、两手放下），裁成方形、只留她和墙（不要 Hassaan 的小窗），脸放大一倍多；字一行；箭头从右边指向脸。
画面是 Tavus 官方视频的截帧（长视频那期下好的 @tavus 推文视频），裁掉了烧进去的英文字幕（窗口下沿 y=975 以上）；成品 png 不进 git。
方框 / 标签 / 箭头 / 大字的画法借长视频那期的 make_cover_ai.py（同一套颜色、字体、箭头几何），这里只换版式。
"""
import subprocess
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

LONG_COVER = Path(r"D:\大疆\独立视频\2026-10_Tavus-Griffin模型介绍\制作\04_封面")
sys.path.insert(0, str(LONG_COVER))
import make_cover_ai as M          # noqa: E402  arrow_svg / text_css（箭头几何、衬线大字样式）
from make_covers import CSS, GF    # noqa: E402  奶油点阵底、字体

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE / "_src"
VIDEO = M.SRC_VIDEO                # @tavus 推文视频（长视频那期下好的）

INK, PINK, CREAM = "#140206", "#FF6183", "#F7F4EF"

# 版式。win = 在原片 1920×1080 里取的窗口（x0, y0, x1, y1）；face = Vanessa 的脸中心（OpenCV 检出）；
# card = (左, 上, 宽)，高按窗口比例算；k = 方框内一个原片像素 = 多少封面像素；text.lines = 大字几行；s_tag = 小标签的缩放；s_arrow = 箭头的缩放（几何见 make_cover_ai.arrow_svg）
VARIANTS = {
    "A_整帧": dict(t=43.283, win=(93, 0, 1827, 975), face=(1078, 529), card=(40, 760, 1000), shadow=12, frame_pad=12, frame_border=3,
                   text=dict(lines=["这是", "AI！"], cx=540, top=96, fs=300, pitch=0.96), s_tag=0.8, s_arrow=0.663, arrow_ang=-10.5, arrow_gap=186),
    "B_特写": dict(t=41.2, win=(725, 0, 1700, 975), face=(1054, 539), card=(80, 410, 920), shadow=12, frame_pad=14, frame_border=3,
                   text=dict(lines=["这是AI！"], cx=540, top=64, fs=236, pitch=1.0), s_tag=0.85, s_arrow=0.95, arrow_ang=-10.5, arrow_gap=186),
    # 用户 2026-10-04：“把文字缩小一点，放在画框中，画框可以充满整个屏幕”：画框铺满整个封面（四周只留 30 px 放硬投影），大字缩小、放进画框里（盖在画面上方的墙上），箭头从右下指向脸。
    # card = (左, 上, 宽, 高)；win_x0 / win_y = 原片里的窗口左边和上下边，窗口宽按画框内的比例自动算。
    "C_满框_安静": dict(t=41.2, win_y=(0, 975), win_x0=725, face=(1054, 539), card=(30, 30, 1008, 1368), shadow=12, frame_pad=14, frame_border=3,
                      text=dict(lines=["这是AI！"], cx=540, top=150, fs=170, pitch=1.0), s_tag=0.8, s_arrow=0.9, arrow_ang=-35.0, arrow_gap=186),
    "D_满框_大拇指": dict(t=43.283, win_y=(0, 975), win_x0=640, face=(1078, 529), card=(30, 30, 1008, 1368), shadow=12, frame_pad=14, frame_border=3, patch=[(636, 78, 724, 378)],
                      text=dict(lines=["这是AI！"], cx=540, top=150, fs=170, pitch=1.0), s_tag=0.8, s_arrow=0.9, arrow_ang=-42.0, arrow_gap=186, arrow_len=250),
    # 用户 2026-10-04：“用 C 封面来发”——B 站投稿页要 16:9 和 4:3 两个横版，所以把 C 的版式（安静的帧、画框铺满、字缩小放进画框里）也做成横版。
    "E_C风格_16x9": dict(canvas=(1920, 1080), suffix="16x9", t=41.2, win_y=(0, 975), win_x0=55, face=(1054, 539), card=(30, 30, 1860, 1020), shadow=12, frame_pad=14, frame_border=3,
                      text=dict(lines=["这是AI！"], cx=1330, top=130, fs=150, pitch=1.0), s_tag=1.0, s_arrow=1.0, arrow_ang=-12.0, arrow_gap=186, arrow_len=330),
    "F_C风格_4x3": dict(canvas=(1440, 1080), suffix="4x3", t=41.2, win_y=(0, 975), win_x0=190, face=(1054, 539), card=(30, 30, 1380, 1020), shadow=12, frame_pad=14, frame_border=3,
                     text=dict(lines=["这是AI！"], cx=1040, top=130, fs=130, pitch=1.0), s_tag=0.9, s_arrow=0.95, arrow_ang=-12.0, arrow_gap=186, arrow_len=250),
    # 抖音横封面（4:3）被判“封面不佳：请勿使用截屏当封面”（疑似左上 Hassaan 小窗像视频通话截屏）：窗口左边推到 740（小窗右边约 720），通话画面右边在 1740，
    # 所以窗口只剩 997×730 的一块（4:3），全在通话画面里（不带四周的点阵边），只剩 Vanessa 一个人。
    "G_C风格_4x3_无小窗": dict(canvas=(1440, 1080), suffix="4x3", t=41.2, win_y=(110, 840), win_x0=740, face=(1054, 539), card=(30, 30, 1380, 1020), shadow=12, frame_pad=14, frame_border=3,
                     text=dict(lines=["这是AI！"], cx=1040, top=130, fs=130, pitch=1.0), s_tag=0.9, s_arrow=0.95, arrow_ang=-12.0, arrow_gap=225, arrow_len=270),
}


def frame_png(t, win, out_w, patches=()):
    """从原片取第 t 秒整帧，patches = [(x0, y0, x1, y1)] 的区域用它右边同宽的一条墙镜像盖掉（遮住 Hassaan 小窗露在窗口边上的一截），再裁 win、lanczos 缩到宽 out_w。"""
    SRC_DIR.mkdir(exist_ok=True)
    x0, y0, x1, y1 = win
    w, h = x1 - x0, y1 - y0
    out_h = round(out_w * h / w)
    tag = "_".join(str(v) for r in patches for v in r)
    out = SRC_DIR / f"v_{t}_{x0}_{y0}_{x1}_{y1}_{out_w}_{tag}.png"
    full = SRC_DIR / f"full_{t}.png"
    if not full.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(VIDEO), "-frames:v", "1", str(full)], check=True)
    im = Image.open(full).convert("RGB")
    for (px0, py0, px1, py1) in patches:
        im.paste(im.crop((px1, py0, px1 + (px1 - px0), py1)).transpose(Image.FLIP_LEFT_RIGHT), (px0, py0))
    im.crop((x0, y0, x1, y1)).resize((out_w, out_h), Image.LANCZOS).save(out)
    return out, out_w, out_h


def ink_bbox(browser, text, fs):
    """量 text 在字号 fs 下的墨迹框（含描边）：返回 (相对 left 的偏移, 相对 top 的偏移, 宽, 高)。"""
    stroke = round(fs * 0.062)
    pg = browser.new_page(viewport={"width": 2400, "height": 800})
    pg.set_content(f'<meta charset="utf-8"><link rel="stylesheet" href="{GF}"><body style="margin:0;background:transparent">'
                   f'<div style="position:absolute;left:300px;top:200px;{M.text_css(fs)};color:{PINK};-webkit-text-stroke:{stroke * 2}px {INK};paint-order:stroke fill">{text}</div></body>')
    pg.wait_for_timeout(500)
    pg.evaluate("""async () => { await document.fonts.load('900 100px "Noto Serif SC"', '这是AI！'); await document.fonts.ready; }""")
    pg.wait_for_timeout(300)
    png = pg.screenshot(omit_background=True)
    pg.close()
    x0, y0, x1, y1 = Image.open(BytesIO(png)).getchannel("A").getbbox()
    return x0 - 300, y0 - 200, x1 - x0, y1 - y0


def big_text(browser, v):
    t = v["text"]
    fs = t["fs"]
    stroke, off = round(fs * 0.062), round(fs * 0.05)
    html, y = "", t["top"]
    for line in t["lines"]:
        ix, iy, iw, ih = ink_bbox(browser, line, fs)
        left, top = t["cx"] - iw / 2 - ix, y - iy
        base = f"left:{left:.1f}px;top:{top:.1f}px;{M.text_css(fs)}"
        html += (f'<div class="abs" style="{base};color:{INK};-webkit-text-stroke:{stroke * 2}px {INK};transform:translate({off}px,{off}px)">{line}</div>'
                 f'<div class="abs" style="{base};color:{PINK};-webkit-text-stroke:{stroke * 2}px {INK};paint-order:stroke fill">{line}</div>')
        y += fs * t["pitch"]
    return html, y


def card_html(v, img, iw, ih):
    cx, cy, cw = v["card"][:3]
    pad, bd, sh = v["frame_pad"], v["frame_border"], v["shadow"]
    ch = ih + 2 * (pad + bd)                                   # 方框外高 = 图高 + 两边的内边距和边框
    st = v["s_tag"]
    tags = (f'<div style="position:absolute;left:{22 * st:.0f}px;top:{20 * st:.0f}px;display:flex;align-items:stretch;border:{3 * st:.1f}px solid {INK};box-shadow:{5 * st:.0f}px {5 * st:.0f}px 0 {INK};z-index:5">'
            f'<div style="background:{PINK};color:{INK};font:800 {27 * st:.0f}px \'Noto Sans SC\';padding:{7 * st:.0f}px {18 * st:.0f}px;white-space:nowrap">官方演示</div>'
            f'<div style="background:{CREAM};color:{INK};font:700 {24 * st:.0f}px \'Space Grotesk\',\'Noto Sans SC\';padding:{7 * st:.0f}px {18 * st:.0f}px;white-space:nowrap;display:flex;align-items:center;letter-spacing:.03em">Griffin 发布视频</div></div>'
            f'<div style="position:absolute;right:{22 * st:.0f}px;top:{20 * st:.0f}px;background:{INK};color:{CREAM};font:700 {25 * st:.0f}px \'Noto Sans SC\';padding:{8 * st:.0f}px {20 * st:.0f}px;white-space:nowrap;z-index:5;border:{3 * st:.1f}px solid {INK};box-shadow:{5 * st:.0f}px {5 * st:.0f}px 0 {PINK}">画面：@tavus · X（2026-10-01）</div>')
    html = (f'<div class="abs" style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;background:{INK};transform:translate({sh}px,{sh}px)"></div>'
            f'<div class="abs" style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;background:#fff;border:{bd}px solid {INK};padding:{pad}px">'
            f'<div style="position:relative;width:100%;height:100%;overflow:hidden;background:{INK}"><img src="{img.as_uri()}" style="position:absolute;left:0;top:0;width:100%;height:100%;display:block">{tags}</div></div>')
    return html, (cx + bd + pad, cy + bd + pad), ch


def build(browser, name, v):
    W, H = v.get("canvas", (1080, 1440))
    if len(v["card"]) == 4:                                      # 满框版式：画框的宽高都指定，窗口宽按画框内的比例算
        cx, cy, cw, chh = v["card"]
        iw_px = cw - 2 * (v["frame_pad"] + v["frame_border"])
        ih_px = chh - 2 * (v["frame_pad"] + v["frame_border"])
        y0_, y1_ = v["win_y"]
        v["win"] = (v["win_x0"], y0_, v["win_x0"] + round((y1_ - y0_) * iw_px / ih_px), y1_)
    else:
        cx, cy, cw = v["card"]
        iw_px = cw - 2 * (v["frame_pad"] + v["frame_border"])
    img, iw, ih = frame_png(v["t"], v["win"], iw_px, v.get("patch", ()))
    x0, y0, x1, y1 = v["win"]
    k = iw / (x1 - x0)                                          # 一个原片像素 = k 个封面像素
    txt, text_bottom = big_text(browser, v)
    card, (ox, oy), ch = card_html(v, img, iw, ih)
    fx, fy = v["face"]
    face_c = (ox + (fx - x0) * k, oy + (fy - y0) * k)           # 脸中心在封面上的位置
    a = dict(gap=v["arrow_gap"], length=v.get("arrow_len", 318), shaft=52, head_w=134, head_l=108, ang=v["arrow_ang"])
    arrow = f'<svg class="abs" style="left:0;top:0" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{M.arrow_svg(*face_c, v["s_arrow"], a, v["shadow"])}</svg>'
    html = (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{GF}"><style>{CSS}</style>'
            f'<body><div class="cv" style="width:{W}px;height:{H}px"><div class="abs dots" style="left:0;top:0;width:{W}px;height:{H}px"></div>{card}{arrow}{txt}</div></body>')
    f = HERE / f"_cover_D竖_{name}.html"
    f.write_text(html, encoding="utf-8")
    pg = browser.new_page(viewport={"width": W, "height": H})
    pg.goto(f.as_uri())
    pg.wait_for_timeout(800)
    pg.evaluate("""async () => { await document.fonts.load('900 100px "Noto Serif SC"', '这是AI！'); await document.fonts.ready; }""")
    ok = pg.evaluate("[...document.fonts].filter(f => f.status==='loaded').map(f => f.family.replace(/[\"']/g,''))")
    assert "Noto Serif SC" in ok, f"字体没加载到：{set(ok)}"
    pg.wait_for_timeout(300)
    out = HERE / f"cover_D竖_{name}_{v.get('suffix', '3x4')}.png"
    pg.screenshot(path=str(out))
    pg.close()
    tail = card_bottom = cy + ch
    print(f"{out.name}: 大字下沿 y≈{text_bottom:.0f}，方框 y {cy}–{card_bottom}（+投影 {v['shadow']}），脸中心 ({face_c[0]:.0f}, {face_c[1]:.0f})，一个原片像素 = {k:.3f} 封面像素")
    return out


def main():
    want = [a for a in sys.argv[1:] if a in VARIANTS] or list(VARIANTS)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for n in want:
            build(b, n, VARIANTS[n])
        b.close()


if __name__ == "__main__":
    main()
