# -*- coding: utf-8 -*-
r"""扫抽好的素材帧里有没有人脸（官方课 / 访谈素材里“讲师突然切回来”的镜头）。

  python scan_faces.py <本条目录> [--min-face 90] [--step 6]

读 <本条>\制作\00_整片\frames.js 里每个窗口（上框 scr / 下框 scr2）每一帧用的素材帧文件，每 --step 帧（默认 6 = 0.2 s）用 OpenCV Haar 正脸检测看一张，
脸宽 ≥ --min-face 像素（素材帧是 1474 宽）的连成一段打印：场景 / 窗口 / 成片秒数 / 脸的位置。有命中退出码 1，没有 0。
用在：《Claude官方教程》这类“只用官方课的屏幕 / 动画镜头、不放讲师的脸”的片子；`prep_frames.py` 之后、渲整片之前跑一遍。
为什么要扫：三秒一帧的联系表看不出讲师的短暂切入（第 1 期出镜版：按联系表推断“这一段都是屏幕”，扫完发现 4 处露脸）。
误报：鼠标手形光标、圆形头像图标偶尔会被当成脸（宽 100 px 左右、只出现 1–2 张），看一眼那一帧就知道。
"""
import json
import sys
from pathlib import Path

import cv2


def load_js(path):
    s = Path(path).read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ep = Path(args[0])
    opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    min_face, step = opt("--min-face", 90), opt("--step", 6)
    here = ep / "制作" / "00_整片"
    if not (here / "media").is_dir() or not any((here / "media").iterdir()):
        print("制作/00_整片/media 不存在或是空的（被清掉了？）：先跑 prep_frames.py 抽帧再扫")
        return 2
    tl, fr = load_js(here / "timeline.js"), load_js(here / "frames.js")
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    fps = tl["fps"]
    segs = tl["segs"]

    def seg_of(t):
        g = None
        for s in segs:
            if s["s"] <= t + 1e-6:
                g = s
        return g["id"] if g else "?"

    hits = []
    n_read = n_miss = 0
    for key in ("scr", "scr2"):
        arr = fr.get(key) or []
        for n in range(0, len(arr), step):
            f = arr[n]
            if not f or f.startswith("card"):
                continue
            im = cv2.imread(str(here / "media" / f), cv2.IMREAD_GRAYSCALE)
            if im is None:
                n_miss += 1
                continue
            n_read += 1
            faces = det.detectMultiScale(im, scaleFactor=1.1, minNeighbors=6, minSize=(min_face, min_face))
            if len(faces):
                hits.append((n / fps, key, seg_of(n / fps), [tuple(map(int, b)) for b in faces]))
    if n_miss and n_miss > n_read:
        print(f"素材帧大多读不到（读到 {n_read}，缺 {n_miss}）：media/ 被清掉了？先跑 prep_frames.py 再扫")
        return 2
    if not hits:
        print(f"没扫到脸（看了 {n_read} 张）")
        return 0
    runs, cur = [], [hits[0]]
    for h in hits[1:]:
        if h[1] == cur[-1][1] and h[0] - cur[-1][0] <= step / fps * 2.5:
            cur.append(h)
        else:
            runs.append(cur)
            cur = [h]
    runs.append(cur)
    for r in runs:
        print(f"{r[0][2]} {'上框' if r[0][1] == 'scr' else '下框'} {r[0][0]:.1f}–{r[-1][0]:.1f} s（{len(r)} 张） 脸 {r[0][3][0]}")
    print(f"共 {len(runs)} 段疑似有脸（鼠标手形 / 头像图标偶尔误报，看一眼那一帧）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
