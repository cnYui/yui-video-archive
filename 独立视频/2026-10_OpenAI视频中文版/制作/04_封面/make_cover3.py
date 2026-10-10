# -*- coding: utf-8 -*-
"""封面三选一（每种出 16:9 1920×1080 和 4:3 1440×1080），标题是用户定的：OpenAI DevDay演示翻车后 重演 dots 演示：订机票、选酒店、整理用户反馈（中文同传）。

  python make_cover3.py            # 三选一（A / B / C）
  python make_cover3.py --openai   # “A 蓝”：A 的版式改成 OpenAI 蓝黑白。作废：保留了“演示翻车了？”，用户后来要求去掉；
                                   # 现行版见 make_cover_final.py（A3）、make_cover_a4.py（A4）

A 人像大字：原片 4.6 s 那帧（刚说完“昨天的演示没按计划进行”，表情很对）+ 大字“演示翻车了？”
B 三件事拼图：标题 + 三张原片画面（打电话 / 酒店卡片 / 反馈对话），每张一个标签
C 黄色对话气泡：原创的聊天界面小插画（不画任何角色），气泡里是我概括的话，不是原片台词；头像用原片里的脸

B 站信息流会在封面下沿盖播放量和时长：重要的字都放在下面 12% 以上。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
CAND = HERE / "cand"
FONT = Path(r"D:/大疆/AI科普/素材/字体/NotoSansSC.ttf")
YELLOW = (255, 214, 64)
WHITE, BLACK = (255, 255, 255), (16, 16, 20)
RED = (255, 84, 62)


def font(size, weight=800):
    f = ImageFont.truetype(str(FONT), int(size))
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def tw(d, s, f):
    return d.textlength(s, font=f)


def load(name):
    return Image.open(CAND / name).convert("RGB")


def fit(im, w, h, cx=0.5, cy=0.5, box=None):
    """先按 box（原图坐标 x0,y0,x1,y1）裁，再按“铺满”缩放到 w×h；cx / cy 是多出来那部分里的取景位置。"""
    if box:
        im = im.crop(box)
    sw, sh = im.size
    k = max(w / sw, h / sh)
    nw, nh = int(sw * k + 0.5), int(sh * k + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = int((nw - w) * cx), int((nh - h) * cy)
    return im.crop((x0, y0, x0 + w, y0 + h))


def rounded(im, radius):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), radius=radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def shadow(canvas, box, radius, blur=22, alpha=150, dy=10):
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), radius=radius, fill=(0, 0, 0, alpha))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def gradient(w, h, top, bottom):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))


def chip(img, x, y, text, f, h, padx, fill, color, anchor_x=None):
    """圆角标签：文字垂直居中；返回右边界。"""
    d = ImageDraw.Draw(img)
    w = tw(d, text, f) + 2 * padx
    if anchor_x == "right":
        x = x - w
    d.rounded_rectangle((int(x), int(y), int(x + w), int(y + h)), radius=int(h / 2), fill=fill)
    d.text((x + padx, y + h / 2), text, font=f, fill=color, anchor="lm")
    return x + w


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for ch in text:
        if tw(d, cur + ch, f) <= max_w or not cur:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- A 人像大字
def make_a(W, H):
    s = W / 1920
    wide = W / H > 1.5
    img = fit(load("g_4.6.png"), W, H, cx=0.0 if not wide else 0.5, cy=0.3).convert("RGBA")
    g = Image.new("L", (1, H), 0)
    top = int(H * 0.44)
    for y in range(top, H):
        g.putpixel((0, y), int(215 * ((y - top) / (H - top)) ** 0.9))
    img = Image.composite(Image.new("RGBA", (W, H), (6, 8, 12, 255)), img, g.resize((W, H)))
    d = ImageDraw.Draw(img)
    f1, f1b, f2, f3 = font(158 * s, 900), font(196 * s, 900), font(104 * s, 900), font(40 * s, 700)
    parts = [("演示", f1, WHITE), ("翻车", f1b, RED), ("了？", f1, WHITE)]
    total = sum(tw(d, p[0], p[1]) for p in parts)
    x, y = (W - total) / 2, H * (0.485 if wide else 0.575)
    for txt, f, col in parts:
        d.text((x, y + (0 if f is f1b else 20 * s)), txt, font=f, fill=col, stroke_width=int(11 * s), stroke_fill=(10, 10, 14))
        x += tw(d, txt, f)
    d.text((W / 2, y + 215 * s), "OpenAI 重演 dots", font=f2, fill=YELLOW, stroke_width=int(9 * s), stroke_fill=(10, 10, 14), anchor="ma")
    tag = "DevDay 2026｜订机票 · 选酒店 · 整理用户反馈｜中文同传"
    w3 = tw(d, tag, f3)
    pad, y3 = 28 * s, H * (0.885 if wide else 0.875)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((int((W - w3) / 2 - pad), int(y3 - 14 * s), int((W + w3) / 2 + pad), int(y3 + 62 * s)), radius=int(38 * s), fill=(0, 0, 0, 175))
    img.alpha_composite(ov)
    ImageDraw.Draw(img).text((W / 2, y3 + 4 * s), tag, font=f3, fill=WHITE, anchor="ma")
    return img.convert("RGB")


# ---------------------------------------------------------------- A 的 OpenAI 配色版（用户选了 A，要蓝 黑 白）
BLUE = (58, 131, 247)         # #3A83F7：openai.com 页面的品牌蓝（CSS --color-brand-blue-400；这是同一对话另一个分支从官网读到的，我没重新核对）。DevDay 片头蓝环我实测约 #4FA8F4，偏浅，不用
OBLACK = (8, 8, 8)            # #080808，同上


def make_a_openai(W, H):
    s = W / 1920
    wide = W / H > 1.5
    img = fit(load("g_4.6.png"), W, H, cx=0.0 if not wide else 0.5, cy=0.3).convert("RGBA")
    g = Image.new("L", (1, H), 0)
    top = int(H * 0.44)
    for y in range(top, H):
        g.putpixel((0, y), int(228 * ((y - top) / (H - top)) ** 0.85))
    img = Image.composite(Image.new("RGBA", (W, H), OBLACK + (255,)), img, g.resize((W, H)))
    d = ImageDraw.Draw(img)
    f1, f1b, f2, f3 = font(158 * s, 900), font(196 * s, 900), font(104 * s, 900), font(40 * s, 700)
    parts = [("演示", f1, WHITE), ("翻车", f1b, BLUE), ("了？", f1, WHITE)]
    total = sum(tw(d, p[0], p[1]) for p in parts)
    x, y = (W - total) / 2, H * (0.485 if wide else 0.575)
    for txt, f, col in parts:
        d.text((x, y + (0 if f is f1b else 20 * s)), txt, font=f, fill=col, stroke_width=int(11 * s), stroke_fill=OBLACK)
        x += tw(d, txt, f)
    seg = [("OpenAI 重演 ", WHITE), ("dots", BLUE)]
    total2 = sum(tw(d, t, f2) for t, _ in seg)
    x2, y2 = (W - total2) / 2, y + 215 * s
    for t, col in seg:
        d.text((x2, y2), t, font=f2, fill=col, stroke_width=int(9 * s), stroke_fill=OBLACK)
        x2 += tw(d, t, f2)
    tag = "OpenAI DevDay 2026｜中文同传"
    w3 = tw(d, tag, f3)
    r, gap, pad = 11 * s, 18 * s, 30 * s
    inner = 2 * r + gap + w3
    y3 = H * (0.885 if wide else 0.875)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((int((W - inner) / 2 - pad), int(y3 - 14 * s), int((W + inner) / 2 + pad), int(y3 + 62 * s)), radius=int(38 * s), fill=OBLACK + (200,))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    cx0 = (W - inner) / 2
    d.ellipse((cx0, y3 + 24 * s - r, cx0 + 2 * r, y3 + 24 * s + r), fill=BLUE)
    d.text((cx0 + 2 * r + gap, y3 + 4 * s), tag, font=f3, fill=WHITE)
    return img.convert("RGB")


def main_openai():
    for tag, (w, h) in (("16x9", (1920, 1080)), ("4x3", (1440, 1080))):
        out = HERE / f"封面_A蓝_{tag}.png"
        make_a_openai(w, h).save(out)
        print(out.name)


# ---------------------------------------------------------------- B 三件事拼图
PANELS = {   # 标签, 文件, 16:9 小图的裁切框, 4:3 小图的裁切框（原图坐标）
    "phone": ("① 打电话订机票", "g_453.png", (480, 120, 1440, 660), (560, 120, 1400, 960)),
    "hotel": ("② 选酒店", "g_209.png", (620, 330, 1580, 870), (700, 300, 1400, 967)),
    "feedback": ("③ 整理用户反馈", "g_544.png", (130, 450, 1250, 1080), (330, 260, 1170, 1060)),
}


def make_b(W, H):
    wide = W / H > 1.5
    img = gradient(W, H, (12, 16, 26), (30, 36, 56)).convert("RGBA")
    d = ImageDraw.Draw(img)
    fl, ft = font(46, 800), font(40, 700)
    if wide:
        d.text((90, 62), "演示翻车后", font=font(124, 900), fill=WHITE)
        d.text((90, 205), "OpenAI 重演 dots", font=font(112, 900), fill=YELLOW)
        pw, ph = 700, 400
        pb = rounded(fit(load("g_7.0.png"), pw, ph, cx=0.3, cy=0.3), 30)
        box = (1130, 50, 1130 + pw, 50 + ph)
        shadow(img, box, 30)
        img.alpha_composite(pb, (box[0], box[1]))
        pw, ph, gap, x0, y0, idx = 560, 315, 40, 80, 540, 2
    else:
        d.text((W / 2, 64), "演示翻车后", font=font(150, 900), fill=WHITE, anchor="ma")
        d.text((W / 2, 246), "OpenAI 重演 dots", font=font(120, 900), fill=YELLOW, anchor="ma")
        pw, ph, gap, x0, y0, idx = 420, 400, 30, 60, 450, 3
    for i, key in enumerate(("phone", "hotel", "feedback")):
        label, fn, *crops = PANELS[key]
        x = x0 + i * (pw + gap)
        pic = rounded(fit(load(fn), pw, ph, box=crops[0 if wide else 1]), 26)
        shadow(img, (x, y0, x + pw, y0 + ph), 26)
        border = Image.new("RGBA", (pw + 10, ph + 10), (0, 0, 0, 0))
        ImageDraw.Draw(border).rounded_rectangle((0, 0, border.size[0] - 1, border.size[1] - 1), radius=30, fill=YELLOW + (255,))
        img.alpha_composite(border, (x - 5, y0 - 5))
        img.alpha_composite(pic, (x, y0))
        chip(img, x + 18, y0 + ph - 34, label, fl, 76, 22, YELLOW + (255,), BLACK)
    ImageDraw.Draw(img).text((W / 2, H * 0.885), "OpenAI DevDay 2026｜中文同传", font=ft, fill=(235, 235, 240), anchor="ma")
    return img.convert("RGB")


# ---------------------------------------------------------------- C 黄色对话气泡
def circle_avatar(size):
    face = load("g_7.0.png").crop((400, 70, 980, 650))
    face = ImageEnhance.Brightness(face).enhance(1.3).resize((size, size), Image.LANCZOS)
    ring = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    m = Image.new("L", (size + 12, size + 12), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size + 11, size + 11), fill=255)
    ring.paste(Image.new("RGB", (size + 12, size + 12), WHITE), (0, 0), m)
    mm = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mm).ellipse((0, 0, size - 1, size - 1), fill=255)
    ring.paste(face, (6, 6), mm)
    return ring


def make_c(W, H):
    wide = W / H > 1.5
    img = gradient(W, H, (255, 224, 96), (255, 190, 30)).convert("RGBA")
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    for (px, py, r, a) in [(0.04, 0.9, 120, 60), (0.30, 0.97, 70, 70), (0.52, 0.04, 90, 55), (0.97, 0.06, 150, 60), (0.93, 0.93, 100, 70),
                           (0.62, 0.50, 36, 70), (0.12, 0.45, 28, 80), (0.45, 0.62, 44, 60)]:
        dd.ellipse((W * px - r, H * py - r, W * px + r, H * py + r), fill=(255, 255, 255, a))
    img.alpha_composite(deco)
    d = ImageDraw.Draw(img)
    if wide:
        P = dict(tx=90, f0=50, y0=60, f1=150, y1=112, pill_y=316, pill_h=196, fb=56, lh=76, pady=26, av=150, bx=960, bw=880, y_b=100, g_user=82, g_dot=70)
    else:
        P = dict(tx=60, f0=44, y0=44, f1=128, y1=92, pill_y=262, pill_h=164, fb=42, lh=56, pady=18, av=92, bx=60, bw=1320, y_b=444, g_user=50, g_dot=28)
    d.text((P["tx"], P["y0"]), "OpenAI DevDay", font=font(P["f0"], 800), fill=BLACK)
    d.text((P["tx"], P["y1"]), "演示翻车后", font=font(P["f1"], 900), fill=BLACK)
    f2 = font(P["f1"], 900)
    chip(img, P["tx"], P["pill_y"], "重演 dots", f2, P["pill_h"], 34, BLACK + (255,), YELLOW)
    ff, fc = font(40 if wide else 36, 800), font(46, 800)
    if wide:
        x = P["tx"]
        for t in ("订机票", "选酒店", "整理用户反馈"):
            x = chip(img, x, 560, t, fc, 88, 30, WHITE + (255,), BLACK) + 16
        chip(img, P["tx"], 880, "中文同传", ff, 76, 30, BLACK + (255,), YELLOW)
    else:
        chip(img, W - 60, 54, "中文同传", ff, 64, 26, BLACK + (255,), YELLOW, anchor_x="right")

    fb, fs = font(P["fb"], 700), font(34, 800)
    av = circle_avatar(P["av"])
    bx, bw, lh, pady, avs = P["bx"], P["bw"], P["lh"], P["pady"], P["av"]

    def bubble(y, text, mine, label=None):
        if mine:
            x_left = bx + avs + 26
            max_w = bx + bw - x_left - 70
        else:
            max_w = bw - 70
        lines = wrap(d, text, fb, max_w)
        inner = max(tw(d, ln, fb) for ln in lines)
        h, wid = len(lines) * lh + 2 * pady, inner + 70
        x0 = x_left if mine else bx + bw - wid
        box = (int(x0), int(y), int(x0 + wid), int(y + h))
        shadow(img, box, 40, blur=16, alpha=90, dy=8)
        ImageDraw.Draw(img).rounded_rectangle(box, radius=40, fill=(WHITE if mine else BLACK) + (255,))
        for k, ln in enumerate(lines):
            ImageDraw.Draw(img).text((x0 + 35, y + pady + (k + 0.5) * lh), ln, font=fb, fill=BLACK if mine else WHITE, anchor="lm")
        if mine:
            img.alpha_composite(av, (int(bx), int(y + h / 2 - av.size[1] / 2)))
        if label:
            ImageDraw.Draw(img).text((x0 + 10, y - 8), label, font=fs, fill=BLACK, anchor="lb")
        return y + h

    y = P["y_b"]
    y = bubble(y, "明天要去洛杉矶，帮我订机票、选酒店", True) + P["g_user"]
    y = bubble(y, "好，我来安排。", False, "dot") + P["g_dot"]
    y = bubble(y, "再帮我整理一下用户反馈", True) + P["g_user"]
    bubble(y, "我来办。", False, "dot")
    return img.convert("RGB")


def main():
    for name, fn in (("A", make_a), ("B", make_b), ("C", make_c)):
        for tag, (w, h) in (("16x9", (1920, 1080)), ("4x3", (1440, 1080))):
            fn(w, h).save(HERE / f"封面_{name}_{tag}.png")
    # 预览总览：三种各取 16:9 和 4:3，缩小拼一张（行 = 方案）
    rows = []
    for name in "ABC":
        a = Image.open(HERE / f"封面_{name}_16x9.png").resize((640, 360), Image.LANCZOS)
        b = Image.open(HERE / f"封面_{name}_4x3.png").resize((480, 360), Image.LANCZOS)
        rows.append((a, b))
    gut = 80                                   # 左边留一栏放 A / B / C，不盖住封面
    sheet = Image.new("RGB", (gut + 640 + 30 + 480 + 30, 30 + 3 * (360 + 30)), (34, 34, 38))
    for r, (a, b) in enumerate(rows):
        y = 30 + r * 390
        sheet.paste(a, (gut, y))
        sheet.paste(b, (gut + 640 + 30, y))
        ImageDraw.Draw(sheet).text((gut / 2, y + 180), "ABC"[r], font=font(56, 900), fill=(255, 255, 255), anchor="mm")
    sheet.save(HERE / "封面_三选一_预览.png")
    print("六张 + 预览总览已生成")


if __name__ == "__main__":
    import sys
    main_openai() if "--openai" in sys.argv else main()
