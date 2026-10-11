# -*- coding: utf-8 -*-
r"""画面 × 旁白对照表：每隔 STEP 秒从成片抽一帧（只裁上下两个框），下面写当时在讲的那句，用来检查幻灯片高亮 / 页面状态有没有和旁白错位。

  python qa_sheet.py 10            第 10 期 → <scratchpad>\qa_10_*.png（每张 16 格）
  python qa_sheet.py 9 10 --step 1.5 --out D:\某目录

读 制作\00_整片\timeline.json 的 cues（句子起止）和 segs；成片取 <slug>_成片.mp4。
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT  # noqa: E402

FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
SCRATCH = Path(r"C:\Users\yui\AppData\Local\Temp\claude\D----\0ca7ab01-5e32-4422-ab13-ad2f1adafd32\scratchpad")


def main():
    args = sys.argv[1:]
    step = 2.0
    out = SCRATCH
    nums = []
    i = 0
    while i < len(args):
        if args[i] == "--step":
            step = float(args[i + 1]); i += 2
        elif args[i] == "--out":
            out = Path(args[i + 1]); i += 2
        else:
            nums.append(int(args[i])); i += 1
    out.mkdir(parents=True, exist_ok=True)
    f_cap = ImageFont.truetype(FONT, 17)
    f_small = ImageFont.truetype(FONT, 14)
    for n in nums:
        d = EPISODES[n]
        ep = EP_ROOT / d["folder"]
        mp4 = ep / f"{d['slug']}_成片.mp4"
        tl = json.loads((ep / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
        tmp = out / f"_qa{n}_{step}"                 # 每个步长一个目录：重跑同一步长时同名帧直接覆盖
        tmp.mkdir(exist_ok=True)
        every = max(1, round(step * 30))             # 成片 30 fps：按帧号精确取（fps 滤镜会取取整窗口里最后一帧，标的时间会晚约 1 s）
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf", f"select='not(mod(n,{every}))',crop=1080:1060:0:660,scale=250:-1", "-fps_mode", "vfr",
                        str(tmp / "f_%03d.png")], check=True)
        frames = sorted(tmp.glob("f_*.png"))
        tiles = []
        for k, p in enumerate(frames):
            t = k * step
            im = Image.open(p).convert("RGB")
            cue = next((q for q in tl["cues"] if q["s"] - 0.05 <= t < q["e"] + 0.2), None)
            cap = Image.new("RGB", (im.width, 74), "white")
            dr = ImageDraw.Draw(cap)
            dr.text((2, 0), f"{t:.1f}s {cue['id'] if cue else '-'}", fill="black", font=f_cap)
            txt = cue["zh"] if cue else ""
            for r in range(3):
                dr.text((2, 20 + r * 17), txt[r * 17:(r + 1) * 17], fill=(60, 60, 60), font=f_small)
            tile = Image.new("RGB", (im.width, im.height + cap.height), "white")
            tile.paste(im, (0, 0)); tile.paste(cap, (0, im.height))
            tiles.append(tile)
        per = 16
        for si in range(0, len(tiles), per):
            chunk = tiles[si:si + per]
            w, h = chunk[0].size
            cols = 8
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * h), "white")
            for k, tl_ in enumerate(chunk):
                sheet.paste(tl_, ((k % cols) * w, (k // cols) * h))
            fn = out / f"qa_{n:02d}_{si // per + 1}.png"
            sheet.save(fn)
            print(fn, sheet.size)


if __name__ == "__main__":
    main()
