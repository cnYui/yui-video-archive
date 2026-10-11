# -*- coding: utf-8 -*-
r"""《Claude官方教程》系列① 十期的数据源：台本（zh 字幕 / say 念的字 / en 英文字幕）+ 每个场景的画面选段 + 本期叠加层。
gen_episode.py 从这里生成各期的 录制稿 / plan / 素材表 / 叠加层。选段的 a、b 取自 素材\2026-10_ClaudeAcademy\分镜\*.json 的 safe_in / safe_out（避开转场帧）。

  python series_data.py     自检：句数 / 汉字数 / 估时 / 禁用词（我 / 他 / 她、不是…而是…）
"""
import re
from pathlib import Path

EP_ROOT = Path(r"D:\大疆\Claude官方教程\短视频")
VIDEO_DIR = Path(r"D:\大疆\Claude官方教程\素材\2026-10_ClaudeAcademy\视频")

CRED = "官方教程 第{n}期"        # 黄贴纸（≤ 16 字）：系列名 + 期号，和封面贴纸一致

EPISODES = {}


def L(i, zh, say, en, **kw):
    d = {"id": f"N{i:02d}", "zh": zh, "say": say, "en": en}
    d.update(kw)
    return d


# ════════════════════════════════════════ 第 1 期｜Claude Code 是什么、怎么工作
EPISODES[1] = dict(
    folder="01_ClaudeCode是什么", slug="ClaudeCode是什么",
    title="Claude官方教程 第1期｜Claude Code 是什么、怎么工作",
    kicker="<b>Claude官方教程</b> 第1期",
    hook=["不是聊天框", "会自己验收的代理"],
    credit=CRED.format(n=1),
    src={"a": "CC101-01_what-is-claude-code__fl1DSmwQKKY.mp4", "b": "CC101-02_how-claude-code-works__6bs5b4FltCU.mp4", "c": "CC101-03_installing-claude-code__0kILa02vKuI.mp4"},
    lines=[
        L(1, "Claude Code 干活，就三步：找线索，动手，验结果。", "Claude Code 干活，就三步：找线索，动手，验结果。",
          "Claude Code works in three steps: gather context, take action, verify the result."),
        L(2, "官方入门课第一课，五月发布，出镜的是 Lewis Menelaws。", "官方入门课第一课，五月发布，出镜的是 Lewis Menelaws。",
          "Lesson one of the official intro course, published in May, taught by Lewis Menelaws."),
        L(3, "它和聊天窗口最大的差别，是能直接动你的文件和终端。", "它和聊天窗口最大的差别，是能直接动你的文件和终端。",
          "The big difference from a chat window: it can work on your files and terminal directly."),
        L(4, "聊天框给你一段代码，你得自己复制粘贴。它自己进去改。", "聊天框给你一段代码，你得自己复制粘贴。它自己进去改。",
          "A chat window hands you code to copy and paste. Claude Code goes in and edits it itself."),
        L(5, "怎么改？先收集上下文，再动手改文件、跑命令，最后验证结果。", "怎么改？先收集上下文，再动手改文件、跑命令，最后验证结果。",
          "How? It gathers context, then acts by editing files and running commands, then verifies the result."),
        L(6, "没达标，就回到第一步重来，一直循环到能验证为止。", "没达标，就回到第一步重来，一直循环到能验证为止。",
          "If it falls short, it loops back and tries again until the result checks out."),
        L(13, "比如让它修失败的测试：先跑，读报错，找文件，改，再跑一遍。", "比如让它修失败的测试：先跑，读报错，找文件，改，再跑一遍。",
          "Ask it to fix failing tests: it runs them, reads the errors, finds the files, edits, and runs them again."),
        L(7, "整个过程里，你随时能插话、打断、纠偏。", "整个过程里，你随时能插话、打断、纠偏。",
          "At any point, you can add context, interrupt, or steer it."),
        L(14, "改错了？按两下 Esc，文件能回到改之前；远端的改动撤不回。", "改错了？按两下 Esc，文件能回到改之前；远端的改动撤不回。",
          "Made a mistake? Press Esc twice and your files roll back, though changes to remote systems can't be undone."),
        L(8, "撑起这个循环的有四样：循环本身、上下文窗口、工具、权限。", "撑起这个循环的有四样：循环本身、上下文窗口、工具、权限。",
          "Four things hold it up: the loop itself, the context window, tools, and permissions."),
        L(9, "窗口满了会自动压缩，什么时候调用工具由它判断，权限由你来定。", "窗口满了会自动压缩，什么时候调用工具由它判断，权限由你来定。",
          "The window compacts itself when it fills up, Claude decides when to call tools, and you set the permissions."),
        L(10, "终端、编辑器插件、桌面应用、网页版，都能用。", "终端、编辑器插件、桌面应用、网页版，都能用。",
          "It runs in your terminal, as an editor plugin, in the desktop app, and on the web."),
        L(11, "官方课自己也提醒：它可能理解错、写出 bug、把事情做过头。", "官方课自己也提醒：它可能理解错、写出 bug、把事情做过头。",
          "The official course itself warns: it can misread your intent, introduce bugs, and over-engineer things."),
        L(12, "聊天框交答案，代理交结果。结果对不对，还得你来验。", "聊天框交答案，代理交结果。结果对不对，还得你来验。",
          "A chat window delivers answers; an agent delivers results. Whether they're right is still on you to verify."),
    ],
    # 每个场景：win = 素材窗口（自动拆上下框）；也可直接写 top / bottom 选段 {src, a, b, [crop, speed, hold, bg, w]}；src: a = 第 1 课、b = 第 2 课、c = 安装那课（入口镜头）
    scenes=[
        dict(id="S1", name="钩子：三步", lines=["N01"],
             top=[dict(src="b", a=14.4, b=16.6), dict(src="b", a=5.2, b=7.4)],
             bottom=[dict(src="b", a=48.7, b=52.9)]),
        dict(id="S2", name="背书：官方入门课", lines=["N02"],
             top=[dict(src="a", a=5.15, b=7.18), dict(src="a", a=11.6, b=13.8)],
             bottom=[dict(src="a", a=7.45, b=11.3)]),
        dict(id="S3", name="和聊天窗口的差别", lines=["N03", "N04"], win=[("a", 30.2, 55.5)]),
        dict(id="S4", name="三步循环", lines=["N05"], win=[("b", 17.0, 37.2)]),
        dict(id="S5", name="循环 + 随时打断", lines=["N06", "N13", "N07", "N14"], win=[("b", 53.0, 61.2), ("b", 143.6, 154.1)]),
        dict(id="S6", name="四个零件", lines=["N08", "N09"], win=[("b", 64.0, 97.7)]),
        dict(id="S7", name="在哪用", lines=["N10"],
             top=[dict(src="c", a=114.5, b=121.1)],
             bottom=[dict(src="c", a=65.2, b=72.0)]),
        dict(id="S8", name="泼冷水 + 收尾", lines=["N11", "N12"], win=[("a", 141.8, 171.2)]),
    ],
    overlays="""
note(S('N01') + 0.1, E('N01') + 0.3, '找线索 → 动手 → 验结果');
note(S('N05'), E('N05') + 0.2, '收集上下文 → 动手 → 验证', '', {lower: true});
note(S('N08'), E('N09') + 0.2, '循环 · 上下文 · 工具 · 权限');
note(S('N11'), E('N11') + 0.2, '官方提醒：它会犯错');
""",
)


