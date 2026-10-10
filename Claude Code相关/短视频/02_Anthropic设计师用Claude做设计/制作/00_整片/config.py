# -*- coding: utf-8 -*-
"""《Anthropic 设计师怎么用 Claude 做设计》的共用参数（画幅、版式、颜色、素材路径）。所有脚本从这里取数。

画幅 1080×2340（19.5:9，用户确认“尺寸对的”）、30 fps，米白底 #FAF9F5 + **技能 short-video 的背景印花（每条随机挑一张，见 make_bg.py / bg.json）**，强调橙 #FF4F1A、黄荧光 #FFD84D；不加悠一片头片尾。
版式 = 技能 short-video 的 dual（用户 2026-10-04 选定「版式 B + 边框 6」，layout.md）：
  0–250 留空（状态栏、平台顶部标签栏）→ 280–570 标题（随步骤变化的小标签 + 两行大字，整条一直在）→ 上框 680–1170 → 下框 1194–1684（860×490，x 110–970）
  → 字幕 1764–1876（中文 52 px + 英文 30 px，项目双语标准；用户 2026-10-04：“字幕放在屏幕底部偏上的位置”）→ 1950–2340 留空（平台的账号名 / 文案 / 音乐条）。
边框 6：7 px 黑描边 + 橙色硬阴影（右下偏移 14 px）+ 右上角黄色贴纸（文字 = 画面来源）；框里的画面 846×476（x264 要偶数高）。
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # 制作/00_整片
EP = HERE.parents[1]                                   # 本条目录
COLL = EP.parents[1]                                   # Claude Code相关
MAT = COLL / "素材" / "2026-10_Anthropic设计师_ClaudeDesign与Slides"
SRC = {"design": MAT / "Design_原片_视频流.webm", "slides": MAT / "Slides_原片_视频流.mp4"}
AUD = {"design": MAT / "Design_原片_音频流.weba", "slides": MAT / "Slides_原片_音频流.m4a"}
NATIVE = {"design": 2.0, "slides": 1.0}                # 1080p 画面坐标 → 原片像素（Design 是 4K）
SRC_FPS = 24
FONTS = HERE / "fonts"
VAR_FONT = FONTS / "NotoSansSC.ttf"                    # 变量字体（标题 900 / 800 / 700 字重）
WAY_SCRIPTS = Path(r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")     # bilingual_std.py（字幕标准的代码实现）
BUILD = HERE / "build"

W, H = 1080, 2340
FPS = 30
CRF_SCENE = 14
CRF_FINAL = 17

BOX_X, BOX_W, BOX_H = 110, 860, 490                    # dual 版式：两个 860×490 的框（x 110–970）
TOP_Y, BOT_Y = 680, 1194                               # 上框 680–1170，下框 1194–1684（间隔 24）
PAD = 7                                                # 边框 6：7 px 黑描边（框里的画面 846×476，16:9，偶数高）
INNER_W, INNER_H = BOX_W - 2 * PAD, BOX_H - 2 * PAD
RADIUS, INNER_RADIUS = 14, 4
SHADOW = 14                                            # 橙色硬阴影：右下偏移 14 px，无模糊
BAND_TOP = 1764                                        # 字幕带顶（dual：两框 → 字幕间距 80）：中文行高 66，英文从带顶往下 70 px，行高 40
ZH_PX, EN_PX = 52, 30
BG_LIB = Path(r"D:\大疆\短视频\skill\short-video\assets\backgrounds")     # 背景印花库（pattern_*.png，1080×2340 透明 PNG）：每条随机挑一张
ZH_CY, EN_CY = BAND_TOP + 33, BAND_TOP + 70 + 20
CX = W // 2

BG = (0xFA, 0xF9, 0xF5)
INK = (0x14, 0x14, 0x13)
GREY = (0x6B, 0x72, 0x80)
EN_GREY = (0x4B, 0x55, 0x63)
LINE = (0xE5, 0xE7, 0xEB)
ORANGE = (0xFF, 0x4F, 0x1A)
MARKER = (0xFF, 0xD8, 0x4D)
WHITE = (255, 255, 255)

# 同传时间
TTS_LAG = 0.40                 # 同传比英文开口晚 0.4 s（技能 short-video 的规矩）
TTS_GAP = 0.12                 # 两句同传之间至少空这么久
TTS_TAIL = 0.30                # 最后一句同传说完后画面再留这么久
