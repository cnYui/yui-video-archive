# -*- coding: utf-8 -*-
"""口播字幕条（按成片顺序）→ cues.json。每条：段号、录像编号、原录像里的起止秒、条内要剪掉的口癖、中文、英文。

每期重写下面的 c(...)：先跑 asr.py，再用 `python show_asr.py <编号> -w` 看逐词时间，一句一句核对后手写。
- 中文按实际说的话整理（去掉"就是""那个""这个这个"等口癖、说错重来的半句），不照搬台本；
- 英文逐句翻译，简短口语；名字写"悠一"，英文 Yui；
- s / e 是原录像里的秒数，说话前后别切到字（build_edit.py 会自动前后各多留 0.06 / 0.10 s）；
- skip=[(起, 止), ...]：条内要剪掉的口癖或重来的半句；
- cut=True：和上一条强制分开（上一条尾巴上有不要的字时用）；
- hold=(秒, 录像, 起点)：这条念完后停几秒不出人声（例如作品展示让片段原声出来），出镜画面用那段录像里没说话的镜头。
- 中文里的全角括号"（…）"只放没说出口的注释，如"那给猴子一部打字机（这是无限猴子定理）"，英文对应 "(the infinite monkey theorem)"；
  一般 12 字以内、约每分钟一条，算在 28 字 / 90 字符里；对齐说话时间时括号里的字会被跳过；
- 写之前先列本期术语表（写法以用户用过的为准），放进 asr.py 的 PROMPT；去口癖、误识别、双语翻译、终检的完整规范见技能的 references/subtitles.md；
完整的例子见 Way to AGI 第 02 期：`D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\制作\02_出镜\make_cues.py`（131 条）。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

C = []


def c(pid, clip, s, e, zh, en, skip=(), **kw):
    """kw：cut=True 强制和上一条分开；hold=(秒, 录像, 起点) 这条念完后停几秒（不出人声），出镜画面用那段录像里没说话的镜头。"""
    C.append({"pid": pid, "clip": clip, "s": s, "e": e, "zh": zh, "en": en, "skip": [list(x) for x in skip], **kw})


# ==================================================
# 0176 ── P01–P05
# 48.64s 之后是悬句"就比如说像过年的时候出来的Copi"，切掉
# ==================================================
c("P01", "0176",  0.40,  4.80,
  "Hello，大家好，我是悠一。求求大家别再用 VS Code 写代码了！",
  "Hello everyone, I'm Yui. Please — stop writing code in VS Code!")

c("P02", "0176",  5.08, 14.46,
  "这个视频我想做一个系列，告诉正在搞科研的朋友和写代码的朋友，如何在 AI 时代更好地与 Agent 协作。",
  "I want to make a series for researchers and developers — on how to work with AI agents in this new era.")

c("P03", "0176", 15.78, 23.62,
  "这期我想谈一谈：为什么不用 VS Code，不用之后应该用什么样的新形态，以及怎么用。想直接看怎么用的，可以跳到第二章。",
  "This episode: why I stopped using VS Code, what the new paradigm looks like, and how to use it. Jump to chapter two if you just want the how-to.")

c("P04", "0176", 24.60, 37.28,
  "大家应该或多或少都听过 Copilot、Cursor、Trae、Claude Code、Codex、WorkBuddy 这些名字，还有 IDE 和 CLI，以及 SSH 远程连接服务器。",
  "You've probably heard of Copilot, Cursor, Trae, Claude Code, Codex, WorkBuddy — and terms like IDE, CLI, and SSH remote servers.")

c("P05", "0176", 38.94, 48.60,
  "我先下一个定论：现在写代码的主工作台，已经从 VS Code 这种传统的代码编辑器，变成了 Agent 智能体的页面。",
  "My conclusion first: the main coding workbench has shifted from traditional editors like VS Code to the AI agent interface.")

# ==================================================
# 0177 ── P06 IDE 定义
# 0177 开头 0–14s 是 P05 重录，直接从 15s 开始取 P06
# 29.80s 之后是悬句"但是现在"，切掉
# ==================================================
c("P06", "0177", 15.00, 22.20,
  "IDE，全称 Integrated Development Environment，集成开发环境：写代码、管文件、调试，都在一个图形界面里完成。",
  "IDE stands for Integrated Development Environment — one graphical window for writing code, managing files, and debugging.")

c("P06", "0177", 22.32, 29.80,
  "VS Code、Cursor、Trae 都是这种带图形界面的开发工具。",
  "VS Code, Cursor, and Trae are all IDEs — graphical development tools.")

# ==================================================
# 0178 ── P07 CLI、P09 两种工具、P10 演变 intro
# 以及历史段 P11–P25（共 162.5s）
# ==================================================
c("P07", "0178",  0.52,  9.50,
  "CLI，全称 Command-Line Interface，命令行界面：没有按钮，在终端里敲一行命令，它回你一段文字。git、ssh 都是命令行工具。",
  "CLI stands for Command-Line Interface — no buttons, just type a command and get text back. git and ssh are classic examples.")

c("P09", "0178",  9.50, 18.00,
  "这两年出现的 AI 编程工具，基本上都是这两种：一种住在 IDE 里，一种住在 CLI 里。",
  "The AI coding tools of the past few years basically fall into two categories: ones that live inside an IDE, and ones that live in the CLI.")

c("P10", "0178", 18.00, 23.56,
  "我们先把这个软件的演变捋一遍。",
  "Let me walk you through how these tools evolved.")

# ── 0178 Copilot 历史（P11）──────────────────────────────────
c("P11", "0178", 24.44, 37.48,
  "一开始是 VS Code 先做了 Copilot，2021 年 6 月开始预览，第二年正式上线，它只是用来做代码补全的。",
  "VS Code launched Copilot first — preview in June 2021, fully released the next year — just for code completion.")

# ── 0178 ChatGPT 时代（P12–P15）─────────────────────────────
c("P12", "0178", 37.48, 51.06,
  "到 2022 年 ChatGPT 出来了，大家就从传统的 CV 工程师，从 CSDN 或者 Stack Overflow 里面复制代码然后跑，变成了去 ChatGPT 的聊天框里面粘贴。",
  "Then in 2022 ChatGPT arrived, and developers went from copying code off CSDN and Stack Overflow straight to pasting into ChatGPT.")

c("P13", "0178", 51.50, 68.20,
  "看 ChatGPT 给的代码，再把代码复制粘贴到 VS Code 里面，报错了，再把报错粘贴回 ChatGPT，然后再去这样做一个循环。",
  "You'd read what ChatGPT gave you, paste it into VS Code, hit an error, paste the error back into ChatGPT — one big loop.")

c("P15", "0178", 69.28, 78.72,
  "这个时候人是主角，人来主导，AI 只是一个聊天框。",
  "At that point the human was still in charge. AI was just a chat box.")

# ── 0178 2024 年底转变（P18–P21）────────────────────────────
c("P18", "0178", 78.72, 93.08,
  "但随着 AI 的发展，到 2024 年年底开始就不一样了，因为模型能力慢慢提升，越来越聪明，能够调用工具、做更复杂的事情。当时就有一个 AI 产品叫 Windsurf 发布了。",
  "Then around late 2024 things shifted. Models got smarter, started calling tools and handling complex tasks. That's when Windsurf launched.")

c("P19", "0178", 93.08, 109.18,
  "Cursor 也上线了一个 Agent 模式——它能让 AI 去创建文件、修改文件、运行文件，再拿到报错之后，再去修改它原先的那个代码。",
  "Cursor added an Agent mode: AI could now create, edit, and run files, then read the error and fix the original code itself.")

# ── 0178 Trae（P22）─────────────────────────────────────────
c("P22", "0178", 110.70, 121.70,
  "在 2025 年 1 月的时候，字节跳动发布了 Trae，当时国际版是免费的，而且是内测的，我很荣幸申请了一个内测名额，然后就使用了将近半年的时间。",
  "In January 2025, ByteDance released Trae — the international version was free and invite-only. I got an invite and used it for nearly six months.")

# ── 0178 SOLO / PRD（P24–P25）───────────────────────────────
c("P24", "0178", 124.28, 138.58,
  "当时 Trae 有一个 SOLO 模式，它可以让用户先写 PRD，然后 AI 根据这个 PRD，在一轮之内不需要用户介入，AI 能够一次把这个 PRD 里的项目完成。",
  "Trae had a SOLO mode: write a PRD, hand it to AI, and it would finish the whole project in one shot — no check-ins needed.")

c("P25", "0178", 138.58, 159.28,
  "但是就有个问题：AI 一次做的太多了，容易刹不住车，如果方向偏了，就会越做越偏。因为 AI 本身就是一个概率输出的模型，它做出来的内容和 PRD 对不上，那就很尴尬了，所以在后来……",
  "The problem: when AI does too much at once, it's hard to stop. If the direction drifts, it drifts further. AI is a probabilistic model — what it builds may not match your PRD, and that gets awkward.")

# ==================================================
# 0179 ── P26 上下文腐烂、P27–P29 CLI 路线、P30–P32 CLI 优缺点
# 尾巴 87.48–92.42 是"所以……他"悬句，skip 掉
# ==================================================
c("P26", "0179",  0.52, 24.10,
  "任务一长就会乱。当时 Claude 已经有 20 万 Token 的上下文了，现在已经是 100 万。但塞的越多越容易乱，2025 年 7 月有研究专门测试过，18 个模型都是输入越长、表现越不好，这个后来被称为上下文腐烂——context rot，或者叫上下文飘移。",
  "Longer tasks meant more confusion. Claude already had 200k token context, now it's 1M. But more input means more drift — a July 2025 study tested 18 models and confirmed: longer input, worse performance. This became known as context rot, or context drift.",
  cut=True)

c("P27", "0179", 24.60, 38.08,
  "再往后，就是在终端里的 CLI 智能体。Anthropic 在 2025 年 2 月发布了 Claude Code，5 月份正式上线，当时只是一个 CLI，用户需要在终端里敲命令、发消息。",
  "Then came CLI agents — ones that live in the terminal. Anthropic released Claude Code in February 2025, launched publicly in May. At the time it was CLI-only: you typed commands and sent messages in a terminal.")

c("P29", "0179", 38.08, 50.02,
  "OpenAI 当时 4 月份也发布了 Codex CLI，后来 Google 出了 Gemini CLI，Cursor 也出了 CLI，2025 年基本上每家都做了自己的智能体终端。",
  "OpenAI released Codex CLI in April, then Google shipped Gemini CLI, Cursor added a CLI too. By 2025 basically every major player had their own agentic terminal.")

c("P30", "0179", 53.38, 69.94,
  "CLI 刚出来的时候很受程序员的喜爱，因为 CLI 看起来非常极客，而且敲命令比用 GUI 页面点来点去更快，用 git、SSH、各种 PowerShell 脚本也都很兼容，非常方便。",
  "CLIs were popular with developers at first — they looked cool, typing commands felt faster than clicking around a GUI, and they integrated naturally with git, SSH, and PowerShell scripts.")

c("P32", "0179", 70.36, 86.70,
  "但是它也有一个学习门槛：每家厂商做的命令其实都不一样。我当时用了 Codex CLI 用得很熟了，后来切到 Claude Code 的 CLI，发现命令不一样，又得重新学，用起来就经常很卡。",
  "But there was a learning curve: every vendor's commands were different. I'd gotten fluent in Codex CLI, then switched to Claude Code's CLI and found the commands were totally different. Back to square one.",
  skip=[(87.48, 92.42)])

# ==================================================
# 0181 ── P33–P49（210.67s）
# 尾巴 207.22–210.67 悬句"所以它的页面越来越"，skip 掉
# 注意：录制里 P43（Meta）先于 P42（GPT5.4），按录制顺序排
# ==================================================
c("P33", "0181",  0.00, 27.90,
  "有一句话我很认同：在 AI 时代，学得越快的会发现什么都要学，但学得慢的，很多东西都不用学了。因为 AI 的门槛一直在降低。CLI 就是一个例子，后面就会知道它的门槛是怎么被一步一步抹平的。再到后来，就出现了叫 agent loop 这样一个东西。Agent loop 就是：用户写需求，AI 写代码，AI 跑测试，AI 再改，AI 再写测试……",
  "I really agree with this: in the AI era, fast learners will find there's always more to learn, but slow learners will find they don't need to learn much at all — because AI keeps lowering the bar. CLI is a perfect example. Then came something called the agent loop: user writes requirements, AI writes code, AI runs tests, AI fixes it, AI runs tests again…",
  cut=True)

c("P34", "0181", 28.36, 45.12,
  "前端、后端、数据库三块一起测试、一起联调，人的重要性就被大大降低了。人只需要写需求文档，AI 就可以跑测试、跑代码，没跑过就改，改完再跑 TDD 测试。",
  "Frontend, backend, database — all tested and integrated together. The human's role shrank dramatically. You just write the requirements doc; AI runs and fixes code in a TDD loop until it passes.")

c("P36", "0181", 45.12, 61.06,
  "Anthropic 2025 年 4 月给 Claude Code 写的官方最佳实践，推荐的就是这样一个流程：一个大的 agent loop 里面包含很多小的 loop，小的 loop 都在调工具、跑命令，人就不用中途盯着，最后只要看一下结果就可以了。",
  "Anthropic's official Claude Code best practices from April 2025 recommend exactly this: one big agent loop containing many small loops, each calling tools and running commands. You don't need to watch. Just check the result at the end.")

c("P38", "0181", 64.78, 76.92,
  "但是它也有一个问题：AI 当时的浏览器控制能力不够强。很多需要前端页面点击、输入的东西，它没有办法通过 TDD 来跑测试，因为 TDD 一般都是测试数据库和后端的内容。",
  "But there was a problem: AI's browser control was still weak. Anything requiring front-end clicks and inputs couldn't be covered by TDD, which mostly tests backend and database logic.")

c("P39", "0181", 78.36, 91.14,
  "前端的话需要人去通过鼠标来点，比如一些复杂的管理系统，数据要从浏览器里点进去、输入，后端再查数据库有没有写对，也有很多边界条件，这个时候人去测试的话就会很麻烦。",
  "For the frontend you'd need a human clicking around. Complex admin systems, for example — you'd click in data through the browser, then check if the backend wrote it correctly. With so many edge cases, manual testing got exhausting.")

c("P40", "0181", 91.56, 100.48,
  "后来 AI 的浏览器自动化能力越来越强了。2024 年 10 月份，Anthropic 推出了 Computer Use，模型能看屏幕、动鼠标、打字。",
  "Then AI's browser automation got much stronger. In October 2024, Anthropic launched Computer Use — the model could see the screen, move the mouse, and type.")

c("P43", "0181", 100.86, 118.68,
  "当然这往后有一个非常离谱的事：Meta 从今年 4 月份开始，在他们员工的工作电脑上记录鼠标、键盘和截图，6 月份又因为数据在公司内部泄露了，然后就暂停了。",
  "Then something truly wild happened: starting this April, Meta began recording mouse movements, keystrokes, and screenshots on their employees' work computers. In June the data leaked internally, and they paused the whole thing.")

c("P42", "0181", 119.32, 132.30,
  "在 2025 年 3 月的时候，GPT-5.4，一直到现在的 GPT-6、GPT-6.1，它都高于了人类自动化点击的极限，虽然可能慢一点，但是很准确。",
  "By March 2025, GPT-5.4 — and now GPT-6 and GPT-6.1 — all surpass the human ceiling for automated clicking. They might be a bit slower, but they're very accurate.")

# ── 0181 界面转变（P44 / P46 / P53 / P54）────────────────────
c("P44", "0181", 135.16, 147.94,
  "现在来看，已经是一个围绕着智能体为中心的桌面工作台了。人在这个代码编辑循环里的重要程度就被大大降低了。",
  "Now we have agent-centered desktop workspaces. The human's importance in the code-editing loop has shrunk dramatically.")

c("P46", "0181", 148.64, 161.88,
  "而且大家可以发现，在 2025 年底一直到现在，各家都在改界面：不管是 Trae 到现在的 Trae Work，或者 WorkBuddy，它从刚开始内测的那个代码编辑页面，已经变成了现在的 Agent 页面。",
  "And you can see it everywhere: since late 2025, every major tool has been redesigning. Trae became Trae Work, WorkBuddy evolved from a code editor into an agent workspace.")

# ── 0181 METR、C 编译器（P47 / P48）─────────────────────────
c("P47", "0181", 164.46, 176.14,
  "有一个机构叫 METR，专门测试 AI，他们的结论是：AI 能独立完成的任务长度，大约每七个月翻一倍，2023 年以后更快，大概每四个月翻一倍。",
  "There's a research org called METR that benchmarks AI autonomy. Their finding: the length of tasks AI can handle independently doubles roughly every seven months — and even faster since 2023, about every four months.")

c("P48", "0181", 176.88, 184.46,
  "写代码本身，模型已经很强了。今年二月份，Anthropic 让 16 个 Claude 并行干活，写出了一个能编译 Linux 内核的 C 编译器，大约十万行代码。",
  "On raw coding ability, the models are already remarkable. In February, Anthropic ran 16 Claude instances in parallel and produced a C compiler that can build the Linux kernel — roughly 100,000 lines of code.")

# ── 0181 vibe coding（P49）──────────────────────────────────
c("P49", "0181", 186.30, 208.56,
  "现在其实很多人写代码，他已经不看代码了，甚至直接用语音输入去口喷。去年也有一个词特别火，叫 vibe coding，就是用语音输入，所有的改动全部接受，代码也不看……",
  "A lot of people writing code now don't even read it. They just dictate. Last year a term went viral: vibe coding — voice input, accept all changes, never look at the code.",
  skip=[(207.22, 210.67)])

# ==================================================
# 0182 ── P50–P62（100.93s）
# ==================================================
c("P50", "0182",  0.00, 24.30,
  "所以，代码编辑的页面，随着需求就进行了变化。Cursor 2.0 的时候就已经把页面换成了以智能体为中心、能同时跑好几个智能体的 Agent 模式。11 月份，Google 发布了 Antigravity，专门有一个试图来同时管理多个智能体。Claude Code 后来有了 Desktop 桌面版，2026 年 Codex 也推出了桌面版 App。",
  "So the code-editor interface evolved with the demand. Cursor 2.0 relaunched as an agent-centered workspace that can run multiple agents at once. Google launched Antigravity in November, designed specifically for managing parallel agents. Claude Code got a desktop app, and Codex launched their own desktop app in 2026.",
  cut=True)

c("P53", "0182", 26.14, 40.10,
  "今年 6 月份，GitHub 也出了 Copilot 桌面端 App；Windsurf 改名成了 Devin Desktop，打开就是默认的智能体控制台；字节 Trae 甚至把 Trae 拆成了 Trae Code 和 Trae Work。",
  "This June, GitHub released a Copilot desktop app. Windsurf rebranded as Devin Desktop, defaulting to an agent console at launch. ByteDance split Trae into Trae Code and Trae Work.")

c("P55", "0182", 43.32, 65.22,
  "在今年过年的时候，OpenClaw 出现之后，大家会发现，模型其实不仅能写代码，它也能调用很多工具——比如说浏览网页、做一些邮件的处理。所以说今年就是 agent 的元年，因为今年的 agent 这么火，离不开 OpenClaw 的出现。",
  "When OpenClaw came out around the new year, it became clear that models aren't just for code — they can browse the web, handle emails, all sorts of tools. That's why this year is called the year of agents: OpenClaw's launch was a big part of why.")

c("P56", "0182", 66.72, 78.00,
  "在 OpenClaw 出现之后，Anthropic 同步在 2026 年 1 月推出了 Cowork，把 Claude 的这个能力，分给了不写代码的人用，同时开源项目 OpenClaw 爆火。",
  "Right around the same time, Anthropic launched Cowork in January 2026 — bringing Claude's capabilities to people who don't write code. And the open-source OpenClaw project blew up.")

c("P57", "0182", 79.90, 91.04,
  "我当时也本地部署了，它可以接入到 Telegram 里面，接入到 WhatsApp 里面，当时「养瞎」这个词也特别火，几乎没有人不知道。",
  "I ran it locally myself — you could hook it into Telegram, into WhatsApp. The phrase 'raising an AI pet' was everywhere at the time.")

c("P62", "0182", 92.90, 98.48,
  "所以这个方向就是：AI 从帮写代码，变成了干活。",
  "So the direction is clear: AI went from helping you write code to actually doing the work.")

# ==================================================
# 0183 ── P65–P78 Claude Code 演示（205.95s）
# ==================================================
c("P65", "0183",  0.44, 30.34,
  "下面给大家演示一下 Claude Code 桌面版，如何去使用这样一个 Agent 的操作台。我用 Claude Code 演示是因为现在大部分厂商做的都大差不差，功能大家都会有，所以稍微过一下有哪些功能就可以了。来看一下，为什么相比于 VS Code，我更倾向于推荐使用 Agent 工作台来进行代码的开发。",
  "Let me demo the Claude Code desktop app — how to use an agent workspace. I'm using Claude Code because most tools are roughly similar now; you just need to know what's available. Here's why I prefer an agent workspace over VS Code for coding.",
  cut=True)

c("P66", "0183", 32.20, 38.00,
  "首先，Claude Code 可以同时开好几个会话，每个会话可以有自己的 Git worktree，互不干扰。",
  "First, Claude Code can run multiple sessions at once, each with its own Git worktree — completely isolated from each other.")

c("P67", "0183", 39.42, 48.98,
  "第二，右边可以看 Diff，点某一行就能写评论，写完 Claude 会按评论改，也能 add 一些你想问的问题，然后发给 Claude。",
  "Second, you get a diff panel on the right. Click any line to leave a comment, Claude will revise based on it, and you can also attach questions and send them directly.")

c("P68", "0183", 50.20, 60.16,
  "在内置终端和浏览器方面，Claude Code 也能自己起服务、打开页面、自动化地操作一遍；生成的 PDF、HTML 也可以在右边的面板打开。",
  "The built-in terminal and browser let Claude start a server, open a page, and automate interactions itself. Generated PDFs and HTML also open right in the side panel.")

c("P69", "0183", 61.68, 84.90,
  "第四点，我更倾向于推荐的是：用好这个 HTML 可视化。我一般会在 AI 改了一大部分代码之后，去让它生成一个 HTML 可视化，来看一下它到底改了什么。因为相比于文字，我更倾向于看图，图片让我一眼就能捕捉到修改的内容。",
  "Fourth — make full use of HTML visualization. After AI makes a big round of changes, I ask it to generate an HTML summary of what changed. Compared to reading text diffs, a diagram lets me grasp the changes at a glance.")

c("P71", "0183", 94.04, 117.20,
  "然后可以看一下权限：manual 是每一步都问你；accept edits 是改文件不问，运行命令时才问；plan 是只出方案、不动代码；auto 是自动，但后台会有另一个模型替你审批；bypass 是全放开，我一般会开这个。",
  "Then there are permission levels: manual asks at every step; accept edits skips file changes but asks before running commands; plan proposes without touching code; auto runs independently but a second model reviews in the background; bypass is fully open — that's what I usually use.")

c("P72", "0183", 118.88, 129.42,
  "Claude Code 也可以通过 SSH 连接远程服务器。我比较喜欢用这个功能，因为它可以在实验室的服务器上直接干活。",
  "Claude Code also connects to remote servers over SSH. I use this a lot — it lets me work directly on the lab server without being there.")

c("P73", "0183", 132.38, 134.86,
  "而且我不用在实验室。",
  "And I don't need to physically be in the lab.")

c("P74", "0183", 138.84, 159.58,
  "Routines 就是定时任务，分两种：本地任务能读本地文件，但电脑要开着；云端任务关机也能跑，所有文件都在云端。现在越来越多的厂商倾向于把内容全部上云，AI 也在云端，这样本地无论是电脑还是手机，都可以让云端的 AI 去做事情。",
  "Routines are scheduled tasks, two kinds: local tasks can read your files but the computer needs to be on; cloud tasks run even when it's off, everything lives in the cloud. More and more vendors are pushing everything to the cloud — AI included — so your phone or laptop can both trigger cloud AI to do work.")

c("P75", "0183", 160.34, 176.24,
  "Computer Use 也是一个非常厉害的功能，就是它能操作我电脑上的软件。比如 Codex 里面的 GPT-6 Astra，它就可以通过 MCP 来调用 Blender 去建模。",
  "Computer Use is another powerful feature — it can control software on your computer. For example, GPT-6 Astra inside Codex can call Blender via MCP to do 3D modeling.")

c("P77", "0183", 177.28, 197.52,
  "还有就是浏览器插件也非常好用。我一般会用来在网页里看论文的时候，把一些不懂的东西直接 add，然后发给浏览器插件，让它回答。它也可以帮我去做一些前端页面的点击操作，因为它在我的浏览器里面，直接用了我的 cookie。",
  "The browser extension is also really handy. When I'm reading a paper online, I highlight something I don't understand, send it to the extension, and get an answer. It can also handle front-end clicks on my behalf — since it's running in my browser, it already has my cookies.")

c("P78", "0183", 201.10, 202.98,
  "这就是这期。",
  "That's the demo.")

# ==================================================
# 0185 ── P79 总结 + P80（45.61s）
# ==================================================
c("P79", "0185",  0.68, 40.92,
  "我们来总结一下，为什么我更倾向于使用 Agent 桌面端去做代码编辑。因为 Agent 桌面端包含了 VS Code 里面所有的功能，而且门槛更低，不像新手打开 VS Code 看到一堆设置就劝退了。而且 Agent 桌面端不仅能写代码，也能用来办公、整理文档、给图片分类，都非常方便。所以我更倾向于去使用这样一个软件。",
  "To wrap up: why do I prefer an agent desktop over VS Code for coding? Because agent desktops include everything VS Code offers, but with a lower barrier to entry — beginners won't get scared off by all the settings. And it's not just code: you can use it for office work, organizing documents, sorting images. That's why I recommend it.",
  cut=True)

# ==================================================
# 0187 ── P81 结尾（12.35s）
# ==================================================
c("P81", "0187",  0.60, 10.80,
  "也希望大家可以去多多尝试一下这些新的 Agent 桌面端的软件。大家如果有哪些想分享的内容，可以分享在评论区。好，这期视频我们就到这里，拜拜。",
  "Hope you'll give some of these new agent desktop tools a try. If you have thoughts to share, drop them in the comments. That's it for this episode — bye!",
  cut=True)

# ==================================================
# 输出 cues.json
# ==================================================
if __name__ == "__main__":
    import json
    out = HERE / "cues.json"
    out.write_text(json.dumps(C, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {len(C)} cues → {out}")
