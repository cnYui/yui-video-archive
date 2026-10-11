# -*- coding: utf-8 -*-
"""台本 → 录制稿_v1.json（唯一来源）+ 录制稿_v1.md（给人读）。改台词改这个文件再重跑。

  python build_script.py

字段：id / ch（章节序号）/ zh（字幕上的字）/ say（配音念的字：数字写汉字、斜杠命令写“斜杠 xxx”、英文名照写）。
say 不写就按 to_say() 自动转；自动转不对的地方在 SAY 里单独写。
事实依据（全部是官方原文，2026-10-02 读的）：
  · ClaudeDevs 的 X 帖子串（Claude Code mods，2026-10-01 美国时间 / 10-02 东京时间）、claude.dev 新站帖
  · claude.dev/blog/getting-started-with-claude-code-mods（Addy Osmani，Oct 01）
  · code.claude.com/docs/en/plugins/mods/overview（Mods overview）
  · claude.dev/blog/building-with-claude-sonnet-5-5（Sep 28）、claude.dev/blog/automating-eval-design-and-hillclimbing（Sep 28）
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

CHAPTERS = ["模组是什么", "示例和注意事项", "顺带三件事"]      # 用户 2026-10-02：目录缩短、压缩为三个


def chap(i):
    """按字幕条号分章：N01–N12 模组是什么；N13–N41 示例和注意事项；N42 起顺带三件事。"""
    n = int(i[1:])
    return 0 if n <= 12 else 1 if n <= 41 else 2

# (id, 章节, 字幕)
L = [
    # ── 0 开场
    ("N01", 0, "Claude Code 现在，能装模组了。"),
    ("N02", 0, "对，就是你玩游戏时装的那种模组。"),
    ("N03", 0, "Claude 官方开发者账号，这几天连发了好几条新东西。"),
    ("N04", 0, "我给你捋一遍，先说最大的这个。"),
    # ── 1 模组怎么写、怎么装
    ("N05", 1, "以前你能改的东西不少：设置、权限规则、斜杠命令、技能、状态栏。"),
    ("N06", 1, "模组再往前一步：改它的行为，改它的界面，还能换上你自己写的功能。"),
    ("N07", 1, "怎么写？几行 TypeScript 就行。"),
    ("N08", 1, "懒得写，就直接告诉 Claude Code 你想要啥，它帮你写。"),
    ("N09", 1, "怎么装？模组就是插件，输入 /plugin 就能装。"),
    ("N10", 1, "命令行版，和桌面版的 Code 标签页，都能用。"),
    ("N11", 1, "版本要 2.1.287 以上，默认就是开着的。"),
    ("N12", 1, "Claude Code 自己的 /diff 窗格，还有 AGENTS.md 支持，就是模组做的。"),
    # ── 2 官方三个示例
    ("N13", 2, "官方给了三个示例。第一个，Token Weather，上下文天气预报。"),
    ("N15", 2, "上下文，就是 Claude 在这场对话里，一次能记住的内容。"),
    ("N16", 2, "它在输入框上面画一行：天气图标，用了百分之几，"),
    ("N17", 2, "最近十二轮的小折线，还有上一轮涨了多少。"),
    ("N18", 2, "不到百分之二十五是晴天，往上依次是多云、阵雨、暴风雨。"),
    ("N19", 2, "到了百分之九十，它提醒你：快要压缩了。"),
    ("N20", 2, "整个模组，才八十行代码。"),
    ("N21", 2, "看到暴风雨，建议别再往里塞大文件了。"),
    ("N22", 2, "第二个，Blast Radius，爆炸半径。"),
    ("N23", 2, "Claude 要跑删文件夹、强制回退代码、强制推送这类命令时，"),
    ("N24", 2, "Blast Radius 先把命令拦住，告诉你它会动哪些文件。"),
    ("N25", 2, "你选继续，命令照跑。选取消，什么都不会被删，Claude 还会收到拒绝的理由。"),
    ("N26", 2, "删库跑路之前，你多了一次反悔的机会。"),
    ("N27", 2, "不过官方说了，它只是一道安全网，不能当权限系统用。"),
    ("N28", 2, "它只看命令的文字，绕得过去。真要硬拦，还得用权限规则。"),
    ("N29", 2, "第三个，Replay Theater，回放剧场。"),
    ("N30", 2, "比如让 Claude 把一个函数改名，它一口气改了六处，分在四个文件里。"),
    ("N31", 2, "这一轮结束，输入 /replay，或者按 R 键，就能一处一处回看。"),
    ("N32", 2, "上一步，下一步，像看比赛回放。"),
    # ── 3 装之前要知道
    ("N33", 3, "好玩归好玩，装之前，有件事要知道。"),
    ("N34", 3, "模组不在沙盒里，权限和 Claude Code 一样大。"),
    ("N35", 3, "它能读写你的文件，能启动程序，能联网，还能看到你环境变量里的密钥。"),
    ("N36", 3, "所以和装软件一个标准：只装信得过的人写的。"),
    ("N37", 3, "装之前，先跑一遍 claude plugin validate，能列出它挂了哪些事件、要调用什么。"),
    ("N38", 3, "不想用了，在 /plugin 里关掉就行。"),
    ("N39", 3, "自己写的想分享，放进 GitHub 仓库，别人三条命令就能装，也能提交到 Claude 目录。"),
    ("N41", 3, "没灵感？官方正往 Claude Code Playground 仓库里，加现成的示例。"),
    # ── 4 顺带三件事
    ("N42", 4, "顺带，官方这几天还发了三件事。"),
    ("N43", 4, "第一件，claude.dev，给用 Claude 做东西的开发者，开的新主页。"),
    ("N44", 4, "里面有工程深度文章，Claude Code 和 API 的指南，各个团队的经验，还藏了些彩蛋。"),
    ("N45", 4, "官方配的视频里，是站里一个像素小游戏：收集五个火花，把太阳叫醒。"),
    ("N46", 4, "第二件，Sonnet 5.5，5.5 家族的第二个模型，前面是 Opus 5.5。"),
    ("N48", 4, "比 Sonnet 5 更聪明，快三成以上。"),
    ("N49", 4, "单价没变，但干同样的活用的 token 更少，大多数任务最多便宜三成。"),
    ("N50", 4, "边界清楚的日常活交给它，比如修 bug、快速改功能。最难的长任务，还是交给 Opus 5.5。"),
    ("N51", 4, "Claude Code 里输入 /model sonnet 就能切过去，默认模型还是 Opus 5.5。"),
    ("N52", 4, "第三件，评测。"),
    ("N53", 4, "官方在 claude-api 技能里，加了两个命令。"),
    ("N54", 4, "build-eval，帮你给自己的应用建一套评测。"),
    ("N55", 4, "hillclimb，对着这套评测，一次只改一处，把分数一点点往上爬。"),
    ("N56", 4, "它还会留一部分没见过的题，防止光背题。"),
    ("N57", 4, "官方拿客服工单做例子，成本降到原来的五分之一左右，准确率还高了。"),
    ("N58", 4, "最后，想玩模组：先更新，看一眼版本号，2.1.287 以上就行。"),
    ("N59", 4, "建议从 Token Weather 做起，官方连提示词都写好了，复制给 Claude Code 就行。"),
    ("N60", 4, "以上来自官方 X 账号、claude.dev 和 Claude Code 文档，链接在简介里。"),
    ("N61", 4, "感谢观看。"),
]

# 自动转不对、要单独指定念法的句子
SAY = {}

REPL = [
    ("/model sonnet", "斜杠 model sonnet"),
    ("/plugin", "斜杠 plugin"),
    ("/replay", "斜杠 replay"),
    ("/diff", "斜杠 diff"),
    ("2.1.287", "二点一点二八七"),
    ("5.5", "五点五"),
    ("Sonnet 5", "Sonnet 五"),
    ("claude-api", "claude api"),
    ("build-eval", "build eval"),
]


def to_say(zh):
    s = zh
    for a, b in REPL:
        s = s.replace(a, b)
    return s


def main():
    lines = []
    for i, ch, zh in L:
        say = SAY.get(i) or to_say(zh)
        bad = re.findall(r"[0-9/\-]", say)
        assert not bad, f"{i} 的 say 里还有 {bad}：{say}"
        lines.append({"id": i, "ch": chap(i), "kind": "vo", "zh": zh, "say": say})
    doc = {
        "title": "现在你可以修改Claude Code成自己喜欢的样子",
        "version": "v1（2026-10-02）",
        "voice": "Fish Audio 网页版「赛马娘（曼波欧耶版）」，整期一次生成；模型 S2 Pro（用户 2026-10-01 指定，账号级设置）",
        "rules": [
            "kind = vo：画外音。zh = 字幕上的字；say = 配音念的字（数字写汉字，斜杠命令写“斜杠 xxx”）。",
            "短句口语，不用“不是……而是……”；不夸张，不替官方加没说过的话；事实全部来自官方原文。",
            "笑点打流程和命令，不打人：删库跑路、看到暴风雨别再塞大文件、像看比赛回放。",
            "日期不写具体几号（美国时间和北京时间差一天），说“这几天”。",
        ],
        "chapters": CHAPTERS,
        "lines": lines,
    }
    (HERE / "录制稿_v1.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# {doc['title']}", "", f"{doc['version']} · 配音：{doc['voice']}", ""]
    cur = -1
    for l in lines:
        if l["ch"] != cur:
            cur = l["ch"]
            md += ["", f"## {cur + 1}. {CHAPTERS[cur]}", ""]
        md.append(f"- **{l['id']}** {l['zh']}" + ("" if l["say"] == l["zh"] else f"　（念：{l['say']}）"))
    (HERE / "录制稿_v1.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    n = sum(len(re.sub(r"\s", "", l["say"])) for l in lines)
    print(f"{len(lines)} 句，念的字 {n}（按 6.3 字/秒 ≈ {n / 6.3:.0f} s，加句间停顿 ≈ {n / 6.3 + len(lines) * 0.25:.0f} s）；最长一句 {max(len(l['zh']) for l in lines)} 字")


if __name__ == "__main__":
    main()