# ════════════════════════════════════════ 第 2 期｜装好 Claude Code，跑第一个提示
EPISODES[2] = dict(
    folder="02_装好并跑第一个提示", slug="装好并跑第一个提示",
    title="Claude官方教程 第2期｜装好 Claude Code，跑第一个提示",
    kicker="<b>Claude官方教程</b> 第2期",
    hook=["装它只要一条命令", "第一个提示先别动手"],
    credit=CRED.format(n=2),
    src={"a": "CC101-03_installing-claude-code__0kILa02vKuI.mp4", "b": "CC101-04_your-first-prompt__gbetp6D7J_Q.mp4"},
    lines=[
        L(1, "装 Claude Code，三大系统都只要一条命令。", "装 Claude Code，三大系统都只要一条命令。",
          "Installing Claude Code takes one command on Windows, Mac and Linux."),
        L(2, "Mac 和 Linux 用 curl，Windows 用 PowerShell。", "Mac 和 Linux 用 curl，Windows 用 PowerShell。",
          "On Mac and Linux it's a curl command; on Windows, PowerShell."),
        L(13, "提示符带 PS 的是 PowerShell，不带的是 CMD，别敲错。", "提示符带 PS 的是 PowerShell，不带的是 CMD，别敲错。",
          "A prompt starting with PS is PowerShell; without it, it's CMD. Don't mix them up."),
        L(3, "Homebrew 和 winget 也能装，不过默认不会自动更新。", "Homebrew 和 Windows 的包管理器也能装，不过默认不会自动更新。",
          "Homebrew and winget work too, but they don't auto-update by default."),
        L(14, "装完开个新终端，运行 claude --version，能出版本号就成功。", "装完开个新终端，运行 claude 杠杠 version，能出版本号就成功。",
          "Open a new terminal and run claude --version. If a version number shows up, you're set."),
        L(4, "装完在项目目录里敲 claude，第一次运行要先登录。", "装完在项目目录里敲 claude，第一次运行要先登录。",
          "Run claude in your project folder. The first launch asks you to sign in."),
        L(5, "登录能用 Pro、Max、Team 或企业账号，也能用 API key。", "登录能用 Pro、Max、Team 或企业账号，也能用 API key。",
          "You can sign in with a Pro, Max, Team or Enterprise account, or use an API key."),
        L(6, "它能访问你启动的那个目录和所有子目录，目录之外的要经你许可。", "它能访问你启动的那个目录和所有子目录，目录之外的要经你许可。",
          "It can access the folder you launch it in and every subfolder; anything outside needs your permission."),
        L(7, "不想用终端也行：编辑器插件、桌面应用、网页版都能用。", "不想用终端也行：编辑器插件、桌面应用、网页版都能用。",
          "Prefer not to use the terminal? There are editor plugins, a desktop app, and a web version."),
        L(8, "不过终端的功能最全，有些功能只有终端里才有。", "不过终端的功能最全，有些功能只有终端里才有。",
          "Still, the terminal has the fullest feature set, and some features exist only there."),
        L(9, "第一个提示别急着动手：按 Shift+Tab，轮换到计划模式。", "第一个提示别急着动手：按 Shift 加 Tab，轮换到计划模式。",
          "For your first prompt, don't let it edit yet. Press Shift+Tab until the status bar shows plan mode."),
        L(10, "计划模式只研究、只提方案，不改你的源码，最后交一份计划。", "计划模式只研究、只提方案，不改你的源码，最后交一份计划。",
          "Plan mode researches and proposes without editing your source, then hands back a plan."),
        L(15, "计划出来后，按 Ctrl+G 能先改，再批准。", "计划出来后，按 Ctrl 加 G 能先改，再批准。",
          "Once the plan is up, press Ctrl+G to edit it before you approve."),
        L(11, "官方示例：整个应用要暗色模式，顶栏加个切换开关，再挑个对比度合适的颜色。", "官方示例：整个应用要暗色模式，顶栏加个切换开关，再挑个对比度合适的颜色。",
          "The official example: dark mode across the whole app, a toggle in the header, and a good contrast color."),
        L(12, "装它一条命令，用好它，从 Shift+Tab 开始。", "装它一条命令，用好它，从 Shift 加 Tab 开始。",
          "Installing it takes one command. Using it well starts with Shift+Tab."),
    ],
    scenes=[
        dict(id="S1", name="一条命令装好", lines=["N01", "N02", "N13"], win=[("a", 4.7, 34.0)]),
        dict(id="S2", name="不自动更新 + 首次登录", lines=["N03", "N14", "N04", "N05"], win=[("a", 34.0, 61.0)]),
        dict(id="S3", name="启动目录", lines=["N06"], at=("a", 137.1)),
        dict(id="S4", name="别的入口", lines=["N07", "N08"],
             top=[dict(src="a", a=65.3, b=69.8), dict(src="a", a=98.9, b=102.9)],
             bottom=[dict(src="a", a=114.5, b=119.0), dict(src="a", a=122.0, b=126.0)]),
        dict(id="S5", name="计划模式", lines=["N09", "N10", "N15"],
             top=[dict(src="b", a=16.7, b=22.1, face=True), dict(src="b", a=36.1, b=38.4, face=True), dict(src="b", a=41.4, b=42.3, face=True), dict(src="b", a=76.9, b=80.6, face=True)],
             bottom=[dict(src="b", a=124.7, b=129.6), dict(src="b", a=42.6, b=47.6)]),
        dict(id="S6", name="官方示例", lines=["N11"],
             top=[dict(src="b", a=102.1, b=104.0, face=True), dict(src="b", a=110.9, b=112.2, face=True), dict(src="b", a=116.2, b=116.9, face=True), dict(src="b", a=119.7, b=122.2, face=True), dict(src="b", a=71.1, b=72.3, face=True)],
             bottom=[dict(src="b", a=88.8, b=94.0), dict(src="b", a=117.2, b=119.4)]),
        dict(id="S7", name="收尾", lines=["N12"],
             top=[dict(src="b", a=134.1, b=138.0, face=True), dict(src="b", a=140.7, b=142.6, face=True)],
             bottom=[dict(src="b", a=131.4, b=133.8), dict(src="b", a=138.2, b=140.6, face=True)]),
    ],
    overlays="""
note(S('N01'), E('N02') + 0.2, 'macOS / Linux：curl　Windows：PowerShell');
note(S('N09'), E('N09') + 0.2, 'Shift+Tab → 计划模式');
""",
)


