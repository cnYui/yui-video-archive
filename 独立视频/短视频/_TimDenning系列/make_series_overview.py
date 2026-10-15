# -*- coding: utf-8 -*-
"""交付包的总览图：6 期各取一个比例拼成一张（默认每期的候选 A / B / C 的 3:4 三张并排，6 行），方便用户一眼选封面。

  python make_series_overview.py            → 系列目录下 六期封面总览_3x4.png（每行一期：A B C）
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402

FONT = Path(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf")
TW, TH = 330, 440                       # 每张 3:4 缩略图
rows = []
for ep in D.EPISODES:
    d = ep_dir(ep) / "制作" / "04_封面"
    ims = [Image.open(d / f"候选{k}_3x4.png").convert("RGB").resize((TW, TH), Image.LANCZOS) for k in "AB"]
    rows.append((ep, ims))
W, H = 40 + 2 * (TW + 14) + 150, 20 + len(rows) * (TH + 54)
sheet = Image.new("RGB", (W, H), (232, 232, 232))
dr = ImageDraw.Draw(sheet)
f = ImageFont.truetype(str(FONT), 26)
for i, (ep, ims) in enumerate(rows):
    y = 20 + i * (TH + 54)
    dr.text((20, y), f"第 {ep['num']} 期 · {ep['name'].split('_', 1)[1]}    A 整张配图铺满 / B 紧裁到脸", font=f, fill=(20, 20, 19))
    for j, im in enumerate(ims):
        sheet.paste(im, (20 + j * (TW + 14), y + 40))
out = HERE / "六期封面总览_3x4.png"
sheet.save(out)
print(out, sheet.size)
