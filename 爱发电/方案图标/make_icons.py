# -*- coding: utf-8 -*-
"""爱发电三档赞助方案的像素图标：引路人 / 同行者 / 共创者。

40×40 的像素网格手写精灵，最近邻放大 24 倍成 960×960 PNG。
三张是一条线：夜里一盏提灯（引路）→ 黎明两个人提着灯并肩走（同行）→
白天两个人牵手、头顶一颗一起造出来的星星（共创）。框是铜 / 银 / 金，
底下牌子上 1 / 2 / 3 颗星。蓝头发 = 悠一，棕头发 = 赞助者。

用法：python make_icons.py      （输出写到本目录）
"""
from math import atan2, hypot, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

N = 40          # 网格边长
SCALE = 24      # 放大倍数 → 960 px
OUT = Path(__file__).resolve().parent


def rgba(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def mix(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3])) + (255,)


# 精灵调色板：一个字母一种颜色
PAL = {k: rgba(v) for k, v in {
    'K': '#2a1a12',                                                       # 轮廓
    'S': '#ffd9b8', 's': '#f0b48c', 'P': '#ff9a8a', 'E': '#2a1a12', 'M': '#d0605a',  # 皮肤 / 腮红 / 眼 / 嘴
    'A': '#4b5f96', 'a': '#8197d4', 'Z': '#34446e',                       # 蓝头发（悠一）
    'W': '#f4efe6', 'w': '#d3c9b9', 'N': '#2f3550',                       # 米白上衣 / 深蓝下装
    'B': '#8b5a3c', 'b': '#c08559', 'X': '#5e3b26',                       # 棕头发（赞助者）
    'R': '#e2614a', 'r': '#b8453a',                                       # 橙红外套
    'G': '#a8763e', 'g': '#d09a5a',                                       # 背包
    'L': '#7a4a22', 'l': '#b5733a', 'c': '#e3a565',                       # 灯的铜件
    'Y': '#ffd23f', 'y': '#ffeb99', 'O': '#ff8c2b', 'F': '#fff8e0',       # 灯罩 / 火苗
}.items()}

# ---------------- 精灵 ----------------
LANTERN_BIG = [  # 16×20 提灯（火苗上尖下圆）
    "......KKKK......",
    ".....KllllK.....",
    ".....KlKKlK.....",
    "...KKKKKKKKKK...",
    "..KcclllllllLK..",
    ".KLLLLLLLLLLLLK.",
    ".KcYYYYYYYYYYLK.",
    ".KcYFyyyOyyyYLK.",
    ".KcYFyyOOyyyYLK.",
    ".KcYyyOYYOyyYLK.",
    ".KcYyyOYYOyyYLK.",
    ".KcYyOYFFYOyYLK.",
    ".KcYyOYFFYOyYLK.",
    ".KcYyyOOOOyyYLK.",
    ".KcYyyyKKyyyYLK.",
    ".KcYYYYYYYYYYLK.",
    ".KLLLLLLLLLLLLK.",
    "..KllllllllllK..",
    "...KLLLLLLLLK...",
    "....KKKKKKKK....",
]

LANTERN_SMALL = [  # 5×6 手提小灯
    ".KKK.",
    "KlllK",
    "KYFYK",
    "KyOyK",
    "KlllK",
    ".KKK.",
]

A_FRONT = [  # 9×14 蓝发波波头，正面
    "..KKKKK..",
    ".KAaaAAK.",
    "KAaAAAAAK",
    "KAAAAAAZK",
    "KAASSSAAK",
    "KASESESAK",
    "KAPSMSPAK",
    ".KASSSAK.",
    "..KWWWK..",
    ".KWWWWWK.",
    "KSWWwWWSK",
    ".KNNNNNK.",
    "..KSKSK..",
    "..KK.KK..",
]

B_FRONT = [  # 9×14 棕色短发，正面
    "..KKKKK..",
    ".KBbbBBK.",
    "KBbBBBBBK",
    "KBBBBBBXK",
    "KBSSSSSBK",
    "KsSESESsK",
    "KsPSMSPsK",
    ".KSSSSSK.",
    "..KRRRK..",
    ".KRRRRRK.",
    "KSRRrRRSK",
    ".KNNNNNK.",
    "..KNKNK..",
    "..KK.KK..",
]

A_CHEER = [  # 11×14 正面，举起左手（A_FRONT 右移 2 格 + 手臂）
    "....KKKKK..",
    "...KAaaAAK.",
    ".KKAaAAAAAK",
    "KSKAAAAAAZK",
    "KSKAASSSAAK",
    "KWKASESESAK",
    "KWKAPSMSPAK",
    ".KWKASSSAK.",
    "..KWWWWWK..",
    "...KWWWWWK.",
    "..KWWWwWWSK",
    "...KNNNNNK.",
    "....KSKSK..",
    "....KK.KK..",
]

