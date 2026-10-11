# -*- coding: utf-8 -*-
"""qa_subs.py —— 抽查烧进画面的字幕：每隔几条取一条的中间时刻，把画面底部 y 880–1080 一条条叠起来看（字有没有被切、挤、压在画面上）。
  python qa_subs.py [视频=整片_v2.mp4] [每几条取一条=6] [是否含片头秒数=0]
输出 _check\\subs_<k>.png
"""
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import make_subs  # noqa: E402
import ui  # noqa: E402


def main():
    video = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "整片_v2.mp4")
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    off = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    out = make_subs.build()
    pick = out[::step]
    crops = []
    for o in pick:
        t = (o["da"] + o["db"]) / 2 + off
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", str(video), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        c = im.crop((0, 860, im.width, im.height)).resize((1560, int(220 * 1560 / im.width)), Image.LANCZOS)
        ImageDraw.Draw(c).text((6, 4), "%.1f s  %s" % (t, o["zh"][:12]), font=ui.nsc(18), fill=(200, 0, 0))
        crops.append(c)
    per = 9
    for k in range(0, len(crops), per):
        grp = crops[k:k + per]
        sh = Image.new("RGB", (1560, sum(c.height + 4 for c in grp)), (60, 60, 60))
        y = 0
        for c in grp:
            sh.paste(c, (0, y))
            y += c.height + 4
        p = HERE / "_check" / ("subs_%d.png" % (k // per))
        sh.save(p)
        print(p)


main()