# ════════════════════════════════════════ 第 3 期｜探索 → 计划 → 编码 → 提交
EPISODES[3] = dict(
    folder="03_探索计划编码提交", slug="探索计划编码提交",
    title="Claude官方教程 第3期｜探索→计划→编码→提交，标准工作流",
    kicker="<b>Claude官方教程</b> 第3期",
    hook=["先别让它写代码", "四步标准工作流"],
    credit=CRED.format(n=3),
    src={"a": "CC101-05_explore-plan-code-commit__xJQuF02NAK8.mp4"},
    lines=[
        L(1, "Claude 动手写代码之前，最该做的，是不让它动手。", "Claude 动手写代码之前，最该做的，是不让它动手。",
          "Before Claude writes a line of code, the best thing you can do is stop it from writing any."),
        L(2, "官方入门课教的标准工作流，就四步：探索、计划、编码、提交。", "官方入门课教的标准工作流，就四步：探索、计划、编码、提交。",
          "The standard workflow in Anthropic's intro course has four steps: explore, plan, code, commit."),
        L(3, "前两步放在计划模式里：它先把相关文件读一遍，研究、出方案，但不改你的源码。", "前两步放在计划模式里：它先把相关文件读一遍，研究、出方案，但不改你的源码。",
          "The first two happen in plan mode: it reads the relevant files, researches and proposes, but doesn't edit your source."),
        L(4, "计划出来先看一遍，不满意就告诉它具体改哪一块。", "计划出来先看一遍，不满意就告诉它具体改哪一块。",
          "Read the plan before anything runs, and tell it exactly which part to change."),
        L(5, "这时候纠偏最划算，因为一行代码还没写。", "这时候纠偏最划算，因为一行代码还没写。",
          "This is the cheapest moment to correct course, because no code exists yet."),
        L(13, "按 Ctrl+G，能直接在编辑器里改计划。", "按 Ctrl 加 G，能直接在编辑器里改计划。",
          "Press Ctrl+G to edit the plan right in your editor."),
        L(6, "编码阶段给它三样东西：成功标准、趁手的工具、能反复跑的测试。", "编码阶段给它三样东西：成功标准、趁手的工具、能反复跑的测试。",
          "In the coding phase, give it three things: a success criterion, the right tools, and tests it can run repeatedly."),
        L(7, "装上 Claude in Chrome，它能自己测界面，需直连官方账号。", "装上 Claude in Chrome，它能自己测界面，需直连官方账号。",
          "Install the Claude in Chrome extension and it can open pages and test your interface itself, on a direct Anthropic plan."),
        L(8, "官方课还提醒：测试要靠得住，别让它削弱测试来蒙混过关。", "官方课还提醒：测试要靠得住，别让它削弱测试来蒙混过关。",
          "The course also warns: the tests have to be trustworthy, and Claude shouldn't weaken them just to pass."),
        L(9, "提交之前，先让子代理审一遍：它没参与写代码，眼光是新的。", "提交之前，先让子代理审一遍：它没参与写代码，眼光是新的。",
          "Before committing, have a subagent review the work: it didn't write the code, so it brings fresh eyes."),
        L(14, "官方课还列了提交前看的三样：没要求的改动、变弱的测试、硬编码的值。", "官方课还列了提交前看的三样：没要求的改动、变弱的测试、硬编码的值。",
          "The course also lists three things to check before committing: changes you didn't ask for, weakened tests, and hard-coded values."),
        L(10, "提交信息想要固定格式？把约定写进 CLAUDE.md，它就照做。", "提交信息想要固定格式？把约定写进 Claude 点 md，它就照做。",
          "Want a fixed commit message format? Put the convention in CLAUDE.md."),
        L(11, "官方也说：一句话说得清的小改动，别计划，直接做。", "官方也说：一句话说得清的小改动，别计划，直接做。",
          "Anthropic also says: if you can describe the diff in one sentence, skip the plan."),
        L(12, "先看后改，先审后交。", "先看后改，先审后交。",
          "Look before you change; review before you ship."),
    ],
    scenes=[
        dict(id="S1", name="钩子", lines=["N01"], at=4.4),
        dict(id="S2", name="四步", lines=["N02"], at=16.8),
        dict(id="S3", name="计划模式", lines=["N03"], at=35.9),
        dict(id="S4", name="审计划", lines=["N04", "N05", "N13"], at=76.6),
        dict(id="S5", name="编码三样东西", lines=["N06"], at=109.9),
        dict(id="S6", name="Claude in Chrome", lines=["N07"], at=117.8),
        dict(id="S7", name="测试要可靠", lines=["N08"], at=126.6),
        dict(id="S8", name="子代理审查 + 提交信息", lines=["N09", "N14", "N10"], at=145.8),
        dict(id="S9", name="小改动别计划 + 收尾", lines=["N11", "N12"], at=168.5),
    ],
    overlays="""
note(S('N02'), E('N02') + 0.2, '探索 → 计划 → 编码 → 提交');
note(S('N08'), E('N08') + 0.2, '测试要先靠得住');
""",
)


# ════════════════════════════════════════ 第 4 期｜上下文管理
EPISODES[4] = dict(
    folder="04_上下文管理", slug="上下文管理",
    title="Claude官方教程 第4期｜上下文管理：/compact、/clear、/context",
    kicker="<b>Claude官方教程</b> 第4期",
    hook=["提示越含糊", "越费上下文"],
    credit=CRED.format(n=4),
    src={"a": "CC101-06_context-management__eW3oTyfeWZ0.mp4"},
    lines=[
        L(1, "目标明确的活，提示写得越含糊，Claude 越费上下文。", "目标明确的活，提示写得越含糊，Claude 越费上下文。",
          "When the goal is clear, the vaguer your prompt, the more context Claude burns."),
        L(2, "Anthropic 官方入门课专门有一课，讲怎么管这块“记忆”。", "Anthropic 官方入门课专门有一课，讲怎么管这块“记忆”。",
          "Anthropic's intro course has a whole lesson on managing this memory."),
        L(3, "上下文窗口，是 Claude 这次会话的工作记忆。", "上下文窗口，是 Claude 这次会话的工作记忆。",
          "The context window is Claude's working memory for the session."),
        L(4, "你的提示、读过的文件、命令的输出，全都占位。", "你的提示、读过的文件、命令的输出，全都占位。",
          "Your prompts, the files it has read, command outputs: all of it takes up space."),
        L(5, "装满了会自动压缩：先清掉旧的工具输出，不够再总结对话。", "装满了会自动压缩：先清掉旧的工具输出，不够再总结对话。",
          "When it fills up, Claude Code compacts automatically: it clears old tool output first, then summarizes the conversation."),
        L(6, "代价是，早期的详细指令可能丢。", "代价是，早期的详细指令可能丢。",
          "The catch: detailed instructions from early on may be lost."),
        L(7, "三个命令：/compact 压成摘要，/clear 清空对话，/context 看占用。", "三个命令管它：斜杠 compact 压成摘要，斜杠 clear 清空对话，斜杠 context 看占用。",
          "Three commands: /compact summarizes and carries on, /clear empties the conversation, /context shows what takes the most space.",
          cut=[["压成摘要，", "carries on,"], ["清空对话，", "conversation,"]]),
        L(8, "同一个功能做到快满，用 /compact。开新功能，用 /clear。", "同一个功能做到快满，用 compact。开新功能，用 clear。",
          "Use /compact when a feature runs you near the limit. Use /clear when you start a new one."),
        L(13, "同一个问题纠正两次还不对，就清空重来。", "同一个问题纠正两次还不对，就清空重来。",
          "Corrected the same issue twice and it's still wrong? Clear and start over."),
        L(14, "小问题想问一句，用 /btw，答案不占上下文。", "小问题想问一句，用斜杠 B T W，答案不占上下文。",
          "For a quick side question, use /btw. The answer never enters the conversation."),
        L(9, "要跨会话记住的事，写进 CLAUDE.md：压缩之后，它会从磁盘重新读一遍。", "要跨会话记住的事，写进 Claude 点 md：压缩之后，它会从磁盘重新读一遍。",
          "For anything to remember across sessions, put it in CLAUDE.md. After a compact, it's re-read from disk.",
          cut=[["要跨会话记住的事，", "across sessions,"], ["压缩之后，", "After a compact,"]]),
        L(10, "还有个反直觉的：目标明确的活，提示写得越具体，越省上下文。", "还有个反直觉的：目标明确的活，提示写得越具体，越省上下文。",
          "One counterintuitive tip: when the goal is clear, the more specific the prompt, the less context it uses."),
        L(11, "含糊的提示看着短，它却得自己到处翻代码、自己推理，反而更费。", "含糊的提示看着短，它却得自己到处翻代码、自己推理，反而更费。",
          "A vague prompt looks short, but Claude has to explore and reason on its own, which costs more."),
        L(12, "上下文是预算，不是仓库。", "上下文是预算，不是仓库。",
          "Context is a budget, not a warehouse."),
    ],
    scenes=[
        dict(id="S1", name="钩子", lines=["N01"], at=15.9),
        dict(id="S2", name="上下文窗口", lines=["N02", "N03", "N04"], at=29.4, more=[("a", 4.4, 12.9)]),
        dict(id="S3", name="自动压缩", lines=["N05", "N06"], at=39.8),
        dict(id="S4", name="三个命令", lines=["N07", "N08", "N13", "N14"], at=58.2),
        dict(id="S5", name="CLAUDE.md", lines=["N09"], at=117.7),
        dict(id="S6", name="越具体越省", lines=["N10", "N11"], at=128.2),
        dict(id="S7", name="收尾", lines=["N12"], at=200.9),
    ],
    overlays="""
note(S('N07'), E('N07') + 0.2, '/compact · /clear · /context');
""",
)


