# -*- coding: utf-8 -*-
r"""《Claude官方教程》第 1 期｜出镜版（悠一露脸 + 配音，画面由我做）——台本 + 每个场景的窗口 / 素材选段。

  python gen_ep.py            台本 + 选段 → 台本\录制稿.json / plan.json / 台本\出镜稿_v3_五分钟版.md（估时；悠一录完后给 台本\timing.json 就换成真时间）

LINES   = 每句：zh（字幕 / 他念的）、en（英文字幕）。悠一会“略微修改”这些字：改完录好，用 own_voice.py asr → build 换成他实际说的话，再重新生成。
SCENES  = 每个场景：mode（one 单窗 / two 双窗上下叠 / big 单窗拉大成两个窗口合并的大小）、lines（这个场景里讲的句子）、
          kind（clip = 官方课 / 录屏镜头，card = 自己画的说明卡，画在 scenes.js 里）、
          top / bottom = 窗口里放的素材选段 [dict(src, a, b, speed, w, hold, crop)]；w = 这一段在场景里占的相对时长（秒数的权重），
          credit = 窗口右上角的黄贴纸（≤ 20 字）。素材 src 的键见 制作\00_整片\common.py。
画面规则：只用官方课里的屏幕 / 动画镜头，不放讲师的脸（悠一自己出镜）；官方课视频都挂 credit。
"""

TITLE = {
    "slug": "ClaudeCode是什么_出镜版",
    "title": "Claude官方教程 第1期｜Claude Code 是什么、怎么工作（出镜版）",
    "kicker": "<b>Claude官方教程</b> 第1期",
    "hook": ["Claude Code 是什么", "怎么干活，小白讲清楚"],
}

L = lambda i, zh, en: {"id": f"N{i:02d}", "zh": zh, "say": zh, "en": en}