B_CHEER = [  # 11×14 正面，举起右手（B_FRONT + 右侧手臂）
    "..KKKKK....",
    ".KBbbBBK...",
    "KBbBBBBBKK.",
    "KBBBBBBXKSK",
    "KBSSSSSBKSK",
    "KsSESESsKRK",
    "KsPSMSPsKRK",
    ".KSSSSSKRK.",
    "..KRRRRRK..",
    ".KRRRRRK...",
    "KSRRrRRRK..",
    ".KNNNNNK...",
    "..KNKNK....",
    "..KK.KK....",
]

A_BACK = [  # 背影
    "..KKKKK..",
    ".KAaaAAK.",
    "KAaAAAAAK",
    "KAAAAAAZK",
    "KAAAAAAZK",
    "KAAAAAAZK",
    "KZAAAAAZK",
    ".KZZZZZK.",
    "..KWWWK..",
    ".KWWWWWK.",
    "KSWWWWWSK",
    ".KNNNNNK.",
    "..KSKSK..",
    "..KK.KK..",
]

B_BACK = [  # 背影，背着包
    "..KKKKK..",
    ".KBbbBBK.",
    "KBbBBBBBK",
    "KBBBBBBXK",
    "KBBBBBBXK",
    "KXBBBBBXK",
    ".KXXXXXK.",
    "..KSSSK..",
    ".KGGGGGK.",
    "KRGgGGGRK",
    "KSGGGGGSK",
    ".KNNNNNK.",
    "..KNKNK..",
    "..KK.KK..",
]

STAR11 = [  # 头顶的大星星
    ".....#.....",
    ".....#.....",
    "....###....",
    "....###....",
    "###########",
    ".#########.",
    "..#######..",
    "..#######..",
    ".####.####.",
    ".###...###.",
    ".##.....##.",
]

STAR5 = ["..#..", "..#..", "#####", ".###.", ".#.#."]  # 牌子上的小星

CLOUD = [".WWW..", "WWWWWW", ".cccc."]


# ---------------- 画布工具 ----------------
def new_canvas():
    return [[None] * N for _ in range(N)]


def put(cv, x, y, col):
    if 0 <= x < N and 0 <= y < N:
        cv[y][x] = col


def blit(cv, rows, ox, oy, pal=PAL):
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != '.':
                put(cv, ox + dx, oy + dy, pal[ch])


def _rounded():
    cut = {0: 3, 1: 1, 2: 1}  # 圆角：每个角第 0 行切 3 格，第 1、2 行切 1 格
    m = set()
    for y in range(N):
        for x in range(N):
            ry, rx = min(y, N - 1 - y), min(x, N - 1 - x)
            if (ry in cut and rx < cut[ry]) or (rx in cut and ry < cut[rx]):
                continue
            m.add((x, y))
    return m


