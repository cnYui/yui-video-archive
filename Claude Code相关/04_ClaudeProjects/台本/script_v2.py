# -*- coding: utf-8 -*-
r"""口播稿 v2 + 镜头表 + 英文字幕的唯一来源（改稿子、改镜头都改这个文件，再跑一遍）：

    python script_v2.py

生成：
  台本\录制稿.json        build_timeline.py 读：每句 zh / say / en（中英双语字幕标准：每句必须有 en）
  台本\plan.json          build_timeline.py 读：场景表（素材段 / 页面镜头 / A 版式要点）
  制作\00_整片\scenes_gen.js   页面镜头（pageShot）、演示视频上的中文译文条（note）、高亮框（box），按每句的开口时刻排
  台本\口播稿_v2.md       给悠一照着念的稿子（一幕一节，每个场景写了画面）

约定：
- d1 = @ClaudeDevs 官方 4 分钟视频原片（3840×2160，24 fps）。**只用没有讲师露脸的段**（faces.json 的 safe 区间）：
  [1.0–5.0] [9.8–20.2] [25.6–34.0] [41.4–44.4] [48.0–53.0] [70.4–111.0] [114.0–124.2] [127.2–148.4] [151.4–176.8] [179.8–184.8]
  [187.6–197.2] [213.6–235.4] [238.6–246.2] [249.0–254.2] [259.0–264.4]。75–76 s、121–122 s 是误报（界面里的图标），已人工看过，可以用。
- 场景的素材段写 (入点, 出点) 秒；话比画面长时，build_timeline 把最后一段接着往下放——所以每个素材场景末尾自动补一小段定格（取最后一段出点前 0.15 s 的一帧），
  话比画面长的部分就定格在这一帧，不会放进讲师露脸的段。
- 每句 (中文, 英文)；录制稿里 say = 中文；估时 4.9 字/秒（build_timeline.py 的 EST_CPS），录完口播后按实际识别结果重排。
"""
import json
from pathlib import Path

EP = Path(r"D:\大疆\Claude Code相关\04_ClaudeProjects")
CHAPTERS = ["它是什么", "怎么用", "用不用"]            # 左栏目录（≤ 3 条、每条 ≤ 7 字）
CREDIT = "@ClaudeDevs · X（官方演示）"


def Z(*v):
    """原片抽成 1600 宽的帧里量的 (x, y, w, h) → 演示区 1474×829 的坐标（× 0.92125）"""
    return tuple(round(a * 0.92125) for a in v)


# ───────────────────────── 场景表
# kind: clip（素材段 d1）/ page（官方页面、推文录屏）/ A（出镜大框 + 右边要点）
# lines: [(中文, 英文), …]；pages / notes / boxes / ui 里的 k 是本场景里第几句（从 0 数）
S = []


def clip(id, act, ch, ranges, lines, notes=(), boxes=(), boxes_src=(), sync=None, name=""):
    """sync = (k, 原片秒)：原片这一秒的画面在本场景第 k 句开口时出现（只在“按实际口播生成”时用）"""
    S.append(dict(id=id, act=act, kind="clip", chapter=ch, ranges=ranges, lines=lines, notes=list(notes), boxes=list(boxes), boxes_src=list(boxes_src), sync=sync, name=name or id))


def page(id, act, ch, pages, lines, name=""):
    S.append(dict(id=id, act=act, kind="page", chapter=ch, pages=pages, lines=lines, name=name or id))


def card_a(id, act, ch, ui, lines, name=""):
    S.append(dict(id=id, act=act, kind="A", chapter=ch, ui=ui, lines=lines, name=name or id))


# ═════════ 开场（A 版式，只在“按实际口播生成”时用：悠一打招呼 + 一句话结论）
ACT00 = "开场"
card_a("sOpen", ACT00, -1, dict(kick="今天讲什么", h1="Claude Code Projects：什么时候该用？", items=[
    dict(t="任务要跨多个文件夹", s="", k=3, off=2.6), dict(t="需要长期地跑", s="", k=3, off=4.5), dict(t="合上电脑也要能跑", s="", k=3, off=6.4)],
    verdict=[dict(t="那就应该用 Project", s="", k=3, off=8.4, cls="go")]), [("（开场）", "(opening)")], name="开场：悠一 + 一句话结论")

# ═════════ 幕 0　钩子
ACT0 = "幕 0　钩子"
clip("s01", ACT0, -1, [(1.0, 5.0), (9.8, 20.2)], [
    ("官方演示里，发两条消息，Claude 在云上开出了 8 个线程。", "In the official demo, two messages are enough for Claude to start eight cloud threads."),
    ("8 个线程，同时修一个网站的性能问题。", "Eight threads, all fixing one website's performance problem at once."),
    ("这个功能，叫 Claude Code Projects。", "The feature is called Claude Code Projects."),
], name="钩子：官方演示")
page("s02", ACT0, -1, [dict(key="Y_blog", a=0, b=0, marks=[("now available in beta in Claude Code", 0, 0.3, "官方博客：更新后的 Projects 在 Claude Code 里公测")])], [
    ("9 月中旬，它在 Claude Code 里开了公测。", "In mid-September it went into public beta in Claude Code."),
], name="官方博客")
page("s03", ACT0, -1, [dict(key="X_t1", a=0, b=1, marks=[("every Pro and Max user", 1, 0.0, "官方推文：等候名单上的 Pro 和 Max 用户全部放进来了"),
                                                          ("4 minute walkthrough", 1, 3.0, "附了一个 4 分钟的上手视频")])], [
    ("这几天，官方推特又说：", "A few days ago the official account added:"),
    ("等候名单里的 Pro 和 Max 用户，已经全放进来了。", "everyone on the Pro and Max waitlist is now in."),
], name="官方推文")
clip("s04", ACT0, -1, [(25.6, 34.0)], [
    ("这期讲四件事：它是什么，怎么上手，什么时候用，哪里有坑。", "Four things today: what it is, how to start, when to use it, and where the traps are."),
], name="本期四件事")

