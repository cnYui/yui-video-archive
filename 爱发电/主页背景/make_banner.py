# -*- coding: utf-8 -*-
"""爱发电主页背景图：把三档方案的三个元素画进同一幅像素风景里（不放文字、金额）。

左边夜里，路口一根灯杆挂着提灯（引路）；中间黎明，两个人牵手沿着路走向日出，
赞助者提着一盏小灯（同行）；右边白天，路通到小山坡，坡顶悬着一颗一起造出来的星星（共创）。
天空从夜到昼连续过渡（抖动着色，不分块）。

200×100 的像素网格，最近邻放大 12 倍 → 2400×1200（2:1）。爱发电主页封面电脑上按 4:1
居中裁（只露第 25–75 行），手机约 2:1 全露，所以灯、人、星星都放在第 25–75 行之间。

用法：python make_banner.py      （人物、小灯的精灵从 ../方案图标/make_icons.py 里取）
"""
import random
import sys
from math import atan2, hypot, pi, sin
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '方案图标'))
import make_icons as mi  # noqa: E402

W, H = 200, 100
SCALE = 12
HZ = 60            # 地平线（这一行及以上是天）
DY = -5            # 灯杆、人物、路相对第一版整体上移的行数（让电脑上的 4:1 那条不贴底）
BAND = (25, 75)    # 电脑上 4:1 能看到的行
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def ramp(stops, t):
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            return lerp(rgb(c0), rgb(c1), (t - p0) / (p1 - p0) if p1 > p0 else 0)
    return rgb(stops[-1][1])


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def dq(v, n, x, y):
    """带 4×4 抖动地把 0..1 的 v 量化成 n 档。"""
    t = (BAYER[y % 4][x % 4] + 0.5) / 16
    return min(n - 1, max(0, int(v * (n - 1) + t))) / (n - 1)


def time_of_day(x, y, steps=40):
    """横向位置 → 一天里的时间 s：0 = 夜，0.5 = 黎明，1 = 白天（带抖动）。"""
    u = x / (W - 1)
    s = (u - 0.12) / 0.76
    return dq(max(0.0, min(1.0, s)), steps, x, y)


def by_time(s, night, dawn, day):
    """三个时段的颜色按 s 混合。参数是颜色元组。"""
    if s <= 0.5:
        return lerp(night, dawn, smooth(s / 0.5))
    return lerp(dawn, day, smooth((s - 0.5) / 0.5))


SKY = {
    'night': [(0, '#0b1230'), (0.55, '#15214a'), (1, '#24376b')],
    'dawn': [(0, '#33296a'), (0.35, '#6c3a83'), (0.68, '#d0637a'), (1, '#ffb36d')],
    'day': [(0, '#3a9fe5'), (0.5, '#64c0f3'), (1, '#a8e2fb')],
}


def sky_color(x, y):
    s = time_of_day(x, y)
    v = dq(y / HZ, 18, x, y)
    return by_time(s, ramp(SKY['night'], v), ramp(SKY['dawn'], v), ramp(SKY['day'], v))


def tod_color(x, y, night, dawn, day):
    return by_time(time_of_day(x, y), rgb(night), rgb(dawn), rgb(day))


class Canvas:
    def __init__(self):
        self.px = [[(0, 0, 0)] * W for _ in range(H)]

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = c

    def get(self, x, y):
        return self.px[y][x]

    def blend(self, x, y, c, t):
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = lerp(self.px[y][x], c, t)

    def sprite(self, rows, ox, oy, pal):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != '.':
                    c = pal[ch]
                    self.put(ox + dx, oy + dy, c[:3] if len(c) == 4 else c)


LANTERN_MID = [  # 9×12 挂在灯杆上的提灯
    "...KKK...",
    "..KcllK..",
    ".KLLLLLK.",
    "KcYYYYYLK",
    "KcYyOyYLK",
    "KcYOYOYLK",
    "KcYOFOYLK",
    "KcYyOyYLK",
    "KcYYYYYLK",
    ".KLLLLLK.",
    "..KlllK..",
    "...KKK...",
]

