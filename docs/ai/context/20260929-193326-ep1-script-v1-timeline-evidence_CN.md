# 第 1 期台本 v1：修正后的时间线、证据链补充、改好的口播稿

- 时间：2026-09-29（UTC+9），晚上。
- 起因：用户看完上一份核对（`20260929-191823-ep1-evolution-factcheck_CN.md`）后说：“没问题，你捋一下正确的时间线，然后修改一下上面的稿子，还有证据链你觉得还缺什么吗，比如openclaw的出现这种”。
- 本文包含：
  1. 修正后的时间线（**以本文为准**，比上一份多了 OpenClaw、MCP、computer use、Antigravity、Kiro 等）；
  2. 证据链还缺什么；
  3. 改好的口播稿 v1，像论文一样带证据编号：句子后面的 `[n]` 对应稿子末尾「证据」里的同号条目；
  4. 字幕括号注释候选；
  5. 待用户确认的点。
- 同日晚第二次修改。用户：“这些补充的材料你可以像论文一样，在这句话后面加括号和数字，然后在最后按照数字来标注证据，然后你也在稿子开头说一下，就是注解的含义”。
  - 加了证据编号（69 条）和稿子开头的注解说明。
  - 重新核对出处时更正了三处，见文末「核对的局限」。
- 同日晚第三次修改：用户审过全文，删了“插曲”和原第 8 段（研究生怎么用），把桌面版演示挪成第二章，并要求开头介绍 IDE 和 CLI、加上“善用 HTML 可视化”那段。
  - 复查后按首次出现重新编号：69 条 → 59 条（新增 1 条：Claude 100 万上下文；11 条随删掉的段落拿出正文，出处留在第六节）。
  - 更正“1M 一千万”的笔误（1M 是一百万）；“跳转下一节”改成“跳到第二章”。
- 稿子按 `AGENTS.md` 的台本风格写：
  - 短句、口语、分点；
  - 开场一句话，先抛困惑再拆解；
  - 不用“不是……而是……”，不堆例子。
- 事实都联网核过，日期写到月；拿不准的在稿子里标【待确认】。
- 新系列的目录还没定，稿子先放在这里；目录定了再挪到 `<系列目录>/01_<标题>/台本/`。

---

## 一、修正后的时间线

### 画面上放的精简版（16 个点，做成一条横向时间线）

| 时间 | 事件 | 属于哪个阶段 |
|---|---|---|
| 2021-06 | GitHub Copilot 在 VS Code 里预览（行内补全） | 补全 |
| 2022-11 | ChatGPT 发布，开始“复制粘贴” | 聊天 |
| 2023-12 | Copilot Chat 正式可用（聊天进侧边栏） | 聊天 |
| 2024-10 | Anthropic 推出 computer use（AI 看屏幕、动鼠标） | 基础设施 |
| 2024-11 | Windsurf、Cursor Agent 模式；Anthropic 发布 MCP | 编辑器里的智能体 |
| 2025-01 | 字节发布 Trae | 编辑器里的智能体 |
| 2025-02 | Claude Code 预览（终端） | 终端智能体 |
| 2025-04 | OpenAI Codex CLI | 终端智能体 |
| 2025-07 | Trae SOLO、亚马逊 Kiro：写需求文档，AI 一次做完 | 需求驱动 |
| 2025-09~11 | Anthropic 不再给中国控股公司供货 → Trae 下架 Claude | 模型断供 |
| 2025-10 | Cursor 2.0：界面改成以智能体为中心 | 桌面工作台 |
| 2025-11 | Google Antigravity（管理多个智能体的视图） | 桌面工作台 |
| 2026-01 | Claude Cowork；OpenClaw 爆火（“养龙虾”） | 替你干活 |
| 2026-02 | Codex 桌面 App | 桌面工作台 |
| 2026-06 | Copilot 桌面 App、Devin Desktop（原 Windsurf）、TRAE Work | 桌面工作台 / 替你干活 |
| 2026-09 | Cowork 并入 Claude 主界面 | 替你干活 |

### 完整版（分阶段）

**0. 前 AI：搜答案、抄代码**
- 在 Stack Overflow / CSDN 上找答案、复制。
- Stack Overflow 的月提问量 2014 年见顶；ChatGPT 出来后加速下滑，到 2025-05 跌回 2009 年刚上线时的水平（The Pragmatic Engineer，数据来自 Stack Exchange Data Explorer）。

**1. 补全（2021–2022）**
- 2021-06-29：GitHub Copilot 技术预览，首发在 VS Code，背后是 OpenAI 的 Codex 模型。
- 2022-06-21：Copilot 正式可用。
- 这一阶段 AI 只能往下补代码（一行或一整个函数）。

**2. 聊天，复制粘贴（2022-11 起）**
- 2022-11-30：ChatGPT 发布。
- 2023-12-29：Copilot Chat 正式可用，聊天进了 VS Code 侧边栏；能问答、解释，不能自己改文件、跑命令。

**3. 编辑器里的智能体（2024-11 起）**
- 2023-03：Cursor 发布（从 VS Code 分叉出的独立编辑器）。
- 2024-11-12：VS Code Copilot Edits 预览（多文件编辑）。
- 2024-11-13：Codeium 发布 Windsurf，自称“第一个智能体 IDE”（也是 VS Code 分叉）。
- 2024-11-24：Cursor 0.43 上线 Agent 模式（改多个文件、跑终端命令）。
- 2025-01-19/20：字节发布 Trae（VS Code 分叉）；国际版当时免费，带 Claude 3.5 Sonnet、GPT-4o。
- 2025-02：Copilot Agent 模式（自己改文件、跑命令、看报错再改）。
- 2025-02-02：Karpathy 提出 vibe coding（用语音输入、改动全部接受、不看 diff）；后来成了柯林斯词典 2025 年度词（2025-11-06 公布）。

**3b. 写需求文档，AI 一次做完（2025 年中）**
- 2025-07-14：亚马逊 Kiro 公开预览，主打“规格驱动开发”：先生成需求、设计、任务清单，再写代码。
- 2025-07-21：Trae SOLO 预览（国际版 Pro，要邀请码）。
- 2025-07-14：Chroma 发布“上下文腐烂（context rot）”研究：18 个模型，输入越长表现越不稳定。

**4. 终端智能体、云端智能体（2025）**
- 2025-02-24：Claude Code 研究预览（随 Claude 3.7 Sonnet），2025-05-22 正式可用（随 Claude 4）。
- 2025-04-16：OpenAI Codex CLI（开源）；2025-05-16：Codex 云端智能体预览。
- 2025-05-19：GitHub Copilot coding agent（把 issue 指派给它，它在后台开 PR）。
- 2025-06-25：Google Gemini CLI（开源，个人免费每天 1000 次）。
- 2025-08-07：Cursor CLI beta。

**基础设施：让智能体能自己验证、能连外部世界（和上面几段并行）**
- 2024-10-22：Anthropic computer use 公开测试（看屏幕、动鼠标、打字）。
- 2024-11-25：Anthropic 发布 MCP（AI 连接外部工具的开放标准）；2025-12-09 捐给 Linux 基金会下的 Agentic AI Foundation，当时月 SDK 下载 9700 万。
- 2025-01-23：OpenAI Operator（操作浏览器的智能体）；2025-07-17 并入 ChatGPT agent。
- 2025-03：微软 Playwright MCP（AI 通过 MCP 操作浏览器做测试）。
- 2025-04：Anthropic 发布 Claude Code 最佳实践，推荐测试驱动：先写测试、确认失败、再写代码、反复跑到通过。
- 2025-08：AGENTS.md 开放格式（OpenAI、Google、Cursor 等一起推），后来 6 万多个项目采用；2025-12 也捐给 AAIF。
- 2025-08-26：Claude for Chrome 研究预览（1000 名 Max 用户），2025-12 开放到所有付费档。
- 2025-10-16：Anthropic Agent Skills（SKILL.md）；2025-12-18 开放成标准。
- 2025-11-26：Anthropic 公开“长时间运行的智能体”做法：先拆成功能清单，每轮只做一项，做完用浏览器自动化测一遍，写进度文件，下一轮接着做。
- 2026-01：“Ralph Wiggum loop”走红（用一个 while 循环不停把同一个提示喂给 Claude Code），Anthropic 做成了官方插件。
- 2026-02-05：Anthropic 用 16 个并行的 Claude 从零写出能编译 Linux 内核的 C 编译器（约 10 万行、近 2000 个会话、约 2 万美元 API 费用）。
- 2026-02：OpenAI 公开“harness engineering”：一个小团队（3 人，后来 7 人）用 Codex 5 个月写了约 100 万行代码，没有一行是手写的，合并了约 1500 个 PR。
- 2026-03-05：GPT-5.4 在 OSWorld-Verified（让 AI 操作真实电脑完成任务的基准）上 75.0%，超过人类基线 72.4%。
- 2026-03-13：Claude Opus 4.6 / Sonnet 4.6 的 100 万 token 上下文正式可用；现在的 Claude Opus 5.5 也是 100 万。