# ═════════ 幕 1　它是什么
ACT1 = "幕 1　它是什么"
page("s05", ACT1, 0, [dict(key="D_intro", a=0, b=4, marks=[("doing the coordinating yourself", 1, 0.0, "没有 Projects：协调要你自己来"),
                                                          ("repeat the same background", 2, 0.0, "每个会话开头，重复同样的背景"),
                                                          ("check back to see which finished", 3, 0.0, "回头看谁做完了、谁在等你"),
                                                          ("Send work to one place", 4, 0.0, "有了 Projects：把活发到一个地方")])], [
    ("先看没有 Projects 的时候。", "First, what life looks like without Projects."),
    ("你同时开好几个会话，得自己分活。", "You run several sessions and divide the work yourself."),
    ("每个会话开头，背景要重讲一遍。", "Each session starts with you repeating the background."),
    ("过一阵，还得回头看：谁做完了，谁在等你。", "Later you check back: who finished, who is waiting on you."),
    ("Projects 把这些活，交给了 Claude。", "Projects hands that bookkeeping to Claude."),
], name="没有 Projects 的时候")
clip("s06", ACT1, 0, [(25.6, 34.0), (41.4, 44.4)], [
    ("一个 Project，就是一场不会结束的对话。", "A project is one ongoing conversation."),
    ("Claude 在里面当协调员。", "Claude acts as the coordinator inside it."),
    ("你把任务丢进去，它给每件事开一个线程。", "You drop tasks in and it starts a thread for each one."),
], sync=(2, 28.2), name="协调员和线程（官方示意动画）")
page("s07", ACT1, 0, [dict(key="Y_blog2", a=0, b=3, marks=[("Brief Claude in the project the way you'd brief a chief of staff", 0, 0.0, "官方博客：像给幕僚长交代工作一样"),
                                                          ("@@each thread is a Claude Code cloud session working on its own branch", 1, 0.0, "每个线程：云端的 Claude Code 会话，自己的分支")])], [
    ("官方博客的比方：像给一位幕僚长交代工作。", "The blog's comparison: briefing a chief of staff."),
    ("线程是什么？一个云端的 Claude Code 会话。", "What's a thread? A Claude Code session running in the cloud."),
    ("它有自己的分支，自己的上下文窗口。", "It has its own branch and its own context window."),
    ("该开 PR，它就开 PR。", "When it needs a pull request, it opens one."),
], name="幕僚长和线程")
page("s08", ACT1, 0, [dict(key="Y_blog_body", a=0, b=1, marks=[("even from your phone", 1, 0.0, "手机上也能看进度、发指令；你离开电脑，它继续干")])], [
    ("你合上电脑，云端线程照跑。", "Close your laptop and the cloud threads keep going."),
    ("手机上，也能看进度，也能发指令。", "From your phone you can check progress and steer."),
], name="合上电脑也在跑")
page("s09", ACT1, 0, [dict(key="S_old", a=0, b=4, marks=[("self-contained workspaces", 1, 0.0, "聊天里的 Projects：自成一体的工作区"),
                                                       ("Free users can create a maximum of five projects", 3, 0.0, "免费账号最多 5 个")])], [
    ("Projects 这个名字，你可能早就用过。", "You may already know the name Projects."),
    ("在聊天里，它是个资料夹。", "In chat, it's a folder."),
    ("聊天记录，加知识库，再加一段项目说明。", "Chats, a knowledge base, plus project instructions."),
    ("免费用户也能建，最多 5 个。", "Free users can create up to five."),
    ("Cowork 里也有一套：任务、文件、说明、记忆，放进一个工作区。", "Cowork has its own: tasks, files, instructions and memory in one workspace."),
], name="聊天里本来就有 Projects")
page("s10", ACT1, 0, [dict(key="Y_blog", a=0, b=1, marks=[("from folder to conversation", 0, 0.0, "官方博客：从文件夹，到对话")])], [
    ("这次是升级。官方博客的标题就叫：从文件夹，到对话。", "This is an upgrade. The blog title says it: from folder to conversation."),
    ("升级后，一个 Project 是一场对话，加一群线程。", "After the upgrade, a project is one conversation plus a crowd of threads."),
], name="升级：从文件夹到对话")
page("s11", ACT1, 0, [dict(key="S_new", a=0, b=4, marks=[("chat, Cowork, Team, and Enterprise will follow", 0, 0.0, "先从 Claude Code 开始，聊天、Cowork、Team、Enterprise 之后跟上"),
                                                       ("Existing projects in chat and Cowork keep working as they do today", 1, 0.0, "已有的项目照常用")])], [
    ("先在 Claude Code 里公测，聊天和 Cowork 之后跟上。", "It starts in Claude Code, with chat and Cowork to follow."),
    ("Pro 和 Max 上，你已有的项目照常用，放量到了，官方替你升级。", "On Pro and Max, your existing projects keep working and get upgraded as the rollout reaches them."),
    ("现阶段有个差别。", "One difference for now."),
    ("聊天里的项目，Team 和 Enterprise 能共享。", "Projects in chat can be shared on Team and Enterprise."),
    ("升级版，一个项目只属于你一个人。", "In the upgraded version, a project belongs to you alone."),
], name="升级的节奏和差别")

