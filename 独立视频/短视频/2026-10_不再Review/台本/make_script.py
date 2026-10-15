# -*- coding: utf-8 -*-
"""短视频《不再 Review》台本唯一来源：改台本只改这里，再跑 python make_script.py 生成 录制稿.json 和 plan.json（build_timeline.py 读这两个）。
长视频（独立视频/长视频/2026-10_不再Review/）的二次剪辑：钩子 → 背书 → 算账 → 拆机制 → 泼冷水 → 金句；第三人称、AI大圆镜写法。
事实全部来自长视频的 台本/事实核对.md（访谈原话 + 她的演讲 + pstack 官方文档）。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

LINES = [
    # id, zh（字幕）, say（念的字）, en（英文字幕）
    ("N01", "一个月 2000 多个 PR，她说自己没有逐个 Review。", "一个月两千多个PR，她说自己没有逐个Review。",
     "2,000-plus PRs in a month, and she says she didn't review them one by one."),
    ("N02", "她叫 Lauren Tan，在 SpaceXAI 做 Grok Bot。", "她叫Lauren Tan，在SpaceXAI做Grok Bot。",
     "Lauren Tan works on Grok Bot at SpaceXAI."),
    ("N03", "10 月 2 号，Matt Pocock 请她上直播，聊了 65 分钟。", "十月二号，Matt Pocock请她上直播，聊了六十五分钟。",
     "On October 2, Matt Pocock had her on his livestream for 65 minutes."),
    ("N04", "按 2000 个算，每天 67 个。一个看 15 分钟，要 17 个小时。", "按两千个算，每天六十七个。一个看十五分钟，要十七个小时。",
     "At 2,000 PRs, that's 67 a day. At 15 minutes each, that's 17 hours."),
    ("N05", "一个人看不过来，所以她改成抽样。靠两样东西：验证，和规矩。", "一个人看不过来，所以她改成抽样。靠两样东西：验证，和规矩。",
     "One person can't keep up, so she samples instead. Two things hold it together: verification and rules."),
    ("N06", "验证：让 AI 像真人用户一样，把程序跑一遍。", "验证：让AI像真人用户一样，把程序跑一遍。",
     "Verification: the AI uses the program like a real user."),
    ("N07", "规矩：AI 犯过的错，写成 lint 规则，让它再也犯不了。", "规矩：AI犯过的错，写成lint规则，让它再也犯不了。",
     "Rules: a mistake the AI made once becomes a lint rule, so it can't happen again."),
    ("N08", "她把做法写成了一组技能，叫 pstack。", "她把做法写成了一组技能，叫pstack。",
     "She wrote the method up as a set of skills called pstack."),
    ("N09", "官方文档里的全自动模式：每个 PR 派一批验证员，裁决干净，才准合并。", "官方文档里的全自动模式：每个PR派一批验证员，裁决干净，才准合并。",
     "In its official docs' full-autopilot mode, every PR gets a swarm of verifiers, and only a clean verdict lets it merge."),
    ("N10", "合并之后，她才看：早上翻提交记录，有问题就撤回，再加规则。", "合并之后，她才看：早上翻提交记录，有问题就撤回，再加规则。",
     "She reviews after the merge: the morning commit log, revert what's wrong, add a rule."),
    ("N11", "但她自己说，走到这一步非常难。撤不回、又难验证的活，她说没有答案。", "但她自己说，走到这一步非常难。撤不回、又难验证的活，她说没有答案。",
     "But she says getting here is very hard, and for work that can't be undone or verified, she has no answer."),
    ("N12", "Review 没有消失。它从每个 PR 的门口，搬到了早上的提交记录里。", "Review没有消失。它从每个PR的门口，搬到了早上的提交记录里。",
     "Review didn't vanish. It moved from the door of every PR to the morning's commit log."),
]

# ═══════════ 镜头表（dual：上框 ranges = 访谈里的人脸，静音；下框 ranges2 = 她演讲里的幻灯片（静音、纯色补边）或官方页面录屏（scenes.js 的 pageShot {lower: true}））
# iv = Matt 的直播（1920×1080，左半 Matt、右半 Lauren，各 960×1080 的人像格）：crop 取一格里 960×540 的上半身（x、y 方向都是 0.5，所以还是 16:9，直接铺满）
LAUREN = [0.5, 0.06, 1.0, 0.56]
MATT = [0.0, 0.06, 0.5, 0.56]


def tk_crop(x0, y0, x1, y1):
    """Lauren 的演讲视频 1720×1080：避开右下头像圆框、底部字幕条、顶栏（同长视频 make_script.py 的 crop）。"""
    return [round(x0 / 1720, 4), round(y0 / 1080, 4), round(x1 / 1720, 4), round(y1 / 1080, 4)]


CROP_TITLE = tk_crop(96, 140, 1366, 854)      # 首页：i shipped 2000 PRs last month
CROP_CHART = tk_crop(420, 110, 1210, 880)     # 三张 GitHub 贡献曲线：i shipped 5000+ PRs in 6 months
CROP_VERIFY = tk_crop(170, 120, 1380, 810)    # High-quality verification：THE AGENT CAN VERIFY ITS OWN WORK
CROP_RULES = tk_crop(150, 55, 1500, 715)      # whenever you correct your agent：1 codebase … 5 style guide
CRED = "Matt Pocock 直播"                      # 上框右上角的黄贴纸（≤ 16 字）；下框不贴


def top(a, b, crop):
    return {"src": "iv", "in": a, "out": b, "mute": True, "crop": crop}


def slide(t, hold, crop, bg):
    return {"src": "tk", "in": t, "hold": hold, "crop": crop, "bg": bg}


def ln(*ids):
    return [{"id": i, "a": 0.0} for i in ids]


PLAN = [
    {"id": "S1", "type": "clip", "kind": "demo", "overlay": "clip", "name": "钩子：2000 个 PR + 她是谁", "credit": CRED,
     "ranges": [top(2392.0, 2402.8, LAUREN)], "ranges2": [slide(1.0, 11.0, CROP_TITLE, "#F9F8FB")], "lines": ln("N01", "N02", "N03")},
    {"id": "S2", "type": "clip", "kind": "demo", "overlay": "clip", "name": "算账：每天 67 个 → 抽样", "credit": CRED,
     "ranges": [top(2960.4, 2965.9, MATT), top(2974.0, 2978.7, LAUREN)], "ranges2": [slide(220.0, 10.3, CROP_CHART, "#F9F8FB")], "lines": ln("N04", "N05")},
    {"id": "S3", "type": "clip", "kind": "demo", "overlay": "clip", "name": "验证：给 AI 一双手和眼睛", "credit": CRED,
     "ranges": [top(996.0, 1000.0, LAUREN)], "ranges2": [slide(610.0, 5.0, CROP_VERIFY, "#F8F5E8")], "lines": ln("N06")},
    {"id": "S4", "type": "clip", "kind": "demo", "overlay": "clip", "name": "规矩：写成 lint 规则", "credit": CRED,
     "ranges": [top(1000.6, 1004.8, LAUREN)], "ranges2": [slide(1010.0, 5.0, CROP_RULES, "#F9F8FB")], "lines": ln("N07")},
    {"id": "S5", "type": "clip", "kind": "demo", "overlay": "clip", "name": "pstack README", "credit": CRED,
     "ranges": [top(3170.0, 3173.0, LAUREN)], "lines": ln("N08")},
    {"id": "S6", "type": "clip", "kind": "demo", "overlay": "clip", "name": "官方文档：全自动模式", "credit": CRED,
     "ranges": [top(3174.0, 3180.0, LAUREN)], "lines": ln("N09")},
    {"id": "S7", "type": "clip", "kind": "demo", "overlay": "clip", "name": "合并之后才看", "credit": CRED,
     "ranges": [top(3235.5, 3240.3, LAUREN)], "lines": ln("N10")},
    {"id": "S8", "type": "clip", "kind": "demo", "overlay": "clip", "name": "泼冷水：非常难、没有答案", "credit": CRED,
     "ranges": [top(3080.2, 3085.4, LAUREN)], "ranges2": [top(3366.5, 3371.8, MATT)], "lines": ln("N11")},
    {"id": "S9", "type": "clip", "kind": "demo", "overlay": "clip", "name": "收尾金句", "credit": CRED,
     "ranges": [top(3257.0, 3261.6, LAUREN)], "lines": ln("N12")},
]
(HERE / "plan.json").write_text(json.dumps({"layout": "dual", "plan": PLAN}, ensure_ascii=False, indent=1), encoding="utf-8")

script = {
    "slug": "不再Review短视频",
    "title": "不再 Review：她一个月 2000 多个 PR 是怎么把关的（长视频《不再Review》的二次剪辑）",
    "kicker": "悠一 · <b>AI 编程</b> 访谈",
    "hook": ["一个月2000多个PR", "她说不逐个Review"],
    "lines": [{"id": i, "zh": zh, "say": say, "en": en} for i, zh, say, en in LINES],
}
(HERE / "录制稿.json").write_text(json.dumps(script, ensure_ascii=False, indent=1), encoding="utf-8")
han = sum(1 for _, _, say, _ in LINES for ch in say if "一" <= ch <= "鿿")
print(f"{len(LINES)} 句，念的汉字 {han} 个（估时 {han * 0.225:.0f} s，温柔男生实测约 0.21–0.235 s/字）")