STAR15 = [
    ".......#.......",
    ".......#.......",
    "......###......",
    "......###......",
    ".....#####.....",
    "###############",
    ".#############.",
    "..###########..",
    "...#########...",
    "...#########...",
    "..#####.#####..",
    "..####...####..",
    ".####.....####.",
    ".###.......###.",
    ".##.........##.",
]

CLOUD = ["...WWW....", ".WWWWWWW..", "WWWWWWWWWW", ".cccccccc."]

# 路：(中心 x, 行, 半宽)，从近处左下一直爬到右边坡顶
ROAD = [(14, 100, 14), (44, 85, 10.5), (78, 74, 8.5), (100, 67, 7.5),
        (124, 61, 4.5), (146, 55, 2.6), (160, 50, 1.4), (165, 47, 0.8)]


def road_at(y):
    """某一行路的中心和半宽；不在路的范围里返回 None。"""
    for (x0, y0, w0), (x1, y1, w1) in zip(ROAD, ROAD[1:]):
        if y1 <= y <= y0:
            t = (y0 - y) / (y0 - y1) if y0 != y1 else 0
            return x0 + (x1 - x0) * t, w0 + (w1 - w0) * t
    return None


def hill_top(x):
    """右边的小山坡（星星所在）。"""
    return 47 + ((x - 166) / 31.0) ** 2 * 13


def far_hills(x):
    return HZ - round(3 + 2.2 * sin(x / 11.0) + 1.6 * sin(x / 4.7 + 2.0))


def build():
    cv = Canvas()
    # 1. 天空
    for y in range(HZ + 1):
        for x in range(W):
            cv.put(x, y, sky_color(x, y))
    # 2. 太阳（黎明，地平线上露半个）
    for y in range(HZ + 1):
        for x in range(W):
            d = hypot(x + 0.5 - 100.5, y + 0.5 - (HZ + 1.5))
            if d <= 24:
                cv.blend(x, y, rgb('#ffcf8a'), 0.22)
            for r, col in ((13, '#ffc983'), (9, '#ffdea0'), (5, '#fff1c8')):
                if d <= r:
                    cv.put(x, y, rgb(col))
    # 3. 星星那一侧的放射光 + 光晕（只在白天那段的天上）
    scx, scy = 166.5, 36.5
    for y in range(HZ + 1):
        for x in range(W):
            d = hypot(x + 0.5 - scx, y + 0.5 - scy)
            s = time_of_day(x, y)
            if d < 40 and s > 0.55:
                ang = atan2(y + 0.5 - scy, x + 0.5 - scx)
                if int((ang + pi) / (2 * pi) * 18) % 2 == 0:
                    cv.blend(x, y, (255, 255, 255), 0.20 * (1 - d / 40) * smooth((s - 0.55) / 0.2) * 1.6)
            if d <= 13:
                cv.blend(x, y, rgb('#fffbe0'), 0.25)
            if d <= 10:
                cv.blend(x, y, rgb('#fffbe0'), 0.35)
    # 4. 月亮、星星（夜那段）
    for y in range(3, 26):
        for x in range(8, 32):
            if hypot(x - 19.5, y - 13.5) <= 6.5 and hypot(x - 22.5, y - 11.5) > 5.6:
                cv.put(x, y, rgb('#eef1ff'))
    rnd = random.Random(11)
    for _ in range(90):
        x, y = rnd.randrange(1, 80), rnd.randrange(1, HZ - 6)
        if time_of_day(x, y, 100) < 0.32 and hypot(x - 38.5, y - 52) > 14 and hypot(x - 19.5, y - 13.5) > 9:
            cv.put(x, y, rgb('#cfd8ff') if rnd.random() < 0.75 else rgb('#fff6cf'))
    for x, y in ((44, 9), (66, 20), (8, 40), (58, 36), (30, 30)):
        cv.put(x, y, rgb('#fff6cf'))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.put(x + dx, y + dy, rgb('#a9b8ee'))
    # 5. 远山（黎明那段挡住太阳的下半截）
    for x in range(W):
        for y in range(far_hills(x), HZ + 1):
            cv.put(x, y, tod_color(x, y, '#1a2550', '#58396e', '#7fbfa8'))
    # 6. 地面
    for y in range(HZ + 1, H):
        for x in range(W):
            cv.put(x, y, tod_color(x, y, '#0f1733', '#2f2350', '#45a046'))
    # 7. 右边小山坡
    for x in range(120, W):
        top = round(hill_top(x))
        for y in range(top, H):
            if y < top + 1:
                c = tod_color(x, y, '#2a3a5a', '#6a4a6e', '#8fe07c')
            else:
                c = tod_color(x, y, '#1d2a48', '#4a3560', '#5cb85a')
                if x > 168 and (x + y) % 3 == 0 and y < top + 6:
                    c = tod_color(x, y, '#1a2542', '#43305a', '#4fa64f')
            cv.put(x, y, c)
    # 8. 路
    for y in range(48, H):
        r = road_at(y)
        if not r:
            continue
        cx, hw = r
        for x in range(W):
            off = abs(x + 0.5 - cx)
            if off <= hw:
                edge = off > hw - 1.0
                c = (tod_color(x, y, '#273259', '#6e4866', '#cdbb7e') if edge
                     else tod_color(x, y, '#323f6c', '#8c5d70', '#e6d79c'))
                cv.put(x, y, c)
    # 9. 草丛、小花、石头
    rnd = random.Random(5)
    for _ in range(70):
        x, y = rnd.randrange(0, W), rnd.randrange(HZ + 2, H - 1)
        r = road_at(y)
        if r and abs(x + 0.5 - r[0]) <= r[1] + 1:
            continue
        s = time_of_day(x, y, 100)
        if s > 0.7:
            cv.put(x, y, rgb('#8fe07c'))
            cv.put(x, y - 1, rgb('#8fe07c'))
            if rnd.random() < 0.35:
                cv.put(x + 1, y - 2, rgb(rnd.choice(['#fff3a0', '#ff9ab0', '#ffffff'])))
        elif s < 0.35:
            cv.put(x, y, rgb('#1d2850'))
            cv.put(x + 1, y, rgb('#26335e'))
    return cv