def _edge(mask):
    return {(x, y) for (x, y) in mask
            if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


SHAPE = _rounded()
RING0 = _edge(SHAPE)          # 外轮廓
_m1 = SHAPE - RING0
RING1 = _edge(_m1)            # 金属框外圈
_m2 = _m1 - RING1
RING2 = _edge(_m2)            # 金属框内圈
INNER = _m2 - RING2           # 画面

METALS = {
    'bronze': ('#f0b77a', '#c07a3e', '#7f4a20'),
    'silver': ('#f4f7fb', '#b4bfcc', '#6f7b8c'),
    'gold': ('#fff3a8', '#f2c12e', '#b5820f'),
}


def sky(cv, bands):
    for (x, y) in SHAPE:
        for y0, y1, col in bands:
            if y0 <= y <= y1:
                cv[y][x] = rgba(col)
                break


def glow(cv, cx, cy, rings, light):
    """以 (cx, cy) 为心，半径内的像素往 light 混合；rings = [(半径, 混合比例)]。"""
    lc = rgba(light)
    for (x, y) in INNER:
        d = hypot(x + 0.5 - cx, y + 0.5 - cy)
        t = max((tt for r, tt in rings if d <= r), default=0)
        if t and cv[y][x]:
            cv[y][x] = mix(cv[y][x], lc, t)


def halo(cv, cx, cy, rings):
    """实色同心圈：rings = [(半径, 颜色)]，从大到小画。"""
    for (x, y) in INNER:
        d = hypot(x + 0.5 - cx, y + 0.5 - cy)
        for r, col in rings:
            if d <= r:
                cv[y][x] = rgba(col)


def twinkle(cv, x, y, core='#fff6cf', arm='#a9b8ee'):
    put(cv, x, y, rgba(core))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(cv, x + dx, y + dy, rgba(arm))


def frame(cv, metal):
    hi, base, lo = (rgba(c) for c in METALS[metal])
    for (x, y) in RING1:
        cv[y][x] = hi if x + y < N - 1 else base
    for (x, y) in RING2:
        cv[y][x] = base if x + y < N - 1 else lo
    for (x, y) in RING0:
        cv[y][x] = rgba('#1d1626')
    for y in range(N):
        for x in range(N):
            if (x, y) not in SHAPE:
                cv[y][x] = None


def plaque(cv, n):
    """底部压在框上的小牌子，n 颗星。"""
    w = 6 * n + 3
    x0, y0, y1 = (N - w) // 2, 32, 38
    dark, fill = rgba('#1d1626'), rgba('#2b2140')
    for y in range(y0, y1 + 1):
        for x in range(x0, x0 + w):
            if x in (x0, x0 + w - 1) and y in (y0, y1):
                continue
            cv[y][x] = dark if (x in (x0, x0 + w - 1) or y in (y0, y1)) else fill
    gold, light = rgba('#ffd23f'), rgba('#fff3a0')
    for i in range(n):
        ox, oy = x0 + 2 + 6 * i, y0 + 1
        for dy, row in enumerate(STAR5):
            for dx, ch in enumerate(row):
                if ch == '#':
                    cv[oy + dy][ox + dx] = light if dy == 0 else gold


def big_star(cv, ox, oy):
    pix = {(ox + dx, oy + dy) for dy, row in enumerate(STAR11) for dx, ch in enumerate(row) if ch == '#'}
    for (x, y) in pix:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in pix:
                put(cv, x + dx, y + dy, PAL['K'])
    fill, hi, lo = rgba('#ffd23f'), rgba('#fff3a0'), rgba('#e89a17')
    for (x, y) in pix:
        col = fill
        if (x, y - 1) not in pix:
            col = hi
        elif (x, y + 1) not in pix:
            col = lo
        put(cv, x, y, col)
    put(cv, ox + 4, oy + 4, rgba('#ffffff'))


def hold_hands(cv, y):
    """左边的人（x10–18）和右边的人（x20–28）在 y 这一行牵手。"""
    for x in (18, 19, 20):
        put(cv, x, y - 1, PAL['K'])
        put(cv, x, y, PAL['S'])
        put(cv, x, y + 1, PAL['K'])


def cloud(cv, ox, oy):
    pal = {'W': rgba('#ffffff'), 'c': rgba('#d4ecfa')}
    blit(cv, CLOUD, ox, oy, pal)


# ---------------- 三张图 ----------------
def tier1():
    """引路人：夜里一盏提灯。"""
    cv = new_canvas()
    sky(cv, [(0, 8, '#0c1433'), (9, 14, '#111b40'), (15, 20, '#16234c'),
             (21, 26, '#1b2a57'), (27, 39, '#1f3061')])
    halo(cv, 20.0, 18.0, [(14.0, '#22336a'), (11.5, '#2c3e7c'), (9.6, '#3a4a8e')])
    for x, y in ((6, 6), (33, 7), (27, 4), (9, 28), (30, 29), (5, 20), (35, 23), (13, 4)):
        put(cv, x, y, rgba('#cfd8ff'))
    twinkle(cv, 8, 12)
    twinkle(cv, 32, 15)
    blit(cv, LANTERN_BIG, 12, 8)
    frame(cv, 'bronze')
    plaque(cv, 1)
    return cv


def tier2():
    """同行者：黎明，两个人背影牵手走在路上，赞助者提着灯。"""
    cv = new_canvas()
    hz = 24  # 地平线：头在太阳前，身体落在暗色地面上
    sky(cv, [(0, 4, '#33296a'), (5, 7, '#4b3279'), (8, 10, '#6c3a83'), (11, 13, '#934783'),
             (14, 16, '#bf5a80'), (17, 19, '#e2727a'), (20, 22, '#f6916e'), (23, hz, '#ffb36d'),
             (hz + 1, hz + 2, '#4a3266'), (hz + 3, 39, '#38285a')])
    for (x, y) in INNER:  # 太阳，只画地平线以上
        if y <= hz:
            d = hypot(x + 0.5 - 19.5, y + 0.5 - (hz + 1.0))
            if d <= 10.0:
                cv[y][x] = rgba('#ffc983')
            if d <= 7.0:
                cv[y][x] = rgba('#ffdea0')
            if d <= 4.0:
                cv[y][x] = rgba('#fff1c8')
    for cx, half, h in ((7, 6, 3), (32, 6, 2)):  # 远山
        for x in range(cx - half, cx + half + 1):
            k = 1 - ((x - cx) / (half + 0.5)) ** 2
            for y in range(hz - round(h * k) + 1, hz + 1):
                if (x, y) in INNER:
                    cv[y][x] = rgba('#4a2c5e')
    for y in range(hz + 1, 37):  # 小路
        hw = 1.0 + (y - hz - 1) * 0.7
        for x in range(N):
            off = abs(x + 0.5 - 19.5)
            if off <= hw and (x, y) in INNER:
                cv[y][x] = rgba('#5e4176') if off <= hw * 0.45 else rgba('#523a6c')
    for x, y in ((7, 9), (8, 10), (9, 9), (12, 6), (13, 7), (14, 6)):  # 两只鸟
        put(cv, x, y, rgba('#2a1d45'))
    blit(cv, A_BACK, 10, 17)
    blit(cv, B_BACK, 20, 17)
    hold_hands(cv, 27)
    glow(cv, 29.5, 31.0, [(5.0, 0.25), (3.5, 0.45)], '#ff9a5a')
    blit(cv, LANTERN_SMALL, 27, 28)
    frame(cv, 'silver')
    plaque(cv, 2)
    return cv


def tier3():
    """共创者：白天，两个人牵手，头顶一颗一起造出来的星星。"""
    cv = new_canvas()
    sky(cv, [(0, 7, '#3aa0e6'), (8, 12, '#4fb1ee'), (13, 17, '#66c1f4'),
             (18, 22, '#7ecff8'), (23, 39, '#98dbfb')])
    cx, cy = 19.5, 9.5
    white = rgba('#ffffff')
    for (x, y) in INNER:  # 放射光
        d = hypot(x + 0.5 - cx, y + 0.5 - cy)
        ang = atan2(y + 0.5 - cy, x + 0.5 - cx)
        if d < 24 and int((ang + pi) / (2 * pi) * 16) % 2 == 0:
            cv[y][x] = mix(cv[y][x], white, 0.25)
    glow(cv, cx, cy, [(8.5, 0.30), (7.0, 0.5)], '#fffbe0')
    cloud(cv, 3, 14)
    cloud(cv, 31, 15)
    for x in range(N):  # 草坡
        top = 31 + round(4 * ((x + 0.5 - 19.5) / 17.0) ** 2)
        for y in range(top, N):
            if (x, y) in SHAPE:
                cv[y][x] = rgba('#8fe07c') if y == top else rgba('#4fae4f')
    big_star(cv, 14, 4)
    blit(cv, A_CHEER, 8, 17)
    blit(cv, B_CHEER, 20, 17)
    hold_hands(cv, 27)
    for x, y in ((6, 8), (33, 6), (5, 23), (34, 24)):
        twinkle(cv, x, y, core='#fffbe0', arm='#ffe27a')
    frame(cv, 'gold')
    plaque(cv, 3)
    return cv


# ---------------- 输出 ----------------
def render(cv, scale=SCALE):
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    for y in range(N):
        for x in range(N):
            if cv[y][x]:
                im.putpixel((x, y), cv[y][x])
    return im.resize((N * scale, N * scale), Image.NEAREST)


def main():
    icons = [
        ('tier1_yinluren.png', '引路人 ¥5', tier1()),
        ('tier2_tongxingzhe.png', '同行者 ¥20', tier2()),
        ('tier3_gongchuangzhe.png', '共创者 ¥50', tier3()),
    ]
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 26)
    cell, gap = 320, 40
    W = 3 * cell + 4 * gap
    H = gap + cell + 60 + 120 + gap
    sheet = Image.new('RGBA', (W, H), (242, 242, 242, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, label, cv) in enumerate(icons):
        im = render(cv)
        im.save(OUT / name)
        x = gap + i * (cell + gap)
        sheet.alpha_composite(render(cv, 8), (x, gap))
        d.text((x, gap + cell + 12), label, fill=(40, 40, 40), font=font)
        sheet.alpha_composite(im.resize((96, 96), Image.LANCZOS), (x, gap + cell + 60))
        sheet.alpha_composite(im.resize((56, 56), Image.LANCZOS), (x + 120, gap + cell + 60))
        print(OUT / name, im.size)
    sheet.convert('RGB').save(OUT / 'preview.png')
    print(OUT / 'preview.png')


if __name__ == '__main__':
    main()
