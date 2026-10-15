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
XV = MAT / "<YYYY-MM_主题>"               # 这条用的素材子目录（合集层 素材\ 下按主题分，里面放 README / 来源.md）
SRC = {
    # "d1": XV / "<来源>_<编号>.mp4",            # 一行写清：谁的、什么内容、规格、有没有声（fetch_x_video.py 下的 X 视频叫 <账号>_<推文ID>.mp4）
    # "m1": Path(r"D:\大疆\Claude Code相关\03_YouShouldKnow插件\素材\X平台视频_ClaudeDevs\ClaudeDevs_2106118517447876618.mp4"),   # 别的合集里下过的素材直接引用，不重复下
}
AUDIO_SRC = {
    # "k1": XV / "keynote_audio.weba",         # 画面和音频分开的素材：音频从这里取，时间和画面一致
}
HAS_AUDIO = {
    # "d1": True,  "m1": False,   有声的写 True；静音 / 没有音轨的写 False（不然 mix_audio 会把静音当素材原声去拉增益）。官方演示的音轨多半是界面提示音，不是人声（whisper 听不出话）
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
