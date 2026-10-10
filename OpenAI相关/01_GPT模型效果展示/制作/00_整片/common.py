# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio 共用的路径和素材表。"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # OpenAI相关/01_GPT模型效果展示/
FPS = 30
SW, SH = 1636, 920                         # 演示区实际像素（页面里按 1474×829 写，整体 scale 1.1099）
XV = EP / "素材" / "X平台视频"
KN = Path(r"D:\大疆\独立视频\2026-10_OpenAI-DevDay-2026解读\素材")     # DevDay 主题演讲：无声画面 + 单独的音频，同一起点
SRC = {
    "g1": XV / "higgsfield_ai_2105012668348383325.mp4",   # Higgsfield：Sol（上）vs Astra（下）做 3D 游戏原型，2244×2160，60 s，有声（音乐 / 游戏音效）
    "g2": XV / "LuminaBench_2104995514433564800.mp4",     # LuminaBench：四个模型做 3D 斗兽场，1920×1400，12.8 s，无音轨
    "g3": XV / "chetanankola_2105207149869814091.mp4",    # chetanankola：爱琴海（Three.js），2902×2160，31.2 s，无音轨
    "g4": XV / "ishuagra02_2105060021599871162.mp4",      # ishuagra02：Sol 做的 3D 秋天，1920×1080，29.1 s，音轨是静音
    "p1": XV / "abhinavflac_2105117731440005249.mp4",     # abhinavflac：猕猴桃果冻，Sol Max（上）vs Astra Max（下），1080×1200，30.9 s，音轨是静音
    "p2": XV / "R_ChajX_2103098256066523405.mp4",         # R_ChajX：Astra 做的人体图谱（2,234 个 3D 部件），3840×2096，38.7 s，有声
    "p3": XV / "abstrakt314_2105756028935504032.mp4",     # abstrakt314：高斯泼溅的 dots，1080×1080，11.5 s，音轨是静音
    "m1": XV / "magnific_2105003172385497114.mp4",        # magnific：dots × Magnific，1920×1080，14.1 s，有声（音乐）
    "e1": XV / "SamGCoder_2105822535212581210.mp4",       # SamGCoder：Clearwater，从太空到海面，2560×1392，202.4 s，音轨是静音
    "k1": KN / "keynote_video_silent.mp4",                # OpenAI DevDay 2026 主题演讲（官方），1920×1080，3214 s，无声
}
AUDIO_SRC = {"k1": KN / "keynote_audio.weba"}             # 画面和音频分开的素材：音频从这里取，时间和画面一致
HAS_AUDIO = {"g1": True, "g2": False, "g3": False, "g4": False, "p1": False, "p2": True, "p3": False, "m1": True, "e1": False, "k1": True}


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
