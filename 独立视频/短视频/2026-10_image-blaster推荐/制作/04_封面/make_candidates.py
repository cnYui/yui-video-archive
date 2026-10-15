# -*- coding: utf-8 -*-
"""image-blaster 推荐的封面候选：用技能 short-video 的 make_cover.py 出三个候选，每个三个比例，再拼一张总览给用户选。

  python make_candidates.py

画面取自作者 @neilsonks 原帖（2560×1440 版本）的几帧，存成 _src_*.png：
  cabin   原帖 7.0 s：小木屋 3D 场景，右下角小图 = 输入的那张图（“一张图 → 世界”最直观的一帧）
  village 原帖 61.6 s：意大利小巷的 3D 场景（椅子、盆栽、邮筒都是单独生成的物件）
  library 原帖 103.0 s：旧图书室，右下角同样有输入图
候选：
  A  shot  cabin + 箭头指向右下角的输入图，大字「一张图 / 变3D世界」
  B  shot  village + 箭头指向盆栽，大字「5000星 / Claude技能」（GitHub 推荐的社交证明钩子）
  C  split 白底分栏 library，大字「一张图 / 变3D世界」
封面协定：大字简短（每行 ≤ 6 字）、不放最下面那行小字、主角放大；平台标题写详细，和封面不写同一句。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
TOOL = Path(r"D:\大疆\短视频\skill\short-video\scripts\make_cover.py")
FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
RATIOS = ("3x4", "16x9", "4x3")

CANDS = {
    "A": dict(image="_src_cabin_crop.png", big=["一张图", "变3D世界"], accent_line=1, target=[0.72, 0.72], style="shot", note="真实画面 + 箭头指输入图"),
    "B": dict(image="_src_village.png", big=["5000星", "Claude技能"], accent_line=0, target=[0.70, 0.40], style="shot", note="真实画面 + 箭头指盆栽（5000 星钩子）"),
    "C": dict(image="_src_library.png", big=["一张图", "变3D世界"], accent_line=1, style="split", note="白底分栏"),
}


def main():
    # 源图：cabin 取右 75% 宽（和 4:3 同比例），让右下角的输入图在三个比例里都尽量完整
    im = Image.open(HERE / "_src_cabin.png")
    im.crop((int(im.width * 0.25), 0, im.width, im.height)).save(HERE / "_src_cabin_crop.png")
    for name, c in CANDS.items():
        cfg = {k: v for k, v in c.items() if k != "note"}
        (HERE / "cover.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        subprocess.run([sys.executable, str(TOOL), str(EP)], check=True)
        for r in RATIOS:
            shutil.copy2(HERE / f"cover_{r}.png", HERE / f"候选{name}_{r}.png")
    # 总览：每行一个候选，三个比例并排
    big, small = ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 26)
    H = 420
    rows = []
    for name, c in CANDS.items():
        ims = [Image.open(HERE / f"候选{name}_{r}.png").convert("RGB") for r in RATIOS]
        ims = [i.resize((int(i.width * H / i.height), H), Image.LANCZOS) for i in ims]
        rows.append((name, c["note"], ims))
    W = max(sum(i.width for i in r[2]) + 40 * (len(r[2]) + 1) for r in rows)
    sheet = Image.new("RGB", (W, len(rows) * (H + 110) + 30), "#F1F2F5")
    d = ImageDraw.Draw(sheet)
    y = 20
    for name, note, ims in rows:
        d.text((40, y), f"候选 {name} · {note}", fill="#141413", font=big)
        x = 40
        for i in ims:
            sheet.paste(i, (x, y + 70))
            x += i.width + 40
        y += H + 110
    sheet.save(HERE / "候选总览.png")
    print("ok", sheet.size)


if __name__ == "__main__":
    main()