**5. 模型断供（2025）**
- 2025-06-03：Anthropic 几乎切断 Windsurf 的 Claude 3.x 直供，提前不到 5 天通知，原因是 OpenAI 要收购 Windsurf 的传闻。
- 2025-07-14：Cognition 收购 Windsurf；2025-07-16 恢复 Claude Sonnet 4 直供。
- 2025-09-05：Anthropic 改条款，不再给多数股权由中国等地实体控制的公司提供 Claude（字节、腾讯、阿里都在内）。
- 2025-11-04/05：Trae 下架全部 Claude 模型（含 Claude Sonnet 4），给付费用户补偿每月额外请求次数。

**6. 以智能体为中心的桌面工作台（2025-10 起）**
- 2025-10-29：Cursor 2.0，界面从“文件”换成“智能体”，可同时跑多个智能体（各自一个 worktree）；推出自研模型 Composer。
- 2025-11-18：Google Antigravity（随 Gemini 3）：编辑器视图 + 管理多个智能体的“Manager 视图”。
- 2025 年底前后：Claude 桌面 App 出现 Code 标签页（第三方报道，没找到一手公告）；2026-04-14 前后大改版：多会话侧栏、集成终端和文件编辑器、worktree 隔离、Routines。
- 2026-02-02：Codex 桌面 App（macOS），2026-03-04 Windows；2026-04-16 更新加入 computer use、内置浏览器、插件、自动化。
- 2026-06-02：GitHub Copilot 桌面 App 技术预览；同日 Windsurf 更名 Devin Desktop，默认界面换成智能体控制台。
- 2026-08-04：TRAE IDE 品牌升级为 TraeCode。

**7. 从写代码到替你干活（2026）**
- 2025-11-24：OpenClaw 首次发布（当时叫 Warelay，12 月改 CLAWDIS，2026-01-02 改 Clawdbot）。
- 2026-01-12：Anthropic Cowork 研究预览（把 Claude Code 的能力给不写代码的人用），4 月正式可用。
- 2026-01 下旬：OpenClaw 爆火。01-27 因 Anthropic 商标投诉改名 Moltbot，01-30 改名 OpenClaw。装在自己电脑上，通过 Telegram、WhatsApp、Discord、Signal 等聊天软件指挥，有长期记忆、会主动执行任务；到 2026-03-02 GitHub 24.7 万星。国内叫“养龙虾”，开发者接上了 DeepSeek 和微信，腾讯、智谱推出了基于它的服务。
- 2026-02：安全公司在 OpenClaw 技能市场 ClawHub 的 2857 个技能里查出 341 个恶意技能（偷密码），2 月 16 日增加到 824 个以上。
- 2026-02-14：OpenClaw 作者 Peter Steinberger 宣布加入 OpenAI，项目转给基金会。
- 2026-03：工信部网络安全威胁和漏洞信息共享平台（NVDB）、国家互联网应急中心（CNCERT）先后发风险提示；工信部提出“六要六不要”；国企和政府机关被限制在办公电脑上用。
- 2026-03-09：腾讯 WorkBuddy（CodeBuddy 家族的本地办公智能体，媒体称“类 OpenClaw”）。
- 2026-04-21：Meta 宣布在美国员工的工作电脑上记录鼠标、键盘和部分截图训练 AI，不能退出；2026-06 因数据在公司内部泄露暂停。
- 2026-06-08：TRAE SOLO 更名 TRAE Work；2026-08-24/25 字节把 TRAE、扣子并入豆包体系，推出豆包 Work。
- 2026-09-03：GPT-6 Astra 发布（先给部分机构），官方定位是电脑操作和长任务；发布演示里在 Blender 建模再导入虚幻引擎。
- 2026-09-16：Anthropic 宣布把 Cowork 并入 Claude 主界面；Claude Code 保持独立。

---

## 二、证据链还缺什么

稿子的论证链是：界面变了 → AI 能干的活越来越长 → 要靠 loop 和自动验证 → 行业都转向智能体工作台 → AI 走出编辑器；第二章录屏演示桌面版怎么用。

原稿每一环都有“我的体感”，缺“别人也看到了”的证据。按环节补，方括号里是它在稿子里的证据编号（见第三节末尾的「证据」）；没有编号的，是随删掉的段落拿出了稿子，出处留在第六节。

| 环节 | 原稿缺的 | 补什么（日期） | 放在稿子哪段 | 优先级 |
|---|---|---|---|---|
| 界面变了 → 分工变了 | 只有体感 | Anthropic 经济指数：同样是 Claude，聊天界面里 49% 的对话是“让 AI 直接干完”，Claude Code 里是 79%（2025-04 数据） | 已随原第 8 段删去 | 必加：直接证明“界面决定分工” |
| 复制粘贴时代 | 没数据 | Stack Overflow 月提问量跌回 2009 年水平（2025-05）[4] | 第 1 段 | 建议 |
| AI 能干的活越来越长 | “自主性变强”只是感觉 | METR：AI 能独立完成的任务长度约每 7 个月翻一倍（2025-03）[33]；2023 年后约 4.3 个月（2026-01 更新）[34] | 第 5 段开头 | **必加**：解释为什么所有工具都转向智能体 |
| 写代码本身很强了 | “不会再有语法报错”说过头 | 16 个 Claude 并行，写出能编译 Linux 内核的 C 编译器（2026-02）[35]。原来用的 SWE-bench Verified 80.9% 不用了：OpenAI 2026-02-23 公开说这个基准已被训练数据污染、不少测试有问题，不再拿它比前沿代码能力 | 第 5 段开头 | 建议 |
| 一次做完会跑偏 | 归因于“上下文不够长”，不准 | Claude 3 起就有 20 万 token 上下文[16]，现在是 100 万[17]；Chroma“上下文腐烂”研究（2025-07）[18] | 第 2 段 | **必加**：修正归因 |
| PRD 一次做完 | 只有 Trae SOLO | Trae SOLO（2025-07）[14]；亚马逊 Kiro 的规格驱动开发（2025-07）[15] | 第 2 段 | 建议：说明这是行业趋势 |
| PRD + TDD 的 loop | 只有体感 | Anthropic 官方推荐测试驱动（2025-04）[24]；长时间运行智能体的做法（2025-11）[25]；Ralph loop（2026-01，稿子没用） | 第 4 段 | **必加**前两项 |
| “人只需要构建 loop，文字占主导” | 只有体感 | OpenAI harness engineering：约 100 万行代码，0 行手写，人的工作是设计环境、写清意图、搭反馈 loop（2026-02） | 已随原第 8 段删去 | 必加：最强的一条 |
| 浏览器 / 电脑控制 | Meta 的例子不准 | computer use（2024-10）[26] → MCP（2024-11）[27] → Playwright MCP（2025-03）[28] → GPT-5.4 在 OSWorld 上 75%，超过人类基线（2026-03）[29]；速度：最好的智能体多走 2.7–4.3 倍步骤（2025-06）[30]；Meta 记录员工操作数据（2026-04，6 月暂停）[31, 32] | 第 4 段 | **必加**：支撑“准确率已经很强、速度还慢” |
| 口喷、语音输入 | 只有体感 | Karpathy 的 vibe coding（2025-02，用语音输入、不看 diff）[36] | 第 5 段开头 | 建议 |
| 行业都转向桌面工作台 | 只点了 Claude / Codex | Cursor 2.0（2025-10）[37]、Antigravity（2025-11）[38]、Codex App（2026-02）[40]、Copilot App、Devin Desktop（2026-06）[41, 42]、TraeCode / TRAE Work[43, 44] | 第 5 段 | **必加**：否则“别用 Copilot / Cursor”站不住 |
| AI 走出编辑器 | 只有 CoWork / WorkBuddy 两个名字 | **OpenClaw**（2026-01 爆火，“养龙虾”）[46, 47, 48] 是这一波的导火索：Cowork 同月发布[45]，WorkBuddy 被称“类 OpenClaw”[50]，TRAE Work[43]、豆包 Work[51] 随后跟进 | 第 6 段 | **必加**（你提的） |
| 风险 | 基本没有 | OpenClaw 恶意技能（2026-02）[53]、工信部风险提示（2026-03）[47]、Meta 数据内部泄露（2026-06）[32]；模型断供（2025）已随插曲删去 | 第 4、6 段 | **必加**：不讲风险，“把权限全放开”那段容易被喷 |
| 反方证据 | 没有 | METR 随机对照实验：老手用 2025 年初的 AI 工具，自己觉得快了 20%，实际慢了 19%（2025-07）；Stack Overflow 2025 调查：84% 在用或打算用，46% 不信任准确性，66% 说最大的困扰是“差一点就对”，45% 说调 AI 写的代码更费时间 | 已随原第 8 段删去 | 必加：加了反而更可信 |
| 对研究生特有的 | 没有 | PaperBench：AI 从零复现 20 篇 ICML 2024 论文，发布时最好的模型平均 21%，还没超过顶尖 ML 博士（2025-04） | 已随原第 8 段删去 | 必加：这是研究生频道 |

