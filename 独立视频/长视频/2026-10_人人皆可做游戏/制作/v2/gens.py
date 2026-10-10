# -*- coding: utf-8 -*-
"""gens.py —— 画板里的“活”素材（frame(t) → PIL RGB，t 是这块素材自己的秒数）：动作墙、视差街景、终端卡……
合成引擎里的 GenSrc 直接用它们；样板图也用 t=0 的那一帧。"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from ui import INK, GRAY, ORANGE, MARKER, WHITE, SOFT, nsc, mono

MAT = Path(r"D:\大疆\游戏素材\银魂")
GAME = MAT / "游戏"


def action_wall(w: int, h: int, cols: int = 9, rows: int = 4, char: str = "gintoki", scale: int = 2, bg=SOFT):
    """一个角色的全部动作同时播（34 个动作 9×4 摆开，每格按自己的帧数 / 帧率循环）。"""
    jd = json.loads((MAT / "角色图集" / char / f"{char}.json").read_text(encoding="utf-8"))
    atlas = Image.open(MAT / "角色图集" / char / f"{char}.png").convert("RGBA")
    cw, ch = jd["cell"]
    anims = list(jd["animations"].items())[: cols * rows]
    cache: dict = {}
    cell_w, cell_h = w / cols, h / rows

    def frame(t: float):
        im = Image.new("RGB", (w, h), bg)
        for i, (name, a) in enumerate(anims):
            fi = int(t * a.get("fps", 12)) % max(1, a["frames"])
            key = (i, fi)
            if key not in cache:
                cache[key] = atlas.crop((fi * cw, a["row"] * ch, (fi + 1) * cw, (a["row"] + 1) * ch)).resize((cw * scale, ch * scale), Image.NEAREST)
            c = cache[key]
            x = int((i % cols) * cell_w + cell_w / 2 - c.width / 2)
            y = int((i // cols) * cell_h + cell_h / 2 - c.height / 2)
            im.paste(c, (x, y), c)
        return im

    frame.names = [n for n, _ in anims]
    return frame


def parallax(w: int, h: int, speed: float = 22.0, scale: int = 3):
    """街景图层各走各的速度（远景慢、近景快），一眼看出“背景是拆成一层层的”。"""
    base = GAME / "assets" / "bg" / "street"
    sky = Image.open(base / "sky.png").convert("RGBA")
    spec = [("back.png", 56, 0.12), ("mid.png", 56, 0.32), ("facade.png", 56, 0.62), ("road.png", 152, 1.0)]
    layers = [(Image.open(base / f).convert("RGBA"), y, k) for f, y, k in spec]

    def frame(t: float):
        comp = sky.copy()
        for im, y, k in layers:
            off = int(t * speed * k) % im.width
            for x in (-off, -off + im.width):
                if x < 384 and x + im.width > 0:
                    comp.alpha_composite(im, (x, y)) if x >= 0 else comp.alpha_composite(im.crop((-x, 0, im.width, im.height)), (0, y))
        big = comp.convert("RGB").resize((384 * scale, 216 * scale), Image.NEAREST)
        x0, y0 = (big.width - w) // 2, (big.height - h) // 2 + 40
        return big.crop((x0, max(0, y0), x0 + w, max(0, y0) + h))

    return frame


def mixed_text(d: ImageDraw.ImageDraw, xy, text: str, size: int, fill, anchor="la"):
    """英文数字用等宽字体、中文用 Noto：逐段画。anchor 只支持 'la' / 'lm'。"""
    x, y = xy
    fm, fc = mono(size), nsc(size, 600)
    i = 0
    while i < len(text):
        j = i
        cjk = ord(text[i]) >= 0x2E80
        while j < len(text) and (ord(text[j]) >= 0x2E80) == cjk:
            j += 1
        seg, f = text[i:j], (fc if cjk else fm)
        d.text((x, y), seg, font=f, fill=fill, anchor=anchor)
        x += f.getlength(seg)
        i = j
    return x


def terminal_card(w: int, h: int, lines: list[str], title: str, size: int = 22, hi: tuple = (), scroll: float = 0.0):
    """深色“终端”卡：用于镜头表 / 文件清单。hi = 要标黄的行号（0 起），scroll = 往上滚了几行。"""
    im = Image.new("RGB", (w, h), (30, 32, 40))
    d = ImageDraw.Draw(im)
    lh = size + 9
    y = 62 - scroll * lh
    for k, ln in enumerate(lines):
        if y > 40 and y < h:
            col = (255, 216, 77) if k in hi else (230, 233, 240)
            if k in hi:
                d.rectangle((0, y - 3, w, y + lh - 5), fill=(60, 56, 30))
            mixed_text(d, (22, y), ln, size, col)
        y += lh
    d.rectangle((0, 0, w, 44), fill=(45, 48, 58))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((18 + i * 28, 14, 34 + i * 28, 30), fill=c)
    d.text((w / 2, 22), title, font=nsc(20, 600), fill=(200, 205, 215), anchor="mm")
    return im


# ---------------------------------------------------------------- 文件夹窗口（“双击就能玩”）
def explorer(w: int = 1152, h: int = 648, t_arrive: float = 1.6, t_click: float = 2.0, name: str = "index.html"):
    """一个文件夹窗口：鼠标从右下角移到 index.html 上，双击（两圈涟漪）。frame(t) → PIL RGB。"""
    import math
    rows = [("assets", "文件夹", ""), ("docs", "文件夹", ""), ("engine", "文件夹", ""), ("story", "文件夹", ""),
            ("data.js", "JavaScript 文件", "491 KB"), ("index.html", "HTML 文档", "10 KB"), ("main.js", "JavaScript 文件", "15 KB"), ("README.md", "Markdown 文档", "22 KB")]
    row_h, y0 = 62, 214
    sel = [i for i, r in enumerate(rows) if r[0] == name][0]
    tx, ty = 250, y0 + sel * row_h + row_h // 2
    sx, sy = w - 150, h - 90

    def icon(d, x, y, kind):
        if kind == "文件夹":
            d.rounded_rectangle((x, y + 6, x + 44, y + 38), radius=6, fill=(255, 200, 69), outline=(214, 160, 30), width=2)
            d.rounded_rectangle((x, y, x + 20, y + 12), radius=4, fill=(255, 200, 69), outline=(214, 160, 30), width=2)
        else:
            d.polygon([(x + 4, y), (x + 30, y), (x + 42, y + 12), (x + 42, y + 42), (x + 4, y + 42)], fill=(255, 255, 255), outline=(150, 156, 168))
            d.polygon([(x + 30, y), (x + 30, y + 12), (x + 42, y + 12)], fill=(222, 226, 233), outline=(150, 156, 168))
            col = {"HTML 文档": (255, 79, 26), "JavaScript 文件": (234, 179, 8), "Markdown 文档": (37, 99, 235)}.get(kind, (107, 114, 128))
            d.rectangle((x + 10, y + 22, x + 36, y + 32), fill=col)

    def frame(t: float):
        im = Image.new("RGB", (w, h), (246, 247, 250))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w, 66), fill=(255, 255, 255))
        d.line((0, 66, w, 66), fill=(222, 225, 231), width=2)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse((26 + i * 36, 22, 48 + i * 36, 44), fill=c)
        d.text((w / 2, 34), "银魂像素游戏", font=nsc(28), fill=INK, anchor="mm")
        d.rounded_rectangle((34, 88, w - 34, 150), radius=14, fill=WHITE, outline=(214, 218, 225), width=2)
        d.text((60, 119), "游戏素材  ›  银魂  ›  游戏", font=nsc(26, 600), fill=GRAY, anchor="lm")
        d.text((60, 186), "名称", font=nsc(22, 600), fill=(150, 156, 168), anchor="lm")
        d.text((560, 186), "类型", font=nsc(22, 600), fill=(150, 156, 168), anchor="lm")
        d.text((900, 186), "大小", font=nsc(22, 600), fill=(150, 156, 168), anchor="lm")
        d.line((34, 204, w - 34, 204), fill=(226, 229, 235), width=2)
        # 鼠标位置
        u = max(0.0, min(1.0, (t - (t_arrive - 1.3)) / 1.3))
        u = u * u * (3 - 2 * u)
        mx, my = sx + (tx - sx) * u, sy + (ty - sy) * u
        hover = u >= 1.0
        clicked = t >= t_click
        for i, (nm, kind, size) in enumerate(rows):
            y = y0 + i * row_h
            if i == sel and (hover or clicked):
                d.rounded_rectangle((34, y + 2, w - 34, y + row_h - 2), radius=10, fill=(255, 226, 214) if clicked else (255, 240, 233))
            icon(d, 66, y + 10, kind)
            d.text((136, y + row_h / 2), nm, font=nsc(30, 800 if i == sel else 600), fill=INK, anchor="lm")
            d.text((560, y + row_h / 2), kind, font=nsc(24, 600), fill=GRAY, anchor="lm")
            d.text((900, y + row_h / 2), size, font=nsc(24, 600), fill=GRAY, anchor="lm")
        # 双击涟漪
        for k, tc in enumerate((t_click, t_click + 0.24)):
            tt = t - tc
            if 0 <= tt < 0.5:
                r = 8 + tt * 110
                a = int(255 * (1 - tt / 0.5))
                ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                ImageDraw.Draw(ov).ellipse((mx - r, my - r, mx + r, my + r), outline=(255, 79, 26, a), width=6)
                im.paste(ov, (0, 0), ov)
                d = ImageDraw.Draw(im)
        # 鼠标指针
        pts = [(mx, my), (mx, my + 38), (mx + 10, my + 29), (mx + 18, my + 46), (mx + 26, my + 42), (mx + 18, my + 26), (mx + 31, my + 26)]
        d.polygon(pts, fill=INK, outline=WHITE)
        return im

    return frame


# ---------------------------------------------------------------- 代码窗口（带语法着色，用于“台词是写在代码里的”）
def code_view(w: int, h: int, lines: list[str], first_no: int = 1, hi: tuple = (), title: str = "chapter1.js", size: int = 24, scroll: float = 0.0):
    """深色编辑器：行号 + 简单着色（字符串橙黄、关键字紫、await/S.say 蓝）；hi = 要标亮的行下标（0 起）。"""
    import re
    f_m, f_c = mono(size), nsc(size, 600)
    lh = size + 12
    cols = {"str": (206, 145, 120), "kw": (197, 134, 192), "api": (86, 156, 214), "num": (181, 206, 168), "txt": (212, 212, 212), "com": (106, 153, 85)}
    BS = chr(92)
    q1 = "'(?:[^'" + BS + BS + "]|" + BS + ".)*'"
    q2 = '"(?:[^"' + BS + BS + ']|' + BS + '.)*"'
    q3 = '`(?:[^`' + BS + BS + ']|' + BS + '.)*`'
    pat = re.compile('(?P<com>//.*$)|(?P<str>' + q1 + '|' + q2 + '|' + q3 + ')|(?P<kw>' + BS + 'b(?:await|async|function|const|let|var|return|if|else|for|of|new|true|false|null)' + BS + 'b)|(?P<api>' + BS + 'bS' + BS + '.' + BS + 'w+|' + BS + 'bsay' + BS + 'b)|(?P<num>' + BS + 'b' + BS + 'd+' + BS + 'b)')

    def frame(t: float):
        im = Image.new("RGB", (w, h), (30, 30, 30))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w, 44), fill=(37, 37, 38))
        d.rectangle((0, 0, 260, 44), fill=(30, 30, 30))
        d.text((20, 22), title, font=nsc(20, 600), fill=(220, 220, 220), anchor="lm")
        y = 60 - scroll * lh
        for k, ln in enumerate(lines):
            if hi and k in hi:
                d.rectangle((0, y - 4, w, y + lh - 6), fill=(60, 56, 30))
            d.text((18, y), "%3d" % (first_no + k), font=f_m, fill=(110, 110, 110))
            x = 84
            pos = 0
            for m in pat.finditer(ln):
                if m.start() > pos:
                    x = _run(d, x, y, ln[pos:m.start()], f_m, f_c, cols["txt"])
                x = _run(d, x, y, m.group(0), f_m, f_c, cols[m.lastgroup])
                pos = m.end()
            if pos < len(ln):
                x = _run(d, x, y, ln[pos:], f_m, f_c, cols["txt"])
            y += lh
        return im

    return frame


def _run(d, x, y, text, f_m, f_c, col):
    i = 0
    while i < len(text):
        j = i
        cjk = ord(text[i]) >= 0x2E80
        while j < len(text) and (ord(text[j]) >= 0x2E80) == cjk:
            j += 1
        seg = text[i:j]
        f = f_c if cjk else f_m
        d.text((x, y), seg, font=f, fill=col)
        x += f.getlength(seg)
        i = j
    return x
