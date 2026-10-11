# -*- coding: utf-8 -*-
"""竖屏短视频的共用参数（画幅、版式、颜色、路径）。所有脚本从这里取数，改版式只改这里。

版式照技能 short-video（D:\\大疆\\短视频\\skill\\short-video\\references\\layout.md，用户 2026-10-04 定的竖屏）：
  画布 1080×2340、30 fps；白底（#FAF9F5 米白 + 淡点阵），强调色橙 #FF4F1A、黄荧光 #FFD84D；没有片头片尾、没有左栏目录、没有出镜框。
  0–250 留空（状态栏、抖音 / B 站顶部标签栏）→ 280–570 标题（kicker 小字 + 两行大字：黑 76 px、橙 60 px，一直在）→ 590–1165 上框 1000×575（人脸）
  → 1195–1305 字幕（中文 52 px + 英文 30 px，项目双语标准）→ 1325–1900 下框 1000×575（电脑操作）→ 1950–2340 留空（抖音的账号名 / 文案 / 音乐条）。
  外框白底 + 14 px 内边距 + 1 px 边 + 18 px 圆角 + 阴影，里面是 972×547 的 16:9 画面。右边 x ≥ 940、y 1170–1990 是抖音的点赞 / 评论按钮：字幕居中、左右留 ≥ 70 px。
画面片段从 4K 原片里按“裁切框 + 变速”切出来（裁切框写在 shots.json，16:9，用 [中心x, 中心y, 宽] 表示，坐标按 1920×1080 画面算）。
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
MAT = EP.parents[1] / "素材" / "2026-10_ClaudeDesign设计师用法"   # 合集层素材（2026-10-04 用户：素材放合集层、短长视频共用；本条从顶层 短视频\ 挪进 Claude Code相关\短视频\）
SRC_4K = MAT / "原片_视频流.webm"
SRC_PROXY = HERE / "proxy_1080.mp4"
FONTS = HERE / "fonts"
WAY_SCRIPTS = Path(r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")     # bilingual_std.py（字幕标准的代码实现）
VAR_FONT = Path(r"D:\大疆\独立视频\2026-10_ClaudeSlides设计师用法\制作\00_整片\fonts\NotoSansSC.ttf")   # 变量字体（标题要 900 / 800 / 700 字重）

W, H = 1080, 2340
FPS = 30
CRF_CLIP = 12                  # 中间片段（小，几乎无损）
CRF_FINAL = 17

# 版式
BOX_X, BOX_W, BOX_H = 40, 1000, 575
FACE_Y = 590                               # 上框：人脸
SCREEN_Y = 1325                            # 下框：电脑操作
PAD = 14                                   # 外框内边距
INNER_W, INNER_H = BOX_W - 2 * PAD, 546                      # 972 × 546（≈ 16:9；x264 要偶数高，CSS 里的 547 取 546，下沿多 1 px 白边看不出来）
RADIUS, INNER_RADIUS = 18, 8
BAND_TOP = 1195                            # 字幕带顶（中文行高 66；英文从带顶往下 70 px，行高 40 → 带底 1305）
ZH_PX, EN_PX = 52, 30
ZH_CY, EN_CY = BAND_TOP + 33, BAND_TOP + 70 + 20
CX = W // 2

# 颜色（技能引擎 index.html 的 :root）
BG = (0xFA, 0xF9, 0xF5)
INK = (0x14, 0x14, 0x13)
INK2 = (0x37, 0x41, 0x51)
GREY = (0x6B, 0x72, 0x80)
EN_GREY = (0x4B, 0x55, 0x63)
LINE = (0xE5, 0xE7, 0xEB)
ORANGE = (0xFF, 0x4F, 0x1A)
MARKER = (0xFF, 0xD8, 0x4D)
WHITE = (255, 255, 255)

# 时间线
LEAD_FIRST = 0.10               # 第一句配音比画面晚 0.10 s 开口（第一帧就是钩子）
LEAD = 0.05                     # 其余各句：画面先切 0.05 s，配音再开口
GAP = 0.07                      # 句尾到下一次画面切之间（再加 LEAD = 句间 0.12 s）
HOLD_END = 0.8                  # 最后一句念完后画面再停多久（技能规定金句说完 0.8 s 结束）
