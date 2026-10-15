# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # 短视频/NN_<短名>/
FPS = 30
SW, SH = 1474, 829                         # 素材框里的原生坐标（竖屏页面的素材框 1000×575，内边距 14，内容按 1474×829 写、显示时缩放 0.6594）
# 短视频不加悠一片头片尾（用户 2026-10-04），SRT 时间就是正片时间，没有偏移。

# ── 素材表：键是短名（plan.json 的 range 里写这个），值是视频文件。
XV = EP / "素材" / "视频"
SHARED = Path(r"D:\大疆\独立视频\素材\2026-10_image-blaster")     # 合集层共用素材（短、长视频都用，不放在本期目录里）
SRC = {
    # d1：image-blaster 的演示视频（X @liambraus 2026-10-03 的推文所附；720p 1280×720、126.7 s、h264 + aac；声音是演示者的英文讲解，同传段落里压低留着）
    "d1": SHARED / "liambraus_2106383261089849825_720p.mp4",
}
AUDIO_SRC = {
    # "k1": XV / "keynote_audio.weba",         # 画面和音频分开的素材：音频从这里取，时间和画面一致
}
HAS_AUDIO = {
    "d1": True,         # 演示者自己的英文讲解：同传段落里原声压低（曼波说话时 −9 dB）留着；自己的解说段落（range 里写 mute）不放
}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