### 放进稿子里的选择

- 按台本风格“不堆例子”，口播里每个环节只讲 1–2 条最硬的；
- 其余放在画面的时间线里，或写进简介的“参考资料”；
- 简介里的参考资料可以直接用第三节末尾的「证据」列表。

---

## 三、改好的口播稿 v1（带证据编号）

- 口播约 3000 个汉字，按每分钟 260–280 字算，约 11–11 分钟（第二章录屏时边做边说，实际会更长）。第 4 段里的 Meta、第二章的 GPT-6 可删。
- 版式沿用 Way to AGI：A 大出镜框、B 小框 + 目录、录屏放演示区。

### 注解说明

| 记号 | 含义 |
|---|---|
| `[1]`、`[9, 12, 13]` | 证据编号，用法和论文的参考文献一样：编号对应本稿最后「证据」里的同号条目，那里写着出处、日期、要点和链接。按第一次出现的顺序编号，同一个出处再出现时沿用原来的编号。**录音时不念，写字幕时不带。** |
| 没有编号的句子 | 你的亲身经历或观点，公开资料查不到，也不需要出处。 |
| 【画面】 | 画面建议。 |
| 【待确认】 | 需要你确认的事实，多是你的个人经历。 |
| 【可选】、（可删） | 可以删掉的内容。 |
| 小标题后的时间 | 这一段的估计时长。 |

### 0 开场（1:10）

【画面】A 版式；右边大字“别再用VSCode了”。

Hello，大家好，我是悠一。求求大家别再用 VS Code 写代码了！

这个视频我想做一个系列，来告诉正在搞科研的朋友、搞科研的同学，以及写代码的朋友，如何在 AI 时代更好地与 Agent 进行协作和代码开发。

这期视频我想谈一谈为什么不用 VS Code，以及不用 VS Code 之后，我们应该用什么样的新形态去开始写代码，以及如何去使用这种新的形态。

大家应该或多或少都听说过 Copilot、Cursor、Trae、Claude Code、Codex、WorkBuddy 这些名字。IDE、CLI 又是什么？
远程 SSH 连接服务器来做科研、跑实验，该用哪个？

我先说一下我的结论：写代码的主工作台，已经从代码编辑器换成了智能体。

先认识两个词，后面会一直用到：
- IDE，全称 Integrated Development Environment，集成开发环境。写代码、管文件、调试、看改动，都在一个图形界面里完成。VS Code、Cursor、Trae 都是这种带图形界面的开发工具。
- CLI，全称 Command-Line Interface，命令行界面。没有按钮，在终端里敲一行命令，它回你一段文字。平时用的 git、ssh 都是命令行工具。
- 【可选】智能体，也叫 Agent：能自己读文件、改代码、跑命令的 AI。

这两年的 AI 编程工具，基本就是在这两种界面里长出来的：一种住在 IDE 里，一种住在 CLI 里。

这期我把 AI 写代码这五年的变化捋一遍，你就知道为什么了。想直接看怎么用的，可以直接跳到第二章。

### 1 补全和聊天（1:40）

【画面】B 版式，目录“补全 → 聊天”；时间线 2021-06 / 2022-11 / 2023-12；Stack Overflow 月提问量曲线。（时间线中要出现各自app的图标）

- 2021 年 6 月，GitHub Copilot 在 VS Code 里开始预览[1]，第二年正式上线[2]。它只会一件事：你敲代码，它帮你往下补，补一行，或者补一整个函数[1]。
- 2022 年 11 月，ChatGPT 出来了[3]。那时候大家这样写代码：在聊天框里要代码，复制，粘贴到 VS Code 里跑；报错了，再把报错复制回去。网页、App、手机都一样，大家都成了“CV 工程师”。
- 这和以前在 CSDN、Stack Overflow 上抄代码，流程几乎一样，只是换了个地方抄。数据上也看得出来：Stack Overflow 的月提问量在 ChatGPT 出来后一路往下掉，到 2025 年 5 月，跌回了它 2009 年刚上线时的水平[4]。
- 2023 年底，Copilot Chat 正式可用，聊天框搬进了 VS Code 的侧边栏[5]。能问，能解释代码，但还不能自己改文件、跑命令。

这一阶段，人是主角，AI 是一个更聪明的chatbox（聊天框）。

### 2 编辑器里的智能体（2:00）

【画面】时间线 2024-11 / 2025-01 / 2025-02 / 2025-07；Trae、Kiro 截图。（时间线中要出现各自app的图标）

变化从 2024 年底开始：AI 能自己动手了。

- 2024 年 11 月，Windsurf 发布，号称第一个“智能体 IDE”[6]；同一个月，Cursor 上线 Agent 模式[7]，VS Code 的 Copilot 也能一次改多个文件[8]。
- 2025 年 1 月，字节发布 Trae[9]。国际版当时免费，能用 Claude 3.5 Sonnet[10]。2 月，Copilot 也有了 Agent 模式[11]。
- 这些编辑器有个共同点：Cursor、Windsurf、Trae 都是从 VS Code 改出来的[9, 12, 13]。所以那时候的 AI，还是住在 VS Code 里。

再往后，大家嫌一轮一轮指挥 AI 太累，开始“写好需求文档，让 AI 一次做完”。

- 2025 年 7 月，Trae 推出 SOLO 模式，要邀请码[14]。我当时拿到了资格。【待确认：你是 SOLO 内测用户，还是 Trae 早期用户】
- 用法很简单：人把 PRD，也就是产品需求文档写好，AI 自己拆任务、写代码、跑起来[14]。
- 同一个月，亚马逊的 Kiro 也在推同样的思路，叫“规格驱动开发”：先出需求、设计、任务清单，再写代码[15]。

体感上，AI 的自主性一下子强了很多。人不用每一轮都告诉它做什么，定好一份文档，它一口气做完。

问题也很快出来了：
- 一次做太多，容易刹不住车，越做越偏，做出来的和 PRD 对不上。
- 任务一长就乱。那时候 Claude 已经有 20 万 token 的上下文了[16]，现在更是到了 100 万[17]。麻烦在于塞得越多，它越容易乱。2025 年 7 月有研究专门测过，18 个模型都是输入越长、表现越不稳定，这个现象叫“上下文腐烂”[18]。

### 3 终端里的智能体（1:40）

【画面】时间线 2025-02 Claude Code / 2025-04 Codex CLI / 2025-06 Gemini CLI / 2025-08 Cursor CLI；终端录屏。（时间线中要出现各自app的图标）

同一时间，另一条路线在终端里起来了。

