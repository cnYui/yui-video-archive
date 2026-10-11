# -*- coding: utf-8 -*-
r"""《我把〈银魂〉做成了剧情游戏 -- 幕后过程》封面（框版）：候选 A（用户选定）+ 候选 C（用户又要了一份），各三个比例（3:4 竖屏 1080×1440、16:9 1920×1080、4:3 1440×1080）+ 总览。

  python make_cover.py              → 封面_A_{3x4,16x9,4x3}.png（并复制成 封面_选定_*，成片第 0 帧用的就是它）、封面_C_{…}.png、封面_总览.png
  python make_cover.py --only C     只出 C（不动 封面_选定_*）

用户 2026-10-06 看了三个候选（A 银魂视频 / 长成游戏、B 不到 20 小时 / 做完 15 章、C 我用 AI / 做了个游戏）说：
  “用 A，但是标题修改为 欢迎进入人人皆可做游戏时代，标题为 我把《银魂》做成了剧情游戏 -- 幕后过程”——第一个“标题”= 封面大字，第二个 = 视频标题（封面字和标题不写同一句，见封面协定）；
  随后又说：“候选 C 你也做一份，标题为 我把《银魂》做成了游戏”——按同一个用法，C 的封面大字 = “我把《银魂》做成了游戏”（两行：我把《银魂》/ 做成了游戏，第 2 行橙字）。
第一版（三个候选）在 _旧稿_第一版/。

版式 = 短视频技能的“框版”（`短视频/skill/short-video/scripts/make_cover_framed.py`，用户 2026-10-05 定成所有视频统一的封面样式）：
钩子大字在框外（白字 + 橙字、黑描边 + 错位阴影，每行 ≤ 6 字，不放最下面那行小字）、画面缩进“边框 6”（7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸），
底是和成片同一张横版印花（landscape_orange；3:4 用竖版 pattern_orange）。技能脚本的 make() 按 2 行排；A 的大字是 3 行，所以这里用它的函数（measure / hook_text / draw_frame / fit）自己排一遍；16:9 的内容收在 x 110–1810。
画面（真实素材）：
  A 同一幕“全江户，集结！”：上 / 左 = 原片（03_银魂_像素风.mp4 的 292.3 s，那条 5 分半的像素视频），下 / 右 = 游戏实机（整部实况录屏 D 段 474.9 s，384×216 最近邻放大 5 倍）。
  C 游戏标题画面（实况 A 段第 2 秒）+ 他出镜的安静一帧（02_出镜/proxy/0190.mp4 的 0.25 秒：两手放下、闭嘴、正对镜头）做成左下角的小窗，和成片里的出镜框同一套（黑描边 + 橙色硬阴影）。
"""
import importlib.util
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent                      # 制作/04_封面
SRC = HERE / "_src"
ROOT = HERE.parent                                          # 制作
SKILL = Path(r"D:\大疆\短视频\skill\short-video\scripts\make_cover_framed.py")
BGDIR = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")
FONT = Path(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf")

spec = importlib.util.spec_from_file_location("mcf", SKILL)
mcf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcf)
mcf.FONT = FONT
mcf.HERE = HERE
mcf.SRC_DIR = SRC

SS, BGC, INK, ORANGE, WHITE = mcf.SS, mcf.BGC, mcf.INK, mcf.ORANGE, mcf.WHITE
PAD, SHADOW = mcf.PAD, mcf.SHADOW


def pattern_bg(w, h):
    """16:9 / 4:3 用横版印花（和成片同一张 landscape_orange），3:4 用竖版 pattern_orange。"""
    base = Image.new("RGBA", (w, h), BGC + (255,))
    if w > h:
        pat = Image.open(BGDIR / "landscape_orange.png").convert("RGBA")
        base.alpha_composite(pat.crop((0, 0, w, h)), (0, 0))
    else:
        pat = Image.open(BGDIR / "pattern_orange.png").convert("RGBA")
        base.alpha_composite(pat.crop((0, 300, w, 300 + h)), (0, 0))
    return base.convert("RGB").resize((w * SS, h * SS), Image.LANCZOS)