# ════════════════════════════════════════ 第 5 期｜CLAUDE.md
EPISODES[5] = dict(
    folder="05_CLAUDE-md", slug="CLAUDE-md",
    title="Claude官方教程 第5期｜CLAUDE.md：给 Claude 写一份入职手册",
    kicker="<b>Claude官方教程</b> 第5期",
    hook=["每次开机都像", "第一天上班"],
    credit=CRED.format(n=5),
    src={"a": "CC101-08_claude-md-file__O0FGCxkHM-U.mp4"},
    lines=[
        L(1, "Claude Code 每开一个新会话，上下文都是全新的，像第一天上班。", "Claude Code 每开一个新会话，上下文都是全新的，像第一天上班。",
          "Every new Claude Code session starts with a fresh context, like day one on the job."),
        L(2, "官方课说：没有 CLAUDE.md，结构、依赖、功能都得重新摸。", "官方课说：没有 Claude 点 md，结构、依赖、功能都得重新摸。",
          "The course says that without CLAUDE.md, it re-explores your structure, dependencies and finished features."),
        L(3, "解法是项目根目录的一个 Markdown 文件，每次开会话，它都会自动读。", "解法是项目根目录的一个 Markdown 文件，每次开会话，它都会自动读。",
          "The fix is a Markdown file in your project root, read automatically at the start of every session."),
        L(4, "官方的比喻：给代码库写的入职手册。", "官方的比喻：给代码库写的入职手册。",
          "Anthropic's analogy: an onboarding script for your codebase."),
        L(5, "写什么？常用命令、代码风格，这些读代码也猜不到的规矩，每份别超过两百行。", "写什么？常用命令、代码风格，这些读代码也猜不到的规矩，每份别超过两百行。",
          "What goes in? Commands and style rules it can't guess from the code, and keep each file under 200 lines."),
        L(6, "项目级的进版本库，全队共享；用户级的放你的配置文件夹，只给你自己。", "项目级的进版本库，全队共享；用户级的放你的配置文件夹，只给你自己。",
          "The project file goes into version control for the team; the user file lives in your config folder, just for you."),
        L(7, "几份是叠加着一起读，不是谁覆盖谁。", "几份是叠加着一起读，不是谁覆盖谁。",
          "They stack when read; one doesn't override another."),
        L(8, "同一个错纠正第二遍，就写下来，比如“别用 API 路由”。", "同一个错纠正第二遍，就写下来，比如“别用 API 路由”。",
          "Correct the same mistake twice and it's time to write it down, like use server actions instead of API routes."),
        L(9, "想进文件，要明说“加到 CLAUDE.md”；只说“记住”，进的是自动记忆。", "想进文件，要明说“加到 Claude 点 md”；只说“记住”，进的是自动记忆。",
          "To get it into the file, say add this to CLAUDE.md. Just saying remember saves it to Claude's own memory."),
        L(10, "项目文档用 @ 加路径引用，不过引用的内容照样一启动就全载入，不省上下文。", "项目文档用艾特加路径引用，不过引用的内容照样一启动就全载入，不省上下文。",
          "Reference project docs with @ and a path, though they still load in full at launch and don't save context."),
        L(11, "官方课还建议：一开始先别写，看它总在哪被纠偏，再用 /init 生成。", "官方课还建议：一开始先别写，看它总在哪被纠偏，再用斜杠 init 生成。",
          "The course also suggests starting without one, seeing where you keep correcting it, then running /init."),
        L(12, "但它是上下文，不是强制配置。必须照做的硬规矩，交给 hook。", "但它是上下文，不是强制配置。必须照做的硬规矩，交给 hook。",
          "But it's context, not enforced configuration. Rules that must always hold belong in a hook."),
    ],
    scenes=[
        dict(id="S1", name="每次从零开始", lines=["N01", "N02"], at=14.3),
        dict(id="S2", name="一个文件 + 入职手册", lines=["N03", "N04"], at=28.0),
        dict(id="S3", name="里面写什么", lines=["N05"], at=49.0),
        dict(id="S4", name="项目级和用户级", lines=["N06", "N07"], at=95.5),
        dict(id="S5", name="纠正过的存进记忆", lines=["N08", "N09"], at=121.8),
        dict(id="S6", name="@ 引用", lines=["N10"], at=134.8),
        dict(id="S7", name="先别写 + 硬规矩交给 hook", lines=["N11", "N12"], at=149.7),
    ],
    overlays="""
note(S('N03'), E('N03') + 0.2, 'CLAUDE.md：放在项目根目录');
note(S('N09'), E('N09') + 0.2, '想写进文件：加到 CLAUDE.md');
note(S('N11'), E('N11') + 0.2, '/init：让 Claude 生成');
""",
)


