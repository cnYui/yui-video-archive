# -*- coding: utf-8 -*-
"""一次性补丁：给 plan.py 加 S05（从原片到游戏 + 台词页）。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "plan.py"
s = p.read_text(encoding="utf-8")
s = s.replace('crop=(0.0, 0.0, 0.66, 0.2)), {"bw": 5', 'crop=(0.0, 0.0, 0.66, 0.224)), {"bw": 5')
s = s.replace('    t_atlas = ph("0193", "AI他自己去画", dt=-0.9)\n    t_act', '    t_atlas = a + 0.9\n    t_act')

marker = "# ---------------------------------------------------------------- build"
add = '''# ---------------------------------------------------------------- S05 从原片到游戏
def shot_lines(md_name, limit=64):
    md = (MAT / "剧情分镜" / "场景分镜" / md_name).read_text(encoding="utf-8")
    i0 = md.index("SHOT LIST")
    seg = md[i0:].split("```")[0].splitlines()
    return [l.rstrip()[:limit] for l in seg if l.strip()]


def table_src(lines, title, size, rect, t_start, phases):
    """镜头表终端卡。phases = [(t, scroll_lines, (高亮行…))]（t 是成片秒），按时间取最后一个已到的。"""
    w, h = rect[2], rect[3]

    def fn(tl):
        t = t_start + tl
        sc, hi = 0.0, ()
        for tt, a_, b_ in phases:
            if tt <= t:
                sc, hi = a_, b_
        return gens.terminal_card(w, h, lines, title, size, hi=hi, scroll=sc)
    return GenSrc(fn)


def s05(T, st):
    a, b = sec_range("S05")
    t_end = b + 0.3
    rs = board_rects()
    l02, l13 = shot_lines("s02_shinpachi.md"), shot_lines("s13_silver_soul.md")
    iD = [i for i, l in enumerate(l02) if l.startswith("  D ")][0]
    iE = [i for i, l in enumerate(l02) if l.startswith("  E ")][0]
    iW = [i for i, l in enumerate(l13) if "13.45" in l[:12]]
    iW = iW[0] if iW else 14
    t_orig = ph("0193", "原片场景", dt=-0.5)
    t_story = ph("0193", "15个大的", dt=-0.4)
    t_table = ph("0193", "镜头表", dt=-0.4)
    t_push = ph("0193", "哪一秒推进", dt=-0.2)
    t_who = ph("0193", "哪个角色站哪边", dt=-0.2)
    t_onom = ph("0193", "拟生字", dt=-0.2)
    t_file = ph("0193", "专门文件", dt=-0.3)
    t_fam = ph("0193", "名场面", dt=-0.3)
    t_wall = ph("0193", "打穿墙壁", dt=-0.4)
    t_rally = ph("0193", "全江户集结", dt=-0.4)
    t_mini = ph("0193", "小游戏解谜", dt=-0.5)
    t_say = ph("0193", "台词是", dt=-0.5)
    fade = ("fade", 0.22)
    SB = MAT / "剧情分镜" / "分镜图"
    # --- A 组：眼睛特写（s02 的 D 镜）
    tbl_a = table_src(l02, "场景分镜 / s02 / 镜头表", 21, rs[2], t_table, [(t_table, 0, ()), (t_push, 0, (1,)), (t_who, 0, (2,)), (t_onom, 0, (3,)), (t_fam, iD - 1, (iD, iD + 1))])
    e = t_wall - 0.15
    T.add(Panel(t_orig, e, rs[0], ImageSrc(HERE / "mat" / "orig_eyes.png", "cover"), {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade))
    label(T, rs[0], "① 原片里的一个场景", t_orig, e)
    T.add(Panel(t_story, e, rs[1], ImageSrc(SB / "s02_shinpachi.png", "cover", 0.5, 0.42), {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade))
    label(T, rs[1], "② 每个场景一张分镜图", t_story, e)
    T.add(Panel(t_table, e, rs[2], tbl_a, {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade))
    label(T, rs[2], "③ 镜头表：哪一秒推近、谁站哪、拟声字", t_table, e)
    T.add(Panel(t_file, e, rs[3], game_cover("eyes", rs[3][2:], vy=0.0), {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade))
    label(T, rs[3], "④ 游戏里的这一章", t_file, e)
    toc_mark(a - 0.2, t_wall - 0.15, 1, 2)
    # --- B 组：一拳打穿墙（s02 的 E 镜）
    e2 = t_rally - 0.15
    tbl_b = table_src(l02, "场景分镜 / s02 / 镜头表", 21, rs[2], t_wall, [(t_wall, iE - 1, (iE, iE + 1, iE + 2))])
    T.add(Panel(e, e2, rs[0], ImageSrc(HERE / "mat" / "orig_hit2.png", "cover"), {}, z=3, enter=fade, exit=fade))
    label(T, rs[0], "① 原片：一拳打穿墙", e, e2)
    T.add(Panel(e, e2, rs[1], ImageSrc(SB / "s02_shinpachi.png", "cover", 0.5, 0.62), {}, z=3, enter=fade, exit=fade))
    label(T, rs[1], "② 分镜图", e, e2)
    T.add(Panel(e, e2, rs[2], tbl_b, {}, z=3, enter=fade, exit=fade))
    label(T, rs[2], "③ 镜头表", e, e2)
    T.add(Panel(e, e2, rs[3], game_cover("wall", rs[3][2:], vy=0.0), {}, z=3, enter=fade, exit=fade))
    label(T, rs[3], "④ 游戏里：一拳打穿墙", e, e2)
    toc_mark(e, e2, 1, 2)
    # --- C 组：全江户，集结！（s13 的 W 镜）
    e3 = t_mini - 0.15
    tbl_c = table_src(l13, "场景分镜 / s13 / 镜头表", 21, rs[2], t_rally, [(t_rally, max(0, iW - 2), (iW, iW + 1))])
    T.add(Panel(e2, e3, rs[0], ImageSrc(HERE / "mat" / "orig_rally.png", "cover"), {}, z=3, enter=fade, exit=fade))
    label(T, rs[0], "① 原片：「全江户，集结！」", e2, e3)
    T.add(Panel(e2, e3, rs[1], ImageSrc(SB / "s13_silver_soul.png", "cover", 0.5, 0.5), {}, z=3, enter=fade, exit=fade))
    label(T, rs[1], "② 分镜图", e2, e3)
    T.add(Panel(e2, e3, rs[2], tbl_c, {}, z=3, enter=fade, exit=fade))
    label(T, rs[2], "③ 镜头表", e2, e3)
    T.add(Panel(e2, e3, rs[3], game_cover("rally", rs[3][2:], vy=0.0, dt=0.2), {}, z=3, enter=fade, exit=fade))
    label(T, rs[3], "④ 游戏里的同一幕", e2, e3)
    toc_mark(e2, e3, 1, 13)
    # --- D 组：小游戏解谜（四个小游戏同时放）
    t_d1 = t_say - 0.2
    items = [("hair", "给将军剪头发"), ("sheep", "骑小绵羊躲路障"), ("pachinko", "打柏青哥"), ("sofa", "翻沙发缝找字条")]
    for k, (shot, lab) in enumerate(items):
        T.add(Panel(e3 + 0.12 * k, t_d1, rs[k], game_cover(shot, rs[k][2:], vy=0.0), {}, z=3, enter=fade, exit=fade))
        label(T, rs[k], lab, e3 + 0.12 * k, t_d1)
    toc_mark(e3, t_d1, 1, None)
    # --- E：台词（实机 + 代码 + 口头禅便利贴）
    t_cat = ph("0193", "天然卷", dt=-0.4)
    t_k = ph("0193", "冬野湖", dt=-0.3)
    t_katsura = ph("0193", "不是假发", dt=-0.5)
    t_hab = ph("0193", "口头禅", dt=-0.3)
    t_e0 = t_say - 0.2
    main_clip(T, "dialog1", t_e0, t_katsura, enter=("slide", 0, 40, 0.4))
    main_clip(T, "katsura", t_katsura, t_end)
    toc_mark(t_e0, t_katsura, 1, 1)
    toc_mark(t_katsura, t_end, 1, 5)
    c1 = (MAT / "游戏" / "story" / "chapter1.js").read_text(encoding="utf-8").splitlines()
    i1 = [k for k, l in enumerate(c1) if "这是木刀。洞爷湖的。" in l][-1]
    c5 = (MAT / "游戏" / "story" / "chapter5.js").read_text(encoding="utf-8").splitlines()
    i5 = [k for k, l in enumerate(c5) if "'katsura', '不是假发，是桂！', { actor: k, expr: 'shout' }" in l][-1]

    def code_card(lines, first, hi, title):
        im = gens.code_view(C_W, STRIP[3], [l.strip()[:84] for l in lines], first, hi=hi, size=24, title=title)(0)
        return GenSrc(lambda tl, im=im: im)
    T.add(Panel(t_e0, t_katsura, STRIP, code_card(c1[i1 - 1:i1 + 2], i1, (1,), "story/chapter1.js"), {"bw": 5, "sh": (8, 8), "sc": ui.INK}, z=6, enter=("slide", 0, 30, 0.35), exit=("fade", 0.15)))
    T.add(Panel(t_katsura, t_end, STRIP, code_card(c5[i5 - 1:i5 + 2], i5, (1,), "story/chapter5.js"), {"bw": 5, "sh": (8, 8), "sc": ui.INK}, z=6, enter=("fade", 0.15), exit=("fade", 0.2)))
    notes = [(t_cat, "天然卷", -1.5), (t_k, "洞爷湖", 2.0), (t_katsura, "不是假发，是桂！", -2.0), (t_katsura + 1.15, "ヅラじゃない、桂だ！", 1.5), (t_hab, "口头禅都留着", -1.0)]
    for i, (t0, text, rot) in enumerate(notes):
        T.add(SpriteItem(t0, t_end, (R_X - 6, 40 + i * 150), sticky(text, R_W - 10, 118, rot=rot, size=54, fill=ui.MARKER if i != 4 else (255, 150, 110)), z=5, enter=("slide", 0, 30, 0.3), exit=("fade", 0.25)))


'''
assert marker in s
s = s.replace(marker, add + marker, 1)
s = s.replace("    s04(T, st)\n    add_toc", "    s04(T, st)\n    s05(T, st)\n    add_toc")
p.write_text(s, encoding="utf-8")
print("patched")
