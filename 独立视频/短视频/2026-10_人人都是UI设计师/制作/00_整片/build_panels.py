# -*- coding: utf-8 -*-
"""把 20 张对比图的标注合并成引擎要的 panels.js（window.RULES）；把长视频已经截好的推文 / 书官网页面图拷过来，写 pages.js。

输入（全部只读，不改长视频目录）：
  LONG/台本/marks/marks_*.json      每张图的 size、sets（面板 L / R 外框、高亮框 hl）——长视频的两个标注子代理量的，原图像素坐标
  LONG/台本/rules_meta.json          每条规则的标题、书里的英文章名、页码
  LONG/制作/00_整片/pages.json + media/pages/*.png   推文（X_t1）、书官网首屏（Y_hero）、“The Book”一节（Y_book）、“Design with tactics”（Y_tactics）
  IMG_DIR/图NN_*.jpg                 20 张对比图原图（共用素材目录，绝对路径引用，不拷进本条）
输出：panels.js、pages.js、media/pages/*.png、_check/panels_check.png（本条用到的面板 + 编号的高亮框，对着它写 scenes.js）

VIEWS = 本条对 marks 里面板外框的改动（marks 里的 L / R 是“面板”，有的面板里空白太多、比例不适合放进 16:9 的框，这里换成更合适的取景）。
每个面板另外量一个“边缘底色”（取景框外圈 3 px 的中位色），引擎拿它给框里没铺满的地方填色，看起来就像面板一直延伸到框边。
"""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import HERE, IMG_DIR, LONG

OUT_PAGES = HERE / "media" / "pages"
PAGES_USED = ["X_t1", "Y_hero", "Y_book", "Y_tactics"]
USED = [6, 9, 13, 14, 17]                       # 本条讲的 5 条（_check 图只画这几条）
# 页面图上补的手动框选（长视频的 pages.json 里没有；坐标是页面图像素，用 PIL 画出来核对过）
EXTRA_MARKS = {"X_t1": {"@rect:《Refactoring UI》": [[100, 432, 345, 54]]}}

# 对 marks 里的面板外框 L / R 的改动：{规则号: {set 序号: {"L": [x, y, w, h], "R": [...]}}}（原图像素坐标）
VIEWS = {
    # 图 06：面板上方有一大条白色页眉（放 ✕ 角标），按钮卡片只占中间一小块；收紧到卡片 + 一点边（850×478，16:9），按钮在框里大约 1.35 倍
    6: {0: {"L": [140, 56, 850, 478], "R": [1272, 56, 850, 478]}},
    # 图 09：整块面板里只有左半边有用（20px 标注 + 标签 + 输入框），收紧到 640×360（16:9），标注的字在框里大得多
    9: {0: {"L": [100, 80, 640, 360], "R": [1054, 80, 640, 360]}},
    # 图 13 上层：marks 的 L 只含 5 色色条（1249×115 的细条），放进 16:9 的框里太瘦——取和 R 一样高的整块（色条在中间），两边一样大
    # 图 13 下层：R 比 L 多了红色连线和底部色块行（1096 对 826 高）；两边取同样大、界面位置对齐的窗口（R 的界面比 L 低 63 px），上下两个框里的界面一样大
    # R 往左多取一点：行名 Primary / Neutral / Accents 贴着 marks 的左边，原来的取景把首字母压在框边上
    13: {0: {"L": [8, 14, 1278, 585], "R": [1290, 14, 1266, 585]},
         1: {"L": [31, 756, 1233, 826], "R": [1316, 756, 1233, 826]}},
    # 图 14：面板右边有一大片空白，裁到数字（5.97 (AA) / 12.32 (AAA)）后面留一点边（右边的标签要有地方放）
    14: {0: {"L": [20, 20, 960, 480], "R": [1081, 20, 960, 480]}},
}


def load_marks():
    marks = {}
    for f in sorted((LONG / "台本" / "marks").glob("marks_*.json")):
        marks.update(json.loads(f.read_text(encoding="utf-8")))
    return marks


def edge_color(im, rect, ratio=1474 / 829):
    """框里没铺满的那两边的底色（#rrggbb）：取景框比框（1474×829）更“高”→ 左右留边，取左右两列（离边 2–5 px）的中位色；更“宽”→ 上下留边，取上下两行。"""
    x, y, w, h = [int(round(v)) for v in rect]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(im.width, x + w), min(im.height, y + h)
    a = np.asarray(im.convert("RGB").crop((x0, y0, x1, y1)))
    if (x1 - x0) / (y1 - y0) < ratio:
        strip = np.concatenate([a[:, 2:5].reshape(-1, 3), a[:, -5:-2].reshape(-1, 3)])
    else:
        strip = np.concatenate([a[2:5].reshape(-1, 3), a[-5:-2].reshape(-1, 3)])
    r, g, b = [int(v) for v in np.median(strip, axis=0)]
    return f"#{r:02x}{g:02x}{b:02x}"


