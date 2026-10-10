# -*- coding: utf-8 -*-
"""build_timeline / prep_frames / mix_audio / finish 共用的路径和素材表。**每期只改这个文件里的素材表（SRC / AUDIO_SRC / HAS_AUDIO）。**
本条：《Claude官方教程》第 1 期出镜版（版式 = 标题 + 中间 1 / 2 / 大窗口 + 最下面悠一出镜位，见 ../../台本/README.md）。"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]                       # <合集>/短视频/NN_<短名>/
MAT = EP.parents[1] / "素材"               # <合集>/素材/：素材放合集层，短、长视频共用（用户 2026-10-04：“素材可以公用”）
FPS = 30
NATURAL_TIMING = True                      # True = 用户自己录的口播：不按句切块、不加句间停顿，字幕 / 画面 / 音频的时间和他的原片一致（现在还没录，用估时；录完用 own_voice.py 换成真时间）
SW, SH = 1474, 829                         # 单窗 / 双窗的内容坐标；大窗（BIG）是 1474×1725，见 prep_frames.py / engine.js
# 短视频不加悠一片头片尾（用户 2026-10-04），SRT 时间就是正片时间，没有偏移。

XV = MAT / "2026-10_Claude官方教程_出镜版"   # 悠一的录屏放这里
CA = MAT / "2026-10_ClaudeAcademy" / "视频"  # Claude Academy 官方课视频（README 有来源和挂名）
SRC = {
    "rec": XV / "录屏_来源演示_Recording_2026_10_6_13_10_31.mp4",   # 悠一 2026-10-06 录的：Anthropic 官网 → Learn → Claude Academy，13.03 s，1822×1080，60 fps
    "c1": CA / "CC101-01_what-is-claude-code__fl1DSmwQKKY.mp4",      # 官方课 Claude Code 101 第 1 课（1080p；只用屏幕 / 动画镜头，不用讲师的脸）
    "c2": CA / "CC101-02_how-claude-code-works__6bs5b4FltCU.mp4",
    "c3": CA / "CC101-03_installing-claude-code__0kILa02vKuI.mp4",
    "c4": CA / "CC101-04_your-first-prompt__gbetp6D7J_Q.mp4",
    "c6": CA / "CC101-06_context-management__eW3oTyfeWZ0.mp4",
    "c8": CA / "CC101-08_claude-md-file__O0FGCxkHM-U.mp4",
    "p4": CA / "CCA-04_permission-modes__IS6larFJBK8.mp4",
    "perm": XV / "录屏_五种权限_Recording_2026_10_6_15_53_59.mp4",    # 悠一 2026-10-06 录的：Claude 桌面应用里的五种权限（自动 / 手动 / 接受编辑 / 计划 / 跳过权限确认）+ “绕过所有权限？”确认框，9.9 s，1666×1080；侧栏里有会话名和别人的名字，用的时候一定要 crop 掉左边
}
AUDIO_SRC = {}
HAS_AUDIO = {k: False for k in SRC}       # 这条没有任何素材原声：成片静音（悠一之后单独露脸 + 配音）


def src_duration(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(SRC[key])],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_tl():
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"): s.rindex("}") + 1])