# ═════════ 幕 2　官方演示
ACT2 = "幕 2　官方演示：一个网站，8 个线程"
clip("s12", ACT2, 0, [(70.4, 74.0)], [
    ("官方的 4 分钟视频，演示了一个场景。", "The official four-minute video walks through one scenario."),
    ("一个营销网站，性能掉了整整一个月。", "A marketing site whose performance has been slipping for a month."),
], name="演示：开场")
clip("s13", ACT2, 0, [(74.0, 83.0)], [
    ("先建项目：名字，目标，仓库。", "First, create a project: a name, a goal, repositories."),
    ("目标就写一行：LCP 压到 2.5 秒以下，CLS 压到 0.1 以下。", "The goal is one line: LCP under 2.5 seconds and CLS under 0.1."),
    ("LCP 是主要内容出现的时间，CLS 是页面抖不抖。", "LCP is when the main content shows up; CLS is how much the page jumps around."),
], name="演示：新建项目")
clip("s14", ACT2, 0, [(83.5, 96.0)], [
    ("建好进入主对话，Claude 先给了 4 条建议。", "In the main conversation, Claude first offers four suggestions."),
    ("比如：读仓库，提方案。", "For example: read the repo and propose next steps."),
    ("官方的话：可以挑一条，问个小问题，或者直接丢一串任务。", "The video says: pick one, ask a quick question, or hand over a list of tasks."),
], name="演示：主对话")
clip("s15", ACT2, 0, [(96.0, 111.0)], [
    ("第一条消息：把指标贴进去，让 Claude 先读代码、给方案。", "First message: paste in the metrics and ask Claude to read the code and propose fixes."),
    ("它先开一个线程，去读两个仓库。", "It first starts one thread to read both repositories."),
    ("回来列了 8 条建议。", "It comes back with eight suggestions."),
    ("还说：前三条占了大部分 LCP 和 CLS，建议先做。", "It adds: the first three account for most of the LCP and CLS, so start there."),
    ("第二条消息，只有一句：全都做。", "The second message is one line: do all of them."),
], notes=[(0, 1, "发给 Claude 的第一条消息：营销网站的 Core Web Vitals 掉了一个月，手机端 p75 LCP 4.1 秒、CLS 0.28，用户说导航慢。先读两个仓库，再按影响大小提修复方案。", "", dict(x=40, y=300, w=1394))],
     name="演示：两条消息")
clip("s16", ACT2, 0, [(114.0, 124.2), (127.2, 134.0)], [
    ("Claude 回：8 个线程，一个任务一个。", "Claude replies: eight threads, one per task."),
    ("优化图片、预加载字体、拆 JS 包、给横幅留位置……", "Optimizing images, preloading fonts, splitting the JS bundle, reserving space for the banner…"),
    ("线程各读各的代码，各开各的分支。", "Each thread reads its own code and works on its own branch."),
    ("点开线程卡片，能看它一步步在干什么。", "Open a thread card to watch what it's doing, step by step."),
    ("你可以直接在线程里改它的方向，也可以叫停。", "You can steer it right inside the thread, or stop it."),
], notes=[(0, 1, "8 个线程：客户端导航 · 优化图片 · 缓存页面内容 · 懒加载脚本 · 预加载字体 · 拆 JS 包 · 给横幅留位置 · 压缩静态资源", "", dict(x=40, y=20, w=980))],
     name="演示：8 个线程")
clip("s17", ACT2, 0, [(134.0, 148.4)], [
    ("线程手里有了具体改动，比如修一个 bug，就自己开 PR。", "Once a thread has a concrete change, like a bug fix, it opens a PR itself."),
    ("你一句话，它也会开。", "Or you can ask, and it will."),
    ("PR 开了，它还接着盯：CI 挂了，它推修复；有评审意见，它来改。", "After the PR opens it keeps watching: if CI fails it pushes a fix, and it handles review comments."),
    ("想看所有 PR 的状态，", "To see the status of every PR,"),
    ("去 Overview 里的 Pull requests 标签页。", "go to the Pull requests tab in Overview."),
    ("想合并？跟 Claude 说一声。", "Ready to merge? Just tell Claude."),
], name="演示：PR")
clip("s18", ACT2, 0, [(152.0, 158.0), (162.0, 168.0), (172.0, 176.8)], [
    ("合完，再说一句：写份复盘。", "After the merge, one more request: write a post-mortem."),
    ("它开一个线程，把前后指标写成报告，放进 Library。", "It starts a thread, writes the before-and-after metrics into a report and puts it in the Library."),
    ("官方管 Library 叫“项目的共享文件夹”。", "The video calls the Library the project's shared folder."),
    ("每个线程都读得到，下次再优化，它直接更新这份报告。", "Every thread can read it, so next time it simply updates the report."),
], name="演示：复盘和 Library")
clip("s19", ACT2, 0, [(179.8, 184.8), (187.6, 197.2)], [
    ("最后一步：接上监控服务，演示里用的是 Sentry。", "Last step: connect a monitoring service — Sentry, in the demo."),
    ("再让它建一个例程，也就是定时任务，每天下午 5 点查一遍。", "Then have it create a routine, a scheduled task that checks every day at 5 pm."),
    ("查到回归，它自己开线程调查。", "If it finds a regression, it starts a thread to investigate."),
    ("你下次打开项目，它已经在等你了。", "Next time you open the project, it's already waiting for you."),
    ("例程本身，官方标的是 research preview。", "Routines themselves are labeled research preview."),
    ("行为和限制，都可能会变。", "Behavior and limits may change."),
], name="演示：连接监控、例程")
clip("s20", ACT2, 0, [(238.6, 242.8)], [
    ("演示里，它真查到了一个。", "In the demo, it actually finds one."),
    ("/pricing 页面，手机端 LCP 3.4 秒，前一天是 2.1 秒。", "On the /pricing page, mobile LCP is 3.4 seconds, up from 2.1 the day before."),
    ("原因：一张 1.9 MB 的 PNG。", "The cause: a 1.9 MB PNG."),
    ("说清楚：这个网站是官方做的演示，数字也是演示的。", "To be clear: the site is an official demo, and so are the numbers."),
], boxes=[(0, 0) + Z(185, 200, 1205, 92), (1, 1) + Z(180, 312, 1205, 92), (2, 2) + Z(250, 488, 700, 48)],
     notes=[(1, 1, "例程查到的回归：/pricing 手机端 p75 LCP 3.4 秒，前一天 2.1 秒", "", dict(x=40, y=585, w=1100)),
            (2, 2, "原因：/pricing 上一张 1.9 MB 的 PNG（线程问：要开 PR 吗？）", "", dict(x=40, y=585, w=1100)),
            (3, 3, "官方演示的数据，网站是虚构的公司", "", dict(x=40, y=585, w=900))],
     name="演示：例程查到回归")

