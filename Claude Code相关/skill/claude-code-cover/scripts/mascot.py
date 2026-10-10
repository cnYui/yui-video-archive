# -*- coding: utf-8 -*-
"""Claude 像素宇航员：官方 40×33 像素表（assets/sprite_official.dat，fetch_sprite.py 取的）+ 我们自己画的动作和道具。

  python mascot.py gallery [--scheme night] [--out gallery.png]     把所有动作画成一张总览图
  python mascot.py list                                             列出动作名

用户 2026-10-02：“当前 claude 这个像素形象，你可以自己画不同的动作，自由发挥即可”。所以这里有两类动作：
  官方帧  float / float2 / float3 / stand：直接用官方动画里的帧（漂浮摇摆、拖着腿、冒小星光 / 站直戴头盔）
  自画    wave cheer gear terminal megaphone flag shield plug gift point think bolt：在 stand 的格子上改手臂、腿、眼睛，再加道具（手画的像素，同一套调色板）
          —— 想要新动作就在 POSES 里加一个函数：用 cv.rect / cv.stamp 在官方的 40×33 格子（身体在 cols 9–32、rows 10–32）上画，
          道具模板在 PROPS 里（P/S 是随背景方案换色的“主色 / 副色”，0/1/2 = 深色 / 深橙 / 品牌橙 固定，I = 米白，Y = 淡黄）。
格子坐标（官方 40×33）：头 = rows 17–20、cols 13–28（眼睛是 2×2 深色格，在 cols 15–16 和 25–26、rows 19–20）；躯干 = rows 21–28；
  手臂 = rows 21–24、cols 9–12 和 29–32（站姿时是两个小方块）；腿 = rows 29–32 的四条（cols 13–14、17–18、23–24、27–28）；
  头盔 = 一圈 1 格宽的浅灰环（rows 10–23、cols 10–31）+ 领口一条线（row 23）+ 右上角白色高光。
渲染：每格放大成 cell×cell 像素（整数倍、最近邻，不糊），可选 1 格宽的深色描边（橙色底上用）。
"""
import argparse
import json
from collections import namedtuple
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ANCHOR = (21, 25)             # 身体中心（cols 13–28 的正中、rows 17–32 的正中），封面上摆放宇航员时对准的点
FLOAT_FRAMES = {"float": 40, "float2": 47, "float3": 54}      # 官方动画里漂浮的几帧（累积补丁后的下标）
STAND_FRAME = 12                                                # 官方动画里站直戴头盔的一帧

# ---- 配色：官方调色板 + 四种背景方案（品牌色：橙 #D97757、米白 #FAF9F5、淡黄 #F5DB9A、深色 #141413） ----
BRAND = {"orange": "#D97757", "orange_deep": "#BF684C", "orange_accent": "#C15F3C", "ivory": "#FAF9F5", "oat": "#E3DACC",
         "yellow": "#F5DB9A", "dark": "#141413", "ring": "#D1CFC4"}
# 0 深色 1 深橙 2 品牌橙 3 头盔环 4 小星光 5 高光 | I 米白 Y 淡黄 | P S 随方案换色 | Z 装饰小星光（同 4）
SCHEMES = {
    "night": dict(bg="#141413", t1="#FAF9F5", t2="#D97757", glow=True, outline=None,
                  c={"0": "#141413", "1": "#BF684C", "2": "#D97757", "3": "#D1CFC4", "4": "#F5DB9A", "5": "#FAF9F4", "I": "#FAF9F5", "Y": "#F5DB9A", "P": "#FAF9F5", "S": "#F5DB9A", "Z": "#F5DB9A"},
                  deco=["#2A2927", "#3A3936", "#5E5D59", "#87867F"], deco_spark="#F5DB9A"),
    "ivory": dict(bg="#FAF9F5", t1="#141413", t2="#C15F3C", glow=False, outline=None,
                  c={"0": "#141413", "1": "#BF684C", "2": "#D97757", "3": "#141413", "4": "#D97757", "5": "#FAF9F5", "I": "#FAF9F5", "Y": "#F5DB9A", "P": "#141413", "S": "#D97757", "Z": "#D97757"},
                  deco=["#EFEDE5", "#E3DACC", "#D1CFC4", "#F5DB9A"], deco_spark="#D97757"),
    "orange": dict(bg="#D97757", t1="#FAF9F5", t2="#141413", glow=False, outline="#141413",
                   c={"0": "#141413", "1": "#BF684C", "2": "#D97757", "3": "#FAF9F5", "4": "#F5DB9A", "5": "#FAF9F5", "I": "#FAF9F5", "Y": "#F5DB9A", "P": "#FAF9F5", "S": "#F5DB9A", "Z": "#F5DB9A"},
                   deco=["#DE8567", "#E39478", "#BF684C", "#F5DB9A"], deco_spark="#F5DB9A"),       # 星光不用米白：和字色撞了，验收会把它数成“字色像素”
    "yellow": dict(bg="#F5DB9A", t1="#141413", t2="#C15F3C", glow=False, outline=None,
                   c={"0": "#141413", "1": "#BF684C", "2": "#D97757", "3": "#141413", "4": "#D97757", "5": "#FAF9F5", "I": "#FAF9F5", "Y": "#F5DB9A", "P": "#141413", "S": "#D97757", "Z": "#D97757"},
                   deco=["#F1D08A", "#EBC878", "#FAF9F5", "#E3DACC"], deco_spark="#D97757"),
}
DECO_CHARS = "4Z"             # 不算在宇航员外框里的装饰小星光


