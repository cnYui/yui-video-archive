# -*- coding: utf-8 -*-
"""整片时间轴（v1，无字幕、出镜占位）：按口播稿分段估时，排出每个画面的起止时间。

输出：timeline.json、timeline.js（页面用）、分段时间表.md（录制时对照）。
稿子：工作树 docs/ai/context/20260929-193326-ep1-script-v1-timeline-evidence_CN.md 第三节（用户 2026-09-29 晚审过、第三次修改后的版本）。
还没有配音：时长按每秒约 3.9 个字估，每段后面多留一点；用户录完再按实际录音重排（用户：“你先做，然后我配音和视频，之后你再微调”）。
做法照第 02 期的 00_整片（Way to AGI/02_如何使用Claude来低成本的生成视频/制作/00_整片/）。
录屏先在 ../01_录屏剪辑/ 去掉停顿、抹掉右下角黑框（cut_pauses.py），这里的剪辑表写原片秒数，按那边的 EDL 换算成去停顿版的秒数。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUTDIR = HERE.parent / "01_录屏剪辑" / "out"
RATE = 3.9          # 每秒多少个“字”（估时单位，见 units()）
PARA_TAIL = 0.6     # 每段念完多留的秒数
SCENE_TAIL = 0.4    # 每个画面结束前多留的秒数
REC_SPEED = 1.25    # 录屏画面至少留够按这个倍速放完的时间（去停顿以后的长度）
FPS = 30

# ---------------------------------------------------------------- 口播分段（照稿子；证据编号 [n] 和【画面】【待确认】这些标记不念，已去掉）
# 全角括号里的是字幕注释，不念（spoken() 去掉后再估时，提词也不显示）。
PARAS = [
    # 0 开场
    ("P01", "Hello，大家好，我是悠一。求求大家别再用 VS Code 写代码了！"),
    ("P02", "这个视频我想做一个系列，来告诉正在搞科研的朋友、搞科研的同学，以及写代码的朋友，如何在 AI 时代更好地与 Agent 进行协作和代码开发。"),
    ("P03", "这期视频我想谈一谈为什么不用 VS Code，以及不用 VS Code 之后，我们应该用什么样的新形态去开始写代码，以及如何去使用这种新的形态。"),
    ("P04", "大家应该或多或少都听说过 Copilot、Cursor、Trae、Claude Code、Codex、WorkBuddy 这些名字。IDE、CLI 又是什么？远程 SSH 连接服务器来做科研、跑实验，该用哪个？"),
    ("P05", "我先说一下我的结论：写代码的主工作台，已经从代码编辑器换成了智能体。"),
    ("P06", "先认识两个词，后面会一直用到。IDE，全称 Integrated Development Environment，集成开发环境。写代码、管文件、调试、看改动，都在一个图形界面里完成。VS Code、Cursor、Trae 都是这种带图形界面的开发工具。"),
    ("P07", "CLI，全称 Command-Line Interface，命令行界面。没有按钮，在终端里敲一行命令，它回你一段文字。平时用的 git、ssh 都是命令行工具。"),
    ("P08", "智能体，也叫 Agent：能自己读文件、改代码、跑命令的 AI。"),
    ("P09", "这两年的 AI 编程工具，基本就是在这两种界面里长出来的：一种住在 IDE 里，一种住在 CLI 里。"),
    ("P10", "这期我把 AI 写代码这五年的变化捋一遍，你就知道为什么了。想直接看怎么用的，可以直接跳到第二章。"),
    # 1 补全和聊天
    ("P11", "2021 年 6 月，GitHub Copilot 在 VS Code 里开始预览，第二年正式上线。它只会一件事：你敲代码，它帮你往下补，补一行，或者补一整个函数。"),
    ("P12", "2022 年 11 月，ChatGPT 出来了。那时候大家这样写代码：在聊天框里要代码，复制，粘贴到 VS Code 里跑；报错了，再把报错复制回去。网页、App、手机都一样，大家都成了“CV 工程师”。"),
    ("P13", "这和以前在 CSDN、Stack Overflow 上抄代码，流程几乎一样，只是换了个地方抄。数据上也看得出来：Stack Overflow 的月提问量在 ChatGPT 出来后一路往下掉，到 2025 年 5 月，跌回了它 2009 年刚上线时的水平。"),
    ("P14", "2023 年底，Copilot Chat 正式可用，聊天框搬进了 VS Code 的侧边栏。能问，能解释代码，但还不能自己改文件、跑命令。"),
    ("P15", "这一阶段，人是主角，AI 是一个更聪明的 chatbox（聊天框）。"),
    # 2 编辑器里的智能体
    ("P16", "变化从 2024 年底开始：AI 能自己动手了。"),
    ("P17", "2024 年 11 月，Windsurf 发布，号称第一个“智能体 IDE”；同一个月，Cursor 上线 Agent 模式，VS Code 的 Copilot 也能一次改多个文件。"),
    ("P18", "2025 年 1 月，字节发布 Trae。国际版当时免费，能用 Claude 3.5 Sonnet。2 月，Copilot 也有了 Agent 模式。"),
    ("P19", "这些编辑器有个共同点：Cursor、Windsurf、Trae 都是从 VS Code 改出来的。所以那时候的 AI，还是住在 VS Code 里。"),
    ("P20", "再往后，大家嫌一轮一轮指挥 AI 太累，开始“写好需求文档，让 AI 一次做完”。"),
    ("P21", "2025 年 7 月，Trae 推出 SOLO 模式，要邀请码。我当时拿到了资格。"),
    ("P22", "用法很简单：人把 PRD，也就是产品需求文档写好，AI 自己拆任务、写代码、跑起来。"),
    ("P23", "同一个月，亚马逊的 Kiro 也在推同样的思路，叫“规格驱动开发”：先出需求、设计、任务清单，再写代码。"),
    ("P24", "体感上，AI 的自主性一下子强了很多。人不用每一轮都告诉它做什么，定好一份文档，它一口气做完。"),
    ("P25", "问题也很快出来了：一次做太多，容易刹不住车，越做越偏，做出来的和 PRD 对不上。"),
    ("P26", "任务一长就乱。那时候 Claude 已经有 20 万 token 的上下文了，现在更是到了 100 万。麻烦在于塞得越多，它越容易乱。2025 年 7 月有研究专门测过，18 个模型都是输入越长、表现越不稳定，这个现象叫“上下文腐烂”。"),
    # 3 终端里的智能体
    ("P27", "同一时间，另一条路线在终端里起来了。"),
    ("P28", "2025 年 2 月，Anthropic 发布 Claude Code，5 月正式上线。它一开始就是个命令行工具：在终端里说一句话，它自己读代码、改文件、跑命令。"),
    ("P29", "4 月，OpenAI 发布开源的 Codex CLI。之后 Google 出了 Gemini CLI，Cursor 也出了 CLI。2025 年，基本每家都做了自己的终端智能体。"),
    ("P30", "程序员很喜欢 CLI：看起来很极客；敲命令比点界面快；和 git、SSH、各种脚本天然接得上。"),
    ("P31", "门槛也在这：各家命令不一样，换一个工具就要重新学一遍；没有界面，看改动、看结果都得自己敲命令。"),
    ("P32", "我自己用了一段时间 Codex 的 CLI，后来尝试了一下 Claude Code 的 CLI，发现有些命令不一样，得重新适应，用起来就卡卡的，经常打错命令。"),
    ("P33", "有句话我很认同：学得快的人，会发现什么都要学；学得慢的人，会发现很多东西不用学了，因为 AI 一直在降低门槛。CLI 就是个例子，后面你会看到它的门槛怎么被抹平。"),
    # 4 让 AI 自己验收：loop
    ("P34", "一次做完靠不住，那怎么办？答案是 Agent loop。"),
    ("P35", "需求文档加测试：先写测试，再写代码，跑测试，没过就改，改完再跑。Anthropic 2025 年 4 月给 Claude Code 写的官方最佳实践，推荐的就是这个流程。"),
    ("P36", "大 loop 里套小 loop，每个小 loop 都在调工具、跑命令。人不用中途盯着，最后验收就行。这样 AI 能把一个 demo 做到八九成。"),
    ("P37", "2025 年 11 月，Anthropic 公开了让 AI 做长任务的办法，这类任务要跑好几个小时，甚至好几天：先把需求拆成一张功能清单，每次只做一项，做完用浏览器自动测一遍，写进度文件，下一轮接着做。这就是“PRD 加测试”的 loop。"),
    ("P38", "早期卡在前端：那时候流行前后端分开写两个 PRD，最后人来联调。"),
    ("P39", "一联调就发现，AI 写的前端经常点不动。管理系统这类东西，数据要在浏览器里点、要输入，后端再去查数据库有没有写对，边界条件又多。"),
    ("P40", "所以浏览器控制成了关键：2024 年 10 月，Anthropic 推出 computer use，模型能看屏幕、动鼠标、打字。"),
    ("P41", "11 月，Anthropic 发布 MCP，一个让 AI 连外部工具的标准接口。2025 年 3 月，微软基于它出了 Playwright MCP，AI 可以直接操作浏览器做测试。"),
    ("P42", "2026 年 3 月，GPT-5.4 在 OSWorld 上拿到 75%，人类基线是 72.4%。准确率已经追上人了。速度还差：2025 年的研究发现，最好的智能体要比必要的步骤多走 2.7 到 4.3 倍，人几分钟的事它要几十分钟。"),
    ("P43", "大公司已经在收集人操作电脑的数据来训练这个能力。Meta 今年 4 月开始，在美国员工的工作电脑上记录鼠标、键盘和部分截图，6 月因为数据在公司内部泄露暂停了。"),
    ("P44", "浏览器跑通以后，前端、后端、数据库就能连起来测。云上的服务，只要你敢给权限，它也能测。"),
    ("P45", "我最近在做一个微信小程序：数据库用腾讯的 CloudBase，后端是微信云函数，前端在本地跑。把这些命令告诉 AI，它能自己把测试跑完。"),
    # 5 以智能体为中心的桌面工作台
    ("P46", "为什么 2025 年底开始，各家都改界面？因为 AI 能独立干的活越来越长。"),
    ("P47", "有个研究机构叫 METR，专门测这个。他们的结论是：AI 能独立完成的任务长度，大约每 7 个月翻一倍，2023 年以后更快，大概 4 个月翻一倍。"),
    ("P48", "写代码本身也已经很强了。今年 2 月，Anthropic 让 16 个 Claude 并行干活，写出了一个能编译 Linux 内核的 C 编译器，大约 10 万行代码。"),
    ("P49", "很多人已经不怎么看代码了，靠说。2025 年 2 月，Karpathy 提了个词叫 vibe coding：用语音输入，改动全部接受，diff 都不看。做个 demo 可以这么干，做研究不行，后面说为什么。"),
    ("P50", "所以界面跟着变了：2025 年 10 月，Cursor 2.0 把界面换成以智能体为中心，能同时跑好几个智能体。"),
    ("P51", "11 月，Google 发布 Antigravity，专门有一个视图用来同时管多个智能体。"),
    ("P52", "Claude Code 有了桌面版，2026 年 2 月 Codex 出了桌面 App。"),
    ("P53", "今年 6 月，GitHub 出了 Copilot 桌面 App；Windsurf 改名 Devin Desktop，打开默认就是智能体控制台；字节把 Trae 拆成了 TraeCode 和 TRAE Work。"),
    ("P54", "编辑器还在，只是退到了第二层。"),
    # 6 AI 走出编辑器
    ("P55", "今年 Agent 这么火，离不开 OpenClaw 的出现。"),
    ("P56", "2026 年 1 月，Anthropic 推出 Cowork，把 Claude Code 这套能力给不写代码的人用。"),
    ("P57", "几乎同时，开源项目 OpenClaw 爆火。它装在你自己的电脑上，你在 Telegram、WhatsApp 这类聊天软件里发一句话，它就在电脑上替你干活；它能记住之前的事，还会自己连续执行任务。"),
    ("P58", "到 3 月初，GitHub 上有 24 万多星，现在已经超过 39 万星。国内叫它“养龙虾”。"),
    ("P59", "2 月，OpenClaw 的作者加入了 OpenAI。"),
    ("P60", "国内也跟上了：3 月腾讯出了 WorkBuddy；6 月字节把 TRAE SOLO 改名 TRAE Work；8 月又出了豆包 Work。"),
    ("P61", "9 月，Anthropic 宣布把 Cowork 并进 Claude 的主界面。"),
    ("P62", "方向很清楚：AI 从帮你写代码，变成替你干活。"),
    ("P63", "风险也很清楚：2 月，安全公司在 OpenClaw 的技能市场里查出几百个恶意技能，会偷你电脑上的账号密码。3 月，工信部专门发了风险提示：默认配置很容易被攻击、泄露信息。"),
    ("P64", "给 AI 的权限越大，出事的代价越大。"),
    # 7 第二章：Claude Code 桌面版实操
    ("P65", "下面拿 Claude Code 桌面版演示，Codex 桌面版思路差不多。"),
    ("P66", "同时开好几个会话。每个会话可以有自己的 Git worktree，互不干扰。"),
    ("P67", "右边看 diff。点某一行就能写评论，写完一次提交，Claude 按评论改。也能用 @ 引用文件。"),
    ("P68", "内置终端和浏览器：它能自己起服务、打开页面点一遍。生成的 PDF、HTML 也直接在右边打开。"),
    ("P69", "善用 HTML 可视化。想知道 AI 改了什么，或者自己哪里没看懂，我一般让 AI 写一个 HTML 页面，把内容画出来，在右边的浏览器里直接打开。"),
    ("P70", "原因很简单：同一件事，给我一段文字和一张图，我肯定先看图。图有颜色，字有大有小、有主有次，一眼就能抓到它想说什么。"),
    ("P71", "权限分几档：Manual，每一步都问你；Accept edits，改文件不问；Plan，只出方案，不动代码；Auto，由另一个模型替你审批；Bypass，全放开，要先在设置里打开开关。"),
    ("P72", "SSH：在环境里添加一个 SSH 连接，它会在服务器上装好 Claude Code，直接在实验室服务器上干活。"),
    ("P73", "注意两点：服务器要是 Linux 或 macOS；服务器要能连上模型的 API，因为 Claude 是在服务器上跑的。Codex 桌面版也能连 SSH 主机，但要先在服务器上装好 Codex。"),
    ("P74", "Routines，定时任务，分两种：本地任务，能读你的文件，但要电脑开着、App 开着；云端任务，关机也能跑，但读不到你本地的文件。我用本地任务定期整理项目的上下文目录：超过一个月的记录，让它移到归档。"),
    ("P75", "computer use：直接操作你电脑上的软件。现在是研究预览，Mac 和 Windows 都有，要 Pro 或 Max，默认关着，每个 App 第一次用都要你点允许。在 Windows 上，命令行版用不了 computer use，这也是我推荐桌面版的一个原因。"),
    ("P76", "浏览器插件 Claude in Chrome：用你浏览器的登录状态帮你查信息、比价、整理网页，也能替你发消息、下单，但这些事的责任算你的。"),
    ("P77", "它有几条限制：不做股票交易，不绕验证码，不替你输入敏感信息；进金融网站前要你同意，成人网站和盗版网站直接拦截。它默认自己审自己的操作，建议改成每一步都要你批准。把登录状态交给 AI，风险要自己掂量。"),
    ("P78", "今年 9 月 OpenAI 发布的 GPT-6 Astra，官方定位就是电脑操作和长任务，发布演示里在 Blender 里建了一整栋房子，再导进虚幻引擎。"),
    ("P79", "一句话总结：它把前面所有东西都放进一个界面里，门槛很低，上手就能用。说它是编程软件也行，说它是办公软件也行。"),
    # 8 结尾
    ("P80", "这就是 AI 写代码这五年的变化。"),
    ("P81", "我是悠一，拜拜。"),
]
OPTIONAL = {"P08": "可选", "P43": "可删", "P78": "可选，待确认"}
FIXED = {}
PARA_MIN = {"P81": 3.0}

# ---------------------------------------------------------------- 画面
# 版式：A = 出镜大框在左、右边写要点；B = 出镜缩到左上角、左下是本章目录（toc 为 None 时不显示目录）、右边大区域放演示。
# 出镜框在每个画面都留着（用户：“你也要预留出我露脸视频的位置”）；录屏只放在右边演示区，不压出镜框。
# toc = -1：目录显示、全部算“已讲过”（第二章可选的 GPT-6 那段）。
CHAPTERS = {
    "开场": {"title": "开场", "items": []},
    "第一章": {"title": "第一章：AI 写代码这五年", "items": ["补全和聊天", "编辑器里的智能体", "终端里的智能体", "让 AI 自己验收：loop", "以智能体为中心的桌面工作台", "AI 走出编辑器"]},
    "第二章": {"title": "第二章：Claude Code 桌面版", "items": ["多会话 · worktree", "看 diff · 写评论", "终端和浏览器", "HTML 可视化", "权限分几档", "SSH 连服务器", "Routines 定时任务", "computer use", "Claude in Chrome"]},
    "结尾": {"title": "结尾", "items": []},
}
SCENES = [
    # id, type, 版式, 章, 目录第几项, 段落, 最短时长
    # 第一章每一节一个画面：上面是这一节的时间线（带各家图标），下面的内容按段落换。
    ("S01", "intro",       "A", "开场", None, ["P01"], 6.0),
    ("S02", "series",      "A", "开场", None, ["P02", "P03"], 0),
    ("S03", "names",       "A", "开场", None, ["P04"], 0),
    ("S04", "conclusion",  "A", "开场", None, ["P05"], 0),
    ("S05", "terms",       "B", "开场", None, ["P06", "P07", "P08", "P09"], 0),
    ("S06", "roadmap",     "A", "开场", None, ["P10"], 0),
    ("S07", "sec1",        "B", "第一章", 0, ["P11", "P12", "P13", "P14", "P15"], 0),
    ("S08", "sec2a",       "B", "第一章", 1, ["P16", "P17", "P18", "P19"], 0),     # P19 放 TraeCode 录屏（IDE 界面）
    ("S09", "sec2b",       "B", "第一章", 1, ["P20", "P21", "P22", "P23"], 0),     # P21 Trae 使用记录；P22 TraeCode 录屏（SOLO 模式）
    ("S10", "sec2c",       "B", "第一章", 1, ["P24", "P25", "P26"], 0),
    ("S11", "sec3",        "B", "第一章", 2, ["P27", "P28", "P29", "P30", "P31", "P32"], 0),
    ("S12", "quote",       "A", "第一章", 2, ["P33"], 0),
    ("S13", "sec4a",       "B", "第一章", 3, ["P34", "P35", "P36", "P37"], 0),     # 第 4 节都用代码模拟操作（稿子标题里的要求）
    ("S14", "sec4b",       "B", "第一章", 3, ["P38", "P39"], 0),
    ("S15", "sec4c",       "B", "第一章", 3, ["P40", "P41", "P42", "P43"], 0),
    ("S16", "sec4d",       "B", "第一章", 3, ["P44", "P45"], 16.0),
    ("S17", "sec5a",       "B", "第一章", 4, ["P46", "P47", "P48", "P49"], 0),
    ("S18", "sec5b",       "B", "第一章", 4, ["P50", "P51", "P52", "P53", "P54"], 0),
    ("S19", "sec6",        "B", "第一章", 5, ["P55", "P56", "P57", "P58", "P59", "P60", "P61"], 0),
    ("S20", "direction",   "A", "第一章", 5, ["P62"], 0),
    ("S21", "risk",        "B", "第一章", 5, ["P63", "P64"], 0),
    ("S22", "ch2",         "A", "第二章", None, ["P65"], 5.0),
    ("S23", "sessions",    "B", "第二章", 0, ["P66"], 0),        # 录屏剪辑见 RECS；最短时长按录屏长度自动算
    ("S24", "diff",        "B", "第二章", 1, ["P67"], 0),
    ("S25", "termbrowser", "B", "第二章", 2, ["P68"], 0),
    ("S26", "html",        "B", "第二章", 3, ["P69", "P70"], 0),     # 模拟：录屏里没有这一项
    ("S27", "perms",       "B", "第二章", 4, ["P71"], 0),
    ("S28", "ssh",         "B", "第二章", 5, ["P72", "P73"], 0),
    ("S29", "routines",    "B", "第二章", 6, ["P74"], 0),
    ("S30", "computeruse", "B", "第二章", 7, ["P75"], 0),            # 模拟：录屏里没有这一项
    ("S31", "chrome",      "B", "第二章", 8, ["P76", "P77"], 0),
    ("S32", "gpt6",        "B", "第二章", -1, ["P78"], 11.0),        # 可选；GPT-6 片段借用第 02 期素材
    ("S33", "summary",     "A", "第二章", None, ["P79"], 0),
    ("S34", "outro",       "A", "结尾", None, ["P80", "P81"], 0),
]

# ---------------------------------------------------------------- 录屏剪辑表（原片秒数，看联系表挑的）
# cuts = [[起, 止, 从哪句话开始（"段号:短语"；不写就按去停顿后的长短分配）], …]
# 页面把画面时间映射到原片：留的时间比片段长就停在最后一帧，短就加速。prep_media.py 只抽表里用到的范围。
# maxSpeed：这个画面允许的最快倍速（最短时长按它算）；part：录屏只占画面里的一段（最短时长不按录屏算）。
RECS = {
    "sec2a":       {"src": "trae", "cuts": [[0.0, 10.4, "P19:这些编辑器"]], "part": True},             # IDE：资源管理器、编辑器、右边的 Agent
    "sec2b":       {"src": "trae", "cuts": [[10.6, 21.3, "P22:用法很简单"]], "part": True},             # 切到 SOLO 模式、打开工具
    "sessions":    {"src": "cc", "cuts": [[10.0, 24.0], [28.0, 38.0], [40.0, 50.0]]},               # Code 页、切换会话、分支和 worktree
    "diff":        {"src": "cc", "cuts": [[58.0, 64.0], [66.0, 72.0], [74.0, 82.0]]},               # 打开 diff、选对比范围、看改动
    "termbrowser": {"src": "cc", "cuts": [[82.0, 91.0], [92.0, 100.0, "P68:它能自己起服务"]]},     # 终端、浏览器面板（检测到开发服务器）
    "perms":       {"src": "cc", "cuts": [[136.0, 139.5], [152.0, 157.0, "P71:Manual"], [158.0, 163.0, "P71:Accept edits"],
                                         [164.0, 172.0, "P71:Plan"], [140.0, 151.0, "P71:Auto"], [178.0, 188.0, "P71:Bypass"],
                                         [301.0, 302.4, "P71:要先在设置里"]]},                          # 最后一段：切到 Bypass 时弹的警告框
    "ssh":         {"src": "cc", "cuts": [[286.0, 299.0], [299.0, 300.8, "P72:直接在实验室"]]},     # 环境菜单：Remote Control、WSL、SSH → 选好 rpartx3080（后面是切权限，不要）
    "routines":    {"src": "cc", "cuts": [[254.0, 262.0], [262.0, 272.0, "P74:本地任务"]]},        # Routines 页、新建本地任务
    "chrome":      {"src": "cc", "cuts": [[102.0, 114.0]]},                                        # Chrome 右边打开 Claude 侧边栏
    "gpt6":        {"src": "gpt6", "cuts": [[0.0, 30.0]], "maxSpeed": 3.0},
}
SOURCES = {
    "cc": {"edl": "录屏_ClaudeCode桌面版_edl.json", "video": "../01_录屏剪辑/out/录屏_ClaudeCode桌面版_去停顿.mp4"},
    "trae": {"edl": "录屏_TraeCode_edl.json", "video": "../01_录屏剪辑/out/录屏_TraeCode_去停顿.mp4"},
    "gpt6": {"edl": None, "video": r"D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\教程_Claude做视频\素材\GPT6建模\GPT6建模_原片30s.mp4"},
}


def spoken(text):
    """念出来的部分：去掉全角括号里的字幕注释。"""
    return re.sub(r"（[^（）]*）", "", text)


def units(text):
    """估时单位：汉字 1，英文单词 1.5，数字每位 1.1，逗号类停顿 0.9，句号类停顿 1.6。页面里的 at() 用同一套算法。"""
    u = 0.0
    for m in re.finditer(r"[A-Za-z][A-Za-z\-]*|\d|[一-鿿]|[，、：；]|[。？！]", spoken(text)):
        s = m.group(0)
        if s[0].isascii() and s[0].isalpha():
            u += 1.5
        elif s.isdigit():
            u += 1.1
        elif s in "，、：；":
            u += 0.9
        elif s in "。？！":
            u += 1.6
        else:
            u += 1.0
    return u


def edl_map(src):
    """原片秒数 → 去停顿版秒数（落在剪掉的地方就取下一段的开头）。"""
    name = SOURCES[src]["edl"]
    if not name:
        return lambda t: t
    segs = json.loads((CUTDIR / name).read_text(encoding="utf-8"))["segments"]

    def m(t):
        for a, b, v, n0, n1 in segs:
            if t < a:
                return n0
            if t <= b:
                return n0 + (t - a) / v
        return segs[-1][4]
    return m


def rec_table():
    out = {}
    for typ, r in RECS.items():
        m = edl_map(r["src"])
        cuts = []
        for c in r["cuts"]:
            n0, n1 = m(c[0]), m(c[1])
            cuts.append({"s0": c[0], "s1": c[1], "n0": round(n0, 3), "n1": round(max(n0 + 1 / FPS, n1), 3), "at": c[2] if len(c) > 2 else None})
        out[typ] = {"src": r["src"], "cuts": cuts, "len": round(sum(c["n1"] - c["n0"] for c in cuts), 3),
                    "maxSpeed": r.get("maxSpeed", REC_SPEED), "part": r.get("part", False)}
    return out


def main():
    paras, t = {}, 0.0
    order = [p for p, _ in PARAS]
    text = dict(PARAS)
    assert len(order) == len(set(order)), "段号重复"
    used = [p for s in SCENES for p in s[5]]
    assert sorted(used) == sorted(order), f"段落没排进画面或重复：{set(order) ^ set(used)}"
    for typ, r in RECS.items():
        for c in r["cuts"]:
            if len(c) > 2:
                pid, phrase = c[2].split(":", 1)
                assert phrase in spoken(text[pid]), f"{typ}: 「{phrase}」不在 {pid}"
    recs = rec_table()
    for pid in order:
        if pid in FIXED:
            speech, dur = FIXED[pid], FIXED[pid]
        else:
            speech = units(text[pid]) / RATE
            dur = max(speech + PARA_TAIL, PARA_MIN.get(pid, 0))
        paras[pid] = {"id": pid, "text": text[pid], "say": spoken(text[pid]), "speech": round(speech, 3), "dur": round(dur, 3),
                      "optional": OPTIONAL.get(pid)}
    scenes = []
    for sid, typ, layout, chap, toc, pids, min_dur in SCENES:
        if typ in recs and not recs[typ]["part"]:      # 整个画面都是录屏：至少留够按 maxSpeed 放完的时间（前后各留 0.5 s）
            min_dur = max(min_dur, recs[typ]["len"] / recs[typ]["maxSpeed"] + 1.0)
        start = t
        for pid in pids:
            paras[pid]["start"] = round(t, 3)
            paras[pid]["scene"] = sid
            t += paras[pid]["dur"]
        t += SCENE_TAIL
        if t - start < min_dur:
            extra = min_dur - (t - start)
            paras[pids[-1]]["dur"] = round(paras[pids[-1]]["dur"] + extra, 3)
            t = start + min_dur
        t = round(round(t * FPS) / FPS, 4)
        scenes.append({"id": sid, "type": typ, "layout": layout, "chapter": chap, "toc": toc,
                       "start": round(start, 4), "end": t, "paras": pids})
    total = t
    tl = {"fps": FPS, "total": total, "rate": RATE, "paraTail": PARA_TAIL,
          "chapters": CHAPTERS, "scenes": scenes, "paras": [paras[p] for p in order],
          "recs": recs, "sources": SOURCES}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False) + ";\n", encoding="utf-8")

    def mmss(x):
        return f"{int(x // 60):02d}:{x % 60:04.1f}"
    lay = {"A": "出镜大框", "B": "出镜左上角"}
    lines = ["# 分段时间表（录制对照）", "",
             f"整片 {mmss(total)}（{total:.1f} 秒）。时长是按每秒约 {RATE} 个字估的，念得快慢都没关系：录完以后会按你的实际录音重新排。",
             "出镜框里有这一段要念的话（提词），右下角是段号（P01…），对着这张表念就行。",
             "标了“可选 / 可删”的段，不想要就跳过不念。第二章录屏那几段留的时间比稿子长，可以边看边多讲几句。", "",
             "| 开始 | 段号 | 画面 | 版式 | 念什么 |", "|---|---|---|---|---|"]
    for s in scenes:
        for pid in s["paras"]:
            p = paras[pid]
            opt = f"（{p['optional']}）" if p["optional"] else ""
            lines.append(f"| {mmss(p['start'])} | {pid}{opt} | {s['id']} {s['type']} | {lay[s['layout']]} | {p['text']} |")
    (HERE / "分段时间表.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"total {total:.1f}s = {mmss(total)}, scenes {len(scenes)}, paras {len(order)}")
    for s in scenes:
        extra = f"  录屏 {recs[s['type']]['len']:.1f}s" if s["type"] in recs else ""
        print(f"  {s['id']} {s['type']:<12} {s['layout']} {mmss(s['start'])}-{mmss(s['end'])} ({s['end'] - s['start']:.1f}s){extra}")


if __name__ == "__main__":
    main()
