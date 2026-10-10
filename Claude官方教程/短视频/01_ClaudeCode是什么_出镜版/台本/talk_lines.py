# -*- coding: utf-8 -*-
r"""悠一出镜口播（5 段 DJI 原片）→ 字幕行：每行 = (id, 片段, 起点锚点, 终点锚点, 中文字幕, 英文字幕)。

- 片段 A–E = 原片 0181 / 0182 / 0183 / 0186 / 0189（拍摄顺序，内容也是接着讲的）。
- 锚点 = 在 large-v3-turbo 逐词转写里找这一行的开头 / 结尾几个字（去掉标点、小写；ASR 听错的词照 ASR 写，比如 cloud = Claude），
  build_talk.py 用它们定位这一行在原片里的起止时间；中文字幕写的是他实际说的话（只改听错的专名 / 同音字，不润色）。
- CUTS = 要整段剪掉的口误 / 重说（原片秒数，会吸附到最近的静音处）。
- 英文字幕忠实直译他说的话（他说“我”就写 I）。

要他耳朵确认的词（ASR 听不准）列在 UNSURE 里，交付时写给他。
"""

CLIPS = {
    "A": r"H:\DCIM\DJI_001\DJI_20261006153440_0181_D.MP4",
    "B": r"H:\DCIM\DJI_001\DJI_20261006153707_0182_D.MP4",
    "C": r"H:\DCIM\DJI_001\DJI_20261006153807_0183_D.MP4",
    "D": r"H:\DCIM\DJI_001\DJI_20261006154343_0186_D.MP4",
    "E": r"H:\DCIM\DJI_001\DJI_20261006155028_0189_D.MP4",
}
ASR_DIR = r"D:\大疆\Claude官方教程\素材\2026-10_Claude官方教程_出镜版\出镜_ASR"
ASR_NAME = {"A": "DJI_20261006153440_0181_D", "B": "DJI_20261006153707_0182_D", "C": "DJI_20261006153807_0183_D",
            "D": "DJI_20261006154343_0186_D", "E": "DJI_20261006155028_0189_D"}

# 脸的裁切（占原片高度的比例；正方形）：cx / cy = 中心，side = 边长
CROP = {"cx": 0.50, "cy": 0.47, "side": 0.90}

# 要剪掉的口误 / 重说：(片段, 起, 止)，原片秒
CUTS = [
    ("C", 214.98, 217.20),   # “执行这些任务，[停]执行这些，完成这些任务，执行这些命令” → 留“执行这些任务，执行这些命令”
    ("D", 70.73, 73.08),     # “每开一个新的对话呢，也就是一场，[停 1.7 s]也就是新开了一场对话” → 去掉“也就是一场，”
]

