# -*- coding: utf-8 -*-
r"""出镜版（悠一露脸 + 他自己的原声）——字幕 = 他实际说的话（talk_lines.py），画面 = 每个场景的窗口模式 + 素材选段。
（骨架。第 1 期真实的 45 个场景在 assets/oncam-multiclip/example_ep1/script_data.py，照那个格式写。）

  python scripts/gen_ep.py <本条目录> --timing 制作/01_口播/timing.json     台本 + 选段 + 母带上每句的真时间 → 录制稿.json / plan.json / tts_edit.json / 实际口播稿_字幕版.md

LINES   = talk_lines.LINES：zh 字幕、en 英文字幕（照他说的，只改听错的专名 / 同音字）。
SCENES  = 每个场景：mode（one 单窗 / two 双窗上下叠 / big 大窗 = 两个窗口合并那么大，看清文字用）、lines（这个场景讲的字幕行 id）、
          kind（clip = 官方素材 / 录屏镜头，card = 自己画的说明卡，画在 制作/00_整片/scenes_ep.js）、
          top / bottom = 窗口里放的素材选段 [S(src, a, b, w, speed, crop) / H(src, a, w)]（w = 这一段占场景的相对时长；H = 定格 a 那一帧），credit = 窗口右上角的黄贴纸（来源）。
出镜小窗（技能固定规则）：单窗场景居中在字幕下面，双窗 / 大窗缩到左下角 —— 所以大窗里的说明卡内容都放在 y ≤ 1330、左下角（x < 320 且 y > 1335）留空。
画面规则：只用官方素材里的屏幕 / 动画镜头，**不放讲师的脸**（渲前 scripts/scan_faces.py 扫一遍）；官方视频都挂 credit；他自己的录屏挂“悠一 · 录屏”。
选段只能用已经核过的安全段；别凭 3 秒一帧的联系表推断“这一段都是屏幕”（第 1 期推断错了 4 处）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import talk_lines as TLN  # noqa: E402

TITLE = {
    "slug": "短名_出镜版",                                  # 成片 / 字幕文件名前缀
    "title": "内部标题（不是平台标题）",
    "kicker": "<b>系列名</b> 第N期",
    "hook": ["第一行 ≤ 12 字", "第二行 ≤ 15 字"],            # 顶上两行字，每一帧都在：第一次发静帧 / 交付包里单独给用户看一眼（第 1 期成片发出去才被指出写错，整片重渲）
}

LINES = [{"id": l[0], "zh": l[4], "say": l[4], "en": l[5]} for l in TLN.LINES]
T = lambda a, b: [f"T{i:02d}" for i in range(a, b + 1)]          # T(1, 5) → T01…T05

# 素材短名（common.py 的 SRC 里是同一套）→ 中文名（gen_ep.py 写口播稿的“画面”行用）
LABEL = {"c1": "官方课第1课", "rec": "悠一的录屏"}
C1 = "官方课 · 第1课"
S = lambda src, a, b, w=None, **kw: dict(src=src, a=a, b=b, w=w if w is not None else round(b - a, 3), **kw)     # 放 src 的 a–b 秒
H = lambda src, a, w, **kw: dict(src=src, a=a, hold=True, w=w, **kw)                                           # 定格 src 的第 a 秒那一帧
# 常用裁切（占画面宽 / 高的比例 [x0, y0, x1, y1]）：写在这里，场景里引用
BIGL = [0.095, 0.070, 0.508, 0.930]                       # 大窗（宽高比 0.854）：16:9 画面里裁左边的终端面板
RECC = [0.0, 0.025, 1.0, 0.974]                           # 把略高的录屏裁成 16:9

SCENES = [
    # ═══════ 开场（单窗，小窗居中）
    dict(id="S01", name="开场", mode="one", kind="clip", lines=T(1, 2), credit=C1,
         top=[S("c1", 7.6, 11.3, w=4.3), S("c1", 14.0, 16.5, w=3.0)]),
    # ═══════ 双窗（小窗在左下角）：上下各一组选段；某个窗口素材不够就 H() 定格——但单段定格 > 3 s 会被 gen_ep.py 标 ⚠
    # dict(id="S02", name="…", mode="two", kind="clip", lines=T(3, 4), credit=C1,
    #      top=[S("c1", 50.0, 56.0, w=6.0)], bottom=[S("c1", 63.0, 69.2, w=6.2)]),
    # ═══════ 大窗（big）：官方课终端面板放大 / 自己画的说明卡（内容写在 scenes_ep.js 的 card('S03', …)）
    # dict(id="S03", name="…", mode="big", kind="card", lines=T(5, 8)),
]
