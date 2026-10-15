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
XV = MAT / "2026-10_不再Review"           # 这条用的素材子目录（合集层 素材\ 下按主题分，里面放 README / 来源.md）；长视频《不再Review》也用这个目录
SRC = {
    # iv = Matt Pocock 的 YouTube 直播访谈（Matt × Lauren Tan / poteto，2026-10-02，1:05:36，1920×1080 30 fps）：左半是 Matt、右半是 Lauren（两个 960×1080 的人像格并排），名牌在各自格子左下角；上框用它（crop 裁出单人，静音）
    "iv": XV / "YouTube直播_MattPocock×poteto" / "MattPocock_poteto_直播_MN9dGgmLyso.mp4",
    # tk = Lauren Tan 在 X 上发的 38 分钟演讲（tldraw 幻灯片 + 头像框 + 英文字幕条，1720×1080 60 fps）：下框放幻灯片（crop 裁出幻灯片本身、纯色补边，静音）
    "tk": XV / "X推文" / "poteto_演讲视频_2102050467505430555" / "poteto_2102050467505430555.mp4",
}
AUDIO_SRC = {
    # "k1": XV / "keynote_audio.weba",         # 画面和音频分开的素材：音频从这里取，时间和画面一致
}
HAS_AUDIO = {
    "iv": False,    # 画面全部静音（重新用温柔男生讲，不留原声）
    "tk": False,
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
