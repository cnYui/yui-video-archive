# -*- coding: utf-8 -*-
"""ui.py —— 2340×1080 横版长视频的小部件（全是 PIL 画的精灵，合成引擎和版式样板图都用它）。

版式（见 页面设计.md）：三栏 + 底部字幕带
    左栏 L（出镜框 + 本期目录）| 中栏 C（主画面 + 下面一条说明带）| 右栏 R（副素材）
    要摊开的素材（图集、对照表）把 C 和 R 并成一块宽板。字幕在 y 922 以下（中英双语标准），内容都在 y ≤ 899。
画板的样子照封面框版：INK 粗黑边 + 橙色硬阴影 + 黄色贴纸（标出这块素材是什么）。
颜色沿用 独立视频 引擎：--ink #1B1B1F / --accent #FF4F1A / --marker #FFD84D。
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
W, H, FPS = 2340, 1080, 60

INK = (27, 27, 31)
INK2 = (55, 65, 81)
GRAY = (107, 114, 128)
GRAY2 = (154, 161, 172)
LINE = (229, 231, 235)
SOFT = (244, 245, 247)
ORANGE = (255, 79, 26)
MARKER = (255, 216, 77)
GREEN = (22, 163, 74)
BLUE = (37, 99, 235)
RED = (225, 29, 72)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 版式常量（内容矩形 x, y, w, h；边框画在矩形外面）
L_X, L_W = 48, 520
C_X, C_W = 592, 1152            # 主画面 3 倍整数放大 384×216 → 1152×648
R_X, R_W = 1768, 524
TOP, BOT = 40, 899              # 内容区上下沿；字幕带 y 922 起
MAIN = (C_X, TOP, C_W, 648)
STRIP = (C_X, 712, C_W, BOT - 712)       # 187 高
FACE_RAIL = (L_X, TOP, L_W, 390)         # 4:3
WIDE = (C_X, TOP, R_X + R_W - C_X, BOT - TOP)   # 1700×859：C+R 并成的宽板

_FC: dict = {}


def nsc(size: int, w: int = 800) -> ImageFont.FreeTypeFont:
    """Noto Sans SC：w ≥ 700 用 800 字重，否则 600。"""
    key = (size, 800 if w >= 700 else 600)
    if key not in _FC:
        _FC[key] = ImageFont.truetype(str(ROOT / "fonts" / ("NSC800.ttf" if key[1] == 800 else "NSC600.ttf")), size)
    return _FC[key]


def sg(size: int) -> ImageFont.FreeTypeFont:
    """Space Grotesk Bold：数字、英文。"""
    key = ("sg", size)
    if key not in _FC:
        f = ImageFont.truetype("D:/大疆/AI科普/素材/字体/SpaceGrotesk.ttf", size)
        try:
            f.set_variation_by_axes([700])
        except Exception:
            pass
        _FC[key] = f
    return _FC[key]


def mono(size: int) -> ImageFont.FreeTypeFont:
    key = ("mono", size)
    if key not in _FC:
        f = ImageFont.truetype("D:/大疆/AI科普/素材/字体/JetBrainsMono.ttf", size)
        try:
            f.set_variation_by_axes([600])
        except Exception:
            pass
        _FC[key] = f
    return _FC[key]


# ---------------------------------------------------------------- 基础
def rr_mask(w: int, h: int, r: int, ss: int = 4) -> Image.Image:
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def frame_layers(w: int, h: int, r: int = 22, bw: int = 6, sh: tuple = (10, 10), sc=ORANGE, ink=INK, ss: int = 3):
    """画板的框：→ (shadow, ring, m)：两张 RGBA，尺寸 (w+2m, h+2m)，内容矩形的左上角在 (m, m)。
    shadow = 硬阴影（偏移 sh，颜色 sc），ring = 粗边（厚 bw，圆角 r，中间是镂空的内容区）。"""
    m = bw + max(abs(sh[0]), abs(sh[1])) + 2
    ww, hh = w + 2 * m, h + 2 * m

    def rr(box, rad):
        im = Image.new("L", (ww * ss, hh * ss), 0)
        ImageDraw.Draw(im).rounded_rectangle([v * ss for v in box], radius=rad * ss, fill=255)
        return im.resize((ww, hh), Image.LANCZOS)

    outer = rr((m - bw, m - bw, m + w - 1 + bw, m + h - 1 + bw), r + bw)
    inner = rr((m, m, m + w - 1, m + h - 1), r)
    ring_a = ImageChops.subtract(outer, inner)
    shadow_a = rr((m - bw + sh[0], m - bw + sh[1], m + w - 1 + bw + sh[0], m + h - 1 + bw + sh[1]), r + bw)
    ring = Image.new("RGBA", (ww, hh), ink + (0,))
    ring.putalpha(ring_a)
    shadow = Image.new("RGBA", (ww, hh), sc + (0,))
    shadow.putalpha(shadow_a)
    return shadow, ring, m


_FRAME_CACHE: dict = {}


def put_panel(canvas: Image.Image, img: Image.Image, rect, r: int = 22, bw: int = 6, sh=(10, 10), sc=ORANGE, ink=INK, opacity: float = 1.0):
    """把 img（RGB，已经是 rect 的尺寸）按框版贴到 RGBA 画布上。"""
    x, y, w, h = rect
    key = (w, h, r, bw, sh, sc, ink)
    if key not in _FRAME_CACHE:
        _FRAME_CACHE[key] = frame_layers(w, h, r, bw, sh, sc, ink)
    shadow, ring, m = _FRAME_CACHE[key]
    layer = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    layer.alpha_composite(shadow)
    body = img.convert("RGBA")
    mask = rr_mask(w, h, r)
    layer.paste(body, (m, m), mask)
    layer.alpha_composite(ring)
    if opacity < 1:
        a = layer.getchannel("A").point(lambda v: int(v * opacity))
        layer.putalpha(a)
    canvas.alpha_composite(layer, (x - m, y - m))


def fit_cover(im: Image.Image, w: int, h: int, cx: float = 0.5, cy: float = 0.5, pixel: bool = False) -> Image.Image:
    """铺满 w×h（裁掉多出来的），cx / cy 是裁切中心占源图的比例。pixel=True 用最近邻（像素画）。"""
    sw, sh_ = im.size
    s = max(w / sw, h / sh_)
    nw, nh = max(w, round(sw * s)), max(h, round(sh_ * s))
    r = im.resize((nw, nh), Image.NEAREST if pixel else Image.LANCZOS)
    x0 = min(max(round(cx * nw - w / 2), 0), nw - w)
    y0 = min(max(round(cy * nh - h / 2), 0), nh - h)
    return r.crop((x0, y0, x0 + w, y0 + h))


def fit_contain(im: Image.Image, w: int, h: int, bg=(255, 255, 255), pixel: bool = False) -> Image.Image:
    sw, sh_ = im.size
    s = min(w / sw, h / sh_)
    r = im.resize((max(1, round(sw * s)), max(1, round(sh_ * s))), Image.NEAREST if pixel else Image.LANCZOS)
    out = Image.new("RGB", (w, h), bg)
    out.paste(r, ((w - r.width) // 2, (h - r.height) // 2))
    return out


def text_w(text: str, font) -> float:
    return font.getlength(text)


def wrap(text: str, font, max_w: int) -> list[str]:
    """按像素宽度折行：中文逐字，英文 / 数字尽量不拆词。"""
    lines, cur, word = [], "", ""
    def flush_word():
        nonlocal cur, word
        if not word:
            return
        if text_w(cur + word, font) <= max_w or not cur:
            cur += word
        else:
            lines.append(cur.rstrip())
            cur = word.lstrip()
        word = ""
    for ch in text:
        if ch == "\n":
            flush_word(); lines.append(cur.rstrip()); cur = ""; continue
        if ord(ch) < 0x2e80 and ch != " " or (ch == " " and word):
            word += ch
            continue
        if ch == " ":
            flush_word(); cur += " "; continue
        flush_word()
        if text_w(cur + ch, font) <= max_w or not cur:
            cur += ch
        else:
            lines.append(cur.rstrip()); cur = ch
    flush_word()
    if cur:
        lines.append(cur.rstrip())
    return lines


def outline_text(img: Image.Image, xy, text: str, font, fill, stroke=INK, sw: int = 8, shadow=None, anchor="la"):
    """封面式描边字：外面一圈 INK，可选错位阴影。"""
    d = ImageDraw.Draw(img)
    x, y = xy
    if shadow:
        d.text((x + shadow[0], y + shadow[1]), text, font=font, fill=stroke, stroke_width=sw, stroke_fill=stroke, anchor=anchor)
    d.text((x, y), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)


# ---------------------------------------------------------------- 贴纸 / 标签
def sticker(text: str, size: int = 30, fill=MARKER, ink=INK, bw: int = 3, padx: int = 16, pady: int = 8, rot: float = -2.5, ss: int = 3) -> Image.Image:
    """黄色贴纸：粗黑边、圆角、微微歪着。RGBA。"""
    f = nsc(size * ss)
    tw = int(f.getlength(text))
    asc, desc = f.getmetrics()
    w, h = tw + 2 * padx * ss, asc + desc + 2 * pady * ss
    im = Image.new("RGBA", (w + 8 * ss, h + 8 * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4 * ss, 4 * ss, 4 * ss + w, 4 * ss + h), radius=10 * ss, fill=fill, outline=ink, width=bw * ss)
    d.text((4 * ss + padx * ss, 4 * ss + pady * ss), text, font=f, fill=ink)
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im.resize((max(1, im.width // ss), max(1, im.height // ss)), Image.LANCZOS)


def badge(text: str, size: int = 26, fill=ORANGE, color=WHITE, padx: int = 14, pady: int = 6, r: int = 10, ss: int = 3) -> Image.Image:
    f = nsc(size * ss)
    tw = int(f.getlength(text))
    asc, desc = f.getmetrics()
    w, h = tw + 2 * padx * ss, asc + desc + 2 * pady * ss
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r * ss, fill=fill)
    d.text((padx * ss, pady * ss), text, font=f, fill=color)
    return im.resize((max(1, w // ss), max(1, h // ss)), Image.LANCZOS)


def paste_rgba(canvas: Image.Image, sprite: Image.Image, xy, opacity: float = 1.0):
    if opacity < 1:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel("A").point(lambda v: int(v * opacity)))
    canvas.alpha_composite(sprite, (int(xy[0]), int(xy[1])))


def label_on(canvas: Image.Image, rect, text: str, size: int = 30, rot: float = -2.5, dx: int = -14, dy: int = -26, corner: str = "tl"):
    """在画板 rect 的左上角（或右上角 tr）压一张贴纸。"""
    s = sticker(text, size, rot=rot)
    x, y, w, h = rect
    px = x + dx if corner == "tl" else x + w - s.width - dx
    paste_rgba(canvas, s, (px, y + dy))


# ---------------------------------------------------------------- 卡片
def card(w: int, h: int, fill=WHITE, r: int = 22, bw: int = 5, sh=(8, 8), sc=INK, ink=INK) -> tuple[Image.Image, int]:
    """白色卡片的底（含粗边和硬阴影），RGBA；返回 (图, 内容区在图里的偏移 m)。"""
    shadow, ring, m = frame_layers(w, h, r, bw, sh, sc, ink)
    layer = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    layer.alpha_composite(shadow)
    body = Image.new("RGBA", (w, h), fill + (255,))
    layer.paste(body, (m, m), rr_mask(w, h, r))
    layer.alpha_composite(ring)
    return layer, m


def toc_card(items: list[str], now: int | None, chapter_dots: int = 15, dot_now: int | None = None, w: int = L_W, title="本期目录", sub="看一遍这个游戏是怎么长出来的") -> tuple[Image.Image, int]:
    """本期目录（≤ 3 条、每条 ≤ 7 字）+ 15 个章节点。now = 第几条是当前的（0 起，None = 都没到）。"""
    pad = 30
    row_h = 66
    h = pad + 44 + 34 + 12 + row_h * len(items) + 12 + (50 if chapter_dots else 0) + pad - 8
    base, m = card(w, h)
    d = ImageDraw.Draw(base)
    x0, y0 = m + pad, m + pad - 4
    d.text((x0, y0), title, font=nsc(34), fill=INK)
    d.text((x0, y0 + 46), sub, font=nsc(20, 600), fill=GRAY2)
    y = y0 + 46 + 34 + 12
    for i, it in enumerate(items):
        cur = (now == i)
        done = now is not None and i < now
        col = INK if cur else (GRAY if done else (176, 182, 191))
        if cur:
            d.rounded_rectangle((x0, y + 12, x0 + 8, y + row_h - 14), radius=4, fill=ORANGE)
        d.text((x0 + 26, y + row_h / 2), str(i + 1), font=sg(26), fill=ORANGE if cur else col, anchor="lm")
        d.text((x0 + 26 + 40, y + row_h / 2), it, font=nsc(34 if cur else 32, 800 if cur else 600), fill=col, anchor="lm")
        y += row_h
    if chapter_dots:
        y += 14
        n = chapter_dots
        gap = (w - 2 * pad - 15) / (n - 1)
        for i in range(n):
            cx = x0 + 7 + i * gap
            if dot_now is not None and i == dot_now:
                d.ellipse((cx - 11, y + 5 - 11 + 7, cx + 11, y + 5 + 11 + 7), fill=INK)
            else:
                shown = dot_now is not None and i < dot_now
                d.ellipse((cx - 7, y + 5 + 7 - 7, cx + 7, y + 5 + 7 + 7), fill=ORANGE if shown else (226, 229, 235))
    return base, m


def draw_num(d: ImageDraw.ImageDraw, xy, text: str, size: int, fill) -> float:
    """大数字：数字 / 符号用 Space Grotesk，汉字（万、亿）用 Noto 800。返回画出来的宽度。"""
    x0, y0 = xy
    x = x0
    i = 0
    while i < len(text):
        j = i
        cjk = ord(text[i]) >= 0x2E80
        while j < len(text) and (ord(text[j]) >= 0x2E80) == cjk:
            j += 1
        seg = text[i:j]
        f = nsc(int(size * 0.92)) if cjk else sg(size)
        d.text((x, y0 + (size * 0.06 if cjk else 0)), seg, font=f, fill=fill)
        x += f.getlength(seg)
        i = j
    return x - x0


def stat_card(w: int, h: int, num: str, unit: str, caption: str, accent=ORANGE, num_size: int = 96) -> tuple[Image.Image, int]:
    """数字卡：大数字（Space Grotesk）+ 橙色单位 + 灰色说明。"""
    base, m = card(w, h)
    d = ImageDraw.Draw(base)
    pad = 26
    nw = draw_num(d, (m + pad, m + pad + 4), num, num_size, INK)
    d.text((m + pad + nw + 10, m + pad + 4 + num_size * 0.58), unit, font=nsc(int(num_size * 0.4)), fill=accent)
    d.text((m + pad, m + h - pad - 10), caption, font=nsc(28, 600), fill=GRAY, anchor="ls")
    return base, m


def keycap(letter: str, label: str, sub: str = "", h: int = 92) -> Image.Image:
    """键帽 + 说明：[J] 三连击。RGBA。"""
    ss = 3
    kw = h
    f = sg(52 * ss // 1)
    lab = nsc(40)
    sf = nsc(24, 600)
    lw = int(lab.getlength(label) / 1)
    sw_ = int(sf.getlength(sub)) if sub else 0
    tw = max(lw, sw_)
    w = kw + 18 + tw + 6
    im = Image.new("RGBA", (w * ss, (h + 10) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 键帽：下面一圈“键身”
    d.rounded_rectangle((0, 8 * ss, kw * ss - 1, (h + 8) * ss - 1), radius=18 * ss, fill=INK)
    d.rounded_rectangle((0, 0, kw * ss - 1, (h - 4) * ss), radius=18 * ss, fill=WHITE, outline=INK, width=5 * ss)
    d.text((kw * ss / 2, (h - 4) * ss / 2 + 2 * ss), letter, font=f, fill=INK, anchor="mm")
    im = im.resize((w, h + 10), Image.LANCZOS)
    d2 = ImageDraw.Draw(im)
    ty = (h - 4) / 2 - (14 if sub else 0)
    d2.text((kw + 18, ty + 2), label, font=lab, fill=INK, anchor="lm")
    if sub:
        d2.text((kw + 18, ty + 36), sub, font=sf, fill=GRAY, anchor="lm")
    return im


def chip(text: str, size: int = 28, fill=WHITE, color=INK, bw: int = 4, padx: int = 20, pady: int = 9, r: int = 16, ss: int = 3, sh=(5, 5), sc=INK) -> Image.Image:
    """小药丸：白底粗黑边硬阴影。"""
    f = nsc(size * ss)
    tw = int(f.getlength(text))
    asc, desc = f.getmetrics()
    w, h = tw + 2 * padx * ss, asc + desc + 2 * pady * ss
    mm = (bw + 7) * ss
    im = Image.new("RGBA", (w + 2 * mm, h + 2 * mm), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((mm + sh[0] * ss, mm + sh[1] * ss, mm + w + sh[0] * ss, mm + h + sh[1] * ss), radius=r * ss, fill=sc)
    d.rounded_rectangle((mm, mm, mm + w, mm + h), radius=r * ss, fill=fill, outline=INK, width=bw * ss)
    d.text((mm + padx * ss, mm + pady * ss), text, font=f, fill=color)
    return im.resize((im.width // ss, im.height // ss), Image.LANCZOS)


def arrow_right(size: int = 70, color=INK, ss: int = 3) -> Image.Image:
    s = size * ss
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t = s * 0.14
    d.rounded_rectangle((s * 0.06, s / 2 - t, s * 0.66, s / 2 + t), radius=t * 0.6, fill=color)
    d.polygon([(s * 0.58, s * 0.16), (s * 0.94, s / 2), (s * 0.58, s * 0.84)], fill=color)
    return im.resize((size, size), Image.LANCZOS)


def cross_mark(size: int = 64, ss: int = 3) -> Image.Image:
    s = size * ss
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=RED, outline=INK, width=int(s * 0.06))
    p = s * 0.3
    d.line((p, p, s - p, s - p), fill=WHITE, width=int(s * 0.12))
    d.line((p, s - p, s - p, p), fill=WHITE, width=int(s * 0.12))
    return im.resize((size, size), Image.LANCZOS)


def check_mark(size: int = 64, ss: int = 3) -> Image.Image:
    s = size * ss
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=GREEN, outline=INK, width=int(s * 0.06))
    d.line((s * 0.26, s * 0.52, s * 0.43, s * 0.68), fill=WHITE, width=int(s * 0.12))
    d.line((s * 0.43, s * 0.68, s * 0.76, s * 0.32), fill=WHITE, width=int(s * 0.12))
    return im.resize((size, size), Image.LANCZOS)


def glow_ring(rect, color=ORANGE, bw: int = 6, r: int = 22, pad: int = 10) -> tuple[Image.Image, int]:
    """强调环：套在画板外面一圈的橙色光环（RGBA，返回图和偏移）。"""
    x, y, w, h = rect
    m = pad + bw + 4
    ss = 3
    im = Image.new("RGBA", ((w + 2 * m) * ss, (h + 2 * m) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((m * ss, m * ss, (m + w) * ss, (m + h) * ss), radius=(r + pad) * ss, outline=color, width=bw * ss)
    return im.resize((w + 2 * m, h + 2 * m), Image.LANCZOS), m


def new_canvas(bg_path: Path | None = None) -> Image.Image:
    bg_path = bg_path or (HERE / "bg.png")
    png = Image.open(bg_path).convert("RGBA")          # 印花 PNG 是带透明的，网页里叠在白底上（#fff url(bg.png)）
    if png.size != (W, H):
        png = png.resize((W, H), Image.LANCZOS)
    bg = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    bg.alpha_composite(png)
    return bg