# ═════════ 幕 3　怎么上手
ACT3 = "幕 3　怎么上手"
page("s21", ACT3, 1, [dict(key="D_note", a=0, b=5, marks=[("public beta on Pro and Max plans", 0, 0.0, "公开测试：Pro 和 Max 套餐"),
                                                         ("join the waitlist", 4, 0.0, "还没轮到你：加入等候名单")])], [
    ("第一步，看你的侧栏有没有 Projects。", "Step one: check whether Projects shows up in your sidebar."),
    ("网址 claude.ai/code，桌面端是 Code 标签。", "At claude.ai/code, or in the Code tab of the desktop app."),
    ("手机 App 里也有。", "It's in the mobile app too."),
    ("没有？说明还没轮到你。", "Not there? Your turn hasn't come yet."),
    ("官方留了等候名单，链接我放简介里。", "There's an official waitlist; I'll put the link in the description."),
    ("没开通，先看官方那页对比，里面有 5 种并行方式。", "Until then, see the official comparison page: it covers five ways to run work in parallel."),
], name="第一步：看侧栏")
page("s22", ACT3, 1, [dict(key="D_create", a=0, b=2, marks=[("Only the name is required", 1, 0.0, "只有名字是必填"),
                                                          ("one line of what you're trying to get done", 2, 0.0, "目标：一行字，写你想做成什么")])], [
    ("第二步，新建项目。", "Step two: create a project."),
    ("只有名字是必填。", "Only the name is required."),
    ("目标写一行，仓库、文件，都可以以后再加。", "Write the goal in one line; repositories and files can come later."),
], name="第二步：新建项目")
page("s23", ACT3, 1, [dict(key="D_prereq", a=0, b=5, marks=[("github.com rather than GitHub Enterprise Server, GitLab, or Bitbucket", 1, 0.0, "代码要在 github.com（不是企业版 / GitLab / Bitbucket）"),
                                                          ("push access to it", 2, 0.0, "账号要有 push 权限，装好 Claude GitHub App")])], [
    ("做代码项目有三个前提：", "Code projects have three prerequisites:"),
    ("代码要在 github.com 上。", "Your code must be on github.com."),
    ("账号有 push 权限，装了 Claude GitHub App。", "Your account needs push access, and the Claude GitHub App must be installed."),
    ("GitLab、Bitbucket，现在不行。", "GitLab and Bitbucket don't work yet."),
    ("GitHub Enterprise Server，也不行。", "Neither does GitHub Enterprise Server."),
    ("没有仓库也行：做调研、写文档，成果放进 Library。", "No repository is fine too: research and write documents, with results going to the Library."),
], name="代码项目的前提")
page("s24", ACT3, 1, [dict(key="D_ctx", a=0, b=0, marks=[("up to 16,000 characters", 0, 0.5, "项目说明：最多 16,000 个字符")]),
                      dict(key="D_instr", a=1, b=6, marks=[("What the project is for", 2, 0.0, "写什么：项目为了什么、分支、自查、缺东西怎么办、先问你什么"),
                                                          ("Don't substitute, mock, or guess.", 5, 0.0, "官方例子：缺东西就停下来说清楚，不许替代、模拟、猜"),
                                                          ("Don't merge, force-push, or change CI configuration", 6, 0.0, "合并、强推、改 CI 配置，要先问你")])], [
    ("第三步，写项目说明。上限 16,000 个字符。", "Step three: write the project instructions — up to 16,000 characters."),
    ("官方建议写五样：", "The docs suggest five things:"),
    ("项目为了什么，分支怎么开，做完怎么自查。", "What the project is for, which branch to use, how to check the work."),
    ("缺东西怎么办，哪些要先问你。", "What to do when something is missing, and what needs your go-ahead."),
    ("官方给的例子里，有一条：缺什么，就停下来说清楚。", "One line in the official example: if something is missing, stop and say exactly what."),
    ("不许替代，不许模拟，不许猜。", "No substituting, no mocking, no guessing."),
    ("合并、强推、改 CI 配置，要先在线程里问你。", "Merging, force-pushing or changing CI config needs your OK in the thread first."),
], name="第三步：项目说明")
page("s25", ACT3, 1, [dict(key="D_batch", a=0, b=1, marks=[("Send one small piece of the real work", 0, 0.0, "先发一小块真实的活")]),
                      dict(key="D_create", a=2, b=4, marks=[("That turn uses your plan.", 4, 0.0, "这一轮也用你的额度")]),
                      dict(key="D_files", a=5, b=7, marks=[("up to 100 files and 2 GB in one pick", 5, 0.0, "Library：一次最多 100 个文件、2 GB"),
                                                          ("a single file up to 480 MB", 6, 0.0, "单个文件最多 480 MB"),
                                                          ("files over 30 MB are skipped", 7, 0.0, "建项目对话框里超过 30 MB 的文件会被跳过")])], [
    ("第四步，先丢一小块真活。", "Step four: send one small piece of real work first."),
    ("看它怎么汇报，再把整批任务丢进去。", "See how it reports back, then send the whole batch."),
    ("还有个提醒：第一个项目建好后，", "One warning: after your first project is created,"),
    ("你要是没先发消息，Claude 会自己先跑一轮。", "if you haven't sent a message, Claude takes a turn of its own."),
    ("这一轮，也花你的额度。", "That turn uses your plan too."),
    ("Library 一次最多加 100 个文件、2 GB。", "The Library takes up to 100 files and 2 GB at a time."),
    ("单个文件，最多 480 MB。", "A single file can be up to 480 MB."),
    ("超过 30 MB 的文件，建项目时会被跳过，建好再传。", "Files over 30 MB are skipped in the new-project dialog; add them afterwards."),
], name="第四步：先丢一小块真活")

