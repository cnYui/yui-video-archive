# -*- coding: utf-8 -*-
r"""短视频封面（框版）：成片里的真实界面画面缩进“边框 6”（7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸）+ 短钩子大字，出 3 个候选 × 三个比例 + 候选总览。

  python make_cover_framed.py <本条目录> [--only A]       读 <本条>\制作\04_封面\candidates_framed.json → 候选A_3x4.png（1080×1440）、候选A_16x9.png（1920×1080）、候选A_4x3.png（1440×1080）… + 候选总览.png
  python make_cover_framed.py <本条目录> --select A        用户选了 A：复制成 封面_选定_3x4 / 16x9 / 4x3.png
  （不写 <本条目录> 就按脚本所在目录当 04_封面——旧用法：把本脚本拷进 04_封面 里跑）

**2026-10-05 起这是所有封面（短视频 / 长视频）的统一样式**（用户贴了两张封面样图：“标题这里，统一图中的风格并落实到skill中，白色+橙色”）：
大字白字 + 橙字（accent_line 那行）、墨色粗描边 + 硬投影，画面缩进“边框 6”（7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸），底是印花；有脸的画面（访谈、人像）也用它，不再用 make_cover.py 的 full / shot / split。
candidates_framed.json 可以写顶层 "bg": "<1080×2340 印花 png 路径>"（横版长视频的引擎目录里没有竖屏印花，借短视频那条的 制作/00_整片/bg.png）。

为什么不用 make_cover.py 的 full 样式：full 是给“有人脸的画面”设计的（脸居中、字盖在画面上方的空处、箭头指脸），界面截图（终端、面板、网页）没有脸，字会盖住内容、3:4 裁窗会把面板切掉。
框版的做法照第 2 条（make_cover_short.py）：钩子大字在框外（3:4、4:3 在上，16:9 在左），画面在框里完整露出，底是本条的背景印花，和成片同一个版式。

candidates_framed.json：{"candidates": [{"id", "note", "recommend", "video", "t", "crop": [x0, y0, x1, y1]（占整帧的比例）, "big": [行1, 行2], "accent_line": 1, "sticker": "@ClaudeDevs · X"}]}
封面协定（用户）：大字简短（每行 ≤ 6 字）、不放最下面那行小字；平台标题写详细，和封面不写同一句。
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent                      # 制作/04_封面
EP = HERE.parents[1]
FONT = Path(r"D:\大疆\Claude Code相关\短视频\02_Anthropic设计师用Claude做设计\制作\00_整片\fonts\NotoSansSC.ttf")   # 变量字体（900 / 700 字重）
BG_PNG = EP / "制作" / "00_整片" / "bg.png"                  # 本条的背景印花（1080×2340 透明 PNG）
SS = 2
BGC, INK, ORANGE, MARKER, WHITE = (0xFA, 0xF9, 0xF5), (0x14, 0x14, 0x13), (0xFF, 0x4F, 0x1A), (0xFF, 0xD8, 0x4D), (255, 255, 255)
PAD, SHADOW, RADIUS, INNER_R = 7, 14, 14, 4
SRC_DIR = HERE / "_src"


def vfont(px, weight):
    f = ImageFont.truetype(str(FONT), int(round(px)))
    f.set_variation_by_axes([weight])
    return f


def grab(video, t, crop):
    SRC_DIR.mkdir(exist_ok=True)
    if Path(video).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):       # 底图是静态图（截图 / 拼图）：直接打开，不走 ffmpeg（ffmpeg -ss 0 对单帧图片会一帧都不出，还不报错）
        im = Image.open(video).convert("RGB")
    else:
        png = SRC_DIR / f"{Path(video).stem}_{t:.2f}.png"
        if not png.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(png)], check=True)
        im = Image.open(png).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = crop
    return im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def pattern_bg(w, h):
    pat = Image.open(BG_PNG).convert("RGBA")
    base = Image.new("RGBA", (w, h), BGC + (255,))
    if w <= 1080:
        base.alpha_composite(pat.crop((0, 420, w, 420 + h)), (0, 0))
    else:
        base.alpha_composite(pat.crop((0, 300, 1080, 300 + h)), (0, 0))
        base.alpha_composite(pat.crop((0, 1240, w - 1080, 1240 + h)), (1080, 0))
    return base.convert("RGB").resize((w * SS, h * SS), Image.LANCZOS)


def draw_sticker(cv, text, right, top, scale):
    """右上角黄贴纸（成片里的 badge：黄底、墨色描边、倾斜 3°），右边缘对齐 right、上边缘约在 top。"""
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
    """x, y, iw, ih：最终像素（1×），外框 = 内 + 2*PAD。边框 6：7 px 黑描边、14 px 橙色硬阴影、圆角 14。"""
    s = SS
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    shadow = Image.new("L", cv.size, 0)
    shadow.paste(rmask(ow * s, oh * s, RADIUS * s), ((x + SHADOW) * s, (y + SHADOW) * s))
    cv.paste(Image.new("RGB", cv.size, ORANGE), (0, 0), shadow)
    cv.paste(Image.new("RGB", (ow * s, oh * s), INK), (x * s, y * s), rmask(ow * s, oh * s, RADIUS * s))
    cv.paste(inner.resize((iw * s, ih * s), Image.LANCZOS), ((x + PAD) * s, (y + PAD) * s), rmask(iw * s, ih * s, INNER_R * s))
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


def make(c, inner):
    asp = inner.width / inner.height
    hook, al, stk = c["big"], c.get("accent_line", 1), c.get("sticker")
    out = {}
    # ---- 3:4（1080×1440）：钩子在上，框在下；整块竖直居中
    w, h = 1080, 1440
    cv = pattern_bg(w, h)
    iw, ih = fit(asp, 920, 860)
    fs = measure(hook, w - 140, 176)[0]
    bh = fs * 1.14 * len(hook)
    gap = 56
    total = bh + gap + ih + 2 * PAD + SHADOW
    top0 = max(70, (h - total) / 2)
    fs, bw, bh = hook_text(cv, hook, al, 70, top0, w - 140, 176, align="center")
    ow = iw + 2 * PAD
    draw_frame(cv, inner, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["3x4"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    # ---- 16:9（1920×1080）：字在左，框在右（内容收在 x 110–1810 里，B 站首页会把 16:9 切成 16:10）
    w, h = 1920, 1080
    cv = pattern_bg(w, h)
    iw, ih = fit(asp, 900, 820)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    x0 = 1810 - SHADOW - ow
    avail = x0 - 110 - 40
    fs = measure(hook, avail, 176)[0]
    bh = fs * 1.14 * len(hook)
    fs, bw, bh = hook_text(cv, hook, al, 110, (h - bh) / 2, avail, 176, align="left")
    draw_frame(cv, inner, x0, (h - oh - SHADOW) // 2, iw, ih, stk, 0.9)
    out["16x9"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}，框左 {x0}")
    # ---- 4:3（1440×1080）：钩子在上，框在下
    w, h = 1440, 1080
    cv = pattern_bg(w, h)
    fs = measure(hook, w - 140, 150)[0]
    bh0 = fs * 1.14 * len(hook)
    gap = 36
    iw, ih = fit(asp, 1180, h - 2 * PAD - SHADOW - bh0 - gap - 90)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    total = bh0 + gap + oh + SHADOW
    top0 = (h - total) / 2
    fs, bw, bh = hook_text(cv, hook, al, 70, top0, w - 140, 150, align="center")
    draw_frame(cv, inner, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["4x3"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    return out


def main():
    global HERE, EP, BG_PNG, SRC_DIR
    argv = sys.argv[1:]
    val_flags = ("--only", "--select")
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in val_flags)]
    if pos:                                                   # 给了本条目录：04_封面 / 背景印花都按它找
        EP = Path(pos[0])
        HERE = EP / "制作" / "04_封面"
        BG_PNG = EP / "制作" / "00_整片" / "bg.png"
        SRC_DIR = HERE / "_src"
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    if "--select" in sys.argv:
        k = sys.argv[sys.argv.index("--select") + 1]
        for r in ("3x4", "16x9", "4x3"):
            (HERE / f"封面_选定_{r}.png").write_bytes((HERE / f"候选{k}_{r}.png").read_bytes())
        print(f"已把候选 {k} 复制成 封面_选定_3x4 / 16x9 / 4x3.png")
        return
    spec = json.loads((HERE / "candidates_framed.json").read_text(encoding="utf-8"))
    if spec.get("bg"):
        BG_PNG = Path(spec["bg"])
    sheet_items = []
    for c in spec["candidates"]:
        if only and c["id"] != only:
            continue
        inner = grab(c["video"], c["t"], c["crop"])
        res = make(c, inner)
        for k, (im, info) in res.items():
            im.save(HERE / f"候选{c['id']}_{k}.png")
            print(f"候选{c['id']}_{k}.png {im.size[0]}×{im.size[1]}：{info}")
        sheet_items.append((c, res))
    if only:
        return
    # 总览：每个候选一行（3:4 / 16:9 / 4:3），标题行写候选说明
    rowh, pad = 520, 24
    th = {"3x4": (390, rowh), "16x9": (924, 520), "4x3": (693, 520)}
    W = 40 + sum(v[0] for v in th.values()) + 2 * pad
    sheet = Image.new("RGB", (W, len(sheet_items) * (rowh + 70) + 20), (232, 232, 232))
    d = ImageDraw.Draw(sheet)
    lab = vfont(30, 700)
    y = 20
    for c, res in sheet_items:
        d.text((20, y + 6), f"候选 {c['id']}{'（推荐）' if c.get('recommend') else ''}  ·  {c['note']}", font=lab, fill=INK)
        x = 20
        for k in ("3x4", "16x9", "4x3"):
            im = res[k][0].copy()
            im.thumbnail(th[k])
            sheet.paste(im, (x, y + 56))
            x += th[k][0] + pad
        y += rowh + 70
    sheet.save(HERE / "候选总览.png")
    print("候选总览.png", sheet.size)


if __name__ == "__main__":
    main()
