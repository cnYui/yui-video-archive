# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio 共用的路径和素材表。"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # 独立视频/2026-10_ClaudeFable5.5模型介绍/
FPS = 30
SW, SH = 1636, 920                         # 演示区实际像素（页面里按 1474×829 写，整体 scale 1.1099）
CL = EP / "素材" / "X平台视频_chetaslua"
SRC = {
    "c1": CL / "chetaslua_2105792187200147541.mp4",   # Fable 5.5：HEAD CASES: HEROES（24 个英雄头像），1920×1080，有声
    "c2": CL / "chetaslua_2105757136219504862.mp4",   # Fable 5.5：SUPERMAN 3000 BC → 2020s（20 种画风），1920×1080，有声
    "c3": CL / "chetaslua_2101376238703333883.mp4",   # Fable 5.2：HEAD CASES（会动的小脸），2940×1600，无声
    "c4": CL / "chetaslua_2105674430924103789.mp4",   # Opus 5.5：同一只小生物的 20 种画法，2940×1492，无声
}
HAS_AUDIO = {"c1": True, "c2": True, "c3": False, "c4": False}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