LINES = [
    # ───────── A：0181（开场 + 它是什么）
    ("T01", "A", "嗨大家好", "嗨大家好", "嗨，大家好。", "Hi, everyone."),
    ("T02", "A", "今天这个系列", "入门使用cloudcode", "今天这个系列，我会带着大家从零开始入门使用 Claude Code。", "In this series, I'll take you from zero to getting started with Claude Code."),
    ("T03", "A", "我相信点击来", "自己的使用经验", "我相信点进来的朋友，多多少少对 AI 有一些自己的使用经验，", "I'm sure those of you who clicked in already have some experience using AI,"),
    ("T04", "A", "而这期视频", "方法过一遍", "而这期视频，就会带着大家系统地把使用 AI 的方法过一遍。", "and this video will walk you through how to use AI, systematically."),
    ("T05", "A", "ai就是工具", "更好的使用工具", "AI 就是工具，只有知道怎么用工具，才能更好地使用工具。", "AI is a tool, and you can only use a tool well once you know how to use it."),
    ("T06", "A", "当前搜的资料", "提供的免费资料", "当前所有的资料，都来源于 Anthropic 官网提供的免费资料，", "All the material here comes from the free resources on Anthropic's website,"),
    ("T07", "A", "可以像图中", "原始的内容", "可以像图中这样，去找到它的原始的内容。", "and you can find the original content the way you see on screen."),
    ("T08", "A", "好那我们开始", "好那我们开始", "好，那我们开始。", "Alright, let's begin."),
    ("T09", "A", "第一个概念", "统成为cloud", "第一个概念，Claude Code 和 Claude Cowork，之后统称为 Claude。", "First concept: Claude Code and Claude Cowork. From here on I'll just call them Claude."),
    ("T10", "A", "这两个有什么区别", "这两个有什么区别", "这两个有什么区别？", "What's the difference between these two?"),
    ("T11", "A", "那网页版", "是一个chatbox", "那网页版的聊天窗口里的那个 Claude 呢，它是一个 chatbox。", "The Claude in the web chat window is a chatbox."),
    ("T12", "A", "它可以回答问题", "伸到电脑里", "它可以回答问题，但是它没有办法修改电脑里的文件，也就是没有办法把双手伸到电脑里。", "It can answer questions, but it can't modify the files on your computer. It can't reach its hands into your machine."),
    ("T13", "A", "写完代码之后", "复制粘贴和运行", "写完代码之后，我得自己去复制粘贴和运行。", "After it writes code, I have to copy, paste and run it myself."),
    ("T14", "A", "一旦代码有错", "再问它", "一旦代码有错，我得贴回去再问它。", "If the code has an error, I have to paste it back and ask again."),
    ("T15", "A", "前几年的ai", "操作系统中", "前几年的 AI 是这样的一个形式，而 Claude Code，就是把这只手伸进了我的电脑的操作系统中。", "That's what AI looked like a few years ago. Claude Code puts that hand into my computer's operating system."),
    ("T16", "A", "它能够创建", "任何文件", "它能够创建、修改、删除整个电脑上的任何内容，任何文件。", "It can create, modify and delete anything on the whole computer, any file."),
    ("T17", "A", "那么cloudcode它是什么呢", "它是什么呢", "那么 Claude Code，它是什么呢？", "So what is Claude Code?"),
    ("T18", "A", "cloudcode是", "一个ai助手", "Claude Code 是 Anthropic 官方做的一个 AI 助手。", "Claude Code is an AI assistant made by Anthropic."),
    ("T19", "A", "它能在你的电脑上", "自己动手干活", "它能在你的电脑上，自己动手干活。", "It works on your computer and does the work itself."),
    ("T20", "A", "我们可以举一个例子", "给我出主意", "我们可以举一个例子，比如说聊天窗口，它就像请一个顾问，隔着电话去给我出主意。", "Take an example: a chat window is like hiring a consultant who gives me advice over the phone."),
    ("T21", "A", "我问的一些问题", "必须要粘贴", "我问的一些问题呢，它会给我回答，但是我必须要粘贴。", "It answers the questions I ask, but I have to paste things in."),
    ("T22", "A", "如果有报错的话", "去问它", "如果有报错的话，我得粘贴到它这个窗口里去问它。", "If there's an error, I have to paste it into that window and ask."),
    ("T23", "A", "而cloudcode呢", "你的电脑前面", "而 Claude Code 呢，就像请了一个助手，请了一个同事，他直接坐在了你的电脑前面，", "Claude Code is like hiring an assistant, a colleague, who sits right at your computer"),
    ("T24", "A", "去在你的项目文件里", "删除文件", "去在你的项目文件里，去找代码，改代码，跑命令，搜索整个项目，创建文件，删除文件。", "and finds code in your project files, edits code, runs commands, searches the whole project, creates and deletes files."),
    ("T25", "A", "它的活动范围", "子文件夹", "它的活动范围，默认是这个文件夹里的子文件夹。", "By default it only works inside this folder and its subfolders."),
    ("T26", "A", "如果想要去碰", "经过你的同意", "如果想要去碰别的地方的话，必须要经过你的同意。", "If it wants to touch anywhere else, it needs your permission."),
    # ───────── B：0182（怎么启动 + 智能体）
    ("T27", "B", "那么我如何去启动", "cloud呢", "那么我如何去启动 Claude 呢？", "So how do I start Claude?"),
    ("T28", "B", "就是在终端里", "它就启动了", "就是在终端里，去输入 Claude 这个命令，它就启动了。", "You type the claude command in a terminal, and it starts."),
    ("T29", "B", "那终端是什么", "白底黑字的那个窗口", "那终端是什么？终端是那个只能敲命令的窗口，白底黑字的那个窗口。", "What's a terminal? It's the window where you can only type commands, the one with black text on a white background."),
    ("T30", "B", "那有朋友就会", "有些劝退", "那有朋友就会觉得很陌生，可能他就会觉得有些劝退，", "Some of you may find that unfamiliar, maybe even a bit off-putting,"),
    ("T31", "B", "但是不用担心", "其实就可以了", "但是不用担心，你只要敲了 Claude 这个命令之后，你用自然语言去跟它沟通，其实就可以了。", "but don't worry. Once you've typed the claude command, you just talk to it in plain language."),
    ("T32", "B", "这样一个能看环境", "英文名叫aiagent", "这样一个能看环境，能动手，能一步一步完成目标的软件，业内叫智能体，英文名叫 AI Agent。", "Software that can see its environment, take action and reach a goal step by step is called an agent in the industry. In English, an AI Agent."),
    ("T33", "B", "而cloudcode它就是", "智能体的一个框架", "而 Claude Code，它就是一个典型的智能体的一个框架。", "Claude Code is a typical agent framework."),
    ("T34", "B", "名字里有一个", "写代码的", "名字里有一个 Code，但是它不是只是用来写代码的，", "It has \"Code\" in the name, but it isn't only for writing code."),
    ("T35", "B", "它可以去写文档", "都可以", "它可以去写文档，跑程序，搜文件，查资料，都可以。", "It can write documents, run programs, search files, look things up, all of it."),
    ("T36", "B", "所以它真正的本事", "替你动手", "所以它真正的本事，是替你动手。", "So its real skill is doing the work for you."),
    # ───────── C：0183（能干什么 + 怎么干活 + 四个零件开头）
    ("T37", "C", "好刚刚我们知道了", "能干什么呢", "好，刚刚我们知道了它是什么之后，那它具体能干什么呢？", "OK, now that we know what it is, what can it actually do?"),
    ("T38", "C", "它第一点", "可以读项目", "它第一点，可以读项目。", "First, it can read a project."),
    ("T39", "C", "比如说你可以问它", "讲给你听", "比如说你可以问它，这个项目是干什么的？它自己去翻文件，然后讲给你听。", "For example, ask it what this project does. It goes through the files itself and explains it to you."),
    ("T40", "C", "你还可以跟它说", "语言讲一遍", "你还可以跟它说，讲得详细一点，或者讲得简略一点，或者讲得用大白话的语言讲一遍。", "You can also ask for more detail, or a shorter version, or an explanation in plain language."),
    ("T41", "C", "第二个就是改代码", "第二个就是改代码", "第二个就是改代码。", "Second, it edits code."),
    ("T42", "C", "用户提出了", "非常炫酷的网页", "用户提出了自己想要的效果和需求，比如说我要做一个非常炫酷的网页，", "The user states the effect and requirements they want, say, a really cool web page,"),
    ("T43", "C", "就能根据你的需求", "会改好给你", "它就能根据你的需求，作为它的目标，自己去联网找这种动效库，自己去找本地的文件，然后会改好给你。", "and it takes your request as its goal, finds animation libraries online by itself, finds the local files itself, and gives you the finished edit."),
    ("T44", "C", "第三点就是跑命令", "想要看到一个结果", "第三点就是跑命令，你要装一个软件，卸载一个软件，跑一个程序，跑一下检查，想要看到一个结果，", "Third, it runs commands: install a program, uninstall one, run a program, run a check, whatever result you want to see."),
    ("T45", "C", "它就会去跑这些命令", "给你回答", "它就会去跑这些命令，然后给你回答。", "It runs those commands and then gives you the answer."),
    ("T46", "C", "第四点就是上网查资料", "新闻聚合的内容", "第四点就是上网查资料，比如说我会做一些新闻聚合的内容，", "Fourth, it looks things up online. For example, I make news-roundup content,"),
    ("T47", "C", "就会每天定时定点", "来给我看", "它就会每天定时定点地去搜这些新闻，然后把它整理好，创建一个新的文档，来给我看。", "and it searches the news at a set time every day, organizes it, and creates a new document for me to read."),
    ("T48", "C", "这些事情不需要", "它就会自己去做", "这些事情不需要一件件自己指挥，你只要去提前写好之后，告诉它目标，先干哪个，再干哪个，它就会自己去做。", "You don't need to direct these one by one. Write it up in advance, tell it the goal and what to do first and next, and it does it by itself."),
    ("T49", "C", "那么它是怎么去干活", "干活的呢", "那么它是怎么去干活的呢？", "So how does it do its work?"),
    ("T50", "C", "这里就要提到", "循环的概念", "这里就要提到一个循环的概念。", "This is where a loop comes in."),
    ("T51", "C", "这个多轮的一个操作", "agentloop", "这个多轮的一个操作，叫 agent loop，", "This multi-round process is called the agent loop."),
    ("T52", "C", "它会先把你的要求", "达成这个目标", "它会先把你的要求，你的 prompt，作为它必须要完成的目标，然后经过多轮的思考和操作，来达成这个目标。", "It takes your request, your prompt, as the goal it must complete, then goes through several rounds of thinking and acting to reach it."),
    ("T53", "C", "这个也就是常说的", "代理循环", "这个也就是常说的代理循环。", "That's what people call the agentic loop."),
    ("T54", "C", "那举个例子嘛", "发给它", "那举个例子嘛，比如说你跟他说了，我做了一个网页，有一个页面登录页，我点了没反应，然后你帮我修一下，发给它。", "Let's take an example. Say you tell it: I built a web page, the login page doesn't respond when I click, please fix it, and you send that."),
    ("T55", "C", "然后cloud收到你的需求", "必须完成的目标", "然后 Claude 收到你的需求之后，它就会列为它必须完成的目标。", "When Claude receives your request, it lists it as a goal it must complete."),
    ("T56", "C", "然后cloud就会用命令行", "查看代码文件", "然后 Claude 就会用命令行，也就是它的工具，去查看代码文件。", "Then Claude uses the command line, which is its tool, to look at the code files."),
    ("T57", "C", "而这些都不用太担心", "了解而已", "而这些都不用太担心，因为这只是作为了解而已。", "You don't need to worry about any of this; it's just for understanding."),
    ("T58", "C", "这些cloud它会自己", "了解就可以了", "这些 Claude 它会自己去完成这些事情，我们只需要了解就可以了。", "Claude does these things by itself; we only need to understand them."),
    ("T59", "C", "cloud它用它的命令", "去动手改", "Claude 它用它的命令去查看了代码文件，然后找到了跟代码登录页面相关的代码，然后去读了这个报错，然后去动手改，", "Claude uses its commands to look at the code files, finds the code related to the login page, reads the error, and then goes to edit it."),
    ("T60", "C", "改了判断出了", "再去跑", "改了判断出了毛病在哪里，把这个文件改了之后再去跑。", "It works out where the problem is, edits the file, and then runs it."),
    ("T61", "C", "跑了之后看看", "达成了这个目标", "跑了之后看看有没有修好，如果修好了，它就达成了这个目标。", "After running it, it checks whether it's fixed. If it is, it has reached the goal."),
    ("T62", "C", "如果没有修好", "直到目标达成", "如果没有修好，你就再回到第一步，再重新地去修改代码，再转一圈，一直转，直到目标达成。", "If it isn't, go back to step one, edit the code again, go around once more, and keep going until the goal is met."),
    ("T63", "C", "这三步不是", "会混在一起", "这三步不是死板的流水线，会混在一起。", "These three steps aren't a rigid assembly line; they blend together."),
    ("T64", "C", "有的时候问一个问题", "需要转半圈", "有的时候问一个问题呢，它可能只需要转半圈，", "Sometimes you ask one question and it only needs half a loop."),
    ("T65", "C", "比如说它完成了一个任务", "没有这个循环", "比如说它完成了一个任务，一步它就完成了，那就没有这个循环。", "If it finishes a task in one step, there's no loop at all."),
    ("T66", "C", "那如果有一个毛病", "反复的去执行命令", "那如果有一个毛病比较难，它会常常都会反复地去修改，反复地去执行命令，", "If a problem is harder, it usually edits over and over and runs commands over and over."),
    ("T67", "C", "它能连着做几十步", "纠正自己", "它能连着做几十步，一边做，它能一边纠正自己。", "It can chain dozens of steps, correcting itself as it goes."),
    ("T68", "C", "还有一点就很关键", "随时地打断它", "还有一点就很关键，就是如果你发现它有一些地方做错了，或者说你有新的想法，你就可以随时地打断它。", "One more key point: if you see it getting something wrong, or you have a new idea, you can interrupt it at any time."),
    ("T69", "C", "你就可以按esc", "让它停止", "你就可以按 ESC，让它停止。", "Press ESC to make it stop."),
    ("T70", "C", "或者你想要在它的循环里", "回车发给它", "或者你想要在它的循环里去插一些你自己的新的内容，你就可以去回车，把你的内容打字出来，然后回车发给它。", "Or if you want to add something of your own into its loop, type it out and press Enter to send it."),
    ("T71", "C", "当它把手头的这批", "去进行调整", "当它把手头的这批内容执行完之后，就会读到你的话，然后去进行调整。", "When it finishes the batch it's working on, it reads what you wrote and adjusts."),
    ("T72", "C", "那么第四点就是", "怎么跑起来的", "那么第四点就是，这个循环是怎么跑起来的？", "Fourth point: how does this loop actually run?"),
    ("T73", "C", "这里就要说到四个点", "四个点", "这里就要说到四个点。", "That brings us to four things."),
    ("T74", "C", "第一个就是大脑", "第四个就是钥匙", "第一个就是大脑，第二个是双手，第三个是它的记忆，第四个就是钥匙。", "First, the brain. Second, the hands. Third, its memory. Fourth, the key."),
    ("T75", "C", "先说大脑的话", "就是cloud模型", "先说大脑的话，它的大脑就是 Claude 模型。", "Start with the brain: its brain is the Claude model."),
    ("T76", "C", "cloud模型不是在本地", "是在云端的", "Claude 模型不是在本地，是在云端的。", "The Claude model isn't local; it's in the cloud."),
    ("T77", "C", "这个模型呢", "决定下一步做什么", "这个模型呢，它能听懂你的话，能看懂代码，决定下一步做什么，", "The model understands what you say, reads code, and decides what to do next,"),
    ("T78", "C", "但是它没有办法", "执行这些命令", "但是它没有办法在本地执行这些任务，执行这些命令。", "but it can't carry out these tasks or run these commands locally."),
    ("T79", "C", "那它的双手", "执行这些命令的", "那它的双手，也就是它的工具，是用来执行这些命令的。", "Its hands, meaning its tools, are what run those commands."),
    ("T80", "C", "它的双手并不知道", "修改本地的内容", "它的双手并不知道要执行什么，所以是通过它的大脑，去告诉它的双手，去执行什么命令，它才能修改本地的内容。", "The hands don't know what to run, so the brain tells the hands which commands to execute, and only then can it change local content."),
    # ───────── D：0186（大脑和双手怎么配合 + 记忆 + CLAUDE.md + 权限）
    ("T81", "D", "比如说本地有一个代码", "修复代码的需求", "比如说本地有一个代码，然后你提出了这样一个修复代码的需求，", "Say you have some code locally and you ask it to fix something."),
    ("T82", "D", "你的这个prompt", "云端的cloud模型", "你的这个 prompt 就会发给云端的 Claude 模型，", "Your prompt is sent to the Claude model in the cloud."),
    ("T83", "D", "cloud模型就会说", "包含这个bug的代码", "Claude 模型就会说，我要找一下这个 bug 是哪些文件里的，然后他就会发到本地，去让 Claude Code 去用工具，来查看包含这个 bug 的代码，", "The model says: I need to find which files this bug is in. It sends that to your machine, so Claude Code uses tools to look at the code containing the bug."),
    ("T84", "D", "然后你的请求", "这个大脑", "然后你的请求，再加上你的这个代码，再发给他的 Claude 模型这个大脑，", "Then your request plus that code goes back to the Claude model, the brain."),
    ("T85", "D", "大脑去做了一些", "判断之后", "大脑去做了一些修改代码的判断之后，", "After the brain decides how to change the code,"),
    ("T86", "D", "本地去调用工具", "这个任务完成了", "本地去调用工具，把代码修改之后，跑出来，如果说跑通了，再发回他的大脑，他大脑说，OK，这个任务完成了，", "the local side calls the tools, edits the code and runs it. If it passes, that's sent back to the brain, which says: OK, the task is done."),
    ("T87", "D", "他就会把已经完成", "这样一个结果", "他就会把已经完成了这个任务，再发到本地，这样你就能看到他的这样一个结果。", "It sends the completed result back to your machine, and that's how you see the outcome."),
    ("T88", "D", "那么第三点就是记忆", "上下文窗口", "那么第三点就是记忆，学名叫上下文窗口，", "The third thing is memory, formally called the context window."),
    ("T89", "D", "你说过的", "都在他的记忆里", "你说过的 prompt，他读过的文件，以及命令跑出来的结果，都在他的记忆里。", "The prompts you wrote, the files it read, and the results of the commands it ran are all in its memory."),
    ("T90", "D", "但是模型的记忆大小", "满了的话呢", "但是模型的记忆大小是有限的，就跟存储一样，满了的话呢，", "But a model's memory is limited, just like storage, and when it fills up,"),
    ("T91", "D", "模型他会自动的去压缩", "旧的命令给清除掉", "模型他会自动地去压缩，自动地把旧的命令给清除掉。", "the model automatically compresses, and automatically clears out old commands."),
    ("T92", "D", "他的代价就是", "不知道是什么了", "他的代价就是很早之前交代的细节就没有了，就比如说你一开始发的内容，他可能就不知道是什么了。", "The cost is that details you gave long ago are gone. For instance, what you sent at the very beginning, it may no longer know."),
    ("T93", "D", "然后每开一个新的对话呢", "记忆就是空的", "然后每开一个新的对话呢，也就是新开了一场对话，他的记忆就是空的，", "And every time you open a new conversation, its memory is empty;"),
    ("T94", "D", "他就不会带着", "他这些都是独立的", "他就不会带着另一个窗口的聊天内容，他这些都是独立的，", "it won't carry over the chat from another window; they're all independent."),
    ("T95", "D", "如果说你想让他", "这个文件里", "如果说你想让他每次都去遵守一个规则，你就要去把它写到 CLAUDE.md 这个文件里，", "If you want it to follow a rule every time, write it into a file called CLAUDE.md."),
    ("T96", "D", "他每次在开启一个新的", "都会先读这个文件", "他每次在开启一个新的 session，开启一个新的会话的时候，都会先读这个文件，", "Every time it starts a new session, a new conversation, it reads that file first."),
    ("T97", "D", "这个文件很重要", "讲这个文件", "这个文件很重要，我们之后的视频会专门地去讲这个文件。", "That file is important; a later video will cover it in detail."),
    ("T98", "D", "第四点就是钥匙", "也就是权限", "第四点就是钥匙，也就是权限。", "The fourth is the key, which means permissions."),
    ("T99", "D", "cloudcode他要改", "可以设定权限的", "Claude Code 他要改你本地的文件的时候呢，你是可以设定权限的，", "When Claude Code wants to change your local files, you can set permissions:"),
    ("T100", "D", "他可以改什么", "不可以改什么", "他可以改什么，不可以改什么。", "what it may change and what it may not."),
    ("T101", "D", "比如说他分为手动挡", "他会先问你", "比如说他分为手动档，手动档就是改文件的时候，他会先问你，", "For example, there's manual mode, where it asks you first whenever it changes a file."),
    ("T102", "D", "然后能够接受编辑挡", "不问你", "然后能够接受编辑档，就是在项目文件夹里改文件，不问你，", "Then there's accept-edits mode, where it edits files in the project folder without asking you,"),
    ("T103", "D", "建议文件夹", "文件操作也不问", "建立文件夹、移动、删除这几类常见的文件操作也不问，", "and doesn't ask about common file operations like creating a folder, moving, or deleting either;"),
    ("T104", "D", "别的命令他还是会问", "别的命令他还是会问", "别的命令他还是会问。", "other commands it still asks about."),
    ("T105", "D", "aplan", "不碰你的代码", "Plan，这个计划档，就是只研究出方案，不碰你的代码，", "Plan mode only works out a plan and doesn't touch your code."),
    ("T106", "D", "自动呢就是让", "危险操作", "自动呢，就是让他放手去做，后台会有一道安全检查，专门拦一些删除的危险操作，", "Auto lets it go ahead on its own, with a safety check in the background that blocks dangerous operations like deletions."),
    ("T107", "D", "还有一个就是能把", "全部放开", "还有一个就是能把这些命令执行询问你的这个全部关掉的模式，就是全部放开，", "And there's a mode that turns off all of that asking, which means everything is allowed,"),
    ("T108", "D", "但是这个不建议", "不建议新手看", "但是这个不建议新手开。", "but I don't recommend beginners turn it on."),
    # ───────── E：0189（总结 + 泼冷水 + 怎么用 + 建议）
    ("T109", "E", "那么有了这四个工具", "权限钥匙", "那么有了这四个工具，有了大脑，有了双手，记忆和你的这个权限钥匙，", "With these four things, the brain, the hands, the memory and the permission key,"),
    ("T110", "E", "那它就是一个能够", "本地的智能体", "那它就是一个能够去按照你的要求，去完成你的这样一个任务的本地的智能体。", "it becomes a local agent that can complete your task the way you ask."),
    ("T111", "E", "那么说完了这么好用", "不好是什么呢", "那么说完了这么好用的这样一个好处，那么不好是什么呢？", "We've covered the good side, so what's the bad side?"),
    ("T112", "E", "就是有点破冷水", "冷水的意思", "就是有点泼冷水的意思。", "This is a bit of a cold shower."),
    ("T113", "E", "就是它这个东西", "它可能会有bug", "就是它这个东西，它是会有幻觉的，它是一个概率模型，它可能会有 bug。", "It can hallucinate, it's a probabilistic model, and it can have bugs."),
    ("T114", "E", "但是随着模型越来越强", "但是它也会说", "但是随着模型越来越强，这个 bug 越来越少，但是它也会说，", "As models get stronger there are fewer and fewer bugs, but still,"),
    ("T115", "E", "比如说社交媒体上", "这样一个问题", "比如说社交媒体上，有的时候也会有朋友发一些这种，哎呀，它把我的某一个文件给删除了，这样一个问题。", "on social media, sometimes a friend posts something like: oh no, it deleted one of my files."),
    ("T116", "E", "它还是有一定的风险", "最大", "就是它还是有一定的风险，所以平时这个权限的命令还是要注意一下，不要开最大。", "So there's still some risk. Be careful with permission commands day to day, and don't turn it all the way up."),
    ("T117", "E", "那么最后是怎么用上它", "用上它的呢", "那么最后是怎么用上它的呢？", "Finally, how do you get to use it?"),
    ("T118", "E", "刚刚也说了一种方法", "就可以用", "刚刚也说了一种方法，就是在终端里用，你输入 Claude 这个命令，然后回车，它会安装，然后会启动，然后你登录你的账号就可以用。", "I mentioned one way already: use it in the terminal. Type the claude command and press Enter; it installs and starts, then you log into your account and you can use it."),
    ("T119", "E", "那么它还可以在你的", "网页", "那么它还可以在你的这个代码编辑器里面去插件，去用它的插件，然后桌面也有一个应用，然后它可以用它的网页版。", "It also has a plugin for your code editor, a desktop app, and a web version."),
    ("T120", "E", "ok当前这期", "就先到这里", "OK，当前这期 Claude 入门视频就先到这里。", "OK, that's it for this beginner's video on Claude."),
    ("T121", "E", "我提两点建议", "先确认它的权限", "我提两点建议，第一点就是用的时候，先看状态栏，先确认它的权限，", "I have two suggestions. First, when you use it, check the status bar first and confirm its permission mode."),
    ("T122", "E", "第二点的时候就是", "让它去改东西", "第二点的时候就是，你可以先尝试着问一问它，比如说先问这个项目是干什么的，或者说这个概念是什么意思，然后再去深入地去让它去改东西。", "Second, try asking it questions first, like what this project does or what a concept means, and only then dig in and have it change things."),
    ("T123", "E", "用着用着其实", "边用边学嘛", "用着用着其实就会用了，边用边学嘛。", "You'll get the hang of it as you go; learn while you use it."),
    ("T124", "E", "好我们下期再见", "下期再见", "好，我们下期再见。", "Alright, see you in the next one."),
]

# 他实际说了什么、ASR 又听不准的地方：交付时请他耳朵确认
UNSURE = [
    ("T09", "“Claude Code 和 Claude Cowork，之后统称为 Claude”——第二个词我按时长和能量听成 Cowork（转写器听成 Code），请确认。"),
    ("T103", "“建立文件夹、移动、删除”——转写器两次都听成“建议文件夹”，我按语义写成“建立”，请确认是不是“新建 / 创建”。"),
    ("T116", "“不要开最大”——转写器听成“不要 cloud 最大”，中间只有一个很短的音，我按语义写成“开”，请确认。"),
    ("T59", "“找到了跟代码登录页面相关的代码”——两个转写器都是这样，字面照写；如果你说的是“跟登录页面相关的代码”，告诉我改。"),
    ("T29", "“白底黑字的那个窗口”——你说的是白底黑字（macOS 默认终端是这样；官方课里的终端画面多是深色），字幕照你说的写。"),
]