# ═════════ 幕 4　官方的三条技巧
ACT4 = "幕 4　官方的三条技巧"
clip("s26", ACT4, 1, [(216.6, 235.4)], [
    ("官方视频最后，给了三条建议。", "At the end the video gives three tips."),
    ("第一条，管额度。", "Tip one: manage your usage."),
    ("每个线程，都是一个完整的 Claude Code 会话。", "Every thread is a full Claude Code session."),
    ("同时开几个，额度掉得比单个会话快。", "Run several at once and your plan drains faster than with one session."),
    ("新项目默认全用 Opus。", "A new project runs Opus everywhere by default."),
    ("文档写：线程 high effort，协调员 low effort。", "The docs say: threads at high effort, the coordinator at low."),
    ("但演示的设置页里，线程显示的是 Medium。", "But in the demo's settings page, threads show Medium."),
    ("以你自己设置页里看到的为准。", "Go by what your own settings page shows."),
    ("官方建议：协调员继续留在低 effort。", "The advice: leave the coordinator on low effort."),
    ("它主要是分活，调高了也没有明显更好。", "It mostly routes work, so a higher setting won't help much."),
    ("线程可以默认用小一点的模型，大任务再在线程里切。", "Threads can default to a smaller model; switch up inside a thread for bigger tasks."),
    ("演示里，就把线程的模型改成了 Sonnet。", "The demo switches the thread model to Sonnet."),
], sync=(10, 228.5), boxes=[(4, 4) + Z(460, 262, 910, 72), (4, 4) + Z(460, 438, 910, 72), (5, 5) + Z(460, 350, 910, 72), (5, 7) + Z(460, 526, 910, 72), (10, 11) + Z(460, 438, 910, 72)],
     notes=[(4, 4, "新项目默认：协调员和线程都是 Opus", "", dict(x=40, y=700, w=1000)),
            (6, 7, "演示的设置页：Thread effort = 默认 Medium（文档写的是 high）", "", dict(x=40, y=700, w=1100)),
            (10, 11, "演示里把 Thread model 改成了 Sonnet", "", dict(x=40, y=700, w=900))],
     name="三条技巧 1：管额度")
clip("s27", ACT4, 1, [(242.8, 246.2)], [
    ("第二条，直接告诉 Claude 你想怎么干。", "Tip two: tell Claude how you want it to work."),
    ("同时跑几个，多久汇报一次，开工前先给你看方案。", "How many threads at once, how often to update you, show a plan before starting."),
], name="三条技巧 2：告诉 Claude 怎么干")
clip("s28", ACT4, 1, [(249.0, 254.2)], [
    ("第三条，线程共享记忆。", "Tip three: threads share memory."),
    ("你让它记住的偏好，之后每个线程都会读到。", "Preferences you ask it to remember reach every later thread."),
    ("设置里，能看、能改、能删。", "In settings you can read, edit and delete it."),
    ("它和你本机的 CLAUDE.md、本机的自动记忆，是分开的。", "It's separate from your local CLAUDE.md and your machine's auto memory."),
], sync=(1, 251.6), boxes_src=[(253.4, 3) + Z(385, 505, 1110, 62), (253.4, 3) + Z(418, 703, 1042, 78), (253.4, 3) + Z(395, 30, 950, 70)],   # 按镜头推近之后（254 s 定格那一帧）量的
     notes=[(1, 2, "Auto memory：Claude 自己写的笔记，每个线程开工都读", "", dict(x=40, y=730, w=1100)),
            (3, 3, "项目说明（Project instructions）像 CLAUDE.md，上限 16,000 字符", "", dict(x=40, y=730, w=1100))],
     name="三条技巧 3：共享记忆")

