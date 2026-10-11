# -*- coding: utf-8 -*-
"""投稿信息：从时间轴算出简介里的章节时间（正片时间 + 片头 4.8 s），写 投稿信息.json 和 制作/_desc_final.txt。

  python make_submission.py

正片重渲、片头长度变了、台词改了，都要重跑一遍。投稿由用户自己点“立即投稿”（插件传不了 10 MB 以上的文件，要用户把 mp4 拖进上传框）。
标题、封面字、片尾清单都是我拟的草稿，用户要在投稿页里改就以页面为准（投稿后把线上标题同步回这里）。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds   # noqa: E402

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "制作" / "00_整片" / "timeline.json").read_text(encoding="utf-8"))
INTRO, OUTRO = intro_seconds(), outro_seconds()      # 共用片头片尾的时长（2026-10-03 起 4.8 s / 9.0 s）
cu = {(q.get("key") or q["id"]): q for q in T["cues"]}


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


# 简介里的章节（比左栏目录细）：名字 + 台本里起了名字的字幕条（时间取这条开始前 0.3 s）
CH = [("开场：一个月 2000 多个 PR，她说没有逐个 Review", None), ("她的原话：倒着想，怎么让 AI 自己合并", "d1_start"), ("宝玉：这个质疑，他半年前也挨过", "x2_q"),
      ("算一笔账：每天 67 个 PR，一个人看不过来", "b1_pr"), ("抽样，不逐个看", "d3_taste"), ("pstack：她把做法写成了技能", "p1_sum"),
      ("第一样：给 AI 一双手和一双眼睛", "b2_two"), ("全自动模式 autopilot-full：验证者说了算", "p2_auto"), ("第二样：规矩，人眼是最弱的一层", "b4_rules"),
      ("早上看提交记录，睡得更好", "d7_env"), ("边界：撤得回的和撤不回的", "b6_q"), ("宝玉的提醒：模型、Token、验证", "b8_self"), ("收尾", "z_end")]
chapters = []
for name, k in CH:
    t0 = 0.0 if k is None else max(0.0, cu[k]["s"] - 0.3)
    chapters.append([mmss(t0 + INTRO) if k else "00:00", name])

TITLES = [
    "一个月合并2000多个PR，却不逐个Review：SpaceXAI工程师Lauren Tan怎么做到的？（访谈 + 演讲原话同传）",
    "AI时代为什么有人不再逐个Review PR？机器验证、写成规矩、事后抽查，再看哪些活不能放手",
    "晚上让AI自己合并，早上再抽查：Lauren Tan的“不Review”到底靠什么，宝玉提醒了三个前提",
]
TITLE = TITLES[0]
COVER_TEXT = "不再Review"                        # 封面 A；B = “2000个PR / 谁来审？”，C = “AI自己合并”（封面协定：封面短大字，标题详细，两边不写同一句）
LINKS = [
    ("Matt Pocock 的 YouTube 直播（2026-10-02 美国时间，65 分钟）", "https://www.youtube.com/watch?v=MN9dGgmLyso"),
    ("Lauren Tan 的演讲视频（X，2026-09-21，“here's how i shipped 2,500 PRs last month to production”）", "https://x.com/poteto/status/2102050467505430555"),
    ("Lauren Tan 推荐这场直播的推文", "https://x.com/poteto/status/2106134336705843554"),
    ("宝玉对这场直播的中文总结（X 长推文）", "https://x.com/dotey/status/2106635352609865925"),
    ("pstack（Cursor 插件，MIT）", "https://github.com/cursor/plugins/tree/main/pstack"),
    ("pstack 官方指南 · Run work while you sleep", "https://github.com/cursor/plugins/blob/main/pstack/docs/guide/07-overnight.md"),
]
SRC_LINE = "画面来自 Matt Pocock 的 YouTube 直播（2026-10-02）、Lauren Tan 在 X 上发的演讲视频、推文和 GitHub 页面，版权归原作者，仅作介绍、评论和翻译引用；访谈和演讲的中文是 AI 同传，可能有误，以原话为准。"
AI_LINE = "配音：温柔男生声线（AI 生成）；剪辑：Claude Code（Sonnet 5.5）；含 AI 生成内容。"
desc = "\n".join([
    SRC_LINE,
    AI_LINE,
    "",
    "Lauren Tan（网名 poteto，在 SpaceXAI 做 Grok Bot，pstack 的作者）说，她一个月合并了 2000 多个 PR，却不逐个 Review：晚上让 AI 自己验证、自己合并，早上再看提交记录、抽查。这期用她的访谈和演讲原话（中文同传 + 中英字幕），加上宝玉的长文总结，讲她怎么把关，以及哪些情况不能照着学。",
    "",
    "本期内容",
    *[f"{t} {n}" for t, n in chapters],
    "",
    "要点",
    "· 抽样代替逐个看：她说，每道菜都尝不过来，更像抽样；每天挑一些 PR 仔细看，看出共性问题就去改环境，不去修某一个 AI。",
    "· 机器先验收：让 AI 像真人用户一样把程序跑起来、点一遍、抓追踪记录；她说这是进 Cursor 后写的第一个技能。",
    "· 规矩写进代码库：她演讲里那张表，AI 犯了错往哪一层补——代码库、静态分析（lint / 编译器 / CI）、规则、技能、风格指南；最后一层只能靠人在 Review 里盯，PR 来得太快，这根本不可能。",
    "· pstack 官方文档：autopilot-full 里每个 PR 有一个负责的 AI，但要一组独立验证者给出干净的裁决才允许合并；autopilot-stack 则不合并，留给人审；官方指南写着“早上审的是决策，不用把整晚重读一遍”。",
    "· 边界：她自己说走到这一步非常难；改动撤得回、能自动验证的活更容易放手，撤不回又难验证的，她说没有答案。宝玉提醒了三个前提：模型要够强、Token 要够烧、验证不能全交给 AI 且方向要人来指（这三条是宝玉自己的点评，不是访谈内容）。",
    "",
    "几处要说明",
    "· “2000 多个”是她自己报的：演讲首页写 2000，推文写 2500，访谈里她口头说“两千、两千五”，不是官方统计，也没有说明口径。",
    "· “不逐个 Review”指合并之前；她自述合并之后还会 Review、早上看提交记录、每天抽查，并不是没人看。",
    "· “fuzz（模糊测试）”“到处点”是她在访谈里的口语；pstack 官方文档的写法是独立验证者 + 在真实界面上实测。",
    "· 宝玉写“半年前说自己不怎么 Review PR”是他的回忆，我没有找到那条原推。",
    "· 两位说的都是他们各自的做法，不是对所有团队的建议。",
    "",
    "资料来源（2026 年 10 月 5 日读的页面）",
    *[f"· {n}：{u}" for n, u in LINKS],
])
assert len(desc) <= 2000, len(desc)

# 其余三个平台（用户 2026-10-05：“长视频也发四个平台”）：标题取推荐的第 1 个的限长版，和同题短视频的标题错开（写“完整版”）
P_TITLE = {"douyin": "完整版：她为什么不再逐个Review PR（访谈+演讲）", "xiaohongshu": "不再逐个Review PR，完整访谈", "weixin_channels": "为什么不再逐个Review"}
assert len(P_TITLE["douyin"]) <= 30 and len(P_TITLE["xiaohongshu"]) <= 20 and 6 <= len(P_TITLE["weixin_channels"]) <= 16, {k: len(v) for k, v in P_TITLE.items()}
TOPICS_10 = ["AI编程", "代码审查", "CodeReview", "Cursor", "AIAgent", "软件工程", "程序员", "人工智能", "Grok", "pstack"]
TOPICS_5 = ["AI编程", "代码审查", "程序员", "AIAgent", "人工智能"]
DESC_SHORT = "\n".join([
    TITLES[0],
    SRC_LINE,
    AI_LINE,
    "",
    "Lauren Tan（网名 poteto，SpaceXAI 做 Grok Bot，pstack 的作者）说她一个月发了 2000 多个 PR，却不逐个 Review：晚上让 AI 自己验证、自己合并，早上再看提交记录、抽查。",
    "· 她的做法：抽样代替逐个看；让 AI 像真人用户一样把程序跑一遍；把 AI 犯过的错写成 lint 规则；pstack 官方文档里的全自动模式要一组验证者给出“干净”裁决才允许合并。",
    "· 边界：走到这一步非常难，撤不回、又难验证的活她没有答案；宝玉提醒了三个前提（模型、Token、验证，是他自己的点评）。",
    "· “2000 多个”是她自己报的：演讲首页写 2000，推文写 2500，不是官方统计；她说的是合并之前不逐个看，合并之后仍会看、早上抽查。",
])
assert len(DESC_SHORT) + sum(len(t) + 2 for t in TOPICS_10) < 1000, len(DESC_SHORT)

info = {
    "platform": "B站 + 抖音 + 小红书 + 视频号（2026-10-05 用户定四个平台；B 站不选合集：独立视频）",
    "status": "未发布（2026-10-05 用户：并行、封面用 A、短视频发完后长视频也发四个平台；标题按推荐的第 1 个；等用户把 mp4 拖进各平台上传区 → 我填表读回 → 点发布）",
    "title": TITLE,
    "title_candidates": TITLES,
    "title_note": "标题写详细（对象、数字、结论），不和封面字“不再Review”是同一句；第 1 个最直接，第 2 个最贴“为什么”，第 3 个带上宝玉的三个前提。投稿页上用户若手改标题，以页面为准。",
    "cover_text": COVER_TEXT,
    "video": f"{json.loads((HERE / '台本' / '录制稿.json').read_text(encoding='utf-8'))['slug']}_成片.mp4",
    "video_note": f"含悠一片头 {INTRO} s + 正片 {T['total']:.1f} s + 片尾 {OUTRO} s；2340×1080；正片版本 制作/00_整片/整片_v1.mp4；字幕是中英双语烧进画面，另有三份 SRT（时间含片头）",
    "cover_16x9": "制作/04_封面/封面_选定_16x9.png（用户 2026-10-05 选定 A）",
    "cover_4x3": "制作/04_封面/封面_选定_4x3.png",
    "cover_3x4": "制作/04_封面/封面_选定_3x4.png（抖音竖封面 / 小红书用；A 的 3:4 版式 2026-10-05 补做）",
    "frame0": "成片第 0 帧 = 选定的 16:9 封面（cover_frame0.py，原片留 不再Review_成片_无封面帧.mp4）；视频号“编辑封面”选第 0 帧",
    "cover_note": "A = Lauren 的安静帧（访谈里 Matt 提问时她笑着听）+ “不再Review”；B = 她演讲里的三张 GitHub 贡献曲线 + “2000个PR / 谁来审？”；C = 并排画面 + “AI自己合并”。画面都是第三方素材（YouTube 直播 / X 演讲视频），封面 png 不进公开仓库。推荐 A。",
    "category": "人工智能（接口 tid 231）",
    "declaration": "含AI生成内容；来源写简介里的链接（YouTube 直播、X 演讲和推文）；是否选“转载”由用户定",
    "tags": ["AI编程", "代码审查", "Code Review", "Cursor", "AI Agent", "软件工程", "程序员", "人工智能", "Grok", "pstack"],
    "tags_backup": ["SpaceX", "Lauren Tan", "AI工具", "大模型"],
    "tags_note": "手敲的大写 Claude 会被拒，点“推荐标签”里的小写；自动加的“原创”“短片”要删；每个标签加完等 2 s；加完读回，被丢掉的换备用。",
    "douyin": {"title": P_TITLE["douyin"], "desc": DESC_SHORT, "topics": TOPICS_5, "declaration": "内容由AI生成", "collection": None, "cover": "竖封面 3:4 = 封面_选定_3x4.png；横封面 4:3 = 封面_选定_4x3.png", "published": None},
    "xiaohongshu": {"title": P_TITLE["xiaohongshu"], "desc": DESC_SHORT, "topics": TOPICS_10, "declaration": "笔记含AI合成内容（原创声明关）", "cover": "3:4 = 封面_选定_3x4.png", "published": None},
    "weixin_channels": {"short_title": P_TITLE["weixin_channels"], "desc": DESC_SHORT, "topics": TOPICS_10, "declaration": "视频标注：含AI生成内容", "location": "不显示位置", "collection": None, "cover": "成片第 0 帧 = 选定封面；编辑封面选第 0 帧", "published": None},
    "chapters": chapters,
    "chapters_note": f"时间 = 正片时间 + 片头 {INTRO} s（取整到秒）；正片重渲或片头长度变了要重跑 make_submission.py。",
    "desc": desc,
    "youtube": "未定（只发 B 站）",
    "todo_after_publish": [
        "GitHub release（tag 建议 independent-no-more-review）要等用户定了提交 git 的事再做；独立视频 README 的表和根 README 的“视频存档”表加这一条。",
        "片尾清单（制作/00_整片/outro.json）是草稿，用户没确认。",
        "机器识别分低的配音句子没人听过（见 制作/02_配音 的 qa 报告），用户要耳朵听。",
        "页面会变：pstack 版本 / 文档、两条推文的互动数、直播观看数都会变；简介里的“10 月 5 日读的”按这个日期算。",
    ],
}
(HERE / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "制作" / "_desc_final.txt").write_text(desc + "\n", encoding="utf-8")
print(f"投稿信息.json 已写：标题 {len(TITLE)} 字，简介 {len(desc)} 字，章节 {len(chapters)} 条")
for t, n in chapters:
    print(" ", t, n)
