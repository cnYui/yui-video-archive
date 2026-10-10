"""《欢迎来到 人人皆可做游戏的 时代》无声版的画面生成库（PIL + numpy）。

每个 gen_* 返回 (总帧数, frame(i) -> PIL.Image 1920×1080)；build_silent.py 把它们逐帧喂给 ffmpeg。
画面风格跟着游戏走：深紫蓝底、金色强调、宋体点阵字（游戏界面同款）、华文行楷（大字）。
"""
from __future__ import annotations

import json
import math
import os
import random
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 60
GAME = Path(r"D:\大疆\游戏素材\银魂\游戏")
MAT = Path(r"D:\大疆\游戏素材\银魂")
FONTS = Path("C:/Windows/Fonts")
GOLD, RED, BLUE = (255, 216, 77), (214, 40, 47), (45, 79, 163)
INK, PAPER = (14, 12, 26), (244, 238, 224)


def font(kind: str, size: int):
    f = {"code": "simsun.ttc", "ui": "msyh.ttc", "uib": "msyhbd.ttc", "brush": "STXINGKA.TTF", "mono": "consola.ttf"}[kind]
    return ImageFont.truetype(str(FONTS / f), size)


# ---------------------------------------------------------------- 小工具
def lerp(a, b, u):
    return a + (b - a) * u


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


_bg = None


