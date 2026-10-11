# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds   # noqa: E402  共用片头片尾的时长（读 intro / outro 页面里的 window.DURATION）

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # 独立视频/长视频/2026-10_不再Review/
MAT = EP.parents[1] / "素材" / "2026-10_不再Review"        # 独立视频/素材/2026-10_不再Review/（短、长视频共用的素材）
FPS = 30
SW, SH = 1474, 829                         # 演示区的原生坐标（页面里的演示区 1504×859，内边距 14，内容不缩放；为了让出 y 922 以下的中英字幕带）
INTRO_SEC = intro_seconds()                # 悠一片头（2026-10-03 起 4.8 s）；SRT / 章节的时间要加上它（成片 = 片头 + 正片 + 片尾，都必加）

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。
SRC = {
    # iv = Matt Pocock 的 YouTube 直播访谈（Matt × Lauren Tan / poteto，2026-10 初，1:05:36，1920×1080 30 fps，AAC 128 kbps；说话的人名牌在画面左下角）
    "iv": MAT / "YouTube直播_MattPocock×poteto" / "MattPocock_poteto_直播_MN9dGgmLyso.mp4",
    # tk = Lauren Tan 在 X 上发的 38 分钟演讲（tldraw 幻灯片 + 她的头像框 + 英文字幕条，1720×1080 60 fps）：只当画外音段的幻灯片素材用（crop 裁出幻灯片本身，静音）
    "tk": MAT / "X推文" / "poteto_演讲视频_2102050467505430555" / "poteto_2102050467505430555.mp4",
}
AUDIO_SRC = {}
HAS_AUDIO = {
    "iv": True,     # 访谈原声：同传段压低垫底（−29 LUFS）、画外音段 mute
    "tk": True,     # 演讲原声：全部 mute，不进成片
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
