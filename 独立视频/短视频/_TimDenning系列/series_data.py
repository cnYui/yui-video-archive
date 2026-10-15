# -*- coding: utf-8 -*-
"""《Tim Denning 的 36 条忠告》竖屏短视频系列：6 期的台本 + 画面表 + 页面高亮点，一份数据源。

  python series_data.py            自检：每期句数 / 汉字数 / 估时，页面高亮点引用的句子和短语是不是都存在
  python gen_episode.py 1          生成第 1 期的 录制稿.json / plan.json / scenes.js / 台本.md / say_lines.txt（并同步引擎、页面图）

文章：Tim Denning（@Tim_Denning）《I'm 38. If You're in Your 20's or 30's, Read This.》36 条忠告
  X 长文 2026-01-20（https://x.com/Tim_Denning/status/2013552215097778231）；Substack 首发 2025-01-21（timdenning.substack.com，两个版本正文一致）。
  页面录屏用 Substack 公开页（X 长文在无头浏览器里是登录墙）；配图只有一张封面（Substack 页面标注 Image Credit-Midjourney），另有作者照片 / X 横幅。
口径（用户 2026-10-05：“查一下他是谁，用他的头衔来讲述文章中他的观点，分好几期，用他的配图”）：
  - 第三人称：叫 Tim / 这位作家，不用“我 / 他 / 她”开头；英文字幕尽量叫名字。
  - 头衔 = 他简介里的自称（X：Writer with 1B+ views that made me 7+ figures；Substack：Aussie writer with 1B+ views that made me $6M+. Quit my banking job in 2021.）：
    每期第 2 句挂名“简介自称”，数字全是自称，不当成事实说。
  - 文章里的判断都挂 “Tim 说 / 文中”；他没给依据的数字（1000 美元变 12 万、关新闻升智商）在泼冷水那拍明说“文里没给”。
  - 不碰过审风险大的条目：加密货币推荐（23）、宗教（33）、自杀 / 海洛因比喻（13 里的两句）、性 / 性病（27 里半句）、死亡体验（30）。
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAT = Path(r"D:\大疆\独立视频\素材\2026-10_TimDenning38岁忠告")
SUB_URL = "https://timdenning.substack.com/p/im-38-if-youre-in-your-20s-or-30s"
PROFILE_URL = "https://substack.com/@timdenning"
TWEET_ID = "2013552215097778231"
EMBED_URL = f"https://platform.twitter.com/embed/Tweet.html?id={TWEET_ID}&theme=light&hideThread=true&lang=en&dnt=true"
TWEET_SHOW_URL = f"https://x.com/Tim_Denning/status/{TWEET_ID}"

# 每期共用的“头衔”句子（简介原话：Substack 主页）
BIO_ZH = "简介自称 10 亿阅读、赚了 600 万美元以上"


def L(id_, zh, en, say=None, cut=None):
    d = dict(id=id_, zh=zh, say=say or zh, en=en)
    if cut:
        d["cut"] = cut
    return d


def M(needle, line, phrase, off, zh=None):
    """页面高亮点：needle = 页面里的英文原文子串（≤ 15 个词）；刷上的时刻 = 第 line 句里说到 phrase 的时刻 + off（phrase = None → 这句开口）；zh = 底部中文译文条。"""
    return dict(needle=needle, line=line, phrase=phrase, off=off, zh=zh)


def PG(key, marks, **opt):
    return dict(kind="page", key=key, marks=marks, opt=opt)


def PH(key, **opt):
    return dict(kind="photo", key=key, opt=opt)


def BIG(line, phrase, num, unit, desc, dur=2.6, off=0.0):
    return dict(line=line, phrase=phrase, num=num, unit=unit, desc=desc, dur=dur, off=off)


def SC(id_, name, shot, lines, tag=None, credit=None, bigs=None, kicker=None):
    return dict(id=id_, name=name, shot=shot, lines=lines, ui=dict(tag=tag, credit=credit, kicker=kicker), bigs=bigs or [])


CR_ART = "图：Substack · Modern Freedom 原文"
CR_BIO = "图：Substack · Tim Denning 主页"
CR_X = "图：X · @Tim_Denning"
CR_MJ = "图：Midjourney（Tim 文章配图）"
CR_FACE = "图：Tim Denning 作者照"
CR_BAN = "图：X · @Tim_Denning 横幅"

# 页面图规格：key → (怎么截, 起点, 终点)。A_n = 第 n 条忠告整段（从它的标题到下一条标题）；A_top = 页面顶部到第 1 条标题；A_21 / A_28 / A_29 = “Shorter lessons”列表里单条截图（避开 23 比特币 / 27 戒酒 / 30 死亡体验）；A_31 = 第 31 条
PAGES = {
    "X_t1": dict(kind="tweet", url=EMBED_URL, show=TWEET_SHOW_URL),
    "P_bio": dict(kind="profile", url=PROFILE_URL, h=700),
    "A_top": dict(kind="top"),
    "A_21": dict(kind="li_range", first="21.", last="22.", head=True, vw=420),          # “Shorter lessons”标题 + 第 21、22 条（只截这两条，不带后面的第 23 条比特币）
    "A_28": dict(kind="li_range", first="28.", last="28.", vw=420),
    "A_29": dict(kind="li_range", first="29.", last="29.", vw=420),
    "A_31": dict(kind="lesson", n=31, until="Less hours worked, more flow states."),
}
for _n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 19, 32, 34, 35, 36):
    PAGES[f"A_{_n}"] = dict(kind="lesson", n=_n)
# 第 13 条：同一段里有 heroin / su!cide 两句（台本跳过的），只截不含它们的片段
PAGES["A_13"] = dict(kind="lesson", n=13, until="Busyness is a red flag.")            # 标题 + 第一句
PAGES["A_13p"] = dict(kind="para_lines", starts="The key to life is to not be busy", lines=4, vw=420)   # “The key to life…” 这段只要前两行（到 Eliminate calendar events as quickly）
PAGES["A_13q"] = dict(kind="para_lines", starts="Busyness isn't cool.", lines=None, vw=420)

EPISODES = []

# ═════════════════════════════════════════════════════════════════════ 第 1 期：35 岁分水岭（第 1、4、5、6 条）
EPISODES.append(dict(
    num=1, slug="TimDenning忠告1_35岁分水岭", name="TimDenning忠告1_35岁分水岭",
    hook=["10亿阅读的作家", "说35岁会分出两种人"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ①",
    scenes=[
        SC("H0", "钩子", PG("A_top", [
            M("When you turn 35 you'll see the difference", "N01", "35 岁", -0.3, "35 岁那年，你会看出冒险的人和没冒险的人的差别"),
        ]), [
            L("N01", "“35 岁那年，你会看出谁冒过险。”",
              "“By 35, you'll see who took risks and who didn't.”",
              "三十五岁那年，你会看出谁冒过险。"),
        ], tag="文章第 1 条", credit=CR_ART),
        SC("B1", "背书·简介", PG("P_bio", [
            M("Aussie writer with 1B+ views that made me $6M+", "N02", "10 亿阅读", -0.6, "简介原话：10 亿+ 阅读的澳洲作家，赚了 600 万美元+"),
            M("Quit my banking job in 2021", "N03", "2021 年", -0.3, "简介原话：2021 年辞掉了银行的工作"),
        ]), [
            L("N02", "出自 Tim Denning，简介自称 10 亿阅读、赚 600 万美元以上。",
              "That's Tim Denning, whose bio claims 1B+ views and $6M+ earned.",
              "出自 Tim Denning，简介自称十亿阅读、赚六百万美元以上。"),
            L("N03", "澳洲人，自述银行干了十年，2021 年辞职，转做网上写作。",
              "An Aussie who says he spent ten years in banking, then quit in 2021 to write online.",
              "澳洲人，自述银行干了十年，二零二一年辞职，转做网上写作。"),
        ], tag="简介自称", credit=CR_BIO),
        SC("B2", "背书·数据", PG("X_t1", [
            M("@Tim_Denning", "N04", "36 条", -0.2, "X 账号 @Tim_Denning（已认证）"),
            M("Jan 20, 2026", "N04", "浏览", -0.4, "2026 年 1 月 20 日，以 X 长文重发（正文没改）"),
        ], fit=True), [
            L("N04", "2025 年首发的 36 条忠告，写于 38 岁，X 上浏览 2800 万。",
              "First published in 2025, written at 38: these 36 lessons have drawn 28 million views on X.",
              "二零二五年首发的三十六条忠告，写于三十八岁，X 上浏览两千八百万。"),
        ], tag="X 长文", credit=CR_X, bigs=[BIG("N04", "浏览", "2800万+", "次浏览", "X 上这篇长文（2026-10-05 读取）", 2.2, -0.2)]),
        SC("L1", "第1条", PG("A_1", [
            M("When you turn 35 you'll see the difference", "N05", "第一条", 0.0, "第 1 条：35 岁，你会看出谁冒过险、谁没有"),
            M("Not taking risks leads to regrets which ages you faster", "N06", "后悔", -0.6, "不冒险只会攒下后悔，后悔让人老得更快"),
            M("You always move decisions to the future", "N07", "推到以后", -0.2, "决定总被推到以后，到时没人为它负责"),
            M("overthinking $100 purchases", "N08", "100 美元", -0.1, "连 100 美元的东西都要纠结？醒醒"),
        ]), [
            L("N05", "第一条：觉得自己老不老，看怎么活的。",
              "Lesson 1: how old you feel depends on how you lived.",
              "第一条：觉得自己老不老，看怎么活的。"),
            L("N06", "不冒险，攒下的是后悔，后悔让人老得更快。",
              "Playing it safe stacks up regrets, and regrets age you faster.",
              "不冒险，攒下的是后悔，后悔让人老得更快。"),
            L("N07", "决定总被推到以后，到时没人为它负责。",
              "Decisions keep getting pushed to later, when nobody is accountable.",
              "决定总被推到以后，到时没人为它负责。"),
            L("N08", "连 100 美元的东西都纠结？Tim 的态度：醒醒。",
              "Overthinking a $100 purchase? Tim's reply: wake up.",
              "连一百美元的东西都纠结？Tim 的态度：醒醒。"),
        ], tag="第 1 条 · 冒险", credit=CR_ART),
        SC("L4", "第4条", PG("A_4", [
            M("Raise your standards so high", "N09", "第四条", 0.0, "第 4 条：标准高到别人觉得你是疯子，也别当平均人"),
            M("It helps them feel good about where they're at in life", "N10", "找台阶", -0.7, "这是自我安慰，让人对现状好受些"),
            M("A lot of decisions are automated for you", "N11", "自动做完", -0.2, "标准一高，很多决定自动替你做完"),
        ]), [
            L("N09", "第四条：标准高到被当成疯子，也别当平均人。",
              "Lesson 4: raise your standards until people call you crazy. Never settle for average.",
              "第四条：标准高到被当成疯子，也别当平均人。"),
            L("N10", "Tim 说，嫌你疯的人，是在给自己找台阶。",
              "Tim says people who call you crazy are just making excuses for themselves.",
              "Tim 说，嫌你疯的人，是在给自己找台阶。"),
            L("N11", "标准一高，很多决定自动做完：少刷剧，少喝酒，少久坐。",
              "Higher standards make decisions for you: less binge-watching, less drinking, less sitting.",
              "标准一高，很多决定自动做完：少刷剧，少喝酒，少久坐。"),
        ], tag="第 4 条 · 标准", credit=CR_ART),
        SC("L5", "第5条", PG("A_5", [
            M("Never follow the conventional path", "N12", "第五条", 0.0, "第 5 条：别走常规路，它最无聊，竞争也最多"),
            M("Get a degree, get into debt, choose a job you pretend is your life's work", "N13", "标准路线", -0.2, "拿学位、欠一身债、挑一份假装是毕生事业的工作"),
            M("I could predict what would happen in a week", "N14", "猜得到", -0.9, "下周会发生什么，一眼就能预测"),
            M("Mighty Melbourne burger with beef or the Simon Says chicken burger", "N15", "牛肉堡", -0.5, "唯一的惊喜：吃牛肉堡还是鸡肉堡"),
        ]), [
            L("N12", "第五条：别走常规路，那里最无聊，竞争也最挤。",
              "Lesson 5: skip the conventional path. It's the most boring and the most crowded.",
              "第五条：别走常规路，那里最无聊，竞争也最挤。"),
            L("N13", "Tim 总结的标准路线：拿学位，欠一身债，挑份假装是毕生事业的工作。",
              "The standard path, per Tim: a degree, some debt, and a job you pretend is your life's work.",
              "Tim 总结的标准路线：拿学位，欠一身债，挑份假装是毕生事业的工作。"),
            L("N14", "怎么发现的？总在无聊，下周会发生什么，一眼猜得到。",
              "How did Tim notice? Always bored, and the whole week was predictable.",
              "怎么发现的？总在无聊，下周会发生什么，一眼猜得到。"),
            L("N15", "唯一的悬念：午饭吃牛肉堡，还是鸡肉堡。",
              "The only suspense: a beef burger or a chicken burger for lunch.",
              "唯一的悬念：午饭吃牛肉堡，还是鸡肉堡。"),
        ], tag="第 5 条 · 常规路", credit=CR_ART),
        SC("L6", "第6条", PG("A_6", [
            M("One of the clearest signs of intelligence", "N16", "第六条", 0.0, "第 6 条：听到不同意见还不上头，是聪明的标志"),
            M("Labels have dumbed us right down", "N17", "贴标签", -0.1, "标签让我们变笨：“不是这个，就是那个”"),
        ]), [
            L("N16", "第六条：听到不同意见还不上头，是聪明的标志。",
              "Lesson 6: hearing an opinion you disagree with without getting emotional is a sign of intelligence.",
              "第六条：听到不同意见还不上头，是聪明的标志。"),
            L("N17", "贴标签让人变笨：非此即彼，世界没那么简单。",
              "Labels make us dumber. The world is too nuanced for 'this or that'.",
              "贴标签让人变笨：非此即彼，世界没那么简单。"),
        ], tag="第 6 条 · 情绪", credit=CR_ART),
        SC("C1", "泼冷水", PG("A_top", [
            M("I'm not that smart but these experiences", "N18", "不算聪明", -0.9, "我不算聪明，只是这些经历给了我一些有力的教训"),
        ]), [
            L("N18", "不过全是个人经验，没引用一项研究。Tim 自己也说，自己不算聪明。",
              "But it's all personal experience, with no study cited. Tim admits he's 'not that smart'.",
              "不过全是个人经验，没引用一项研究。Tim 自己也说，自己不算聪明。"),
        ], tag="Tim 自己说", credit=CR_ART),
        SC("E1", "金句", PH("face", zoom=0.07, fx=0.5, fy=0.42), [
            L("N19", "后悔都是一次次“以后再说”攒出来的，35 岁只是来收账。",
              "Regret piles up one 'later' at a time. Thirty-five just comes to collect.",
              "后悔都是一次次“以后再说”攒出来的，三十五岁只是来收账。"),
        ], tag="写这篇时 38 岁", credit=CR_FACE),
    ]))

# ═════════════════════════════════════════════════════════════════════ 第 2 期：那把小刀（第 3、12、8 条）
EPISODES.append(dict(
    num=2, slug="TimDenning忠告2_那把小刀", name="TimDenning忠告2_那把小刀",
    hook=["人好、守时、孝顺", "可你拿的是把小刀"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ②",
    scenes=[
        SC("H0", "寓言", PG("A_3", [
            M("Let's say that the person you love the most has just been shot", "N01", "最爱", -0.1, "假设你最爱的人倒在街上，血流不止"),
            M("Are you a doctor?", "N02", "是医生吗", -0.2, "“你是医生吗？”"),
            M("he is a nice guy, he is honest, he is always on time", "N02", "人好", -0.1, "答：不是，但我人好、诚实、从不迟到"),
        ]), [
            L("N01", "你最爱的人倒在街上流血，一个人掏出小刀，说要做手术。",
              "The person you love most lies bleeding in the street. A stranger pulls out a pocket knife to operate.",
              "你最爱的人倒在街上流血，一个人掏出小刀，说要做手术。",
              cut=[["流血，", "street."]]),
            L("N02", "你问：你是医生吗？对方说：不是，但人好、守时、孝顺。",
              "You ask: are you a doctor? No, the stranger says, but he's kind, punctual and a devoted son.",
              "你问：你是医生吗？对方说：不是，但人好、守时、孝顺。"),
        ], tag="文中的比方", credit=CR_ART),
        SC("H1", "寓意", PG("A_3", [
            M("society is full of people who need things", "N03", "社会", -0.1, "社会满是有需求的人：要房子、要吃的、要娱乐"),
            M("learning a unique set of skills, or the world will reject you", "N04", "世界照样拒绝", -0.7, "要么练出一套独特技能，要么被世界拒绝"),
            M("– Jason Pargin", "N05", "Jason Pargin", -0.3, "文末署名：Jason Pargin"),
        ]), [
            L("N03", "社会就是那个流血的人：要房子，要吃的，要娱乐。",
              "Society is the bleeding person: it needs houses, food and entertainment.",
              "社会就是那个流血的人：要房子，要吃的，要娱乐。"),
            L("N04", "拿着小刀的，是你。人再好，没有技能，世界照样拒绝。",
              "You're the one with the knife. However nice you are, the world rejects you without skills.",
              "拿着小刀的，是你。人再好，没有技能，世界照样拒绝。"),
            L("N05", "第三条里，Tim Denning 引了这个比方，署名 Jason Pargin。",
              "In lesson 3, Tim Denning quotes this parable, credited to Jason Pargin.",
              "第三条里，Tim Denning 引了这个比方，署名 Jason Pargin。"),
        ], tag="第 3 条 · 执念", credit=CR_ART),
        SC("L3", "解法", PG("A_3", [
            M("Chasing obsession is the fastest way to become a high performer", "N06", "解法", -0.2, "标题：执念，是成为高手最快的路"),
            M("all-out obsessed with one thing", "N07", "彻底着迷", -0.3, "对一件事彻底着迷：纯粹的投入和自律"),
            M("even my homeless friend Peter", "N08", "Peter", -0.5, "它救过我，也能救任何人，连无家可归的朋友 Peter"),
        ]), [
            L("N06", "简介自称 10 亿阅读的作家 Tim，给的解法是：执念。",
              "The writer who claims 1B+ views offers one fix: obsession.",
              "简介自称十亿阅读的作家 Tim，给的解法是：执念。"),
            L("N07", "从什么都有点兴趣，变成对一件事彻底着迷。",
              "Go from lukewarm interest to being all-out obsessed with one thing.",
              "从什么都有点兴趣，变成对一件事彻底着迷。"),
            L("N08", "Tim 说，这救过自己，也能救无家可归的朋友 Peter。",
              "Tim says it saved him, and can save anyone, even his homeless friend Peter.",
              "Tim 说，这救过自己，也能救无家可归的朋友 Peter。"),
        ], tag="第 3 条 · 执念", credit=CR_ART),
        SC("L12", "第12条", PG("A_12", [
            M("Maniacs are incredible", "N09", "第十二条", 0.0, "第 12 条：“疯子”很了不起，他们教你努力和执念能做到什么"),
            M("They replied to comments on X for 14 hours a day for a year", "N10", "14 个小时", -0.5, "每天在 X 上回复评论 14 小时，坚持一年"),
            M("made enough money to never work a job", "N11", "不上班", -0.7, "赚的钱够一辈子不用打工"),
            M("close to zero because it's hard work", "N12", "几乎为零", -0.2, "竞争几乎为零，因为这活太累"),
        ]), [
            L("N09", "第十二条：向“疯子”学习。Tim 说自己见过一个：",
              "Lesson 12: learn from maniacs. Tim says he met one:",
              "第十二条：向“疯子”学习。Tim 说自己见过一个："),
            L("N10", "每天回复 X 上的评论 14 个小时，坚持了一年。",
              "Someone replied to comments on X 14 hours a day, for a year.",
              "每天回复 X 上的评论十四个小时，坚持了一年。"),
            L("N11", "结果粉丝成群，赚的钱够一辈子不上班。",
              "The result: a big following, and enough money to never work a job.",
              "结果粉丝成群，赚的钱够一辈子不上班。"),
            L("N12", "Tim 的看法：竞争几乎为零，因为太苦了。",
              "Tim's view: competition is close to zero, because it's hard work.",
              "Tim 的看法：竞争几乎为零，因为太苦了。"),
        ], tag="第 12 条 · 疯子", credit=CR_ART,
            bigs=[BIG("N10", "14 个小时", "14", "小时 / 天", "回复 X 评论，连续一年（文中举例）", 3.0, -0.2)]),
        SC("L8", "第8条", PG("A_8", [
            M("The more hard things you do the more successful you become", "N13", "第八条", 0.0, "第 8 条：难事做得越多，你越成功"),
            M("we lost both our family homes to bankruptcy", "N14", "两处房子", -0.3, "童年时，我们家的两处房子都因破产没了"),
            M("Now I see it as a huge win", "N15", "赢面", -0.3, "现在我把它看成一个大赢面"),
        ]), [
            L("N13", "第八条：难事做得越多，越容易成功。",
              "Lesson 8: the more hard things you do, the more successful you become.",
              "第八条：难事做得越多，越容易成功。"),
            L("N14", "据 Tim 自述，小时候家里的两处房子都因破产没了。",
              "By Tim's own account, both family homes were lost to bankruptcy in his childhood.",
              "据 Tim 自述，小时候家里的两处房子都因破产没了。"),
            L("N15", "现在回头看，那是赢面：逼着练出了别人没有的本事。",
              "Looking back, he calls it a win: it forced skills most people never built.",
              "现在回头看，那是赢面：逼着练出了别人没有的本事。"),
        ], tag="第 8 条 · 难事", credit=CR_ART),
        SC("C1", "泼冷水", PG("A_12", [
            M("Commenting for 14 hours a day with no breaks is almost stupidity", "N16", "近乎愚蠢", -0.9, "每天不歇地评论 14 小时，近乎愚蠢"),
        ]), [
            L("N16", "Tim 自己都说，14 小时不休息近乎愚蠢。没撑下来的人，文中没提。",
              "Tim himself calls 14 hours without a break almost stupid. The ones who gave up go unmentioned.",
              "Tim 自己都说，十四个小时不休息近乎愚蠢。没撑下来的人，文中没提。"),
        ], tag="Tim 自己说", credit=CR_ART),
        SC("E1", "金句", PG("A_3", [
            M("no matter how inoffensive and courteous you are", "N17", "人再好", -0.1, "不管你多无害、多有礼貌"),
        ]), [
            L("N17", "人再好，也得带着能止血的本事。",
              "Be as nice as you like, but carry a skill that can stop the bleeding.",
              "人再好，也得带着能止血的本事。"),
        ], tag="第 3 条 · 执念", credit=CR_ART),
    ]))

# ═════════════════════════════════════════════════════════════════════ 第 3 期：别爬公司梯子（第 9、10、34、35、15 条）
EPISODES.append(dict(
    num=3, slug="TimDenning忠告3_别爬公司梯子", name="TimDenning忠告3_别爬公司梯子",
    hook=["10亿阅读的作家", "劝你别爬公司的梯子"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ③",
    scenes=[
        SC("H0", "钩子", PG("A_9", [
            M("No one who climbs the corporate ladder is happy", "N01", "没一个", -0.9, "爬公司梯子的人，没一个开心。这是个陷阱，选自由"),
        ]), [
            L("N01", "“爬公司梯子的人，没一个开心。”",
              "“No one who climbs the corporate ladder is happy.”",
              "“爬公司梯子的人，没一个开心。”"),
        ], tag="文章第 9 条", credit=CR_ART),
        SC("B1", "背书·简介", PG("P_bio", [
            M("Aussie writer with 1B+ views", "N02", "10 亿阅读", -0.6, "简介原话：10 亿+ 阅读的澳洲作家"),
            M("Quit my banking job in 2021", "N02", "银行", -0.2, "2021 年辞掉了银行的工作"),
        ]), [
            L("N02", "说这话的 Tim Denning，简介自称 10 亿阅读，自述银行干了十年。",
              "That's Tim Denning, whose bio claims 1B+ views and who says he spent ten years in banking.",
              "说这话的 Tim Denning，简介自称十亿阅读，自述银行干了十年。"),
        ], tag="简介自称", credit=CR_BIO),
        SC("L9", "第9条", PG("A_9", [
            M("I spoke to General Managers and CEOs about climbing the corporate ladder", "N03", "总经理", -0.4, "我找总经理、CEO 聊过爬公司梯子这件事"),
            M("Most of them wished they didn't", "N04", "希望当初", -0.3, "他们大多希望自己当初没爬"),
            M("You get accustomed to a certain amount of money and status", "N05", "习惯了", -0.2, "你习惯了那份钱和地位，就放不下了"),
        ]), [
            L("N03", "Tim 说，为这事专门问过总经理和 CEO。",
              "Tim says he asked general managers and CEOs about it.",
              "Tim 说，为这事专门问过总经理和 CEO。"),
            L("N04", "多数人的答案：希望当初没爬。",
              "Most of them said: I wish I hadn't climbed.",
              "多数人的答案：希望当初没爬。"),
            L("N05", "可爬久了，退不回去：习惯了那份钱和地位。",
              "But after a while there's no going back: you get used to the money and status.",
              "可爬久了，退不回去：习惯了那份钱和地位。"),
        ], tag="第 9 条 · 梯子", credit=CR_ART),
        SC("L10", "第10条", PG("A_10", [
            M("If you have 8 hours a day to work a boring job", "N06", "第十条", 0.0, "第 10 条：每天花 8 小时干无聊的工作，就留 1 小时早晨投资自己"),
            M("The life you dream of is built before and after work", "N07", "理想的生活", -0.1, "梦想的生活，建在上班前和下班后"),
            M("You'll never be less busy, have enough money, or know enough", "N08", "更闲", -0.2, "你永远不会更闲、更有钱、更懂行"),
        ]), [
            L("N06", "第十条：每天 8 小时给无聊的工作，就留 1 小时早晨给自己。",
              "Lesson 10: if a boring job gets 8 hours, keep one morning hour for yourself.",
              "第十条：每天八小时给无聊的工作，就留一小时早晨给自己。"),
            L("N07", "理想的生活，是在上班前和下班后建起来的。",
              "The life you dream of is built before and after work.",
              "理想的生活，是在上班前和下班后建起来的。"),
            L("N08", "不会有更闲、更有钱、更懂行的那一天。不开始，就永远不会开始。",
              "There's no day when you're less busy, richer or wiser. Don't start now and you never will.",
              "不会有更闲、更有钱、更懂行的那一天。不开始，就永远不会开始。"),
        ], tag="第 10 条 · 早晨", credit=CR_ART,
            bigs=[BIG("N06", "8 小时", "8 + 1", "小时", "给无聊工作的 8 小时 + 早晨留给自己的 1 小时", 3.2, -0.4)]),
        SC("L34", "第34条", PG("A_34", [
            M("Most workplaces are adult daycare centers", "N09", "第三十四条", 0.0, "第 34 条：多数职场是成年人的托儿所"),
            M("At work if your family member dies everyone is sorry", "N10", "亲人去世", -0.1, "在公司，亲人去世，大家都说抱歉，还给你假"),
            M("thoughts and prayers", "N11", "上一分钟", -0.1, "上一分钟“送上祝福”，下一分钟“你被解雇了”"),
        ]), [
            L("N09", "第三十四条：多数公司是成年人的托儿所。",
              "Lesson 34: most workplaces are adult daycare centers.",
              "第三十四条：多数公司是成年人的托儿所。"),
            L("N10", "亲人去世，公司会说抱歉、放你假；真实世界没人管，照常上班。",
              "If a relative dies, work apologizes and gives time off. The real world expects you to show up.",
              "亲人去世，公司会说抱歉、放你假；真实世界没人管，照常上班。"),
            L("N11", "裁员文化也一样：上一分钟“送上祝福”，下一分钟“你被解雇了”。",
              "Layoff culture too: one minute 'thoughts and prayers', the next 'you've been let go'.",
              "裁员文化也一样：上一分钟“送上祝福”，下一分钟“你被解雇了”。"),
        ], tag="第 34 条 · 托儿所", credit=CR_ART),
        SC("L35", "第35条", PG("A_35", [
            M("Building a startup unicorn by raising VC money", "N12", "第三十五条", 0.0, "第 35 条：靠融资做创业独角兽，是最蠢的幻想之一"),
            M("you don't need to raise money or buy ads", "N13", "不用融资", -0.1, "新世界里，你不用融资，也不用买广告"),
            M("use free social media to build an email list", "N13", "邮件列表", -0.6, "用免费的社交媒体攒一个邮件列表，就能开张"),
        ]), [
            L("N12", "第三十五条：靠融资做独角兽，是最蠢的幻想之一。",
              "Lesson 35: building a unicorn on VC money is one of the stupidest fantasies.",
              "第三十五条：靠融资做独角兽，是最蠢的幻想之一。"),
            L("N13", "新世界不用融资、不用买广告：免费社交媒体攒个邮件列表，就能开张。",
              "Today you need no funding or ads: build an email list on free social media and launch.",
              "新世界不用融资、不用买广告：免费社交媒体攒个邮件列表，就能开张。"),
        ], tag="第 35 条 · 融资", credit=CR_ART),
        SC("L15", "第15条", PG("A_15", [
            M("Disappear from public life. Adopt a nickname", "N14", "第十五条", 0.0, "第 15 条：从公众视野消失，换个昵称，再无所畏惧地去网上做事"),
            M("From here on I will be known as Tim Winterbottom", "N15", "Tim Winterbottom", -0.4, "括号里：从今往后，改叫 Tim Winterbottom"),
        ]), [
            L("N14", "第十五条：隐身，换个昵称，再放手去网上做事。",
              "Lesson 15: disappear, take a nickname, then build online without fear.",
              "第十五条：隐身，换个昵称，再放手去网上做事。"),
            L("N15", "括号里 Tim 还开了个玩笑：今后改叫 Tim Winterbottom。",
              "In brackets Tim jokes that from here on he goes by Tim Winterbottom.",
              "括号里 Tim 还开了个玩笑：今后改叫 Tim Winterbottom。"),
        ], tag="第 15 条 · 昵称", credit=CR_ART),
        SC("C1", "泼冷水", PG("P_bio", [
            M("238K+ subscribers", "N16", "网上", -0.3, "23.8 万+ 订阅者：他的生意就在网上"),
        ]), [
            L("N16", "别忘了，劝人离开公司的 Tim，自己的生意就在网上。",
              "Remember: Tim, who urges people to leave their jobs, runs his own business online.",
              "别忘了，劝人离开公司的 Tim，自己的生意就在网上。"),
        ], tag="别忘了", credit=CR_BIO),
        SC("E1", "金句", PG("A_9", [
            M("Stop worrying about promotions, pay rises, and job titles", "N17", "头衔", -0.4, "别再操心晋升、加薪和头衔，去网上建点真正给你自由的东西"),
        ]), [
            L("N17", "头衔是公司给的，自由得自己挣。",
              "Titles are handed out by the company. Freedom you have to earn yourself.",
              "头衔是公司给的，自由得自己挣。"),
        ], tag="第 9 条 · 自由", credit=CR_ART),
    ]))

# ═════════════════════════════════════════════════════════════════════ 第 4 期：别装清高（第 16、17、36 条）
EPISODES.append(dict(
    num=4, slug="TimDenning忠告4_别装清高", name="TimDenning忠告4_别装清高",
    hook=["10亿阅读的作家", "劝你别装清高"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ④",
    scenes=[
        SC("H0", "钩子", PG("A_16", [
            M("People who think they don't pursue their goal for money are delusional", "N01", "自欺", -0.9, "以为自己追目标不为钱的人，是在自欺欺人"),
        ]), [
            L("N01", "“说自己不为钱的人，多半在自欺。”",
              "“People who say they don't chase money are delusional.”",
              "“说自己不为钱的人，多半在自欺。”"),
        ], tag="文章第 16 条", credit=CR_ART),
        SC("B1", "背书·简介", PG("P_bio", [
            M("Aussie writer with 1B+ views that made me $6M+", "N02", "10 亿阅读", -0.7, "简介原话：10 亿+ 阅读的澳洲作家，赚了 600 万美元+"),
        ]), [
            L("N02", "出自 Tim Denning，简介自称 10 亿阅读、赚 600 万美元以上。",
              "It's Tim Denning, whose bio claims 1B+ views and $6M+ earned.",
              "出自 Tim Denning，简介自称十亿阅读、赚六百万美元以上。"),
        ], tag="简介自称", credit=CR_BIO),
        SC("L16", "第16条", PG("A_16", [
            M("Without the scoreboard it lets you off the hook", "N03", "计分板", -0.4, "没了计分板，你就不用对任何事负责"),
            M("blame the market or say", "N04", "怪市场", -0.1, "于是可以怪市场，或者说“没人懂我”"),
            M("Romantic artists are the worst. So are $0 hobbyists.", "N05", "最糟", -0.2, "最糟的是浪漫的艺术家，还有一分钱不赚的业余爱好者"),
            M("Even if you run a charity you still need money", "N06", "慈善", -0.2, "哪怕做慈善，也需要钱"),
        ]), [
            L("N03", "第十六条：说钱不重要，等于撤掉了计分板，没人要你负责。",
              "Lesson 16: saying money doesn't matter removes the scoreboard, and with it your accountability.",
              "第十六条：说钱不重要，等于撤掉了计分板，没人要你负责。"),
            L("N04", "没有计分板，就能怪市场，怪“没人懂我”。",
              "Without a scoreboard you can blame the market, or say 'people don't get me'.",
              "没有计分板，就能怪市场，怪“没人懂我”。"),
            L("N05", "Tim 点名最糟的两类：浪漫的艺术家，和一分钱不赚的业余爱好者。",
              "The worst two types, per Tim: romantic artists and $0 hobbyists.",
              "Tim 点名最糟的两类：浪漫的艺术家，和一分钱不赚的业余爱好者。"),
            L("N06", "做慈善也要钱。钱就是个资源。",
              "Even charity needs money. Money is just a resource.",
              "做慈善也要钱。钱就是个资源。"),
        ], tag="第 16 条 · 计分板", credit=CR_ART),
        SC("L17", "第17条", PG("A_17", [
            M("If you don't learn how money works you will always work for money", "N07", "第十七条", 0.0, "第 17 条：不懂钱怎么运转，你就永远在为钱打工"),
            M("The escape route is to obsessively learn how it works", "N08", "死磕", -0.3, "出路是死磕搞懂它怎么运转"),
        ]), [
            L("N07", "第十七条：不懂钱怎么运转，就得一辈子为钱打工。",
              "Lesson 17: don't learn how money works and you'll work for money forever.",
              "第十七条：不懂钱怎么运转，就得一辈子为钱打工。"),
            L("N08", "Tim 说，钱的规则被设计得很复杂，出路是死磕搞懂它。",
              "Tim says money's rules are complex by design, and the way out is to study them obsessively.",
              "Tim 说，钱的规则被设计得很复杂，出路是死磕搞懂它。"),
        ], tag="第 17 条 · 懂钱", credit=CR_ART),
        SC("L36", "第36条", PG("A_36", [
            M("Understand human psychology and you can make as much money as you want", "N09", "第三十六条", 0.0, "第 36 条：懂人的心理，你想赚多少钱都行"),
            M("humans act out of self-interest. Appeal to it", "N10", "自利", -0.2, "人都出于自利而行动，去迎合它"),
        ]), [
            L("N09", "第三十六条：懂人性，就能赚到想赚的钱。",
              "Lesson 36: understand human psychology and you can make as much money as you want.",
              "第三十六条：懂人性，就能赚到想赚的钱。"),
            L("N10", "生意是门心理学课：人都出于自利，去迎合它。",
              "Business is a psychology masterclass: people act out of self-interest, so appeal to it.",
              "生意是门心理学课：人都出于自利，去迎合它。"),
        ], tag="第 36 条 · 人性", credit=CR_ART),
        SC("C1", "泼冷水", PG("A_17", [
            M("Last year I took $1000 and turned it into $120K", "N11", "1000 美元", -0.5, "文中自称：拿 1000 美元，变成 12 万美元"),
            M("All you need is one strategy or arbitrage to attract more money", "N12", "一个字没提", -0.3, "只需要一个策略或套利，就能吸引更多的钱——没写细节"),
        ]), [
            L("N11", "最后一个数字要小心：Tim 自称，1000 美元不到 5 分钟变 12 万。",
              "Be careful with the last number: Tim claims $1,000 became $120K in under 5 minutes.",
              "最后一个数字要小心：Tim 自称，一千美元不到五分钟变十二万。"),
            L("N12", "怎么做到的？文里一个字没提。",
              "How? The article doesn't say.",
              "怎么做到的？文里一个字没提。"),
        ], tag="Tim 自称", credit=CR_ART,
            bigs=[BIG("N11", "1000 美元", "1000 → 12万", "美元", "Tim 自称 5 分钟内；文里没写怎么做的", 4.2, -0.4)]),
        SC("E1", "金句", PG("A_16", [
            M("not disconnecting what you do from money", "N13", "切开", -0.7, "别把你做的事和钱割裂开"),
        ]), [
            L("N13", "想做成的事，先别和钱切开。",
              "Whatever you want to build, don't cut it off from money.",
              "想做成的事，先别和钱切开。"),
        ], tag="第 16 条 · 钱", credit=CR_ART),
    ]))

# ═════════════════════════════════════════════════════════════════════ 第 5 期：朋友会换，父母不会等（第 7、2、29、32 条）
EPISODES.append(dict(
    num=5, slug="TimDenning忠告5_朋友会换父母不会等", name="TimDenning忠告5_朋友会换父母不会等",
    hook=["10亿阅读的作家", "说朋友会换，父母不会等"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ⑤",
    scenes=[
        SC("H0", "钩子", PH("party", zoom=0.05, base=1.75, fx=0.45, fy=0.23), [
            L("N01", "“年纪越大，你越想把一些朋友留在身后。这很正常。”",
              "“As you get older, you'll want to leave some friends behind. It's normal.”",
              "“年纪越大，你越想把一些朋友留在身后。这很正常。”"),
        ], tag="文章第 7 条", credit=CR_MJ),
        SC("B1", "背书·简介", PG("P_bio", [
            M("Aussie writer with 1B+ views that made me $6M+", "N02", "10 亿阅读", -0.6, "简介原话：10 亿+ 阅读的澳洲作家，赚了 600 万美元+"),
        ]), [
            L("N02", "出自 Tim Denning，简介自称 10 亿阅读、赚 600 万美元以上。",
              "It's Tim Denning, whose bio claims 1B+ views and $6M+ earned.",
              "出自 Tim Denning，简介自称十亿阅读、赚六百万美元以上。"),
            L("N03", "写这篇时，Tim 38 岁，有个 2 岁的女儿。",
              "Tim wrote this at 38, with a 2-year-old daughter.",
              "写这篇时，Tim 三十八岁，有个两岁的女儿。"),
        ], tag="简介自称", credit=CR_BIO),
        SC("L7", "第7条", PG("A_7", [
            M("When you're young you try to look good", "N04", "年轻时", -0.1, "年轻时，你想让自己看起来好"),
            M("Many of my friends worked in nightclubs", "N05", "夜店", -0.5, "我很多朋友在夜店工作"),
            M("40 year olds still trying to live like 20 year olds", "N06", "原地踏步", -0.9, "40 岁了，还想过 20 岁的日子"),
            M("Just slowly reduce contact", "N07", "慢慢少联系", -0.2, "慢慢减少联系就好"),
        ]), [
            L("N04", "原因：年轻时挑朋友是为了好看，后来不在乎好不好看了，朋友就换了。",
              "The reason: when you're young you pick friends to look good. Later you stop caring, and friends change.",
              "原因：年轻时挑朋友是为了好看，后来不在乎好不好看了，朋友就换了。"),
            L("N05", "Tim 举的例子：夜店里的朋友，能给免费的酒，能带你插队。",
              "Tim's example: friends from nightclubs who get you free drinks and skip the line.",
              "Tim 举的例子：夜店里的朋友，能给免费的酒，能带你插队。"),
            L("N06", "可 40 岁还想过 20 岁日子的人，在 Tim 眼里是原地踏步。",
              "But someone at 40 still living like 20 is, in Tim's eyes, standing still.",
              "可四十岁还想过二十岁日子的人，在 Tim 眼里是原地踏步。"),
            L("N07", "做法很温和：别粗暴断联，慢慢少联系。",
              "The method is gentle: don't cut them off rudely, just slowly reduce contact.",
              "做法很温和：别粗暴断联，慢慢少联系。"),
        ], tag="第 7 条 · 朋友", credit=CR_ART),
        SC("L2", "第2条", PG("A_2", [
            M("Having kids isn't the end of freedom", "N08", "第二条", 0.0, "第 2 条：有孩子不是自由的终点，而是起点"),
            M("Your life is over when it happens, Timbo", "N09", "人生就完了", -0.5, "“发生的那一刻，你的人生就结束了，Timbo。”"),
            M("it's the best experience of my life", "N10", "最好的经历", -0.5, "这是我一生最好的经历"),
            M("Choose your hard", "N11", "选你的难", -0.2, "选你的难"),
        ]), [
            L("N08", "第二条：生孩子，Tim 说是自由的起点。",
              "Lesson 2: having kids, Tim says, is where freedom starts.",
              "第二条：生孩子，Tim 说是自由的起点。"),
            L("N09", "20 岁时，有人对 Tim 说：生了孩子，你的人生就完了。",
              "At 20, someone told Tim: your life is over once you have kids.",
              "二十岁时，有人对 Tim 说：生了孩子，你的人生就完了。"),
            L("N10", "2 岁的女儿占去大把时间，Tim 却说这是一生最好的经历。",
              "A 2-year-old takes up lots of his time, yet Tim calls it the best experience of his life.",
              "两岁的女儿占去大把时间，Tim 却说这是一生最好的经历。"),
            L("N11", "孩子难，好东西都难。Tim 的话：选你的难。",
              "Kids are hard, and so is everything good. Tim's line: choose your hard.",
              "孩子难，好东西都难。Tim 的话：选你的难。"),
        ], tag="第 2 条 · 孩子", credit=CR_ART),
        SC("L29", "第29条", PG("A_29", [
            M("Spend more time with your parents than feels normal", "N12", "陪父母", -0.2, "花在父母身上的时间，要比你觉得正常的更多"),
            M("Soon they'll be gone", "N12", "很快", -0.1, "他们很快就不在了"),
        ], fit=True), [
            L("N12", "第二十九条：陪父母，要比你觉得正常的更多，他们很快会走。",
              "Lesson 29: spend more time with your parents than feels normal. They'll be gone soon.",
              "第二十九条：陪父母，要比你觉得正常的更多，他们很快会走。"),
        ], tag="第 29 条 · 父母", credit=CR_ART),
        SC("L32", "第32条", PG("A_32", [
            M("light it on fire", "N13", "烧掉", -0.2, "第 32 条：把父母给你定的人生计划点火烧掉"),
            M("In a world of AI, all the rules are now broken", "N14", "AI", -0.3, "在 AI 的世界里，所有规则都被打破了"),
        ]), [
            L("N13", "第三十二条却说：把父母给你定的人生计划烧掉。",
              "Yet lesson 32 says: set your parents' plan for your life on fire.",
              "第三十二条却说：把父母给你定的人生计划烧掉。"),
            L("N14", "理由：世界变太快，AI 时代的规则全被打破，要走自己的路。",
              "Why: the world moves too fast, AI has broken all the rules, so carve your own path.",
              "理由：世界变太快，AI 时代的规则全被打破，要走自己的路。"),
        ], tag="第 32 条 · 自己的路", credit=CR_ART),
        SC("C1", "泼冷水", PG("A_top", [
            M("I'm 38. If You're in Your 20's or 30's, Read This.", "N15", "38 岁", -0.2, "标题：38 岁的 Tim，写给 20、30 多岁的人"),
        ]), [
            L("N15", "不过这是 38 岁、有了孩子的人的视角，20 多岁的你不必照搬。",
              "But this is the view of a 38-year-old father. If you're in your 20s, don't copy it.",
              "不过这是三十八岁、有了孩子的人的视角，二十多岁的你不必照搬。"),
        ], tag="别忘了", credit=CR_ART),
        SC("E1", "金句", PG("A_29", [
            M("Soon they'll be gone", "N16", "不会等", -0.4, "他们很快就不在了"),
        ], fit=True), [
            L("N16", "朋友会换，父母不会等。",
              "Friends change. Parents won't wait.",
              "朋友会换，父母不会等。"),
        ], tag="第 29 条 · 父母", credit=CR_ART),
    ]))

# ═════════════════════════════════════════════════════════════════════ 第 6 期：忙是低地位（第 13、14、19、28、31、21 条）
EPISODES.append(dict(
    num=6, slug="TimDenning忠告6_忙是低地位", name="TimDenning忠告6_忙是低地位",
    hook=["10亿阅读的作家", "说“我很忙”是低地位"],
    kicker="悠一 · <b>Tim Denning</b> 忠告 ⑥",
    scenes=[
        SC("H0", "钩子", PG("A_13", [
            M("Avoid being busy", "N01", "很忙", -0.4, "第 13 条：别忙。它说明你不会专注，是低地位的信号"),
        ]), [
            L("N01", "“说自己很忙，是低地位的信号。”",
              "“Saying you're busy is a sign of low status.”",
              "“说自己很忙，是低地位的信号。”"),
        ], tag="文章第 13 条", credit=CR_ART),
        SC("B1", "背书·简介", PG("P_bio", [
            M("Aussie writer with 1B+ views that made me $6M+", "N02", "10 亿阅读", -0.6, "简介原话：10 亿+ 阅读的澳洲作家，赚了 600 万美元+"),
        ]), [
            L("N02", "出自 Tim Denning，简介自称 10 亿阅读、赚 600 万美元以上。",
              "It's Tim Denning, whose bio claims 1B+ views and $6M+ earned.",
              "出自 Tim Denning，简介自称十亿阅读、赚六百万美元以上。"),
        ], tag="简介自称", credit=CR_BIO),
        SC("L13a", "第13条·失控", PG("A_13q", [
            M("It means your life is out of control and you have no focus", "N03", "失控", -0.3, "忙意味着你的生活失控，没有焦点"),
        ], fit=True), [
            L("N03", "忙，意味着不会专注，生活失控。",
              "Busyness means you can't focus and your life is out of control.",
              "忙，意味着不会专注，生活失控。"),
        ], tag="第 13 条 · 忙", credit=CR_ART),
        SC("L13b", "第13条·做法", PG("A_13p", [
            M("Eliminate calendar events as quickly", "N04", "删掉", -0.5, "尽快删掉日历上的安排"),
        ], fit=True), [
            L("N04", "做法：尽快删掉日历上的安排，把时间空出来过日子。",
              "The fix: delete calendar events as fast as you can, and make room for living.",
              "做法：尽快删掉日历上的安排，把时间空出来过日子。"),
        ], tag="第 13 条 · 忙", credit=CR_ART),
        SC("L14", "第14条", PG("A_14", [
            M("Keanu Reeves are bizarrely quiet", "N05", "基努", -0.4, "第 14 条：基努·里维斯这样的成功者，安静得出奇"),
            M("conversations where you don't talk at all", "N06", "一句不说", -0.4, "一句话都不说的对话，你学到很多"),
        ]), [
            L("N05", "第十四条：很多成功的人，比如基努·里维斯，安静得出奇。",
              "Lesson 14: many successful people, like Keanu Reeves, are bizarrely quiet.",
              "第十四条：很多成功的人，比如基努·里维斯，安静得出奇。"),
            L("N06", "多数人话多不听；整场对话一句不说，反而学到最多。",
              "Most people talk but never listen; say nothing for a whole conversation and you learn the most.",
              "多数人话多不听；整场对话一句不说，反而学到最多。"),
        ], tag="第 14 条 · 安静", credit=CR_ART),
        SC("L19", "第19条", PG("A_19", [
            M("Keeping your dopamine addiction under control", "N07", "多巴胺", -0.4, "第 19 条：管住多巴胺，比任何其他健康技巧都管用"),
            M("TikTok, Netflix, video games, and anything with an easy payoff", "N08", "轻松", -0.9, "TikTok、Netflix、电子游戏，一切轻易就有回报的东西"),
        ]), [
            L("N07", "第十九条：管住多巴胺，比任何健康技巧都管用。",
              "Lesson 19: keeping your dopamine in check beats any other health hack.",
              "第十九条：管住多巴胺，比任何健康技巧都管用。"),
            L("N08", "清单：TikTok、Netflix、电子游戏，凡是轻松就有回报的东西。",
              "The list: TikTok, Netflix, video games, anything with an easy payoff.",
              "清单：TikTok、Netflix、电子游戏，凡是轻松就有回报的东西。"),
        ], tag="第 19 条 · 多巴胺", credit=CR_ART),
        SC("L28", "第28条", PG("A_28", [
            M("Video games are fine when you're younger", "N09", "游戏", -0.1, "第 28 条：年轻时玩游戏无妨，年纪大了就是吃时间的黑洞"),
        ], fit=True), [
            L("N09", "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。",
              "Lesson 28: games are fine when you're young, but later they're a time suck.",
              "第二十八条：游戏年轻时无妨，年纪大了就是吃时间的黑洞。"),
        ], tag="第 28 条 · 游戏", credit=CR_ART),
        SC("L31", "第31条", PG("A_31", [
            M("Flow states are more important than productivity", "N10", "心流", -0.3, "第 31 条：心流比效率更重要"),
            M("Feeling like 8 hours happened in 1 hour will feel better", "N11", "8 小时", -0.4, "感觉 8 小时像 1 小时，会好得多"),
        ]), [
            L("N10", "第三十一条：心流比效率更重要。",
              "Lesson 31: flow states matter more than productivity.",
              "第三十一条：心流比效率更重要。"),
            L("N11", "待办清单激励不了人，感觉 8 小时像 1 小时，才有劲。",
              "To-do lists won't motivate you; feeling 8 hours pass like 1 hour will.",
              "待办清单激励不了人，感觉八小时像一小时，才有劲。"),
        ], tag="第 31 条 · 心流", credit=CR_ART,
            bigs=[BIG("N11", "8 小时", "8 ≈ 1", "小时", "心流：感觉 8 小时像 1 小时", 3.0, -0.4)]),
        SC("C1", "泼冷水", PG("A_21", [
            M("Turn off news and politics to naturally increase your IQ", "N12", "第二十一条", 0.0, "第 21 条：关掉新闻和政治，智商会自然升高"),
        ], fit=True), [
            L("N12", "第二十一条说：关掉新闻政治，智商会自然升高。依据？文里没给。",
              "Lesson 21 says turning off news and politics raises your IQ. Evidence? The article gives none.",
              "第二十一条说：关掉新闻政治，智商会自然升高。依据？文里没给。"),
        ], tag="文里没给依据", credit=CR_ART),
        SC("E1", "金句", PH("banner", zoom=0.06, fx=0.5, fy=0.5), [
            L("N13", "忙碌换不来地位，空出来的时间才值钱。",
              "Being busy buys no status. Free time is what's worth something.",
              "忙碌换不来地位，空出来的时间才值钱。"),
        ], tag="空出来的时间", credit=CR_BAN),
    ]))


# ═════════════════════════════════════════════════════════════════════ 自检
def est_dur(say):
    han = sum(1 for ch in say if "一" <= ch <= "鿿")
    lat = len(re.findall(r"[A-Za-z]+", say))
    inner = len(re.findall(r"[，、：；？！,]", say[:-1]))
    return 0.140 * han + 0.333 * lat + 0.284 * inner + 0.405


def check():
    bad = 0
    total_chars = total_s = 0
    for ep in EPISODES:
        ids = [ln["id"] for sc in ep["scenes"] for ln in sc["lines"]]
        assert ids == sorted(ids) and len(set(ids)) == len(ids), f"第 {ep['num']} 期句号不连续 / 重复"
        zh = {ln["id"]: ln for sc in ep["scenes"] for ln in sc["lines"]}
        s = 0.0
        han = 0
        for ln in zh.values():
            s += est_dur(ln["say"]) + 0.12
            han += sum(1 for ch in ln["say"] if "一" <= ch <= "鿿")
        # 禁用词：他 / 她 / 我（字幕和念的字），开头“我”
        for ln in zh.values():
            for k in ("zh", "say"):
                t = re.sub(r"“[^”]*”", "", ln[k])
                if re.search(r"[我]|[他她](?!们)", t):
                    print(f"  ⚠ 第 {ep['num']} 期 {ln['id']} {k} 里有 他 / 她 / 我：{ln[k]}")
                    bad += 1
            if "不是" in ln["zh"] and "而是" in ln["zh"]:
                print(f"  ⚠ 第 {ep['num']} 期 {ln['id']} 有“不是…而是…”")
                bad += 1
            if len(ln["zh"]) > 38:
                print(f"  ⚠ 第 {ep['num']} 期 {ln['id']} 中文 {len(ln['zh'])} 字 > 38")
            if len(ln["en"]) > 112:
                print(f"  ⚠ 第 {ep['num']} 期 {ln['id']} 英文 {len(ln['en'])} 字符 > 112")
        for sc in ep["scenes"]:
            if sc["shot"]["kind"] == "page":
                assert sc["shot"]["key"] in PAGES, f"{ep['num']} {sc['id']} 没有页面 {sc['shot']['key']}"
                last = -1e9
                for m in sc["shot"]["marks"]:
                    q = zh.get(m["line"])
                    assert q, f"第 {ep['num']} 期 {sc['id']} 高亮引用了不存在的句子 {m['line']}"
                    if m["phrase"]:
                        assert m["phrase"] in q["zh"], f"第 {ep['num']} 期 {m['line']} 里没有短语「{m['phrase']}」：{q['zh']}"
                    sceneids = [x["id"] for x in sc["lines"]]
                    assert m["line"] in sceneids, f"第 {ep['num']} 期 {sc['id']} 的高亮引用了别的场景的句子 {m['line']}"
            for b in sc["bigs"]:
                q = zh[b["line"]]
                assert b["phrase"] in q["zh"], f"第 {ep['num']} 期大数字引用的短语「{b['phrase']}」不在 {b['line']}：{q['zh']}"
        print(f"第 {ep['num']} 期 {ep['name']}：{len(ids)} 句，{len(ep['scenes'])} 个场景，汉字 {han}，估有声 {s:.1f} s（整片约 {s + 1.4:.0f} s）")
        total_chars += han
        total_s += s
    print(f"合计汉字 {total_chars}，估有声 {total_s:.0f} s；问题 {bad} 处")


if __name__ == "__main__":
    check()
