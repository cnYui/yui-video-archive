# -*- coding: utf-8 -*-
"""成片核对：时长、帧数、响度，再从 mp4 里按时刻抽帧拼一张联系表（不是从页面截，是从编码后的视频里取）。

  python check_video.py 整片_v2.mp4 [秒 秒 …]   → stills/_check_<名字>.png
  不写秒数 = 每段开头 + 1.5 s 各一张，再加微信那段前后。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent


def main():
    mp4 = HERE / sys.argv[1]
    ts = [float(x) for x in sys.argv[2:]]
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    T = json.loads(s[s.index("{"): s.rindex("}") + 1])
    if not ts:
        ts = [round(g["s"] + 1.5, 2) for g in T["segs"]]
        cu = {q["id"]: q for q in T["cues"]}
        ts += [round(cu["C28"]["s"] + 0.5, 2), round(cu["C28"]["e"] - 0.3, 2), round(cu["V05"]["s"] + 1, 2)]
        ts.sort()
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames",
                         "-of", "json", str(mp4)], capture_output=True, text=True)
    info = json.loads(pr.stdout)
    print("时长", info["format"]["duration"], "页面总长", T["total"])
    for st in info["streams"]:
        print(" ", st)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    print("响度", re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1], "LUFS；真峰值", re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", err)[-1], "dBFS")
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 22)
    W, H, cols = 702, 324, 3
    tiles = []
    for t in ts:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                           capture_output=True)
        from io import BytesIO
        tiles.append((t, Image.open(BytesIO(p.stdout)).convert("RGB").resize((W, H), Image.LANCZOS)))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + 8) + 8, rows * (H + 36) + 8), "#C9CDD3")
    dr = ImageDraw.Draw(sheet)
    for j, (t, im) in enumerate(tiles):
        x, y = 8 + (j % cols) * (W + 8), 8 + (j // cols) * (H + 36)
        dr.text((x, y), f"{int(t // 60)}:{t % 60:05.2f}", fill="#111", font=font)
        sheet.paste(im, (x, y + 30))
    out = HERE / "stills" / f"_check_{mp4.stem}.png"
    sheet.save(out)
    print("联系表 ->", out)


if __name__ == "__main__":
    main()