LINES = [
    L(1, "聊天窗口里的 Claude，有脑子，但伸不进你的电脑。", "The Claude in a chat window has a brain, but it can't reach into your computer."),
    L(2, "它写完代码，你得自己复制、粘贴、运行。", "After it writes code, you copy it, paste it, and run it yourself."),
    L(3, "报错了，再贴回去问它。", "Hit an error? Paste it back and ask again."),
    L(4, "Claude Code，就是把这只手伸了进来。", "Claude Code is that hand, reaching in."),
    L(5, "这期用最白的话，讲三件事。", "This video explains three things in plain words."),
    L(6, "它是什么，怎么干活，第一次用要防什么。", "What it is, how it works, and what to watch for the first time you use it."),
    L(7, "先说清楚，这期的内容从哪来。", "First, where this video's content comes from."),
    L(8, "打开 Anthropic 官网，在 Learn 里点 Claude Academy。", "Open Anthropic's website and click Claude Academy under Learn."),
    L(9, "这是官方的免费课程，下面的内容，都出自官方课程和官方文档。", "These are free official courses, and everything below comes from the official course and docs."),
    L(10, "其中有一门入门课，叫 Claude Code 101。", "One of them is an intro course called Claude Code 101."),
    L(11, "先说结论：Claude Code 是 Anthropic 官方做的 AI 助手。", "The short version: Claude Code is an AI assistant made by Anthropic."),
    L(12, "它能在你的电脑上，自己动手干活。", "It works on your computer and does the work itself."),
    L(13, "怎么理解？聊天窗口，像请了个顾问，隔着电话给你出主意。", "Think of a chat window as a consultant giving you advice over the phone."),
    L(14, "Claude Code，像请了个助手，直接坐到你电脑前。", "Claude Code is an assistant who sits down at your computer."),
    L(15, "它能翻你的文件，搜整个项目，改代码，还能跑命令。", "It can read your files, search the whole project, edit code, and run commands."),
    L(16, "默认只在你启动它的文件夹里干活，想去别的地方，要先问你。", "By default it works only in the folder you start it in; anywhere else, it asks first."),
    L(17, "命令在哪跑？在终端里。终端，就是那个只能敲命令的窗口。", "Where do commands run? In the terminal, the window where you type commands."),
    L(18, "别怕，你不用背命令，用平时说话的方式告诉它就行。", "Don't worry. You don't have to memorize commands; just tell it in everyday language."),
    L(19, "能看环境、能动手、一步步完成目标的软件，业内叫智能体。", "Software that can see its environment, act, and work toward a goal step by step is called an agent."),
    L(20, "英文叫 AI Agent，Claude Code 就是一个典型的智能体。", "In English, an AI agent, and Claude Code is a typical one."),
    L(21, "名字里有 Code，但命令行里能做的事，它基本都能做。", "It has \"Code\" in the name, but it can do pretty much anything you can do on the command line."),
    L(22, "具体能干什么？读懂项目，改代码，跑命令，上网查资料。", "What can it do? Read a project, edit code, run commands, and look things up on the web."),
    L(23, "你只说目标，先干哪个，它自己定。", "You state the goal; it decides what to do first."),
    L(24, "它为什么能自己干活？因为它会转圈。", "How does it get things done by itself? It goes around in a loop."),
    L(25, "官方管这个圈叫代理循环，一共三步：找线索，动手，验结果。", "Anthropic calls it the agentic loop, with three steps: gather context, take action, verify the result."),
    L(26, "比如你说：登录页点了没反应，帮我修一下。", "Say you tell it: the login page doesn't respond when clicked, please fix it."),
    L(27, "它先找线索：翻代码，找到登录相关的文件，读报错。", "First it gathers clues: it reads the code, finds the login files, reads the error."),
    L(28, "再动手改文件。最后验结果：把程序跑一遍，看修好没有。", "Then it edits files. Last it verifies: it runs the program to see if it's fixed."),
    L(29, "没修好？回到第一步，再转一圈，直到验得过去为止。", "Not fixed? Back to step one, another lap, until it checks out."),
    L(30, "还有一点关键：你也在圈里。", "One key point: you're in the loop too."),
    L(31, "想让它停，按一下 Esc；想补一句，直接打字回车。", "To make it stop, press Esc; to add something, just type and press Enter."),
    L(32, "所以别当甩手掌柜，把它当个听得进话的搭档。", "So don't be a hands-off boss. Treat it as a partner who listens."),
    L(33, "这个循环，靠四样东西撑着：大脑，双手，书桌，钥匙。", "Four things hold up this loop: a brain, hands, a desk, and a key."),
    L(34, "先说大脑：Claude 模型，负责看懂你的话和代码，决定下一步。", "The brain is the Claude model: it understands your words and code and decides the next step."),
    L(35, "它在云端。你电脑上的程序，靠网络和它传话。", "It lives in the cloud. The program on your computer talks to it over the network."),
    L(36, "程序把你的话和读到的内容发过去，大脑回一句：去读这个文件。", "The program sends your words and what it read; the brain answers: go read this file."),
    L(37, "大脑管想，程序管做。", "The brain thinks; the program does."),
    L(38, "双手，是工具。没有工具，AI 只能回你一段文字。", "The hands are tools. Without tools, an AI can only reply with text."),
    L(39, "有了工具，它才能读文件、改文件、跑命令、上网查。", "With tools, it can read files, edit files, run commands, and search the web."),
    L(40, "书桌，就是上下文窗口。", "The desk is the context window."),
    L(41, "你说过的话，读过的文件，命令的结果，都摆在这张桌子上。", "What you said, the files it read, the results of commands: all of it sits on this desk."),
    L(42, "桌子有限，堆满了会自动收拾：先清旧的输出，再把对话压成摘要。", "The desk is limited. When it fills up, it tidies itself: old output first, then the conversation is summarized."),
    L(43, "代价是，很早交代的细节，可能就收没了。", "The catch: details you gave long ago may get tidied away."),
    L(44, "每开一场新对话，桌子都是空的。", "Every new conversation starts with an empty desk."),
    L(45, "每次都要遵守的规矩，写进 CLAUDE.md 这个文件。", "Rules it must always follow go into a file called CLAUDE.md."),
    L(46, "钥匙，是权限：它能不能直接改你的文件、跑命令，你说了算。", "The key is permissions: you decide whether it may edit your files and run commands directly."),
    L(47, "按 Shift 加 Tab 轮换：手动档，每步先问你。", "Press Shift+Tab to cycle: Manual mode asks you at every step."),
    L(48, "接受编辑档，改文件不问；计划档，只研究，不动手。", "Accept Edits doesn't ask for file edits; Plan mode only researches and doesn't act."),
    L(49, "自动档，它放手去做，后台有一道安全检查。", "In Auto mode it acts freely, with a safety check running in the background."),
    L(50, "官方说得很清楚：自动档，不保证绝对安全。", "The docs are clear: Auto mode does not guarantee safety."),
    L(51, "新版终端里，新会话默认就是自动档。", "In recent terminal versions, new sessions start in Auto mode by default."),
    L(52, "所以第一次打开，先看一眼底部的状态栏。", "So the first time you open it, check the status bar at the bottom."),
    L(53, "泼点冷水：官方课提醒，它可能理解错，可能写出 bug，也可能把事情做复杂。", "A bit of cold water: the official course warns it may misunderstand you, write bugs, or overcomplicate things."),
    L(54, "所以你得留在圈里看着。好在有两层保险。", "So stay in the loop and watch. Luckily there are two safety nets."),
    L(55, "第一层，快照：改文件之前，它先拍一张。", "First, snapshots: before it edits a file, it takes one."),
    L(56, "改错了，连按两下 Esc，就能退回去。", "If it gets it wrong, press Esc twice to rewind."),
    L(57, "但快照只管文件。数据库、线上接口、部署，退不回来。", "But snapshots only cover files. Databases, live APIs, and deployments can't be undone."),
    L(58, "第二层，让它自己验：给它一个能跑的检查，比如跑测试。", "Second, let it check itself: give it something runnable, like tests."),
    L(59, "还有，大脑在云端，读到的内容会随对话发过去。", "One more thing: the brain is in the cloud, so what it reads is sent along with the conversation."),
    L(60, "密码、密钥这类文件，别让它碰。", "Keep passwords and keys away from it."),
    L(61, "怎么用上它？入口有四个：终端，编辑器插件，桌面应用，网页版。", "How do you get it? Four entry points: the terminal, an editor plugin, the desktop app, or the web."),
    L(62, "想用要有账号：Claude 订阅，或者 Console 账号。", "You need an account: a Claude subscription, or a Console account."),
    L(63, "不会写代码也能用，但越不懂代码，越要让它把结果跑给你看。", "You can use it without knowing code, but the less you know, the more you should make it show you results."),
    L(64, "第一次用，先看状态栏，再问一句：这个项目是干什么的？", "The first time, check the status bar, then ask: what does this project do?"),
    L(65, "看它怎么翻你的项目，你就亲眼看到“找线索”了。", "Watch how it digs through your project, and you'll see \"gathering clues\" for yourself."),
    L(66, "聊天窗口交答案，Claude Code 交结果。", "A chat window gives answers; Claude Code gives results."),
    L(67, "结果对不对，还得你来验收。", "Whether the result is right is still for you to check."),
    L(68, "下一期，我带你从零装好它，跑出第一个提示。", "Next episode: installing it from scratch and running your first prompt."),
]