# ════════════════════════════════════════ 第 6 期｜Hooks
EPISODES[6] = dict(
    folder="06_Hooks", slug="Hooks",
    title="Claude官方教程 第6期｜Hooks：把“通常照做”变成“绝对照做”",
    kicker="<b>Claude官方教程</b> 第6期",
    hook=["通常照做", "和一定照做"],
    credit=CRED.format(n=6),
    skip=[("a", 178.7, 182.8)],        # 画面里是 Edit|MultiEdit|Write 的配置，当前文档里没有 MultiEdit
    src={"a": "CCA-05_hooks__1m0huCacWPs.mp4"},
    lines=[
        L(1, "提示里写“改完代码要格式化”，Claude 通常会照做。", "提示里写“改完代码要格式化”，Claude 通常会照做。",
          "Tell Claude in a prompt to always format after editing, and it usually will."),
        L(2, "通常，不等于每次。Hooks 的卖点就一句：它想跳也跳不过去。", "通常，不等于每次。Hooks 的卖点就一句：它想跳也跳不过去。",
          "Usually isn't always. The whole pitch of hooks: Claude can't skip it."),
        L(3, "官方列了三十多个钩子事件，常用的就几个。", "官方列了三十多个钩子事件，常用的就几个。",
          "Anthropic lists more than thirty hook events, and you'll reach for just a handful."),
        L(4, "PreToolUse，在工具调用之前触发，能在事情发生前把它拦下来。", "PreToolUse，在工具调用之前触发，能在事情发生前把它拦下来。",
          "PreToolUse fires before a tool call, so it can stop something before it happens."),
        L(5, "PostToolUse，在调用成功之后触发，自动格式化、自动检查放这里。", "PostToolUse，在调用成功之后触发，自动格式化、自动检查放这里。",
          "PostToolUse fires after a successful call, which is where auto-formatting and linting go."),
        L(6, "Stop，在它想收工时触发。一句“你还没做完”，就能让它接着干。", "Stop，在它想收工时触发。一句“你还没做完”，就能让它接着干。",
          "Stop fires when Claude wants to wrap up. It's how you say: no, you're not done yet."),
        L(7, "PreToolUse 能返回三种决定：放行、拒绝、交给你来定。", "PreToolUse 能返回三种决定：放行、拒绝、交给你来定。",
          "A PreToolUse hook can return three decisions: allow, deny, or ask you."),
        L(8, "不返回 JSON 的钩子看退出码：2 是拦截，0 是没意见，别的都不拦。", "不返回 JSON 的钩子看退出码：2 是拦截，0 是没意见，别的都不拦。",
          "Hooks that skip JSON use exit codes: 2 blocks, 0 means no objection, and anything else doesn't block."),
        L(9, "最容易踩的坑：退出码 1 看着像报错，其实不拦，命令照样跑。", "最容易踩的坑：退出码 1 看着像报错，其实不拦，命令照样跑。",
          "The classic trap: exit code 1 feels like an error, but it doesn't block. The command still runs."),
        L(13, "就算跳过权限，钩子的拒绝照样拦得住。", "就算跳过权限，钩子的拒绝照样拦得住。",
          "Even with permissions bypassed, a hook's deny still blocks the call."),
        L(10, "还有一招：不拦，改写。把命令里的密钥换成占位符，再放行。", "还有一招：不拦，改写。把命令里的密钥换成占位符，再放行。",
          "Another move: don't block, rewrite. Swap a secret in the command for a placeholder, then let it run."),
        L(11, "压缩后补上下文，别用 PostCompact，用 SessionStart。", "压缩后补上下文，别用 PostCompact，用 SessionStart。",
          "To restore context after a compact, don't use PostCompact. Use SessionStart with the compact matcher."),
        L(12, "提示词是请求，Hooks 才是规矩。不过路径写错，它会悄悄失效。", "提示词是请求，Hooks 才是规矩。不过路径写错，它会悄悄失效。",
          "A prompt is a request. A hook is a rule. Just don't mistype the path, or it fails silently."),
    ],
    scenes=[
        dict(id="S1", name="通常 vs 一定", lines=["N01", "N02"],
             top=[dict(src="a", a=76.87, b=85.45, speed=1.0, w=8.58)],
             bottom=[dict(src="a", a=4.65, b=11.005, speed=1.0, w=6.355), dict(src="a", a=73.45, b=75.675, speed=1.0, w=2.225)]),
        # S2：上框 = 生命周期图；下框 = 图的各个放大状态，最后几秒（旁白讲 Stop）换成官方课里 Stop 钩子真的拦下收工的终端（原来是退出码幻灯片，早了 9 秒）
        dict(id="S2", name="事件在循环里的位置", lines=["N03", "N04", "N05", "N06"],
             top=[dict(src="a", a=16.65, b=19.577, speed=1.0, w=2.927), dict(src="a", a=42.4, b=52.202, speed=1.0, w=9.802),
                  dict(src="a", a=52.9, b=57.5, speed=0.8, w=5.75), dict(src="a", a=57.45, hold=True, w=0.24)],
             bottom=[dict(src="a", a=20.15, b=20.968, speed=1.0, w=0.818), dict(src="a", a=21.65, b=23.928, speed=1.0, w=2.278),
                     dict(src="a", a=24.9, b=27.387, speed=1.0, w=2.487), dict(src="a", a=28.4, b=30.47, speed=1.0, w=2.07),
                     dict(src="a", a=31.4, b=33.053, speed=1.0, w=1.653), dict(src="a", a=33.9, b=34.509, speed=1.0, w=0.609),
                     dict(src="a", a=35.15, b=36.385, speed=1.0, w=1.235), dict(src="a", a=37.15, b=39.011, speed=1.0, w=1.861),
                     dict(src="a", a=39.9, b=41.553, speed=1.0, w=1.653),
                     dict(src="a", a=122.9, b=126.0, speed=0.8, w=3.88), dict(src="a", a=125.9, hold=True, w=0.18)]),
        dict(id="S3", name="PreToolUse 三种决定", lines=["N07"], win=[("a", 59.65, 73.21)], cards=True),
        # S4：退出码幻灯片（官方课 93 s 起 0 变绿、109 s 起 2 变红、121 s 起 1 变黄）——N08 讲 2 / 0 时给 0 绿 + 2 红的状态，N09 讲 1 时给 1 变黄的状态；原来下框开头是 3 秒空白页
        dict(id="S4", name="退出码", lines=["N08", "N09", "N13"],
             top=[dict(src="a", a=109.4, b=114.4, speed=1.0, w=4.92), dict(src="a", a=120.6, b=122.5, speed=1.0, w=1.9), dict(src="a", a=122.45, hold=True, w=6.36)],
             bottom=[dict(src="a", a=93.0, b=97.9, speed=1.0, w=4.92), dict(src="a", a=101.0, b=106.0, speed=1.0, w=5.02), dict(src="a", a=114.5, b=117.74, speed=1.0, w=3.24)]),
        dict(id="S5", name="不拦，改写", lines=["N10"], at=145.65, until=169.4, cards=True),
        dict(id="S6", name="压缩后恢复", lines=["N11"],
             top=[dict(src="a", a=165.2, b=169.3, speed=1.0, w=4.1)],
             bottom=[dict(src="a", a=136.15, b=138.582, speed=1.0, w=2.432), dict(src="a", a=182.89, b=184.558, speed=1.0, w=1.668)]),
        dict(id="S7", name="收尾", lines=["N12"], win=[("a", 191.05, 199.13), ("a", 169.52, 178.63)], cards=True),
    ],
    overlays="""
note(S('N04'), E('N04') + 0.2, 'PreToolUse：调用前 · 能拦');
note(S('N05'), E('N05') + 0.2, 'PostToolUse：调用后 · 自动格式化');
note(S('N08'), E('N09') + 0.2, '退出码 0 成功　2 拦截　1 不拦');
""",
)


