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
XV = EP / "素材" / "X平台视频_ClaudeDevs"
E1 = Path(r"D:\大疆\Claude Code相关\01_Claude Code模组发布\素材\X平台视频_ClaudeDevs")        # 第 1 期下的三条官方视频（要回顾“模组示例”时用）
SRC = {
    "d1": XV / "ClaudeDevs_2106118517447876618.mp4",     # @ClaudeDevs 官方演示：You should know 插件（深色终端 + 缩放运镜），38.87 s，1920×1080，60 fps，AAC，有声（界面提示音）
    "m1": E1 / "ClaudeDevs_2105721434807083061.mp4",     # 第 1 期：三个官方示例模组连播（Token Weather → Blast Radius → Replay Theater，底部带英文说明条），71.77 s，30 fps，无声
}
AUDIO_SRC = {
}
HAS_AUDIO = {
    "d1": True,  "m1": False,
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