# ---- 官方数据 ----
def load_official():
    p = ASSETS / "sprite_official.dat"
    if not p.exists():
        raise SystemExit("缺 assets/sprite_official.dat：先跑 scripts/fetch_sprite.py")
    d = json.loads(p.read_text(encoding="utf-8"))
    W, H, cur, frames = d["w"], d["h"], d["base"], []
    for t in d["deltas"]:
        g = list(cur)
        for tok in [x for x in t.split(",") if x]:
            g[int(tok[:-1], 36)] = tok[-1]
        cur = "".join(g)
        frames.append(cur)
    return W, H, d["base"], frames


class Canvas:
    """稀疏格子：{(x, y): 字符}，坐标是官方 40×33 的格子（可以是负数或超出，渲染时按外框裁）。"""

    def __init__(self, cells=None):
        self.c = dict(cells or {})

    def set(self, x, y, ch):
        if ch == ".":
            self.c.pop((x, y), None)
        else:
            self.c[(x, y)] = ch

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, ch)

    def erase(self, cells):
        for xy in cells:
            self.c.pop(xy, None)

    def stamp(self, rows, x0, y0, mapping=None):
        """贴一块字符画（'.' 和空格 = 透明）。"""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch not in ". ":
                    self.set(x0 + dx, y0 + dy, (mapping or {}).get(ch, ch))

    def cells(self, exclude=""):
        return [xy for xy, ch in self.c.items() if ch not in exclude]

    def bbox(self, exclude=DECO_CHARS):
        xs = [x for (x, y), ch in self.c.items() if ch not in exclude]
        ys = [y for (x, y), ch in self.c.items() if ch not in exclude]
        return min(xs), min(ys), max(xs), max(ys)

    def flipped(self, axis=ANCHOR[0]):
        return Canvas({(2 * axis - x, y): ch for (x, y), ch in self.c.items()})


