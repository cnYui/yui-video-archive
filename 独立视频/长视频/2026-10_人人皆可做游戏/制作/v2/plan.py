# -*- coding: utf-8 -*-
"""plan.py —— 整条片子的页面时间线。build() → comp.Timeline。

时间全是成片秒（含开场 4 秒），画面点位用口播里的词对：ph(素材, "词") → 这个词在成片里第几秒。
版式规矩见 页面设计.md；小部件 ui.py、活素材 gens.py、合成引擎 comp.py。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import numpy as np
from PIL import Image, ImageDraw

import comp
import gens
import ui
import voice
from comp import Custom, FaceSrc, GenSrc, ImageSrc, Panel, SpriteItem, Sprite, Timeline, VideoSrc, ease_out, smooth, clamp, lerp
from ui import C_W, C_X, FACE_RAIL, L_W, L_X, MAIN, R_W, R_X, STRIP, TOP, WIDE

TL = voice.timeline()
TOTAL = voice.total(TL)
REC = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-06_全流程实况")
CH = {"A": REC / "A_序章到第三章" / "full.webm", "B": REC / "B_第四到第七章" / "full.webm", "C": REC / "C_第八到第十章" / "full.webm", "D": REC / "D_第十一章到终章" / "full.webm", "E": REC / "E_序章输一次重来" / "full.webm"}
ORIG = Path(r"D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\教程_Claude做视频\素材\展示视频\03_银魂_像素风.mp4")
FACE_TL = HERE.parent / "face_tl.mp4"
MAT = Path(r"D:\大疆\游戏素材\银魂")

# 实机镜头：(录像段, 起点秒, 章号, 章名, 说明)；起点来自 footage.json（2026-10-06 v1 选的），章号用来走目录里的 15 个点
SHOTS = {
    "prologue": ("A", 143.4, 0, "序章 · 白夜叉", "打天人部队长：看红光、躲大招"),
    "title": ("A", 1.0, None, "标题画面", "双击打开，就是这个标题画面"),
    "lose": ("E", 120.0, 0, "序章 · 白夜叉", "输了，从这一仗重来"),
    "money": ("A", 284.4, 1, "第一章 · 事务所解谜", "钱不够：被登势一脚踢飞"),
    "fly": ("A", 295.6, 1, "第一章 · 事务所解谜", "钱不够：被登势一脚踢飞"),
    "dialog1": ("A", 364.6, 1, "第一章 · 歌舞伎町大街", "台词：天然卷、洞爷湖"),
    "katsura": ("B", 303.6, 5, "第五章 · 桂与伊丽莎白", "台词：「不是假发，是桂！」"),
    "sheep": ("A", 895.0, 3, "第三章 · 小游戏", "骑小绵羊躲路障"),
    "pachinko": ("B", 499.0, 6, "第六章 · 小游戏", "打柏青哥：按 J 停转轮"),
    "hair": ("C", 386.8, 10, "第十章 · 小游戏", "给将军剪头发：看准时机"),
    "kondo": ("B", 93.0, 4, "第四章 · 真选组", "和近藤一对一决斗"),
    "rain": ("B", 653.5, 7, "第七章 · 红樱篇", "雨夜对人斩冈田似藏"),
    "street": ("A", 330.3, 1, "第一章 · 歌舞伎町大街", "8 个 NPC，10 个能调查的地方"),
    "sofa": ("A", 241.0, 1, "第一章 · 事务所解谜", "沙发缝里有张字条"),
    "tangfen": ("A", 262.2, 1, "第一章 · 事务所解谜", "「糖分」字画后面"),
    "eyes": ("A", 515.9, 2, "第二章 · 家庭餐厅", "眼睛特写，原片里就有"),
    "wall": ("A", 549.5, 2, "第二章 · 家庭餐厅", "一拳打穿墙"),
    "crowd": ("D", 359.0, 13, "第十三章 · 银之魂篇", "各路人马一组组杀进来"),
    "roof": ("D", 377.0, 13, "第十三章 · 银之魂篇", "屋顶第一段混战"),
    "rally": ("D", 466.0, 13, "第十三章 · 银之魂篇", "「全江户，集结！」"),
    "backtoback": ("D", 518.0, 13, "第十三章 · 银之魂篇", "和高杉背靠背"),
    "dawn": ("D", 591.0, 13, "第十三章 · 银之魂篇", "撑到天亮"),
    "kick": ("D", 774.6, 14, "终章 · 两年后", "定春咬头，一脚踢飞「完」"),
}


def ph(clip, text, after=0.0, dt=0.0):
    s = voice.find_phrase(clip, text, after)
    assert s is not None, (clip, text, after)
    return voice.out_time(TL, clip, s) + dt


def sec_range(sec):
    ps = [p for p in TL if p["sec"] == sec]
    return ps[0]["out_in"], ps[-1]["out_out"]


# ---------------------------------------------------------------- 小零件
def game_src(shot, size=(1152, 648), dt=0.0):
    ch, st = SHOTS[shot][0], SHOTS[shot][1]
    flags = "neighbor" if size == (1152, 648) else "lanczos"
    return VideoSrc(CH[ch], st + dt, dec=size, flags=flags)


def label(T, rect, text, t0, t1, size=30, rot=-2.5, dx=-14, dy=-26, corner="tl", z=20):
    s = ui.sticker(text, size, rot=rot)
    x, y, w, h = rect
    px = x + dx if corner == "tl" else x + w - s.width - dx
    return T.add(SpriteItem(t0 + 0.12, t1, (px, y + dy), s, z=z, enter=("slide", 0, -14, 0.25), exit=("fade", 0.15)))


def card_item(T, t0, t1, xy, card, z=8, enter=("slide", 0, 30, 0.3), exit=("fade", 0.2)):
    img, m = card
    return T.add(SpriteItem(t0, t1, (xy[0] - m, xy[1] - m), img, z=z, enter=enter, exit=exit))


class DynSprite:
    """按 key 缓存的动态精灵：key_fn(t_local) → key，make_fn(key) → PIL RGBA。"""

    def __init__(self, key_fn, make_fn):
        self.key_fn, self.make_fn = key_fn, make_fn


def dyn_item(T, t0, t1, xy, key_fn, make_fn, z=8, enter=("slide", 0, 30, 0.3), exit=("fade", 0.2)):
    class _I(SpriteItem):
        def _sprite(self, t):
            k = key_fn(t - self.t0)
            return comp._sprite_cache(("dyn", id(self), k), lambda: make_fn(k))
    it = _I(t0, t1, xy, None, z=z, enter=enter, exit=exit)
    return T.add(it)


def count_up(t_local, t_dur, target):
    return int(round(target * ease_out(t_local / t_dur)))


# ---------------------------------------------------------------- 出镜框和目录：跟着“脚本”走
def face_schedule():
    """出镜框在哪：[(t, mode)]；mode = main（中栏放大）/ rail（左栏小框）/ hide。"""
    s01 = sec_range("S01")
    s03 = sec_range("S03")
    s06 = sec_range("S06")
    s08 = sec_range("S08")
    s11 = sec_range("S11")
    t_o = ph("0194", "其他的动漫", dt=-0.6)
    return [(s01[0] - 0.4, "main"), (s03[0] - 0.9, "rail"), (s06[1] + 0.8, "hide"), (s08[0] - 0.6, "rail"), (s08[1] + 0.2, "main"), (t_o - 0.5, "rail"), (sec_range("S10")[1] + 0.1, "main"), (TOTAL, "end")]


FACE_RECT = {"main": MAIN, "rail": FACE_RAIL}
TWEEN = 0.5


def add_face(T):
    st = face_schedule()
    runs, cur = [], None
    for (t, m), (tn, _) in zip(st, st[1:]):
        if m == "hide":
            cur = None
            continue
        if cur is None:
            cur = {"t0": t, "t1": tn, "keys": [(t, FACE_RECT[m])], "mode": m}
            runs.append(cur)
        else:
            if m != cur["mode"]:
                cur["keys"] += [(t, FACE_RECT[cur["mode"]]), (t + TWEEN, FACE_RECT[m])]
                cur["mode"] = m
            cur["t1"] = tn
    for r in runs:
        keys = r["keys"] if len(r["keys"]) > 1 else r["keys"][0][1]
        T.add(Panel(r["t0"], r["t1"], keys, FaceSrc(FACE_TL), {"sc": ui.MARKER}, z=2, src_t0=0.0, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    return st


def face_mode_at(st, t):
    m = "hide"
    for tt, mm in st:
        if tt <= t:
            m = mm
    return m


def toc_y(st, t):
    return 454 if face_mode_at(st, t) == "rail" else 296


def add_toc(T, st, states):
    """states = [(t0, t1, now, dot)]；位置：出镜框在左栏时放它下面，否则垂直居中。"""
    for (t0, t1, now, dot) in states:
        card = ui.toc_card(["先玩一下", "怎么做的", "门槛还剩什么"], now, 15, dot)
        # 位置关键帧：按出镜框模式变化
        pts = sorted({t0, t1} | {tt for tt, _ in st if t0 < tt < t1} | {tt + TWEEN for tt, _ in st if t0 < tt + TWEEN < t1})
        keys = []
        for tt in pts:
            mode = face_mode_at(st, tt) if tt >= st[0][0] else "main"
            # 在 tween 期间的中间点用线性插值，由 SpriteItem 自己插
            y = 454 if mode == "rail" else 296
            keys.append((tt, (L_X - card[1], y - card[1])))
        # 去掉相邻重复，保证 smooth 插值只发生在变化的两点之间
        T.add(SpriteItem(t0 - 0.06, t1 + 0.06, keys if len(keys) > 1 else keys[0][1], card[0], z=3, enter=("fade", 0.12), exit=("fade", 0.12)))


# ---------------------------------------------------------------- 说明带
def strip_caption(kicker, title, sub="", color=None):
    w, h = C_W, STRIP[3]
    base, m = ui.card(w, h)
    d = ImageDraw.Draw(base)
    pad = 34
    tag = ui.badge(kicker, 28, color or ui.ORANGE)
    base.alpha_composite(tag, (m + pad, m + pad))
    d.text((m + pad, m + pad + 52), title, font=ui.nsc(58), fill=ui.INK)
    if sub:
        d.text((m + w - pad, m + pad + 14), sub, font=ui.nsc(28, 600), fill=ui.GRAY, anchor="ra")
    return base, m


def title_sprite():
    """片名（封面式描边字）：白字一行 + 橙字一行。"""
    im = Image.new("RGBA", (1500, 230), (0, 0, 0, 0))
    f1, f2 = ui.nsc(92), ui.nsc(112)
    ui.outline_text(im, (10, 0), "欢迎来到", f1, ui.WHITE, ui.INK, 10, shadow=(6, 7))
    ui.outline_text(im, (10, 104), "人人皆可做游戏的时代", f2, ui.ORANGE, ui.INK, 11, shadow=(6, 7))
    return im


def title_line_sprite(size=72):
    """片名一行：白字“欢迎来到” + 橙字“人人皆可做游戏的时代”（封面式描边字），宽 ≤ 中栏 1152。"""
    f = ui.nsc(size)
    a, b = "欢迎来到", "人人皆可做游戏的时代"
    wa, wb = f.getlength(a), f.getlength(b)
    gap = 26
    w = int(wa + gap + wb) + 40
    im = Image.new("RGBA", (w, int(size * 1.7)), (0, 0, 0, 0))
    ui.outline_text(im, (14, 8), a, f, ui.WHITE, ui.INK, 9, shadow=(5, 6))
    ui.outline_text(im, (14 + wa + gap, 8), b, f, ui.ORANGE, ui.INK, 9, shadow=(5, 6))
    return im


PROMPT_Q = "“像素风《银魂》的经典场景，按顺序把经典场景列出来，然后去讲故事。”"


def prompt_card(n_chars, badges=2):
    """提示词卡：两个徽章 + 一句话逐字打出来，卡片随行数长高。"""
    w = R_W
    fq = ui.nsc(38)
    lines = ui.wrap(PROMPT_Q, fq, w - 56)
    shown, k = [], 0
    for ln in lines:
        if k < n_chars:
            shown.append(ln[: n_chars - k])
        k += len(ln)
    h = 26 + 62 + 44 + max(1, len(shown)) * 56 + 22
    base, m = ui.card(w, h)
    d = ImageDraw.Draw(base)
    cx, cy = m + 28, m + 26
    if badges >= 1:
        base.alpha_composite(ui.badge("Ultra Code", 26, ui.INK), (cx, cy))
    if badges >= 2:
        base.alpha_composite(ui.badge("Opus 5.5", 26, ui.ORANGE), (cx + 168, cy))
    d.text((cx, cy + 62), "他只说了一句话：", font=ui.nsc(24, 600), fill=ui.GRAY)
    y = cy + 106
    for i, part in enumerate(shown):
        d.text((cx, y), part, font=fq, fill=ui.INK)
        if i == len(shown) - 1 and n_chars < len(PROMPT_Q):
            wx = cx + fq.getlength(part)
            d.rectangle((wx + 4, y + 6, wx + 12, y + 46), fill=ui.ORANGE)
        y += 56
    return base, m


# ---------------------------------------------------------------- 开场快切（没有人声）
def cold_open(T):
    t1 = voice.PRE
    big = (402, 30, 1536, 864)
    aud(0.0, 2.0, "D", 472.7, "full")
    aud(2.0, t1, "D", 517.4, "full")
    T.add(Panel(0.0, 2.0, big, VideoSrc(CH["D"], 472.7, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=None, exit=None))
    T.add(Panel(2.0, t1 + 0.3, big, VideoSrc(CH["D"], 517.4, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=None, exit=("fade", 0.3)))
    # 片名：压在第二段快切上（封面式描边字）
    T.add(SpriteItem(2.35, t1 + 0.1, (445, 172), title_sprite(), z=6, enter=("slide", -60, 0, 0.35), exit=("fade", 0.2)))


# ---------------------------------------------------------------- S01 开场
def journey_card(active):
    """说明带（S01）：像素视频 → 游戏素材 → 银魂游戏，当前讲到哪一步亮哪一步。"""
    w, h = C_W, STRIP[3]
    base, m = ui.card(w, h)
    d = ImageDraw.Draw(base)
    steps = [("像素视频", "9 月 25 号 · 5 分半"), ("游戏素材", "15 场景 · 42 角色"), ("银魂游戏", "15 章 · 600 句台词")]
    colw = (w - 2 * 36) / 3
    for i, (a, b) in enumerate(steps):
        x0 = m + 36 + i * colw
        cur = i == active
        cx, cy = x0 + 36, m + h / 2
        d.ellipse((cx - 31, cy - 31, cx + 31, cy + 31), fill=ui.ORANGE if cur else (226, 229, 235), outline=ui.INK if cur else None, width=4)
        d.text((cx, cy + 1), str(i + 1), font=ui.sg(34), fill=ui.WHITE if cur else ui.GRAY2, anchor="mm")
        d.text((x0 + 86, cy - 18), a, font=ui.nsc(42 if cur else 38, 800 if cur else 600), fill=ui.INK if cur else ui.GRAY2, anchor="lm")
        d.text((x0 + 86, cy + 28), b, font=ui.nsc(24, 600), fill=ui.GRAY if cur else (176, 182, 191), anchor="lm")
        if i < 2:
            ax = x0 + colw - 20
            d.polygon([(ax - 8, cy - 18), (ax + 12, cy), (ax - 8, cy + 18)], fill=ui.INK if i < active else (200, 205, 214))
    return base, m


def s01(T, st):
    a, b = sec_range("S01")
    t_end = b + 0.3
    # ---- 左边下面那条：旅程条
    t_orig = ph("0190", "视频里长出来", dt=-0.6)
    t_cards = ph("0190", "拆了15个场景", dt=-0.5)
    t_c0 = ph("0190", "看到他素材", dt=-0.3)
    for i, (t0, t1) in enumerate([(a, t_cards), (t_cards, t_c0), (t_c0, t_end)]):
        card_item(T, t0 - 0.1 if i else a + 0.6, t1 + 0.1, (C_X, STRIP[1]), journey_card(i), z=6, enter=("slide", 0, 30, 0.35) if i == 0 else ("fade", 0.15), exit=("fade", 0.15))
    # ---- 原片 + 提示词卡
    r_orig = (R_X, TOP, R_W, 295)
    T.add(Panel(t_orig, t_cards + 0.2, r_orig, VideoSrc(ORIG, 0.0, dec=(R_W, 295), flags="area"), {}, z=4, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, r_orig, "原片 · 9 月 25 号", t_orig, t_cards)
    t_ultra = ph("0190", "Ultra", dt=-0.3)
    t_type0 = ph("0190", "像素风", dt=-0.2)
    t_type1 = ph("0190", "讲故事", dt=0.4)
    t_opus = ph("0190", "Opus", dt=-0.3)
    kf = lambda tl: int(clamp((tl - (t_type0 - t_ultra)) / max(0.1, (t_type1 - t_type0))) * len(PROMPT_Q))
    badges_at = lambda tl: 2 if tl >= (t_opus - t_ultra) else 1
    m_card = prompt_card(0)[1]
    dyn_item(T, t_ultra, t_cards + 0.2, (R_X - m_card, 380 - m_card), lambda tl: (kf(tl), badges_at(tl)), lambda k: prompt_card(k[0], k[1])[0], z=4)
    # ---- 数字卡：拆了 15 个场景…
    add_stat_cards(T, t_cards, [
        (ph("0190", "拆了15个场景", dt=-0.2), "15", "个场景", "原片拆出来的"),
        (ph("0190", "42个角色", dt=-0.2), "42", "个角色", "全是它自己画的"),
        (ph("0190", "动作", dt=-0.3), "31", "个动作", "每个角色一整套"),
        (ph("0190", "配乐", dt=-0.3), "12", "首配乐", "还有 80 多个音效"),
    ], t_c0)
    # ---- 视频 → 游戏
    t_g = ph("0190", "做成游戏", dt=-0.5)
    t_c1 = ph("0190", "15张的剧情", dt=-0.6)
    r_top = (R_X, TOP, R_W, 295)
    r_bot = (R_X, TOP + 295 + 92, R_W, 295)
    T.add(Panel(t_c0, t_c1 + 0.2, r_top, VideoSrc(ORIG, 1.0, dec=(R_W, 295), flags="area"), {}, z=4, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, r_top, "视频", t_c0, t_c1, size=32)
    arrow = ui.arrow_right(78, ui.ORANGE).rotate(-90, expand=True)
    T.add(SpriteItem(t_g - 0.1, t_c1 + 0.2, (R_X + R_W // 2 - 39, TOP + 295 + 7), arrow, z=5, enter=("slide", 0, -20, 0.3), exit=("fade", 0.25)))
    T.add(Panel(t_g, t_c1 + 0.2, r_bot, game_src("prologue", (R_W, 295), 2.0), {}, z=4, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, r_bot, "游戏", t_g, t_c1, size=32)
    # ---- 15 章 / 600+ / 1万+ / <20 小时
    add_stat_cards(T, t_c1, [
        (ph("0190", "15张的剧情", dt=-0.3), "15", "章", "剧情"),
        (ph("0190", "600多", dt=-0.3), "600+", "句", "台词"),
        (ph("0190", "1万多", dt=-0.3), "1万+", "行", "代码，都是 AI 写的"),
        (ph("0190", "20个小时", dt=-0.5), "<20", "小时", "从头写到最后一章"),
    ], t_end)


def add_stat_cards(T, t_start, specs, t_end):
    """右栏四张数字卡依次弹出（数字从 0 数上去）。specs = [(t, 数字, 单位, 说明)]。"""
    ch = 200
    gap = 20
    for i, (t, num, unit, cap) in enumerate(specs):
        y = TOP + i * (ch + gap)
        digits = "".join(c for c in num if c.isdigit())
        target = int(digits) if digits else 0
        pre, post = num[: num.index(digits[0])] if digits else "", num[num.rindex(digits[-1]) + 1:] if digits else num

        def key(tl, target=target):
            return count_up(tl, 0.9, target)

        def make(k, pre=pre, post=post, unit=unit, cap=cap):
            return ui.stat_card(R_W, ch, "%s%d%s" % (pre, k, post), unit, cap)[0]
        m = ui.stat_card(R_W, ch, "0", unit, cap)[1]
        dyn_item(T, t, t_end, (R_X - m, y - m), key, make, z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.25))


# ---------------------------------------------------------------- 通用：实机 + 说明带 + 目录
TOC_STATES: list = []
AUDIO: list = []          # 实机的声音：(t0, t1, 录像段, 起点秒, 模式)；模式 under = 垫在人声下面 / full = 只有游戏声


def aud(t0, t1, chunk, start, mode="under"):
    AUDIO.append((round(t0, 3), round(t1, 3), chunk, round(start, 3), mode))


def main_clip(T, shot, t0, t1, dt=0.0, enter=("fade", 0.2), exit=("fade", 0.2), z=1, rect=MAIN):
    ch, st = SHOTS[shot][:2]
    size = rect[2:]
    aud(t0, t1, ch, st + dt)
    return T.add(Panel(t0, t1, rect, VideoSrc(CH[ch], st + dt, dec=size, flags="neighbor" if size[0] % 384 == 0 else "lanczos"), {}, z=z, enter=enter, exit=exit))


def caption(T, shot, t0, t1, sub=""):
    kicker, title = SHOTS[shot][3], SHOTS[shot][4]
    card_item(T, t0, t1, (C_X, STRIP[1]), strip_caption(kicker, title, sub), z=6, enter=("fade", 0.15), exit=("fade", 0.15))


def toc_mark(t0, t1, now, dot):
    TOC_STATES.append((t0, t1, now, dot))


def keys_card(lit):
    """说明带：J / K / L 三个键帽，lit = 哪几个已经讲到（亮）。"""
    w, h = C_W, STRIP[3]
    base, m = ui.card(w, h)
    specs = [("J", "三连击", "下劈 · 上撩 · 突刺"), ("K", "跳", "空中再按 J = 跳斩"), ("L", "防御", "按住，挡正面")]
    kcs = []
    for (k, l, sub), on in zip(specs, lit):
        kc = ui.keycap(k, l, sub)
        if not on:
            kc = kc.copy()
            kc.putalpha(kc.getchannel("A").point(lambda v: int(v * 0.28)))
        kcs.append(kc)
    gap = 46
    tot = sum(k.width for k in kcs) + gap * 2
    x = m + (w - tot) // 2
    for kc in kcs:
        base.alpha_composite(kc, (x, m + (h - kc.height) // 2 + 2))
        x += kc.width + gap
    return base, m


def sticky(text, w, h, rot=2.0, size=64, fill=ui.MARKER):
    """黄色便利贴（毛笔字）。"""
    from PIL import ImageFont
    ss = 2
    im = Image.new("RGBA", ((w + 30) * ss, (h + 30) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16 * ss, 20 * ss, (w + 14) * ss, (h + 20) * ss), radius=10 * ss, fill=ui.INK)
    d.rounded_rectangle((6 * ss, 10 * ss, (w + 4) * ss, (h + 10) * ss), radius=10 * ss, fill=fill, outline=ui.INK, width=5 * ss)
    try:
        fb = ImageFont.truetype("C:/Windows/Fonts/STXINGKA.TTF", size * ss)
    except Exception:
        fb = ui.nsc(size * ss)
    lines = ui.wrap(text, fb, (w - 60) * ss)
    y = ((h - len(lines) * size * 1.35) / 2 + 10) * ss
    for ln in lines:
        d.text((34 * ss, y), ln, font=fb, fill=ui.INK)
        y += size * 1.35 * ss
    im = im.resize((w + 30, h + 30), Image.LANCZOS)
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)


def thumbs(T, items, t_in, t_out, rings, size=(464, 261), x=R_X + 30, y0=54, step=285):
    for i, (shot, lab) in enumerate(items):
        rect = (x, y0 + i * step, size[0], size[1])
        t0 = t_in + 0.22 * i
        T.add(Panel(t0, t_out, rect, game_src(shot, size), {"bw": 5, "sh": (7, 7)}, z=4, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25), ring=rings[i] if rings else None))
        label(T, rect, lab, t0, t_out, size=26, dx=-10, dy=-22, rot=-2 if i % 2 == 0 else 2)


# ---------------------------------------------------------------- S03 实机①
def s03(T, st):
    a, b = sec_range("S03")
    t_main = a - 0.35
    t_small = ph("0191", "小巧思", dt=-0.3)
    t_hair = ph("0191", "剪头发", dt=-0.5)
    t_sheep = ph("0191", "小绵羊", dt=-0.5)
    t_pach = ph("0191", "播清歌", dt=-0.5)
    t_skill = ph("0191", "没有加很多技能", dt=-0.3)
    t_atk = ph("0191", "普通的攻击", dt=-0.2)
    t_jump = ph("0191", "跳跃", dt=-0.2)
    t_story = ph("0191", "剧情上", dt=-0.6)
    t_web = ph("0193", "网页的代码文件", dt=-0.5)
    seq = [("prologue", t_main, t_hair), ("hair", t_hair, t_sheep), ("sheep", t_sheep, t_pach), ("pachinko", t_pach, t_skill), ("kondo", t_skill, t_story), ("street", t_story, t_web)]
    for shot, t0, t1 in seq:
        main_clip(T, shot, t0, t1, enter=("slide", 0, 40, 0.4) if shot == "prologue" else ("fade", 0.2))
        toc_mark(t0, t1, 0, SHOTS[shot][2])
        if shot == "kondo":
            continue
        caption(T, shot, t0, t1)
    # 说到攻击和跳跃：说明带换成键位
    for i, (t0, t1, lit) in enumerate([(t_skill, t_atk, (0, 0, 0)), (t_atk, t_jump, (1, 0, 0)), (t_jump, t_story, (1, 1, 0))]):
        card_item(T, t0 if i else t_skill, t1, (C_X, STRIP[1]), keys_card(lit), z=6, enter=("slide", 0, 30, 0.3) if i == 0 else ("fade", 0.12), exit=("fade", 0.12))
    # 右栏：他说一句，冒一条
    t_web2 = ph("0193", "网页的代码文件", dt=-0.5) - 0.1
    chips = [(t_skill, "没加很多技能", ui.ORANGE), (t_atk, "一个普通的攻击", ui.ORANGE), (t_jump, "跳跃", ui.ORANGE),
             (t_story, "剧情上的对话", ui.GREEN), (ph("0191", "环境", dt=-0.3), "环境的对话", ui.GREEN), (ph("0191", "NPC的对话", dt=-0.4), "NPC 的对话", ui.GREEN)]
    for i, (tc, txt, col) in enumerate(chips):
        card_item(T, tc, t_web2, (R_X, TOP + 8 + i * 104), list_chip(txt, col), z=5, enter=("slide", 40, 0, 0.3), exit=("fade", 0.2))
    # 三个小游戏的缩略图：亮着的是正在放的那个
    thumbs(T, [("hair", "给将军剪头发"), ("sheep", "骑小绵羊躲路障"), ("pachinko", "打柏青哥")], t_small, t_skill, [[(t_hair, t_sheep)], [(t_sheep, t_pach)], [(t_pach, t_skill)]])


def list_chip(text, color=ui.ORANGE, w=R_W, h=84):
    base, m = ui.card(w, h)
    d = ImageDraw.Draw(base)
    d.ellipse((m + 26, m + h / 2 - 11, m + 48, m + h / 2 + 11), fill=color)
    d.text((m + 70, m + h / 2 + 1), text, font=ui.nsc(36), fill=ui.INK, anchor="lm")
    return base, m


# ---------------------------------------------------------------- S03 后半：双击就能玩 / 横版剧情打斗
def s03b(T, st):
    a, b = sec_range("S03")
    t_web = ph("0193", "网页的代码文件", dt=-0.5)
    t_dbl = ph("0193", "双击", dt=-0.1)
    t_xhs = ph("0193", "小红书", dt=-0.7)
    t_dy = ph("0193", "抖音", dt=-0.5)
    t_all = ph("0193", "让大家", dt=-0.3)
    t_hv = ph("0193", "横版剧情", dt=-0.6)
    t_j = ph("0193", "三联机跳", dt=-0.3)
    t_l = ph("0193", "L防御", dt=-0.3)
    t_inter = ph("0193", "交互", dt=-0.5)
    t_wander = ph("0193", "随便逛", dt=-0.3)
    t_npc = ph("0193", "NPC聊天", dt=-0.3)
    t_cute = ph("0193", "小的巧思", dt=-0.3)
    t_hp = ph("0193", "雪条", dt=-0.4)
    t_low = ph("0193", "血条不够", dt=-0.4)
    t_end = sec_range("S04")[0] + 0.85          # 一直放到 S04 的图集板进来，中间不空
    # ---- E：文件夹窗口 → 标题画面
    t_open = t_dbl + 0.9
    T.add(Panel(t_web, t_open, MAIN, GenSrc(gens.explorer(1152, 648, t_arrive=(t_dbl - t_web) - 0.35, t_click=t_dbl - t_web), pixel=False), {}, z=1, enter=("slide", 0, 40, 0.4), exit=("fade", 0.2)))
    toc_mark(t_web, t_open, 0, None)
    card_item(T, t_web, t_hv - 0.1, (C_X, STRIP[1]), strip_caption("一个网页", "双击 index.html 就能玩", "不用装任何东西"), z=6, enter=("fade", 0.2), exit=("fade", 0.15))
    main_clip(T, "title", t_open - 0.15, t_hv, dt=0.0)
    toc_mark(t_open, t_hv, 0, None)
    # 便利贴：准备上架
    T.add(SpriteItem(t_xhs, t_hv, (R_X - 6, 80), sticky("准备上架：小红书的小程序", R_W - 10, 150, rot=-2, size=52), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    T.add(SpriteItem(t_dy, t_hv, (R_X - 6, 290), sticky("抖音的小程序 / 小工具", R_W - 10, 150, rot=2, size=52), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    T.add(SpriteItem(t_all, t_hv, (R_X - 6, 500), sticky("让大家都能玩", R_W - 10, 130, rot=-1.5, size=56, fill=(255, 150, 110)), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    # ---- D：横版剧情打斗（键位 → 交互 / 逛 / NPC / 巧思 → 血条）
    main_clip(T, "rain", t_hv, t_inter)
    toc_mark(t_hv, t_inter, 0, SHOTS["rain"][2])
    for i, (t0, t1, lit) in enumerate([(t_hv, t_j, (0, 0, 0)), (t_j, t_j + 0.7, (1, 0, 0)), (t_j + 0.7, t_l, (1, 1, 0)), (t_l, t_inter, (1, 1, 1))]):
        card_item(T, t0 if i else t_hv, t1, (C_X, STRIP[1]), keys_card(lit), z=6, enter=("slide", 0, 30, 0.3) if i == 0 else ("fade", 0.1), exit=("fade", 0.1))
    main_clip(T, "street", t_inter, t_hp, dt=7.0)
    toc_mark(t_inter, t_hp, 0, 1)
    card_item(T, t_inter, t_hp, (C_X, STRIP[1]), strip_caption(SHOTS["street"][3], SHOTS["street"][4], "走到哪儿都能聊"), z=6, enter=("fade", 0.2), exit=("fade", 0.15))
    main_clip(T, "prologue", t_hp, t_low, dt=3.0)
    toc_mark(t_hp, t_low, 0, 0)
    card_item(T, t_hp, t_end, (C_X, STRIP[1]), strip_caption("战斗", "有血条，输了从这一仗重来", "没有装备、没有技能树"), z=6, enter=("fade", 0.2), exit=("fade", 0.2))
    main_clip(T, "lose", t_low, t_end, dt=0.0)
    toc_mark(t_low, t_end, 0, 0)
    # 右栏：小标签依次弹出
    items = [(t_inter, "场景可以交互"), (t_wander, "可以随便逛"), (t_npc, "能跟 NPC 聊天"), (t_cute, "小剧情、小巧思")]
    for i, (t0, text) in enumerate(items):
        card_item(T, t0, t_hp + 0.1, (R_X, 40 + i * 100), list_chip(text), z=5, enter=("slide", 40, 0, 0.3), exit=("fade", 0.2))
    hp_rect = (R_X, 470, R_W, 100)
    T.add(Panel(t_hp, t_end, hp_rect, VideoSrc(CH["A"], 143.4 + 3.0, dec=(R_W, 100), flags="lanczos", crop=(0.0, 0.0, 0.66, 0.224)), {"bw": 5, "sh": (7, 7)}, z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    label(T, hp_rect, "血条", t_hp, t_end, size=28, dx=-10, dy=-24)
    card_item(T, t_low, t_end, (R_X, 640), list_chip("血条空了：从这一仗重来", ui.RED), z=5, enter=("slide", 0, 40, 0.3), exit=("fade", 0.25))


# ---------------------------------------------------------------- 宽板（C+R 并成 1700×859）
def board_rects(cols=2, rows=2, gap=24):
    x, y, w, h = WIDE
    cw, ch = (w - gap * (cols - 1)) // cols, (h - gap * (rows - 1)) // rows
    return [(x + c * (cw + gap), y + r * (ch + gap), cw, ch) for r in range(rows) for c in range(cols)]


def game_cover(shot, size, dt=0.0, vy=0.02):
    """实机铺满一块宽 / 扁的画板（上下裁掉一点）。"""
    ch, st = SHOTS[shot][:2]
    w, h = size
    frac = (384 / 216) / (w / h)                # 要保留的高度比例
    frac = min(1.0, frac)
    y0 = min(vy, 1 - frac)
    return VideoSrc(CH[ch], st + dt, dec=size, flags="lanczos", crop=(0.0, y0, 1.0, y0 + frac))


def num_sticker(T, rect, text, t0, t1, k=0, size=54, fill=ui.ORANGE, rot=3, top=False):
    s_ = ui.sticker(text, size, fill=fill, rot=rot)
    x, y, w, h = rect
    yy = (y + 16 + k * (s_.height + 6)) if top else (y + h - s_.height - 18 - k * (s_.height + 6))
    T.add(SpriteItem(t0, t1, (x + w - s_.width - 22, yy), s_, z=22, enter=("slide", 0, 24, 0.3), exit=("fade", 0.2)))


# ---------------------------------------------------------------- S04 素材四件套
def audio_lines():
    names = []
    for d in ("音乐_a", "音乐_b"):
        names += sorted(p.name for p in (MAT / "音频" / d).glob("*.wav") if not p.name.endswith("_x2.wav"))
    return ["music/"] + ["  " + n for n in names] + ["", "sfx/   88 files"]


def s04(T, st):
    a, b = sec_range("S04")
    t_in = a + 0.8
    t_atlas = a + 0.9
    t_act = ph("0193", "31个动作", dt=-1.0)
    t_bg = ph("0193", "背景也是代码", dt=-0.5)
    t_au = ph("0193", "12首", dt=-0.8)
    t_end = b + 0.3
    rs = board_rects()
    toc_mark(t_in - 0.2, t_end, 1, None)
    atlas = MAT / "角色图集" / "总览.png"
    T.add(Panel(t_atlas, t_end, rs[0], ImageSrc(atlas, "cover", 0.5, 0.5, kb=(1.0, 1.12, 14.0)), {}, z=3, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, rs[0], "角色图集：全是它自己画的", t_atlas, t_end)
    T.add(Panel(t_act, t_end, rs[1], GenSrc(gens.action_wall(rs[1][2], rs[1][3])), {}, z=3, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, rs[1], "银时的动作，同时在演", t_act, t_end)
    T.add(Panel(t_bg, t_end, rs[2], GenSrc(gens.parallax(rs[2][2], rs[2][3])), {}, z=3, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, rs[2], "背景：代码画的，一层一层", t_bg, t_end)
    al = audio_lines()
    T.add(Panel(t_au, t_end, rs[3], GenSrc(lambda t: gens.terminal_card(rs[3][2], rs[3][3], al, "音频清单", 22, scroll=t * 2.2)), {}, z=3, enter=("slide", 0, 40, 0.4), exit=("fade", 0.3)))
    label(T, rs[3], "8 位配乐和音效：代码合成", t_au, t_end)
    # 数字贴纸
    num_sticker(T, rs[0], "42 个角色", ph("0193", "42个角色", dt=-0.15), t_end)
    num_sticker(T, rs[1], "31 个动作", ph("0193", "31个动作", dt=-0.15), t_end, 0, 46, ui.ORANGE, 3)
    num_sticker(T, rs[1], "11 种表情", ph("0193", "11种表情", dt=-0.15), t_end, 1, 46, ui.MARKER, -3)
    num_sticker(T, rs[1], "13124 帧", ph("0193", "13124帧", dt=-0.15), t_end, 2, 46, ui.ORANGE, 2)
    num_sticker(T, rs[2], "没给任何参考图", ph("0193", "参考图片", dt=-0.4), t_end, 0, 44, ui.MARKER, -2)
    num_sticker(T, rs[3], "12 首配乐", ph("0193", "12首", dt=-0.15), t_end, 0, 46, ui.ORANGE, 3)
    num_sticker(T, rs[3], "80+ 音效", ph("0193", "80多个音效", dt=-0.15), t_end, 1, 46, ui.MARKER, -3)


# ---------------------------------------------------------------- S05 从原片到游戏
def shot_lines(md_name, limit=64):
    """场景分镜 md 里“镜头表”那一块代码围栏里的内容（逐行，截到 limit 个字符）。"""
    md = (MAT / "剧情分镜" / "场景分镜" / md_name).read_text(encoding="utf-8")
    i0 = md.index("## 镜头表")
    j0 = md.index("```", i0)
    j0 = md.index(chr(10), j0) + 1
    j1 = md.index("```", j0)
    return [l.rstrip()[:limit] for l in md[j0:j1].splitlines() if l.strip()]


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
    t_15 = ph("0193", "15个大的", dt=-0.4)
    t_table = ph("0193", "镜头表", dt=-0.4)
    t_orig = t_table - 0.9
    t_story = t_table - 0.6
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
    # --- 开头：原片（5 分半的像素视频）→ 15 个场景 = 15 章
    fade0 = ("fade", 0.22)
    t_in = a + 0.1
    T.add(Panel(t_in, t_15 - 0.2, MAIN, VideoSrc(ORIG, 21.0, dec=(1152, 648), flags="area"), {}, z=3, enter=("slide", 0, 40, 0.4), exit=fade0))
    label(T, MAIN, "原片：那条 5 分半的像素视频", t_in, t_15 - 0.2, size=32)
    toc_mark(a - 0.2, t_15 - 0.2, 1, None)
    SBD = MAT / "剧情分镜" / "分镜图"
    names = ["开场", "万事屋阿银", "新八登场", "神乐与定春", "真选组", "桂与伊丽莎白", "日常", "红樱篇", "真选组动乱篇", "吉原炎上篇", "将军暗杀篇", "松阳老师", "洛阳决战·离别", "银之魂篇", "尾声"]
    files = sorted(SBD.glob("s[0-9][0-9]_*.png"))[:15]
    gx0, gy0, gw0, gh0 = WIDE
    cw0, ch0 = (gw0 - 4 * 18) // 5, (gh0 - 2 * 18) // 3
    for k, f in enumerate(files):
        rect = (gx0 + (k % 5) * (cw0 + 18), gy0 + (k // 5) * (ch0 + 18), cw0, ch0)
        ta = t_15 - 0.2 + 0.07 * k
        T.add(Panel(ta, t_orig - 0.1, rect, ImageSrc(f, "cover", 0.5, 0.25), {"bw": 5, "sh": (6, 6)}, z=3, enter=("slide", 0, 30, 0.3), exit=fade0))
        label(T, rect, ("序章" if k == 0 else ("终章" if k == 14 else "第%d章" % k)) + " " + names[k], ta, t_orig - 0.1, size=22, dx=-8, dy=-20, rot=-2 if k % 2 == 0 else 2)
    num_sticker(T, WIDE, "15 个场景 = 15 章", t_15 + 0.2, t_orig - 0.1, 0, 60, ui.ORANGE, -2, top=False)
    toc_mark(t_15 - 0.2, t_orig - 0.1, 1, None)
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
    toc_mark(t_orig - 0.1, t_wall - 0.15, 1, 2)
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


# ---------------------------------------------------------------- S06 第一章：解谜
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
    T.add(SpriteItem(t_note, t_tang + 0.2, (R_X - 6, 500), sticky("重要的钱，藏在你最重视的东西后面", R_W - 10, 262, rot=2.0, size=52), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    T.add(SpriteItem(t_tang + 0.1, t_end, (R_X - 6, 120), sticky("最重视的东西，是——糖分！", R_W - 10, 170, rot=-2.0, size=56), z=5, enter=("slide", 0, 40, 0.35), exit=("fade", 0.25)))
    card_item(T, t_5000, t_end, (R_X, 360), ui.stat_card(R_W, 200, "5000", "日元", "字画后面的信封"), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.25))
    card_item(T, t_short, t_end, (R_X, 590), list_chip("还不够三个月的房租", ui.RED), z=5, enter=("slide", 0, 36, 0.3), exit=("fade", 0.25))
    # ---- 只有游戏原声的一段：实机放大居中（眼睛特写 → 一拳打穿墙）
    g0, g1 = t_end - 0.1, sec_range("S08")[0] - 0.2
    big = (402, 30, 1536, 864)
    t_mid = g0 + 3.4
    aud(g0, t_mid, "A", 515.9, "full")
    aud(t_mid, g1, "A", 553.0, "full")
    T.add(Panel(g0, t_mid, big, VideoSrc(CH["A"], 515.9, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=("fade", 0.3), exit=("fade", 0.2)))
    label(T, big, "第二章 · 眼睛特写，原片里就有", g0, t_mid, size=34, dy=-24, corner="tr", dx=-10)
    T.add(Panel(t_mid, g1, big, VideoSrc(CH["A"], 553.0, dec=(1536, 864), flags="neighbor"), {}, z=1, enter=("fade", 0.2), exit=("fade", 0.3)))
    label(T, big, "下一秒：一拳打穿墙", t_mid, g1, size=34, dy=-24, corner="tr", dx=-10)


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
    num_sticker(T, MAIN, "将近 5 分钟的打斗", t_five, t_end_ch, 0, 50, ui.ORANGE, 2, top=True)
    num_sticker(T, MAIN, "银魂永不完结", ph("0194", "永不完结", dt=-0.3), t_end, 0, 50, ui.MARKER, -2, top=True)


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
    toc_mark(sec_range("S10")[0] - 0.3, t_j, 2, None)
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
    t_now = ph("0194", "现在只需要", dt=-0.3) if voice.find_phrase("0194", "现在只需要") else t_want - 1.4
    T.add(SpriteItem(t_j + 0.1, t_now, (rx - 6, y + 160), sticky("做游戏的门槛，还剩什么？", rw - 10, 300, rot=-2.0, size=76), z=5, enter=("slide", 0, 40, 0.4), exit=fade))
    m_r = ui.card(rw, 803)[1]
    dyn_item(T, t_now, t_k, (rx - m_r, y + 56 - m_r), lambda tl: 0 if tl + t_now < t_want else (1 if tl + t_now < t_say2 else 2), lambda k: right_card(k), z=5, enter=("slide", 0, 40, 0.35), exit=fade)
    gw = rw - 72
    grect = (rx + 36, y + 56 + 330, gw, int(gw * 9 / 16))
    T.add(Panel(t_make, t_k, grect, VideoSrc(CH["D"], 475.0, dec=(gw, int(gw * 9 / 16)), flags="lanczos"), {"bw": 5, "sh": (7, 7)}, z=6, enter=("slide", 0, 40, 0.4), exit=fade))
    T.add(SpriteItem(t_make + 0.2, t_k, (rx + rw - 110, y + 56 + 18), ui.check_mark(66), z=7, enter=("slide", 0, -20, 0.25), exit=fade))
    T.add(SpriteItem(t_pick, t_k, (rx + rw - 340, y + 56 + 250), ui.sticker("审美：你来挑", 40, fill=ui.MARKER, rot=3), z=8, enter=("slide", 0, 20, 0.3), exit=fade))
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
    # 先压一张大便利贴：“不仅仅是游戏”（第一张输入卡进来之前，右边不空着）
    T.add(SpriteItem(t_k, srcs[0][1] + 0.1, (x + 40, y + 190), sticky("不仅仅是游戏", 760, 190, rot=-2.0, size=92), z=5, enter=("slide", 0, 40, 0.4), exit=fade))
    for i, (txt, ta) in enumerate(srcs):
        base, m = ui.card(520, 112)
        d = ImageDraw.Draw(base)
        d.text((m + 40, m + 56), txt, font=ui.nsc(50), fill=ui.INK, anchor="lm")
        T.add(SpriteItem(ta, t_end, (x - m, y + 40 + i * 134 - m), base, z=5, enter=("slide", -40, 0, 0.35), exit=fade))
    T.add(SpriteItem(t_k, t_end, (x + 6, y - 14), ui.sticker("它们都可以……", 36, rot=-2), z=8, enter=("slide", 0, 20, 0.3), exit=fade))
    arrow = ui.arrow_right(96, ui.ORANGE)
    T.add(SpriteItem(srcs[0][1] + 0.2, t_end, (x + 548, y + 40 + 300), arrow, z=5, enter=("slide", -30, 0, 0.3), exit=fade))
    gx, gy = x + 700, y + 20
    gw2, gh2 = 484, 272
    # 四个真实成品：跟着输入一个个进来（文章 → 视频；视频 → 游戏；课 → 10 集；长文 → 短视频）
    outs = [("ui_cover.png", "一篇文章 → 一条视频", srcs[0][1] + 0.1, (0.5, 0.5), [(t_video, t_game)]),
            ("game_title.png", "一条视频 → 一个游戏", srcs[1][1] + 0.1, (0.5, 0.5), [(t_game, t_fast)]),
            ("courses_wall.png", "一门课 → 10 集", srcs[2][1] + 0.1, (0.5, 0.5), [(t_video, t_game)]),
            ("rl_frame.png", "一篇长文 → 一分钟短视频", srcs[3][1] + 0.1, (0.5, 0.45), [(t_video, t_game)])]
    for k, (fn, lab, ta, (cx, cy), ring) in enumerate(outs):
        rect = (gx + (k % 2) * (gw2 + 24), gy + (k // 2) * (gh2 + 40), gw2, gh2)
        T.add(Panel(ta, t_end, rect, ImageSrc(HERE / "mat" / fn, "cover", cx, cy, pixel=(fn == "game_title.png")), {}, z=4, enter=("slide", 0, 40, 0.4), exit=fade, ring=ring))
        label(T, rect, lab, ta, t_end, size=28, dx=-10, dy=-22)
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
    T.add(SpriteItem(t_wel, t_end, (C_X + 6, 742), title_line_sprite(72), z=6, enter=("slide", -40, 0, 0.35), exit=None))
    logo = Image.open(HERE / "mat" / "logo.png").convert("RGBA")
    logo = logo.resize((logo.width * 5 // 2, logo.height * 5 // 2), Image.NEAREST)
    T.add(SpriteItem(t_wel + 0.2, t_end, (R_X + (R_W - logo.width) // 2, 300), logo, z=6, enter=("slide", 0, 40, 0.45), exit=None))
    toc_mark(a - 0.5, t_end, 2, None)


# ---------------------------------------------------------------- build
def build():
    T = Timeline(HERE / "bg.png")
    TOC_STATES.clear()
    AUDIO.clear()                  # 要在 cold_open 之前清（开场快切的声音也登记在 AUDIO 里）
    cold_open(T)
    st = add_face(T)
    toc_mark(voice.PRE, sec_range("S03")[0] - 0.4, None, None)
    s01(T, st)
    s03(T, st)
    s03b(T, st)
    s04(T, st)
    s05(T, st)
    s06(T, st)
    s08(T, st)
    s10(T, st)
    s11(T, st)
    add_toc(T, st, TOC_STATES)
    return T