mcf.pattern_bg = pattern_bg


# ---------------------------------------------------------------- 小零件
def pill(cv, xy, text, fill, color, size=64):
    """左上角的小标签：粗黑描边的圆角药丸（“原片”白底黑字、“游戏”橙底白字，在深色画面上都看得清）。"""
    f = mcf.vfont(size, 800)
    d = ImageDraw.Draw(cv)
    tw = f.getlength(text)
    w, h = int(tw + 2 * size * 0.55), int(size * 1.5)
    x, y = xy
    d.rounded_rectangle([x + 6, y + 6, x + w + 6, y + h + 6], radius=h // 2, fill=INK)
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill, outline=INK, width=7)
    d.text((x + w / 2, y + h / 2 + 2), text, font=f, fill=color, anchor="mm")


def arrow_badge(cv, cx, cy, direction, d_=200):
    """橙色圆形箭头徽章（压在两张画面的分界线上）：direction = down / right。"""
    s = 3
    badge = Image.new("RGBA", (d_ * s, d_ * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    d.ellipse([0, 0, d_ * s - 1, d_ * s - 1], fill=ORANGE + (255,), outline=INK + (255,), width=10 * s)
    m = d_ * s / 2
    L, hw, hl = 0.30 * d_ * s, 0.10 * d_ * s, 0.22 * d_ * s            # 箭杆半长 / 箭杆半宽 / 箭头长
    if direction == "down":
        d.rectangle([m - hw, m - L, m + hw, m + L - hl * 0.6], fill=WHITE + (255,))
        d.polygon([(m - 0.24 * d_ * s, m + L - hl), (m + 0.24 * d_ * s, m + L - hl), (m, m + L + 0.04 * d_ * s)], fill=WHITE + (255,))
    else:
        d.rectangle([m - L, m - hw, m + L - hl * 0.6, m + hw], fill=WHITE + (255,))
        d.polygon([(m + L - hl, m - 0.24 * d_ * s), (m + L - hl, m + 0.24 * d_ * s), (m + L + 0.04 * d_ * s, m)], fill=WHITE + (255,))
    badge = badge.resize((d_, d_), Image.LANCZOS)
    shadow = Image.new("RGBA", (d_, d_), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([0, 0, d_ - 1, d_ - 1], fill=INK + (255,))
    cv.paste(shadow, (int(cx - d_ / 2 + 7), int(cy - d_ / 2 + 7)), shadow)
    cv.paste(badge, (int(cx - d_ / 2), int(cy - d_ / 2)), badge)


# ---------------------------------------------------------------- 候选 A 的画面：同一幕，原片 → 游戏
def rally_pair():
    orig = Image.open(ROOT / "v2" / "mat" / "orig_rally2.png").convert("RGB")                     # 原片 1920×1080（292.3 s，没有冲击环那一帧）
    game = Image.open(SRC / "g_rally_b.png").convert("RGB").resize((1920, 1080), Image.NEAREST)   # 游戏：D 段 474.9 s
    return orig, game


def inner_A(ratio):
    """stack = 上下叠放（3:4、16:9；每张裁掉上下的空天空和空地面，只留 860 px 高），sbs = 左右并排（4:3，整张）。"""
    orig, game = rally_pair()
    if ratio != "4x3":
        top, bot = 30, 890
        a, b = orig.crop((0, top, 1920, bot)), game.crop((0, top, 1920, bot))
        hh = bot - top
        cv = Image.new("RGB", (1920, 2 * hh), INK)
        cv.paste(a, (0, 0))
        cv.paste(b, (0, hh))
        ImageDraw.Draw(cv).rectangle([0, hh - 6, 1920, hh + 6], fill=INK)
        pill(cv, (34, 30), "原片", WHITE, INK)
        pill(cv, (34, hh + 30), "游戏", ORANGE, WHITE)
        arrow_badge(cv, 1920 // 2, hh, "down")
    else:
        cv = Image.new("RGB", (3840, 1080), INK)
        cv.paste(orig, (0, 0))
        cv.paste(game, (1920, 0))
        ImageDraw.Draw(cv).rectangle([1920 - 6, 0, 1920 + 6, 1080], fill=INK)
        pill(cv, (34, 30), "原片", WHITE, INK)
        pill(cv, (1920 + 34, 30), "游戏", ORANGE, WHITE)
        arrow_badge(cv, 1920, 540, "right")
    return cv


# ---------------------------------------------------------------- 候选 C 的画面：游戏标题画面 + 他的出镜小窗
def inner_C(ratio):
    base = Image.open(ROOT / "v2" / "mat" / "game_title.png").convert("RGB").resize((1920, 1080), Image.NEAREST)
    size, pad, sh = 480, 14, 20
    x, y = 52, 1080 - size - pad - 96                         # 左下角，让开底下那行“原作：空知英秋《银魂》｜同人像素致敬作品”和中间的 GINTAMA 横幅
    face = Image.open(SRC / "_face_0190_0.25.png").convert("RGB")
    cx, cy, half = 1030, 585, 470                             # 头肩正方形裁切
    face = face.crop((cx - half, cy - half, cx + half, cy + half)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size + 2 * pad, size + 2 * pad), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, m.width - 1, m.height - 1], radius=34, fill=255)
    base.paste(Image.new("RGB", m.size, ORANGE), (x - pad + sh, y - pad + sh), m)
    base.paste(Image.new("RGB", m.size, INK), (x - pad, y - pad), m)
    fm = Image.new("L", face.size, 0)
    ImageDraw.Draw(fm).rounded_rectangle([0, 0, face.width - 1, face.height - 1], radius=22, fill=255)
    base.paste(face, (x, y), fm)
    return base


CANDS = {
    "A": {"hook": ["欢迎进入", "人人皆可", "做游戏时代"], "accent": 2, "sticker": "同一幕：视频 → 游戏", "inner": inner_A,
          "cap34": 140, "cap169": 176, "cap43": 140, "gap34": 44, "gap43": 58, "maxw43": 1240,
          "note": "用户选定：大字 欢迎进入人人皆可做游戏时代；同一幕“全江户，集结！”原片 → 游戏"},
    "C": {"hook": ["我把《银魂》", "做成了游戏"], "accent": 1, "sticker": "幕后过程", "inner": inner_C,
          "cap34": 176, "cap169": 176, "cap43": 150, "gap34": 56, "gap43": 36, "maxw43": 1180,
          "note": "用户要的第二份：大字 我把《银魂》做成了游戏；标题画面 + 他出镜的小窗"},
}


# ---------------------------------------------------------------- 三个比例的排版（hook 可以是 2 行或 3 行）
def make_set(c):
    out = {}
    hook, al, stk, n = c["hook"], c["accent"], c["sticker"], len(c["hook"])
    # ---- 3:4（1080×1440）：钩子在上，框在下；整块竖直居中
    w, h = 1080, 1440
    cv = pattern_bg(w, h)
    im = c["inner"]("3x4")
    asp = im.width / im.height
    fs = mcf.measure(hook, w - 140, c["cap34"])[0]
    bh = fs * 1.14 * n
    gap, margin = c["gap34"], 66
    ih_max = h - 2 * margin - bh - gap - 2 * PAD - SHADOW
    iw, ih = mcf.fit(asp, 940, ih_max)
    ow = iw + 2 * PAD
    total = bh + gap + ih + 2 * PAD + SHADOW
    top0 = (h - total) / 2
    fs, bw, bh = mcf.hook_text(cv, hook, al, 70, top0, w - 140, c["cap34"], align="center")
    mcf.draw_frame(cv, im, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["3x4"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    # ---- 16:9（1920×1080）：字在左，框在右（内容收在 x 110–1810 里，B 站首页会把 16:9 切成 16:10）
    w, h = 1920, 1080
    cv = pattern_bg(w, h)
    im = c["inner"]("16x9")
    asp = im.width / im.height
    iw, ih = mcf.fit(asp, 900, 820)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    x0 = 1810 - SHADOW - ow
    avail = x0 - 110 - 40
    fs = mcf.measure(hook, avail, c["cap169"])[0]
    bh = fs * 1.14 * n
    fs, bw, bh = mcf.hook_text(cv, hook, al, 110, (h - bh) / 2, avail, c["cap169"], align="left")
    mcf.draw_frame(cv, im, x0, (h - oh - SHADOW) // 2, iw, ih, stk, 0.9)
    out["16x9"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}，框左 {x0}")
    # ---- 4:3（1440×1080）：钩子在上，框在下
    w, h = 1440, 1080
    cv = pattern_bg(w, h)
    im = c["inner"]("4x3")
    asp = im.width / im.height
    fs = mcf.measure(hook, w - 140, c["cap43"])[0]
    bh0 = fs * 1.14 * n
    gap = c["gap43"]
    iw, ih = mcf.fit(asp, c["maxw43"], h - 2 * PAD - SHADOW - bh0 - gap - 90)
    ow, oh = iw + 2 * PAD, ih + 2 * PAD
    total = bh0 + gap + oh + SHADOW
    top0 = (h - total) / 2
    fs, bw, bh = mcf.hook_text(cv, hook, al, 70, top0, w - 140, c["cap43"], align="center")
    mcf.draw_frame(cv, im, (w - ow - SHADOW) // 2, int(top0 + bh + gap), iw, ih, stk, 0.9)
    out["4x3"] = (cv.resize((w, h), Image.LANCZOS), f"大字 {fs} px，框 {iw}×{ih}")
    return out


def main():
    argv = sys.argv[1:]
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    results = {}
    for cid, c in CANDS.items():
        if only and cid != only:
            continue
        res = make_set(c)
        results[cid] = res
        for k, (im, info) in res.items():
            im.save(HERE / f"封面_{cid}_{k}.png")
            print(f"封面_{cid}_{k}.png {im.size[0]}×{im.size[1]}：{info}")
            if cid == "C":                                     # 用户最后选定的是 C（先选过 A，后来说“还是用C吧”）：封面_选定_* = C（成片第 0 帧用的就是它）
                shutil.copyfile(HERE / f"封面_C_{k}.png", HERE / f"封面_选定_{k}.png")
    # 总览：每个候选一行，三个比例并排
    th = {"3x4": (390, 520), "16x9": (924, 520), "4x3": (693, 520)}
    pad, rowh = 24, 580
    rows = [(cid, c) for cid, c in CANDS.items() if cid in results or not only]
    if only:                                                   # 只出了一个：总览里另一个读现成的文件
        for cid, c in CANDS.items():
            if cid not in results and all((HERE / f"封面_{cid}_{k}.png").is_file() for k in th):
                results[cid] = {k: (Image.open(HERE / f"封面_{cid}_{k}.png"), "") for k in th}
        rows = [(cid, c) for cid, c in CANDS.items() if cid in results]
    sheet = Image.new("RGB", (40 + sum(v[0] for v in th.values()) + 2 * pad, len(rows) * rowh + 20), (232, 232, 232))
    d = ImageDraw.Draw(sheet)
    y = 10
    for cid, c in rows:
        d.text((20, y + 4), f"封面 {cid}{'（用户选定，成片第 0 帧）' if cid == 'A' else '（用户又要的一份）'} · 大字：{''.join(c['hook'])} · {c['note'].split('；')[-1]}", font=mcf.vfont(26, 700), fill=INK)
        x = 20
        for k in ("3x4", "16x9", "4x3"):
            im = results[cid][k][0].copy()
            im.thumbnail(th[k])
            sheet.paste(im, (x, y + 44))
            x += th[k][0] + pad
        y += rowh
    sheet.save(HERE / "封面_总览.png")
    print("封面_总览.png", sheet.size)


if __name__ == "__main__":
    main()