# ═════════ 幕 5　文档里藏着的细节
ACT5 = "幕 5　文档里藏着的几个细节"
page("s29", ACT5, 1, [dict(key="D_approval", a=0, b=2, marks=[("the prompt is inside that thread", 1, 0.0, "批准的提示在线程里"),
                                                            ("Telling Claude in the project conversation to go ahead doesn't reach it.", 2, 0.0, "在项目对话里说“同意”，传不到线程")])], [
    ("文档里，有几处细节，容易漏。", "A few details in the docs are easy to miss."),
    ("线程要你批准的时候，得进线程里点。", "When a thread needs your approval, you answer inside that thread."),
    ("在项目对话里说“同意”，传不过去。", "Saying 'go ahead' in the project conversation doesn't reach it."),
], name="批准要进线程")
page("s30", ACT5, 1, [dict(key="D_overview", a=0, b=2, marks=[("Ready for review", 1, 0.0, "6 组：等评审"),
                                                            ("Waiting on you", 1, 1.6, "等你回复"),
                                                            ("Resolved", 2, 0.0, "已解决：一周没动静自动归这里")])], [
    ("Overview 面板，把线程分成 6 组：", "The Overview pane sorts threads into six groups:"),
    ("等你评审，等你回复，在跑，在合并，闲着，已解决。", "ready for review, waiting on you, working, landing, idle and resolved."),
    ("一周没动静的线程，自动归到“已解决”。", "A thread with no activity for a week is resolved automatically."),
], name="Overview 的 6 组")
page("s31", ACT5, 1, [dict(key="D_local", a=0, b=4, marks=[("Work locally", 1, 0.0, "+ 菜单里选 Work locally"),
                                                         ("Both need Claude Code v2.1.280 or later", 2, 0.0, "电脑上的 Claude Code 要 v2.1.280 以上"),
                                                         ("but not with its memory files loaded", 4, 0.0, "收到项目说明，但不加载项目记忆文件")])], [
    ("活儿要在你自己的电脑上跑，也行。", "Work can also run on your own computer."),
    ("在 + 菜单里选 Work locally。", "Choose Work locally from the + menu."),
    ("Claude Code 要 2.1.280 以上，电脑还得醒着。", "You need Claude Code 2.1.280 or later, and the computer has to stay awake."),
    ("9 月的博客还写着“即将推出”，现在文档里已经有了。", "The September blog still said 'coming very soon'; now it's in the docs."),
    ("这种线程，不会加载项目记忆。", "Such a thread doesn't load the project memory."),
], name="在自己电脑上跑线程")
page("s32", ACT5, 1, [dict(key="D_tools", a=0, b=3, marks=[("Cloud threads don't have the skills", 0, 0.0, "云端线程没有你本机装的技能、MCP、插件"),
                                                         ("The project conversation itself has no connectors", 3, 0.0, "项目对话本身没有连接器")])], [
    ("云端线程，也不继承你本机装的东西。", "Cloud threads don't inherit what's installed on your machine."),
    ("要用连接器，连在你的 claude.ai 账号上。", "For connectors, connect them on your claude.ai account."),
    ("技能和子代理，提交进仓库的 .claude 目录。", "Skills and subagents go into the repo's .claude directory."),
    ("注意：项目对话本身没有连接器，要用的活，得交给云端线程。", "Note: the project conversation itself has no connectors; hand such work to a cloud thread."),
], name="云端线程不继承本机")

# ═════════ 幕 6　什么时候用，什么时候别用
ACT6 = "幕 6　什么时候用，什么时候别用"
card_a("s33", ACT6, 2, dict(kick="什么时候用", h1="什么时候值得用 Project？", items=[
    dict(t="目标比一次会话更大", s="", k=1, off=0.3), dict(t="要跨好几个文件夹", s="", k=1, off=3.2), dict(t="要并行很多任务", s="", k=1, off=5.6),
    dict(t="例：把应用从废弃的包上迁走", s="", k=2), dict(t="例：一个接口同时改 API、网页、手机三个仓库", s="", k=3)]), [
    ("官方视频里有张卡：什么时候该用 Project。", "The video has a card: when to reach for a project."),
    ("目标比一次会话大，跨好几个仓库，很多任务能并行。", "A goal bigger than one session, work across several repos, many tasks in parallel."),
    ("比如：把应用从废弃的包上迁走。", "For example, migrating an app off a deprecated package."),
    ("或者一个接口，同时改 API、网页、手机三个仓库。", "Or changing one endpoint across API, web and mobile repos."),
], name="什么时候值得用（出镜 + 要点）")
page("s34", ACT6, 2, [dict(key="A_table", a=0, b=7, marks=[("Public beta on Pro and Max", 3, 0.0, "Projects：Pro 和 Max 上公开测试"),
                                                         ("Experimental and disabled by default", 6, 0.0, "agent teams：实验性，默认关闭")])], [
    ("Claude Code 现在有 5 种，同时干多件事的方式：", "Claude Code now has five ways to do several things at once:"),
    ("子代理，agent view，agent teams，", "subagents, agent view, agent teams,"),
    ("dynamic workflows，再加 Projects。", "dynamic workflows, and Projects."),
    ("官方给 Projects 的定位很具体：", "The docs position Projects quite specifically:"),
    ("活儿跨很多任务，持续几天到几周，电脑关了也要接着跑。", "many tasks over days or weeks, and it should keep running when your machine is off,"),
    ("而且你想描述一次，不想一个个派、一个个盯。", "and you'd rather describe it once than dispatch and track each session."),
    ("agent teams 还标着 experimental。", "Agent teams is still labeled experimental."),
    ("Projects，是 public beta。", "Projects is a public beta."),
], name="5 种并行方式（官方对比页）")
page("s35", ACT6, 2, [dict(key="D_other", a=0, b=4, marks=[("One task that fits in a session", 1, 0.0, "一个会话够用：开云端会话"),
                                                         ("Work where every task needs your machine", 2, 0.0, "每个任务都要你的机器：本地会话 / agent view"),
                                                         ("One task that repeats on a schedule with no conversation around it", 3, 0.0, "单个定时任务：建例程"),
                                                         ("Several people giving Claude work and steering it together in a Slack channel", 4, 0.0, "多人在 Slack 里指挥：Claude Tag")])], [
    ("反过来，官方明说，这 4 种情况别用 Projects。", "Conversely, the docs say these four cases are not for Projects."),
    ("一个会话就能干完的单个任务，开云端会话就行。", "A single task that fits in one session: just start a cloud session."),
    ("每个任务都离不开你本机，用本地会话，或者 agent view。", "Every task needs your machine: use a local session or agent view."),
    ("单个定时任务、没有对话，建一个例程就行。", "One scheduled task with no conversation: just create a routine."),
    ("一群人在 Slack 里一起指挥，去看 Claude Tag。", "A group steering Claude together in Slack: look at Claude Tag."),
], name="官方说别用 Projects 的 4 种情况")

