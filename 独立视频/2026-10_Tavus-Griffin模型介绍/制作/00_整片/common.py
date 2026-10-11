# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO / SRC_CROP）。**"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # 独立视频/2026-10_Tavus-Griffin模型介绍/
FPS = 30
SW, SH = 1474, 829                         # 演示区的原生坐标（页面里的演示区 1508×863，边框 3 + 内边距 14，内容不缩放；为了让出 y 922 以下的中英字幕带）
INTRO_SEC = 3.8                            # 悠一片头；SRT 的时间要加上它（成片 = 片头 + 正片 + 片尾）

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。素材全部是 @tavus 官方账号在 X 上发的视频（TwitterSaver 同一个源 video.twimg.com，1080p）。
XV = EP / "素材" / "X平台视频"
SRC = {
    "gr": XV / "tavus_2105704169009246248.mp4",    # Griffin 发布视频：@tavus 2026-10-01，1920×1080，108.6 s，有声（Hassaan 和 Vanessa 的视频通话对白 + 配乐），片尾 8 s 是黑底 TAVUS logo
    "el": XV / "tavus_2104998304279048334.mp4",    # Elevare 客户案例：@tavus 2026-09-29，1920×1080（X 上有 4K 版，演示区 1474 宽用不上），181.8 s，有声（访谈）
    "me": XV / "tavus_2100277005841469469.mp4",    # Memories 介绍：@tavus 2026-09-16（被 2026-09-18 那条引用），1920×1080，91.6 s，有声（Elisa Ding 解说）
}
AUDIO_SRC = {}
HAS_AUDIO = {"gr": True, "el": True, "me": True}

# 三个视频都自带英文烧录字幕（y 985–1040，底部）；我们有自己的中英双语字幕带，所以统一裁掉底部到 y=975，再按 16:9 左右各裁 4.87%（[x0, y0, x1, y1] 占整帧的比例）。
SRC_CROP = {k: [0.0487, 0.0, 0.9513, 0.9028] for k in SRC}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