- 2025 年 2 月，Anthropic 发布 Claude Code[19]，5 月正式上线[20]。它一开始就是个命令行工具：在终端里说一句话，它自己读代码、改文件、跑命令。
- 4 月，OpenAI 发布开源的 Codex CLI[21]。之后 Google 出了 Gemini CLI[22]，Cursor 也出了 CLI[23]。2025 年，基本每家都做了自己的终端智能体。

程序员很喜欢 CLI：
- 看起来很极客；
- 敲命令比点界面快；
- 和 git、SSH、各种脚本天然接得上。

门槛也在这：
- 各家命令不一样，换一个工具就要重新学一遍；
- 没有界面，看改动、看结果都得自己敲命令。

我自己用了一段时间 Codex 的 CLI，后来尝试了一下 Claude Code 的 CLI，发现有些命令不一样，得重新适应，用起来就卡卡的，经常打错命令。

有句话我很认同：学得快的人，会发现什么都要学；学得慢的人，会发现很多东西不用学了，因为 AI 一直在降低门槛。CLI 就是个例子，后面你会看到它的门槛怎么被抹平。

### 4 让 AI 自己验收：loop（2:30）（这里所有的操作都需要你通过代码来写演示的操作来模拟视频展示）

【画面】loop 示意：需求 → 写代码 → 跑测试 → 改 → 再测；前端 / 后端 / 数据库三块；

一次做完靠不住，那怎么办？答案是 Agent loop。

- 需求文档加测试：先写测试，再写代码，跑测试，没过就改，改完再跑。Anthropic 2025 年 4 月给 Claude Code 写的官方最佳实践，推荐的就是这个流程[24]。
- 大 loop 里套小 loop，每个小 loop 都在调工具、跑命令。人不用中途盯着，最后验收就行。这样 AI 能把一个 demo 做到八九成。
- 2025 年 11 月，Anthropic 公开了让 AI 做长任务的办法，这类任务要跑好几个小时，甚至好几天：先把需求拆成一张功能清单，每次只做一项，做完用浏览器自动测一遍，写进度文件，下一轮接着做[25]。这就是“PRD 加测试”的 loop。

早期卡在前端：
- 那时候流行前后端分开写两个 PRD，最后人来联调。
- 一联调就发现，AI 写的前端经常点不动。管理系统这类东西，数据要在浏览器里点、要输入，后端再去查数据库有没有写对，边界条件又多。

所以浏览器控制成了关键：
- 2024 年 10 月，Anthropic 推出 computer use，模型能看屏幕、动鼠标、打字[26]。
- 11 月，Anthropic 发布 MCP，一个让 AI 连外部工具的标准接口[27]。2025 年 3 月，微软基于它出了 Playwright MCP，AI 可以直接操作浏览器做测试[28]。
- 2026 年 3 月，GPT-5.4 在 OSWorld 上拿到 75%，人类基线是 72.4%[29]。准确率已经追上人了。速度还差：2025 年的研究发现，最好的智能体要比必要的步骤多走 2.7 到 4.3 倍，人几分钟的事它要几十分钟[30]。
- 大公司已经在收集人操作电脑的数据来训练这个能力。Meta 今年 4 月开始，在美国员工的工作电脑上记录鼠标、键盘和部分截图[31]，6 月因为数据在公司内部泄露暂停了[32]。（可删）

浏览器跑通以后，前端、后端、数据库就能连起来测。云上的服务，只要你敢给权限，它也能测。

我最近在做一个微信小程序：数据库用腾讯的 CloudBase，后端是微信云函数，前端在本地跑。把这些命令告诉 AI，它能自己把测试跑完。【待确认：技术名词】

### 5 以智能体为中心的桌面工作台（3:00）

【画面】行业趋同时间线：2025-10 Cursor 2.0 → 2025-11 Antigravity → Claude Code 桌面版 → 2026-02 Codex App → 2026-06 Copilot App / Devin Desktop / TRAE Work；之后是 Claude Code 桌面版录屏。（时间线中要出现各自app的图标）

为什么 2025 年底开始，各家都改界面？因为 AI 能独立干的活越来越长。
- 有个研究机构叫 METR，专门测这个。他们的结论是：AI 能独立完成的任务长度，大约每 7 个月翻一倍[33]，2023 年以后更快，大概 4 个月翻一倍[34]。
- 写代码本身也已经很强了。今年 2 月，Anthropic 让 16 个 Claude 并行干活，写出了一个能编译 Linux 内核的 C 编译器，大约 10 万行代码[35]。
- 很多人已经不怎么看代码了，靠说。2025 年 2 月，Karpathy 提了个词叫 vibe coding：用语音输入，改动全部接受，diff 都不看[36]。做个 demo 可以这么干，做研究不行，后面说为什么。

所以界面跟着变了：
- 2025 年 10 月，Cursor 2.0 把界面换成以智能体为中心，能同时跑好几个智能体[37]。
- 11 月，Google 发布 Antigravity，专门有一个视图用来同时管多个智能体[38]。
- Claude Code 有了桌面版[39]，2026 年 2 月 Codex 出了桌面 App[40]。
- 今年 6 月，GitHub 出了 Copilot 桌面 App[41]；Windsurf 改名 Devin Desktop，打开默认就是智能体控制台[42]；字节把 Trae 拆成了 TraeCode 和 TRAE Work[43, 44]。

编辑器还在，只是退到了第二层。

### 6 AI 走出编辑器：替你干活（1:40）

【画面】OpenClaw 的 GitHub 星数、“养龙虾”新闻截图、WorkBuddy / TRAE Work / 豆包 Work 的界面。

今年 Agent 这么火，离不开 OpenClaw 的出现。

- 2026 年 1 月，Anthropic 推出 Cowork，把 Claude Code 这套能力给不写代码的人用[45]。
- 几乎同时，开源项目 OpenClaw 爆火。它装在你自己的电脑上，你在 Telegram、WhatsApp 这类聊天软件里发一句话，它就在电脑上替你干活；它能记住之前的事，还会自己连续执行任务[46, 47]。到 3 月初，GitHub 上有 24 万多星[46]，现在已经超过 39 万星[48]。国内叫它“养龙虾”[47]。
- 2 月，OpenClaw 的作者加入了 OpenAI[49]。
- 国内也跟上了：3 月腾讯出了 WorkBuddy[50]；6 月字节把 TRAE SOLO 改名 TRAE Work[43]；8 月又出了豆包 Work[51]。
- 9 月，Anthropic 宣布把 Cowork 并进 Claude 的主界面[52]。

方向很清楚：AI 从帮你写代码，变成替你干活。

风险也很清楚：
- 2 月，安全公司在 OpenClaw 的技能市场里查出几百个恶意技能，会偷你电脑上的账号密码[53]。
- 3 月，工信部专门发了风险提示：默认配置很容易被攻击、泄露信息[47]。

给 AI 的权限越大，出事的代价越大。

### 7 第二章：Claude Code 桌面版实操（录屏）

这里开始是第二章节，在上面时间线介绍之后，这里我会进行录屏展示

下面拿 Claude Code 桌面版演示，Codex 桌面版思路差不多。【画面：录屏逐项演示】
1. 同时开好几个会话。每个会话可以有自己的 Git worktree，互不干扰[39]。
2. 右边看 diff。点某一行就能写评论，写完一次提交，Claude 按评论改。也能用 @ 引用文件[39]。【待确认：你说的“在右侧 @ Claude”是不是这个功能】
3. 内置终端和浏览器：它能自己起服务、打开页面点一遍。生成的 PDF、HTML 也直接在右边打开[39]。
4. 善用 HTML 可视化。想知道 AI 改了什么，或者自己哪里没看懂，我一般让 AI 写一个 HTML 页面，把内容画出来，在右边的浏览器里直接打开[39]。
   原因很简单：同一件事，给我一段文字和一张图，我肯定先看图。图有颜色，字有大有小、有主有次，一眼就能抓到它想说什么。
   【画面】录一段：让 Claude 把刚才的改动做成一页 HTML（改了哪些文件、流程图、改前改后对比），在右边打开。
