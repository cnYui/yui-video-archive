# -*- coding: utf-8 -*-
"""投稿信息：从时间轴算出简介里的章节时间（正片时间 + 片头秒数），写 投稿信息.json 和 制作/_desc_final.txt。

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
SC = json.loads((HERE / "台本" / "录制稿.json").read_text(encoding="utf-8"))
META = json.loads((HERE / "台本" / "rules_meta.json").read_text(encoding="utf-8"))
INTRO, OUTRO = intro_seconds(), outro_seconds()
seg = {s["id"]: s for s in T["segs"]}


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


chapters = [["00:00", "开场：AI 做的界面为什么丑"], [mmss(seg["O3"]["s"] - 0.3 + INTRO), "规则从哪来：《Refactoring UI》"]]
for n in range(1, 21):
    m = META[str(n)]
    chapters.append([mmss(seg[f"S{n:02d}"]["s"] - 0.3 + INTRO), f"第 {n} 条 {m['title']}"])
chapters += [[mmss(seg["C1"]["s"] - 0.3 + INTRO), "回顾：20 条规则 + 两个练习"], [mmss(seg["C3"]["s"] - 0.3 + INTRO), "全书 50 章，这期只讲了不到一半"]]

TITLES = [
    "AI 做的界面为什么丑？《Refactoring UI》20 条设计规则 + 20 张前后对比图，一个视频讲完",
    "不会设计也能做出好看的界面：20 条 UI 设计规则，每条一张前后对比图（Refactoring UI 精选）",
    "X 长文整理的 20 条 UI 设计军规：从丑界面到好看界面，逐条看前后对比图（含配色、留白、字号）",
]
TITLE = TITLES[0]
COVER_TEXT = "人人都是 / UI设计师（白字 + 橙字、黑描边；候选 A：图 13 丑界面 → 好界面；B：图 17 图上文字；C：20 张对比图墙）"
LINKS = [
    ("龙海 @longhaiqwe123 的推文（带文章链接）", "https://x.com/longhaiqwe123/status/2106216781174251724"),
    ("原文：人人都是 UI 设计师（X 长文）", "https://x.com/i/article/2106193433576570880"),
    ("《Refactoring UI》官网（含两章免费样章和完整目录）", "https://refactoringui.com/"),
    ("墨问笔记：把一本书做成随叫随到的 Skill", "https://note.mowen.cn/detail/4LZPmLxZzVh6ffGRzhlyi"),
]
desc = "\n".join([
    "转载 / 二次创作：本片整理自 X 用户龙海（@longhaiqwe123）2026-10-03 发的长文《人人都是 UI 设计师》，推文：https://x.com/longhaiqwe123/status/2106216781174251724",
    "20 条设计规则出自《Refactoring UI》（Adam Wathan、Steve Schoger，官网 https://refactoringui.com/ ）；20 张前后对比图是书里的插图，经原文转载，版权归原作者所有，本片仅作介绍和评论引用。",
    "",
    "AI 几分钟就能做出一个产品，界面却可能丑得让人想走。这期把原文的 20 条设计规则一条条过一遍：每条一张“错误做法 / 正确做法”的对比图，讲清楚差在哪、为什么，数字都取自图里的标注。",
    "",
    "本期内容",
    *[f"{t} {n}" for t, n in chapters],
    "",
    "几处要说明",
    "· 文中的判断（用户耐心只有三秒、灰色要 8–10 档、每行 45–75 个字符等）是原文作者摘自书里的说法，视频里都挂了“作者说 / 书里说”，不是我的实测；",
    "· 图 10 左边的标题在手机上折成四行（原文文字写“两行”），图 19 右边的行间细线其实还在（变化在卡片外框和输入框描边），台词按图改了；图 14、图 18 左边角标是“？”不是“×”，因为那两张图左边并不算错，只是不够好；",
    "· 全书 50 章，这 20 条对应其中 21 章（第 11 条对应两章），不到一半；想看全书可以去官网，有两章免费样章；",
    "· 官网页面、点赞浏览量都会变，以原页面为准。",
    "",
    "资料来源（2026 年 10 月 5 日读的页面）",
    *[f"· {n}：{u}" for n, u in LINKS],
    "",
    "补充说明",
    "· 画面里的推文、官网和笔记页面截图来自 X、refactoringui.com 和墨问，文章封面和对比图来自龙海的文章，均仅作介绍和评论引用，版权归原作者；",
    "· 中英双语字幕；配音：温柔男生声线（AI 生成）；剪辑：Claude Code（Sonnet 5.5）。",
])
assert len(desc) <= 2000, len(desc)

info = {
    "platform": "B站（独立视频，不选合集）",
    "status": "未投稿。封面选 A（用户 2026-10-05 回“用封面A”）；用户 2026-10-05 说“短视频发布了之后，长视频版本也四个渠道发布”→ 等短视频发完，轮到本条：开四个创作页、资源管理器选中成片、用户拖进上传区说“拖好了”→ 我填表（标题用候选 1，片尾清单用现有草稿）→ 读回核对再点发布",
    "title": TITLE,
    "title_candidates": TITLES,
    "title_note": "封面大字 = 片名《人人都是UI设计师》（用户 2026-10-05 要求封面包含这几个字、文字样式白字 + 橙字 + 黑描边）；标题写详细、不和封面同一句；标题里不写浏览量等会变的数字。用户在投稿页里手改标题时以页面为准。",
    "cover_text": COVER_TEXT,
    "video": f"{SC['slug']}_成片.mp4",
    "video_note": f"含悠一片头 {INTRO} s + 正片 {T['total']:.1f} s + 片尾 {OUTRO} s；2340×1080；正片版本 制作/00_整片/整片_v1.mp4；字幕是中英双语烧进画面，另有三份 SRT（时间含片头）",
    "cover_16x9": "制作/04_封面/封面_选定_16x9.png（现在 = 封面_A_16x9.png；用户选了别的就换成封面_B / C_16x9.png）",
    "cover_4x3": "制作/04_封面/封面_选定_4x3.png",
    "cover_3x4": "制作/04_封面/封面_选定_3x4.png（竖屏封面，1080×1440）",
    "cover_note": "三个候选 × 三个比例（3:4 / 16:9 / 4:3）+ 封面_总览.png；脚本 制作/04_封面/make_cover_framed.py（短视频技能的框版：边框 6、橙色印花底）；第一版（非框版）已进 制作/04_封面/_旧稿/",
    "category": "待定：知识 › 设计·创意（或 科技 › 计算机技术；上一批独立视频用的是 人工智能 tid 231）",
    "declaration": "含AI生成内容（用户 2026-10-04 定“声明统一选AI”；B 站创作声明是单选，自己剪辑 + AI 配音的选这个，来源写在简介前两行；B 站发布后声明灰了改不了，发布时就选对）",
    "tags": ["UI设计", "界面设计", "设计规则", "Refactoring UI", "AI编程", "Tailwind CSS", "前端开发", "产品经理", "设计入门", "氛围编程"],
    "tags_note": "每个标签单独点输入框 → 输入 → Enter，间隔约 2 s；自动加的“原创”“短片”要删；加完读回核对有没有被静默丢掉的（2026-10-05 短视频那条：“Vibe Coding” 被静默丢掉两次，换成“氛围编程”才进）。",
    "chapters": chapters,
    "chapters_note": f"时间 = 正片时间 + 片头 {INTRO} s（取整到秒）；正片重渲或片头长度变了要重跑 make_submission.py。",
    "desc": desc,
    "youtube": "未定",
    "todo_after_publish": [
        "GitHub release 等用户定了提交 git 再做（成片放 Releases，不进 git；中文标题写在 release 标题里）；README 的“视频存档”表加这一期。",
        "片尾清单（制作/00_整片/outro.json）是草稿，要用户确认。",
        "素材（文章全文、图片）在 独立视频/素材/2026-10_人人都是UI设计师/，整个 素材/ 不进公开仓库。",
    ],
}

SOURCE_LINE = "整理自 X 用户龙海（@longhaiqwe123）2026-10-03 的长文《人人都是 UI 设计师》，规则出自《Refactoring UI》；图和截图版权归原作者，仅作介绍和评论引用。配音为 AI 生成（温柔男生声线）。"
RULES_LINE = "；".join(f"{n}.{META[str(n)]['title']}" for n in range(1, 21))
TOPICS10 = ["UI设计", "界面设计", "设计规则", "RefactoringUI", "AI编程", "VibeCoding", "前端开发", "产品经理", "设计入门", "TailwindCSS"]
info["douyin"] = {
    "title": "AI做的界面为什么丑？20条设计规则一个视频讲完",
    "desc": "\n".join([TITLE, "20 条规则：" + RULES_LINE, SOURCE_LINE]),
    "topics": ["UI设计", "界面设计", "AI编程", "产品经理", "设计规则"],
    "declaration": "内容由AI生成",
    "cover": "横屏长视频：横封面 4:3 = 封面_选定_4x3.png；竖封面 3:4 = 封面_选定_3x4.png",
}
info["xiaohongshu"] = {
    "title": "AI做的界面为啥丑？20条规则",
    "desc": "\n".join([TITLE, "", "20 条规则：" + RULES_LINE, "文中的判断是原文作者摘自书里的说法，数字别死记，相信你的眼睛。", SOURCE_LINE]),
    "topics": TOPICS10,
    "declaration": "笔记含AI合成内容（原创声明要关）",
    "cover": "3:4 = 封面_选定_3x4.png",
}
info["weixin_channels"] = {
    "short_title": "20条规则 救救丑界面",
    "desc": "\n".join([TITLE, SOURCE_LINE]),
    "topics": TOPICS10,
    "declaration": "视频标注：含AI生成内容",
    "location": "不显示位置",
    "collection": None,
    "cover": "只能从视频帧里选（长视频第 0 帧是悠一片头，不是封面）：编辑封面里挑一帧好看的规则画面，或先问用户",
}
for k in ("douyin", "xiaohongshu"):
    assert len(info[k]["title"]) <= (30 if k == "douyin" else 20), (k, len(info[k]["title"]))
assert 6 <= len(info["weixin_channels"]["short_title"]) <= 16
# 已发布以后重跑本脚本不要把线上结果冲掉：旧的 投稿信息.json 里有 published 就原样带过来
_old = HERE / "投稿信息.json"
if _old.exists():
    _o = json.loads(_old.read_text(encoding="utf-8"))
    if "published" in _o:
        info["published"] = _o["published"]
        info["status"] = _o.get("status", info["status"])
(HERE / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
(HERE / "制作" / "_desc_final.txt").write_text(desc + "\n", encoding="utf-8")
print(f"投稿信息.json 已写：标题 {len(TITLE)} 字，简介 {len(desc)} 字，章节 {len(chapters)} 条")
for t, n in chapters[:4] + chapters[-3:]:
    print(" ", t, n)
