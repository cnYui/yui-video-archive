# -*- coding: utf-8 -*-
"""文章配图（@kmeanskaran 的 X 长文里的手绘风示意图）→ media/figs/ + figs.js（window.FG = {名字: {src, w, h, bg, marks}}）。
scenes.js 的 figShot() 按“原图像素坐标”给镜头取景、画高亮框。

  python build_figs.py

图原件在 素材\\2026-10_AI工程师GPU指南\\图片\\（用 X 的 FxTwitter 接口取的原图，?name=orig）；不改图，只拷贝、量背景色。
"card" 是拼出来的：X 推文卡（capture_pages.py 的 X_card：作者 / 日期 / 点赞）+ 文章封面图，上下叠在一张画布上，镜头先看推文卡再往下摇到封面（嵌入页不显示文章标题，标题在封面图上）。
"""
import json
import shutil
from pathlib import Path

from PIL import Image

from common import HERE, MAT

SRC_DIR = MAT / "2026-10_AI工程师GPU指南" / "图片"
OUT = HERE / "media" / "figs"
FIGS = {                                    # 名字: 文件
    "dec": "06_Decoding_step_by_step.jpg",          # 一个解码步，穿过存储器阶梯（gpt-oss-120b、一张 H100、batch 1）：搬权重 1.5 ms / 算 0.01 ms
    "inside": "03_Inside_GPU.png",                  # H100 SXM 内部：132 个 SM、L2 50 MB、3.35 TB/s 的细管子、HBM 80 GB
    "trainvs": "07_Training_vs_Inference_on_GPU.jpg",   # 同一张 GPU 两份活：训练 vs 推理（每参数 18 字节；2.1 TB vs 65 GB）
    "quant": "08_Quantization_on_GPU.jpg",          # 量化：BF16 → INT8 的缩放例子；仅权重 vs 原生低精度
}


def edge_bg(im):
    px = im.convert("RGB")
    return "#%02X%02X%02X" % px.getpixel((6, 6))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fg = {}
    for k, fn in FIGS.items():
        src = SRC_DIR / fn
        dst = OUT / f"{k}{src.suffix}"
        shutil.copy(src, dst)
        im = Image.open(src)
        fg[k] = {"src": dst.name, "w": im.width, "h": im.height, "bg": edge_bg(im), "marks": {}}

    # 推文卡 + 文章封面
    cover = Image.open(SRC_DIR / "00_cover_cover.png").convert("RGB")             # 1600×640
    pages = json.loads((HERE / "pages.json").read_text(encoding="utf-8"))
    card = Image.open(HERE / "media" / pages["X_card"]["src"]).convert("RGB")      # 1096×446（DSF 2 的推文卡）
    bg = cover.getpixel((6, 6))
    W = 1600
    CX, CY = (W - card.width) // 2, 70                                              # 推文卡居中，上边留 70
    COVER_Y = CY + card.height + 110
    H = COVER_Y + cover.height + 60
    can = Image.new("RGB", (W, H), bg)
    can.paste(card, (CX, CY))
    can.paste(cover, (0, COVER_Y))
    can.save(OUT / "card.png")
    mk = {}                                                                         # 名字 → 画布上的矩形 [x, y, w, h]
    for name, rects in pages["X_card"]["marks"].items():
        mk[name] = [[CX + x, CY + y, w, h] for x, y, w, h in rects]
    mk["cover_title"] = [[70, COVER_Y + 120, 560, 250]]                             # 封面图上的大标题 “GPUs for AI Engineers”
    mk["cover_all"] = [[0, COVER_Y, 1600, 640]]
    fg["card"] = {"src": "card.png", "w": W, "h": H, "bg": "#%02X%02X%02X" % bg, "marks": mk, "cardY": CY, "coverY": COVER_Y}

    (HERE / "figs.js").write_text("window.FG = " + json.dumps(fg, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    for k, v in fg.items():
        print(f"{k:8s} {v['w']}×{v['h']}  bg {v['bg']}  marks {list(v['marks'])}")


if __name__ == "__main__":
    main()