5. 权限分几档[54]：
   - Manual：每一步都问你；
   - Accept edits：改文件不问；
   - Plan：只出方案，不动代码；
   - Auto：由另一个模型替你审批；
   - Bypass：全放开，要先在设置里打开开关。
6. SSH：在环境里添加一个 SSH 连接，它会在服务器上装好 Claude Code，直接在实验室服务器上干活。注意两点：服务器要是 Linux 或 macOS[39]；服务器要能连上模型的 API，因为 Claude 是在服务器上跑的。Codex 桌面版也能连 SSH 主机，但要先在服务器上装好 Codex[55]。
7. Routines，定时任务，分两种[56]：
   - 本地任务：能读你的文件，但要电脑开着、App 开着；
   - 云端任务：关机也能跑，但读不到你本地的文件。
   我用本地任务定期整理项目的上下文目录：超过一个月的记录，让它移到归档。
8. computer use：直接操作你电脑上的软件。现在是研究预览，Mac 和 Windows 都有，要 Pro 或 Max，默认关着，每个 App 第一次用都要你点允许[39]。在 Windows 上，命令行版用不了 computer use[57]，这也是我推荐桌面版的一个原因。【可选：它能帮你看微信、起草回复，发不发你来点。“定时自动回复”我没法保证，建议不讲】
9. 浏览器插件 Claude in Chrome：用你浏览器的登录状态帮你查信息、比价、整理网页，也能替你发消息、下单，但这些事的责任算你的[58]。它有几条限制：不做股票交易，不绕验证码，不替你输入敏感信息；进金融网站前要你同意，成人网站和盗版网站直接拦截[58]。它默认自己审自己的操作，建议改成每一步都要你批准[58]。把登录状态交给 AI，风险要自己掂量。

【可选】今年 9 月 OpenAI 发布的 GPT-6 Astra，官方定位就是电脑操作和长任务，发布演示里在 Blender 里建了一整栋房子，再导进虚幻引擎[59]。【待确认：官方页面我打不开；社区分析是它写 Blender 的 Python 脚本，不一定是在界面上点】

一句话总结：它把前面所有东西都放进一个界面里，门槛很低，上手就能用。说它是编程软件也行，说它是办公软件也行。



### 8 结尾（0:15）

这就是 AI 写代码这五年的变化。【待确认：项目规则是“不做下期预告”；这个系列是连续的几集，要不要破例加一句“下一集讲怎么把国产模型接进 Claude Code 和 Codex”？你口述里“提示词工程之后的视频讲”那句，我先删了】

我是悠一，拜拜。

### 证据
按稿子里第一次出现的顺序编号。日期是发布日期；“读取”表示页面没有日期、写的是我查的日期。

[1] GitHub 博客《Introducing GitHub Copilot: your AI pair programmer》，2021-06-29。Copilot 在 VS Code 里技术预览，根据上下文建议整行或整个函数，背后是 OpenAI 的 Codex 模型。<https://github.blog/news-insights/product-news/introducing-github-copilot-ai-pair-programmer/>

[2] TechCrunch《Copilot, GitHub's AI-powered programming assistant, is now generally available》，2022-06-21。<https://techcrunch.com/2022/06/21/copilot-githubs-ai-powered-programming-assistant-is-now-generally-available/>

[3] OpenAI《Introducing ChatGPT》，2022-11-30。<https://openai.com/index/chatgpt/>

[4] The Pragmatic Engineer《Stack overflow is almost dead》，2025-05-15。月提问量 2014 年见顶，ChatGPT 发布后加速下滑，2025 年 5 月跌回 2009 年刚上线时的水平；数据来自 Stack Exchange Data Explorer。<https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/>

[5] TechCrunch《GitHub makes Copilot Chat generally available, letting devs ask questions about code》，2023-12-29。在 VS Code 和 Visual Studio 的侧边栏里正式可用。<https://techcrunch.com/2023/12/29/github-makes-copilot-chat-generally-available-letting-devs-ask-questions-about-code/>

[6] Hacker News 发布帖《Codeium launches Windsurf – the first agentic IDE》，2024-11-13。“第一个智能体 IDE”是 Windsurf 的自称。<https://news.ycombinator.com/item?id=42127877>

[7] Cursor 更新日志 0.43，2024-11-24。Composer 里加入早期版本的智能体，能自己挑上下文、使用终端。<https://cursor.com/changelog/0-43-x>

[8] VS Code 官方博客《Introducing Copilot Edits (preview)》，2024-11-12。在多个文件里一起改代码。<https://code.visualstudio.com/blogs/2024/11/12/introducing-copilot-edits>

[9] Visual Studio Magazine《AI-Powered Trae IDE Ships from Chinese TikTok Owner: 'It Looks To Be a Fork'》，2025-01-27。Trae 发布，看起来是 VS Code 的分叉。<https://visualstudiomagazine.com/articles/2025/01/27/ai-powered-trae-ide-ships.aspx>

[10] AIbase《Byte's New AI Programming Tool Trae is Here: Smooth Native Chinese Support with Free Access to Claude 3.5 Sonnet!》，2025-01。Trae 发布时免费提供 Claude 3.5 Sonnet。<https://www.aibase.com/news/14899>

[11] VS Code 官方博客《Introducing GitHub Copilot agent mode (preview)》，2025-02-24（GitHub 2025-02-06 宣布）。自己找上下文、改文件、跑终端命令、看报错再改。<https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode>

[12] Cursor 文档《VS Code Migration》（2026-09 读取）：“Cursor is based upon the VS Code codebase”。<https://cursor.com/docs/configuration/migrations/vscode>

[13] Maginative《Codeium launches Windsurf Editor, an Agentic Integrated Development Environment》，2024-11-13：“The editor itself is a fork of Visual Studio Code”。<https://www.maginative.com/article/codeium-launches-windsurf-editor-an-agentic-integrated-development-environment/>

[14] AIbase《Trae 2.0 Officially Upgraded with SOLO Mode》，2025-07-22。SOLO 7 月 21 日进入预览，国际版 Pro 用户可用，需要邀请码；能自己理解复杂任务、规划开发阶段、执行命令、改文件、交付完整功能。<https://www.aibase.com/news/19848>

[15] Kiro 官方博客《Introducing Kiro》，2025-07-14。亚马逊的智能体 IDE，规格驱动开发：先把需求写成用户故事，再出技术设计，再生成按顺序排好的任务。<https://kiro.dev/blog/introducing-kiro/>

[16] Anthropic《Introducing the next generation of Claude》，2024-03-04。Claude 3 全系 20 万 token 上下文。<https://www.anthropic.com/news/claude-3-family>

[17] Claude 博客《1M context is now generally available for Opus 4.6 and Sonnet 4.6》，2026-03-13。100 万 token 上下文正式可用，全程按标准价格计费。另见 Anthropic 的 Claude Opus 页面（2026-09 读取）：当前的 Claude Opus 5.5 是 100 万 token 上下文。<https://claude.com/blog/1m-context-ga>，<https://www.anthropic.com/claude/opus>

[18] Chroma《Context Rot: How Increasing Input Tokens Impacts LLM Performance》，2025-07-14。测了 18 个模型，输入越长，表现越不稳定。<https://www.trychroma.com/research/context-rot>

[19] Anthropic《Claude 3.7 Sonnet and Claude Code》，2025-02-24。Claude Code 有限研究预览，在终端里把工程任务交给 Claude。<https://www.anthropic.com/news/claude-3-7-sonnet>

[20] Anthropic《Introducing Claude 4》，2025-05-22。Claude Code 正式可用。<https://www.anthropic.com/news/claude-4>

[21] Slashdot《OpenAI Debuts Codex CLI, an Open Source Coding Tool For Terminals》，2025-04-16。另见 GitHub 仓库 openai/codex（2025-04-13 创建）。<https://developers.slashdot.org/story/25/04/16/1931240/openai-debuts-codex-cli-an-open-source-coding-tool-for-terminals>，<https://github.com/openai/codex>

[22] Google 博客《Google announces Gemini CLI: your open-source AI agent》，2025-06-25。开源；个人账号免费，每天 1000 次。<https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-cli-open-source-ai-agent/>

[23] Cursor 论坛《Cursor CLI - Beta Available Now!》，2025-08-07。<https://forum.cursor.com/t/cursor-cli-beta-available-now/126964>

