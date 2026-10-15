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
XV = MAT / "2026-10_text-to-cad"               # 这条用的素材子目录（合集层 素材\ 下按主题分，里面放 README / 来源.md）
SRC = {
    "a": XV / "earthtojake_2106120308037947785.mp4",   # @earthtojake 2026-10-02 20:33 UTC 的推文：Codex 桌面 App 里的 text-to-cad（九缸星型发动机爆炸图、"make the propeller twice as long"），3384×2160，28.3 s，无音轨
    "b": XV / "earthtojake_2081826428295729284.mp4",   # @earthtojake 2026-07-27 19:37 UTC 的推文（仓库破 1 万 star）：Claude Code 里的 text-to-cad 查看器（Juno 人形机器人、灵巧手、剪刀升降台、机械臂），1920×1080，42.1 s，无音轨
}
AUDIO_SRC = {}
HAS_AUDIO = {"a": False, "b": False}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