C1 = "官方课 Claude Code 101"          # 窗口右上角贴纸（官方课视频）
CC = "官方课 · 权限模式"

# spans：src 键见 common.py；a / b = 素材秒；w = 权重（秒）；speed < 1 = 放慢（非人脸可以）；hold = 定格 a 那一帧
S = lambda src, a, b, w=None, **kw: dict(src=src, a=a, b=b, w=w if w is not None else round(b - a, 3), **kw)
H = lambda src, a, w, **kw: dict(src=src, a=a, hold=True, w=w, **kw)
# 大窗（big）裁一块：窗口 846×990 → 内容宽高比 0.8545；官方课终端面板在帧的 x 0.09–0.91、y 0.07–0.93，裁左边约 41% 宽、整个面板高 = 字比单窗大 2 倍多
BIGL = [0.095, 0.070, 0.508, 0.930]      # 面板左 41%
BIGR = [0.490, 0.070, 0.903, 0.930]      # 面板右 41%

SCENES = [
    dict(id="S01", name="聊天窗口伸不进电脑", mode="two", kind="clip", lines=["N01", "N02", "N03"], credit=C1,
         top=[S("c1", 47.0, 49.3, w=5.0), H("c1", 49.2, 4.2)],
         bottom=[S("c1", 50.0, 51.35, w=4.0), H("c1", 51.3, 5.2)]),
    dict(id="S02", name="把手伸进来", mode="two", kind="clip", lines=["N04", "N05", "N06"], credit=C1,
         top=[S("c1", 90.0, 96.8)],
         bottom=[S("c4", 80.9, 86.6), S("c4", 88.9, 94.0)]),
    dict(id="S03", name="内容从哪来（悠一的录屏）", mode="one", kind="clip", lines=["N07", "N08", "N09", "N10"], credit="悠一 · 录屏",
         top=[S("rec", 0.0, 13.0, w=13.0), H("rec", 12.9, 3.0)]),
    dict(id="S04", name="顾问 vs 助手", mode="one", kind="card", lines=["N11", "N12", "N13", "N14"]),
    dict(id="S05", name="翻文件 搜项目 改代码 跑命令", mode="big", kind="clip", lines=["N15", "N16"], credit=C1,
         top=[S("c1", 39.4, 45.4, crop=BIGL), S("c1", 84.2, 88.0, crop=BIGL)]),
    dict(id="S06", name="终端", mode="two", kind="clip", lines=["N17", "N18"], credit="官方课 · 安装",
         top=[S("c3", 18.3, 25.3)],
         bottom=[S("c3", 28.2, 33.4)]),
    dict(id="S07", name="智能体", mode="two", kind="clip", lines=["N19", "N20"], credit=C1,
         top=[S("c1", 71.2, 78.3, speed=0.85)],
         bottom=[S("c1", 63.0, 69.2)]),
    dict(id="S08", name="命令行能做的事它基本都能做 · 你只说目标", mode="two", kind="clip", lines=["N21", "N22", "N23"], credit=C1,
         top=[S("c2", 124.5, 133.6)],
         bottom=[S("c2", 97.9, 107.2)]),
    dict(id="S09", name="代理循环（三步）", mode="big", kind="card", lines=["N24", "N25", "N26"]),
    dict(id="S10", name="例子：修登录页", mode="big", kind="clip", lines=["N27", "N28", "N29"], credit=C1,
         top=[S("c1", 121.0, 127.5, w=4.6, crop=BIGL), S("c1", 159.0, 162.9, w=4.0, crop=BIGL), S("c2", 45.7, 48.0, w=3.9, crop=BIGL)]),
    dict(id="S11", name="你也在圈里", mode="big", kind="card", lines=["N30", "N31", "N32"]),
    dict(id="S12", name="四样东西", mode="big", kind="card", lines=["N33"]),
    dict(id="S13", name="大脑 = 云端的 Claude 模型", mode="big", kind="card", lines=["N34", "N35", "N36", "N37"]),
    dict(id="S14", name="双手 = 工具", mode="two", kind="clip", lines=["N38", "N39"], credit=C1,
         top=[S("c2", 98.0, 104.5)],
         bottom=[S("c1", 86.4, 90.0), S("c2", 147.2, 149.8)]),
    dict(id="S15", name="书桌 = 上下文窗口", mode="two", kind="clip", lines=["N40", "N41"], credit="官方课 · 上下文管理",
         top=[S("c6", 29.6, 34.1), H("c6", 34.0, 2.0)],
         bottom=[S("c6", 13.2, 15.7)]),
    dict(id="S16", name="堆满了自动收拾", mode="two", kind="clip", lines=["N42", "N43"], credit="官方课 · 上下文管理",
         top=[S("c6", 43.2, 46.1), S("c6", 46.4, 52.4)],
         bottom=[S("c6", 103.0, 108.2)]),
    dict(id="S17", name="CLAUDE.md", mode="two", kind="clip", lines=["N44", "N45"], credit=C1,
         top=[S("c4", 80.9, 86.6)],
         bottom=[S("c8", 84.0, 90.6)]),
    dict(id="S18", name="钥匙：手动 / 接受编辑 / 计划", mode="one", kind="clip", lines=["N46", "N47", "N48"], credit=CC,
         top=[S("p4", 24.6, 29.8, w=7.2, speed=0.75), S("p4", 30.4, 35.8, w=2.2), S("p4", 37.2, 41.0, w=2.4)]),
    dict(id="S19", name="自动档", mode="one", kind="clip", lines=["N49", "N50"], credit=CC,
         top=[S("p4", 69.5, 73.8, w=3.6), S("p4", 80.0, 85.0, w=3.4)]),
    dict(id="S20", name="第一次先看状态栏", mode="one", kind="clip", lines=["N51", "N52"], credit=C1,
         top=[S("c4", 92.0, 97.0)]),
    dict(id="S21", name="泼冷水：会犯错", mode="one", kind="clip", lines=["N53", "N54"], credit=C1,
         top=[S("c1", 149.6, 155.8)]),
    dict(id="S22", name="快照：Esc 两下退回去", mode="big", kind="card", lines=["N55", "N56", "N57"]),
    dict(id="S23", name="第二层：让它自己验", mode="two", kind="clip", lines=["N58"], credit=C1,
         top=[S("c4", 112.5, 115.8)],
         bottom=[S("c4", 105.2, 108.7)]),
    dict(id="S24", name="云端：别让它碰密码", mode="big", kind="card", lines=["N59", "N60"]),
    dict(id="S25", name="四个入口", mode="one", kind="clip", lines=["N61"], credit="官方课 · 安装",
         top=[S("c3", 18.8, 21.8), S("c3", 69.0, 72.0), S("c3", 121.6, 124.6), S("c3", 141.0, 144.0)]),
    dict(id="S26", name="账号", mode="one", kind="clip", lines=["N62"], credit="官方课 · 安装",
         top=[S("c3", 48.0, 52.5)]),
    dict(id="S27", name="用平时说话的方式", mode="one", kind="clip", lines=["N63"], credit=C1,
         top=[S("c4", 94.0, 100.5)]),
    dict(id="S28", name="第一次：先问这个项目是干什么的", mode="one", kind="clip", lines=["N64", "N65"], credit=C1,
         top=[S("c4", 88.9, 92.6, w=4.0), S("c2", 124.5, 131.0, w=4.3)]),
    dict(id="S29", name="收尾：交结果", mode="one", kind="clip", lines=["N66", "N67", "N68"], credit=C1,
         top=[S("c4", 116.6, 120.0), S("c4", 121.0, 124.0), S("c1", 164.8, 167.6)]),
]