[24] Anthropic《Claude Code: Best practices for agentic coding》，2025-04。推荐测试驱动：先写测试、确认失败、再写代码直到通过。原链接现在跳转到新版官方文档《Best practices for Claude Code》，第一条就是“给 Claude 一个它能自己跑的检查”。发布时间见 Simon Willison 2025-04-19 的同名帖；测试驱动的原文要点见 NYU 上海 2025-06-19 的整理。<https://code.claude.com/docs/en/best-practices>，<https://simonwillison.net/2025/Apr/19/claude-code-best-practices/>，<https://rits.shanghai.nyu.edu/ai/unlocking-efficiency-best-practices-for-agentic-coding-with-claude-code/>

[25] Anthropic《Effective harnesses for long-running agents》，2025-11-26。面向“跨几小时甚至几天”的任务：初始化智能体先建功能清单和进度文件；编码智能体每轮只做一项；用 Puppeteer MCP 在浏览器里做端到端测试。<https://anthropic.com/engineering/effective-harnesses-for-long-running-agents>

[26] Anthropic《Developing a computer use model》，2024-10-22。computer use 公开测试：看屏幕、移动光标、点击、打字。<https://www.anthropic.com/news/developing-computer-use>

[27] Anthropic《Introducing the Model Context Protocol》，2024-11-25。<https://www.anthropic.com/news/model-context-protocol>

[28] GitHub 仓库 microsoft/playwright-mcp：2025-03-21 创建，2025-03-28 发布第一个版本；让大模型通过 MCP 操作浏览器。<https://github.com/microsoft/playwright-mcp>

[29] OpenAI《Introducing GPT-5.4》，2026-03-05。OSWorld-Verified 75.0%，人类 72.4%。<https://openai.com/index/introducing-gpt-5-4/>

[30] arXiv 2506.16042《OSWorld-Human: Benchmarking the Efficiency of Computer-Use Agents》，2025-06-19。最好的智能体比必要步骤多走 2.7–4.3 倍；人几分钟的任务，它要几十分钟。<https://arxiv.org/abs/2506.16042>

[31] TechCrunch《Meta will record employees' keystrokes and use it to train its AI models》，2026-04-21。<https://techcrunch.com/2026/04/21/meta-will-record-employees-keystrokes-and-use-it-to-train-its-ai-models/>

[32] Engadget《Meta is 'pausing' employee tracking program after it let the whole company see sensitive data》，2026-06。<https://www.engadget.com/2199458/meta-is-pausing-employee-tracking-program-after-it-let-the-whole-company-see-sensitive-data/>

[33] METR《Measuring AI Ability to Complete Long Tasks》，2025-03-19。2019–2024 年，AI 能完成的任务长度约每 7 个月翻一倍。<https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/>

[34] METR《Time Horizon 1.1》，2026-01-29。2023 年以后，翻倍时间约 130.8 天（约 4.3 个月）。<https://metr.org/blog/2026-1-29-time-horizon-1-1/>

[35] Anthropic《Building a C compiler with a team of parallel Claudes》，2026-02-05。16 个 Claude 并行，近 2000 个会话，约 2 万美元 API 费用，写出约 10 万行的 C 编译器，能编译 Linux 6.9。<https://www.anthropic.com/engineering/building-c-compiler>

[36] 维基百科《Vibe coding》。Karpathy 2025-02-02 提出：改动全部接受、不看 diff、用 SuperWhisper 语音输入；2025-11-06 被选为柯林斯词典年度词。<https://en.wikipedia.org/wiki/Vibe_coding>

[37] Cursor 官方博客《Introducing Cursor 2.0 and Composer》，2025-10-29。界面“围绕智能体而不是文件”；多个智能体并行，互不干扰（git worktree 或远程机器）。<https://cursor.com/blog/2-0>

[38] Google《Introducing Google Antigravity》，2025-11-18。Manager 界面是“生成、编排、观察多个智能体的控制台”；另有编辑器视图。<https://antigravity.google/blog/introducing-google-antigravity>

[39] Claude Code 官方文档《Desktop application》（2026-09 读取）。并行会话和 Git worktree；diff 上逐行评论；@ 引用文件；集成终端；Browser 面板（预览应用；HTML、PDF、图片、视频文件在这里打开）；SSH 会话（远程须是 Linux 或 macOS，首次连接自动装好 Claude Code）；computer use（Mac 和 Windows 研究预览，Pro / Max，默认关闭，每个 App 首次使用要批准）。<https://code.claude.com/docs/en/desktop>

[40] OpenAI《Introducing the Codex app》，2026-02-02。<https://openai.com/index/introducing-the-codex-app/>

[41] GitHub 博客《GitHub Copilot app: The agent-native desktop experience》，2026-06-02。技术预览，给现有 Copilot Pro、Pro+、Business、Enterprise 用户；每个会话一个 git worktree，并行运行。<https://github.blog/news-insights/product-news/github-copilot-app-the-agent-native-desktop-experience/>

[42] Digital Applied《Windsurf Is Now Devin Desktop: What Users Should Do》，2026-06。Cognition 2026-06-02 宣布更名，默认界面换成 Agent Command Center。<https://www.digitalapplied.com/blog/windsurf-becomes-devin-desktop-ide-migration-2026>

[43] TRAE 官方博客，2026-06-09：“TRAE SOLO officially evolves into TRAE Work”。<https://www.trae.ai/blog/trae_work_0609>

[44] TRAE 文档《What is TraeCode?》；TRAE 论坛《TRAE IDE 品牌即将升级为 TRAECode》，2026-08-04。<https://docs.trae.ai/ide/what-is-trae?_lang=en>，<https://forum.trae.cn/t/topic/173667>

[45] TechCrunch《Anthropic's new Cowork tool offers Claude Code without the code》，2026-01-12。<https://techcrunch.com/2026/01/12/anthropics-new-cowork-tool-offers-claude-code-without-the-code/>

[46] 维基百科《OpenClaw》（2026-09 读取）。2025-11-24 首次发布；2026-01-27 改名 Moltbot，01-30 改名 OpenClaw；自主运行的开源智能体，通过 Signal、Telegram、Discord、WhatsApp 使用，数据存在本地；2026-03-02 时 24.7 万星。<https://en.wikipedia.org/wiki/OpenClaw>

[47] 观察者网《工信部：“养龙虾”，建议“六要六不要”》，2026-03-11；中新网《工信部发布关于防范OpenClaw（“龙虾”）开源智能体安全风险建议》，2026-03-11。OpenClaw 能持续自主运行、自主决策、调用系统和外部资源；默认或不当配置下风险很高，容易被攻击、泄露信息。<https://www.guancha.cn/politics/2026_03_11_809684.shtml>，<https://www.chinanews.com.cn/sh/2026/03-11/10585276.shtml>

[48] GitHub 仓库 openclaw/openclaw：2025-11-24 创建；2026-09-29 查询时 390,757 星。<https://github.com/openclaw/openclaw>

[49] TechCrunch《OpenClaw creator Peter Steinberger joins OpenAI》，2026-02-15。项目转给开源基金会。<https://techcrunch.com/2026/02/15/openclaw-creator-peter-steinberger-joins-openai/>

[50] TechNode《Tencent launches OpenClaw-like workplace AI agent WorkBuddy》，2026-03-09。<https://technode.com/2026/03/09/tencent-launches-openclaw-like-workplace-ai-agent-workbuddy/>

[51] BigGo 财经：字节把 TRAE、扣子并入豆包体系，推出豆包 Work，2026-08-24/25。<https://finance.biggo.com/news/6476d4c7-5e9c-4308-ab3b-35d52407f666>

[52] VentureBeat《Anthropic is killing off Claude Cowork and folding it into Claude chat, launching Claude Docs and Claude Slides》，2026-09-16。<https://venturebeat.com/technology/anthropic-is-killing-off-cowork-and-folding-it-into-claude-launching-claude-docs-and-claude-slides>

[53] The Hacker News《Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users》，2026-02。在技能市场 ClawHub 的 2857 个技能里查出 341 个恶意技能，会装窃密木马、偷凭证。<https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html>