# ════════════════════════════════════════ 第 7 期｜子代理
EPISODES[7] = dict(
    folder="07_子代理", slug="子代理",
    title="Claude官方教程 第7期｜子代理：脏活交出去，主对话只收答案",
    kicker="<b>Claude官方教程</b> 第7期",
    hook=["脏活交给子代理", "主对话只留答案"],
    credit=CRED.format(n=7),
    src={"a": "CC101-09_subagents__jKErNxuxPXg.mp4"},
    lines=[
        L(1, "查一个问题，Claude 翻了一大堆文件，主对话的上下文就这么被占满了。", "查一个问题，Claude 翻了一大堆文件，主对话的上下文就这么被占满了。",
          "Ask one question and Claude reads a pile of files, and your main context fills up."),
        L(2, "子代理就是解法：它在自己的上下文窗口里干活，只把摘要交回来。", "子代理就是解法：它在自己的上下文窗口里干活，只把摘要交回来。",
          "Subagents are the fix: they work in their own context window and hand back only a summary."),
        L(3, "比如问一句：这个应用在哪处理退款？Claude 会派探索型子代理去翻代码。", "比如问一句：这个应用在哪处理退款？Claude 会派探索型子代理去翻代码。",
          "Ask where the app handles refunds, and Claude sends an Explore subagent to dig through the code."),
        L(4, "翻的过程留在子代理那边，主对话里只剩结论。", "翻的过程留在子代理那边，主对话里只剩结论。",
          "The digging stays with the subagent. Your main conversation gets just the conclusion."),
        L(13, "官方示意里，子代理读了六千多 token，只回你四百多。", "官方示意里，子代理读了六千多 token，只回你四百多。",
          "In Anthropic's illustration, the subagent reads over 6,000 tokens and sends back only about 400."),
        L(5, "自带几个子代理：Explore 只读搜代码，Plan 做计划调研。", "自带几个子代理：Explore 只读搜代码，Plan 做计划调研。",
          "Claude Code ships with built-in subagents: Explore searches code read-only, Plan researches in plan mode."),
        L(6, "想自己做一个？最省事的办法，是直接让 Claude 来建。", "想自己做一个？最省事的办法，是直接让 Claude 来建。",
          "Want your own? The easy way is to ask Claude: build me a subagent."),
        L(7, "官方课演示的 /agents 创建向导，新版本已经删了，别照着找。", "官方课演示的斜杠 agents 创建向导，新版本已经删了，别照着找。",
          "The /agents creation wizard shown in the course has been removed in newer versions, so don't go looking for it."),
        L(8, "描述写得好，Claude 才知道什么时候该叫它；用 @ 点名，则一定会派它。", "描述写得好，Claude 才知道什么时候该叫它；用艾特点名，则一定会派它。",
          "A good description tells Claude when to call it, and an @ mention guarantees it runs."),
        L(9, "子代理就是带 YAML 头的 Markdown 文件，必填只有两个：名字和描述。", "子代理就是带亚马尔头的 Markdown 文件，必填只有两个：名字和描述。",
          "A subagent is a Markdown file with YAML frontmatter, and only the name and description are required."),
        L(10, "加一行 memory，它就能跨对话记住东西，越用越熟。", "加一行 memory，它就能跨对话记住东西，越用越熟。",
          "Add one memory line and it can remember things across conversations."),
        L(11, "还能预载技能：写进 skills 字段，整份技能都会塞进它的上下文。", "还能预载技能：写进 skills 字段，整份技能都会塞进它的上下文。",
          "You can also preload skills: list them in the skills field, and the whole skill is injected into its context."),
        L(12, "不过子代理自己也花用量，别当成免费的。脏活外包，只收结论。", "不过子代理自己也花用量，别当成免费的。脏活外包，只收结论。",
          "Subagents spend usage of their own, so they aren't free. Outsource the heavy lifting; take only the conclusion."),
    ],
    scenes=[
        dict(id="S1", name="上下文被占满", lines=["N01", "N02"], at=35.4, until=74.2),
        dict(id="S2", name="退款例子", lines=["N03", "N04", "N13"], at=3.75, until=35.0),
        dict(id="S3", name="内置子代理", lines=["N05"], at=116.5, until=133.0),
        dict(id="S4", name="自己做一个", lines=["N06", "N07", "N08"], at=79.2, until=116.5),
        dict(id="S5", name="Markdown + 记忆 + 技能", lines=["N09", "N10", "N11"], at=133.2, until=157.2),
        dict(id="S6", name="收尾", lines=["N12"], at=157.2, until=168.4, cards=True, endcard=True),
    ],
    overlays="""
note(S('N02'), E('N02') + 0.2, '自己的上下文 · 只交答案');
note(S('N06'), E('N06') + 0.2, '/agents → 创建新子代理');
""",
)


# ════════════════════════════════════════ 第 8 期｜Skills
EPISODES[8] = dict(
    folder="08_Skills", slug="Skills",
    title="Claude官方教程 第8期｜Skills：把重复的流程做成按需取用的手册",
    kicker="<b>Claude官方教程</b> 第8期",
    hook=["同一段指令", "别再每次粘贴"],
    credit=CRED.format(n=8),
    src={"a": "CC101-10_skills__bjdBVZa66oU.mp4"},
    lines=[
        L(1, "每次让 Claude 审 PR，都得把同一大段审查标准重新粘贴？", "每次让 Claude 审 PR，都得把同一大段审查标准重新粘贴？",
          "Pasting the same long review standards every time you ask Claude to review a PR?"),
        L(2, "Skills 治这个：把流程写成文件，Claude 需要时自己取用。", "Skills 治这个：把流程写成文件，Claude 需要时自己取用。",
          "Skills fix that: write the process down once and Claude pulls it in when needed."),
        L(3, "技能是个文件夹，里面放 SKILL.md：名称、描述，加上步骤。", "技能是个文件夹，里面放 skill 点 md：名称、描述，加上步骤。",
          "A skill is a folder with a SKILL.md: a name and description first, then the actual steps."),
        L(4, "放在个人目录，所有项目都能用；放在项目里，整个团队共享。", "放在个人目录，所有项目都能用；放在项目里，整个团队共享。",
          "Keep it in your personal folder to use it everywhere, or in the project to share it with the team."),
        L(5, "关键区别：它不会一开始就全塞进上下文。", "关键区别：它不会一开始就全塞进上下文。",
          "The key difference: it isn't loaded into context all at once."),
        L(6, "Claude 先只读每个技能的名称和描述，对上号了，才把全文读进来。", "Claude 先只读每个技能的名称和描述，对上号了，才把全文读进来。",
          "Claude first sees only each skill's name and description, and loads the full contents once one matches."),
        L(7, "CLAUDE.md 是每次会话都载入的规矩，技能是需要时才翻开的手册。", "Claude 点 md 是每次会话都载入的规矩，技能是需要时才翻开的手册。",
          "CLAUDE.md is the rulebook loaded every session; a skill is a manual opened only when needed.",
          cut=[["都载入的", "every session;"]]),
        L(8, "输入 / 加技能名能直接调用，也能让它自己判断；改完不用重启。", "输入斜杠加技能名能直接调用，也能让它自己判断；改完不用重启，当场生效。",
          "Type a slash and the skill name to call it, or let Claude decide. Edits take effect right away, no restart."),
        L(9, "官方课的经验法则：同一套多步指令打了两遍，就该做成技能。", "官方课的经验法则：同一套多步指令打了两遍，就该做成技能。",
          "The course's rule of thumb: type the same multi-step instruction twice, and it's a skill."),
        L(10, "比如视频里演示的：提交信息、PR 描述、调试、写文档。", "比如视频里演示的：提交信息、PR 描述、调试、写文档。",
          "Like the ones in the video: commit messages, PR descriptions, debugging, documentation."),
        L(13, "有副作用的流程，比如部署，设成只能手动叫它。", "有副作用的流程，比如部署，设成只能手动叫它。",
          "For workflows with side effects, like deploys, make the skill manual-only."),
        L(11, "别高兴太早：技能装多了，描述每一轮都占上下文，用不到的别装。", "别高兴太早：技能装多了，描述每一轮都占上下文，用不到的别装。",
          "Don't celebrate yet: every skill's description sits in context on every turn, so skip the ones you won't use."),
        L(12, "常驻的规矩进 CLAUDE.md，偶尔用的手册做成技能。", "常驻的规矩进 Claude 点 md，偶尔用的手册做成技能。",
          "Always-on rules go in CLAUDE.md. Occasional manuals become skills."),
    ],
    scenes=[
        dict(id="S1", name="每次粘贴同一段", lines=["N01", "N02"], at=3.75, until=30.3),
        dict(id="S2", name="一个文件夹 + SKILL.md", lines=["N03"], at=30.3, until=63.2),
        dict(id="S3", name="放在哪", lines=["N04"], at=63.3, until=100.4),
        dict(id="S4", name="按需加载", lines=["N05", "N06"], at=100.5, until=109.8),
        dict(id="S5", name="技能 vs CLAUDE.md", lines=["N07"], at=109.9, until=129.0),
        dict(id="S6", name="怎么调用 + 何时用", lines=["N08", "N09", "N10", "N13"], at=129.0, until=163.2),
        dict(id="S7", name="收尾", lines=["N11", "N12"], at=163.2, until=169.3),
    ],
    overlays="""
note(S('N03'), E('N03') + 0.2, 'SKILL.md：名称 + 描述 + 步骤');
note(S('N07'), E('N07') + 0.2, 'CLAUDE.md 常驻　技能按需');
""",
)