def bg_dark() -> Image.Image:
    """深紫蓝渐变 + 淡点阵（和游戏界面一个味道）。"""
    global _bg
    if _bg is None:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top, bot = np.array([26, 22, 52], np.float32), np.array([11, 9, 22], np.float32)
        a = (top * (1 - y) + bot * y) * np.ones((1, W, 1), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        dots = ((xx % 16 == 0) & (yy % 16 == 0))[..., None] * 9
        _bg = Image.fromarray(np.clip(a + dots, 0, 255).astype(np.uint8))
    return _bg.copy()


def tag(img: Image.Image, text: str, x: int = 64, y: int = 972, size: int = 30, color=GOLD):
    """左下角小标签：来源（文件名 / 章节名）。"""
    d = ImageDraw.Draw(img, "RGBA")
    f = font("code", size)
    w = int(f.getlength(text)) + 36
    d.rounded_rectangle((x, y, x + w, y + size + 22), 8, fill=(8, 6, 16, 205), outline=color + (255,), width=3)
    d.text((x + 18, y + 11), text, font=f, fill=color)
    return img


def brush_text(text: str, size: int, fill=(255, 255, 255), stroke=(18, 12, 24), sw=9, red: tuple | None = (150, 24, 30)):
    f = font("brush", size)
    pad = sw * 3 + 8
    im = Image.new("RGBA", (int(f.getlength(text)) + pad * 2, int(size * 1.4) + pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if red:
        d.text((pad, pad // 2), text, font=f, fill=red + (255,), stroke_width=sw + 5, stroke_fill=red + (255,))
    d.text((pad, pad // 2), text, font=f, fill=fill + (255,), stroke_width=sw, stroke_fill=stroke + (255,))
    return im.crop(im.getbbox())


def paste_center(base: Image.Image, im: Image.Image, cx: float, cy: float, alpha: float = 1.0):
    if alpha < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda p: int(p * alpha)))
    base.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def fit(im: Image.Image, w: int, h: int, mode="contain") -> Image.Image:
    s = min(w / im.width, h / im.height) if mode == "contain" else max(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS if s < 1 else Image.NEAREST)


def push_in(src: Image.Image, t: float, dur: float, z0=1.0, z1=1.12, cx=0.5, cy=0.5, pixel=False) -> Image.Image:
    """图片慢推：窗口从整幅缩到 z 倍（居中 / 指定中心），输出 1920×1080。"""
    z = lerp(z0, z1, smooth(t / dur))
    sw, sh = src.width, src.height
    vh = sh / z
    vw = vh * W / H
    if vw > sw:
        vw = sw / z
        vh = vw * H / W
    x0 = clamp(cx * sw - vw / 2, 0, sw - vw)
    y0 = clamp(cy * sh - vh / 2, 0, sh - vh)
    return src.resize((W, H), Image.NEAREST if pixel else Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))


# ---------------------------------------------------------------- 代码页
KEYWORDS = r"\b(await|async|function|const|let|var|return|if|else|for|of|new|true|false|null|import|from|def|class|in|and|or|not)\b"
TOK = [("comment", r"//.*$|#.*$"), ("string", r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`"),
       ("kw", KEYWORDS), ("api", r"\b(?:S|G)\.[A-Za-z_]+"), ("num", r"\b\d+(?:\.\d+)?\b")]
COL = {"comment": (106, 153, 85), "string": (206, 145, 120), "kw": (197, 134, 192), "api": (220, 220, 170), "num": (181, 206, 168),
       "plain": (212, 212, 212)}


def tokenize(line: str):
    pos, out = 0, []
    rx = re.compile("|".join("(?P<%s>%s)" % (n, p) for n, p in TOK))
    for m in rx.finditer(line):
        if m.start() > pos:
            out.append((line[pos:m.start()], "plain"))
        out.append((m.group(), m.lastgroup))
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], "plain"))
    return out


def render_code_tall(lines: list[str], size=32, first_no=1, highlight: tuple | None = None) -> Image.Image:
    """整段代码渲成一张高图（1920 宽）。highlight = (起始行, 结束行) 的行号会垫一条淡金底。"""
    f = font("code", size)
    lh = int(size * 1.5)
    img = Image.new("RGB", (W, lh * len(lines) + 40), (30, 30, 34))
    d = ImageDraw.Draw(img)
    gut = 130
    d.rectangle((0, 0, gut - 14, img.height), fill=(37, 37, 41))
    for i, line in enumerate(lines):
        y = 20 + i * lh
        no = first_no + i
        if highlight and highlight[0] <= no <= highlight[1]:
            d.rectangle((gut - 14, y - 4, W, y + lh - 6), fill=(58, 54, 36))
        d.text((gut - 34, y), str(no), font=f, fill=(110, 110, 118), anchor="ra")
        x = gut + 10
        for s, kind in tokenize(line.rstrip("\n").replace("\t", "  ")):
            d.text((x, y), s, font=f, fill=COL[kind])
            x += f.getlength(s)
    return img


def editor_frame(tall: Image.Image, y: float, filename: str, sub: str = "") -> Image.Image:
    """编辑器外壳：顶部标签栏 + 滚动窗口 + 右侧滚动条。"""
    out = Image.new("RGB", (W, H), (30, 30, 34))
    view_h = H - 70
    y = clamp(y, 0, max(0, tall.height - view_h))
    out.paste(tall.crop((0, int(y), W, int(y) + view_h)), (0, 70))
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, W, 70), fill=(24, 24, 27))
    for k, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((28 + k * 38, 24, 28 + k * 38 + 22, 46), fill=c)
    d.rectangle((190, 14, 190 + int(font("ui", 28).getlength(filename)) + 60, 70), fill=(30, 30, 34))
    d.text((220, 20), filename, font=font("ui", 28), fill=(235, 235, 235))
    if sub:
        d.text((W - 40, 22), sub, font=font("ui", 26), fill=(130, 130, 140), anchor="ra")
    if tall.height > view_h:
        r = view_h / tall.height
        d.rectangle((W - 14, 70 + int(y / tall.height * view_h), W - 4, 70 + int((y / tall.height + r) * view_h)), fill=(80, 80, 88))
    return out


def gen_code_scroll(path: Path, dur: float, a: int, b: int, filename: str, sub: str = "", size=32, highlight=None, ease=smooth):
    lines = path.read_text(encoding="utf-8").splitlines()[a - 1:b]
    tall = render_code_tall(lines, size, first_no=a, highlight=highlight)
    n = int(dur * FPS)
    maxy = max(0, tall.height - (H - 70))

    def frame(i):
        return editor_frame(tall, ease(i / max(1, n - 1)) * maxy, filename, sub)
    return n, frame


def gen_text_scroll(path: Path, dur: float, a: int, b: int, filename: str, sub: str = ""):
    """Markdown 文档滚动：标题金色，表格线灰，其余浅色（不做完整渲染，够“逐个镜头研究原片”的观感）。"""
    lines = path.read_text(encoding="utf-8").splitlines()[a - 1:b]
    size = 30
    f, fb = font("code", size), font("code", size)
    lh = int(size * 1.55)
    img = Image.new("RGB", (W, lh * len(lines) + 60), (252, 250, 244))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        y = 28 + i * lh
        col = (40, 40, 48)
        if line.startswith("#"):
            col = (150, 90, 0)
        elif line.startswith("|"):
            col = (70, 70, 90)
        elif line.startswith(">"):
            col = (110, 110, 120)
        elif line.startswith("-"):
            col = (30, 60, 110)
        d.text((90, y), line[:78], font=f, fill=col)
    n = int(dur * FPS)
    maxy = max(0, img.height - (H - 70))

    def frame(i):
        out = Image.new("RGB", (W, H), (252, 250, 244))
        y = smooth(i / max(1, n - 1)) * maxy
        out.paste(img.crop((0, int(y), W, int(y) + H - 70)), (0, 70))
        dd = ImageDraw.Draw(out)
        dd.rectangle((0, 0, W, 70), fill=(236, 232, 220))
        dd.text((40, 18), filename, font=font("ui", 28), fill=(60, 60, 70))
        if sub:
            dd.text((W - 40, 20), sub, font=font("ui", 26), fill=(130, 130, 140), anchor="ra")
        return out
    return n, frame


# ---------------------------------------------------------------- 信息页
def gen_storyboard_table(dur: float):
    """分镜总表：15 个场景、台词条数那一列高亮。"""
    rows = []
    for line in (MAT / "剧情分镜" / "分镜总表.md").read_text(encoding="utf-8").splitlines():
        if re.match(r"\|\s*\[s\d+\]", line):
            c = [x.strip() for x in line.strip("|").split("|")]
            sid = re.match(r"\[(s\d+)\]", c[0]).group(1)
            rows.append((sid, c[1], c[3], c[6], c[7]))
    total = sum(int(r[3]) for r in rows)
    n = int(dur * FPS)
    cols = [("场景", 140), ("标题", 520), ("时长", 200), ("台词条数", 260), ("音效数", 220)]
    x0 = (W - sum(w for _, w in cols)) // 2
    rh = 52
    fh, fr = font("uib", 34), font("ui", 32)

    def frame(i):
        t = i / FPS
        img = bg_dark()
        d = ImageDraw.Draw(img, "RGBA")
        d.text((W // 2, 62), "分镜总表 · 15 个场景 = 15 章", font=font("uib", 46), fill=GOLD, anchor="mm")
        y = 120
        x = x0
        d.rectangle((x0 - 20, y, x0 + sum(w for _, w in cols) + 20, y + 62), fill=(52, 46, 96, 235))
        for name, w in cols:
            d.text((x + w / 2, y + 31), name, font=fh, fill=(255, 255, 255), anchor="mm")
            x += w
        pulse = 0.5 + 0.5 * math.sin(t * 3.2)
        for k, r in enumerate(rows):
            appear = ease_out((t - 0.5 - k * 0.09) / 0.25)
            if appear <= 0:
                continue
            yy = y + 74 + k * rh + (1 - appear) * 18
            a = int(255 * appear)
            d.rectangle((x0 - 20, yy, x0 + sum(w for _, w in cols) + 20, yy + rh - 6), fill=(34, 30, 70, int(a * (0.85 if k % 2 else 0.6))))
            x = x0
            for ci, ((name, w), val) in enumerate(zip(cols, r)):
                col = (225, 225, 235, a)
                if name == "台词条数":
                    d.rectangle((x + 6, yy + 2, x + w - 6, yy + rh - 8), fill=(255, 216, 77, int(a * (0.18 + 0.16 * pulse))))
                    col = (255, 216, 77, a)
                d.text((x + w / 2, yy + rh / 2 - 3), val, font=fr, fill=col, anchor="mm")
                x += w
        if t > 0.5 + len(rows) * 0.09 + 0.4:
            u = ease_out((t - 0.5 - len(rows) * 0.09 - 0.4) / 0.4)
            d.text((W // 2, 1030), "原片 5 分半，一共 %d 句台词" % total, font=font("uib", 40), fill=(255, 255, 255, int(255 * u)), anchor="mm")
        return img
    return n, frame


def gen_image_push(path: Path, dur: float, z0=1.0, z1=1.25, cx=0.5, cy=0.5, caption: str = "", pixel=False, bg=(14, 12, 26)):
    src = Image.open(path).convert("RGB")
    n = int(dur * FPS)

    def frame(i):
        img = push_in(src, i / FPS, dur, z0, z1, cx, cy, pixel)
        if caption:
            tag(img, caption)
        return img
    return n, frame


def gen_atlas_reel(dur: float):
    """银时的全部动作：按动作表一个个播（动作名 + 帧数）。"""
    jd = json.loads((MAT / "角色图集" / "gintoki" / "gintoki.json").read_text(encoding="utf-8"))
    atlas = Image.open(MAT / "角色图集" / "gintoki" / "gintoki.png").convert("RGBA")
    cw, ch = jd["cell"]
    anims = [(k, v) for k, v in jd["animations"].items() if v.get("frames", 1) >= 4][:16]
    n = int(dur * FPS)
    per = dur / len(anims)

    def frame(i):
        t = i / FPS
        img = bg_dark()
        k = min(len(anims) - 1, int(t / per))
        name, a = anims[k]
        lt = t - k * per
        fi = int(lt * a.get("fps", 12)) % a["frames"]
        cell = atlas.crop((fi * cw, a["row"] * ch, (fi + 1) * cw, (a["row"] + 1) * ch))
        big = cell.resize((cw * 15, ch * 15), Image.NEAREST)
        paste_center(img, big, W // 2, H // 2 - 20)
        d = ImageDraw.Draw(img)
        d.text((W // 2, 920), name, font=font("mono", 52), fill=GOLD, anchor="mm")
        d.text((W // 2, 985), "银时 · 第 %d / %d 个动作　%d 帧" % (k + 1, len(jd["animations"]), a["frames"]), font=font("ui", 30), fill=(190, 190, 205), anchor="mm")
        # 左右两列：已经播过的动作名一个个亮起来
        for j, (nm, _) in enumerate(anims):
            col = GOLD if j == k else ((150, 150, 170) if j < k else (70, 66, 100))
            d.text((90 + (j // 8) * 0 + (W - 400 if j >= 8 else 0), 150 + (j % 8) * 62), nm, font=font("mono", 34), fill=col)
        return img
    return n, frame


def gen_layers_stack(dur: float):
    """街景拆图层：一层层叠上去，最后合成一张。图层来自 assets/bg/street。"""
    base = GAME / "assets" / "bg" / "street"
    spec = [("sky.png", 0, 0, "sky 天空"), ("back.png", 0, 70, "back 远景"), ("mid.png", 0, 96, "mid 中景"), ("facade.png", 0, 120, "facade 店面"),
            ("road.png", 0, 190, "road 路面")]
    layers = []
    for f, x, y, name in spec:
        im = Image.open(base / f).convert("RGBA")
        layers.append((im.crop((0, 0, 384, im.height)) if im.width > 384 else im, x, y, name))
    comp = Image.new("RGBA", (384, 216), (0, 0, 0, 255))
    for im, x, y, _ in layers:
        comp.alpha_composite(im, (x, min(y, 216 - im.height)))
    n = int(dur * FPS)
    sc = 5

    def frame(i):
        t = i / FPS
        img = bg_dark()
        d = ImageDraw.Draw(img)
        k_all = len(layers)
        t_stack = dur * 0.72
        if t < t_stack:
            for k, (im, x, y, name) in enumerate(layers):
                t0 = k * (t_stack / k_all)
                u = ease_out((t - t0) / 0.45)
                if u <= 0:
                    continue
                big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
                ox = (W - 384 * 3) // 2
                oy = 90 + k * 170 + (1 - u) * 120
                lay = big.copy()
                lay.putalpha(lay.getchannel("A").point(lambda p: int(p * u)))
                img.paste(lay, (ox, int(oy)), lay)
                d.text((ox - 30, oy + big.height // 2), name, font=font("ui", 34), fill=GOLD, anchor="rm")
            d.text((W // 2, 1040), "1600 多张图层，远景近景分开动", font=font("uib", 38), fill=(230, 230, 240), anchor="mm")
        else:
            u = smooth((t - t_stack) / 0.9)
            big = comp.resize((384 * sc, 216 * sc), Image.NEAREST).convert("RGB")
            z = lerp(0.62, 1.0, u)
            img.paste(big.resize((int(384 * sc * z), int(216 * sc * z)), Image.NEAREST), (int(W / 2 - 384 * sc * z / 2), int(H / 2 - 216 * sc * z / 2)))
        return img
    return n, frame


def gen_list_scroll(dur: float):
    """音频文件清单快速滚过（终端风格）。"""
    names = []
    for sub in ("音乐_a", "音乐_b", "音效"):
        p = MAT / "音频" / sub
        if p.exists():
            names += ["%s/%s" % (sub, f) for f in sorted(os.listdir(p))]
    if len(names) < 30:
        names = names * 3
    size = 34
    lh = int(size * 1.5)
    tall = Image.new("RGB", (W, lh * len(names) + 40), (14, 18, 14))
    d = ImageDraw.Draw(tall)
    f = font("code", size)
    for i, nm in enumerate(names):
        d.text((120, 20 + i * lh), "$ ls  " + nm, font=f, fill=(120, 220, 140))
    n = int(dur * FPS)
    maxy = tall.height - (H - 70)

    def frame(i):
        out = Image.new("RGB", (W, H), (14, 18, 14))
        y = smooth(i / max(1, n - 1)) * maxy if maxy > 0 else 0
        out.paste(tall.crop((0, int(y), W, int(y) + H - 70)), (0, 70))
        dd = ImageDraw.Draw(out)
        dd.rectangle((0, 0, W, 70), fill=(24, 30, 24))
        dd.text((40, 18), "游戏素材/银魂/音频  ·  %d 个文件（12 首 8 位配乐 + 80 多个音效，全是代码合成）" % len(names), font=font("ui", 28), fill=(170, 220, 180))
        return out
    return n, frame


def gen_tree(dur: float):
    """游戏文件夹结构。"""
    root = GAME
    lines = []

    def add(name, depth, note=""):
        lines.append((depth, name, note))
    add("游戏/", 0)
    add("index.html", 1, "双击就能玩")
    add("main.js", 1, "标题、章节表")
    add("engine/", 1, "引擎：画布、世界、剧情脚本、界面")
    for f in sorted(os.listdir(root / "engine")):
        add(f, 2)
    add("story/", 1, "每章一个文件")
    for f in sorted(os.listdir(root / "story")):
        if f.endswith(".js"):
            add(f, 2)
    add("assets/", 1, "角色、背景、音乐、音效")
    add("tools/", 1, "构建 + 自动通关测试")
    n = int(dur * FPS)
    lh = 44

    def frame(i):
        t = i / FPS
        img = bg_dark()
        d = ImageDraw.Draw(img)
        d.text((W // 2, 60), "一个游戏引擎都没用：浏览器画布 + 原生 JavaScript", font=font("uib", 42), fill=GOLD, anchor="mm")
        k = int(t / dur * (len(lines) + 4))
        cols = 2
        per = math.ceil(len(lines) / cols)
        for j, (dep, name, note) in enumerate(lines):
            if j > k:
                break
            cx = 160 + (j // per) * 900
            cy = 140 + (j % per) * lh
            col = (255, 255, 255) if dep < 2 else (170, 200, 255)
            nm = ("├ " if dep == 2 else "") + name
            d.text((cx + dep * 46, cy), nm, font=font("code", 34), fill=col)
            if note:
                d.text((cx + dep * 46 + font("code", 34).getlength(nm) + 28, cy - 2), note, font=font("ui", 30), fill=GOLD)
        return img
    return n, frame


def gen_results_card(dur: float, lines_n=612, shots_n=242, minutes=34):
    n = int(dur * FPS)
    rows = [("自动通关", "开一个看不见的浏览器，自己从头玩", GOLD), ("对话", "%d 句" % lines_n, (255, 255, 255)), ("截图", "%d 张" % shots_n, (255, 255, 255)),
            ("用时", "%d 分钟" % minutes, (255, 255, 255)), ("控制台报错", "0 个", (120, 230, 140))]

    def frame(i):
        t = i / FPS
        img = bg_dark()
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((260, 150, W - 260, H - 150), 22, fill=(8, 6, 16, 235), outline=(255, 216, 77, 255), width=4)
        d.text((W // 2, 230), "$ python tools/playtest.py all", font=font("mono", 44), fill=(120, 220, 140), anchor="mm")
        for k, (a, b, c) in enumerate(rows):
            u = ease_out((t - 0.5 - k * 0.45) / 0.3)
            if u <= 0:
                continue
            y = 350 + k * 120
            d.text((380, y), a, font=font("uib", 44), fill=(200, 200, 215, int(255 * u)), anchor="lm")
            d.text((W - 380, y), b, font=font("uib", 52 if k else 40), fill=c + (int(255 * u),), anchor="rm")
        return img
    return n, frame


def gen_screenshot_flash(files: list[Path], dur: float, label: str = ""):
    """截图快闪：dur 秒平均分给每一张（太多就均匀抽稀）。"""
    n = int(dur * FPS)
    per = max(1, n // len(files)) if len(files) <= n else 1
    use = files if len(files) <= n else [files[int(k * len(files) / n)] for k in range(n)]
    cache = {}

    def frame(i):
        f = use[min(len(use) - 1, i // per)]
        if f not in cache:
            if len(cache) > 6:
                cache.clear()
            im = Image.open(f).convert("RGB")
            s = max(W / im.width, H / im.height)
            im = im.resize((round(im.width * s), round(im.height * s)), Image.BICUBIC)
            cache[f] = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        img = cache[f].copy()
        if label:
            tag(img, label)
        return img
    return n, frame


def gen_wall(files: list[Path], dur: float, cols: int, rows: int, label: str = ""):
    """封面墙：cols×rows 的格子，一格一格弹出来。"""
    n = int(dur * FPS)
    gw, gh = (W - 160) // cols, (H - 200) // rows
    thumbs = []
    for f in files[:cols * rows]:
        im = Image.open(f).convert("RGB")
        s = min((gw - 16) / im.width, (gh - 16) / im.height)
        thumbs.append(im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS))

    def frame(i):
        t = i / FPS
        img = bg_dark()
        d = ImageDraw.Draw(img)
        if label:
            d.text((W // 2, 70), label, font=font("uib", 46), fill=GOLD, anchor="mm")
        for k, th in enumerate(thumbs):
            u = ease_out((t - 0.3 - k * 0.12) / 0.25)
            if u <= 0:
                continue
            cx = 80 + (k % cols) * gw + gw / 2
            cy = 150 + (k // cols) * gh + gh / 2
            sc = lerp(0.7, 1.0, u)
            t2 = th.resize((max(1, int(th.width * sc)), max(1, int(th.height * sc))), Image.LANCZOS)
            img.paste(t2, (int(cx - t2.width / 2), int(cy - t2.height / 2)))
        return img
    return n, frame


def gen_placeholder(label: str, sub: str, dur: float):
    """出镜占位卡：等露脸视频到了换掉。"""
    n = int(dur * FPS)
    bgi = Image.new("RGB", (W, H), (22, 20, 30))
    d0 = ImageDraw.Draw(bgi)
    for k in range(-H, W, 60):                                  # 斜纹，一眼看出是占位
        d0.line([(k, 0), (k + H, H)], fill=(30, 28, 42), width=18)

    def frame(i):
        img = bgi.copy()
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((420, 300, W - 420, H - 300), 26, fill=(14, 12, 24), outline=(110, 104, 150), width=4)
        d.text((W // 2, 450), "出镜（占位）", font=font("uib", 96), fill=(235, 230, 250), anchor="mm")
        d.text((W // 2, 590), label, font=font("uib", 44), fill=GOLD, anchor="mm")
        d.text((W // 2, 660), sub, font=font("ui", 34), fill=(170, 168, 195), anchor="mm")
        d.text((W // 2, 725), "%.0f 秒" % dur, font=font("ui", 40), fill=(130, 128, 160), anchor="mm")
        return img
    return n, frame


def gen_title_card(dur: float, bg_src: Image.Image):
    """片名卡：游戏画面压暗，行楷大字砸下来。"""
    n = int(dur * FPS)
    base = push_in(bg_src, 0, 1, 1.0, 1.0, pixel=True).point(lambda p: int(p * 0.42))
    t1 = brush_text("欢迎来到", 150)
    t2 = brush_text("人人皆可做游戏的时代", 170)

    def frame(i):
        t = i / FPS
        img = base.copy()
        for k, im in enumerate((t1, t2)):
            u = clamp((t - k * 0.25) / 0.12)
            s = 1 + 0.6 * (1 - ease_out(u))
            im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR) if s > 1.001 else im
            paste_center(img, im2, W / 2, 400 + k * 230, alpha=u)
        if t > dur - 0.25:                                      # 末尾淡出
            img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (dur - 0.25)) / 0.25))
        return img
    return n, frame


def gen_end_card(dur: float):
    """游戏 Logo 片尾：标题天际线 + Logo 砸下来 + 字幕条。"""
    sky = Image.open(GAME / "assets" / "bg" / "title_skyline.png").convert("RGB")
    logo = Image.open(GAME / "assets" / "ui" / "logo.png").convert("RGBA")
    rib = Image.open(GAME / "assets" / "ui" / "ribbon.png").convert("RGBA")
    n = int(dur * FPS)
    L = logo.resize((logo.width * 7, logo.height * 7), Image.NEAREST)
    R = rib.resize((rib.width * 7, rib.height * 7), Image.NEAREST)
    sub = brush_text("人人皆可做游戏的时代", 78, red=None, sw=6)

    def frame(i):
        t = i / FPS
        img = push_in(sky, t, dur, 1.0, 1.05, pixel=True).point(lambda p: int(p * 0.7))
        s = 1 + 1.2 * (1 - ease_out(t / 0.12)) if t < 0.12 else 1.0
        L2 = L.resize((int(L.width * s), int(L.height * s)), Image.NEAREST) if s > 1.001 else L
        paste_center(img, L2, W / 2, 400)
        if t > 0.2:
            paste_center(img, R, lerp(W + 400, W / 2, ease_out((t - 0.2) / 0.3)), 400 + L.height / 2 + 10)
        if t > 0.9:
            paste_center(img, sub, W / 2, 900, alpha=clamp((t - 0.9) / 0.4))
        if t > dur - 0.4:
            img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (dur - 0.4)) / 0.4))
        return img
    return n, frame


def gen_vertical_clip(path: Path, start: float, dur: float, caption: str = ""):
    """竖屏短视频放在横屏中间：左右用同一画面的模糊放大做底。"""
    import subprocess
    n = int(dur * FPS)
    vh = 960
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", "%.3f" % start, "-t", "%.3f" % (dur + 0.2), "-i", str(path), "-vf", "fps=%d,scale=-2:%d" % (FPS, vh),
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "2", "-"], stdout=subprocess.PIPE)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
                           capture_output=True, text=True).stdout.strip().split(",")
    vw = int(round(int(probe[0]) * vh / int(probe[1]) / 2) * 2)
    last = [None]

    def frame(i):
        raw = proc.stdout.read(vw * vh * 3)
        if len(raw) == vw * vh * 3:
            last[0] = Image.frombytes("RGB", (vw, vh), raw)
        fr = last[0] or Image.new("RGB", (vw, vh))
        bgi = fr.resize((W, int(W * vh / vw)), Image.BILINEAR).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(22)).point(lambda q: int(q * 0.35))
        bgi.paste(fr, ((W - vw) // 2, (H - vh) // 2))
        d = ImageDraw.Draw(bgi)
        d.rectangle(((W - vw) // 2 - 4, (H - vh) // 2 - 4, (W + vw) // 2 + 3, (H + vh) // 2 + 3), outline=(255, 216, 77), width=4)
        if caption:
            tag(bgi, caption)
        return bgi
    return n, frame