[54] Claude Code 官方文档《Choose a permission mode》（2026-09 读取）。Manual、Accept edits、Plan、Auto（由另一个分类器模型代替你审批）、Bypass permissions（桌面版要先在设置里打开开关）；命令行还有 dontAsk。<https://code.claude.com/docs/en/permission-modes>

[55] OpenAI Codex 文档《Remote connections》（2026-09 读取）。在 SSH 配置里加主机；远程主机上要先装好并登录 Codex；在 Settings > Connections 里启用。<https://developers.openai.com/codex/remote-connections>

[56] Claude Code 官方文档《Schedule recurring tasks in Claude Code Desktop》（2026-09 读取）。本地任务在你电脑上跑、能读本地文件，但要 App 开着、电脑醒着；云端 routine 关机也能跑，但用的是新克隆的仓库，读不到本地文件，最短间隔 1 小时。<https://code.claude.com/docs/en/desktop-scheduled-tasks>

[57] Claude Code 官方文档《Let Claude use your computer from the CLI》（2026-09 读取）。命令行版 computer use 只支持 macOS；Windows 上要用桌面版。<https://code.claude.com/docs/en/computer-use>

[58] Claude 帮助中心《Use Claude in Chrome safely》，2026-08-12 更新。访问金融网站前要你同意；不做股票和投资交易、不绕验证码、不输入敏感数据、不抓取人脸；成人网站和已知盗版网站拦截；侧边栏默认“自动批准”（Claude 自己审查动作），可改成“手动批准”；它发布的内容、发出的消息、下的单和交易，责任在用户。<https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely>

[59] RuntimeWire《OpenAI launches GPT-6 Astra with a Blender-to-Unreal computer-use demo》，2026-09。9 月 3 日开始向部分机构推出，定位电脑操作和长任务。OpenAI 官方页面 <https://openai.com/index/gpt-6-astra/> 返回 403，没读到；OpenAI 开发者社区的帖子分析，演示是写 Blender 的 Python 脚本。<https://runtimewire.com/article/gpt-6-astra-blender-scene-control-stefan-vaskevich>，<https://community.openai.com/t/how-does-gpt-6-actually-generate-3d-models-in-release-demo-via-codex-local-blender-or-mcps-apis/1395391>

---

## 四、字幕括号注释候选（约每分钟一条，最后按字幕规范挑）

- CV 工程师（Ctrl+C / Ctrl+V 复制粘贴）
- PRD（产品需求文档）
- 规格驱动开发（先写需求和设计 再写代码）
- 上下文腐烂（输入越长 表现越不稳定）
- CLI（命令行界面）
- loop（写代码 跑测试 修改的循环）
- MCP（AI 连接外部工具的标准接口）
- computer use（让 AI 操作电脑）
- OSWorld（测 AI 操作电脑的基准）
- METR（测 AI 能力的研究机构）
- vibe coding（凭感觉让 AI 写 不看代码）
- worktree（同一仓库的独立工作副本）
- OpenClaw（开源 AI 智能体）
- PaperBench（测 AI 复现论文的基准）

---

## 五、待你确认

1. 【插曲已删，不用再确认】**个人迁徙**：Claude Code CLI → Codex → Trae → Windsurf → Cursor 的先后和时间，用账单或邮件核对。
   - 按公开事件，Trae 下架 Claude 是 2025-11，那之后 Windsurf 是能用 Claude 的；
   - 你说“Windsurf 也用不了 Claude”，对上的公开事件是 2025-06，早于 Trae 下架。两者要理顺。
2. **SOLO 内测资格** / “Trae 第一批内测用户”：Trae 2025-01 是公开发布的，没查到内测记录。
3. 【插曲已删，不用再确认】**Cursor“Plus 额度翻倍”** 是什么活动。
4. **“在右侧 @ Claude”** 指哪个功能：我按 diff 评论 + @ 引用文件写的。
5. **微信定时回复**：建议不讲，或改成“起草、你来点发送”。
6. **GPT-6 那段**：保留还是删。
7. **下期预告**：项目规则不做；这个系列要不要破例。
8. **微信小程序那段的技术名词**。
9. **封面**：保留“别再用VSCode了”，还是改成“别再把 VS Code 当主力”。
10. **原第 8 段删掉以后**：PaperBench、METR 随机对照实验、Stack Overflow 调查、OpenAI harness engineering、Anthropic 经济指数都不在稿子里了。这期对研究生的落点和“验收不能交出去”的提醒没了，要不要在第二章或结尾补一两句？
11. **第 4 段的代码演示**：你在标题里写了“所有操作都用代码写演示来模拟”。我准备按这个顺序做：写测试 → 测试失败 → 改代码 → 测试通过 → 浏览器自动点一遍 → 查数据库。要调整就告诉我。

## 六、来源（时间线和证据链表用；稿子里的出处见第三节末尾的「证据」）