def main():
    meta = json.loads((LONG / "台本" / "rules_meta.json").read_text(encoding="utf-8"))
    marks = load_marks()
    rules, miss = {}, []
    for n, m in meta.items():
        key = m["img"]
        if key not in marks:
            miss.append(key)
            continue
        mk = marks[key]
        path = IMG_DIR / key
        im = Image.open(path)
        size = list(im.size)
        assert size == mk["size"], f"{key} 尺寸对不上：标注 {mk['size']}，图片 {size}"
        sets = []
        for si, st in enumerate(mk["sets"]):
            v = VIEWS.get(int(n), {}).get(si, {})
            L, R = v.get("L", st["L"]), v.get("R", st["R"])
            sets.append(dict(L=L, R=R, hl=st["hl"], bgL=edge_color(im, L), bgR=edge_color(im, R), note=st.get("note", "")))
        rules[int(n)] = dict(n=int(n), title=m["title"], en=m["en"], page=m["page"], img=key, url=path.as_uri(), size=size,
                             tagL=m["tagL"], tagR=m["tagR"], sets=sets)
    (HERE / "panels.js").write_text("window.RULES = " + json.dumps(rules, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"panels.js：{len(rules)} 条规则" + (f"；缺标注：{miss}" if miss else ""))

    # 页面图：从长视频拷（只读）
    OUT_PAGES.mkdir(parents=True, exist_ok=True)
    pg_all = json.loads((LONG / "制作" / "00_整片" / "pages.json").read_text(encoding="utf-8"))
    pg = {}
    for k in PAGES_USED:
        shutil.copy2(LONG / "制作" / "00_整片" / "media" / pg_all[k]["src"], OUT_PAGES / Path(pg_all[k]["src"]).name)
        pg[k] = dict(pg_all[k], marks=dict(pg_all[k]["marks"], **EXTRA_MARKS.get(k, {})))
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(pg, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    (HERE / "pages.json").write_text(json.dumps(pg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"pages.js：{len(pg)} 张页面图（{', '.join(pg)}）")

    # 检查图：本条用到的面板 + 编号的高亮框
    chk = HERE / "_check"
    chk.mkdir(exist_ok=True)
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 22)
    tiles = []
    for n in USED:
        R = rules[n]
        im = Image.open(IMG_DIR / R["img"]).convert("RGB")
        for si, st in enumerate(R["sets"]):
            for side in ("L", "R"):
                x, y, w, h = st[side]
                crop = im.crop((x, y, x + w, y + h)).copy()
                d = ImageDraw.Draw(crop)
                for k, hl in enumerate(st["hl"]):
                    if hl["p"] != side:
                        continue
                    rx, ry, rw, rh = hl["r"]
                    d.rectangle((rx - x, ry - y, rx - x + rw, ry - y + rh), outline="#EF4444" if hl["role"] == "problem" else "#16A34A", width=3)
                    d.text((rx - x + 3, ry - y + 1), str(k), fill="#2563EB", font=font)
                s = 560 / crop.width
                crop = crop.resize((560, max(1, int(crop.height * s))), Image.LANCZOS)
                tile = Image.new("RGB", (560, crop.height + 30), st["bg" + side])
                tile.paste(crop, (0, 30))
                ImageDraw.Draw(tile).text((4, 2), f"规则 {n:02d} set{si} {side}  边缘色 {st['bg' + side]}", fill="#111", font=font)
                tiles.append(tile)
    W = 2
    rows = [tiles[i:i + W] for i in range(0, len(tiles), W)]
    H = sum(max(t.height for t in r) + 10 for r in rows) + 10
    sheet = Image.new("RGB", (W * 570 + 10, H), "#C9CDD3")
    y = 10
    for r in rows:
        for j, t in enumerate(r):
            sheet.paste(t, (10 + j * 570, y))
        y += max(t.height for t in r) + 10
    sheet.save(chk / "panels_check.png")
    print("检查图 ->", chk / "panels_check.png")
    for n in USED:
        for si, st in enumerate(rules[n]["sets"]):
            for k, hl in enumerate(st["hl"]):
                print(f"  规则 {n:02d} set{si} hl[{k}] {hl['p']} {hl['role']:7s} {hl['r']} {hl['zh']}")


if __name__ == "__main__":
    main()
