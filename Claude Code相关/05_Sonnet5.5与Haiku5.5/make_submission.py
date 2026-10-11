# -*- coding: utf-8 -*-
"""投稿信息：从时间轴算出简介里的章节时间（正片时间 + 片头秒数），写 投稿信息.json 和 制作/_desc_final.txt。

  python make_submission.py

正片重渲、片头长度变了、台词改了，都要重跑一遍（要先有真实配音的 timeline.json，不是 --est 的）。投稿由用户自己点“立即投稿”（插件传不了 10 MB 以上的文件，要用户把 mp4 拖进上传框）。
标题、封面字、片尾清单都是我拟的草稿，用户要在投稿页里改就以页面为准（投稿后把线上标题同步回这里）。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds   # noqa: E402

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
assert not T.get("est"), "timeline.json 还是按字数估的，先用真实配音重跑 build_timeline.py（不带 --est）"
INTRO, OUTRO = intro_seconds(), outro_seconds()      # 共用片头片尾的时长（2026-10-03 起 4.8 s / 9.0 s）
cu = {q["id"]: q for q in T["cues"]}


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


# 简介里的章节（比左栏目录细）
CH = [("开场：官方护蛋演示", None), ("四款模型的价格", "N12"), ("Sonnet 5.5 的价格", "N23"),
      ("缓存读取减半", "N28"), ("Haiku 5.5 的两档价格", "N31"), ("订阅用户的 API 额度", "N40"), ("Sonnet 5.5 的能力", "N45"),
      ("Haiku 5.5 的能力", "N58"), ("怎么选", "N73")]
chapters = []
for name, cid in CH:
    t0 = 0.0 if cid is None else max(0.0, cu[cid]["s"] - 0.3)
    chapters.append([mmss(t0 + INTRO if cid else 0), name])

TITLE = "Opus5.5 VS Sonnet5.5 VS Haiku5.5 !一个视频看懂价格和能力"      # 用户 2026-10-10 自己定的标题（我先拟的是“Sonnet 5.5 和 Haiku 5.5 怎么选？Haiku 便宜 20 倍，能力差多少？…”，他直接发了这一句），已发布
COVER_TEXT = "价格 + 能力 / 一次看懂（候选 C：官方像素宇航员，用户 2026-10-10 选定；A = 价差 20 倍 / 差在哪？官方护蛋演示结果帧，B = 两款新模型 / 怎么选？官方吉祥物，都没选）"
LINKS = [
    ("Sonnet 5.5 发布页", "https://www.anthropic.com/claude-sonnet-5-5"),
    ("Haiku 5.5 发布页", "https://www.anthropic.com/claude-haiku-5-5"),
    ("价格页", "https://platform.claude.com/docs/en/about-claude/pricing"),
    ("模型总览", "https://platform.claude.com/docs/en/models/overview"),
    ("@claudeai 推文", "https://x.com/claudeai/status/2107894039626277339"),
    ("@ClaudeDevs 推文（护蛋演示）", "https://x.com/ClaudeDevs/status/2107895955144208813"),
]
desc = "\n".join([
    "Claude 最近发了两款新模型：Sonnet 5.5（九月底）和 Haiku 5.5（十月初）。这期只看价格和能力：官方护蛋演示开场，再把官方价格页、模型总览和两篇发布文章里的数字逐条过一遍，最后说怎么选。",
    "",
    "本期内容",
    *[f"{t} {n}" for t, n in chapters],
    "",
    "要点（来自官方发布页、价格页、模型总览和官方推文；价格是每百万 token）",
    "· 价格：Fable 5.1 $10 / $50；Opus 5.5 $4 / $20；Sonnet 5.5 $2 / $10；Haiku 5.5 提示 ≤ 10 万 token $0.10 / $0.50，超过 10 万 $0.50 / $2.50；Haiku 4.5 $1 / $5。Haiku 5.5 比 Sonnet 5.5 便宜 20 倍。",
    "· Sonnet 5.5：单价同 Sonnet 5；官方说同样的活最多便宜 30%、输出快 30% 以上；缓存读取十月初 $0.20 → $0.10，多数智能体任务再省约 20%；Sonnet 5 原定 9 月涨到 $3 / $15，官方说取消。",
    "· Haiku 5.5：官方说平均比 Haiku 4.5 便宜约 75%（短提示 90%、长提示 50%，已计入新分词器多用的 token，完整算式没写）；首个带思考力度档位的 Haiku；已在 Claude Platform 和 Claude Code 可用。",
    "· 订阅额度：Max 5x $100、Max 20x $200、Team 最多 $500 每月，可用于任何模型，到账时间官方没写。",
    "· 能力（Anthropic 公布，Sonnet 5.5 / Sonnet 5 / Opus 5.5）：Terminal-Bench 4.0 70.6% / 10.3% / 66.4%；GDPval-AA 1844 / 1449 / 1846；OSWorld 2.1 80.1% / 57.0% / 81.8%。八项里 Opus 5.5 领先七项，官方说开放复杂任务它更强。",
    "· Haiku 5.5 / Haiku 4.5 / GPT-6 Luna：GDPval-AA 1620 / 735 / 1437；OSWorld 离线子集 72.4% / 15.7% / 48.9%；Terminal-Bench 39.2% / 0.0% / 16.4%。官方说复杂编码任务仍选 Sonnet 5.5 或 Opus 5.5。",
    "",
    "几处要说明",
    "· 成绩都是 Anthropic 自己公布的，没有实测；同一个 Sonnet 5.5 在 Sonnet 页和 Haiku 页的部分数字不同，我只在同一页内比较。",
    "· 护蛋演示是官方挑的一道题；“快近四倍、便宜七成”是我按画面计时器算的，不是通用结论。",
    "· “输入 100 万 + 输出 20 万 token”的账是我按官方标价算的，不含折扣，Haiku 按提示都在 10 万以内算。",
    "· Sonnet 5.5 发布页价格表里的缓存读取 $0.20 是降价前的旧数，以官方价格页（$0.10）为准。",
    "",
    "资料来源（2026 年 10 月 10 日读的官方页面）",
    *[f"· {n}：{u}" for n, u in LINKS],
    "",
    "· 画面中的官方视频、推文和网页来自 Anthropic 官方网站、@claudeai、@ClaudeDevs（X），仅作介绍和评论引用，版权归原作者；封面里的官方形象版权归 Anthropic；价格会变，以官方页面为准。",
    "· 配音：温柔男生（AI 生成）；剪辑：Claude Code（Sonnet 5.5）。",
])
assert len(desc) <= 2000, len(desc)

info = {
    "platform": "B站（合集「Claude Code相关」，id 9223239；投稿页里要自己点开“加入合集”下拉选，别凭印象）",
    "status": "已投稿 BV1fcpi6oEmu（2026-10-10 13:44 北京（东京 14:44）ptime 1791611098，审核中；合集「Claude Code相关」接口已显示）；用户把 mp4 拖进上传页后我填表并点“立即投稿”",
    "title": TITLE,
    "title_note": "用户让我取的（2026-10-10）：具体数字（便宜 20 倍）+ 问题 + 资料来源，封面字“价格 + 能力 / 一次看懂”不在标题里重复；用户在页面里手改标题就以页面为准。",
    "cover_text": COVER_TEXT,
    "video": f"{json.loads((HERE / '台本' / '录制稿.json').read_text(encoding='utf-8'))['slug']}_成片.mp4",
    "video_note": f"含悠一片头 {INTRO} s + 正片 {T['total']:.1f} s + 片尾 {OUTRO} s；2340×1080；字幕是中英双语烧进画面，另有三份 SRT（时间含片头）",
    "cover_16x9": "制作/04_封面/封面_选定_16x9.png（= 候选 C，用户 2026-10-10 选定）",
    "cover_4x3": "制作/04_封面/封面_选定_4x3.png（= 候选 C）",
    "cover_note": "统一框版（白字 + 橙字黑描边 + 画面套边框 + 黄贴纸 + 印花底），脚本 短视频/skill/short-video/scripts/make_cover_framed.py；候选 A 真实演示帧、B 官方吉祥物“八爪鱼”、C 官方像素宇航员（claude-code-cover 的 mascot.py，bolt 动作）。用户选了 C；已用 cover_frame0.py 把 16:9 封面放进成片第 0 帧（原片备份在成片旁的 _成片_无封面帧.mp4）。",
    "category": "人工智能",
    "declaration": "含AI生成内容",
    "tags": ["claude", "Anthropic", "Sonnet 5.5", "Haiku 5.5", "大模型", "API", "人工智能", "AI工具", "AI编程", "价格"],
    "tags_backup": ["Opus 5.5", "AI Agent", "模型对比", "评测"],
    "tags_note": "手敲的大写 Claude 会被拒，点“推荐标签”里的小写 claude；自动加的“原创”“短片”要删；每个标签加完等 2 s，加完读回，被静默丢掉的换备用。",
    "chapters": chapters,
    "chapters_note": f"时间 = 正片时间 + 片头 {INTRO} s（取整到秒）；正片重渲或片头长度变了要重跑 make_submission.py。",
    "desc": desc,
    "youtube": "未定",
    "todo_after_publish": [
        "GitHub release 要等用户定了提交 git 的事再做；README 的“视频存档”表加这一期。",
        "片尾清单（制作/00_整片/outro.json）是草稿，要用户确认。",
        "官方页面会变：价格、缓存读取、订阅额度的发放、两页数字的差别都可能过期；简介里的“10 月 10 日读的”按这个日期算。",
    ],
}
(HERE / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "制作" / "_desc_final.txt").write_text(desc + "\n", encoding="utf-8")
print(f"投稿信息.json 已写：标题 {len(TITLE)} 字，简介 {len(desc)} 字，章节 {len(chapters)} 条")
for t, n in chapters:
    print(" ", t, n)