**补全与聊天**
- [GitHub 博客：Introducing GitHub Copilot](https://github.blog/news-insights/product-news/introducing-github-copilot-ai-pair-programmer/)
- [TechCrunch：Copilot 正式可用](https://techcrunch.com/2022/06/21/copilot-githubs-ai-powered-programming-assistant-is-now-generally-available/)
- [TechCrunch：Copilot Chat 正式可用](https://techcrunch.com/2023/12/29/github-makes-copilot-chat-generally-available-letting-devs-ask-questions-about-code/)
- [The Pragmatic Engineer：Stack Overflow is almost dead](https://blog.pragmaticengineer.com/stack-overflow-is-almost-dead/)

**编辑器里的智能体与需求驱动**
- [VS Code：Copilot Edits](https://code.visualstudio.com/blogs/2024/11/12/introducing-copilot-edits)
- [VS Code：Copilot Agent 模式](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)
- [Maginative：Windsurf 发布](https://www.maginative.com/article/codeium-launches-windsurf-editor-an-agentic-integrated-development-environment/)
- [Cursor 文档：基于 VS Code 代码库](https://cursor.com/docs/configuration/migrations/vscode)
- [Visual Studio Magazine：Trae 发布](https://visualstudiomagazine.com/articles/2025/01/27/ai-powered-trae-ide-ships.aspx)
- [AIbase：Trae 2.0 SOLO](https://www.aibase.com/news/19848)
- [Kiro：Introducing Kiro](https://kiro.dev/blog/introducing-kiro/)
- [Chroma：Context Rot](https://www.trychroma.com/research/context-rot)
- [维基百科：Vibe coding](https://en.wikipedia.org/wiki/Vibe_coding)

**终端与云端智能体**
- [Anthropic：Claude 3.7 Sonnet 与 Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet)
- [Slashdot：Codex CLI](https://developers.slashdot.org/story/25/04/16/1931240/openai-debuts-codex-cli-an-open-source-coding-tool-for-terminals)
- [OpenAI：Introducing Codex](https://openai.com/index/introducing-codex/)
- [TechCrunch：Gemini CLI](https://techcrunch.com/2025/06/25/google-unveils-gemini-cli-an-open-source-ai-tool-for-terminals/)
- [Cursor 论坛：CLI beta](https://forum.cursor.com/t/cursor-cli-beta-available-now/126964)
- [GitHub Changelog：Copilot coding agent](https://github.blog/changelog/2025-05-19-github-copilot-coding-agent-in-public-preview/)

**基础设施与 loop**
- [Anthropic：computer use](https://www.anthropic.com/news/developing-computer-use)
- [Anthropic：MCP](https://www.anthropic.com/news/model-context-protocol)
- [MCP 博客：加入 AAIF](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/)
- [GitHub：microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)
- [TechCrunch：Operator](https://techcrunch.com/2025/01/23/openai-launches-operator-an-ai-agent-that-performs-tasks-autonomously/)
- [Simon Willison：Claude Code 最佳实践](https://simonwillison.net/2025/Apr/19/claude-code-best-practices/)
- [AGENTS.md](https://agents.md/)
- [SiliconANGLE：Agent Skills 开放标准](https://siliconangle.com/2025/12/18/anthropic-makes-agent-skills-open-standard/)
- [VentureBeat：Claude for Chrome](https://venturebeat.com/infrastructure/anthropic-launches-claude-for-chrome-in-limited-beta-but-prompt-injection-attacks-remain-a-major-concern)
- [Anthropic：长时间运行智能体的做法](https://anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [The Register：Ralph Wiggum loop](https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/)
- [Anthropic：16 个 Claude 写 C 编译器](https://www.anthropic.com/engineering/building-c-compiler)
- [OpenAI：Harness engineering](https://openai.com/index/harness-engineering/)（[InfoQ 报道](https://www.infoq.com/news/2026/02/openai-harness-engineering-codex/)）
- [OpenAI：GPT-5.4](https://openai.com/index/introducing-gpt-5-4/)
- [arXiv：OSWorld-Human](https://arxiv.org/abs/2506.16042)
- [Claude：100 万上下文正式可用](https://claude.com/blog/1m-context-ga)

**模型断供**
- [Forbes：Anthropic 切断 Windsurf](https://www.forbes.com/sites/johanmoreno/2025/06/05/anthropic-cuts-windsurfs-claude-access-before-openai-acquisition/)
- [VentureBeat：Windsurf 恢复](https://venturebeat.com/programming-development/remaining-windsurf-team-and-tech-acquired-by-cognition-makers-of-devin-were-friends-with-anthropic-again)
- [Tom's Hardware：Anthropic 新条款](https://www.tomshardware.com/tech-industry/anthropic-blocks-chinese-firms-from-claude)
- [Yahoo / SCMP：Trae 下架 Claude](https://tech.yahoo.com/ai/claude/articles/tech-war-bytedance-cuts-off-093000669.html)
- [TechCrunch：Cognition 收购 Windsurf](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/)
- [Anthropic：不支持地区的销售限制](https://www.anthropic.com/news/updating-restrictions-of-sales-to-unsupported-regions)
- [Cursor：Ultra 和 Pro](https://cursor.com/blog/new-tier)

**桌面工作台**
- [Cursor 2.0](https://cursor.com/blog/2-0)
- [Google Antigravity](https://antigravity.google/blog/introducing-google-antigravity)
- [Claude Code 桌面版文档](https://code.claude.com/docs/en/desktop)
- [权限模式](https://code.claude.com/docs/en/permission-modes)
- [定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)
- [命令行版 computer use](https://code.claude.com/docs/en/computer-use)
- [Claude in Chrome 安全说明](https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely)
- [OpenAI：Codex App](https://openai.com/index/introducing-the-codex-app/)
- [Codex 远程连接文档](https://developers.openai.com/codex/remote-connections)
- [GitHub 博客：Copilot App](https://github.blog/news-insights/product-news/github-copilot-app-the-agent-native-desktop-experience/)
- [Devin Desktop 更名](https://www.digitalapplied.com/blog/windsurf-becomes-devin-desktop-ide-migration-2026)
- [TRAE 文档：TraeCode](https://docs.trae.ai/ide/what-is-trae?_lang=en)
- [BigGo：字节 8 月重组](https://finance.biggo.com/news/6476d4c7-5e9c-4308-ab3b-35d52407f666)

**替你干活、OpenClaw 与风险**
- [VentureBeat：Cowork 并入 Claude](https://venturebeat.com/technology/anthropic-is-killing-off-cowork-and-folding-it-into-claude-launching-claude-docs-and-claude-slides)
- [维基百科：OpenClaw](https://en.wikipedia.org/wiki/OpenClaw)
- [TechCrunch：作者加入 OpenAI](https://techcrunch.com/2026/02/15/openclaw-creator-peter-steinberger-joins-openai/)
- [The Hacker News：341 个恶意技能](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
- [中新网：工信部风险防范建议](https://www.chinanews.com.cn/sh/2026/03-11/10585276.shtml)
- [观察者网：CNCERT 提示](https://www.guancha.cn/industry-science/2026_03_10_809530.shtml)
- [TechNode：WorkBuddy](https://technode.com/2026/03/09/tencent-launches-openclaw-like-workplace-ai-agent-workbuddy/)
- [TechCrunch：Meta 记录员工键盘](https://techcrunch.com/2026/04/21/meta-will-record-employees-keystrokes-and-use-it-to-train-its-ai-models/)
- [Engadget：Meta 暂停](https://www.engadget.com/2199458/meta-is-pausing-employee-tracking-program-after-it-let-the-whole-company-see-sensitive-data/)
- [RuntimeWire：GPT-6 Astra](https://runtimewire.com/article/gpt-6-astra-blender-scene-control-stefan-vaskevich)

**能力、分工与反方证据**
- [METR：任务时长](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)（[Time Horizon 1.1](https://metr.org/blog/2026-1-29-time-horizon-1-1/)）
- [OpenAI：为什么不再用 SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)（2026-02-23；原来这里引的是 Claude Opus 4.5 在 SWE-bench Verified 上的 80.9%，已不再使用）
- [Anthropic 经济指数：软件开发](https://www.anthropic.com/news/impact-software-development)
- [METR：随机对照实验](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [Stack Overflow 2025 调查新闻稿](https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/)（[AI 部分原始数据](https://survey.stackoverflow.co/2025/ai)）
- [arXiv：PaperBench](https://arxiv.org/abs/2504.01848)

## 核对的局限

- **第三次修改（复查用户改过的稿子）**：
  - 用户删了插曲和原第 8 段，桌面版演示挪到第 6 段后面，原来的编号出现两个问题：[23]–[28]、[65]–[69] 共 11 条在正文里没人引用了；[50]–[55] 排在 [56]–[64] 后面才出现，不再符合“按首次出现编号”。已用脚本重排，11 条的出处留在第六节。
  - “现在是 1M 一千万的上下文”：1M 是一百万，已改；补了 Claude 官方博客（2026-03-13 正式可用）和 Claude Opus 页面（Opus 5.5 是 100 万）做出处。
  - “人对图像的接收程度会高于文字”：稿子里改成了“我肯定先看图”这种个人说法，不需要出处。想保留一般性的说法，可以引“图优效应”（图片比文字更容易被记住），别用“大脑处理图像比文字快 6 万倍”：那个数字没有研究出处。

- **第二次修改时的更正**（重新逐条读一手来源时发现）：
  - **Claude in Chrome 的限制**：第一版照第三方文章写了“不能付款、不能注册账号、不碰银行卡和证件、金融网站默认进不去”，和官方帮助页（2026-08-12 更新）不符。官方写的是：访问金融网站前要你同意；不做股票和投资交易、不绕验证码、不输入敏感数据、不抓取人脸；成人和盗版网站拦截；它发的消息、下的单，责任在用户。稿子已按官方改；上一份核对记录（191823）里的同一条也已更正。你原稿说它能订酒店、回评论，大体成立。
  - **Stack Overflow 调查**：第一版把两个数字记反了。原始数据是 66% 说最大的困扰是“差一点就对”，45.2% 说“调 AI 写的代码更费时间”。
  - **SWE-bench Verified**：OpenAI 2026-02-23 公开说这个基准已被训练数据污染、不少测试有问题，不再拿它比前沿代码能力。稿子里“Opus 4.5 超过 80%”换成了 16 个 Claude 写 C 编译器。
- 其他：
  - Anthropic 2025-04 的最佳实践原文链接现在跳转到新版文档；原文的发布时间和测试驱动要点，是靠 Simon Willison 和 NYU 上海的转载间接确认的（Wayback 我这边访问不了）。
  - “Cursor 是 VS Code 分叉”：维基百科没写，改用 Cursor 官方文档“based upon the VS Code codebase”。
  - Windsurf “第一个智能体 IDE” 是它自己的说法，出处用的是它的发布帖。

- 以下来自第三方转述，没找到一手公告：
  - Claude 桌面版 Code 标签页的上线时间和 2026-04 的大改版；
  - Devin Desktop 更名；
  - TRAE Work / TraeCode 的具体日期；
  - Codex App 的 Windows 日期。
- OpenAI 的 GPT-6 Astra 和 PaperBench 官方页面返回 403，没读到原文。PaperBench 的人类基线具体数字，没从一手来源确认，稿子里只说“还没超过”。
- OpenClaw 首发时的名字按维基百科写（Warelay → CLAWDIS → Clawdbot）；很多报道只说 Clawdbot，稿子里不讲这段。
- METR 的具体模型时长没写进稿子，只用了“翻倍时间”这个结论。
