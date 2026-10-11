# -*- coding: utf-8 -*-
r"""【第 1 期真实例子，照这个格式写下一期；换内容不换结构】《Claude官方教程》第 1 期｜出镜版（悠一露脸 + 他自己的原声）——字幕 = 他实际说的话（talk_lines.py），画面 = 每个场景的窗口模式 + 素材选段。

  python scripts/gen_ep.py <本条目录> --timing 制作/01_口播/timing.json     台本 + 选段 + 母带上每句的真时间 → 录制稿.json / plan.json / tts_edit.json / 实际口播稿_字幕版.md

LINES   = talk_lines.LINES（id T01…T124）：zh 字幕、en 英文字幕（照他说的，只改听错的专名 / 同音字）。
SCENES  = 每个场景：mode（one 单窗 / two 双窗上下叠 / big 大窗 = 两个窗口合并那么大）、lines、kind（clip = 官方课 / 录屏镜头，card = 自己画的说明卡，画在 scenes_ep.js）、
          top / bottom = 窗口里放的素材选段 [S(src, a, b, w, speed, crop) / H(src, a, w)]（w = 这一段占场景的相对时长；H = 定格 a 那一帧），credit = 窗口右上角的黄贴纸。
出镜小窗（技能固定规则）：单窗场景居中在字幕下面，双窗 / 大窗缩到左下角 —— 所以大窗里的说明卡内容都放在 y ≤ 1330、左下角留空。
画面规则：只用官方课里的屏幕 / 动画镜头，不放讲师的脸；官方课视频都挂 credit；他自己的录屏挂“悠一 · 录屏”。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import talk_lines as TLN  # noqa: E402

TITLE = {
    "slug": "ClaudeCode是什么_出镜版",
    "title": "Claude官方教程 第1期｜Claude Code 是什么、怎么工作",
    "kicker": "<b>Claude官方教程</b> 第1期",
    "hook": ["Claude Code 是什么", "怎么干活，一个视频讲清楚"],      # 用户 2026-10-06 看了成片说“这里写的不对，修改为怎么干活，一个视频讲清除”（语音输入，“清除”= 清楚）
}

LINES = [{"id": l[0], "zh": l[4], "say": l[4], "en": l[5]} for l in TLN.LINES]
T = lambda a, b: [f"T{i:02d}" for i in range(a, b + 1)]

C1 = "官方课 · Claude Code 101"
S = lambda src, a, b, w=None, **kw: dict(src=src, a=a, b=b, w=w if w is not None else round(b - a, 3), **kw)
H = lambda src, a, w, **kw: dict(src=src, a=a, hold=True, w=w, **kw)
# 大窗（big，内容 1474×1725，宽高比 0.854）：官方课的终端面板在 1920×1080 帧里约 x 0.09–0.91、y 0.07–0.93，裁左边约 41% 宽 × 整个面板高
BIGL = [0.095, 0.070, 0.508, 0.930]
RECC = [0.0, 0.025, 1.0, 0.974]          # 1822×1080 的官网录屏裁成 16:9
PERMZ = [0.16, 0.12, 0.98, 0.83]         # “五种权限”录屏里放大了的下拉框（避开左边的侧栏，里面有会话名和别人的名字）
PERMD = [0.15, 0.0, 0.98, 0.72]          # 同一条录屏里“绕过所有权限？”的确认框

SCENES = [
    # ═══════ 开场 + 资料从哪来（单窗，小窗居中）
    dict(id="S01", name="开场", mode="one", kind="clip", lines=T(1, 5), credit=C1,
         top=[S("c1", 7.6, 11.3, w=4.3), S("c1", 14.0, 16.5, w=3.0), S("c1", 39.5, 44.5, w=5.0), S("c1", 119.8, 124.5, w=5.0)]),
    dict(id="S02", name="官网 → Claude Academy（悠一的录屏）", mode="one", kind="clip", lines=T(6, 7), credit="悠一 · 录屏",
         top=[S("rec", 0.8, 4.2, speed=1.0, crop=RECC), S("rec", 4.2, 12.8, speed=1.8, crop=RECC)]),
    dict(id="S03", name="Claude Code 和 Cowork（桌面应用的三个标签）", mode="one", kind="clip", lines=T(8, 10), credit="官方课 · 安装",
         top=[S("c3", 117.0, 119.4, w=2.4), S("c3", 122.3, 126.5, w=4.3)]),
    # ═══════ 聊天窗口 vs Claude Code（双窗 / 大窗，小窗在左下角）
    dict(id="S04", name="聊天窗口：只能回答，不能改文件", mode="two", kind="clip", lines=T(11, 14), credit=C1,
         top=[S("c3", 115.0, 119.3, w=4.3), H("c3", 118.9, w=5.4), S("c1", 50.0, 51.3, w=1.3), H("c1", 51.3, w=5.6)],
         bottom=[S("c1", 47.0, 49.4, w=2.4), H("c1", 49.3, w=14.2)]),
    dict(id="S05", name="把手伸进电脑：创建、修改、删除", mode="big", kind="clip", lines=T(15, 16), credit=C1,
         top=[S("c1", 39.5, 45.4, w=5.9, crop=BIGL), S("c1", 84.4, 89.0, w=4.8, crop=BIGL)]),
    dict(id="S06", name="Claude Code 是官方做的 AI 助手", mode="two", kind="clip", lines=T(17, 19), credit=C1,
         top=[S("c4", 81.0, 86.6, w=5.6)],
         bottom=[S("c4", 89.0, 96.0, w=7.0)]),
    dict(id="S07", name="顾问 vs 助手", mode="big", kind="card", lines=T(20, 24)),
    # ═══════ 活动范围 / 怎么启动（单窗，小窗居中）
    dict(id="S08a", name="活动范围：这个文件夹", mode="one", kind="card", lines=T(25, 25)),
    dict(id="S08b", name="碰别的地方要经过你的同意", mode="one", kind="clip", lines=T(26, 26), credit=C1,
         top=[S("c1", 133.3, 136.4, w=3.1)]),
    dict(id="S09", name="在终端里输入 claude", mode="one", kind="clip", lines=T(27, 28), credit="官方课 · 安装",
         top=[S("c3", 38.0, 44.8, w=6.8)]),
    # ═══════ 终端是什么 / 智能体 / 它能干什么（双窗、大窗，小窗在左下角）
    dict(id="S10", name="终端：只能敲命令的窗口", mode="two", kind="clip", lines=T(29, 30), credit="官方课 · 安装",
         top=[S("c3", 18.4, 25.3, w=7.0)], bottom=[S("c3", 28.0, 33.5, w=5.5), S("c3", 38.0, 41.0, w=3.0)]),
    dict(id="S11", name="用自然语言跟它沟通", mode="two", kind="clip", lines=T(31, 31), credit=C1,
         top=[S("c4", 88.9, 94.5, w=5.6)], bottom=[S("c4", 95.0, 101.0, w=6.0)]),
    dict(id="S12", name="智能体 AI Agent", mode="two", kind="clip", lines=T(32, 33), credit=C1,
         top=[S("c1", 71.2, 78.4, w=7.2)], bottom=[S("c1", 63.0, 69.2, w=6.2), S("c1", 119.8, 121.8, w=2.0)]),
    dict(id="S13", name="不只是写代码：写文档、跑程序、搜文件、查资料", mode="two", kind="clip", lines=T(34, 36), credit=C1,
         top=[S("c2", 124.5, 133.6, w=9.1)], bottom=[S("c2", 97.9, 107.2, w=9.3)]),
    dict(id="S14a", name="能干什么 ①：读项目", mode="two", kind="clip", lines=T(37, 40), credit=C1,
         top=[S("c4", 44.0, 52.0, w=8.0), S("c4", 53.0, 61.0, w=8.0)], bottom=[S("c6", 20.2, 27.5, w=7.3), S("c4", 62.0, 68.0, w=6.0)]),
    dict(id="S14b", name="能干什么 ②：改代码", mode="two", kind="clip", lines=T(41, 43), credit=C1,
         top=[S("c1", 7.6, 11.3, w=3.7), S("c1", 158.9, 162.9, w=4.0), S("c4", 104.5, 110.5, w=6.0)],
         bottom=[S("c4", 73.5, 75.8, w=2.3), S("c4", 92.0, 98.0, w=6.0), S("c4", 117.1, 119.4, w=2.3), S("c4", 122.5, 123.7, w=1.2)]),   # 原来的网页 → 提需求 → 改好的深色网页（119.4–122.5 是讲师的脸，不能用）
    dict(id="S14c", name="能干什么 ③：跑命令", mode="two", kind="clip", lines=T(44, 45), credit=C1,
         top=[S("c1", 84.4, 89.0, w=4.6), S("c1", 132.3, 136.4, w=4.1)], bottom=[S("c4", 105.0, 110.5, w=5.5), S("c4", 112.5, 115.9, w=3.4)]),
    dict(id="S14d", name="能干什么 ④：上网查资料（新闻聚合）", mode="big", kind="card", lines=T(46, 47)),
    dict(id="S14e", name="不用一件件指挥：告诉它目标", mode="two", kind="clip", lines=T(48, 48), credit=C1,
         top=[S("c4", 22.4, 30.4, w=8.0)], bottom=[S("c4", 89.0, 96.5, w=7.5)]),
    # ═══════ 它怎么干活：代理循环
    dict(id="S15", name="一个循环的概念", mode="two", kind="clip", lines=T(49, 50), credit=C1,
         top=[S("c2", 17.3, 23.0, w=5.7)], bottom=[S("c1", 63.3, 68.8, w=5.5)]),
    dict(id="S16", name="agent loop = 代理循环", mode="two", kind="clip", lines=T(51, 53), credit=C1,
         top=[S("c2", 30.4, 33.4, w=3.0), S("c2", 37.7, 45.0, w=7.3), S("c2", 48.7, 52.5, w=3.8)],
         bottom=[S("c1", 63.3, 69.2, w=6.0), S("c1", 71.2, 78.4, w=7.2)]),
    dict(id="S17", name="例子：登录页点了没反应（循环图 ①）", mode="big", kind="card", lines=T(54, 58)),
    dict(id="S18", name="找代码 → 读报错 → 改 → 跑", mode="two", kind="clip", lines=T(59, 60), credit=C1,
         top=[S("c1", 149.6, 155.8, w=6.3), S("c1", 132.5, 136.4, w=3.7)],
         bottom=[S("c1", 119.8, 124.5, w=4.7), S("c1", 159.0, 162.9, w=4.0), S("c4", 112.5, 115.9, w=3.4)]),
    dict(id="S19", name="修好了就达成目标，没修好再转一圈（循环图 ②）", mode="big", kind="card", lines=T(61, 63)),
    dict(id="S20", name="转半圈 vs 连着做几十步", mode="big", kind="card", lines=T(64, 67)),
    dict(id="S21", name="你也在圈里：Esc / 打字回车", mode="big", kind="card", lines=T(68, 71)),
    # ═══════ 四个零件：大脑 双手 记忆 钥匙
    dict(id="S22", name="四个点：大脑 双手 记忆 钥匙", mode="big", kind="card", lines=T(72, 74)),
    dict(id="S23", name="大脑在云端 / 双手是工具", mode="big", kind="card", lines=T(75, 80)),
    dict(id="S24", name="大脑和双手怎么配合（一来一回）", mode="big", kind="card", lines=T(81, 87)),
    dict(id="S25", name="记忆 = 上下文窗口", mode="two", kind="clip", lines=T(88, 89), credit="官方课 · 上下文管理",
         top=[S("c6", 29.6, 34.0, w=4.4), H("c6", 34.0, w=4.4)], bottom=[S("c6", 13.1, 15.7, w=2.6), H("c6", 15.6, w=6.2)]),
    dict(id="S26", name="满了自动压缩，旧细节会丢", mode="two", kind="clip", lines=T(90, 92), credit="官方课 · 上下文管理",
         top=[S("c6", 43.2, 46.1, w=2.9), S("c6", 46.4, 52.4, w=6.0), S("c6", 65.5, 71.0, w=5.5), S("c1", 112.5, 116.0, w=3.5)], bottom=[S("c6", 102.9, 108.2, w=5.3), S("c6", 176.9, 183.8, w=7.0)]),
    dict(id="S27", name="新开一场对话，记忆是空的", mode="two", kind="clip", lines=T(93, 94), credit="官方课 · 上下文管理",
         top=[S("c6", 113.1, 117.6, w=4.5), S("c6", 190.5, 195.8, w=5.3)], bottom=[S("c6", 121.3, 125.5, w=4.2), S("c6", 102.9, 108.2, w=5.3)]),
    dict(id="S28", name="每次要遵守的规则：写进 CLAUDE.md", mode="two", kind="clip", lines=T(95, 97), credit="官方课 · CLAUDE.md",
         top=[S("c8", 59.0, 68.5, w=9.5), S("c8", 70.0, 75.5, w=5.5)], bottom=[S("c8", 84.2, 90.8, w=6.6), S("c8", 98.6, 101.0, w=2.4)]),   # 93.5–95.3 的标题卡后半段、101 s 以后都有讲师的脸，不用
    # ═══════ 钥匙 = 权限（官方课的六宫格动画 + 悠一自己录的五种权限）
    dict(id="S29", name="钥匙：权限（五种模式）", mode="two", kind="clip", lines=T(98, 100), credit="官方课 · 权限模式",
         top=[S("p4", 25.6, 27.0, w=2.0), H("p4", 26.9, w=7.4)],
         bottom=[S("perm", 4.2, 5.6, speed=0.6, crop=PERMZ), H("perm", 5.3, w=6.9, crop=PERMZ)]),
    dict(id="S30", name="手动档：每步先问你", mode="two", kind="clip", lines=T(101, 101), credit="官方课 · 权限模式",
         top=[S("p4", 26.7, 29.9, w=3.2)], bottom=[S("c1", 133.0, 136.4, w=3.4)]),
    dict(id="S31", name="接受编辑档：改文件不问", mode="two", kind="clip", lines=T(102, 104), credit="官方课 · 权限模式",
         top=[S("p4", 30.4, 36.4, w=6.0)], bottom=[S("c1", 159.0, 162.9, w=3.9), S("c4", 83.0, 86.6, w=3.6), S("c4", 88.9, 91.5, w=2.6)]),
    dict(id="S32", name="计划档：只研究，不碰代码", mode="two", kind="clip", lines=T(105, 105), credit="官方课 · 权限模式",
         top=[S("p4", 37.4, 40.5, w=3.1)], bottom=[S("c4", 104.5, 110.5, w=6.0)]),
    dict(id="S33", name="自动档：后台有安全检查", mode="two", kind="clip", lines=T(106, 106), credit="官方课 · 权限模式",
         top=[S("p4", 69.6, 73.8, w=4.2)], bottom=[S("p4", 82.5, 87.0, w=4.5)]),
    dict(id="S34", name="全部放开：不建议新手开", mode="two", kind="clip", lines=T(107, 108), credit="官方课 · 权限模式",
         top=[S("p4", 53.2, 59.6, w=6.4)],
         bottom=[S("perm", 5.6, 7.9, speed=0.7, crop=PERMD), H("perm", 7.4, w=6.1, crop=PERMD)]),
    # ═══════ 小结 + 泼冷水
    dict(id="S35", name="四个零件合起来 = 本地的智能体", mode="big", kind="card", lines=T(109, 110)),
    dict(id="S36", name="泼冷水：幻觉、概率模型、可能有 bug", mode="big", kind="card", lines=T(111, 114)),
    dict(id="S37", name="还是有风险：权限别开最大", mode="two", kind="clip", lines=T(115, 116), credit="官方课 · 权限模式",
         top=[S("p4", 78.3, 87.0, w=8.7)], bottom=[S("p4", 53.5, 57.5, w=5.8), H("perm", 7.4, w=5.8, crop=PERMD)]),
    # ═══════ 怎么用上它
    # 单窗，镜头按他说的顺序走（权重 = 他说到这里的秒数）：终端 4.6 → 回车启动 3.4 → 登录 2.3 → 编辑器插件 3.7 → 桌面应用 2.0 → 网页版 1.0
    dict(id="S38", name="怎么用上它：终端 / 编辑器插件 / 桌面应用 / 网页版", mode="one", kind="clip", lines=T(117, 119), credit="官方课 · 安装",
         top=[S("c3", 18.4, 23.2, w=4.6), S("c3", 39.0, 42.6, w=3.4), S("c3", 48.0, 50.5, w=2.3), S("c3", 69.0, 72.9, w=3.7), S("c3", 122.3, 124.5, w=2.0), S("c3", 141.0, 142.6, w=1.04)]),
    # ═══════ 收尾（单窗，小窗回到居中）
    dict(id="S39a", name="两点建议 ①：先看状态栏", mode="one", kind="clip", lines=T(120, 121), credit=C1,
         top=[S("c4", 92.0, 97.5, w=5.5), S("c4", 98.0, 101.8, w=4.0)]),
    dict(id="S39b", name="两点建议 ②：先问问题，再让它改东西", mode="one", kind="clip", lines=T(122, 124), credit=C1,
         top=[S("c4", 89.0, 92.6, w=3.6), S("c1", 39.5, 45.0, w=5.5), S("c4", 117.1, 119.4, w=2.3), S("c4", 122.5, 123.7, w=1.2), H("c4", 123.6, w=4.5)]),
]

# 素材短名 → 中文名（gen_ep.py 写 实际口播稿_字幕版.md 的“画面”行用；common.py 的 SRC 里是同一套短名）
LABEL = {"rec": "悠一的录屏", "c1": "官方课第1课", "c2": "官方课第2课", "c3": "官方课第3课", "c4": "官方课第4课", "c6": "官方课第6课", "p4": "官方课·权限模式", "c8": "官方课第8课", "perm": "悠一的录屏（五种权限）"}
