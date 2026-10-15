# -*- coding: utf-8 -*-
r"""口播字幕条（按成片顺序）→ cues.json。每条：所属场景 scene、该场景稿子里对应第 k 句（画面叠加层按它排时间；None = 即兴发挥、没有对应稿子句）、
录像编号 clip、原录像里的起止秒 s / e、条内要剪掉的片段 skip、中文 zh（按悠一实际说的整理：去口癖、改识别错字）、英文 en。

来源：asr/*.json（faster-whisper large-v3-turbo 逐词时间），2026-10-10 逐句读过。用了 0196–0200 全部 5 段；
0196 末尾“它是能够让你”（没说完）、0198 末尾“这个活还是让你在你自己的电脑上跑”（和 0199 开头重复）、“感谢观看”（误录）不用。
名字写“悠一 / Yui”。识别常见错字：薄机=薄肌（开场玩笑）、绘画=会话、Cloud=Claude、县程 / 现成 / 渐存=线程、历程=例程、Century=Sentry、Sunnet=Sonnet、上线=上限、替态=替代。

【删掉的、说得不准确或官方没写的内容】写在下面 CUT 清单里，最后告诉用户（可以随时恢复）：
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = []


def c(scene, k, clip, s, e, zh, en, skip=(), **kw):
    C.append({"scene": scene, "k": k, "clip": clip, "s": s, "e": e, "zh": zh, "en": en, "skip": [list(x) for x in skip], **kw})


# 删掉的内容（原录像里的位置、原话、为什么）——给用户看的清单
CUT = [
    ("0196", 43.66, 44.90, "现在大家都可以用。", "说大了：官方推文是“等候名单里的 Pro 和 Max 用户放进来了”，文档还写着“逐步放量、Team / Enterprise 没有”"),
    ("0196", 44.90, 49.34, "你可以在本地 Claude Code 用，也可以在浏览器里面的 Claude 里面去用。", "不准确：文档写 Projects 不在终端 CLI、VS Code、JetBrains 里，入口是 claude.ai/code、桌面 App 的 Code 标签、手机 App"),
    ("0196", 54.54, 56.42, "它是能够让你……", "没说完的半句"),
    ("0197", 107.16, 111.26, "它其实当时它并没有上云，它是说在本地去……", "不准确：聊天里的 Projects 存在 claude.ai 账号里，不是本地（Cowork 里从电脑文件夹建的才留在本机）"),
    ("0197", 122.26, 127.22, "他就会调用这个 RAG，去更好地进行模型的记忆的管理。", "不准确：RAG 是知识库放不下时自动扩容（最多 10 倍），不是“记忆管理”"),
    ("0197", 135.80, 138.24, "去做一个大的知识库索引。", "官方没这么写：Cowork 项目是任务、文件、说明、记忆放进一个工作区"),
    ("0198", 69.32, 70.18, "拆横幅。", "说错重来（后面重说了“给横幅留位置”）"),
    ("0198", 133.32, 135.10, "每天下午三点查一遍。", "和演示对不上：演示里的例程是“每天下午 5 点”（稿子也是 5 点）"),
    ("0198", 135.70, 136.66, "直到回归。", "说错重来（后面重说了“查到回归”）"),
    ("0198", 261.78, 262.50, "L100。", "识别出来的杂音"),
    ("0198", 265.14, 266.02, "480MB。", "重复了一遍"),
    ("0198", 283.52, 297.60, "所以 Claude Code 它使用了 Project 之后，等于说会开了一个很多很多这样一个 Ultra 的模式，它会用很多的子代理去做这些任务，像开子代理做这个任务一样。", "官方没写：文档里没有“Ultra 模式”，也没说 Projects 会自动开很多子代理（线程是完整的会话，线程自己可以用子代理）"),
    ("0198", 335.30, 338.90, "开工之前，你是把这个需求文档、这个方案要给他。", "说反了：官方的做法是让 Claude 开工前把计划拿给你看（“show me the plan before you start”）"),
    ("0198", 388.44, 407.4, "这个活还是让你在你自己的电脑上跑。感谢观看。", "句子没说完，和 0199 开头重复；“感谢观看”是误录"),
    ("0199", 97.12, 99.38, "说明这个 agent team 它并没有 Project 的好使。", "官方没这么比：对比页只写了各自的定位和状态（agent teams 是实验性的）"),
    ("0199", 124.60, 125.62, "那就建一个 routine。", "重复"),
    ("0199", 146.22, 149.30, "尤其是你上这个 Pro 账号的话，它是完全不够用的。", "说大了：文档写的是“Pro 上更容易碰到限额”，没说完全不够用"),
    ("0199", 149.94, 162.4, "文档里虽然没有说单独要耗费你多少价格，但是你可以想一想，等于说你开了一个 Ultra 模式，那会有很多子代理在做事情……", "“Ultra 模式 / 很多子代理”官方没写；这段也没说完（录像在这里断了）"),
]

# ═══════════════ 0196（57.2 s）：开场 + 钩子 + 官方背书
c("sOpen", 0, "0196", 0.54, 1.94, "嗨，大家好，我是悠一。", "Hi everyone, I'm Yui.")
c("sOpen", 1, "0196", 2.78, 7.54, "今天一个视频，带大家搞懂 Claude Code 新出的这个 Project 是什么东西。", "In this one video I'll walk you through what Claude Code's new Projects feature is.")
c("sOpen", None, "0196", 8.92, 9.98, "展示一下薄肌。", "Let me show off my lean muscles.")   # 悠一开场的玩笑；识别写成“薄机”，用户 10/10 说别删、配字幕
c("sOpen", 3, "0196", 11.12, 20.58, "我的理解来讲，就是如果你的一个任务，它要跨多个文件夹，而且需要长期地跑，而且需要合上电脑还能跑，那你就应该去使用 Project。",
  "My take: if a task spans several folders, needs to run for a long time, and needs to keep running with your laptop closed, you should use Projects.")
c("s01", 0, "0196", 21.82, 28.04, "在官方的演示里面，发两条消息，Claude 在云上开了八个线程，也就是八个会话。",
  "In the official demo, two messages make Claude start eight threads in the cloud — eight sessions.")
c("s01", 1, "0196", 28.04, 31.20, "八个线程，同时在修一个网站的性能问题。", "Eight threads, fixing one website's performance problem at the same time.")
c("s01", 2, "0196", 31.20, 33.54, "这个功能就叫 Claude Code Project。", "The feature is called Claude Code Projects.")
c("s02", 0, "0196", 34.44, 37.48, "在今年 9 月中旬，它在 Claude Code 里面开了公测。", "In mid-September it went into public beta in Claude Code.")
c("s03", 0, "0196", 37.90, 39.26, "这两天官方说：", "A couple of days ago the official account said:")
c("s03", 1, "0196", 39.26, 43.66, "在等候名单里面的 Pro 和 Max 用户，已经全部开放公测了。", "everyone on the Pro and Max waitlist now has access to the beta.")
c("s04", 0, "0196", 49.82, 52.62, "所以我们可以先来看看，它到底是一个什么东西。", "So let's first look at what it actually is.")

# ═══════════════ 0197（181.1 s）：它是什么
c("s05", 0, "0197", 0.38, 24.96,
  "先看如果你不用 Project 的话，会有什么情况。比如说你要开好多个会话，会在不同文件夹下面开很多个会话，然后这些文件夹之间的 agent 交流，需要你自己去告诉 AI，把这个会话的 Session ID 都发给他，告诉他去跟另外一个会话里的 AI 聊天，你自己还要去给他们分不同的活，就会很麻烦。",
  "Without Projects, you open lots of sessions in different folders. For their agents to talk to each other you have to tell the AI yourself, sending it the other session's ID so it can chat with the AI over there, and you still have to hand out the work yourself. It gets messy.")
c("s05", 2, "0197", 25.34, 27.88, "每个会话的开头，都要重新讲一遍背景。", "Each session starts with you repeating the background.")
c("s05", 3, "0197", 28.22, 32.50, "然后过一段时间，可能还要让你去自己看，谁做完了，谁在等。", "Then after a while you have to go check: who is done, who is waiting.")
c("s05", 3, "0197", 32.92, 35.00, "然后你还要自己去把这些东西，进行一个收尾。", "And then you have to wrap all of it up yourself.")
c("s05", 4, "0197", 35.44, 38.04, "那 Project 就把这些活，全部给了 Claude。", "Projects hands all of that to Claude.")
c("s06", 0, "0197", 38.88, 41.66, "一个 Project，就是一场不会结束的对话。", "A project is one ongoing conversation.")
c("s06", 1, "0197", 42.24, 44.62, "Claude 在里面去当一个总的协调员。", "Claude acts as the overall coordinator inside it.")
c("s06", 2, "0197", 44.62, 51.08, "你把一个总的任务丢进去，跟他说和哪些文件夹有关，他又会把这件事，开一个线程。", "You drop in one big task and tell it which folders are involved, and it starts a thread for it.")
c("s06", None, "0197", 51.56, 54.26, "他会先加载所有的文件夹进来，", "It first loads all those folders,")
c("s06", None, "0197", 54.26, 58.60, "然后去定一个他自己的计划，", "then makes a plan of its own,")
c("s06", None, "0197", 58.60, 61.14, "然后开始开工，按照你的要求。", "and gets to work, following your requirements.")
c("s07", 0, "0197", 61.14, 66.34, "官方博客的比喻就是，像在给一个幕僚长去交代工作。", "The blog's comparison is: it's like briefing a chief of staff.")
c("s07", 1, "0197", 68.42, 71.92, "刚刚说的线程，通常来讲就是一个云端的 Claude Code 会话。", "The threads I just mentioned are usually Claude Code sessions running in the cloud.")
c("s07", None, "0197", 72.42, 77.34, "Claude Code 和现在大部分的 AI，他们都想去把这些本地的文件，给推到云端上去，", "Claude Code and most AI tools today all want to push your local files up to the cloud,")
c("s07", None, "0197", 77.34, 84.66, "这样无论电脑合不合，或者说用手机，都能够去进行实时的 AI web coding，或者怎么样都好。", "so that whether your laptop is closed or you're on your phone, you can do live AI web coding, or whatever.")
c("s07", 2, "0197", 85.50, 90.18, "在云端的这个 Claude Code 会话里面呢，它就有自己的分支，自己的上下文窗口。", "In a cloud Claude Code session, it has its own branch and its own context window.")
c("s07", 3, "0197", 90.18, 94.02, "它自己如果说要开 PR 的话，它就会自己开 PR，自己去推。", "If it needs to open a PR, it opens one itself and pushes it.")
c("s08", 0, "0197", 94.02, 96.94, "你合上电脑的时候，云端线程照样能跑。", "When you close your laptop, the cloud threads keep running.")
c("s08", 1, "0197", 96.94, 99.52, "在手机上也能去看进度，也能发指令。", "From your phone you can also check progress and send instructions.")
c("s09", 0, "0197", 100.90, 106.62, "那么 Project 这个名字呢，其实在前段时间，甚至更早，你可能就用过。", "The name Projects — you may well have used it a while back, or even earlier.")
c("s09", 1, "0197", 111.82, 113.36, "做一个资料夹，", "A folder,")
c("s09", 2, "0197", 113.36, 122.26, "你可以把相关的聊天记录，聊天里可能有图片，可能有视频，全部加在它的知识库里，然后再加一段项目说明。", "where you can add related chats — maybe with images or videos — all into its knowledge base, plus a block of project instructions.")
c("s09", 3, "0197", 127.66, 130.62, "免费用户的话也能建，但是最多只能建五个。", "Free users can create them too, but only up to five.")
c("s09", 4, "0197", 130.62, 135.80, "Cowork 里面也有一套，任务、文件、说明、记忆，都会放到一个工作区里。", "Cowork has its own too: tasks, files, instructions and memory all go into one workspace.")
c("s10", 0, "0197", 138.84, 145.40, "那么这次的 Project，就是一个很大的升级，官方博客的名字就叫“从文件夹到对话”。", "This time Projects is a big upgrade — the official blog post is titled \"from folder to conversation.\"")
c("s10", 1, "0197", 145.40, 149.78, "升级之后，一个 Project 就是一场对话，加一群的这个线程。", "After the upgrade, a project is one conversation plus a crowd of threads.")
c("s11", 0, "0197", 151.48, 156.90, "现在 Claude Code 里面在公测，聊天和 Cowork 之后会逐步地开放。", "It's in beta in Claude Code now, and chat and Cowork will open up gradually after that.")
c("s11", 1, "0197", 157.60, 164.98, "那如果在 Pro 和 Max 这个会员等级上的话，你已有的项目可以照常去用，", "If you're on a Pro or Max plan, your existing projects keep working as usual,")
c("s11", 1, "0197", 165.72, 168.76, "官方会替你升级到这个 Project。", "and the official side will upgrade them to the new Projects for you.")
c("s11", 2, "0197", 169.40, 170.80, "现阶段有一个差别，", "One difference for now:")
c("s11", 3, "0197", 170.80, 174.72, "就是聊天里的项目，Team 和 Enterprise，就是企业版，它能共享。", "projects in chat can be shared on Team and Enterprise, the business plans.")
c("s11", 4, "0197", 175.08, 177.24, "升级版的话，一个项目就是属于你一个人。", "In the upgraded version, a project belongs to just you.")

# ═══════════════ 0198（407.4 s）：官方演示、怎么上手、三条技巧、细节
c("s12", 0, "0198", 0.00, 4.46, "官方也附了一个演示，它有一个四分钟的视频，演示了一个场景。", "The official side also attached a demo: a four-minute video that walks through one scenario.")
c("s12", 1, "0198", 4.74, 11.36, "它是想把一个营销网站去进行优化，这个营销网站它的性能已经整整掉了一个月。", "It's about optimizing a marketing site whose performance has been slipping for a whole month.")
c("s13", 0, "0198", 12.10, 18.82, "那么官方的视频里，就先建了这个 Project 的项目：名字，目标，仓库。", "In the video, they first create the project: a name, a goal, repositories.")
c("s13", 1, "0198", 19.28, 24.28, "目标就是把 LCP 压到 2.5 秒以下，CLS 压到 0.1 以下。", "The goal: get LCP under 2.5 seconds and CLS under 0.1.", skip=[(23.86, 23.98)])
c("s13", 2, "0198", 24.68, 28.78, "LCP 是主要内容出现的时间，CLS 是页面抖不抖。", "LCP is when the main content shows up; CLS is how much the page jumps around.")
c("s14", 0, "0198", 29.18, 33.20, "那么建好了主对话之后就进入，Claude 就给了四条建议。", "Once the main conversation opens, Claude gives four suggestions.")
c("s14", 1, "0198", 33.68, 36.06, "Claude 说，比如读仓库、提方案。", "For example: read the repo and propose next steps.")
c("s14", 2, "0198", 36.06, 42.32, "官方的话就是说，你可以挑一条，问一个小问题，或者直接丢一串任务进去，它都会去进行执行。", "The video's point: you can pick one, ask a quick question, or just drop in a list of tasks, and it carries them out.")
c("s15", 0, "0198", 45.96, 51.08, "那么第一条消息就是，把指标贴进去，让 Claude 先读代码、给方案。", "The first message: paste in the metrics and have Claude read the code and propose a plan.")
c("s15", 1, "0198", 51.08, 54.26, "他先开一个线程，去读了两个仓库。", "It starts one thread first, which reads both repositories.")
c("s15", 2, "0198", 54.68, 56.06, "回来列了八条建议。", "It comes back with eight suggestions.")
c("s15", 3, "0198", 56.06, 60.50, "还说前三条占据了大部分 LCP 和 CLS，建议先做。", "It adds that the first three account for most of the LCP and CLS, so start there.")
c("s15", 4, "0198", 60.50, 63.32, "第二条消息，只有一句：全都做。", "The second message is one line: do all of them.")
c("s16", 0, "0198", 63.90, 66.36, "Claude 回：八个线程，一个任务一个。", "Claude replies: eight threads, one per task.")
c("s16", 1, "0198", 66.36, 71.78, "优化图片，预加载字体，拆 JS 包，给横幅留位置。", "Optimizing images, preloading fonts, splitting the JS bundle, reserving space for the banner.", skip=[(69.32, 70.18)])
c("s16", 2, "0198", 71.78, 74.72, "线程各读各的代码，各开各的分支。", "Each thread reads its own code and works on its own branch.")
c("s16", 3, "0198", 74.72, 77.68, "点开线程卡片，能看到它一步步在干什么。", "Open a thread card to see what it's doing, step by step.")
c("s16", 4, "0198", 77.68, 80.64, "你可以直接在线程里面改它的方向，也可以喊停。", "You can steer it right inside the thread, or stop it.")
c("s17", 0, "0198", 81.38, 85.98, "线程手里有了具体改动，比如说修一个 bug，它就会自己开 PR。", "Once a thread has a concrete change, like a bug fix, it opens a PR itself.")
c("s17", 1, "0198", 85.98, 88.08, "你一句话和它说了，它也会开。", "Or if you just tell it to, it will.")
c("s17", 2, "0198", 88.08, 94.90, "PR 开了之后，他会继续盯着：CI 如果挂了，他就能自己修复，如果有 review 评审意见，他就会来继续改。", "After the PR opens it keeps watching: if CI fails it can fix it itself, and if there are review comments it keeps revising.")
c("s17", 3, "0198", 95.28, 101.10, "想看所有的 PR 状态呢，就可以去 Overview 里面，去 PR 的这个标签页，就可以全部看到。", "To see every PR's status, go to the PR tab in Overview, and you'll see them all.")
c("s17", 5, "0198", 101.10, 104.10, "如果想合并的话，只要和 Claude 说一声合并就可以了。", "If you want to merge, just tell Claude to merge.")
c("s18", 0, "0198", 104.10, 106.20, "合完之后，再跟他说，写份复盘。", "After the merge, tell it one more thing: write a post-mortem.")
c("s18", 1, "0198", 106.20, 112.96, "他就会再开一个线程，把所有的这些线程的前后上下文，去做成一个报告，放到 Library 里面。", "It starts another thread, turns the context from all those threads into a report, and puts it in the Library.")
c("s18", 2, "0198", 113.54, 116.42, "官方管这个 Library，叫项目的共享文件夹。", "The video calls the Library the project's shared folder.")
c("s18", 3, "0198", 116.42, 120.66, "每个线程都读得到，下次可以再优化，他也会直接更新这份报告。", "Every thread can read it, so next time it can optimize again and simply update the report.")
c("s19", 0, "0198", 122.10, 128.50, "那最后一步就是，接上这个监控服务，去让他更加的自动化，演示里用的是 Sentry。", "The last step: connect a monitoring service to automate it further — Sentry, in the demo.")
c("s19", 1, "0198", 129.20, 133.32, "再让他新建一个例程，也就是开一个 routine 定时任务。", "Then have it create a routine — a scheduled task.")
c("s19", 2, "0198", 136.66, 139.10, "查到回归，他自己开线程调查。", "If it finds a regression, it starts a thread to investigate on its own.")
c("s19", 3, "0198", 139.10, 141.08, "你下次打开项目，他已经在等你了。", "Next time you open the project, it's already waiting for you.")
c("s19", 4, "0198", 142.14, 146.60, "这个例程，或者说这个 routine 的本身，官方标的是 research preview。", "The routine feature itself is labeled research preview by the official side.")
c("s19", 5, "0198", 147.06, 148.70, "行为和限制都可能会变。", "Behavior and limits may change.")
c("s20", 0, "0198", 149.26, 150.92, "演示里他真的查到了一个：", "In the demo it actually finds one:")
c("s20", 1, "0198", 150.92, 156.56, "在 Pricing 价格页面，手机端 LCP 3.4 秒，前一天是 2.1 秒。", "on the pricing page, mobile LCP is 3.4 seconds, up from 2.1 the day before.")
c("s20", 2, "0198", 156.56, 161.18, "原因是一张 1.9MB 的 PNG，影响了加载的速度。", "The cause is a 1.9 MB PNG slowing down loading.")
c("s21", 0, "0198", 163.02, 168.00, "那么怎么去上手呢？你打开这个 Claude Code，你就可以看到，你的左侧有一个 Project。", "So how do you get started? Open Claude Code and you should see Projects in your left sidebar.")
c("s21", 1, "0198", 168.70, 174.36, "你也可以在网址 claude.ai/code 里面，去打开它的这个网页端。", "You can also open the web version at claude.ai/code.")
c("s21", 2, "0198", 174.76, 176.24, "那么手机 App 里面也有。", "The mobile app has it too.")
c("s21", 3, "0198", 176.66, 179.92, "如果你没有的话，那说明这个还没有轮到你。", "If you don't see it, it just hasn't reached you yet.")
c("s21", 4, "0198", 179.92, 183.38, "官方留了这个等候名单，这个链接会放在简介里。", "The official side has a waitlist, and I'll put the link in the description.")
c("s21", 5, "0198", 183.38, 188.40, "如果没有开通的话，你就可以去官方那一页去看一下，里面有五种的并行方式。", "If you don't have access yet, check the official page: it lists five ways to run work in parallel.")
c("s22", 0, "0198", 189.64, 194.60, "那么第二步就是新建一个项目。点击这个 Project，它会弹出来，叫你输入它的名字。", "Step two: create a project. Click Projects and a dialog asks for its name.")
c("s22", 1, "0198", 194.60, 195.76, "只有名字是必须的。", "Only the name is required.")
c("s22", 2, "0198", 195.76, 199.38, "目标你可以写一行，仓库文件都可以之后再添加。", "Write the goal in one line; repositories and files can be added later.")
c("s23", 0, "0198", 199.76, 201.48, "做代码项目里面，有三个前提：", "For code projects there are three prerequisites:")
c("s23", 1, "0198", 201.48, 203.78, "就是代码要放在 GitHub 上，它才能关联上。", "Your code must be on GitHub so it can be linked.")
c("s23", 2, "0198", 204.16, 207.48, "账号必须要有 push 权限，装了 Claude GitHub App。", "Your account needs push access, and the Claude GitHub App must be installed.")
c("s23", 3, "0198", 208.18, 212.44, "GitLab、Bitbucket 都不行，它现在只支持 GitHub。", "GitLab and Bitbucket don't work; for now it only supports GitHub.")
c("s23", 4, "0198", 212.88, 214.98, "然后 GitHub Enterprise Server 也不行。", "And GitHub Enterprise Server doesn't work either.")
c("s23", 5, "0198", 214.98, 219.60, "没有仓库也行，做调研、写文章，成果可以放进 Library 里面。", "No repository is fine too: do research, write articles, and put the results in the Library.")
c("s24", 0, "0198", 220.04, 223.60, "第三步的话，就是写项目说明，上限是 16000 个字符。", "Step three is writing the project instructions, up to 16,000 characters.")
c("s24", 1, "0198", 223.98, 225.44, "官方建议写五样：", "The docs suggest writing five things:")
c("s24", 2, "0198", 225.44, 228.52, "项目是为了什么，分支怎么开，做完怎么检查。", "what the project is for, which branch to use, how to check the work,")
c("s24", 3, "0198", 228.52, 231.22, "缺东西怎么办，哪些要先问你。", "what to do when something is missing, and what to ask you first.")
c("s24", 4, "0198", 231.22, 234.48, "官方给的例子里有一条：缺什么，就停下来说清楚。", "One line in the official example: if something is missing, stop and say exactly what.")
c("s24", 5, "0198", 234.48, 236.90, "不许替代，不许模拟，不许猜。", "No substituting, no mocking, no guessing.")
c("s24", 6, "0198", 237.34, 240.94, "合并、强推、改 CI 配置，都需要先在线程里等你回答。", "Merging, force-pushing and changing CI config all need to wait for your answer in the thread first.")
c("s25", 0, "0198", 241.50, 244.18, "第四步，先丢一块真的任务。", "Step four: send one real task first.")
c("s25", 1, "0198", 244.18, 247.38, "先看它怎么汇报，再把你的整批任务给丢进去。", "See how it reports back, then send in your whole batch.")
c("s25", 2, "0198", 248.04, 250.82, "还有一个前提就是，你的第一个项目建好之后，", "One more thing: after your first project is created,")
c("s25", 3, "0198", 250.82, 254.84, "如果你是没有发消息的话，Claude Code 它会自己先跑一轮，去摸个底。", "if you haven't sent a message, Claude Code takes a turn on its own to get a feel for it.")
c("s25", 4, "0198", 254.84, 257.28, "这一轮也是会花你的额度的。", "That turn uses your plan too.")
c("s25", 5, "0198", 257.28, 260.56, "Library 一次最多可以添加 100 个文件，2GB。", "The Library takes up to 100 files and 2 GB at a time.")
c("s25", 6, "0198", 263.06, 265.14, "单个文件最多 480MB。", "A single file can be at most 480 MB.")
c("s25", 7, "0198", 266.62, 270.20, "超过 30MB 的这个文件，建项目时会被跳过，建好的话再传。", "Files over 30 MB are skipped when you create the project; upload them after.")
c("s26", 0, "0198", 271.58, 273.76, "官方给了三个建议，在视频的最后。", "At the end of the video the official side gives three tips.")
c("s26", 1, "0198", 273.76, 276.12, "第一条就是，一定要控制你的额度。", "Tip one: keep your usage under control.")
c("s26", 2, "0198", 276.80, 279.38, "这每一个线程，都是一个完整的 Claude Code 会话。", "Every thread is a full Claude Code session.")
c("s26", 3, "0198", 280.70, 283.52, "同时开几个的话，额度会掉得非常快。", "Run several at once and your plan drains very fast.")
c("s26", 4, "0198", 297.60, 299.66, "新项目默认全都是 Opus。", "A new project runs Opus everywhere by default.")
c("s26", 5, "0198", 299.66, 303.88, "文档里面写的是线程 high effort，协调员 low effort。", "The docs say threads at high effort and the coordinator at low.")
c("s26", 6, "0198", 304.26, 308.08, "但演示里的这个设置页，线程显示的是 Medium。", "But in the demo's settings page, threads show Medium.")
c("s26", 7, "0198", 309.32, 310.68, "以你自己看到的为准。", "Go by what you see on your own screen.")
c("s26", 8, "0198", 311.20, 314.76, "官方建议的话，协调员可以留在低的 effort。", "The advice: leave the coordinator on low effort.")
c("s26", 9, "0198", 314.76, 319.80, "它主要是分这个任务，调高了也没有太多的性价比。", "It mostly routes tasks, so turning it up isn't worth much.")
c("s26", 10, "0198", 320.36, 325.68, "线程可以用默认小一点的模型，大任务再切好一点的模型。", "Threads can default to a smaller model; switch to a better one for bigger tasks.")
c("s26", 11, "0198", 326.28, 328.86, "演示里就是把线程的模型改成了 Sonnet。", "In the demo they switch the thread model to Sonnet.")
c("s27", 0, "0198", 329.86, 332.18, "第二步，就是要告诉 Claude 你想怎么做。", "Tip two: tell Claude how you want it to work.")
c("s27", 1, "0198", 332.78, 335.30, "你想同时跑几个，多久汇报一次。", "How many threads at once, how often to report back.")
c("s28", 0, "0198", 339.36, 343.22, "第三点的话，线程是会共享记忆的。", "Tip three: threads share memory.", skip=[(340.08, 340.98)])
c("s28", 1, "0198", 344.34, 347.70, "你可以先告诉他你的偏好是什么，之后每个线程都会读到。", "Tell it your preferences first, and every later thread will read them.")
c("s28", 2, "0198", 347.70, 350.84, "设置里你能看到，你能改，你能删。", "In settings you can see it, edit it, and delete it.")
c("s28", 3, "0198", 350.84, 357.26, "它和你本机的这个 CLAUDE.md，本机的这个自动的 memory.md 的 md 文件，是分开来的。", "It's separate from your local CLAUDE.md and your machine's auto-memory MEMORY.md files.")
c("s29", 0, "0198", 358.42, 360.78, "那文档里还有几个细节，它比较容易漏。", "The docs have a few more details that are easy to miss.")
c("s29", 1, "0198", 360.78, 363.82, "比如说线程你要批准的时候，得点到线程里面去点。", "For example, when a thread needs your approval, you have to go into the thread to approve.")
c("s29", 2, "0198", 364.44, 367.70, "然后在项目对话里说同意的时候，它是收不到的。", "Saying yes in the project conversation doesn't reach it.")
c("s29", 2, "0198", 367.70, 371.18, "你必须要把这个线程点开，然后去点这个 Allow 这个按钮。", "You have to open the thread and click the Allow button.")
c("s30", 0, "0198", 372.50, 374.80, "在 Overview 面板，线程又分成六组：", "In the Overview pane, threads are sorted into six groups:")
c("s30", 1, "0198", 374.80, 383.66, "它会等你评审，等你回复，等你跑完了之后，它会再合并，再闲着，然后最后解决。", "waiting for your review, waiting for your reply, running, then landing, idle, and finally resolved.")
c("s30", 2, "0198", 383.66, 387.44, "如果一周没动静的线程，它会自动归档，归档到已解决。", "A thread with no activity for a week is archived automatically as resolved.")

# ═══════════════ 0199（162.4 s）：本地线程、什么时候用、对比
c("s31", 0, "0199", 0.70, 4.56, "如果你还是不想上云的话呢，那你就也可以在本地跑。", "If you'd rather not go to the cloud, you can also run it locally.")
c("s31", 1, "0199", 7.20, 10.18, "你可以在加号菜单里面选择 Work Locally。", "Pick Work Locally from the plus menu.")
c("s31", 2, "0199", 11.52, 14.12, "它有一个版本要求，然后电脑你得一直开着。", "It has a version requirement, and your computer has to stay on.", skip=[(10.92, 11.24)])
c("s32", 0, "0199", 15.52, 19.90, "云端线程的话，它不继承你本机装的任何东西。", "Cloud threads don't inherit anything installed on your machine.")
c("s32", 1, "0199", 20.04, 24.16, "如果要用连接器 Connector 的话，要连到你的 Claude.ai 账号上，你得先登录。", "To use connectors, connect them to your Claude.ai account — you have to log in first.")
c("s32", 2, "0199", 24.84, 29.80, "而技能和子代理呢，你也得先提交到你的云端仓库里的这个 .claude 隐藏目录下面。", "And skills and subagents need to be committed to the .claude hidden folder in your cloud repository first.")
c("s33", 0, "0199", 33.56, 36.56, "那什么时候值得去用这个 Project？", "So when is Projects worth using?")
c("s33", 0, "0199", 37.60, 41.32, "这个任务，而不是在本地的文件夹里去做这个事情呢，", "For this kind of task, rather than just working in a local folder:")
c("s33", 1, "0199", 41.32, 50.14, "就比如说，你的目标它会比一次的这个 session 更大，而且它会跨好几个文件夹，要并行很多的这个任务。", "say your goal is bigger than one session, spans several folders, and needs lots of tasks in parallel.")
c("s33", 2, "0199", 50.48, 53.50, "就比如说，把应用从废弃的这个包给迁走，", "For example, migrating an app off a deprecated package,")
c("s33", 3, "0199", 53.50, 58.96, "或者一个接口会同时改 API、网页和手机三个仓库，那这个时候你就要使用 Project。", "or changing one endpoint across the API, web and mobile repos — that's when you use Projects.")
c("s34", 0, "0199", 60.78, 64.16, "Claude Code 现在有五种，同时可以干很多事情的方式：", "Claude Code now has five ways to do many things at once:")
c("s34", 1, "0199", 64.16, 66.86, "比如子代理，agent view，agent teams，", "subagents, agent view, agent teams,")
c("s34", 2, "0199", 67.30, 70.90, "Dynamic Workflow，动态工作流，再加上现在出的这个 Project。", "dynamic workflows, plus the Projects that just came out.")
c("s34", None, "0199", 71.34, 73.66, "你有很多种选择方式。", "You have plenty of options.")
c("s34", 3, "0199", 74.12, 76.70, "官方给 Project 这个定位很具体：", "The official positioning of Projects is quite specific:")
c("s34", 4, "0199", 77.18, 84.80, "活儿跨很多的任务，持续几周，电脑关了也要跑，你就需要去使用它这个 Project。", "work with many tasks, lasting weeks, that has to keep running with your computer off — that's when you use it.")
c("s34", 5, "0199", 84.80, 92.28, "而且你只想描述一次，不是想在每开一个新的窗口，都需要重复描述你的需求、你的偏好，也不想一个个盯。", "And you want to describe it once, not repeat your requirements and preferences in every new window, and not watch each one.")
c("s34", 6, "0199", 92.94, 97.12, "agent teams 还标着这个实验性质的。", "Agent teams is still labeled experimental.")
c("s34", 7, "0199", 99.38, 101.74, "Project 现在是 public beta。", "Projects is in public beta.")
c("s35", 0, "0199", 103.62, 107.94, "反过来说，什么情况不要用 Project 呢？有四种：", "Conversely, when shouldn't you use Projects? There are four cases:")
c("s35", 1, "0199", 107.94, 112.72, "就是一个会话你就能干完的，你就不用去 Project 干。", "If one session can finish the job, you don't need Projects.")
c("s35", 2, "0199", 113.10, 118.64, "还有一个就是，每个任务都离不开你本地的这些文件，那就你在你本地跑。", "If every task needs your local files, run it locally.")
c("s35", 3, "0199", 119.26, 124.60, "还有一个就是单个的这个定时任务，没有对话，建一个 routine 就能解决了。", "If it's a single scheduled task with no conversation, a routine is enough.")
c("s35", 4, "0199", 126.00, 138.00, "如果说一群人要在 Slack 里面一起去讨论，一起去指挥的话，那就去 Slack 里面去装这个 Claude Tag，就用不到这个 Project。",
  "If a group of people want to steer it together in Slack, install Claude Tag in Slack — you don't need Projects.")
c("sA1", 0, "0199", 140.20, 142.34, "那它的额度消耗是很大的，", "Its usage cost is high,")
c("sA1", 1, "0199", 142.34, 145.02, "那 Project 它会比单个会话更费额度。", "Projects burns through your plan faster than a single session.")

# ═══════════════ 0200（28.9 s）：收尾
c("sA3", 0, "0200", 3.00, 6.66, "那，所以说，该不该用这个 Project？", "So — should you use Projects?")
c("sA3", 1, "0200", 6.88, 10.68, "判断的依据只有一个，就是你的任务是不是比一次会话还长。", "There's only one test: is your task longer than a single session?")
c("sA3", 2, "0200", 11.18, 16.40, "如果你这个会话很长，而且你要跨很多个文件夹，可能要几天几周，任务会一直来，", "If your session is long, spans lots of folders, may take days or weeks, and tasks keep coming,")
c("sA3", 2, "0200", 16.64, 21.22, "而且你希望你下班了，电脑在路上，它也要在云端跑，", "and you want it to keep running in the cloud even after you've left work with your laptop in transit,")
c("sA3", 3, "0200", 21.62, 23.50, "那么你就很值得去开一个 Project。", "then it's well worth starting a project.")
c("sA3", 6, "0200", 25.62, 28.34, "好的，本期视频就到这里，谢谢大家观看。", "Alright, that's it for this video. Thanks for watching.")


def main():
    for i, x in enumerate(C):
        x["id"] = f"C{i + 1:03d}"
        x["pid"] = x["scene"]
    (HERE / "cues.json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "cut_list.json").write_text(json.dumps([dict(clip=a, s=b, e=c_, said=d, why=e) for a, b, c_, d, e in CUT], ensure_ascii=False, indent=1), encoding="utf-8")
    span = sum(x["e"] - x["s"] for x in C)
    print(f"{len(C)} 条字幕，口播共 {span:.1f} s（原录像 {sum(json.loads((HERE / 'asr' / f'{i}.json').read_text(encoding='utf-8'))['duration'] for i in ['0196', '0197', '0198', '0199', '0200']):.1f} s）；删掉 {len(CUT)} 处")


if __name__ == "__main__":
    main()
