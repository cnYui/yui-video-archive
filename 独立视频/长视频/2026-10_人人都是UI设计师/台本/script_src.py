# -*- coding: utf-8 -*-
"""台本数据源：《人人都是 UI 设计师》长视频（文章：龙海 @longhaiqwe123，2026-10-03；规则出自《Refactoring UI》）。

  python script_src.py            生成 录制稿.json、plan.json（场景表）、rules_meta.json（左栏规则卡片 / 说明栏文案），并检查字幕宽度

每句三栏：zh = 字幕（中文一行）、say = 配音念的字（数字写汉字）、en = 英文字幕。say 缺省 = zh。
口径：
- 第三人称，不以“我”开头；讲解者叫他“X 用户龙海”；文章里的判断（三秒耐心、几档颜色……）一律挂“作者”“书里”“官网”的名。
- 数字取自图片里的标注（图 09 的 20 / 10 像素，图 11 的 120 / 45–55 字符，图 14 的 5.97 / 9.01 ……）或文章原文，不自己编。
- 规则标题的英文 = 《Refactoring UI》官网目录里的章节名（refactoringui.com，2026-10-05 抓取）。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent


def L(id_, zh, en, say=None):
    return dict(id=id_, zh=zh, say=say or zh, en=en)


# ═════════════════════════════════════════ 开场（章 −1）
OPEN = [
    # O1：推文
    dict(scene="O1", name="推文", a0=0.25, lines=[
        L("A01", "AI 几分钟就能做出一个产品，界面却可能丑得让人想走。", "AI can build a product in minutes, but the interface may be too ugly to keep anyone."),
        L("A02", "10 月 3 号，X 用户龙海发了一篇长文。", "On October 3, X user Long Hai posted a long article.", "十月三号，X 用户龙海发了一篇长文。"),
    ]),
    # O2：文章封面
    dict(scene="O2", name="标题", lines=[
        L("A03", "标题叫《人人都是 UI 设计师》。", "It is called \u201cEveryone Is a UI Designer\u201d."),
        L("A04", "二十条设计规则，配二十张前后对比图。", "Twenty design rules, each with a before-and-after picture."),
    ]),
    # O3：书官网首屏
    dict(scene="O3", name="书", lines=[
        L("A05", "规则全部出自一本书，《Refactoring UI》。", "Every rule comes from one book, Refactoring UI.", "规则全部出自一本书，Refactoring UI。"),
        L("A06", "作者是 Adam Wathan 和 Steve Schoger。", "Its authors are Adam Wathan and Steve Schoger."),
        L("A07", "官网写着：出自 Tailwind CSS 的作者之手。", "The site says it comes from the creators of Tailwind CSS."),
    ]),
    # O4：书官网“The Book”一节
    dict(scene="O4", name="全书", lines=[
        L("A08", "全书五十章，一本 218 页的 PDF。", "Fifty chapters in a 218-page PDF.", "全书五十章，一本二百一十八页的 PDF。"),
    ]),
    # O5：丑界面（图 13 的反例）
    dict(scene="O5", name="为什么", lines=[
        L("A09", "为什么要补这一课？因为写代码的门槛，被 AI 抹平了。", "Why learn this now? Because AI has flattened the barrier to writing code."),
        L("A10", "功能能用，界面却很可能丑得没法接受。", "The features work, but the interface can be too ugly to accept."),
        L("A11", "作者估计，用户打开新产品的耐心，只有三秒。", "The author reckons a user gives a new product about three seconds."),
        L("A12", "第一眼像草台班子，功能再强，信任也归零。", "If it looks amateur at first glance, trust drops to zero."),
    ]),
    # O6：书官网“用方法，不靠天赋”
    dict(scene="O6", name="天赋", lines=[
        L("A13", "好消息是，UI 不靠天分。", "The good news: UI does not take talent."),
        L("A14", "书的官网首页就有这句：用方法，别靠天赋。", "The book's homepage says it outright: design with tactics, not talent."),
        L("A15", "二十条规则，分三段，一条一条过。", "Twenty rules in three parts, one at a time."),
    ]),
]

# ═════════════════════════════════════════ 二十条规则
# ch = 左栏目录第几章（0 起步与层级 / 1 空间与排版 / 2 颜色与细节）；take = 左栏卡片里的“记住”一句；
# tagL / tagR = 说明栏的标签（kind: bad ✕ / good ✓ / q ? / neutral），capL / capR = 说明栏的中文说明
RULES = [
    dict(n=1, ch=0, title="为设计选一种个性", en="Choose a personality", page=17, take="先定调，再动手",
         img="图01_个性.jpg", tagL=("neutral", "稳重风"), tagR=("neutral", "俏皮风"),
         capL="深青色、小圆角、措辞规矩", capR="亮色、插画、口语文案",
         lines=[
             L("R01a", "第一条：先给界面定个性。", "Rule one: give your interface a personality."),
             L("R01b", "个性由四样东西决定：字体、颜色、圆角、措辞。", "Four things set it: typeface, color, corner radius, wording."),
             L("R01c", "左边是银行：深青色、小圆角、措辞规矩，传达可靠。", "Left, a bank: deep teal, small corners, formal wording. It feels reliable."),
             L("R01d", "右边是社交产品：亮色、插画、口语文案，传达轻松。", "Right, a social product: bright color, illustration, casual copy. It feels relaxed."),
             L("R01e", "定了调，同一个界面里就别混搭。", "Once you pick a tone, keep it consistent across the interface."),
         ]),
    dict(n=2, ch=0, title="别着急上色", en="Detail comes later", page=10, take="先灰度，后上色",
         img="图02_先灰度后上色.jpg", tagL=("neutral", "灰度版"), tagR=("neutral", "点睛上色"),
         capL="只靠间距和字重，骨架先站稳", capR="只给两处上主色",
         lines=[
             L("R02a", "第二条：先别上色。", "Rule two: hold off on color."),
             L("R02b", "早期用黑白灰做界面，只能靠间距、字重和对比度分层级。", "Early on, work in grayscale: spacing, weight and contrast must carry the hierarchy."),
             L("R02c", "左边就是灰度版：骨架清楚，主次分明。", "The left is the grayscale version: a clear structure with clear priorities."),
             L("R02d", "右边只改了两处：创建账号按钮，和选中套餐的对勾。", "On the right only two spots changed: the Create Account button and the plan's check."),
             L("R02e", "颜色只用来强化重点，不用来撑结构。", "Color only reinforces what the layout already says."),
         ]),
    dict(n=3, ch=0, title="字号并非万能", en="Size isn't everything", page=32, take="字重和颜色也能分层级",
         img="图03_字号并非万能.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="字重全是 400，只有大小不同", capR="标题加粗，次要文字调灰",
         lines=[
             L("R03a", "第三条：别只靠字号分层级。", "Rule three: do not build hierarchy from font size alone."),
             L("R03b", "左边的字重全是 400，只有大小不同。", "On the left every weight is 400. Only the sizes differ.", "左边的字重全是四百，只有大小不同。"),
             L("R03c", "结果是标题膨胀，辅助文字小得看不清。", "The title balloons and the small print becomes hard to read."),
             L("R03d", "右边改用字重和颜色：标题加粗到 700，次要文字调灰。", "On the right, weight and color do the work: a bold 700 title, greyed secondary text.", "右边改用字重和颜色：标题加粗到七百，次要文字调灰。"),
             L("R03e", "两三种文字颜色，加两种字重，就够了。", "Two or three text colors plus two weights are enough."),
         ]),
    dict(n=4, ch=0, title="弱化来凸显重点", en="De-emphasize to emphasize", page=39, take="压低配角，主角自现",
         img="图04_弱化凸显主角.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="选中项被深色粗体淹没", capR="其余调浅，选中项自己跳出来",
         lines=[
             L("R04a", "第四条：想让主角突出，先给配角降音量。", "Rule four: to make the lead stand out, turn the others down."),
             L("R04b", "左边选中的 Orders 用了蓝色。", "On the left, the selected item, Orders, is blue."),
             L("R04c", "可旁边全是深色粗体，它还是跳不出来。", "But everything beside it is dark and bold, so it still does not pop."),
             L("R04d", "右边别再给它加戏，把没选中的调浅、降成常规字重。", "On the right, stop boosting it: lighten the rest and drop them to regular weight."),
             L("R04e", "主角一点没改，却立刻成了焦点。", "The selected item did not change, yet it is now the focus."),
         ]),
    dict(n=5, ch=0, title="非必要不用标签", en="Labels are a last resort", page=41, take="能省标签就省",
         img="图05_删冗余标签.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="“标签：数据”，字段平摊权重", capR="去掉标签，名字放大加粗",
         lines=[
             L("R05a", "第五条：能不写标签，就不写。", "Rule five: if you can skip the label, skip it."),
             L("R05b", "左边每行都是“标签加数据”，像数据库。", "On the left every row is \u201clabel plus value\u201d, like a database dump."),
             L("R05c", "每个字段一样重，页面没有主次。", "Every field weighs the same, so nothing leads."),
             L("R05d", "右边去掉标签，名字加大加粗放最上面。", "On the right the labels go, and the name moves to the top, larger and bolder."),
             L("R05e", "邮箱一看就是邮箱，电话一看就是电话。", "An email looks like an email, a phone number like a phone number."),
             L("R05f", "例外是规格表和数据看板：标签要留，还要比数据略深。", "The exception: spec sheets and dashboards keep labels, a shade darker than the data."),
         ]),
    dict(n=6, ch=0, title="按钮看主次不看含义", en="Semantics are secondary", page=52, take="一个主操作，其余让位",
         img="图06_按钮分主次.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="红、蓝、绿三个实心按钮并排抢戏", capR="发布实心，编辑浅底，删除是文字链接",
         lines=[
             L("R06a", "第六条：按钮看重要性，不看含义。", "Rule six: style buttons by importance, not by meaning."),
             L("R06b", "左边红的删除、蓝的编辑、绿的发布，全是实心。", "On the left: red Delete, blue Edit, green Publish, all solid."),
             L("R06c", "三个并排，互相抢戏。", "Side by side, they compete."),
             L("R06d", "一个页面通常只有一个主操作，一两个次操作，其余是辅助。", "A page usually has one primary action, one or two secondary, and a few minor ones."),
             L("R06e", "右边：发布实心，编辑浅底，删除退成文字链接。", "On the right: Publish solid, Edit muted, Delete reduced to a text link."),
             L("R06f", "删除再危险，也等用户点了再弹确认框，那时才用大红按钮。", "Even a risky Delete waits: the big red button belongs in the confirmation dialog."),
         ]),
    dict(n=7, ch=1, title="从过度留白开始", en="Start with too much white space", page=56, take="先给多，再收紧",
         img="图07_过度留白起步.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="内边距紧凑，内容贴着边", capR="先给足留白，再适度收紧",
         lines=[
             L("R07a", "第七条：留白先给多，再收。", "Rule seven: start with too much white space, then take it back."),
             L("R07b", "平时的做法是加：挤了，就补一点边距。", "The usual habit is adding: it feels crowded, so add a little padding."),
             L("R07c", "结果每个元素只拿到“不至于太糟”的最小空间。", "Each element ends up with just enough room to look \u201cnot terrible\u201d."),
             L("R07d", "反着来：先给得远超所需，再慢慢收紧。", "Flip it: give far more than you need, then tighten bit by bit."),
             L("R07e", "单看一个元素觉得多的留白，放进整个界面，往往刚好。", "Space that feels excessive around one element is often just right in the whole page."),
         ]),
    dict(n=8, ch=1, title="不必填满屏幕", en="You don't have to fill the whole screen", page=65, take="要多宽，用多宽",
         img="图08_别撑满屏幕.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="表单撑满整个屏幕，输入框拉得老长", capR="按内容收窄、居中",
         lines=[
             L("R08a", "第八条：有空间，不等于要用满。", "Rule eight: having space does not mean filling it."),
             L("R08b", "960 像素的桌面时代过去了，画布起手就是 1200 到 1400。", "960 pixels is history. Canvases now start at 1,200 to 1,400 pixels.", "九百六十像素的桌面时代过去了，画布起手就是一千二到一千四。"),
             L("R08c", "只需要 600 像素，就只用 600 像素。", "If 600 pixels is all you need, use 600.", "只需要六百像素，就只用六百像素。"),
             L("R08d", "左边的结账页硬撑满，输入框拉得老长。", "On the left the checkout page is stretched edge to edge, with very long inputs."),
             L("R08e", "右边收窄居中，反而好读好填。", "On the right it is narrower and centered, easier to read and to fill in."),
             L("R08f", "设计小界面没头绪，就先从 400 像素的手机宽度画起。", "Stuck on a small UI? Start from a 400-pixel mobile width.", "设计小界面没头绪，就先从四百像素的手机宽度画起。"),
         ]),
    dict(n=9, ch=1, title="间距有亲疏", en="Avoid ambiguous spacing", page=83, take="组间距 大于 组内距",
         img="图09_间距亲疏.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="标签上下各空 20px，归属不清", capR="上 20px、下 10px，贴住输入框",
         lines=[
             L("R09a", "第九条：这个标签，属于上面还是下面？", "Rule nine: does this label belong to the field above or below?"),
             L("R09b", "左边的表单，标签上下各空 20 像素。", "On the left a label has 20 pixels above it and 20 below.", "左边的表单，标签上下各空二十像素。"),
             L("R09c", "它飘在两个输入框中间，归谁说不清。", "It floats between two inputs, and nobody can say which it belongs to."),
             L("R09d", "右边上面还是 20，下面收到 10 像素。", "On the right it is still 20 above, but only 10 below.", "右边上面还是二十，下面收到十像素。"),
             L("R09e", "标签立刻贴住自己的输入框，一条线都不用画。", "The label snaps to its own input without a single line drawn."),
             L("R09f", "法则：组与组的间距，要大于组内的间距。", "The rule: space between groups must exceed the space inside them."),
         ]),
    dict(n=10, ch=1, title="缩放不总是等比", en="Relative sizing doesn't scale", page=79, take="越大的元素，缩得越多",
         img="图10_手机端非等比缩放.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="2.5em 的标题在手机上是 35px", capR="标题独立收到 24px",
         lines=[
             L("R10a", "第十条：手机上，别照搬桌面的缩放比例。", "Rule ten: do not carry desktop proportions straight onto a phone."),
             L("R10b", "桌面正文 18 像素，标题 45，是 2.5 倍。", "Desktop: 18-pixel body, 45-pixel heading, 2.5 times bigger.", "桌面正文十八像素，标题四十五，是二点五倍。"),
             L("R10c", "手机正文缩到 14，标题还乘 2.5，就是 35 像素。", "On a phone the body drops to 14, and 2.5 times that is a 35-pixel heading.", "手机正文缩到十四，标题还乘二点五，就是三十五像素。"),
             L("R10d", "标题折成四行，又笨又占地方。", "The heading wraps to four lines, clumsy and space-hungry."),
             L("R10e", "右边把标题单独收到 24 像素，只比正文大 1.7 倍。", "On the right the heading is 24 pixels, only about 1.7 times the body.", "右边把标题单独收到二十四像素，只比正文大一点七倍。"),
             L("R10f", "大屏上越大的元素，到小屏要缩得越多。", "The bigger an element is on a large screen, the more it should shrink on a small one."),
         ]),
    dict(n=11, ch=1, title="行长与行高联动", en="Keep your line length in check", page=99, take="每行 45 到 75 个字符",
         img="图11_行长与行高.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="一行约 120 个字符，容易串行", capR="一行 45–55 个字符",
         lines=[
             L("R11a", "第十一条：一行多长，决定行距多大。", "Rule eleven: line length decides line spacing."),
             L("R11b", "左边一行约 120 个字符，眼睛很容易串行。", "On the left a line runs about 120 characters, and the eye slips to the wrong line.", "左边一行约一百二十个字符，眼睛很容易串行。"),
             L("R11c", "右边收到 45 到 55 个字符，读起来稳多了。", "On the right it is 45 to 55 characters, which reads far steadier.", "右边收到四十五到五十五个字符，读起来稳多了。"),
             L("R11d", "书里的建议：每行 45 到 75 个字符。", "The book's advice: 45 to 75 characters per line.", "书里的建议：每行四十五到七十五个字符。"),
             L("R11e", "行越长，行高越大：窄的约 1.5，宽的 1.8 到 2。", "Longer lines need more line height: about 1.5 when narrow, 1.8 to 2 when wide.", "行越长，行高越大：窄的约一点五，宽的一点八到二。"),
             L("R11f", "大标题反过来：行高收到 1.1 到 1.2。", "Big headlines go the other way: tighten to 1.1 or 1.2.", "大标题反过来：行高收到一点一到一点二。"),
         ]),
    dict(n=12, ch=1, title="基线对齐，不居中", en="Baseline, not center", page=102, take="字母坐在同一条线上",
         img="图12_基线对齐.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="align-items: center", capR="align-items: baseline",
         lines=[
             L("R12a", "第十二条：大小字并排，按基线对齐。", "Rule twelve: when big and small text sit together, align the baselines."),
             L("R12b", "标题旁挂着小字链接，多数人直接居中。", "A small link next to a title, and most people just center it."),
             L("R12c", "离得近的时候，小字像飘在半空。", "When they sit close, the small text seems to float."),
             L("R12d", "右边只改了一行：center 换成 baseline。", "On the right one line changed: center became baseline."),
             L("R12e", "基线，就是字母“坐”着的那条隐形横线。", "The baseline is the invisible line the letters sit on."),
             L("R12f", "视线顺着它平移，整行立刻稳了。", "The eye glides along it, and the whole row settles."),
         ]),
    dict(n=13, ch=2, title="颜色比想象的多", en="You need more colors than you think", page=123, take="灰 8 到 10 档，主色 5 到 10 档",
         img="图13_颜色比想象多.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="在线生成的 5 色方案", capR="完整色阶：主色、灰、强调色",
         lines=[
             L("R13a", "第十三条：五种颜色，什么都做不出来。", "Rule thirteen: five colors cannot build anything."),
             L("R13b", "在线调色板给你五个色码，号称够用整个网站。", "Online palette generators give you five hex codes and call it enough for a whole site."),
             L("R13c", "硬套上去，就是左下角这样：黄底、红条、深蓝侧栏。", "Force them on and you get the lower left: a yellow page, a red bar, a dark blue sidebar."),
             L("R13d", "真实界面要三类颜色：灰色 8 到 10 档。", "A real UI needs three families of color. Greys come first: 8 to 10 shades.", "真实界面要三类颜色：灰色八到十档。"),
             L("R13e", "品牌主色 5 到 10 档，红黄绿强调色各 5 到 10 档。", "Five to ten shades of the brand color, and of each accent such as red, yellow and green.", "品牌主色五到十档，红黄绿强调色各五到十档。"),
             L("R13f", "一套成熟的 UI，十种颜色、每种 5 到 10 档很常见。", "A mature UI commonly has ten colors, each with five to ten shades.", "一套成熟的 UI，十种颜色、每种五到十档很常见。"),
             L("R13g", "浅底不抢戏，深字不发虚，层次才自然。", "Light backgrounds stay quiet, dark text stays solid, and the layers feel natural."),
         ]),
    dict(n=14, ch=2, title="无障碍也能好看", en="Accessible doesn't have to mean ugly", page=142, take="浅底深字，对比更高更柔和",
         img="图14_浅底深字.jpg", tagL=("q", "合格，但抢眼"), tagR=("good", "浅底深字"),
         capL="深底白字，对比 5.07–5.97", capR="浅底深字，对比 9.01–12.32",
         lines=[
             L("R14a", "第十四条：无障碍，也可以好看。", "Rule fourteen: accessible can still look good."),
             L("R14b", "WCAG 要求普通文字对比度至少 4.5 比 1。", "WCAG asks for a contrast ratio of at least 4.5 to 1 for normal text.", "W C A G 要求普通文字对比度至少四点五比一。"),
             L("R14c", "白底黑字轻松过线，彩色小标签才难。", "Black on white passes easily. Small colored badges are the hard part."),
             L("R14d", "要让白字过线，底色得又深又饱和，特别抢眼。", "To make white text pass, the badge must be dark and saturated, and it shouts."),
             L("R14e", "左边三个标签都合格：5.97、5.07、5.34。", "The three badges on the left all pass: 5.97, 5.07, 5.34.", "左边三个标签都合格：五点九七、五点零七、五点三四。"),
             L("R14f", "右边反转：浅底深字，9.01、9.78、12.32。", "On the right, flip it: pale background, dark text, 9.01, 9.78, 12.32.", "右边反转：浅底深字，九点零一、九点七八、十二点三二。"),
             L("R14g", "对比度更高，看着反而更柔和。", "More contrast, yet softer on the eye."),
         ]),
    dict(n=15, ch=2, title="别只靠颜色", en="Don't rely on color alone", page=146, take="颜色加图形，双通道",
         img="图15_不只靠颜色.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="只靠红、绿区分涨跌", capR="加上向上、向下的箭头",
         lines=[
             L("R15a", "第十五条：别只靠颜色说话。", "Rule fifteen: do not let color do all the talking."),
             L("R15b", "左边的涨跌，只靠绿和红两种颜色区分。", "On the left, green and red are the only signal for up versus down."),
             L("R15c", "红绿色盲的用户看过去，两个标签几乎一样。", "To a red-green colorblind user the two badges look almost identical."),
             L("R15d", "强光、弱光下，颜色也会失效。", "Glare or dim light can wash color out too."),
             L("R15e", "右边加了向上、向下的箭头，两个通道一起传。", "The right adds an up arrow and a down arrow, so two channels carry the message."),
             L("R15f", "颜色只能强化信息，不能当唯一的手段。", "Color may reinforce a message, never be the only way to send it."),
         ]),
    dict(n=16, ch=2, title="强调色边框", en="Add color with accent borders", page=195, take="加一条彩色细边",
         img="图16_强调色边框.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="平淡白卡片，没有重心", capR="顶部加一条蓝色细边",
         lines=[
             L("R16a", "第十六条：加一道强调色边，界面就有了重心。", "Rule sixteen: add one accent border and the interface gets a focal point."),
             L("R16b", "不会画画，也能让界面更有设计感。", "No illustration skills needed to make a UI feel designed."),
             L("R16c", "左边是一张素净的白卡片，大片白色，没有重心。", "On the left, a plain white card: lots of white, no focus."),
             L("R16d", "右边只在卡片顶部加了一条蓝色细条。", "On the right, just one thin blue bar across the top."),
             L("R16e", "同一招还能用在选中的导航项、提示框侧边、页面顶部。", "The same trick works on a selected nav item, an alert box edge, or the page top."),
             L("R16f", "一个彩色矩形，不需要设计天分。", "One colored rectangle takes no design talent."),
         ]),
    dict(n=17, ch=2, title="图上文字先处理背景", en="Text needs consistent contrast", page=176, take="先压暗背景，再放字",
         img="图17_图上文字.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="文字直接压在照片上，看不清", capR="垫一层半透明黑色蒙版",
         lines=[
             L("R17a", "第十七条：字看不清，要改的是背景。", "Rule seventeen: when text is unreadable, fix the background."),
             L("R17b", "照片光影太复杂，字怎么调，也撑不住每个像素的对比度。", "A photo's light and dark vary too much; no text color holds contrast at every pixel."),
             L("R17c", "左边白字压在亮处就隐形，高光和暗部交错。", "On the left, white text vanishes in the highlights, broken up by shadows."),
             L("R17d", "右边垫了半透明黑色蒙版，标注里写的是 0.55。", "On the right sits a semi-transparent black overlay, 0.55 according to the label.", "右边垫了半透明黑色蒙版，标注里写的是零点五五。"),
             L("R17e", "还有几招：降图片对比度、叠品牌单色、加柔和文字光晕。", "Or lower the photo's contrast, tint it in a brand color, or add a soft text glow."),
         ]),
    dict(n=18, ch=2, title="每样东西有适用尺寸", en="Everything has an intended size", page=181, take="小图标别硬拉大",
         img="图18_适用尺寸.jpg", tagL=("q", "很多人这样做"), tagR=("good", "这样做"),
         capL="小图标直接拉大：笨重", capR="保持原大小，外包浅色圆底",
         lines=[
             L("R18a", "第十八条：图标和截图，都有适用的尺寸。", "Rule eighteen: icons and screenshots each have an intended size."),
             L("R18b", "矢量图放大不糊，就把 24 像素的图标拉到 64。", "Vectors do not blur, so people blow a 24-pixel icon up to 64.", "矢量图放大不糊，就把二十四像素的图标拉到六十四。"),
             L("R18c", "可小图标放大后，线条又粗又笨，比例失调。", "But an icon drawn small turns thick and clumsy when enlarged."),
             L("R18d", "右边让图标保持原大小，外面套一个浅色圆底。", "On the right the icon keeps its size inside a light circle that fills the space."),
             L("R18e", "截图也一样：整张后台缩小七成，文字成了蚂蚁线。", "Same for screenshots: shrink a full dashboard 70 percent and the text becomes ant trails."),
             L("R18f", "只截核心局部，或者画个简化的示意图。", "Crop to the core, or draw a simplified mock-up."),
         ]),
    dict(n=19, ch=2, title="慎用边框", en="Use fewer borders", page=206, take="用底色和留白分区",
         img="图19_慎用边框.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="每个区块、每一行都画线", capR="用底色差和留白分区",
         lines=[
             L("R19a", "第十九条：画线之前，先想想别的办法。", "Rule nineteen: before you draw a line, try something else."),
             L("R19b", "要区分元素，很多人第一反应是一条 1 像素的灰边。", "To separate two things, people reach for a 1-pixel grey border.", "要区分元素，很多人第一反应是一条一像素的灰边。"),
             L("R19c", "边框一多，界面就像一张噪点爆炸的 Excel 表。", "Too many borders and the UI looks like a noisy Excel sheet."),
             L("R19d", "左边每个区块、每一行都有线，切得细碎拥挤。", "On the left every block and row has a line, and the page is chopped into pieces."),
             L("R19e", "右边拿掉外框和输入框的描边，改用阴影和灰底。", "On the right the card and input outlines are gone; a shadow and a grey fill take over."),
             L("R19f", "还有一招：直接拉大间距，留白就是分割线。", "One more option: widen the gap, since white space is a divider too."),
         ]),
    dict(n=20, ch=2, title="别忽视空状态", en="Don't overlook empty states", page=203, take="空状态要指路",
         img="图20_空状态.jpg", tagL=("bad", "别这样"), tagR=("good", "这样做"),
         capL="只有一句 No contacts found", capR="插画 + 引导 + 添加按钮",
         lines=[
             L("R20a", "第二十条：空状态，要先设计。", "Rule twenty: design the empty state first."),
             L("R20b", "新功能上线，新用户点进来，一条数据都没有。", "A feature ships, a new user opens it, and there is no data at all."),
             L("R20c", "左边只有一句“没找到联系人”，用户不知道点哪里。", "The left only says \u201cNo contacts found\u201d, and the user has no idea where to tap."),
             L("R20d", "右边有插画、一句引导，和醒目的添加按钮。", "The right has an illustration, a prompt and a bold Add contact button."),
             L("R20e", "没内容时，把用不上的标签页、筛选器、排序先藏起来。", "Until there is content, hide tabs, filters and sorting that do nothing."),
             L("R20f", "空状态，是用户和新功能的第一次见面。", "The empty state is a user's first meeting with a new feature."),
         ]),
]

# ═════════════════════════════════════════ 结尾（章 3 = 全部标已看）
CLOSE = [
    dict(scene="C1", name="回顾", lines=[
        L("Z01", "二十条看完，有个共同点：没有一条靠天分。", "After all twenty, one thing is common: none of them takes talent."),
        L("Z02", "先灰度后上色，是把骨架和渲染分开。", "Grayscale first and color later separates structure from rendering."),
        L("Z03", "间距和基线，背后是格式塔心理学和阅读习惯。", "Spacing and baselines rest on Gestalt psychology and reading habits."),
    ]),
    dict(scene="C2", name="练习", lines=[
        L("Z04", "作者给了两个练习。第一个：看到好界面就截图。", "The author suggests two exercises. First: screenshot every interface you admire."),
        L("Z05", "再拿清单问自己：字重多少？组间距是组内的几倍？", "Then ask it: what weight is the title? How many times bigger is the group gap?"),
        L("Z06", "第二个：别看源码，用 HTML 和 CSS 一比一复刻。", "Second: skip the source and rebuild it one to one in HTML and CSS.", "第二个：别看源码，用 HTML 和 CSS 一比一复刻。"),
    ]),
    dict(scene="C3", name="五十章", lines=[
        L("Z07", "但二十条，连书里五十章的一半都不到。", "But twenty rules are less than half of the book's fifty chapters."),
        L("Z08", "官网有两章免费样章，想看全书可以从那里开始。", "The site offers two free chapters if you want to start on the rest."),
    ]),
    dict(scene="C4", name="彩蛋", lines=[
        L("Z09", "文末有个彩蛋：墨问上有篇笔记，讲怎么把这本书做成 Skill。", "A bonus at the end: a Mowen note explains how to turn the book into a Skill."),
    ]),
    dict(scene="C5", name="收尾", lines=[
        L("Z10", "规则是跑道，要靠自己的眼睛，别死记数字。", "Rules are a runway. Trust your own eyes and do not memorize numbers."),
        L("Z11", "好看这件事，能逐条检查，就能逐条改。", "If good looks can be checked rule by rule, they can be fixed rule by rule."),
    ]),
]

CHAPTERS = ["起步与层级", "空间与排版", "颜色与细节"]


def all_lines():
    out = []
    for sc in OPEN:
        out += sc["lines"]
    for r in RULES:
        out += r["lines"]
    for sc in CLOSE:
        out += sc["lines"]
    return out


def build():
    sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")
    import bilingual_std as B

    lines = all_lines()
    ids = [l["id"] for l in lines]
    assert len(ids) == len(set(ids)), "句子 id 重复"
    over = []
    for l in lines:
        w, e = B.zh_units(l["zh"]), len(l["en"])
        if w > B.ZH_MAX or e > B.EN_MAX:
            over.append(f"{l['id']}  中文 {w:.1f}/{B.ZH_MAX}  英文 {e}/{B.EN_MAX}  {l['zh']}")
    nchar = sum(len(l["say"]) for l in lines)

    sc = dict(slug="人人都是UI设计师", title="人人都是 UI 设计师：20 条设计军规", sub="20 条设计军规", chapters=CHAPTERS,
              lines=[dict(id=l["id"], zh=l["zh"], say=l["say"], en=l["en"]) for l in lines])
    (HERE / "录制稿.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")

    plan = []
    for s in OPEN:
        plan.append(dict(id=s["scene"], type="card", dur=1.0, name=s["name"], chapter=-1, overlay="page",
                         lines=[dict(id=l["id"], a=(s.get("a0", 0.5) if i == 0 else 0)) for i, l in enumerate(s["lines"])]))
    for r in RULES:
        plan.append(dict(id=f"S{r['n']:02d}", type="card", dur=1.0, name=r["title"], chapter=r["ch"], overlay="rule", rule=r["n"],
                         lines=[dict(id=l["id"], a=(0.9 if i == 0 else 0)) for i, l in enumerate(r["lines"])]))
    for s in CLOSE:
        plan.append(dict(id=s["scene"], type="card", dur=1.0, name=s["name"], chapter=len(CHAPTERS), overlay="page",
                         lines=[dict(id=l["id"], a=(0.5 if i == 0 else 0)) for i, l in enumerate(s["lines"])]))
    (HERE / "plan.json").write_text(json.dumps(dict(plan=plan), ensure_ascii=False, indent=1), encoding="utf-8")

    meta = {r["n"]: {k: r[k] for k in ("n", "ch", "title", "en", "page", "take", "img", "tagL", "tagR", "capL", "capR")} for r in RULES}
    (HERE / "rules_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(lines)} 句，念的字 {nchar} 个；场景 {len(plan)} 个；估时 {nchar / 6.5:.0f} s（按 6.5 字/秒，不含停顿）")
    if over:
        print("【超限】\n  " + "\n  ".join(over))
    else:
        print("字幕宽度全部在限内（中文 ≤ 28.5，英文 ≤ 90）")


if __name__ == "__main__":
    build()
