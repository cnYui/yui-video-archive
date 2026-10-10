# -*- coding: utf-8 -*-
"""投稿信息：从时间轴算出简介里的章节时间（正片时间 + 片头 3.8 s），写 投稿信息.json 和 制作/_desc_final.txt。

  python make_submission.py

正片重渲、片头长度变了、台词改了，都要重跑一遍。投稿由用户自己点“立即投稿”（插件传不了 10 MB 以上的文件，要用户把 mp4 拖进上传框）。
标题、封面字、片尾清单都是我拟的草稿，用户要在投稿页里改就以页面为准（投稿后把线上标题同步回这里）。
"""
import json
from pathlib import Path

import sys

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds   # noqa: E402

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
INTRO, OUTRO = intro_seconds(), outro_seconds()      # 共用片头片尾的时长（2026-10-03 起 4.8 s / 9.0 s）
cu = {q["id"]: q for q in T["cues"]}


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


# 简介里的章节（比左栏目录细）
CH = [("开场：一份看起来很完美的总结", None), ("新插件 You should know 是什么", "N04"), ("官方演示：提醒、详情、带回主会话", "N06"), ("原理：旁路智能体", "N14"),
      ("官方文档：内置模组表、默认关闭、怎么开关", "N16"), ("更新日志：哪个版本加的、有什么前提", "N21"), ("官方没写的地方", "N22")]
chapters = []
for name, cid in CH:
    t0 = 0.0 if cid is None else max(0.0, cu[cid]["s"] - 0.3)
    chapters.append([mmss(t0 + INTRO if cid else 0), name])

TITLE = "一个视频了解 Claude Code 新插件 You should know：Agent Loop 开发里，它替你盯着、帮你复盘"      # 用户 2026-10-03 定：想要“一个视频了解Claude新插件”这种写法，并保留他自己拟的“Agent Loop”“复盘”；“盯着”是官方文档的说法（watches your back）
COVER_TEXT = "别漏看重点 / Claude 新插件"                                                            # 用户 2026-10-03 选定 A（发来封面图：“用这个封面”）；B 是 “You should know / 官方新插件”，C 是 “它替你盯着 / Claude 的输出”
LINKS = [
    ("@ClaudeDevs 推文（新增 You should know，带演示视频）", "https://x.com/ClaudeDevs/status/2106118517447876618"),
    ("@ClaudeDevs 回复（它是个 mod，派出 sideagent 观察）", "https://x.com/ClaudeDevs/status/2106118519368888562"),
    ("官方文档 · Mods 概览 · 内置模组表", "https://code.claude.com/docs/en/plugins/mods/overview#mods-built-into-claude-code"),
    ("官方更新日志（2.1.287、2.1.288）", "https://code.claude.com/docs/en/changelog"),
    ("模组入门教程（claude.dev，推文里链的那篇）", "https://claude.dev/blog/getting-started-with-claude-code-mods/"),
]
desc = "\n".join([
    "Claude Code 新增了一个内置插件 You should know（在 /plugin 里叫 cc-plugin-you-should-know）：Claude 做较长任务时，有一个旁路智能体（side agent）在旁边替你盯着，发现你可能漏掉的事，就在输入框上方给你留一条便条。这期用官方演示视频把它的流程过一遍，再讲官方写明的开关和前提。",
    "",
    "本期内容",
    *[f"{t} {n}" for t, n in chapters],
    "",
    "要点（都来自官方推文、文档和更新日志）",
    "· 官方推文：新增插件 You should know，扫描 Claude 的输出，把你可能漏掉的重要信息挑出来；启用命令 /plugin enable cc-plugin-you-should-know@builtin。",
    "· 官方回复：它是一个 mod（模组），靠派出一个 sideagent 观察 Claude 的输出。",
    "· 官方文档（Mods 概览的内置模组表）：现在共 6 个内置模组，它是其中之一；默认关闭；在 /plugin → Installed → Show disabled 里能看到（如果你的组织可用）；在 /plugin 里 Disable 关闭；内置模组不能更新、不能卸载。",
    "· 更新日志：2.1.287 加入（括号里的前提：第一方会话、遥测开着）；2.1.288 把便条的措辞改成按谁负责某个决定，分别用 we / the main agent / you。",
    "· 官方演示：Claude 修结账超时，加了自动重试；总结之后插件弹出提醒——这个重试可能让顾客被扣两次钱；按 1 看详情（解法是幂等键），按 2 把这条提醒当作旁路智能体的备注带回主会话，Claude 看完改成每笔付款只生成一次随机键。",
    "",
    "几处要说明",
    "· 官方没写：它用哪个模型、多久提醒一次、会不会误报、扫描哪些内容、会不会多花额度；它的源码也没有公开（mods/ 目录里没有它）。我没有实测，以上只来自官方推文、文档和更新日志。",
    "· 画面里的 Glossed over 是官方演示视频自带的标注，不是插件界面。",
    "· 第 1 期讲过的“模组默认开着”指模组这个功能；这个内置插件默认是关的，要自己开。",
    "· 有用户在官方仓库反馈：按提示开启时提示 Plugin is not installed in this project（issue #99071，10 月 3 日还没解决），这是用户反馈，不是官方结论。",
    "",
    "资料来源（2026 年 10 月 3 日读的官方页面）",
    *[f"· {n}：{u}" for n, u in LINKS],
    "",
    "补充说明",
    "· 画面里的官方演示视频、推文和文档页面来自 @ClaudeDevs（X 平台）和 Anthropic 官方网站，仅作介绍和评论引用，版权归原作者；",
    "· 封面里的像素宇航员取自 claude.dev 官方页面，版权归 Anthropic；",
    "· 功能、版本号会变，以官方文档为准；",
    "· 配音：曼波声线（AI 生成）；剪辑：Claude Code（Sonnet 5.5）。",
])
assert len(desc) <= 2000, len(desc)

