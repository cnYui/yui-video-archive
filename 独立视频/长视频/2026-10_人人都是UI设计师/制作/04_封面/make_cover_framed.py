# -*- coding: utf-8 -*-
r"""《人人都是 UI 设计师》封面（框版）：3 个候选 × 三个比例（3:4 竖屏 1080×1440、16:9 1920×1080、4:3 1440×1080）+ 总览。

  python make_cover_framed.py [--only A]

用户 2026-10-05：“封面做的都不行，太丑了，封面图中包含 人人都是UI设计师 这几个字，文字的风格参考这样，白色+橙色（发来的是《Anthropic 设计师怎么用 Claude 做设计》那条的封面），
重新生成封面，封面还需要包含竖屏的封面”。版式 = 短视频技能的“框版”（`短视频/skill/short-video/scripts/make_cover_framed.py`）：
钩子大字在框外（第 1 行白字、第 2 行橙字，黑描边 + 黑色错位阴影）、画面缩进“边框 6”（7 px 黑描边 + 橙色硬阴影 + 右上角倾斜 3° 的黄贴纸）、背景是米白底 + AI 工具图标印花（橙色那张）。
钩子大字就是片名：第 1 行 “人人都是”、第 2 行 “UI设计师”（读起来是“人人都是UI设计师”，每行 ≤ 6 字）。

三个候选的画面（都是文章里的真实对比图，面板位置来自 台本/marks/*.json）：
  A  图 13 下层：✕ 5 个色码硬套出来的黄底红条界面 / ✓ 按色阶配出来的界面（最丑 → 好看，最抓眼）
  B  图 17：✕ 白字压在照片上看不清 / ✓ 垫了半透明蒙版
  C  20 张对比图的 ✓ 半边铺成墙（“20 条军规”）
16:9 和 3:4 里 ✕ / ✓ 上下叠放，4:3 里左右并排；16:9 的内容收在 x 110–1810（B 站首页会把 16:9 切成 16:10）。
素材（图片）是《Refactoring UI》的书内插图经龙海的文章转载，封面 png 不进公开仓库。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent                      # 制作/04_封面
EP = HERE.parents[1]
FONT = Path(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf")        # 变量字体（900 / 700 字重）
IMG = Path(r"D:\大疆\独立视频\素材\2026-10_人人都是UI设计师\图片")
BGDIR = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")
SS = 2
BGC, INK, ORANGE, MARKER, WHITE = (0xFA, 0xF9, 0xF5), (0x14, 0x14, 0x13), (0xFF, 0x4F, 0x1A), (0xFF, 0xD8, 0x4D), (255, 255, 255)
RED, GREEN = (0xEF, 0x44, 0x44), (0x22, 0xA5, 0x59)
PAD, SHADOW, RADIUS, INNER_R = 7, 14, 14, 4
HOOK = ["人人都是", "UI设计师"]

marks = {}
for f in sorted((EP / "台本" / "marks").glob("marks_*.json")):
    marks.update(json.loads(f.read_text(encoding="utf-8")))


def vfont(px, weight):
    f = ImageFont.truetype(str(FONT), int(round(px)))
    f.set_variation_by_axes([weight])
    return f


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


# ───────────────────────── 背景：米白底 + 橙色印花（16:9 / 4:3 用横版印花，3:4 用竖版印花）
def pattern_bg(w, h):
    base = Image.new("RGBA", (w, h), BGC + (255,))
    if w > h or w == 1440:
        pat = Image.open(BGDIR / "landscape_orange.png").convert("RGBA")
        base.alpha_composite(pat.crop((0, 0, w, h)), (0, 0))
    else:
        pat = Image.open(BGDIR / "pattern_orange.png").convert("RGBA")
        base.alpha_composite(pat.crop((0, 300, w, 300 + h)), (0, 0))
    return base.convert("RGB").resize((w * SS, h * SS), Image.LANCZOS)


# ───────────────────────── 框里的画面
def clean_fig13():
    """图 13 的 ✓ 半边（按色阶配出来的界面）被作者叠了一层红色连线（指向下面的色块）——封面上很乱，这里把线抹掉（只动 ✓ 的界面窗口，结果缓存）。
    白底区：粉色（G≈B、R 比 G 高 20–95）逐像素挖掉；蓝色侧栏里线是“R 高、G/B 低于周围中值”；侧栏底部（Archived Channels 下面）是纯色，整块抹平。"""
    import cv2
    import numpy as np
    cache = HERE / "_cache_图13_清线.png"
    if cache.exists():
        return Image.open(cache).convert("RGB")
    src = cv2.imread(str(IMG / "图13_颜色比想象多.jpg"))
    X, Y, W, H = 1400, 876, 1066, 675
    crop = src[Y:Y + H, X:X + W].copy()
    b, g, r = [crop[..., i].astype(int) for i in (0, 1, 2)]
    pink = (r - g > 20) & (r - g < 95) & (np.abs(g - b) < 16) & (r > 190)
    med = cv2.medianBlur(crop, 9).astype(int)
    blue_line = ((r - med[..., 2]) > 14) & ((g - med[..., 1]) < -7) & ((b - med[..., 0]) < -7)
    m = cv2.dilate(((pink | blue_line) * 255).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    out = cv2.inpaint(crop, m, 2, cv2.INPAINT_TELEA)
    out[626:H - 4, 5:318] = (181, 134, 80)          # 侧栏底部纯色（BGR）= RGB (80,134,181)
    src[Y:Y + H, X:X + W] = out
    cv2.imwrite(str(cache), src)
    return Image.open(cache).convert("RGB")


_FIG = {}


def fig(name):
    if name not in _FIG:
        _FIG[name] = clean_fig13() if name.startswith("图13") else Image.open(IMG / name).convert("RGB")
    return _FIG[name]


def panel(name, rect, w=None):
    x, y, pw, ph = rect
    c = fig(name).crop((x, y, x + pw, y + ph))
    if w:
        c = c.resize((w, round(ph * w / pw)), Image.LANCZOS)
    return c


def draw_badge(cv, kind, cx, cy, r):
    """✕ / ✓ 圆形角标（画在整张画布上，骑在画框的左边框上：一半在框里、一半在框外，不挡界面里的字）：黑描边 + 白圈 + 红 / 绿底。cx、cy、r 是封面像素。"""
    s = SS
    d = ImageDraw.Draw(cv)

    def disc(rad, fill):
        d.ellipse(((cx - rad) * s, (cy - rad) * s, (cx + rad) * s, (cy + rad) * s), fill=fill)

    disc(r + 9, INK)
    disc(r + 5, WHITE)
    disc(r, RED if kind == "x" else GREEN)
    k, wd = r * 0.42 * s, max(3, int(r * 0.27 * s))
    cx, cy = cx * s, cy * s
    if kind == "x":
        d.line((cx - k, cy - k, cx + k, cy + k), fill=WHITE, width=wd)
        d.line((cx - k, cy + k, cx + k, cy - k), fill=WHITE, width=wd)
    else:
        d.line((cx - k * 1.05, cy + k * 0.05, cx - k * 0.3, cy + k * 0.8), fill=WHITE, width=wd)
        d.line((cx - k * 0.3, cy + k * 0.8, cx + k * 1.1, cy - k * 0.8), fill=WHITE, width=wd)


def pair(name, rl, rr, mode, pw=900):
    """✕ / ✓ 两个面板 → (拼好的图, 角标位置)。mode = stack 上下叠放（✕ 在上）/ side 左右并排；中间留一条黑缝。
    角标位置是 (kind, x, y)（拼好的图里的像素，x = 0 就是图的左边缘）：画框时画在框的左边框上（✓ 在并排时落在两块之间的黑缝上）。"""
    a, b = panel(name, rl, pw), panel(name, rr, pw)
    h = min(a.height, b.height)
    a, b = a.crop((0, 0, pw, h)), b.crop((0, 0, pw, h))
    gap = 10
    dy = max(56, round(h * 0.11))
    if mode == "stack":
        out = Image.new("RGB", (pw, 2 * h + gap), INK)
        out.paste(a, (0, 0)); out.paste(b, (0, h + gap))
        return out, [("x", 0, dy), ("ok", 0, h + gap + dy)]
    out = Image.new("RGB", (2 * pw + gap, h), INK)
    out.paste(a, (0, 0)); out.paste(b, (pw + gap, 0))
    return out, [("x", 0, dy), ("ok", pw + gap / 2, dy)]


NAMES = {1: "个性", 2: "先灰度后上色", 3: "字号并非万能", 4: "弱化凸显主角", 5: "删冗余标签", 6: "按钮分主次", 7: "过度留白起步", 8: "别撑满屏幕", 9: "间距亲疏", 10: "手机端非等比缩放",
         11: "行长与行高", 12: "基线对齐", 13: "颜色比想象多", 14: "浅底深字", 15: "不只靠颜色", 16: "强调色边框", 17: "图上文字", 18: "适用尺寸", 19: "慎用边框", 20: "空状态"}


def wall(cols=5, rows=4, tw=300, th=200, gap=8):
    out = Image.new("RGB", (cols * tw + (cols - 1) * gap, rows * th + (rows - 1) * gap), INK)
    for n in range(1, cols * rows + 1):
        name = f"图{n:02d}_{NAMES[n]}.jpg"
        st = marks[name]["sets"][-1]
        x, y, pw, ph = st["R"]
        im = fig(name).crop((x, y, x + pw, y + ph))
        s = max(tw / pw, th / ph)
        im = im.resize((round(pw * s), round(ph * s)), Image.LANCZOS)
        ox, oy = (im.width - tw) // 2, (im.height - th) // 2
        c = (n - 1) % cols, (n - 1) // cols
        out.paste(im.crop((ox, oy, ox + tw, oy + th)), (c[0] * (tw + gap), c[1] * (th + gap)))
    return out


def inner_images(key):
    """stack = 16:9 / 3:4 里 ✕ 在上 ✓ 在下的整窗；side = 4:3 里左右并排（每块只取窗口左 3/4：侧栏 + 一部分聊天区，更接近正方形，框才不会太扁）。"""
    if key == "A":
        n = "图13_颜色比想象多.jpg"                     # 窗口坐标：✕ (113,814)，✓ (1400,876)，都是约 1066×675
        return {"stack": pair(n, (113, 814, 1067, 675), (1400, 876, 1066, 675), "stack", 1000),
                "side": pair(n, (113, 814, 812, 675), (1400, 876, 812, 675), "side", 760)}
    if key == "B":
        n = "图17_图上文字.jpg"
        return {"stack": pair(n, (20, 20, 805, 520), (845, 20, 799, 520), "stack", 900),
                "side": pair(n, (20, 20, 640, 520), (845, 20, 640, 520), "side", 700)}
    w = wall()
    return {"stack": (w, []), "side": (w, [])}


# ───────────────────────── 画框、贴纸、大字（和短视频技能的框版同一套）
def draw_sticker(cv, text, right, top, scale):
    f = vfont(30 * SS * scale, 800)
    tw = f.getlength(text)
    pw, ph = int(tw + 40 * SS * scale), int(54 * SS * scale)
    st = Image.new("RGBA", (pw + 8, ph + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle([4, 4, pw + 3, ph + 3], radius=int(8 * SS * scale), fill=MARKER + (255,), outline=INK + (255,), width=max(2, int(3 * SS * scale)))
    d.text((4 + pw / 2, 4 + ph / 2), text, font=f, fill=INK, anchor="mm")
    st = st.rotate(-3, expand=True, resample=Image.BICUBIC)
    cv.paste(st, (int(right * SS - st.width + 10 * SS), int(top * SS - st.height * 0.55)), st)


def draw_frame(cv, inner, x, y, iw, ih, sticker=None, scale=1.0):
    inner, badges = inner
    s = SS
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    shadow = Image.new("L", cv.size, 0)
    shadow.paste(rmask(ow * s, oh * s, RADIUS * s), ((x + SHADOW) * s, (y + SHADOW) * s))
    cv.paste(Image.new("RGB", cv.size, ORANGE), (0, 0), shadow)
    cv.paste(Image.new("RGB", (ow * s, oh * s), INK), (x * s, y * s), rmask(ow * s, oh * s, RADIUS * s))
    cv.paste(inner.resize((iw * s, ih * s), Image.LANCZOS), ((x + PAD) * s, (y + PAD) * s), rmask(iw * s, ih * s, INNER_R * s))
    r = max(26, min(44, round(iw * 0.06)))
    for kind, bx, by in badges:
        draw_badge(cv, kind, x + PAD + bx * iw / inner.width, y + PAD + by * ih / inner.height, r)
    if sticker:
        draw_sticker(cv, sticker, x + ow, y, scale)
    return ow, oh


def measure(lines, avail_w, fs_max):
    fs = fs_max
    while True:
        f = vfont(fs * SS, 900)
        stroke = max(2, round(fs * 0.047 * SS))
        w = max(f.getlength(t) for t in lines) + 2 * stroke
        if w / SS <= avail_w or fs < 90:
            return fs, stroke, f, w / SS
        fs -= 4


def hook_text(cv, lines, accent_line, left, top, avail_w, fs_max, align="left", line_h=1.14):
    s = SS
    fs, stroke, f, bw = measure(lines, avail_w, fs_max)
    sh = round(fs * 0.059 * s)
    d = ImageDraw.Draw(cv)
    pitch = fs * line_h * s
    for i, t in enumerate(lines):
        tw = f.getlength(t)
        x = left * s + (0 if align == "left" else (avail_w * s - tw) / 2 if align == "center" else avail_w * s - tw)
        cy = top * s + pitch * (i + 0.5)
        d.text((x + sh, cy + sh), t, font=f, fill=INK, stroke_width=stroke, stroke_fill=INK, anchor="lm")
        d.text((x, cy), t, font=f, fill=ORANGE if i == accent_line else WHITE, stroke_width=stroke, stroke_fill=INK, anchor="lm")
    return fs, bw, pitch * len(lines) / s


def fit(aspect, max_w, max_h):
    w = max_w
    h = w / aspect
    if h > max_h:
        h, w = max_h, max_h * aspect
    return round(w / 2) * 2, round(h / 2) * 2


def make(inner, stk):
    out = {}
    hook, al = HOOK, 1
    st, sd = inner["stack"], inner["side"]
    st_img, sd_img = st[0], sd[0]
    # 3:4（1080×1440）：钩子在上，框在下
    w, h = 1080, 1440
    cv = pattern_bg(w, h)
    asp = st_img.width / st_img.height
    iw, ih = fit(asp, 920, 800)
    fs = measure(hook, w - 140, 176)[0]
    bh = fs * 1.14 * len(hook)
    gap = 56
    total = bh + gap + ih + 2 * PAD + SHADOW
    top0 = max(70, (h - total) / 2)
    fs, bw, bh = hook_text(cv, hook, al, 70, top0, w - 140, 176, align="center")
    ow = iw + 2 * PAD
    draw_frame(cv, st, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["3x4"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    # 16:9（1920×1080）：字在左，框在右（内容收在 x 110–1810）
    w, h = 1920, 1080
    cv = pattern_bg(w, h)
    iw, ih = fit(asp, 900, 820)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    x0 = 1810 - SHADOW - ow
    avail = x0 - 110 - 40
    fs = measure(hook, avail, 176)[0]
    bh = fs * 1.14 * len(hook)
    fs, bw, bh = hook_text(cv, hook, al, 110, (h - bh) / 2, avail, 176, align="left")
    draw_frame(cv, st, x0, (h - oh - SHADOW) // 2, iw, ih, stk, 0.9)
    out["16x9"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}，框左 {x0}")
    # 4:3（1440×1080）：钩子在上，框在下
    w, h = 1440, 1080
    cv = pattern_bg(w, h)
    asp2 = sd_img.width / sd_img.height
    fs = measure(hook, w - 140, 150)[0]
    bh0 = fs * 1.14 * len(hook)
    gap = 36
    iw, ih = fit(asp2, 1290, h - 2 * PAD - SHADOW - bh0 - gap - 60)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    total = bh0 + gap + oh + SHADOW
    top0 = (h - total) / 2
    fs, bw, bh = hook_text(cv, hook, al, 70, top0, w - 140, 150, align="center")
    draw_frame(cv, sd, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["4x3"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    return out


CANDS = [
    ("A", "图 13：5 个色码硬套的丑界面 → 按色阶配的好界面（最抓眼，推荐）", True, "龙海 · X 长文"),
    ("B", "图 17：白字压在照片上看不清 → 垫半透明蒙版", False, "龙海 · X 长文"),
    ("C", "20 张对比图的 ✓ 半边铺成墙", False, "20 条设计军规"),
]


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    items = []
    for key, note, rec, stk in CANDS:
        if only and key != only:
            continue
        res = make(inner_images(key), stk)
        for k, (im, info) in res.items():
            im.save(HERE / f"封面_{key}_{k}.png")
            print(f"封面_{key}_{k}.png {im.size[0]}×{im.size[1]}：{info}")
        items.append((key, note, rec, res))
    if only:
        return
    rowh, pad = 520, 24
    th = {"3x4": (390, rowh), "16x9": (924, 520), "4x3": (693, 520)}
    W = 40 + sum(v[0] for v in th.values()) + 2 * pad
    sheet = Image.new("RGB", (W, len(items) * (rowh + 70) + 20), (232, 232, 232))
    d = ImageDraw.Draw(sheet)
    lab = vfont(30, 700)
    y = 20
    for key, note, rec, res in items:
        d.text((20, y + 6), f"候选 {key}{'（推荐）' if rec else ''}  ·  {note}", font=lab, fill=INK)
        x = 20
        for k in ("3x4", "16x9", "4x3"):
            im = res[k][0].copy()
            im.thumbnail(th[k])
            sheet.paste(im, (x, y + 56))
            x += th[k][0] + pad
        y += rowh + 70
    sheet.save(HERE / "封面_总览.png")
    print("封面_总览.png", sheet.size)


if __name__ == "__main__":
    main()
