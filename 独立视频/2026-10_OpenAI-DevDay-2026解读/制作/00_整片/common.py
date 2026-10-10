# -*- coding: utf-8 -*-
"""共用常量和读台本。流水线照《白宫超级智能协定》那条改的（build_timeline → prep_frames → mix_audio → render_all → qa_mix），
区别：一套脚本做 6 条短片，每条一个台本 台本/V?_*.json，产出放 out/<V?>/；画面只有一个来源（发布会视频），声音在另一个文件里。"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent            # 制作/00_整片
EP = HERE.parents[1]                              # 独立视频/2026-10_OpenAI-DevDay-2026解读
VOICE = HERE.parent / "02_配音"
SRC_VIDEO = EP / "素材" / "keynote_video_silent.mp4"     # 1920×1080，29.97 fps，没有声音
SRC_AUDIO = EP / "素材" / "keynote_audio.weba"           # 和视频同一起点，时长差 0.03 s
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
FPS = 30
SW, SH = 1636, 920                                # 抽帧的尺寸（最早演示区是 1636×920；2026-10-02 统一字幕标准后演示区缩到 1504×859、内容 1474×829 不缩放，浏览器里把这些帧缩小着显示，不用重抽）


def script_path(ep):
    hits = sorted((EP / "台本").glob(f"{ep}_*.json"))
    assert len(hits) == 1, f"台本/{ep}_*.json 找到 {len(hits)} 个"
    return hits[0]


def load_script(ep):
    return json.loads(script_path(ep).read_text(encoding="utf-8"))


def out_dir(ep):
    d = HERE / "out" / ep
    d.mkdir(parents=True, exist_ok=True)
    return d


def all_eps():
    return sorted({p.name.split("_")[0] for p in (EP / "台本").glob("V?_*.json")})
