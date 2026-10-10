# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # <合集>/短视频/NN_<短名>/
MAT = EP.parents[1] / "素材"               # <合集>/素材/：素材放合集层，短、长视频共用（用户 2026-10-04：“素材可以公用”）
FPS = 30
SW, SH = 1474, 829                         # 素材框里的原生坐标（竖屏页面的素材框 1000×575，内边距 14，内容按 1474×829 写、显示时缩放 0.6594）
# 短视频不加悠一片头片尾（用户 2026-10-04），SRT 时间就是正片时间，没有偏移。

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。
# 这条是《如何使用Claude来低成本的生成视频》（Way to AGI 第 02 期，2026-09-28 发 B 站）的二次剪辑：素材就用长视频那期的工程文件，不重复拷、不挪。
LONG = Path(r"D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频")
SHOW = LONG / "教程_Claude做视频" / "素材"
SRC = {
    "face": LONG / "制作" / "02_出镜" / "edit" / "facecam.mp4",                          # 悠一出镜（和成片同一条时间轴，378.6 s），1280×720、30 fps、没有音轨
    "fin":  LONG / "制作" / "03_成片" / "如何使用Claude来低成本的生成视频_v2.mp4",         # B 站发的成片 2340×1080、383.4 s：只取右边演示窗口里的卡片（价格表、用量、像素代码…），crop 去掉出镜画框和烧进去的字幕
    "gin":  SHOW / "展示视频" / "03_银魂_像素风.mp4",                                      # Claude 做的银魂像素动画 1920×1080、30 fps、5:34（只有音乐音效）
    "nar":  SHOW / "展示视频" / "01_火影_像素风.mp4",                                      # 火影 1920×1080、24 fps、7:45
    "jojo": SHOW / "展示视频" / "02_JoJo第三部_像素风.mp4",                                # JoJo 第三部 1920×1080、24 fps、5:14
    "ep4":  Path(r"D:\大疆\AI科普\第04期_大模型从夯到拉\第04期_大模型从夯到拉_成片.mp4"),   # 《原LAI如此》第 4 期成片 2340×1080（Claude 做的，嘴型 / 配音 / 配色都是它自己查的）
}
AUDIO_SRC = {
}
HAS_AUDIO = {
    "face": False, "fin": False, "gin": False, "nar": False, "jojo": False, "ep4": False,   # 上框是悠一的脸（静音，AI 配音讲解）、下框永远静音；不用任何素材原声
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
