# -*- coding: utf-8 -*-
"""投稿信息：从时间轴算出简介里的章节时间（正片时间 + 片头 3.8 s），写 投稿信息.json 和 制作/_desc_final.txt。

  python make_submission.py

正片重渲、片头长度变了、台词改了，都要重跑一遍。投稿由用户自己点（插件传不了 100 MB 以上的文件，要用户把 mp4 拖进上传框）。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
INTRO = 3.8
cu = {q["id"]: q for q in T["cues"]}


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


# 简介里的章节（比左栏目录细：三个示例各占一条）
CH = [("能装模组了", None), ("模组怎么写、怎么装", "N05"), ("示例 1：Token Weather（上下文天气预报）", "N13"), ("示例 2：Blast Radius（拦住危险命令）", "N22"),
      ("示例 3：Replay Theater（回放每一处修改）", "N29"), ("装之前要知道：模组不在沙盒里", "N33"), ("顺带 1：claude.dev 新主页", "N42"),
      ("顺带 2：Sonnet 5.5", "N46"), ("顺带 3：评测命令 build-eval / hillclimb", "N52"), ("想玩模组，三步", "N58")]
chapters = []
for name, cid in CH:
    t0 = 0.0 if cid is None else max(0.0, cu[cid]["s"] - 0.3)
    chapters.append([mmss(t0 + INTRO if cid else 0), name])

TITLE = "现在你可以让Claude修改自己！Claude新功能：Claude mod"      # 线上的标题：用户在投稿页里自己改定的（我填的是“现在你可以修改Claude Code成自己喜欢的样子”，用户改了好几次）
COVER_TEXT = "Claude mod(模组)发布"
BVID = "BV1Zoa16CEeU"                                  # 2026-10-02 10:44 北京时间发布，合集「Claude Code相关」（id 9223239）
LINKS = [
    ("@ClaudeDevs 帖子串（Claude Code 模组）", "https://x.com/ClaudeDevs/status/2105721434807083061"),
    ("@ClaudeDevs 帖子（claude.dev 新主页）", "https://x.com/ClaudeDevs/status/2105391694741119047"),
    ("模组入门教程（claude.dev）", "https://claude.dev/blog/getting-started-with-claude-code-mods/"),
    ("Mods 官方文档", "https://code.claude.com/docs/en/plugins/mods/overview"),
    ("Sonnet 5.5 使用指南", "https://claude.dev/blog/building-with-claude-sonnet-5-5/"),
    ("评测与 hillclimb", "https://claude.dev/blog/automating-eval-design-and-hillclimbing/"),
]
desc = "\n".join([
    "Claude 官方开发者账号 @ClaudeDevs 这几天连发了好几条新东西。这期一个视频讲完：Claude Code 现在能装“模组”了，再加 claude.dev 新主页、Sonnet 5.5，以及 claude-api 技能里的两个评测命令。",
    "",
    "本期内容",
    *[f"{t} {n}" for t, n in chapters],
    "",
    "模组（mods）要点",
    "· 模组是装在插件里的小程序（JavaScript / TypeScript），能改 Claude Code 的行为和界面，也能换上自己写的功能；几行 TypeScript 就能写，或者让 Claude Code 帮你写。",
    "· 需要 Claude Code 2.1.287 或更高版本，默认开启；命令行版和桌面版的 Code 标签页都能用；用 /plugin 安装。",
    "· 官方示例：Token Weather（输入框上方显示上下文用了多少）、Blast Radius（拦住 rm -rf 这类命令，先列出会动哪些文件）、Replay Theater（回放这一轮的每一处修改）。",
    "· 注意：模组不在沙盒里，权限和 Claude Code 一样大，只装信得过的人写的；装之前可以先跑 claude plugin validate，看它挂了哪些事件、会调用什么。",
    "",
    "顺带三件事",
    "· claude.dev：官方给用 Claude 做东西的开发者开的新主页。",
    "· Sonnet 5.5：5.5 家族的第二个模型（前面是 Opus 5.5），比 Sonnet 5 快 30% 以上，单价没变，大多数任务最多便宜 30%；Claude Code 里用 /model sonnet 切换，默认模型仍是 Opus 5.5。",
    "· 评测：claude-api 技能新增 /claude-api build-eval 和 /claude-api hillclimb。",
    "",
    "资料来源（2026 年 10 月 2 日读的官方页面）",
    *[f"· {n}：{u}" for n, u in LINKS],
    "",
    "补充说明",
    "· 画面里的官方演示视频来自 @ClaudeDevs（X 平台），仅作介绍和评论引用，版权归原作者；",
    "· 封面背景取自 claude.dev 官方教程页底部的太空插画，版权归 Anthropic；",
    "· 功能、版本号和价格会变，以官方文档为准；",
    "· 配音：曼波声线（AI 生成）；剪辑：Claude Code（Sonnet 5.5）。",
])
assert len(desc) <= 2000, len(desc)

info = {
    "platform": "B站（不选合集）",
    "status": "已发布：BV1Zoa16CEeU（2026-10-02 10:44 北京时间，254 s，合集「Claude Code相关」）",
    "title": TITLE,
    "bvid": BVID,
    "season": "Claude Code相关（id 9223239）",
    "title_note": "线上标题是用户 2026-10-02 在投稿页里自己改定的（“我修改了标题，按照我的来”）；我填的是“现在你可以修改Claude Code成自己喜欢的样子”，封面字是“Claude mod(模组)发布”，两处不重复。历史：我拟的草稿“Claude Code 能装模组了！官方这几天发的新东西，一个视频讲完” → 用户整句“Claude mod(模组)发布！现在你可以修改Claude Code成自己喜欢的样子” → 拆成封面字 + 标题 → 用户最后改成现在这个。",
    "cover_text": COVER_TEXT,
    "video": "Claude新功能介绍_成片.mp4",
    "video_note": f"含悠一片头 {INTRO} s + 正片 {T['total']:.1f} s + 片尾 4.8 s；2340×1080；正片版本 制作/00_整片/整片_v1.mp4",
    "cover_16x9": "制作/04_封面/封面_选定_16x9.png（= 封面_C_16x9.png：claude.dev 官方教程页底部的太空场景 + 放大的橙色宇航员 + 白字橙字“Claude mod(模组)发布”）",
    "cover_4x3": "制作/04_封面/封面_选定_4x3.png（= 封面_C_4x3.png，同一设计）",
    "cover_note": "用户 2026-10-02：“封面太丑了”→ 换成官方教程页最底部的太空场景做背景；字只写“Claude mod(模组)发布”；看了三张候选背景后选第三张（紧裁）并要求“claude的形象大一点”。旧的 A 深色 / B 米色（三个演示界面拼贴）在 制作/04_封面/_旧稿/。",
    "category": "人工智能",
    "declaration": "含AI生成内容",
    "tags": ["编程", "claude", "Claude Code", "Harness", "人工智能", "AI编程", "Anthropic", "模组", "Sonnet 5.5", "AI工具"],
    "tags_backup": ["ClaudeDevs", "Opus 5.5", "AI Agent", "效率工具", "大模型"],
    "tags_note": "线上实际用的 10 个标签（B 站自动加了小写的 claude 和 编程，我删掉了自动的“原创”“短片”，补了 Harness 呼应用户的标题；claude.dev 和 科技 没放进去，位置不够）。「Claude」是话题专用标签，自己输入的要小写才行。",
    "chapters": chapters,
    "chapters_note": f"时间 = 正片时间 + 片头 {INTRO} s（取整到秒）；正片重渲或片头长度变了要重跑 make_submission.py。",
    "desc": desc,
    "youtube": "未定（独立视频默认只发 B 站）",
    "todo_after_publish": [
        "GitHub release（tag 建议 claude-code-01）要等用户定了提交 git 的事再做；README 的“视频存档”表已加这一期，release 链接待补。",
        "片尾清单（制作/00_整片/outro.json）是草稿，用户发布时没提异议，已按草稿发布。",
        "官方页面会变：Claude Code 版本号（2.1.287）、Sonnet 5.5 默认模型 / 价格、“官方正往 Playground 仓库里加示例”会过期；简介里的“这几天”按 10 月 2 日算。",
    ],
}
(HERE / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "制作" / "_desc_final.txt").write_text(desc + "\n", encoding="utf-8")
print(f"投稿信息.json 已写：标题 {len(TITLE)} 字，简介 {len(desc)} 字，章节 {len(chapters)} 条")
for t, n in chapters:
    print(" ", t, n)