def lantern_post(cv):
    """左边的灯杆 + 提灯 + 灯光。"""
    # 灯光：天上一圈光晕，地上一片暖光
    for y in range(H):
        for x in range(W):
            d = hypot(x + 0.5 - 38.5, y + 0.5 - (57.5 + DY))
            if y <= HZ:
                if d <= 17:
                    cv.blend(x, y, rgb('#8fa0e6'), 0.12)
                if d <= 12:
                    cv.blend(x, y, rgb('#ffc875'), 0.14)
                if d <= 8:
                    cv.blend(x, y, rgb('#ffc875'), 0.18)
            e = ((x + 0.5 - 40) / 26) ** 2 + ((y + 0.5 - (90 + DY)) / 9) ** 2
            if y > HZ and e <= 1:
                cv.blend(x, y, rgb('#ffb35c'), 0.16 if e > 0.4 else 0.30)
    wood, wood_hi, k = rgb('#4a3423'), rgb('#6b4a2b'), rgb('#2a1a12')
    for y in range(47 + DY, 89 + DY):  # 立柱
        cv.put(28, y, k)
        cv.put(29, y, wood_hi)
        cv.put(30, y, wood)
        cv.put(31, y, k)
    for x in range(27, 33):  # 柱顶
        cv.put(x, 46 + DY, k)
    for x in range(31, 40):  # 横臂
        cv.put(x, 47 + DY, k)
        cv.put(x, 48 + DY, wood)
        cv.put(x, 49 + DY, k)
    for i in range(4):  # 斜撑
        cv.put(32 + i, 53 + DY - i, wood)
        cv.put(32 + i, 54 + DY - i, k)
    cv.put(38, 50 + DY, k)  # 挂钩
    for x in range(25, 35):  # 底座石头
        for y in range(87 + DY, 90 + DY):
            cv.put(x, y, rgb('#3a3f5c') if y == 87 + DY else rgb('#2b2f48'))
    cv.put(24, 88 + DY, k)
    cv.put(35, 88 + DY, k)
    for x in range(25, 35):
        cv.put(x, 86 + DY, k)
    pal = {k_: v[:3] for k_, v in mi.PAL.items()}
    cv.sprite(LANTERN_MID, 34, 51 + DY, pal)
    for x, y in ((20, 66), (49, 61), (24, 52), (55, 74), (13, 76), (46, 50), (60, 66)):
        cv.put(x, y + DY, rgb('#ffe98a'))  # 萤火虫


