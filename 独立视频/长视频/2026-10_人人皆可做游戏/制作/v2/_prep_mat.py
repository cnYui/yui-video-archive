# -*- coding: utf-8 -*-
"""准备 K 页（媒介转换）要用的真实成品画面：v2/mat/*.png。只跑一次。"""
import subprocess
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
MAT = HERE / "mat"
MAT.mkdir(exist_ok=True)
ROOT = HERE.parent
REC = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-06_全流程实况\A_序章到第三章\full.webm")

# 1) UI 设计师长视频封面（16:9）
src = Path(r"D:\大疆\独立视频\长视频\2026-10_人人都是UI设计师\制作\04_封面\封面_选定_16x9.png")
Image.open(src).convert("RGB").save(MAT / "ui_cover.png")

# 2) 强化学习短视频的一帧（竖屏）
rl = Path(r"D:\大疆\独立视频\短视频\2026-10_强化学习赌场闯关\强化学习赌场闯关_成片.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "12", "-i", str(rl), "-frames:v", "1", str(MAT / "rl_frame.png")], check=True)

# 3) 官方课十集：5×2 缩略图墙
eps = sorted((ROOT / "素材").glob("ep*.png"))[:10]
cw, ch = 384, 216
wall = Image.new("RGB", (cw * 5 + 8 * 6, ch * 2 + 8 * 3), (30, 30, 36))
for i, p in enumerate(eps):
    im = Image.open(p).convert("RGB")
    s = max(cw / im.width, ch / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - cw) // 2, (im.height - ch) // 2
    wall.paste(im.crop((x0, y0, x0 + cw, y0 + ch)), (8 + (i % 5) * (cw + 8), 8 + (i // 5) * (ch + 8)))
wall.save(MAT / "courses_wall.png")

# 4) 游戏标题画面
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", str(REC), "-frames:v", "1", str(MAT / "game_title.png")], check=True)

# 5) 标题画面里的游戏 Logo（做结尾用）
logo = Path(r"D:\大疆\游戏素材\银魂\游戏\assets\ui\logo.png")
Image.open(logo).convert("RGBA").save(MAT / "logo.png")
print([p.name for p in sorted(MAT.glob("*.png"))])
