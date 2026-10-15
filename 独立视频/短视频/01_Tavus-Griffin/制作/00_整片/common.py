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
LONG = Path(r"D:\大疆\独立视频\2026-10_Tavus-Griffin模型介绍")     # 这条是它的二次剪辑：素材就用长视频那期下好的（不重复下、不挪），说明见 独立视频\素材\2026-10_Tavus-Griffin\来源.md
XV = LONG / "素材" / "X平台视频"
PAGES_SRC = LONG / "素材" / "官网截图"       # 官网各小节的高清截图（make_pages.py 裁成页面录屏用的图）
SRC = {
    "gr": XV / "tavus_2105704169009246248.mp4",   # @tavus 2026-10-01 的 Griffin 发布视频：108.6 s、1920×1080、23.976 fps、h264 + aac；Hassaan（CEO）× Vanessa（AI）视频通话演示，画面里烧着 Tavus 自己的英文字幕（下面裁掉）
}
AUDIO_SRC = {
}
HAS_AUDIO = {
    "gr": True,    # 有声（Vanessa / Hassaan 的原话）：只有同传那几段不写 mute，其余段 mute
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
