# -*- coding: utf-8 -*-
"""静态层：build/bg_<n>.png（米白底 + 背景印花 + 随步骤变化的小标签 + 两行大标题 + 上下两个边框 6）、build/mask_inner.png（框里画面的圆角蒙版）、build/badge.png（右上角黄色贴纸，盖在画面上）。

  python make_bg.py              # 读 build/timeline.json 里的 chips（没有就读 plan.py），一个标签一张底图
  python make_bg.py --bg pattern_ink.png   # 指定背景印花（默认：bg.json 里记的那张；没有就从技能的背景库里随机挑一张并记下来）

版式数字全部来自 config.py（技能 short-video 的 dual：版式 B + 边框 6，用户 2026-10-04 选定）。
背景：技能 short-video 的 assets/backgrounds/ 里三张 AI 工具图标印花（pattern_color / pattern_ink / pattern_orange，1080×2340 透明 PNG，透明度已烤进去），
  叠在米白 #FAF9F5 上，有印花就不画点阵；**每条随机挑一张**（用户 2026-10-04：“每一期视频随机挑选一张作为背景即可”，又对本条说：“视频记得加上 /short-video 里面规定的背景图片”），选择记在 bg.json。
边框 6：7 px 黑描边 + 橙色硬阴影（右下偏移 14 px）+ 右上角黄色贴纸（文字 = 画面来源，倾斜 3°，贴纸盖在画面上所以单独出 badge.png）。
标题：第一行黑 76 px / 900，第二行橙 60 px / 800 带黄荧光；小标签（kicker 行，y≈302）：[产品名 灰 32 px / 800] [橙色小药丸“第 N 步”] [说明 墨黑 32 px / 700]。
"""
import json
import random
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import config as C

sys.path.insert(0, str(C.EP / "台本"))
import plan  # noqa: E402

SS = 4
STICKER = "Claude 官方 YouTube"


def vfont(px, weight):
    f = ImageFont.truetype(str(C.VAR_FONT), px)
    f.set_variation_by_axes([weight])
    return f


