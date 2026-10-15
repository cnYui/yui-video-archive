# -*- coding: utf-8 -*-
"""封面候选的底图：作者长文里的示意图，各自裁一块（宽高比约 1.6–1.7，三行大字版式里框不会太高）+ 画橙色高亮框（和成片里的高亮框同一个颜色），存进 _src/；
make_cover_framed.py 读 candidates_framed.json 里的 png 路径（video 写 png 路径、crop 写满幅）。
2026-10-05 21:5x 用户定了封面大字 = “AI 工程师需要知道的 GPU 知识”，三个候选只剩画面不同：A 解码图的虚线框、B 文章封面里的 H100 手绘板、C H100 内部图。
  python make_cover_src.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
IMG = Path(r"D:\大疆\独立视频\素材\2026-10_AI工程师GPU指南\图片")
OUT = HERE / "_src"
OUT.mkdir(exist_ok=True)
ORANGE = (0xFF, 0x4F, 0x1A)


def hl(im, rect, pad=12, width=9):
    d = ImageDraw.Draw(im)
    x, y, w, h = rect
    d.rounded_rectangle([x - pad, y - pad, x + w + pad, y + h + pad], radius=16, outline=ORANGE, width=width)


# A：解码一步的存储器阶梯——右下角虚线框 “move the weights ~1.5 ms / do the math ~0.01 ms”
a = Image.open(IMG / "06_Decoding_step_by_step.jpg").convert("RGB")
hl(a, [1258, 796, 306, 208])
a.crop((110, 310, 1600, 1180)).save(OUT / "A_decode.png")

# B：文章封面图里的 H100 手绘板（the chip: does the math / memory: holds your model），去掉左边的英文标题
b = Image.open(IMG / "00_cover_cover.png").convert("RGB")                      # 1600×640
b.crop((700, 0, 1600, 560)).save(OUT / "B_board.png")                           # 900×560（1.61）；从 y=0 起，让 “the chip: does the math” 在黄贴纸下面

# C：H100 内部——3.35 TB/s 的细管子连着 80 GB 的显存（保留上面的标题 “Inside one GPU”，去掉底部那句话和署名，宽高比约 1.56）
c = Image.open(IMG / "03_Inside_GPU.png").convert("RGB")
hl(c, [516, 806, 300, 44])
hl(c, [494, 906, 616, 60])
c.crop((0, 24, 1600, 1048)).save(OUT / "C_inside.png")
print([p.name for p in OUT.glob("*.png")])