info = {
    "platform": "B站（合集「Claude Code相关」，id 9223239；投稿页里要自己点开“加入合集”下拉选，别凭印象）",
    "status": "未投稿（封面选定 A、标题已定；待用户把 mp4 拖进上传页 → 我填表 → 用户说“发布”才点“立即投稿”；片尾清单草稿和配音 6 句机器分低的还没听）",
    "title": TITLE,
    "title_note": "用户 2026-10-03：“标题为：YouShouldKnow 新插件帮你在Agent Loop开发中复盘，或者你想一个新的标题”，随后补一句“比如一个视频了解Claude新插件”。我写成上面这句：保留“Agent Loop”和“复盘”，加“盯着”（官方文档 watches your back 的说法；官方说它是 Claude 干长活时在旁边看着并留便条，不是事后复盘），开头用“一个视频了解”。投稿页上用户若手改标题，以页面为准。",
    "cover_text": COVER_TEXT,
    "video": f"{json.loads((HERE / '台本' / '录制稿.json').read_text(encoding='utf-8'))['slug']}_成片.mp4",
    "video_note": f"含悠一片头 {INTRO} s + 正片 {T['total']:.1f} s + 片尾 {OUTRO} s；2340×1080；正片版本 制作/00_整片/整片_v1.mp4；字幕是中英双语烧进画面，另有三份 SRT（时间含片头）",
    "cover_16x9": "制作/04_封面/封面_选定_16x9.png（= 封面_A_16x9.png，用户选定）",
    "cover_4x3": "制作/04_封面/封面_选定_4x3.png（= 封面_A_4x3.png）",
    "cover_note": "claude-code-cover 技能的版式：品牌色背景 + 官方像素宇航员（只用官方原帧 float2 / float3 / stand，没自己画新动作）+ 两行字。A = night + float2（别漏看重点 / Claude 新插件）；B = orange + float3（You should know / 官方新插件）；C = ivory + stand（它替你盯着 / Claude 的输出）。第一版我擅自换成了自己画的原创小机器人，用户说“太丑了，而且不是 claude 的形象”，已改回官方宇航员；原创版留在 制作/04_封面/_旧稿_原创角色/。",
    "category": "人工智能",
    "declaration": "含AI生成内容",
    "tags": ["claude", "Claude Code", "Anthropic", "AI编程", "插件", "人工智能", "AI工具", "新功能", "编程", "大模型"],
    "tags_backup": ["ClaudeDevs", "AI Agent", "效率工具", "模组"],
    "tags_note": "手敲的大写 Claude 会被拒，点“推荐标签”里的小写 claude；自动加的“原创”“短片”要删；每个标签加完等 2 s。",
    "chapters": chapters,
    "chapters_note": f"时间 = 正片时间 + 片头 {INTRO} s（取整到秒）；正片重渲或片头长度变了要重跑 make_submission.py。",
    "desc": desc,
    "youtube": "未定",
    "todo_after_publish": [
        "GitHub release（tag 建议 claude-code-03）要等用户定了提交 git 的事再做；README 的“视频存档”表加这一期。",
        "片尾清单（制作/00_整片/outro.json）是草稿，按第 1 期的内容写的，要用户确认。",
        "官方页面会变：这个插件的前提（第一方会话、遥测开着、组织可用）、版本号、官方仓库 issue #99071 的状态，都可能过期；简介里的“10 月 3 日读的”按这个日期算。",
    ],
}
(HERE / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "制作" / "_desc_final.txt").write_text(desc + "\n", encoding="utf-8")
print(f"投稿信息.json 已写：标题 {len(TITLE)} 字，简介 {len(desc)} 字，章节 {len(chapters)} 条")
for t, n in chapters:
    print(" ", t, n)