# ════════════════════════════════════════ 第 9 期｜MCP
EPISODES[9] = dict(
    folder="09_MCP", slug="MCP",
    title="Claude官方教程 第9期｜MCP：把代码库之外的工具接进 Claude Code",
    kicker="<b>Claude官方教程</b> 第9期",
    hook=["代码库之外的信息", "靠 MCP 接进来"],
    credit=CRED.format(n=9),
    src={"a": "CC101-11_mcp__kkBFmwkDzdo.mp4"},
    lines=[
        L(1, "很多上下文，其实不在代码库里：在数据库、协作软件、公开仓库里。", "很多上下文，其实不在代码库里：在数据库、协作软件、公开仓库里。",
          "A lot of your context lives outside your codebase: in databases, productivity apps, public repos."),
        L(2, "MCP，模型上下文协议，就是把外部工具接进 Claude Code 的桥。", "MCP，模型上下文协议，就是把外部工具接进 Claude Code 的桥。",
          "MCP, the Model Context Protocol, is the bridge that connects those tools to Claude Code."),
        L(3, "团队用 Linear 管项目？加个 MCP 服务器，就能直接读工单。", "团队用 Linear 管项目？加个 MCP 服务器，就能直接读工单。",
          "If your team tracks work in Linear, add a Linear MCP server and Claude can read the issues itself."),
        L(4, "要查依赖的最新文档，有 Context7 这类文档服务器。", "要查依赖的最新文档，有 Context7 这类文档服务器。",
          "Need up-to-date docs for a dependency? A docs server like Context7 can provide them."),
        L(5, "用 claude mcp add 添加，常用 HTTP 和 stdio 两种。", "用 claude mcp add 添加，常用 HTTP 和 stdio 两种。",
          "Add a server with claude mcp add. The two common types: HTTP for remote services, stdio for local processes."),
        L(6, "会话里敲 /mcp，能看连接状态，不用的直接关掉，配置不会丢。", "会话里敲斜杠 mcp，能看连接状态，不用的直接关掉，配置不会丢。",
          "Inside a session, /mcp shows what's connected and lets you disable what you don't need, keeping its config."),
        L(7, "范围有三档：本地，只有你、只在这个项目；用户，你的所有项目。", "范围有三档：本地，只有你、只在这个项目；用户，你的所有项目。",
          "There are three scopes: local, just you in this project; user, across all your projects."),
        L(8, "第三档是项目：写进 .mcp.json 提交进版本库，全队拿到同一套服务器。", "第三档是项目：写进 mcp 点 json 提交进版本库，全队拿到同一套服务器。",
          "The third is project: a .mcp.json checked into version control, so everyone gets the same servers."),
        L(9, "要记住代价：每个服务器的工具名和说明，每个会话都要载入，会占一点上下文。", "要记住代价：每个服务器的工具名和说明，每个会话都要载入，会占一点上下文。",
          "Mind the cost: each server's tool names and instructions load every session and take a little context."),
        L(10, "有现成命令行的，比如 gh、aws，更省；技能管怎么用，和 MCP 互补。", "有现成命令行的，比如 gh、aws，更省；技能管怎么用，和 MCP 互补。",
          "If a CLI exists, like gh or aws, it's more context-efficient. Skills teach how to use tools, and complement MCP."),
        L(11, "默认只先放工具名，用到才加载。用第三方中转的，默认可能是关着的。", "默认只先放工具名，用到才加载。用第三方中转的，默认可能是关着的。",
          "By default only tool names load first, and the rest on demand. Behind a third-party gateway, that default may be off."),
        L(12, "多接一个，就多占一点上下文，不用的，关掉。", "多接一个，就多占一点上下文，不用的，关掉。",
          "Every server you add costs a little context. Disable the ones you don't use."),
    ],
    scenes=[
        dict(id="S1", name="外部上下文", lines=["N01", "N02"], at=3.5, until=33.2),
        dict(id="S2", name="Linear + Context7", lines=["N03", "N04"], at=36.25, until=72.8),
        dict(id="S3", name="添加服务器", lines=["N05"], at=74.75, until=95.0),
        dict(id="S4", name="/mcp 管理", lines=["N06"], at=95.0, until=105.2),
        # S5：下框 = Local / User / Project 幻灯片，高亮跟旁白（本地 → 用户 → 项目）；官方课里 107.2 s Local 亮、109.4 s User 亮、114.3 s Project 亮。原来 Project 比旁白晚了 1.3 s
        dict(id="S5", name="三档范围", lines=["N07", "N08"],
             top=[dict(src="a", a=31.61, b=33.12, face=True, speed=1.0, w=1.506), dict(src="a", a=61.47, b=63.84, face=True, speed=1.0, w=2.368),
                  dict(src="a", a=177.0, b=183.4, face=True, speed=0.9, w=7.1)],
             bottom=[dict(src="a", a=107.3, b=109.1, speed=1.0, w=1.8), dict(src="a", a=109.0, hold=True, w=1.5),
                     dict(src="a", a=109.6, b=111.46, speed=1.0, w=1.86), dict(src="a", a=114.5, b=120.32, speed=1.0, w=5.82)]),
        dict(id="S6", name="上下文代价", lines=["N09"], at=127.4, until=144.4),
        dict(id="S7", name="命令行 / 技能 / 按需加载 + 收尾", lines=["N10", "N11", "N12"], at=144.4, until=210.5),
    ],
    overlays="""
note(S('N05'), E('N05') + 0.2, 'claude mcp add');
note(S('N07'), E('N08') + 0.2, '本地 · 用户 · 项目（.mcp.json）');
note(S('N09'), E('N09') + 0.2, '工具名和说明：每个会话都占一点');
""",
)