# ═════════ 幕 7　泼冷水（A 版式：出镜大框 + 右边要点）
ACT7 = "幕 7　泼冷水"
card_a("sA1", ACT7, 2, dict(kick="泼冷水", h1="额度：比单个会话更费", items=[
    dict(t="比单个会话更费额度", s="", k=1)]), [
    ("先说额度。", "First, usage."),
    ("官方明说：Projects 比单个会话更费额度，Pro 上更明显。", "The docs say it plainly: Projects burn through your plan faster than one session, especially on Pro."),
], name="泼冷水：额度")
card_a("sA2", ACT7, 2, dict(kick="泼冷水 ②", h1="边界：能做的有限", items=[
    dict(t="一个项目只属于你一个人", s="不能分享；beta 期没有组织级管控", k=1), dict(t="Team / Enterprise 还没有", s="", k=3),
    dict(t="云端沙盒回合之间会暂停", s="没提交的改动可能丢，长任务让它随时提交", k=5), dict(t="多仓库 + 官方托管环境", s="仓库里的权限规则传不到云端线程", k=7),
    dict(t="效果：官方没给数据", s="快多少、省多少，都没有", k=9), dict(t="演示里的网站是虚构的公司", s="", k=10)]), [
    ("再说边界。", "Now the limits."),
    ("一个项目只属于你自己，不能分享。", "A project belongs to you alone and can't be shared."),
    ("beta 期，没有组织级管控。", "No organization-level controls during the beta."),
    ("Team 和 Enterprise，现在还没有。", "Team and Enterprise don't have it yet."),
    ("云端线程的沙盒，回合之间会暂停。", "A cloud thread's sandbox pauses between turns."),
    ("恢复不了，就从新克隆接着干，没提交的改动可能丢。", "If it can't resume, it continues from a fresh clone, and uncommitted changes can be lost."),
    ("长任务，让它随时提交、推送。", "On long tasks, ask it to commit and push as it goes."),
    ("多个仓库，在官方托管环境里，仓库里的权限规则传不到云端线程。", "With several repos in the hosted environment, no repo's permission rules reach cloud threads."),
    ("最后，效果。", "Finally, results."),
    ("比自己手动开会话，快多少、省多少？官方没给数据。", "Faster or cheaper than opening sessions yourself? The docs give no numbers."),
    ("演示里的网站，是虚构的公司。", "The demo site belongs to a fictional company."),
], name="泼冷水：边界")

# ═════════ 幕 8　收尾
ACT8 = "幕 8　收尾"
card_a("sA3", ACT8, 3, dict(kick="该不该用？", h1="你的任务，比一次会话还长吗？", verdict=[
    dict(t="长：跨很多个文件夹、几天几周、任务一直来", s="", k=2, cls="go"),
    dict(t="→ 很值得开一个 Project", s="", k=3, cls="go")]), [
    ("所以，该不该用？", "So, should you use it?"),
    ("判据只有一个：你的活儿，是不是比一次会话还长。", "One test: is your job longer than a single session?"),
    ("活儿长：多个仓库，几天几周，任务一直在来。", "Long job: several repos, days or weeks, tasks that keep coming."),
    ("开一个 Project。", "Start a project."),
    ("活儿短，一个会话够了。", "Short job: one session is enough."),
    ("开十个会话不难，难的是记得它们各干到哪了。", "Opening ten sessions is easy; remembering what each one is doing is hard."),
    ("Projects 把这件事，也交给了 Claude。", "Projects hands that to Claude as well."),
], name="收尾：该不该用")


# ───────────────────────── 生成
class Pick:
    """场景里“稿子第 k 句”→ 对应的字幕条 id。稿子模式：k 就是第 k 句；实际口播模式：找带 k 的字幕条，没有就取前面最近的，再没有取第一条。"""

    def __init__(self, ids, ks=None):
        self.ids, self.ks = ids, ks

    def _idx(self, k, last):
        if self.ks is None:
            return min(k, len(self.ids) - 1)
        hit = [i for i, kk in enumerate(self.ks) if kk == k]
        if hit:
            return hit[-1] if last else hit[0]
        before = [i for i, kk in enumerate(self.ks) if kk is not None and kk <= k]
        return before[-1] if before else 0

    def f(self, k):
        return self.ids[self._idx(k, False)]

    def l(self, k):
        return self.ids[self._idx(k, True)]


