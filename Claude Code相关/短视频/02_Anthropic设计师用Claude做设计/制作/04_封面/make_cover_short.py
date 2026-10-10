# -*- coding: utf-8 -*-
r"""第 2 条的封面：成片里的真实画面（上框 Nate 的脸、下框 Claude Design 做的新手引导）原样 + 短钩子大字，出三个比例。

  python make_cover_short.py            → cover_3x4.png（1080×1440）、cover_16x9.png（1920×1080）、cover_4x3.png（1440×1080）、_总览.png

做法：画面不从成片里截图（有贴纸压在上框右上角、边角是圆的），而是按台本里 D04 那段的裁切参数回原片（4K）取同一时刻的帧，缩进和成片一样的“边框 6”
（7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸“Claude 官方 YouTube”），底是本条的橙色印花；钩子大字 = 白字 + 墨色描边 + 硬投影（强调行橙色），样式照技能 make_cover.py 的 shot 风格。
封面协定（用户）：大字简短（每行 ≤ 6 字）、不放最下面那行小字、主角放大；平台标题写详细，和封面不写同一句。
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent                      # 制作/04_封面
EP = HERE.parents[1]
sys.path.insert(0, str(EP / "制作" / "00_整片"))
import config as C  # noqa: E402

SS = 2                                                      # 超采样倍数
HOOK = ["不只写代码", "还能做设计"]
ACCENT_LINE = 1
SRC_DIR = HERE / "_src"

# 原片帧：D04 段（成片 18.6–27.6 s）第 6.9 s 处 → 上框 = 原片 25.0417 + 6.9 = 31.94 s，裁切中心 (960,560) 宽 1500（1080p 坐标，原片 4K 乘 2）；
# 下框 = 原片 59.4 s 的定格，裁切从 (1340,600,1080) 平滑推到 (1120,665,640)，6.9 s 处约 (1150,656,700)。
TOP_FRAME = (31.94, (420, 276, 3000, 1688))                 # (原片秒, 4K 像素裁切 x, y, w, h)
BOT_FRAME = (59.40, (1600, 918, 1400, 788))


def vfont(px, weight):
    f = ImageFont.truetype(str(C.VAR_FONT), int(round(px)))
    f.set_variation_by_axes([weight])
    return f


def grab(t, crop, name):
    SRC_DIR.mkdir(exist_ok=True)
    png = SRC_DIR / f"{name}_{t:.2f}.png"
    if not png.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(C.SRC["design"]), "-frames:v", "1", str(png)], check=True)
    x, y, w, h = crop
    return Image.open(png).convert("RGB").crop((x, y, x + w, y + h))


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def pattern_bg(w, h):
    """底：米白 + 本条背景印花（1080×2340）。窄的取一段，宽的用两段拼（印花很淡，接缝看不出）。"""
    pat = Image.open(C.HERE / "bg.png").convert("RGBA")
    base = Image.new("RGBA", (w, h), C.BG + (255,))
    if w <= 1080:
        y0 = 420
        base.alpha_composite(pat.crop((0, y0, w, y0 + h)), (0, 0))
    else:
        base.alpha_composite(pat.crop((0, 300, 1080, 300 + h)), (0, 0))
        base.alpha_composite(pat.crop((0, 1240, w - 1080, 1240 + h)), (1080, 0))
    return base.convert("RGB").resize((w * SS, h * SS), Image.LANCZOS)


def sticker():
    """成片里右上角的黄贴纸（build/badge.png 是整幅透明 PNG）→ 裁出贴纸本身，返回 (图, 贴纸左上角相对上框外框右上角的偏移 dx, dy)。"""
    bg = Image.open(C.BUILD / "badge.png").convert("RGBA")
    bb = bg.getbbox()
    st = bg.crop(bb)
    return st, (bb[0] - (C.BOX_X + C.BOX_W), bb[1] - C.TOP_Y)


def draw_frame(cv, inner, x, y, iw, ih, with_sticker=False, scale=1.0):
    """cv：超采样后的画布；x, y, iw, ih：最终像素（1×）。边框 6：7 px 黑描边、14 px 橙色硬阴影、圆角 14。"""
    s = SS
    pad, sh, r = C.PAD, C.SHADOW, C.RADIUS
    ow, oh = iw + 2 * pad, ih + 2 * pad
    shadow = Image.new("L", cv.size, 0)
    shadow.paste(rmask(ow * s, oh * s, r * s), ((x + sh) * s, (y + sh) * s))
    cv.paste(Image.new("RGB", cv.size, C.ORANGE), (0, 0), shadow)
    cv.paste(Image.new("RGB", (ow * s, oh * s), C.INK), (x * s, y * s), rmask(ow * s, oh * s, r * s))
    im = inner.resize((iw * s, ih * s), Image.LANCZOS)
    cv.paste(im, ((x + pad) * s, (y + pad) * s), rmask(iw * s, ih * s, C.INNER_RADIUS * s))
    if with_sticker:
        st, (dx, dy) = sticker()
        k = s * scale
        st2 = st.resize((int(st.width * k), int(st.height * k)), Image.LANCZOS)
        cv.paste(st2, (int((x + ow) * s + dx * k), int(y * s + dy * k)), st2)
    return ow, oh


def measure(lines, avail_w, fs_max):
    """字放不下就缩：返回 (字号, 描边 px（超采样后）, 字体, 文字块宽 1×)。"""
    fs = fs_max
    while True:
        f = vfont(fs * SS, 900)
        stroke = max(2, round(fs * 0.047 * SS))
        w = max(f.getlength(t) for t in lines) + 2 * stroke
        if w / SS <= avail_w or fs < 90:
            return fs, stroke, f, w / SS
        fs -= 4


def hook_text(cv, lines, left, top, avail_w, fs_max, align="left", line_h=1.14):
    """白字 + 墨描边 + 硬投影（强调行橙色）。返回 (字号, 文字块宽, 文字块高)。"""
    s = SS
    fs, stroke, f, bw = measure(lines, avail_w, fs_max)
    sh = round(fs * 0.059 * s)
    d = ImageDraw.Draw(cv)
    pitch = fs * line_h * s
    for i, t in enumerate(lines):
        tw = f.getlength(t)
        x = left * s + (0 if align == "left" else (avail_w * s - tw) / 2 if align == "center" else avail_w * s - tw)
        cy = top * s + pitch * (i + 0.5)
        fill = C.ORANGE if i == ACCENT_LINE else C.WHITE
        d.text((x + sh, cy + sh), t, font=f, fill=C.INK, stroke_width=stroke, stroke_fill=C.INK, anchor="lm")
        d.text((x, cy), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=C.INK, anchor="lm")
    return fs, bw, pitch * len(lines) / s


def finish(cv, w, h, name):
    out = cv.resize((w, h), Image.LANCZOS)
    out.save(HERE / name)
    return out


def main():
    top_img = grab(*TOP_FRAME, "top")
    bot_img = grab(*BOT_FRAME, "bot")
    results = []

    # ---- 3:4（1080×1440）：钩子在上，两个框叠在下面
    w, h = 1080, 1440
    cv = pattern_bg(w, h)
    fs, bw, bh = hook_text(cv, HOOK, 70, 56, w - 140, 168, align="center")
    s_ = 0.86
    iw, ih = round(846 * s_ / 2) * 2, round(476 * s_ / 2) * 2
    ow = iw + 2 * C.PAD
    x0 = (w - ow - C.SHADOW) // 2
    y_top = int(56 + bh) + 40
    draw_frame(cv, top_img, x0, y_top, iw, ih, with_sticker=True, scale=s_)
    draw_frame(cv, bot_img, x0, y_top + ih + 2 * C.PAD + 24, iw, ih)
    end_y = y_top + 2 * (ih + 2 * C.PAD) + 24 + C.SHADOW
    results.append(("3x4", finish(cv, w, h, "cover_3x4.png"), f"大字 {fs} px（宽 {bw:.0f}），框 {iw}×{ih}，内容底 {end_y}/{h}"))

    # ---- 16:9（1920×1080）：字在左，两个框叠在右
    w, h = 1920, 1080
    cv = pattern_bg(w, h)
    # B 站首页把 16:9 封面切成 16:10（x 96–1824），内容收在 x 110–1810 里：右边框的硬阴影 + 贴纸不被切
    s_ = 0.90
    iw, ih = round(846 * s_ / 2) * 2, round(476 * s_ / 2) * 2
    ow, oh = iw + 2 * C.PAD, ih + 2 * C.PAD
    x0 = 1810 - C.SHADOW - ow
    y_top = (h - (2 * oh + 24 + C.SHADOW)) // 2
    left = 110
    avail = x0 - left - 50
    fs = measure(HOOK, avail, 176)[0]
    bh = fs * 1.14 * len(HOOK)
    fs, bw, bh = hook_text(cv, HOOK, left, (h - bh) / 2, avail, 176, align="left")
    draw_frame(cv, top_img, x0, y_top, iw, ih, with_sticker=True, scale=s_)
    draw_frame(cv, bot_img, x0, y_top + oh + 24, iw, ih)
    results.append(("16x9", finish(cv, w, h, "cover_16x9.png"), f"大字 {fs} px（宽 {bw:.0f}），框 {iw}×{ih}，左 {x0}"))

    # ---- 4:3（1440×1080）：钩子在上，两个框并排在下
    w, h = 1440, 1080
    cv = pattern_bg(w, h)
    s_ = 0.76
    iw, ih = round(846 * s_ / 2) * 2, round(476 * s_ / 2) * 2
    ow, oh = iw + 2 * C.PAD, ih + 2 * C.PAD
    total_w = 2 * ow + 28
    x0 = (w - total_w - C.SHADOW) // 2
    fs = measure(HOOK, w - 140, 184)[0]
    bh = fs * 1.14 * len(HOOK)
    gap = 40
    content_h = bh + gap + oh + C.SHADOW
    top0 = (h - content_h) / 2
    fs, bw, bh = hook_text(cv, HOOK, 70, top0, w - 140, 184, align="center")
    y_f = int(top0 + bh + gap)
    draw_frame(cv, top_img, x0, y_f, iw, ih, with_sticker=True, scale=s_)
    draw_frame(cv, bot_img, x0 + ow + 28, y_f, iw, ih)
    results.append(("4x3", finish(cv, w, h, "cover_4x3.png"), f"大字 {fs} px（宽 {bw:.0f}），框 {iw}×{ih}，内容 {top0:.0f}–{y_f + oh + C.SHADOW}"))

    for k, im, info in results:
        print(f"cover_{k}.png {im.size[0]}×{im.size[1]}：{info}")
    sheet = Image.new("RGB", (60 + 540 + 960 + 720 + 40, 980), (225, 225, 225))
    x = 20
    for k, im, _ in results:
        t = im.copy()
        t.thumbnail((960 if k != "3x4" else 540, 940))
        sheet.paste(t, (x, 20))
        x += t.width + 20
    sheet.save(HERE / "_总览.png")


if __name__ == "__main__":
    main()
