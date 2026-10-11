# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds   # noqa: E402  共用片头片尾的时长（读 intro / outro 页面里的 window.DURATION）

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # <合集>/NN_<标题>/
FPS = 30
SW, SH = 1474, 829                         # 演示区的原生坐标（页面里的演示区 1504×859，内边距 14，内容不缩放；为了让出 y 922 以下的中英字幕带）
INTRO_SEC = intro_seconds()                # 悠一片头（2026-10-03 起 4.8 s）；SRT / 章节的时间要加上它（成片 = 片头 + 正片 + 片尾，都必加）

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。
MAT = Path(r"D:\大疆\独立视频\素材\2026-10_人人都是UI设计师")      # 共用素材（图片 / 文章），短、长视频共用，不放进 长视频\ 里
XV = None
SRC = {
    # "d1": XV / "ClaudeDevs_<推文ID>.mp4",     # 一行写清：谁的、什么内容、规格、有没有声（fetch_x_video.py 下载的文件名就是这个格式）
    # "m1": Path(r"D:\大疆\Claude Code相关\01_Claude Code模组发布\素材\X平台视频_ClaudeDevs\ClaudeDevs_2105721434807083061.mp4"),   # 上一期的素材（要回顾时用）
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