def main():
    cues_path = EP / "制作" / "02_出镜" / "cues.json"
    real = cues_path.exists() and (EP / "制作" / "02_出镜" / "edit" / "edit.json").exists() and "--script" not in __import__("sys").argv
    lines, plan, gen = [], [], []
    scenes = [s for s in S if s["id"] != "sOpen"] if not real else list(S)
    picks = {}
    if real:
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        scenes2 = []
        for sc in S:
            cs = [c for c in cues if c["scene"] == sc["id"]]
            if not cs:
                continue
            sc = dict(sc)
            sc["lines"] = [(c["zh"], c["en"]) for c in cs]
            picks[sc["id"]] = Pick([c["id"] for c in cs], [c["k"] for c in cs])
            scenes2.append(sc)
        scenes = scenes2
        for c in cues:
            lines.append(dict(id=c["id"], zh=c["zh"], say=c["zh"], en=c["en"]))
        left = {c["scene"] for c in cues} - {s["id"] for s in S}
        assert not left, f"字幕条里有不认识的场景：{left}"
    else:
        n = 0
        for sc in scenes:                              # 稿子模式：先给每句编号
            ids = []
            for zh, en in sc["lines"]:
                n += 1
                lid = f"L{n:03d}"
                ids.append(lid)
                lines.append(dict(id=lid, zh=zh, say=zh, en=en))
            picks[sc["id"]] = Pick(ids)
    sid2ids = {sid: pk.ids for sid, pk in picks.items()}
    for sc in scenes:
        P = picks[sc["id"]]
        ids = sid2ids[sc["id"]]
        item = dict(id=sc["id"], name=sc["name"], chapter=sc["chapter"], layout="A" if sc["kind"] == "A" else "B",
                    lines=[dict(id=i, a=0) for i in ids])
        if sc["kind"] == "clip":
            rs = [dict(src="d1", **{"in": a, "out": b}) for a, b in sc["ranges"]]
            last = sc["ranges"][-1][1]
            rs.append(dict(src="d1", **{"in": round(last - 0.15, 3), "hold": 0.1}))        # 话比画面长时，定格在这一帧（别接着放进讲师露脸的段）
            item.update(type="clip", ranges=rs, credit=CREDIT)
            if real and sc.get("sync"):
                item["sync"] = dict(line=P.f(sc["sync"][0]), t=sc["sync"][1])
            for k0, k1, zh, small, opt in sc["notes"]:
                gen.append(f"note(S('{P.f(k0)}'), E('{P.l(k1)}'), {json.dumps(zh, ensure_ascii=False)}, {json.dumps(small, ensure_ascii=False)}, {json.dumps(opt, ensure_ascii=False)});")
            for k0, k1, x, y, w, h in sc["boxes"]:
                gen.append(f"box(S('{P.f(k0)}'), E('{P.l(k1)}'), {x}, {y}, {w}, {h});")
            for t0, k1, x, y, w, h in sc.get("boxes_src", []):
                gen.append(f"box(V('d1', {t0}), E('{P.l(k1)}'), {x}, {y}, {w}, {h});")
        elif sc["kind"] == "page":
            item.update(type="card", dur=1.0, overlay="page")
            for pi, pg in enumerate(sc["pages"]):
                marks = ",".join(f"[{json.dumps(nd, ensure_ascii=False)}, S('{P.f(k)}') + {off}, {json.dumps(zh, ensure_ascii=False)}]" for nd, k, off, zh in pg["marks"])
                fl = f"first: {'true' if pi == 0 else 'false'}, last: {'true' if pi == len(sc['pages']) - 1 else 'false'}"
                gen.append(f"pageShotSafe('{P.f(pg['a'])}', '{P.l(pg['b'])}', '{pg['key']}', [{marks}], {{start: 0, pad: 0, {fl}}});")
        else:
            ui = json.loads(json.dumps(sc["ui"], ensure_ascii=False))
            for it in ui.get("items", []) + ui.get("verdict", []):
                it["line"] = P.f(it.pop("k"))
            item.update(type="card", dur=1.0, overlay="A", ui=ui)
        plan.append(item)

    (EP / "台本" / "录制稿.json").write_text(json.dumps(dict(slug="claude-projects", title="Claude Code Projects", sub="Claude Code Projects", chapters=CHAPTERS, lines=lines),
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
    (EP / "台本" / "plan.json").write_text(json.dumps(dict(plan=plan), ensure_ascii=False, indent=1), encoding="utf-8")
    head = ("// 由 台本\\script_v2.py 生成，别手改（改 script_v2.py 再跑一遍）。页面镜头 / 译文条 / 高亮框，时间按每句的开口时刻排。\n"
            "window.__MISS = window.__MISS || [];\n"
            "function pageShotSafe(from, to, key, marks, opt) {\n"
            "  const m = PG[key]; if (!m) { window.__MISS.push('没有页面图 ' + key); return; }\n"
            "  const ok = marks.filter(x => { if (m.marks[x[0]]) return true; window.__MISS.push(key + ' 没有高亮句子 ' + x[0]); return false; });\n"
            "  pageShot(from, to, key, ok, opt);\n}\n")
    (EP / "制作" / "00_整片" / "scenes_gen.js").write_text(head + "\n".join(gen) + "\n", encoding="utf-8")
    if real:
        print(f"【按实际口播】{len(scenes)} 个场景，{len(lines)} 条字幕；生成 录制稿.json / plan.json / scenes_gen.js")
        return

    # 口播稿 v2（给悠一照着念）
    md = ["# 口播稿 v2：Claude Code Projects（横屏长视频，悠一出镜）", "",
          "- 这一版按官方 4 分钟视频（dotey 那条和官方原片一致）的演示顺序和官方中文文档的译法改过；每个场景写了画面。",
          "- 视频是**录制用无声版**：出镜位是空的占位框，字幕是这份稿子（按每秒 4.9 字估的时间，预览用）；你录好口播后，我按实际口播重排画面和字幕。",
          "- 一句一行，句号处可以停一口气；LCP、CLS 读字母；p75 读“P 七十五”；PR 读“P R”。",
          "- 事实出处见 `事实核对.md`；官方没写的，稿里明说“官方没写”。", ""]
    act = None
    for sc in scenes:
        if sc["act"] != act:
            act = sc["act"]
            md += ["", f"## {act}", ""]
        kind = {"clip": "官方演示视频", "page": "官方页面 / 推文录屏", "A": "出镜大框 + 右边要点"}[sc["kind"]]
        if sc["kind"] == "clip":
            kind += "（" + "、".join(f"{a}–{b} 秒" for a, b in sc["ranges"]) + "）"
        elif sc["kind"] == "page":
            kind += "：" + "、".join(p["key"] for p in sc["pages"])
        md.append(f"**【{sc['name']}】画面：{kind}**")
        md.append("")
        for lid, (zh, en) in zip(sid2ids[sc["id"]], sc["lines"]):
            md.append(f"{lid}　{zh}")
        md.append("")
    tot = sum(len(zh) for sc in scenes for zh, _ in sc["lines"])
    md += ["---", "", f"共 {len(lines)} 句、约 {tot} 字（含英文词的字母），按每秒 4.5–5 字约 {tot / 5 / 60:.1f}–{tot / 4.5 / 60:.1f} 分钟。"]
    (EP / "台本" / "口播稿_v2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(scenes)} 个场景，{len(lines)} 句，{tot} 字；生成 录制稿.json / plan.json / scenes_gen.js / 口播稿_v2.md")


if __name__ == "__main__":
    main()
