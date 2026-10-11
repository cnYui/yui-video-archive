# -*- coding: utf-8 -*-
"""检查每个发布会片段的入点画面：每段取 4 帧（开头、1/3、2/3、结尾前）拼联系表，标上段号和原片时间。

  python check_in_points.py V1 [V2 …]      → out/<V?>/stills/_inpoints.png
"""
import json
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

from common import SRC_VIDEO, out_dir

W, H = 384, 216


def main():
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 20)
    for ep in sys.argv[1:]:
        od = out_dir(ep)
        T = json.loads((od / "timeline.json").read_text(encoding="utf-8"))
        (od / "stills").mkdir(exist_ok=True)
        tiles = []
        for cid, c in T["clips"].items():
            d = c["out"] - c["in"]
            for k, f in enumerate((0.03, 0.33, 0.66, 0.97)):
                t = c["in"] + d * f
                p = od / "stills" / f"_ip_{cid}_{k}.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(SRC_VIDEO), "-frames:v", "1", "-vf", f"scale={W}:{H}", "-q:v", "4", str(p)], check=True)
                tiles.append((f"{cid} {t:.1f}s ({c['mode']})", p))
        cols = 4
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (W + 6) + 6, rows * (H + 30) + 6), "#222")
        dr = ImageDraw.Draw(sheet)
        for i, (label, p) in enumerate(tiles):
            x, y = 6 + (i % cols) * (W + 6), 6 + (i // cols) * (H + 30)
            dr.text((x + 2, y + 2), label, fill="#FFD84D", font=font)
            sheet.paste(Image.open(p), (x, y + 28))
            p.unlink()
        out = od / "stills" / "_inpoints.png"
        sheet.save(out)
        print(out, len(tiles), "帧")


if __name__ == "__main__":
    main()
