# -*- coding: utf-8 -*-
"""6 期的交付包文字：标题 3×3（3 个候选 × B 站 / 抖音 / 小红书；视频号 2026-10-06 起不发）+ 各平台默认项（简介、话题、标签、声明、来源）→ 写进每期的 投稿信息.json。

  python series_publish.py            6 期全写（只改 titles / source / 各平台字段 / 说明，不动 approval / published）
  python series_publish.py 3          只写第 3 期
  之后：python D:\\大疆\\短视频\\skill\\short-video\\scripts\\check_titles.py <本期目录>   按各平台要求量字数

口径：简介前两行写转载 / 二次创作来源（B 站“转载”要填来源）；Tim 自称的数字挂名，不写成事实；声明统一选 AI；位置不选；话题抖音 5 / 小红书 10、B 站标签 10 个。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402

X_URL = D.TWEET_SHOW_URL
SUB_URL = D.SUB_URL
SRC_LINE = (f"转载 / 二次创作：整理自澳大利亚作家 Tim Denning（@Tim_Denning）的文章《I'm 38. If You're in Your 20's or 30's, Read This.》36 条忠告，"
            f"X 长文 2026-01-20：{X_URL} ；Substack 首发 2025-01-21：{SUB_URL}（两个版本正文一致）。")
NOTE_COMMON = ("几处要说明\n"
               "· 视频里的判断都是 Tim Denning 在文章里的说法，不是我的建议或实测；他简介自称“10 亿+ 阅读、赚了 600 万美元以上”、自述“银行干了十年、2021 年辞职”，这些没有独立核实，视频里都挂了“自称 / 自述”；\n"
               "· 文章写于他 38 岁时（2025 年 1 月），2026 年 1 月在 X 上原文重发，年龄、“去年”等口径都是 2025 年初的；\n"
               "· 画面里的文章页面、作者主页、推文卡片、作者照片来自 Substack 和 X 的公开页面，文章配图为 Midjourney 生成（原文标注 Image Credit-Midjourney），版权归原作者，仅作介绍和评论引用；\n"
               "· X 长文浏览量 2800 万+ 是 2026-10-05 的页面读数，会变。\n\n"
               "中英双语字幕；配音：温柔男生声线（AI 生成）；剪辑：Claude Code（Sonnet 5.5）。")

# 每期：titles（3 候选 × 4 平台）、要点（简介 / 正文用）、话题 / 标签
PUB = {
    1: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="自称10亿阅读的作家Tim Denning：38岁写下36条忠告，第一条就说35岁会分出两种人",
                 douyin="自称10亿阅读的作家：35岁会分出两种人", xiaohongshu="自称10亿阅读作家的35岁忠告"),
            dict(id=2, angle="数字悬念",
                 bilibili="X上浏览2800万的36条忠告，第一条就在吓人：35岁，冒险的人和没冒险的人差在哪？",
                 douyin="2800万浏览的忠告：35岁差在哪？", xiaohongshu="2800万人看过的36条忠告"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="自称10亿阅读的作家劝20多岁的人别等35岁才后悔，但这篇全是个人经验，一项研究都没引用",
                 douyin="35岁忠告要不要听？全是个人经验，没引用研究", xiaohongshu="35岁忠告，先泼盆冷水"),
        ],
        points=["第 1 条 冒险：不冒险攒下的是后悔，后悔让人老得更快；", "第 4 条 标准：标准高到被当成疯子，也别当平均人；", "第 5 条 常规路：拿学位、欠债、挑份假装是毕生事业的工作；", "第 6 条 情绪：听到不同意见还不上头，是聪明的标志。"],
        hook="自称10亿阅读的作家 Tim Denning，38 岁写下 36 条忠告，X 上浏览 2800 万+。这一期挑 4 条：",
        tags=["人生忠告", "个人成长", "自我提升", "35岁", "认知升级", "冒险", "Tim Denning", "20多岁", "职场", "观点"],
        topics=["人生忠告", "个人成长", "自我提升", "35岁", "认知升级", "冒险", "TimDenning", "20多岁", "职场", "观点"],
    ),
    2: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="你最爱的人倒在街上流血，有人掏出一把小刀说他来做手术：Tim Denning引的这个比方，讲透了“人好”为什么不够",
                 douyin="人好、守时、孝顺，可你手里只有一把小刀", xiaohongshu="人好不够，要有本事"),
            dict(id=2, angle="数字悬念",
                 bilibili="每天回复X评论14小时，坚持一年：自称10亿阅读的作家Tim Denning说，执念是成为高手最快的路",
                 douyin="每天回复评论14小时坚持一年？", xiaohongshu="每天评论14小时坚持一年"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="执念是成为高手最快的路？Tim Denning自己都说14小时不休息近乎愚蠢，没撑下来的人文中没提",
                 douyin="执念救人？没撑下来的人，文里没提", xiaohongshu="执念是捷径？先看没撑下来的人"),
        ],
        points=["寓言（文中署名 Jason Pargin）：亲人受重伤倒在街上，来了个拿小刀的人要动手术，说自己人好、守时、孝顺——社会需要的是能止血的人；", "第 3 条 执念：从什么都有点兴趣，变成对一件事彻底着迷；", "第 12 条 疯子：Tim 说他见过一个每天回复 X 评论 14 小时、坚持一年的人；", "第 8 条 难事：据 Tim 自述，小时候家里两处房子都因破产没了，现在把它看成赢面。"],
        hook="一个比方讲透“人好”为什么不够：自称10亿阅读的作家 Tim Denning 在 38 岁的忠告里，引了作家 Jason Pargin（旧笔名 David Wong，2012 年 Cracked 文章《6 Harsh Truths That Will Make You a Better Person》）的一个比方。",
        tags=["人生忠告", "个人成长", "自我提升", "执念", "技能", "Tim Denning", "认知升级", "20多岁", "寓言", "观点"],
        topics=["人生忠告", "个人成长", "自我提升", "执念", "技能", "TimDenning", "认知升级", "20多岁", "寓言", "观点"],
    ),
    3: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="自称10亿阅读的作家Tim Denning问过总经理和CEO：爬公司梯子的人，多数希望当初没爬",
                 douyin="作家称问过CEO：多数希望当初没爬", xiaohongshu="作家称：多数CEO后悔爬梯子"),
            dict(id=2, angle="数字悬念",
                 bilibili="8小时给无聊的工作，就留1小时早晨给自己：Tim Denning的5条职场忠告，附一条隐身改名的玩笑",
                 douyin="8小时给工作，1小时给自己", xiaohongshu="8小时给工作1小时给自己"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="劝人别爬公司梯子的作家，自己的生意就在网上：Tim Denning的职场忠告该怎么听",
                 douyin="劝人离开公司的作家，生意就在网上", xiaohongshu="劝你离职的人，在卖什么"),
        ],
        points=["第 9 条 梯子：Tim 说问过总经理、CEO，多数人希望当初没爬，习惯了那份钱和地位就退不回去；", "第 10 条 早晨：每天 8 小时给无聊的工作，就留 1 小时早晨给自己；", "第 34 条 托儿所：多数公司是成年人的托儿所，裁员文化上一分钟“送上祝福”、下一分钟“你被解雇了”；", "第 35 条 融资：靠融资做独角兽是最蠢的幻想之一，新世界用免费社交媒体攒邮件列表就能开张；", "第 15 条 昵称：隐身、换个昵称，括号里还开了个玩笑，改叫 Tim Winterbottom。"],
        hook="“爬公司梯子的人，没一个开心。”自称10亿阅读的作家 Tim Denning 在 38 岁的忠告里这么说，自述银行干了十年。这一期挑 5 条职场相关的：",
        tags=["职场", "打工人", "辞职", "副业", "个人成长", "自由", "Tim Denning", "一人公司", "人生忠告", "职场思维"],
        topics=["职场", "打工人", "辞职", "副业", "个人成长", "自由", "TimDenning", "一人公司", "人生忠告", "职场思维"],
    ),
    4: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="“说自己不为钱的人，多半在自欺”：自称10亿阅读的作家Tim Denning的3条钱的忠告",
                 douyin="作家称：说自己不为钱的人多半在自欺", xiaohongshu="作家称说不为钱多半自欺"),
            dict(id=2, angle="数字悬念",
                 bilibili="Tim Denning自称1000美元不到5分钟变成12万，文里一个字没写怎么做到的：钱的3条忠告和1个要小心的数字",
                 douyin="1000美元5分钟变12万？文里没写", xiaohongshu="1000变12万，怎么做到的？"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="谈钱不丢人，但要小心没给方法的数字：Tim Denning的钱的忠告里，最吸引人的那个数据没有任何凭证",
                 douyin="谈钱不丢人，但这个数字没凭证", xiaohongshu="谈钱不丢人，数字要小心"),
        ],
        points=["第 16 条 计分板：说钱不重要，等于撤掉了计分板，没人要你负责；最糟的是浪漫的艺术家和一分钱不赚的业余爱好者；", "第 17 条 懂钱：不懂钱怎么运转，就得一辈子为钱打工，Tim 的出路是死磕搞懂它；", "第 36 条 人性：懂人性就能赚到想赚的钱，人都出于自利，去迎合它；", "要小心的数字：Tim 自称曾用 1000 美元不到 5 分钟变成 12 万，文里没写方法、标的、日期、凭证。"],
        hook="“说自己不为钱的人，多半在自欺。”自称10亿阅读、赚了600万美元以上的作家 Tim Denning，在 38 岁的忠告里这样谈钱。这一期挑 3 条：",
        tags=["理财思维", "赚钱", "认知升级", "个人成长", "财商", "Tim Denning", "副业", "人性", "人生忠告", "商业思维"],
        topics=["理财思维", "赚钱", "认知升级", "个人成长", "财商", "TimDenning", "副业", "人性", "人生忠告", "商业思维"],
    ),
    5: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="自称10亿阅读的作家Tim Denning：年纪越大越想把一些朋友留在身后，生孩子是自由的起点，陪父母要比觉得正常的更多",
                 douyin="作家称：朋友会换，父母不会等", xiaohongshu="作家称：朋友会换父母不会等"),
            dict(id=2, angle="数字悬念",
                 bilibili="20岁时被劝“生了孩子你的人生就完了”，2岁女儿成了最好的经历：Tim Denning的朋友、孩子、父母4条忠告",
                 douyin="20岁被劝别生孩子，后来呢？", xiaohongshu="被劝别生孩子的作家后来"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="38岁、有了孩子的人给20多岁的人的忠告，要不要照搬？Tim Denning的朋友、孩子、父母4条忠告",
                 douyin="38岁有娃的人的忠告，20多岁别照搬", xiaohongshu="20多岁别照搬38岁的忠告"),
        ],
        points=["第 7 条 朋友：年轻时挑朋友是为了好看，后来不在乎了，朋友就换了；别粗暴断联，慢慢少联系；", "第 2 条 孩子：20 岁时有人对 Tim 说“生了孩子你的人生就完了”，他却说这是一生最好的经历，“选你的难”；", "第 29 条 父母：陪父母要比你觉得正常的更多，他们很快会走；", "第 32 条 却说：把父母给你定的人生计划烧掉，AI 时代的规则全被打破，走自己的路。"],
        hook="“年纪越大，你越想把一些朋友留在身后。这很正常。”自称10亿阅读的作家 Tim Denning，写这篇时 38 岁、有个 2 岁的女儿。这一期挑 4 条：",
        tags=["人际关系", "友情", "亲子", "父母", "个人成长", "人生忠告", "Tim Denning", "成长", "家庭", "认知升级"],
        topics=["人际关系", "友情", "亲子", "父母", "个人成长", "人生忠告", "TimDenning", "成长", "家庭", "认知升级"],
    ),
    6: dict(
        titles=[
            dict(id=1, angle="事实陈述（主体 + 动作 + 数字）", recommend=True,
                 bilibili="“说自己很忙，是低地位的信号”：自称10亿阅读的作家Tim Denning的6条时间与专注忠告",
                 douyin="作家称：说自己很忙是低地位信号", xiaohongshu="作家称：很忙是低地位信号"),
            dict(id=2, angle="数字悬念",
                 bilibili="感觉8小时像1小时，才算心流：Tim Denning说管住多巴胺，比任何健康技巧都管用",
                 douyin="8小时像1小时，才算心流", xiaohongshu="8小时像1小时才叫心流"),
            dict(id=3, angle="泼冷水（但是 / 要说明的前提）",
                 bilibili="关掉新闻智商会自然升高？Tim Denning的忠告里，这一条文里没给任何依据：时间与专注的6条忠告",
                 douyin="关掉新闻智商会升高？文里没依据", xiaohongshu="关掉新闻智商会升高？"),
        ],
        points=["第 13 条 忙：忙意味着不会专注、生活失控，尽快删掉日历上的安排；", "第 14 条 安静：很多成功的人，比如基努·里维斯，安静得出奇，整场对话一句不说反而学到最多；", "第 19 条 多巴胺：管住多巴胺比任何健康技巧都管用（TikTok、Netflix、电子游戏……）；", "第 28 条 游戏、第 31 条 心流：感觉 8 小时像 1 小时，才有劲；", "第 21 条 新闻：Tim 说关掉新闻和政治智商会自然升高，文里没给依据。"],
        hook="“说自己很忙，是低地位的信号。”自称10亿阅读的作家 Tim Denning 在 38 岁的忠告里这么说。这一期挑 5 条时间与专注相关的：",
        tags=["时间管理", "专注力", "多巴胺", "自律", "个人成长", "心流", "Tim Denning", "效率", "人生忠告", "认知升级"],
        topics=["时间管理", "专注力", "多巴胺", "自律", "个人成长", "心流", "TimDenning", "效率", "人生忠告", "认知升级"],
    ),
}


# 用户 2026-10-05 夜指定的标题（具体的一句，B 站 / 抖音 / 小红书同一句；视频号 2026-10-06 起去掉）。第 6 期他写的是“自己很忙，是低地位的信号”，我补了“说”。
NEW_TITLES = {
    1: "如果你正值二三十岁，别等35岁再后悔",
    2: "如果你正值二三十岁，人好不够，要有本事",
    3: "公司是成年人托儿所",
    4: "说自己不为钱的人，多半在自欺",
    5: "朋友会换，父母不会等",
    6: "说自己很忙，是低地位的信号",
}

def main():
    nums = [int(a) for a in sys.argv[1:]] or sorted(PUB)
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        pb = PUB[n]
        full = NEW_TITLES[n]
        old_t = pb["titles"]
        pb = dict(pb)
        pb["titles"] = [dict(id=1, angle="用户定的标题（具体的一句）", recommend=True, bilibili=full, douyin=full, xiaohongshu=full),
                        dict(old_t[0], id=2, recommend=False, angle="备选：带“自称”挂名的描述版"),
                        dict(old_t[2], id=3)]
        d = ep_dir(ep)
        f = d / "投稿信息.json"
        info = json.loads(f.read_text(encoding="utf-8"))
        title1 = next(t for t in pb["titles"] if t.get("recommend"))
        desc_b = SRC_LINE + "\n" + pb["hook"] + "\n" + "\n".join("· " + p for p in pb["points"]) + "\n\n" + NOTE_COMMON
        desc_short = f"{title1['bilibili']}\n整理自 Tim Denning（Tim_Denning）36 条忠告文章（X 长文 2026-01-20 / Substack 2025-01-21），观点均为他本人的说法，10 亿阅读、600 万美元等为其简介自称；画面来自公开页面，文章配图为 Midjourney 生成，版权归原作者，仅作介绍和评论引用。配音为 AI 生成（温柔男生声线）。"
        info["slug"] = ep["slug"]
        info["video"] = f"独立视频/短视频/2026-10_{ep['name']}/{ep['slug']}_成片.mp4（用户拖进各平台上传区；不压缩、不绕 10 MB）"
        info["titles"] = pb["titles"]
        info["source"] = {"original_post": X_URL, "original_author": "Tim Denning @Tim_Denning（X 长文 2026-01-20；Substack Modern Freedom 首发 2025-01-21）", "project_or_site": SUB_URL + "；文章配图 Midjourney 生成（原文标注），版权归原作者"}
        info["bilibili"].update({"title": title1["bilibili"], "desc": desc_b, "tags": pb["tags"], "collection": None,
                                 "repost_source": f"转自 X：{X_URL}（Tim Denning @Tim_Denning，X 长文，2026-01-20；Substack 首发 2025-01-21）"})
        info["douyin"].update({"title": title1["douyin"], "desc": desc_short, "topics": pb["topics"][:5], "collection": None})
        info["xiaohongshu"].update({"title": title1["xiaohongshu"], "desc": title1["bilibili"] + "\n\n" + "\n".join("· " + p for p in pb["points"]) + "\n" + desc_short.split("\n", 1)[1], "topics": pb["topics"]})
        f.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"第 {n} 期：{f}")


if __name__ == "__main__":
    main()