def official_canvas(k):
    W, H, base, frames = load_official()
    g = frames[k]
    return Canvas({(i % W, i // W): ch for i, ch in enumerate(g) if ch != "."})


# ---- 身体各部分的格子 ----
LEFT_ARM = [(9, 21), (10, 21), (9, 22), (10, 22), (11, 22), (9, 23), (10, 23), (11, 23), (12, 23), (9, 24), (10, 24), (11, 24), (12, 24)]
RIGHT_ARM = [(31, 21), (32, 21), (30, 22), (31, 22), (32, 22), (29, 23), (30, 23), (31, 23), (32, 23), (29, 24), (30, 24), (31, 24), (32, 24)]
LEGS = [(x, y) for x0 in (13, 17, 23, 27) for x in (x0, x0 + 1) for y in range(29, 33)]
EYES_L, EYES_R = [(15, 19), (16, 19), (15, 20), (16, 20)], [(25, 19), (26, 19), (25, 20), (26, 20)]


def stand():
    return official_canvas(STAND_FRAME)


def mirror_x(x):
    return 2 * ANCHOR[0] - x


def arm_up(cv, side="R", hand_h=2):
    """举手：肩上一条横杆 + 竖直的小臂 + 一个 4 宽的手（在头盔环外面）。side = R 右手 / L 左手。"""
    cv.erase(RIGHT_ARM if side == "R" else LEFT_ARM)
    s = (lambda x: x) if side == "R" else mirror_x
    for (x0, y0, x1, y1) in [(29, 23, 35, 24), (34, 12, 35, 22), (33, 10, 36, 10 + hand_h - 1)]:
        a, b = sorted((s(x0), s(x1)))
        cv.rect(a, y0, b, y1, "2")


def arm_out(cv, side="R", length=7, row=23):
    """手臂平伸：肩上一条 2 格高的横杆，尽头一个 3×4 的手。"""
    cv.erase(RIGHT_ARM if side == "R" else LEFT_ARM)
    s = (lambda x: x) if side == "R" else mirror_x
    xe = 28 + length
    a, b = sorted((s(29), s(xe)))
    cv.rect(a, row, b, row + 1, "2")
    a, b = sorted((s(xe - 1), s(xe + 1)))
    cv.rect(a, row - 1, b, row + 2, "2")


def eyes(cv, style="open"):
    if style == "happy":                      # 笑眯眯：上面一排变成身体色，只剩下面一排深色
        for xy in (15, 16, 25, 26):
            cv.set(xy, 19, "2")
    elif style == "wink":
        for x in (25, 26):
            cv.set(x, 19, "2")


def legs_jump(cv):
    cv.erase(LEGS)
    for x in (13, 14):
        cv.set(x - 1, 29, "2"), cv.set(x, 29, "2"), cv.set(x - 3, 30, "2"), cv.set(x - 2, 30, "2"), cv.set(x - 3, 31, "2"), cv.set(x - 2, 31, "2")
    cv.rect(17, 29, 18, 31, "2")
    cv.rect(23, 29, 24, 31, "2")
    for x in (27, 28):
        cv.set(x + 1, 29, "2"), cv.set(x, 29, "2"), cv.set(x + 3, 30, "2"), cv.set(x + 2, 30, "2"), cv.set(x + 3, 31, "2"), cv.set(x + 2, 31, "2")


# ---- 道具（字符画；P / S 随背景方案换色，0 深 1 深橙 2 橙 I 米白 Y 淡黄 Z 装饰小星光） ----
GEAR = ["....PPP....", ".P..PPP..P.", ".PPPPPPPPP.", "..PP...PP..", "PPP.....PPP", "PPP.....PPP", "PPP.....PPP", "..PP...PP..", ".PPPPPPPPP.", ".P..PPP..P.", "....PPP...."]
PLUG = ["..S...S..", "..S...S..", "..S...S..", ".SSSSSSS.", ".SSSSSSS.", ".SSSSSSS.", ".SSSSSSS.", "..SSSSS..", "...SSS...", "....S....", "....S....", "....S...."]
MEGAPHONE = ["..........SS..", "........SSSSS.", "......SSSSSSS.", "PPPPSSSSSSSSS.", "PPPPSSSSSSSSS.", "PPPPSSSSSSSSS.", "PPPPSSSSSSSSS.", "......SSSSSSS.", "........SSSSS.", "..........SS.."]
SOUND = ["......S", "..S...S", "..S.S.S", "..S.S.S", "..S.S.S", "..S.S.S", "..S...S", "......S"]
SHIELD = ["PPPPPPPPPPP", "PSSSSSSSSSP", "PSSSSSSS0SP", "PSSSSSS00SP", "PS0SSS00SSP", "PS00S00SSSP", "PSS000SSSSP", "PSSS0SSSSSP", ".PSSSSSSSP.", "..PSSSSSP..", "...PSSSP...", "....PSP....", ".....P....."]
GIFT = ["...PP..PP...", "..PPPPPPPP..", "...PPPPPP...", "SSSSSPPSSSSS", "SSSSSPPSSSSS", ".SSSSPPSSSS.", ".SSSSPPSSSS.", ".SSSSPPSSSS.", ".SSSSPPSSSS.", ".SSSSPPSSSS."]
BOLT = ["....SSSS", "...SSSS.", "..SSSS..", ".SSSSSSS", "...SSS..", "..SSS...", ".SSS....", "SS......"]
ARROW_UP = ["...S...", "..SSS..", ".SSSSS.", "SSSSSSS", "..SSS..", "..SSS..", "..SSS..", "..SSS.."]
QUESTION = [".SSS.", "S...S", "....S", "...S.", "..S..", ".....", "..S.."]
SPARK = [".Z.", "Z.Z", ".Z."]
FLAG = ["SSSSSSSSSS", "SSSSSSSSSS", "SSSSISSSSS", "SSSIIISSSS", "SSSSISSSSS", "SSSSSSSSSS", "SSSSSSSSSS"]


def terminal_panel():
    """Claude Code 终端小窗：18×12，深色屏幕 + 标题栏三个小点 + 橙色 > 提示符和光标。"""
    cv = Canvas()
    cv.rect(0, 0, 17, 11, "P")
    cv.rect(1, 1, 16, 10, "0")
    cv.rect(1, 2, 16, 2, "P")
    for x, ch in ((2, "I"), (4, "Y"), (6, "2")):
        cv.set(x, 1, ch)
    for (dx, dy) in ((0, 0), (1, 1), (2, 2), (1, 3), (0, 4)):
        cv.set(3 + dx, 4 + dy, "2")
    cv.rect(7, 8, 9, 8, "I")
    return cv


def put(cv, rows, x, y):
    cv.stamp(rows, x, y)


# ---- 动作 ----
def pose_stand():
    return stand()


def pose_float(k):
    return lambda: official_canvas(FLOAT_FRAMES[k])


def pose_wave():
    cv = stand()
    arm_up(cv, "R")
    for xy in ((38, 9), (39, 11), (38, 13)):
        cv.set(*xy, "S")
    return cv


def pose_cheer():
    cv = stand()
    arm_up(cv, "R"), arm_up(cv, "L")
    legs_jump(cv)
    eyes(cv, "happy")
    put(cv, SPARK, 3, 3), put(cv, SPARK, 38, 4), put(cv, SPARK, 1, 17), put(cv, SPARK, 41, 18)
    return cv


def pose_gear():
    cv = stand()
    arm_up(cv, "R", hand_h=2)
    put(cv, GEAR, 31, -2)
    return cv


def pose_terminal():
    cv = stand()
    cv.erase(LEGS)
    panel = terminal_panel()
    for (x, y), ch in panel.c.items():
        cv.set(12 + x, 22 + y, ch)
    cv.rect(9, 21, 11, 24, "2"), cv.rect(30, 21, 32, 24, "2")          # 手握在小窗两边
    return cv


def pose_megaphone():
    cv = stand()
    arm_out(cv, "R", length=6, row=23)
    put(cv, MEGAPHONE, 36, 19)
    put(cv, SOUND, 51, 20)
    return cv


def pose_flag():
    cv = stand()
    arm_out(cv, "R", length=8, row=23)
    cv.rect(37, 2, 37, 31, "P")
    put(cv, FLAG, 38, 2)
    return cv


def pose_shield():
    cv = stand()
    cv.erase(LEFT_ARM)
    put(cv, SHIELD, 0, 18)
    cv.rect(11, 22, 13, 24, "2")
    return cv


def pose_plug():
    cv = stand()
    arm_up(cv, "R", hand_h=2)
    put(cv, PLUG, 31, -3)
    return cv


def pose_gift():
    cv = stand()
    arm_out(cv, "R", length=6, row=23)
    put(cv, GIFT, 35, 17)
    return cv


def pose_point():
    cv = stand()
    arm_out(cv, "L", length=9, row=23)
    for dy, row in enumerate(["..S", ".SS", "SSS", ".SS", "..S"]):
        cv.stamp([row], 0, 21 + dy)
    return cv


def pose_think():
    cv = stand()
    cv.erase(RIGHT_ARM)
    cv.rect(29, 23, 33, 24, "2"), cv.rect(32, 19, 33, 22, "2"), cv.rect(30, 18, 33, 18, "2")
    put(cv, QUESTION, 33, 3)
    return cv


def pose_bolt():
    cv = stand()
    arm_up(cv, "R", hand_h=2)
    put(cv, BOLT, 32, -1)
    for xy in ((42, 9), (43, 12)):
        cv.set(*xy, "S")
    return cv


POSES = {"stand": pose_stand, "float": pose_float("float"), "float2": pose_float("float2"), "float3": pose_float("float3"),
         "wave": pose_wave, "cheer": pose_cheer, "gear": pose_gear, "terminal": pose_terminal, "megaphone": pose_megaphone, "flag": pose_flag,
         "shield": pose_shield, "plug": pose_plug, "gift": pose_gift, "point": pose_point, "think": pose_think, "bolt": pose_bolt}
# 动作适合的内容（选动作时看）
POSE_USE = {"float": "默认：一般公告 / 更新速递（漂浮，拖着腿）", "float2": "漂浮，周围有小星光（新东西 / 发布）", "float3": "漂浮，眯着眼笑（轻松的更新）", "stand": "中性站姿", "wave": "打招呼 / 新功能上线", "cheer": "重大发布 / 庆祝", "gear": "设置 / 配置 / 模组（改成自己喜欢的样子）",
            "terminal": "Claude Code 命令行 / 教程", "megaphone": "公告 / 新闻", "flag": "新版本 / 里程碑", "shield": "安全 / 权限 / 沙盒", "plug": "插件 / 技能 / 模组（拿着插头）",
            "gift": "新功能礼包 / 福利", "point": "指向左边的标题字（宇航员在右边时用）", "think": "为什么 / 原理解释", "bolt": "提速 / 性能 / 新模型"}


def build(pose, flip=False, eyes_style=None):
    if pose not in POSES:
        raise SystemExit(f"没有这个动作 {pose}；可选：{', '.join(POSES)}")
    cv = POSES[pose]()
    if eyes_style:
        eyes(cv, eyes_style)
    return cv.flipped() if flip else cv


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


Sprite = namedtuple("Sprite", "im anchor bbox origin cell")


def render(cv, cell, scheme="night", outline=None):
    """渲染成 RGBA（每格 cell×cell 像素，最近邻）。返回 Sprite(图, 锚点在图里的像素位置, 外框 [x0,y0,x1,y1]（不含装饰小星光）, 图左上角的格子坐标, cell)。"""
    sc = SCHEMES[scheme]
    col = {k: hex2rgb(v) for k, v in sc["c"].items()}
    xs = [x for x, _ in cv.c]
    ys = [y for _, y in cv.c]
    pad = 1
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    w, h = x1 - x0 + 1, y1 - y0 + 1
    arr = np.zeros((h, w, 4), np.uint8)
    for (x, y), ch in cv.c.items():
        arr[y - y0, x - x0] = (*col[ch], 255)
    oc = outline or sc.get("outline")
    if oc:
        a = arr[..., 3] > 0
        n = np.zeros_like(a)
        n[1:] |= a[:-1]; n[:-1] |= a[1:]; n[:, 1:] |= a[:, :-1]; n[:, :-1] |= a[:, 1:]
        edge = n & ~a
        arr[edge] = (*hex2rgb(oc), 255)
    im = Image.fromarray(arr, "RGBA").resize((w * cell, h * cell), Image.NEAREST)
    bx0, by0, bx1, by1 = cv.bbox()
    return Sprite(im, ((ANCHOR[0] - x0) * cell, (ANCHOR[1] - y0) * cell), [(bx0 - x0) * cell, (by0 - y0) * cell, (bx1 + 1 - x0) * cell, (by1 + 1 - y0) * cell], (x0, y0), cell)


def gallery(scheme, out, cell=12):
    names = list(POSES)
    tiles = []
    for n in names:
        im = render(build(n), cell, scheme).im
        tiles.append((n, im))
    tw = max(t[1].width for t in tiles) + 16
    th = max(t[1].height for t in tiles) + 34
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sc = SCHEMES[scheme]
    sheet = Image.new("RGB", (cols * tw, rows * th), hex2rgb(sc["bg"]))
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im, (x + 8, y + 26), im)
        d.text((x + 8, y + 6), n, fill=hex2rgb(sc["t1"]))
    sheet.save(out)
    print("->", out, sheet.size)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["gallery", "list"])
    ap.add_argument("--scheme", default="night", choices=list(SCHEMES))
    ap.add_argument("--out", default="gallery.png")
    ap.add_argument("--cell", type=int, default=12)
    a = ap.parse_args()
    if a.cmd == "list":
        for k in POSES:
            print(f"{k:10s} {POSE_USE.get(k, '')}")
    else:
        gallery(a.scheme, a.out, a.cell)