def travellers(cv):
    """两个人背影牵手，赞助者右手提着小灯。"""
    pal = {k_: v[:3] for k_, v in mi.PAL.items()}
    ax, bx, top = 91, 101, 59 + DY
    # 脚下一点影子
    for x in range(ax + 1, bx + 9):
        cv.blend(x, top + 14, (0, 0, 0), 0.25)
    cv.sprite(mi.A_BACK, ax, top, pal)
    cv.sprite(mi.B_BACK, bx, top, pal)
    hy = top + 10
    for x in range(ax + 8, bx + 1):  # 牵手
        cv.put(x, hy - 1, pal['K'])
        cv.put(x, hy, pal['S'])
        cv.put(x, hy + 1, pal['K'])
    # 小灯 + 一点暖光
    for y in range(H):
        for x in range(W):
            d = hypot(x + 0.5 - 110.5, y + 0.5 - (73.5 + DY))
            if d <= 5:
                cv.blend(x, y, rgb('#ff9a5a'), 0.22 if d > 3 else 0.38)
    cv.sprite(mi.LANTERN_SMALL, 108, 70 + DY, pal)


def star(cv):
    ox, oy = 159, 29
    pix = {(ox + dx, oy + dy) for dy, row in enumerate(STAR15) for dx, ch in enumerate(row) if ch == '#'}
    k = rgb('#2a1a12')
    for (x, y) in pix:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in pix:
                cv.put(x + dx, y + dy, k)
    fill, hi, lo = rgb('#ffd23f'), rgb('#fff3a0'), rgb('#e89a17')
    for (x, y) in pix:
        c = fill
        if (x, y - 1) not in pix:
            c = hi
        elif (x, y + 1) not in pix:
            c = lo
        cv.put(x, y, c)
    cv.put(ox + 5, oy + 6, (255, 255, 255))
    cv.put(ox + 6, oy + 6, (255, 255, 255))
    for x, y in ((150, 28), (182, 32), (155, 45), (178, 44), (171, 22)):  # 闪光
        cv.put(x, y, rgb('#fffbe0'))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.put(x + dx, y + dy, rgb('#ffe27a'))


def clouds_birds(cv):
    for ox, oy in ((140, 6), (180, 12), (120, 18)):
        for dy, row in enumerate(CLOUD):
            for dx, ch in enumerate(row):
                if ch != '.':
                    base = rgb('#ffffff') if ch == 'W' else rgb('#d4ecfa')
                    x, y = ox + dx, oy + dy
                    s = time_of_day(x, y)
                    # 越往黎明那边，云越染上一点粉
                    cv.put(x, y, lerp(base, rgb('#f6b8b0'), max(0.0, (0.75 - s) / 0.3) * 0.6))
    for x, y in ((84, 22), (85, 23), (86, 22), (92, 17), (93, 18), (94, 17)):
        cv.put(x, y, rgb('#2a1d45'))


def main():
    cv = build()
    lantern_post(cv)
    star(cv)
    clouds_birds(cv)
    travellers(cv)
    im = Image.new('RGB', (W, H))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), cv.get(x, y))
    big = im.resize((W * SCALE, H * SCALE), Image.NEAREST)
    big.save(HERE / 'banner_2400x1200.png')
    band = big.crop((0, BAND[0] * SCALE, W * SCALE, BAND[1] * SCALE))
    pv = Image.new('RGB', (1200, 600 + 300 + 30), (242, 242, 242))
    pv.paste(big.resize((1200, 600), Image.LANCZOS), (0, 0))
    pv.paste(band.resize((1200, 300), Image.LANCZOS), (0, 630))
    pv.save(HERE / 'preview.png')
    print(HERE / 'banner_2400x1200.png', big.size)


if __name__ == '__main__':
    main()