def rounded_mask(w, h, r, ss=SS):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def pick_background():
    """背景印花：--bg 指定 > bg.json 里记的 > 从技能背景库随机挑一张（并记下来）。"""
    lib = sorted(p for p in C.BG_LIB.glob("pattern_*.png") if p.name != "pattern_none.png")
    assert lib, f"背景库是空的：{C.BG_LIB}"
    j = C.HERE / "bg.json"
    want = sys.argv[sys.argv.index("--bg") + 1] if "--bg" in sys.argv else None
    if want:
        src = C.BG_LIB / want
        assert src.is_file(), f"背景库里没有 {want}，可选：{', '.join(p.name for p in lib)}"
        how = "指定"
    elif j.exists():
        name = json.loads(j.read_text(encoding="utf-8"))["file"]
        src, how = C.BG_LIB / name, json.loads(j.read_text(encoding="utf-8")).get("how", "")
    else:
        src, how = random.SystemRandom().choice(lib), "随机（技能 short-video 的规矩：每条随机挑一张）"
    j.write_text(json.dumps({"file": src.name, "how": how, "lib": [p.name for p in lib]}, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(src, C.HERE / "bg.png")
    return src


def base_canvas(pattern):
    img = Image.new("RGBA", (C.W, C.H), C.BG + (255,))
    pat = Image.open(pattern).convert("RGBA")
    assert pat.size == (C.W, C.H), pat.size
    img.alpha_composite(pat)
    return img.convert("RGB")


def draw_frame(img, y):
    """边框 6：橙色硬阴影（右下偏移）+ 7 px 黑描边的圆角框；框里的画面之后由 ffmpeg 贴在 (BOX_X + PAD, y + PAD)。"""
    x, w, h, s = C.BOX_X, C.BOX_W, C.BOX_H, C.SHADOW
    sh = Image.new("L", (C.W, C.H), 0)
    sh.paste(rounded_mask(w, h, C.RADIUS), (x + s, y + s))
    img.paste(Image.new("RGB", (C.W, C.H), C.ORANGE), (0, 0), sh)
    fr = Image.new("L", (C.W, C.H), 0)
    fr.paste(rounded_mask(w, h, C.RADIUS), (x, y))
    img.paste(Image.new("RGB", (C.W, C.H), C.INK), (0, 0), fr)


def draw_title(img):
    d = ImageDraw.Draw(img)
    t1y = 280 + 43 + 22 + 46
    d.text((C.W / 2, t1y), plan.TITLE[0], font=vfont(76, 900), fill=C.INK, anchor="mm")
    f2 = vfont(60, 800)
    t2_top = 280 + 43 + 22 + 93 + 10
    w2 = f2.getlength(plan.TITLE[1])
    box_h = 75
    d.rectangle([C.W / 2 - w2 / 2 - 6, t2_top + box_h * 0.62, C.W / 2 + w2 / 2 + 6, t2_top + box_h * 0.94], fill=C.MARKER)
    d.text((C.W / 2, t2_top + box_h / 2), plan.TITLE[1], font=f2, fill=C.ORANGE, anchor="mm")
    return {"t1_w": round(vfont(76, 900).getlength(plan.TITLE[0])), "t2_w": round(w2)}


def draw_chip(img, chip, cy=302):
    """chip = (产品名, 第 N 步 或 None, 说明)。返回总宽。"""
    prod, step, desc = chip
    d = ImageDraw.Draw(img)
    fp, fd, fs = vfont(32, 800), vfont(32, 700), vfont(26, 800)
    gap = 16
    pw, dw = fp.getlength(prod), fd.getlength(desc)
    if step:
        sw = fs.getlength(step) + 28
        total = pw + gap + sw + gap + dw
    else:
        dot_w = fd.getlength("·")
        total = pw + gap + dot_w + gap + dw
    x = C.W / 2 - total / 2
    d.text((x, cy), prod, font=fp, fill=C.GREY, anchor="lm")
    x += pw + gap
    if step:
        ph = 44
        pill = Image.new("L", (int(sw) * SS, ph * SS), 0)
        ImageDraw.Draw(pill).rounded_rectangle([0, 0, int(sw) * SS - 1, ph * SS - 1], radius=ph // 2 * SS, fill=255)
        pill = pill.resize((int(sw), ph), Image.LANCZOS)
        img.paste(Image.new("RGB", (int(sw), ph), C.ORANGE), (int(x), int(cy - ph / 2)), pill)
        d.text((x + sw / 2, cy + 1), step, font=fs, fill=C.WHITE, anchor="mm")
        x += sw + gap
    else:
        d.text((x, cy), "·", font=fd, fill=C.GREY, anchor="lm")
        x += dot_w + gap
    d.text((x, cy), desc, font=fd, fill=C.INK, anchor="lm")
    return round(total)


def make_badge():
    """右上角黄色贴纸（index.html 的 .frame::after）：黄底 + 5 px 黑描边 + 10 px 圆角，字 900 26 px / 38 px 行高，左右内边距 16；
    right:-8px; top:-40px（相对框的 padding box，即外框右边 +1、上沿 −33），旋转 3°（顺时针）。贴纸盖在画面上，所以出成整幅透明 PNG。"""
    f = vfont(26, 900)
    tw = f.getlength(STICKER)
    w, h = int(round(tw + 32 + 10)), 48
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=10 * SS, fill=C.INK + (255,))
    d.rounded_rectangle([5 * SS, 5 * SS, (w - 5) * SS - 1, (h - 5) * SS - 1], radius=5 * SS, fill=C.MARKER + (255,))
    fbig = vfont(26 * SS, 900)
    d.text((w * SS / 2, h * SS / 2 + 1 * SS), STICKER, font=fbig, fill=C.INK + (255,), anchor="mm")
    big = big.rotate(-3, resample=Image.BICUBIC, expand=True)
    sticker = big.resize((big.width // SS, big.height // SS), Image.LANCZOS)
    cx, cy = C.BOX_X + C.BOX_W + 1 - w / 2, C.TOP_Y - 33 + h / 2
    fg = Image.new("RGBA", (C.W, C.H), (0, 0, 0, 0))
    fg.alpha_composite(sticker, (int(round(cx - sticker.width / 2)), int(round(cy - sticker.height / 2))))
    return fg


def main():
    C.BUILD.mkdir(exist_ok=True)
    pattern = pick_background()
    tlp = C.BUILD / "timeline.json"
    if tlp.exists():
        chips = json.loads(tlp.read_text(encoding="utf-8"))["chips"]
    else:
        chips = []
        for p in plan.PASSAGES:
            if list(p["chip"]) not in chips:
                chips.append(list(p["chip"]))
    base = base_canvas(pattern)
    widths = []
    for i, chip in enumerate(chips):
        img = base.copy()
        info = draw_title(img)
        widths.append(draw_chip(img, chip))
        draw_frame(img, C.TOP_Y)
        draw_frame(img, C.BOT_Y)
        img.save(C.BUILD / f"bg_{i}.png")
    rounded_mask(C.INNER_W, C.INNER_H, C.INNER_RADIUS).save(C.BUILD / "mask_inner.png")
    make_badge().save(C.BUILD / "badge.png")
    print(f"背景印花 {pattern.name}；{len(chips)} 张底图 → build/bg_<n>.png；标题宽 {info}；标签最宽 {max(widths)} px（≤ {C.W - 80}）")


if __name__ == "__main__":
    main()
