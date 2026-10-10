# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**

本条（《人人都是 UI 设计师》竖屏短视频）没有视频素材：画面全是静态图——20 张前后对比图（共用素材目录，绝对路径引用，不拷进本条）
+ 长视频截好的推文 / 书官网页面图（拷了 3 张进 media/pages/，来源见 build_panels.py）。所以 SRC / HAS_AUDIO 是空的，prep_frames.py 不抽帧。
"""
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

# ── 本条的素材（绝对路径；Windows 路径一律用 raw string / Path，别写 "\2026" 这类会被当转义的字面量）
MAT_UI = MAT / "2026-10_人人都是UI设计师"              # 共用素材：文章全文 + 20 张对比图原图
IMG_DIR = MAT_UI / "图片"                              # 图00_封面.jpg、图01…图20_*.jpg（左半 = 错误做法、右半 = 正确做法；图 13 上下两层）
LONG = EP.parents[1] / "长视频" / "2026-10_人人都是UI设计师"   # 长视频目录：**只读**（标注 marks、规则元数据、页面截图）；EP.parents[1] = 独立视频

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。本条没有视频素材。
XV = MAT_UI
SRC = {
}
AUDIO_SRC = {
}
HAS_AUDIO = {
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
