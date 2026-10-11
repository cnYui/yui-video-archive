# -*- coding: utf-8 -*-
"""一次性补丁：给 plan.py 加 S06（第一章解谜）、游戏原声段、S08（高潮）、S10（门槛 / 媒介转换）、S11（收尾）。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "plan.py"
s = p.read_text(encoding="utf-8")

# strip_caption 支持换徽章颜色
s = s.replace('def strip_caption(kicker, title, sub=""):', 'def strip_caption(kicker, title, sub="", color=None):')
s = s.replace("    tag = ui.badge(kicker, 28, ui.ORANGE)\n    base.alpha_composite(tag, (m + pad, m + pad))", "    tag = ui.badge(kicker, 28, color or ui.ORANGE)\n    base.alpha_composite(tag, (m + pad, m + pad))")

# 镜头：补几个
s = s.replace('    "dialog1": ("A", 364.6, 1,', '    "money": ("A", 284.4, 1, "第一章 · 事务所解谜", "钱不够：被登势一脚踢飞"),\n    "fly": ("A", 295.6, 1, "第一章 · 事务所解谜", "钱不够：被登势一脚踢飞"),\n    "dialog1": ("A", 364.6, 1,')

marker = "# ---------------------------------------------------------------- build"
add = '''# ---------------------------------------------------------------- S06 第一章：解谜
def s06(T, st):
    a, b = sec_range("S06")
    t0 = sec_range("S05")[1] + 0.3
    t_end = b + 0.4
    t_npc = ph("0193", "8个NPC", dt=-0.3)
    t_inv = ph("0193", "10个可以调查", dt=-0.3)
    t_rent = ph("0193", "房租", dt=-0.2)
    t_note = ph("0193", "字条", dt=-0.3)
    t_tang = ph("0193", "糖分", dt=-1.4)
    t_5000 = ph("0193", "5000日元", dt=-0.2)
    t_short = ph("0193", "还是不够", dt=-0.2)
    t_fly = ph("0193", "打飞", dt=-0.5)
    seq = [("street", t0, t_rent, 0.0), ("sofa", t_rent, t_tang, 233.4 - 241.0), ("tangfen", t_tang, t_short, 261.0 - 262.2), ("money", t_short, t_fly, 0.0), ("fly", t_fly, t_end, 0.0)]
    for shot, ta, tb, dt in seq:
        main_clip(T, shot, ta, tb, dt=dt, enter=("slide", 0, 40, 0.4) if shot == "street" else ("fade", 0.2))
        toc_mark(ta, tb, 1, SHOTS[shot][2])
    caption(T, "street", t0, t_rent)
    caption(T, "sofa", t_rent, t_tang)
    card_item(T, t_tang, t_short, (C_X, STRIP[1]), strip_caption("第一章 · 事务所解谜", "「糖分」字画后面，5000 日元", "最重视的东西……没错，是糖分"), z=6, enter=("fade", 0.2), exit=("fade", 0.15))
    caption(T, "money", t_short, t_end)
    # 右栏：数字 → 字条 → 糖分 → 5000
    card_item(T, t_npc, t_tang, (R_X, TOP), ui.stat_card(R_W, 200, "8", "个 NPC", "歌舞伎町大街上"), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.2))
    card_item(T, t_inv, t_tang, (R_X, TOP + 220), ui.stat_card(R_W, 200, "10", "处能调查", "每一处都有小对话"), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.2))
    T.add(SpriteItem(t_note, t_tang + 0.2, (R_X - 6, 500), sticky("重要的钱，藏在你最重视的东西后面。", R_W - 10, 262, rot=2.0, size=56), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    T.add(SpriteItem(t_tang + 0.1, t_end, (R_X - 6, 120), sticky("最重视的东西，是——糖分！", R_W - 10, 170, rot=-2.0, size=56), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    card_item(T, t_5000, t_end, (R_X, 360), ui.stat_card(R_W, 200, "5000", "日元", "字画后面的信封"), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.25))
    card_item(T, t_short, t_end, (R_X, 590), list_chip("还不够三个月的房租", ui.RED), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.25))
    # ---- 只有游戏原声的一段：实机放大居中（眼睛特写 → 一拳打穿墙）
    g0, g1 = t_end - 0.1, sec_range("S08")[0] - 0.2
    big = (402, 108, 1536, 864)
    t_mid = g0 + 3.4
    T.add(Panel(g0, t_mid, big, VideoSrc(CH["A"], 515.9, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=("fade", 0.3), exit=("fade", 0.2)))
    label(T, big, "第二章 · 眼睛特写，原片里就有", g0, t_mid, size=34, dy=-24)
    T.add(Panel(t_mid, g1, big, VideoSrc(CH["A"], 549.5, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=("fade", 0.2), exit=("fade", 0.3)))
    label(T, big, "下一秒：一拳打穿墙", t_mid, g1, size=34, dy=-24)


# ---------------------------------------------------------------- S08 高潮
def s08(T, st):
    a, b = sec_range("S08")
    t0 = a - 0.5
    t_end = b + 0.3
    t_roof = ph("0194", "三段混战", dt=-0.3)
    t_crowd = ph("0194", "各路人马", dt=-0.2)
    t_back = ph("0194", "被靠背", dt=-1.0)
    t_dawn = ph("0194", "撑到天亮", dt=-0.3)
    t_end_ch = ph("0194", "大截局", dt=-0.3)
    t_five = ph("0194", "五分钟", dt=-0.4)
    seq = [("rally", t0, t_roof, 470.0 - 466.0), ("roof", t_roof, t_crowd, 0.0), ("crowd", t_crowd, t_back, 0.0), ("backtoback", t_back, t_dawn, 0.0), ("dawn", t_dawn, t_end_ch, 0.0), ("kick", t_end_ch, t_end, 772.0 - 774.6)]
    for shot, ta, tb, dt in seq:
        main_clip(T, shot, ta, tb, dt=dt, enter=("slide", 0, 40, 0.4) if shot == "rally" else ("fade", 0.2))
        toc_mark(ta, tb, 1, SHOTS[shot][2])
        if shot == "kick":
            card_item(T, ta, tb, (C_X, STRIP[1]), strip_caption("终章", "定春一口咬下去，画面变灰，跳出个「完」", "一脚把「完」字踢飞"), z=6, enter=("fade", 0.2), exit=("fade", 0.2))
        elif shot == "rally":
            card_item(T, ta, t_back, (C_X, STRIP[1]), strip_caption("第十三章 · 银之魂篇", "屋顶三段混战，各路人马一组组杀进来", "原片这一篇只有 32 秒"), z=6, enter=("slide", 0, 30, 0.35), exit=("fade", 0.15))
        elif shot == "backtoback":
            card_item(T, ta, t_end_ch, (C_X, STRIP[1]), strip_caption("第十三章 · 银之魂篇", "和高杉背靠背，一路撑到天亮", ""), z=6, enter=("fade", 0.15), exit=("fade", 0.15))
    # 三个缩略图：三段混战 / 背靠背 / 撑到天亮
    thumbs(T, [("roof", "三段混战"), ("backtoback", "和高杉背靠背"), ("dawn", "一路撑到天亮")], t_five, t_end_ch, [[(t_roof, t_back)], [(t_back, t_dawn)], [(t_dawn, t_end_ch)]])
    num_sticker(T, MAIN, "将近 5 分钟的打斗", t_five, t_end_ch, 0, 50, ui.ORANGE, 2)
    num_sticker(T, MAIN, "银魂永不完结", ph("0194", "永不完结", dt=-0.3), t_end, 0, 50, ui.MARKER, -2)


# ---------------------------------------------------------------- S10 门槛 / 媒介转换
def s10(T, st):
    a, b = sec_range("S10")
    t_end = b + 0.3
    fade = ("fade", 0.22)
    rs = board_rects()
    # ---- I：别的动漫的图集（四张同时亮）
    t_o = ph("0194", "其他的动漫", dt=-0.6)
    t_giant = ph("0194", "巨人", dt=-0.5)
    t_naruto = ph("0194", "火影", dt=-0.4)
    t_mush = ph("0194", "无知转生", dt=-0.4)
    t_j = ph("0194", "门槛还剩什么", dt=-1.5)
    wk = MAT.parent
    atlas = [(MAT / "角色图集" / "总览.png", "银魂：这次做成了游戏", t_o), (wk / "进击的巨人" / "角色图集" / "总览.png", "进击的巨人", t_giant),
             (wk / "火影" / "角色图集" / "总览.png", "火影", t_naruto), (wk / "无职转生" / "角色图集" / "总览.png", "无职转生", t_mush)]
    for k, (path, lab, ta) in enumerate(atlas):
        T.add(Panel(ta, t_j, rs[k], ImageSrc(path, "cover", 0.5, 0.5, kb=(1.0, 1.1, 8.0)), {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade))
        label(T, rs[k], lab, ta, t_j, size=30)
    num_sticker(T, rs[3], "这些素材都能复用", ph("0194", "可以服用", dt=-0.3), t_j, 0, 50, ui.ORANGE, 2)
    toc_mark(t_o, t_j, 2, None)
    # ---- J：以前 vs 现在
    t_k = ph("0194", "不仅仅是游戏", dt=-0.3)
    x, y, w, h = WIDE
    lw = 820
    items = [("画画", "角色、背景、动作", ph("0194", "画画", dt=-0.3)), ("写代码", "上万行", ph("0194", "写代码", dt=-0.3)),
             ("作曲", "配乐和音效", ph("0194", "作曲", dt=-0.3)), ("组团队", "人越多越难", ph("0194", "团队", dt=-0.3))]
    T.add(SpriteItem(t_j, t_k, (x + 6, y - 14), ui.sticker("以前", 40, rot=-3), z=8, enter=("slide", 0, 20, 0.3), exit=fade))
    for i, (nm, sub, ta) in enumerate(items):
        yy = y + 56 + i * 192
        base, m = ui.card(lw, 170)
        d = ImageDraw.Draw(base)
        d.text((m + 40, m + 85), nm, font=ui.nsc(60), fill=ui.INK, anchor="lm")
        d.text((m + 290, m + 85), sub, font=ui.nsc(34, 600), fill=ui.GRAY, anchor="lm")
        T.add(SpriteItem(t_j + 0.2 * i, t_k, (x - m, yy - m), base, z=5, enter=("slide", -40, 0, 0.35), exit=fade))
        T.add(SpriteItem(ta, t_k, (x + lw - 110, yy + 53), ui.cross_mark(64), z=7, enter=("slide", 0, -20, 0.2), exit=fade))
    rx = x + lw + 60
    rw = x + w - rx
    t_want = ph("0194", "自己想要什么", dt=-0.5)
    t_say2 = ph("0194", "说清楚", dt=-0.5)
    t_make = ph("0194", "做出来", dt=-0.6)
    t_pick = ph("0194", "当然人是要看", dt=-0.2) if voice.find_phrase("0194", "当然人是要看") else ph("0194", "挑选", dt=-3.0)

    def right_card(stage):
        base, m = ui.card(rw, 803)
        d = ImageDraw.Draw(base)
        d.text((m + 40, m + 60), "现在，你只需要", font=ui.nsc(38, 600), fill=ui.GRAY)
        if stage >= 1:
            d.text((m + 40, m + 120), "想清楚你要什么，", font=ui.nsc(62), fill=ui.INK)
        if stage >= 2:
            d.text((m + 40, m + 206), "把它说清楚。", font=ui.nsc(62), fill=ui.ORANGE)
        return base
    m_r = ui.card(rw, 803)[1]
    dyn_item(T, t_want - 0.2, t_k, (rx - m_r, y + 56 - m_r), lambda tl: 0 if tl + t_want - 0.2 < t_want else (1 if tl + t_want - 0.2 < t_say2 else 2), lambda k: right_card(k), z=5, enter=("slide", 0, 40, 0.35), exit=fade)
    gw = rw - 72
    grect = (rx + 36, y + 56 + 330, gw, int(gw * 9 / 16))
    T.add(Panel(t_make, t_k, grect, VideoSrc(CH["D"], 475.0, dec=(gw, int(gw * 9 / 16)), flags="lanczos"), {"bw": 5, "sh": (7, 7)}, z=6, enter=("slide", 0, 40, 0.4), exit=fade))
    T.add(SpriteItem(t_make + 0.2, t_k, (rx + rw - 110, y + 56 + 18), ui.check_mark(66), z=7, enter=("slide", 0, -20, 0.25), exit=fade))
    T.add(SpriteItem(t_pick, t_k, (rx + rw - 330, y + 56 + 150), ui.sticker("审美：你来挑", 40, fill=ui.MARKER, rot=3), z=8, enter=("slide", 0, 20, 0.3), exit=fade))
    toc_mark(t_j, t_k, 2, None)
    # ---- K：任何知识都能换一种媒介
    t_media = ph("0194", "媒介", dt=-0.4)
    t_book = ph("0194", "大步头", dt=-0.5)
    t_ai = ph("0194", "AI工具", dt=-0.3)
    t_video = ph("0194", "做成视频", dt=-0.3)
    t_game = ph("0194", "做成游戏", dt=-0.3)
    t_fast = ph("0194", "更快速", dt=-0.3)
    srcs = [("一篇文章", ph("0194", "一篇文章", dt=-0.3)), ("一个视频", ph("0194", "一个视频", dt=-0.3)), ("一门课", ph("0194", "一门课", dt=-0.3)),
            ("一本漫画", ph("0194", "一本漫画", dt=-0.3)), ("一本小说", ph("0194", "一本小说", dt=-0.3))]
    for i, (txt, ta) in enumerate(srcs):
        base, m = ui.card(520, 112)
        d = ImageDraw.Draw(base)
        d.text((m + 40, m + 56), txt, font=ui.nsc(50), fill=ui.INK, anchor="lm")
        T.add(SpriteItem(ta, t_end, (x - m, y + 40 + i * 134 - m), base, z=5, enter=("slide", -40, 0, 0.35), exit=fade))
    T.add(SpriteItem(t_k, t_end, (x + 6, y - 14), ui.sticker("它们都可以……", 36, rot=-2), z=8, enter=("slide", 0, 20, 0.3), exit=fade))
    arrow = ui.arrow_right(96, ui.ORANGE)
    T.add(SpriteItem(t_media - 0.3, t_end, (x + 548, y + 40 + 300), arrow, z=5, enter=("slide", -30, 0, 0.3), exit=fade))
    gx, gy = x + 700, y + 20
    gw2, gh2 = 484, 272
    outs = [("ui_cover.png", "一篇文章 → 一条视频", t_media, (0.5, 0.5)), ("rl_frame.png", "一篇长文 → 一分钟短视频", t_media + 1.0, (0.5, 0.45)),
            ("courses_wall.png", "一门课 → 10 集", t_media + 2.0, (0.5, 0.5)), ("game_title.png", "一条视频 → 一个游戏", t_media + 3.0, (0.5, 0.5))]
    for k, (fn, lab, ta, (cx, cy)) in enumerate(outs):
        rect = (gx + (k % 2) * (gw2 + 24), gy + (k // 2) * (gh2 + 40), gw2, gh2)
        ring = [(t_video, t_game)] if k in (0, 1, 2) else [(t_game, t_fast)]
        T.add(Panel(ta, t_end, rect, ImageSrc(HERE / "mat" / fn, "cover", cx, cy, pixel=(fn == "game_title.png")), {}, z=4, enter=("slide", 0, 40, 0.4), exit=fade, ring=ring))
        label(T, rect, lab, ta, t_end, size=28, dx=-10, dy=-22)
    T.add(SpriteItem(t_book, t_media + 99, (x + 80, y + 700), ui.sticker("不用再啃大部头", 44, fill=ui.MARKER, rot=-3), z=8, enter=("slide", 0, 24, 0.3), exit=fade)) if False else None
    T.add(SpriteItem(t_book, t_ai, (gx + 40, gy + 2 * gh2 + 40 + 40), ui.sticker("不用再啃大部头，浪费时间", 44, fill=ui.MARKER, rot=-2), z=8, enter=("slide", 0, 24, 0.3), exit=fade))
    T.add(SpriteItem(t_fast, t_end, (gx + 40, gy + 2 * gh2 + 40 + 40), ui.sticker("更快地了解里面的内容和内涵", 44, fill=ui.ORANGE, rot=2), z=8, enter=("slide", 0, 24, 0.3), exit=fade))
    toc_mark(t_k, t_end, 2, None)


# ---------------------------------------------------------------- S11 收尾
def s11(T, st):
    a, b = sec_range("S11")
    t_end = TOTAL
    t_old = ph("0194", "以前是人去适应", dt=-0.3)
    t_new = ph("0194", "知识可以长成", dt=-0.3)
    t_wel = ph("0194", "欢迎来到", after=300.0 - 0.0, dt=-0.2) if False else b - 2.4
    card_item(T, t_old, t_new, (C_X, STRIP[1]), strip_caption("以前", "是人去适应知识的样子", "", color=ui.GRAY), z=6, enter=("slide", 0, 30, 0.35), exit=("fade", 0.15))
    card_item(T, t_new, t_wel, (C_X, STRIP[1]), strip_caption("现在", "知识可以长成你喜欢的样子", ""), z=6, enter=("fade", 0.15), exit=("fade", 0.2))
    T.add(SpriteItem(t_wel, t_end, (C_X, 716), title_sprite().crop((0, 0, C_W, 230)), z=6, enter=("slide", -40, 0, 0.35), exit=None))
    logo = Image.open(HERE / "mat" / "logo.png").convert("RGBA")
    logo = logo.resize((logo.width * 5 // 2, logo.height * 5 // 2), Image.NEAREST)
    T.add(SpriteItem(t_wel + 0.2, t_end, (R_X + (R_W - logo.width) // 2, 300), logo, z=6, enter=("slide", 0, 40, 0.45), exit=None))
    toc_mark(a - 0.5, t_end, 2, None)


'''
assert marker in s
s = s.replace(marker, add + marker, 1)
s = s.replace("    s05(T, st)\n    add_toc", "    s05(T, st)\n    s06(T, st)\n    s08(T, st)\n    s10(T, st)\n    s11(T, st)\n    add_toc")
p.write_text(s, encoding="utf-8")
print("patched")
