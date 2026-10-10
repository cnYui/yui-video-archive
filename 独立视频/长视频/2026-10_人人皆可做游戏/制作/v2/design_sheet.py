# -*- coding: utf-8 -*-
"""版式样板图：用真实素材把每种页面拼一张静帧，先定框、贴纸、卡片的样子，再做合成引擎。
  python design_sheet.py            → _design/page_*.png + _design/总览.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ui import *  # noqa
import gens

D = HERE / "_design"
S = D / "src"
MAT = Path(r"D:\大疆\游戏素材\银魂")
GAME = MAT / "游戏"


def gimg(name):
    return Image.open(S / f"{name}.png").convert("RGB")


def game_panel(name, w=1152, h=648):
    return gimg(name).resize((w, h), Image.NEAREST)


def face_panel(name, w, h, cx=0.5, cy=0.42):
    return fit_cover(gimg(name), w, h, cx, cy)


def toc(now, dot):
    return toc_card(["先玩一下", "怎么做的", "门槛还剩什么"], now, 15, dot)


def paste_card(cv, card_im_m, xy, opacity=1.0):
    im, m = card_im_m
    paste_rgba(cv, im, (xy[0] - m, xy[1] - m), opacity)


def text_in(cv, xy, text, font, fill=INK, anchor="la"):
    ImageDraw.Draw(cv).text(xy, text, font=font, fill=fill, anchor=anchor)


# ---------------------------------------------------------------- 各页
def page_open():
    """S01 开场：主画面 = 出镜；R = 原片 + 提示词；说明带 = 片名。"""
    cv = new_canvas()
    t = toc(None, None)
    paste_card(cv, t, (L_X, (TOP + BOT) // 2 - t[0].height // 2 + 10))
    put_panel(cv, face_panel("face_a", *MAIN[2:]), MAIN, sc=MARKER)
    # 片名（封面式描边字）放在说明带
    f1, f2 = nsc(86), nsc(100)
    outline_text(cv, (C_X + 8, 716), "欢迎来到", f1, WHITE, INK, 9, shadow=(5, 6))
    outline_text(cv, (C_X + 8, 806), "人人皆可做游戏的时代", f2, ORANGE, INK, 10, shadow=(5, 6))
    # R：原片 + 提示词
    r1 = (R_X, TOP, R_W, 295)
    put_panel(cv, fit_cover(gimg("orig_a"), R_W, 295, pixel=False), r1)
    label_on(cv, r1, "9 月 25 号 · 原片", 28)
    r2 = (R_X, 380, R_W, 519)
    card_im = card(R_W, 519)
    paste_card(cv, card_im, (r2[0], r2[1]))
    cx, cy = R_X + 28, 380 + 26
    paste_rgba(cv, badge("Opus 5.5", 26, ORANGE), (cx, cy))
    paste_rgba(cv, badge("Ultra Code", 26, INK), (cx + 150, cy))
    text_in(cv, (cx, cy + 62), "只说了一句话：", nsc(24, 600), GRAY)
    q = "“像素风《银魂》的经典场景，按顺序把经典场景列出来，然后去讲故事。”"
    fq = nsc(38)
    y = cy + 104
    for ln in wrap(q, fq, R_W - 56):
        text_in(cv, (cx, y), ln, fq, INK)
        y += 56
    text_in(cv, (cx, 380 + 519 - 30), "→ 《300 秒看完〈银魂〉》", nsc(28), ORANGE, "ls")
    return cv


def page_open_numbers():
    """S01 数字：出镜在主画面，R 摞数字卡。"""
    cv = new_canvas()
    t = toc(None, None)
    paste_card(cv, t, (L_X, (TOP + BOT) // 2 - t[0].height // 2 + 10))
    put_panel(cv, face_panel("face_b", *MAIN[2:]), MAIN, sc=MARKER)
    ys = [TOP, TOP + 224, TOP + 448, TOP + 672]
    data = [("15", "章", "剧情"), ("600+", "句", "台词"), ("1万+", "行", "代码，都是 AI 写的"), ("<20", "小时", "从头写到最后一章")]
    # 2 列 × 2 行
    for i, (n, u, c) in enumerate(data):
        x = R_X + (i % 2) * (R_W // 2 + 6)
        y = TOP + (i // 2) * 232
    # 单列四张（524 宽）
    for i, (n, u, c) in enumerate(data):
        paste_card(cv, stat_card(R_W, 200, n, u, c), (R_X, TOP + i * 220))
    # 说明带：做了什么
    paste_card(cv, card(C_W, STRIP[3]), (C_X, STRIP[1]))
    text_in(cv, (C_X + 34, STRIP[1] + 34), "银魂 · 像素剧情游戏", nsc(36), INK)
    text_in(cv, (C_X + 34, STRIP[1] + 92), "一个网页，双击就能玩 · 从那条视频的素材里长出来", nsc(28, 600), GRAY)
    return cv


def page_playlist(variant="orange"):
    """S03 实机：L = 出镜 + 目录，C = 实机 + 说明，R = 三个小游戏缩略图（当前这个亮着）。"""
    cv = new_canvas()
    put_panel(cv, face_panel("face_b", *FACE_RAIL[2:]), FACE_RAIL, sc=MARKER)
    t = toc(0, 10)
    paste_card(cv, t, (L_X, 454))
    put_panel(cv, game_panel("g_hair"), MAIN)
    label_on(cv, MAIN, "第十章 · 给将军剪头发", 32)
    # 说明带：键位
    paste_card(cv, card(C_W, STRIP[3]), (C_X, STRIP[1]))
    x = C_X + 40
    for k, l, s in [("J", "三连击", ""), ("K", "跳", "空中再按 J = 跳斩"), ("L", "防御", "按住")]:
        kc = keycap(k, l, s)
        paste_rgba(cv, kc, (x, STRIP[1] + 40))
        x += kc.width + 56
    # R 三缩略图
    th = [("g_hair", "给将军剪头发", True), ("g_sheep", "骑小绵羊躲路障", False), ("g_pachinko", "打柏青哥", False)]
    tw_, th_ = 464, 261
    y0 = TOP + (859 - 3 * th_ - 2 * 24) // 2
    for i, (n, lab, on) in enumerate(th):
        rect = (R_X + 30, y0 + i * (th_ + 24), tw_, th_)
        put_panel(cv, game_panel(n, tw_, th_), rect, bw=5, sh=(7, 7), sc=ORANGE if on else INK)
        label_on(cv, rect, lab, 26, dx=-10, dy=-22, rot=-2 if i % 2 == 0 else 2)
        if on:
            g, m = glow_ring(rect)
            paste_rgba(cv, g, (rect[0] - m, rect[1] - m))
    return cv


def board_rects(cols=2, rows=2, gap=24):
    x, y, w, h = WIDE
    cw, ch = (w - gap * (cols - 1)) // cols, (h - gap * (rows - 1)) // rows
    return [(x + c * (cw + gap), y + r * (ch + gap), cw, ch) for r in range(rows) for c in range(cols)]


mono_card = None


def page_assets():
    """S04 素材四件套：C+R 并成宽板，2×2。"""
    cv = new_canvas()
    put_panel(cv, face_panel("face_a", *FACE_RAIL[2:]), FACE_RAIL, sc=MARKER)
    paste_card(cv, toc(1, 0), (L_X, 454))
    rs = board_rects()
    atlas = Image.open(MAT / "角色图集" / "总览.png").convert("RGB")
    put_panel(cv, fit_cover(atlas, rs[0][2], rs[0][3], 0.5, 0.5), rs[0])
    label_on(cv, rs[0], "角色图集 · 42 个角色", 30)
    aw = gens.action_wall(rs[1][2], rs[1][3])
    put_panel(cv, aw(0.35), rs[1])
    label_on(cv, rs[1], "每人 31 个动作 · 11 种表情", 30)
    pl = gens.parallax(rs[2][2], rs[2][3])
    put_panel(cv, pl(2.0), rs[2])
    label_on(cv, rs[2], "背景全是代码画的 · 1600+ 张图层", 30)
    names = sorted(p.name for p in (MAT / "音频" / "音乐_a").glob("*.wav") if not p.name.endswith("_x2.wav"))[:12]
    lines = ["music/"] + ["  %s" % n for n in names] + ["sfx/  (88 files)"]
    put_panel(cv, gens.terminal_card(rs[3][2], rs[3][3], lines, "音频清单", 22), rs[3])
    label_on(cv, rs[3], "12 首 8 位配乐 · 80+ 音效", 30)
    # 数字贴纸
    for rect, txt in [(rs[0], "42"), (rs[1], "13124 帧")]:
        s = sticker(txt, 54, fill=ORANGE, rot=3)
        paste_rgba(cv, s, (rect[0] + rect[2] - s.width - 26, rect[1] + rect[3] - s.height - 22))
    return cv


def page_pipeline():
    """S05 从原片到游戏：2×2（原片 → 分镜 → 镜头表 → 游戏）。"""
    cv = new_canvas()
    put_panel(cv, face_panel("face_c", *FACE_RAIL[2:]), FACE_RAIL, sc=MARKER)
    paste_card(cv, toc(1, 2), (L_X, 454))
    rs = board_rects()
    put_panel(cv, fit_cover(gimg("orig_a"), rs[0][2], rs[0][3]), rs[0])
    label_on(cv, rs[0], "① 原片里的一个场景", 30)
    sb = Image.open(MAT / "剧情分镜" / "分镜图" / "s02_shinpachi.png").convert("RGB")
    put_panel(cv, fit_cover(sb, rs[1][2], rs[1][3], 0.5, 0.2), rs[1])
    label_on(cv, rs[1], "② 每个场景一张分镜图", 30)
    md = (MAT / "剧情分镜" / "场景分镜" / "s02_shinpachi.md").read_text(encoding="utf-8")
    i0 = md.index("SHOT LIST (scene")
    lines = [l.rstrip()[:62] for l in md[i0:].splitlines() if l.strip() and not l.startswith("```")][:16]
    put_panel(cv, gens.terminal_card(rs[2][2], rs[2][3], lines, "场景分镜 / s02_shinpachi.md · 镜头表", 21, hi=(3, 4)), rs[2])
    label_on(cv, rs[2], "③ 镜头表：哪一秒推近、谁站哪", 30)
    put_panel(cv, game_panel("g_street", rs[3][2], rs[3][3]), rs[3])
    label_on(cv, rs[3], "④ 游戏里的这一章", 30)
    # 步骤箭头
    for (a, b) in [(0, 1), (2, 3)]:
        ra, rb = rs[a], rs[b]
        ar = arrow_right(64, ORANGE)
        paste_rgba(cv, ar, ((ra[0] + ra[2] + rb[0]) // 2 - 32, ra[1] + ra[3] // 2 - 32))
    return cv


def page_note():
    """S06 实机 + 字条：R 是一张便利贴 + 两个数字。"""
    cv = new_canvas()
    put_panel(cv, face_panel("face_c", *FACE_RAIL[2:]), FACE_RAIL, sc=MARKER)
    paste_card(cv, toc(1, 1), (L_X, 454))
    put_panel(cv, game_panel("g_sofa"), MAIN)
    label_on(cv, MAIN, "第一章 · 事务所解谜", 32)
    # 说明带：数字
    x = C_X
    for txt in ["街上 8 个 NPC", "10 个能调查的地方", "找 5000 日元交房租"]:
        c = chip(txt, 34, WHITE)
        paste_rgba(cv, c, (x, STRIP[1] + 56))
        x += c.width + 26
    # 便利贴
    note = Image.new("RGBA", (R_W, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(note)
    d.rounded_rectangle((10, 18, R_W - 10, 372), radius=8, fill=INK)
    d.rounded_rectangle((0, 8, R_W - 20, 360), radius=8, fill=MARKER, outline=INK, width=5)
    try:
        fb = ImageFont.truetype("C:/Windows/Fonts/STXINGKA.TTF", 66)
    except Exception:
        fb = nsc(60)
    y = 58
    for ln in wrap("重要的钱，藏在你最重视的东西后面。", fb, R_W - 90):
        d.text((40, y), ln, font=fb, fill=INK)
        y += 92
    note = note.rotate(2.5, resample=Image.BICUBIC, expand=True)
    paste_rgba(cv, note, (R_X - 10, TOP + 10))
    # 糖分字画（缩略图）
    rect = (R_X + 30, TOP + 440, 464, 261)
    put_panel(cv, game_panel("g_street", 464, 261), rect, bw=5, sh=(7, 7))
    label_on(cv, rect, "「糖分」字画后面……", 26, dx=-10, dy=-22)
    return cv


def page_before_after():
    """S10 门槛：以前（4 张 ✗ 卡）→ 现在（一句话）。"""
    cv = new_canvas()
    put_panel(cv, face_panel("face_a", *FACE_RAIL[2:]), FACE_RAIL, sc=MARKER)
    paste_card(cv, toc(2, None), (L_X, 454))
    x, y, w, h = WIDE
    # 以前
    lw = 820
    items = [("画画", "角色、背景、动作"), ("写代码", "上万行"), ("作曲", "配乐和音效"), ("组团队", "人越多越难")]
    ch = (h - 3 * 22) // 4
    paste_rgba(cv, sticker("以前", 40, rot=-3), (x + 8, y - 18))
    for i, (a, b) in enumerate(items):
        yy = y + 56 + i * (ch + 22 - 14)
        paste_card(cv, card(lw, ch - 28), (x, yy))
        text_in(cv, (x + 40, yy + (ch - 28) / 2), a, nsc(54), INK, "lm")
        text_in(cv, (x + 40 + 240, yy + (ch - 28) / 2), b, nsc(32, 600), GRAY, "lm")
        paste_rgba(cv, cross_mark(64), (x + lw - 94, yy + (ch - 28) // 2 - 32))
    # 现在
    rx = x + lw + 60
    rw = x + w - rx
    rect = (rx, y + 40, rw, h - 40)
    c, m = card(rw, h - 40)
    paste_rgba(cv, c, (rx - m, y + 40 - m))
    paste_rgba(cv, sticker("现在", 40, fill=ORANGE, rot=3), (rx + rw - 150, y + 10))
    text_in(cv, (rx + 36, y + 110), "你只需要", nsc(36, 600), GRAY)
    text_in(cv, (rx + 36, y + 160), "想清楚你要什么，", nsc(58), INK)
    text_in(cv, (rx + 36, y + 236), "说清楚，", nsc(58), ORANGE)
    paste_rgba(cv, check_mark(64), (rx + rw - 100, y + 600))
    put_panel(cv, game_panel("g_rally", rw - 72, int((rw - 72) * 9 / 16)), (rx + 36, y + 360, rw - 72, int((rw - 72) * 9 / 16)), bw=5, sh=(7, 7))
    return cv


def main():
    D.mkdir(exist_ok=True)
    pages = [("01_开场", page_open), ("02_开场数字", page_open_numbers), ("03_实机", page_playlist), ("04_素材四件套", page_assets),
             ("05_从原片到游戏", page_pipeline), ("06_字条", page_note), ("07_门槛", page_before_after)]
    thumbs = []
    for name, fn in pages:
        cv = fn()
        im = cv.convert("RGB")
        im.save(D / f"page_{name}.png")
        thumbs.append((name, im.resize((1170, 540), Image.LANCZOS)))
        print("ok", name, flush=True)
    sheet = Image.new("RGB", (1170 * 2 + 30, (540 + 20) * ((len(thumbs) + 1) // 2) + 10), (230, 230, 235))
    d = ImageDraw.Draw(sheet)
    for i, (n, th) in enumerate(thumbs):
        x, y = 10 + (i % 2) * 1180, 10 + (i // 2) * 560
        sheet.paste(th, (x, y))
        d.text((x + 8, y + 4), n, font=nsc(22), fill=(255, 255, 0), stroke_width=3, stroke_fill=(0, 0, 0))
    sheet.save(D / "总览.png")


if __name__ == "__main__":
    main()