# ════════════════════════════════════════ 第 10 期｜权限模式与自动模式
EPISODES[10] = dict(
    folder="10_权限模式与自动模式", slug="权限模式与自动模式",
    title="Claude官方教程 第10期｜权限模式：什么时候可以放手，交给自动模式",
    kicker="<b>Claude官方教程</b> 第10期",
    hook=["六种权限模式", "你想放手到哪一步"],
    credit=CRED.format(n=10),
    src={"a": "CCA-04_permission-modes__IS6larFJBK8.mp4"},
    lines=[
        L(1, "Claude Code 有六种权限模式，从事事问你，到完全放手。", "Claude Code 有六种权限模式，从事事问你，到完全放手。",
          "Claude Code has six permission modes, from asking about everything to letting go entirely."),
        L(2, "手动：只读不用问，其余先问你。接受编辑：改文件和常见文件命令，也不问。", "手动：只读不用问，其余先问你。接受编辑：改文件和常见文件命令，也不问。",
          "Manual reads freely and asks about everything else. Accept edits also skips the prompt for file edits and common file commands."),
        L(3, "计划：只研究、只提方案，不改你的源码。", "计划：只研究、只提方案，不改你的源码。",
          "Plan researches and proposes, without editing your source."),
        L(4, "自动：多数直接放行，命令、联网这类，交给另一个分类器模型先审。", "自动：多数直接放行，命令、联网这类，交给另一个分类器模型先审。",
          "Auto lets most things through, and a separate classifier model reviews commands, network calls and the like first."),
        L(5, "不再询问：只放行预先批准的，其余直接拒绝，适合 CI 无人值守。", "不再询问：只放行预先批准的，其余直接拒绝，适合 CI 无人值守。",
          "Don't ask allows only pre-approved tools and denies the rest, which suits CI where no one is there to confirm."),
        L(6, "绕过权限：跳过所有检查，只能放在隔离的容器或虚拟机里。", "绕过权限：跳过所有检查，只能放在隔离的容器或虚拟机里。",
          "Bypass permissions skips every check, and belongs only inside an isolated container or VM."),
        L(7, "日常按 Shift+Tab，在前四种间轮着切，状态栏随时显示当前模式。", "日常按 Shift 加 Tab，在前四种间轮着切，状态栏随时显示当前模式。",
          "Day to day, Shift+Tab cycles the first four modes, and the status bar always shows where you are."),
        L(8, "自动模式拦强制推送、生产部署、把下载的代码直接丢进 shell。", "自动模式拦强制推送、生产部署、把下载的代码直接丢进 shell。",
          "Auto mode blocks force pushes, production deploys, and piping downloaded code straight into a shell."),
        L(14, "想看最新的拦截名单，命令行跑 claude auto-mode defaults。", "想看最新的拦截名单，命令行跑 claude auto-mode defaults。",
          "To see the current block list, run claude auto-mode defaults from the command line."),
        L(13, "连续被拦三次，自动模式就会暂停，回到弹窗询问。", "连续被拦三次，自动模式就会暂停，回到弹窗询问。",
          "After three blocks in a row, auto mode pauses and goes back to asking you."),
        L(9, "新版本里，终端新会话默认就是自动模式，先看状态栏。", "新版本里，终端新会话默认就是自动模式，先看状态栏。",
          "In newer versions, new terminal sessions start in auto mode by default, so check the status bar first."),
        L(10, "分类器管意图，不管对错：认证写坏了，它照样放行。", "分类器管意图，不管对错：认证写坏了，它照样放行。",
          "The classifier checks intent, not correctness: break authentication and it still waves it through."),
        L(11, "所以要搭一个跑测试的 Stop 钩子：一个管动手前，一个管收工后。", "所以要搭一个跑测试的 Stop 钩子：一个管动手前，一个管收工后。",
          "So pair it with a Stop hook that runs your tests: one guards intent before, the other correctness after."),
        L(12, "放手可以，但要有人验收。", "放手可以，但要有人验收。",
          "Letting go is fine, but keep something checking the result."),
    ],
    scenes=[
        dict(id="S1", name="六种模式", lines=["N01"], at=4.65, until=21.7, cards=True),
        # 官方课 CCA-04 的六宫格幻灯片按顺序亮：24.4 s 手动、30 s 接受编辑、37 s 计划（+自动）、45.4 s 不再询问、52 s 绕过权限；66 s 起讲自动模式：68–77 s 分类器小人审命令、78–88 s 拦截清单一项项冒出来；
        # 118–137 s 是 dontAsk 的终端；138 s 四宫格（Shift+Tab）；108–117 s 是“分类器管意图 / 钩子管对错”两句字幕。下面每个场景按旁白手写选段（w = 每段占的秒数）。
        dict(id="S2", name="手动 + 接受编辑 + 计划", lines=["N02", "N03"],
             top=[dict(src="a", a=14.07, b=20.7, speed=0.75, w=8.84), dict(src="a", a=20.6, hold=True, w=0.34)],
             bottom=[dict(src="a", a=24.5, b=29.3, speed=1.0, w=2.45), dict(src="a", a=30.2, b=36.6, speed=1.0, w=3.4),
                     dict(src="a", a=37.2, b=39.6, speed=1.0, w=2.4), dict(src="a", a=39.4, hold=True, w=0.93)]),
        dict(id="S3", name="自动", lines=["N04"],
             top=[dict(src="a", a=38.9, hold=True, w=1.0)],
             bottom=[dict(src="a", a=68.4, b=74.0, speed=1.0, w=5.6)]),
        dict(id="S4", name="不再询问 + 绕过权限", lines=["N05", "N06"],
             top=[dict(src="a", a=120.0, b=125.2, speed=1.0, w=5.34), dict(src="a", a=58.0, b=62.8, speed=1.0, w=4.76)],
             bottom=[dict(src="a", a=45.7, b=51.0, speed=1.0, w=5.3), dict(src="a", a=52.7, b=57.5, speed=1.0, w=4.8)]),
        dict(id="S5", name="Shift+Tab 轮着切", lines=["N07"],
             top=[dict(src="a", a=139.0, hold=True, w=1.9), dict(src="a", a=141.0, b=144.6, speed=1.0, w=3.6)],
             bottom=[dict(src="a", a=145.15, b=150.66, speed=1.0, w=5.51)]),
        dict(id="S6", name="拦什么、新版本默认自动", lines=["N08", "N14", "N13", "N09"],
             top=[dict(src="a", a=78.2, b=87.6, speed=1.0, w=9.4), dict(src="a", a=87.5, hold=True, w=2.7),
                  dict(src="a", a=151.57, b=154.6, speed=1.0, w=3.03), dict(src="a", a=154.5, hold=True, w=1.31)],
             bottom=[dict(src="a", a=88.65, b=105.09, speed=1.0, w=16.44)]),
        dict(id="S7", name="分类器不管对错 + 收尾", lines=["N10", "N11", "N12"],
             top=[dict(src="a", a=109.6, b=116.8, speed=0.75, w=8.4), dict(src="a", a=116.7, hold=True, w=3.3)],
             bottom=[dict(src="a", a=74.0, b=77.8, speed=1.0, w=3.8), dict(src="a", a=105.2, b=108.1, speed=1.0, w=2.9),
                     dict(src="a", a=130.82, b=133.7, speed=1.0, w=2.88), dict(src="a", a=133.6, hold=True, w=2.12)]),
    ],
    overlays="""
note(S('N04'), E('N04') + 0.2, '自动：分类器逐步审核');
note(S('N07'), E('N07') + 0.2, 'Shift+Tab：手动 → 接受编辑 → 计划 → 自动');
note(S('N11'), E('N11') + 0.2, '分类器管意图 · 测试管对错');
""",
)


def selfcheck():
    bad = 0
    for n, d in EPISODES.items():
        han = sum(sum(1 for ch in l["say"] if "\u4e00" <= ch <= "\u9fff") for l in d["lines"])
        est = han * 0.225 + 0.18 * (len(d["lines"]) - 1)
        print(f"第 {n} 期 {d['folder']}：{len(d['lines'])} 句，{han} 个汉字，估时约 {est:.0f} s")
        for l in d["lines"]:
            t = l["zh"] + l["say"]
            if re.search(r"[我他她]", t) or "不是" in t and "而是" in t:
                print("  ✗ 禁用词：", l["id"], l["zh"])
                bad += 1
            if not l["en"]:
                print("  ✗ 没有英文：", l["id"])
                bad += 1
            if len(l["zh"]) > 34:
                print("  ✗ 中文过长（>34）：", l["id"], len(l["zh"]))
                bad += 1
        ids = [i for s in d["scenes"] for i in s["lines"]]
        if ids != [l["id"] for l in d["lines"]]:
            print("  ✗ 场景里的句子和台本对不上")
            bad += 1
    print("问题数：", bad)


if __name__ == "__main__":
    selfcheck()
