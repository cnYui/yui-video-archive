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
XV = MAT / "2026-10_MuseGadgets开源"               # 这条用的素材子目录（合集层 素材\ 下按主题分，里面放 README / 来源.md）
SRC = {
    "a1": XV / "AYi_AInotes_2106239579938238880.mp4",                 # @AYi_AInotes 的 X 帖附的 15 s 动画（1088×832、有配乐无人声）：官网首页 + 设备逐个亮起 + 连线；不是 Meta 官方视频，角标写 “@AYi_AInotes · X”
    "c1": XV / "官网与仓库" / "cards_carousel.mp4",                      # gadgets.muse.ai「Project Ideas」8 张卡片的横向滚动（cap_cards.py 截的真实页面 + make_cards_clip.py 离线滚动 / 高亮框，静音）
    "w1": XV / "官网与仓库" / "homelink_widget.mp4",                     # 官网 Home Link 组件三个页签：Device 转台 → What's inside → Connection（静音，13.8 s）
    "w2": XV / "官网与仓库" / "homelink_conn_hl.mp4",                    # 收尾：Connection 连线图 + 橙框“Meta 的云”（make_conn_clip.py，静音）
}
AUDIO_SRC = {
    # "k1": XV / "keynote_audio.weba",         # 画面和音频分开的素材：音频从这里取，时间和画面一致
}
HAS_AUDIO = {
    "a1": False,      # 有音轨但只是配乐 / 音效，不要（成片另配 BGM）
    "c1": False, "w1": False, "w2": False,
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
