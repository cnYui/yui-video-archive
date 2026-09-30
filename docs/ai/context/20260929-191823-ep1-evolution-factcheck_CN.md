# 第 1 期「软件演变」口述稿：事实核对、逻辑整理、稿子顺序

- 时间：2026-09-29（UTC+9），晚上。
- 起因：用户口述了第 1 期（《AI时代 计算机研究生必须掌握之一》，封面“别再用VSCode了”）想讲的“整个软件的变化”，让我整理逻辑和稿子顺序，并联网核对逻辑、事实和时间顺序，尤其是演变史。
- 结论：**论点方向对，但时间线有 4 处顺序错误、几处事实不准，核心论据“Copilot / Windsurf / Trae / Cursor 还困在侧边栏”已经过时。** 行业在 2025-10 到 2026-06 之间几乎都转向了“以智能体 / 会话为中心”的桌面工作台，所以论点要改成“工作台的中心从编辑器换成了智能体”，而不是“别用 VS Code / Copilot / Cursor”。
- 用户个人的订阅经历（Trae → Windsurf → Cursor 的先后和日期）和公开记录对不上，要用账单 / 邮件自己核对。

## 核对后的时间线（一手或可靠来源；日期为北京时间以外的公布日期）

| 日期 | 事件 |
|---|---|
| 2021-06-29 | GitHub Copilot 技术预览（VS Code，行内补全，背后是 OpenAI 的 Codex 模型） |
| 2022-06-21 | Copilot 正式可用 |
| 2022-11-30 | ChatGPT 发布（聊天框，此后出现“复制粘贴工程师”） |
| 2023-03 起 | Claude 模型系列（Claude 3.5 Sonnet 是 2024-06） |
| 2023-12-29 | Copilot Chat 正式可用（VS Code / Visual Studio 侧边栏，只能问答，不改文件） |
| 2024-11-12 | VS Code Copilot Edits 预览（多文件编辑） |
| 2025-01-19/20 | 字节 Trae 发布（基于 VS Code；国际版免费，带 Claude 3.5 Sonnet、GPT-4o） |
| 2025-02-06 / 02-24 | Copilot Agent 模式（宣布 / VS Code 官方博客） |
| **2025-02-24** | **Claude Code 研究预览**（随 Claude 3.7 Sonnet）；2025-05-22 正式可用（随 Claude 4） |
| **2025-04-16** | **Codex CLI**；2025-05-16 Codex 云端智能体研究预览 |
| 2025-06 | Cursor 计费改成用量制（Pro $20 / Pro+ $60 约 3× / Ultra $200 约 20×），07-04 CEO 道歉 |
| 2025-06-03 | Anthropic 砍掉 Windsurf 对 Claude 3.x 的直供（通知不到 5 天，起因是 OpenAI 收购传闻） |
| 2025-07-14 / 07-16 | Cognition 收购 Windsurf；07-16 恢复 Claude Sonnet 4 直供 |
| 2025-07-21 | Trae SOLO 预览（国际版 Pro，需邀请码） |
| 2025-08-07 | Cursor CLI beta |
| 2025-09-05 | Anthropic 更新条款：禁止中国控股企业使用 Claude |
| **2025-10-29** | **Cursor 2.0：界面改成以智能体为中心**，可并行多个智能体（worktree） |
| **2025-11-04/05** | **Trae 下线全部 Claude 模型**（含 Claude Sonnet 4）；补偿付费用户每月 +300 次、优先请求 +50%（到 2026-01-31） |
| 约 2025-11 | Claude 桌面版出现 Code 标签页（第三方报道，没找到一手公告） |
| 2026-01-12 | Claude Cowork 研究预览（4 月正式可用） |
| 2026-02-02 / 03-04 | Codex 桌面 App：macOS / Windows；2026-04-16 更新加入 computer use、内置浏览器、插件、自动化 |
| 2026-03-09 | 腾讯 WorkBuddy（CodeBuddy 家族的本地办公智能体） |
| 2026-04-14 | Claude Code 桌面版大改版：多会话侧栏、集成终端和文件编辑器、Git worktree 隔离、Routines |
| 2026-04-21 | Meta 宣布 Model Capability Initiative（采集美国员工电脑上的鼠标、键盘、部分截图训练 AI）；2026-06 因数据被内部泄露暂停 |
| 2026-06-02 | GitHub Copilot 桌面 App 技术预览；同日 Windsurf 更名 Devin Desktop（默认界面改成 Agent Command Center） |
| 2026-06-08 | TRAE SOLO 更名 TRAE Work；2026-08-04 TRAE IDE 品牌升级为 TraeCode；2026-08-24/25 TRAE 和 Coze 并入豆包体系，Doubao Work 上线 |
| 2026-09-03 | GPT-6 Astra 发布（先给部分机构） |
| 2026-09-16 | Anthropic 宣布把 Cowork 并入 Claude 主界面（Chat / Cowork 切换将消失）；Claude Code 保持独立 |

## 口述里的说法 → 核对结果

### A. 时间顺序错误

| 你说的 | 实际 | 怎么改 |
|---|---|---|
| ChatGPT 时代 VS Code 里还没有 AI；后来 Copilot 出现一切不一样 | Copilot 2021 年就在 VS Code 里（补全），比 ChatGPT 早一年多；2023-12 才有侧边栏聊天 | 顺序改成：补全（Copilot）→ 聊天（ChatGPT，CV 工程师）→ 聊天进侧边栏（Copilot Chat 等） |
| GPT 推出 Codex，后来出现 Claude 模型和 Claude Code | Claude 模型 2023 年就有；Claude Code（2025-02）早于 Codex CLI（2025-04）；“Codex”在 2021 年就是 Copilot 背后的模型 | 顺序：Claude Code → Codex CLI → Codex 云端 → Cursor CLI |
| 2024 年底（9 月还是 12 月）Trae 的 Claude 3.5 一夜之间下线 | Trae 2025-01 才发布；实际是 2025-11-04/05 下线（Claude Sonnet 4 等），起因是 2025-09-05 的 Anthropic 新条款 | 改日期和模型名 |
| Trae 断供之后转战 Windsurf，Windsurf 跟 OpenAI、Anthropic 关系还不错，后来也用不了 Claude | Windsurf 被断供在 2025-06（比 Trae 早），原因正是 OpenAI 收购传闻；2025-07-16 已恢复 | 用账单核对你自己的先后；讲公开事实时用上面的日期 |
| Trae SOLO（2025-07）→ 出了问题 → 再往后 Codex / Claude Code | Claude Code、Codex CLI 都比 SOLO 早 | 行业史和个人经历分开讲，别混在一条线上 |

### B. 事实不准

| 你说的 | 实际 |
|---|---|
| Cursor：Plus 额度翻倍，Pro 20 倍、200 刀 | 档位是 Pro $20 / Pro+ $60（约 3×）/ Ultra $200（约 20×）；“翻倍”活动没查到 |
| VS Code 里 Cursor 的插件 | Cursor 不是 VS Code 插件，是 VS Code 分叉出的独立 IDE（Trae、Windsurf 也是）；Codex 有 VS Code 扩展和独立 App |
| Facebook 要求监控员工鼠标 | 是 Meta；2026-04 宣布，针对美国员工的公司电脑，采集鼠标、键盘、部分截图，不能退出；2026-06 因数据泄露暂停。要用过去时并注明来源 |
| 现在用 CLI 就没法用 Computer Use | macOS 的 Claude Code CLI 已支持（研究预览，Pro / Max，`-p` 不可用）；Windows / Linux 的 CLI 不支持，Windows 上要用 Desktop |
| WorkBuddy 也从侧边栏改成了 Desktop | WorkBuddy 是腾讯 2026-03 新推的办公智能体（CodeBuddy 家族），不是“改的”；Trae Work 是 SOLO 改名；Cowork 9 月已宣布并入 Claude |
| GPT-6 用 Computer Use 去 3D 建模 | GPT-6 Astra 2026-09-03 发布（先给部分机构）；官方演示是 Blender 建模，但实现方式我没查到官方说明（openai.com 页面 403）；社区分析是无界面模式下用 Blender 的 Python 接口（bpy），不是点界面 |
| Trae 现在叫 Trae Code | 对：2026-08-04 品牌升级为 TraeCode（写法 TraeCode） |

### C. 论点过时或说得过头

| 你说的 | 实际 / 建议 |
|---|---|
| Copilot 还停留在侧边栏，Windsurf、Trae 都寄生在侧边栏 | 过时：Copilot 2026-06 有独立桌面 App；Windsurf 更名 Devin Desktop；Cursor 2.0 早在 2025-10 就换了界面；Trae 拆成 TraeCode + TraeWork |
| AI 不会再出现语法、结构报错，不需要看代码 | 语法错误少了，但研究代码的静默错误（指标算错、数据泄漏、随机种子）不会报错；要保留“验收 / 测试 / 看关键 diff” |
| 现在的人基本上都口喷 / 语音输入 | 改成“不少人” |
| SSH：在聊天框里直接连，在本地控制服务器 | Desktop 是“环境下拉 → + Add SSH connection”（user@host 或 `~/.ssh/config`）；**首次连接自动在远程机器安装 Claude Code，智能体跑在远程机器上**；远程必须是 Linux 或 macOS；所以服务器要能访问模型 API（国内实验室常常不行） |
| Routine 定时整理上下文，删除超过一个月的文档 | Desktop 的 Routines 有两类：本地定时任务（在你电脑上，能访问本地文件，但只在应用开着、电脑没睡眠时运行）和云端 routine（关机也跑，但只有新克隆的仓库，访问不了本地文件，最短 1 小时）。你的例子要用本地任务；删除建议改成“移到归档目录” |
| Desktop 用 computer use 定时回复微信 | 没查到依据，且有风险：computer use 是研究预览（macOS、Windows，仅 Pro / Max，默认关闭），逐个应用要你点允许（只在本次会话有效），无人值守的定时任务会卡在权限提示；替你发消息还涉及隐私和平台规则。改成“读消息并起草回复，由你确认发送” |
| 浏览器插件能做你在浏览器上能做的所有事情（订酒店、逛淘宝、回复评论） | “所有事情”偏大，但订酒店、回评论这类它能做。**更正（同日晚）**：这里原来写“明确禁止付款购买、创建账号、处理银行卡和证件……订酒店只能到付款前”，依据的是第三方文章，和官方帮助页不符。官方（2026-08-12 更新）：访问金融网站前要你同意；不做股票和投资交易、不绕验证码、不输入敏感数据、不抓取人脸；成人和盗版网站拦截；它发的消息、下的单，责任在用户。要提醒风险（把登录态交给智能体） |
| 权限 5 种：Auto / Manual / Accept Edit / Plan / 完全放开 | 基本对，Desktop 选择器里是 Manual（默认）、Accept edits、Plan、Auto（可用时）、Bypass permissions（要先在设置里打开开关）。Auto 是另一个分类器模型代你审批，不是“自动执行一切”。CLI 还有 dontAsk |

### D. 已核实为对

- Copilot 当时不能操作文件（2024-11 才有多文件编辑，2025-02 有 Agent 模式）。
- Trae SOLO 需要邀请码，主打“写需求文档，AI 直接开工”。
- Claude Code 是从 CLI 起家，最火的是 CLI 版；Cursor 也出过 CLI（2025-08-07）。
- Codex / Claude Code 桌面版能同时开多个项目（并行会话 + Git worktree 隔离）。
- Desktop 有集成终端、diff 审阅、内置浏览器（预览应用、打开外部网站、PDF 在右侧打开）。
- Anthropic 不让 Trae 用 Claude（准确说：不让中国控股的企业用）。

### E. 没查到、要用户自己确认

- “我是 Trae 第一批内测用户”：Trae 2025-01 是公开发布的，没查到内测名单。
- “AI 当时上下文还没那么长”：2025 年已有 20 万到 100 万 token，问题主要是长任务跑偏和上下文管理，措辞要改。
- computer use“准确度已经很强”：缺数据，建议引一个基准或去掉。
- 微信小程序“腾讯 CloudBase 数据库 + 微信云函数”：没核对技术措辞；微信云开发本身基于腾讯云 CloudBase。

## 整理后的论证链

1. AI 编程的变化，关键不在模型，而在**人和 AI 之间的界面**怎么变。
2. 补全 → 聊天（复制粘贴）→ 侧边栏聊天：人是主角，AI 是助手。
3. 编辑器里的智能体（改文件、跑命令）→ PRD 一次性做完（SOLO）→ 跑偏、上下文问题 → 需要 loop 和测试。
4. 终端智能体（Claude Code、Codex CLI）把“工具调用 + 测试循环”做到极致，但门槛高。
5. 让智能体自己验证的三块拼图：loop（PRD + TDD）、浏览器 / computer use、云端服务权限。
6. 2025-10 到 2026-06，行业转向**以智能体 / 会话为中心的桌面工作台**：Cursor 2.0、Claude Code Desktop、Codex App、Copilot App、Devin Desktop、TraeCode / TraeWork。
7. 结论：工作台的中心从“文件 / 编辑器”换成了“任务 / 会话”，人从写代码变成写需求、搭 loop、做验收。对研究生：SSH 服务器、长任务、并行实验是收益；验收、可复现、权限、密钥是风险。选哪个，看模型可用性、价格、生态和远程能力 → 引到第 2 集。

## 稿子顺序（约 12–14 分钟，第 4 段可删）

0. 开场钩子（0:30）：结论 + “别再用VSCode了”，立刻澄清“不是 VS Code 不好，是别再把它当主工作台”。
1. 补全 → 聊天（1:30）：Copilot 2021/22 → ChatGPT 2022 → CV 循环 → Copilot Chat 2023。
2. 编辑器里的智能体（2:00）：Copilot Edits / Agent、Cursor、Windsurf、Trae；SOLO 的“PRD 一次做完”和它的问题。
3. 终端智能体（2:00）：Claude Code（2025-02）、Codex CLI（2025-04）、Cursor CLI；CLI 的极客感和门槛；你自己的用法。
4. 插曲：模型供给决定工具（1:00）：Windsurf 2025-06、Anthropic 2025-09、Trae 2025-11；你的订阅迁徙（先核对日期）。
5. 让智能体自己验证（1:30）：loop、浏览器 / computer use、云端权限；微信小程序的例子。
6. 桌面智能体工作台（2:30）：行业趋同（放一张时间线图）；Claude Code Desktop 的并行会话、diff、终端、预览、权限模式、SSH、Routines、computer use 与浏览器扩展，每项配限制。
7. 回到标题（1:00）：为什么别再把 VS Code 当主工作台，以及什么时候仍要用它（调试、Jupyter、精读 diff）。
8. 研究生怎么用 + 风险（1:00）：验收、可复现、权限、密钥、服务器数据。
9. 结尾（0:20）：预告第 2 集（国产模型）。

## 需要用户确认

- 订阅迁徙的真实先后和日期（用账单 / 邮件核对）。
- 标题保留“别再用VSCode了”，还是改成“别再把 VS Code 当主工作台”。
- GPT-6 那句怎么写（建议只说“在 Blender 里建模”，并去官方页面确认）。
- 微信自动回复那段是删掉，还是改成“起草，由你确认发送”。
- “第一批内测”有没有证据。

## 来源

- Copilot：[GitHub 博客：Introducing GitHub Copilot](https://github.blog/news-insights/product-news/introducing-github-copilot-ai-pair-programmer/)、[TechCrunch 2022-06-21](https://techcrunch.com/2022/06/21/copilot-githubs-ai-powered-programming-assistant-is-now-generally-available/)、[TechCrunch 2023-12-29](https://techcrunch.com/2023/12/29/github-makes-copilot-chat-generally-available-letting-devs-ask-questions-about-code/)、[VS Code：Copilot Edits](https://code.visualstudio.com/blogs/2024/11/12/introducing-copilot-edits)、[VS Code：Agent 模式](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)、[GitHub Changelog：Copilot App](https://github.blog/changelog/2026-06-02-expanded-technical-preview-availability-for-the-github-copilot-app/)
- Claude Code：[Anthropic：Claude 3.7 Sonnet and Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet)、[桌面版文档](https://code.claude.com/docs/en/desktop)、[权限模式](https://code.claude.com/docs/en/permission-modes)、[定时任务](https://code.claude.com/docs/en/desktop-scheduled-tasks)、[CLI 的 computer use](https://code.claude.com/docs/en/computer-use)、[Claude in Chrome 安全说明](https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely)、[VentureBeat：Cowork 并入 Claude](https://venturebeat.com/technology/anthropic-is-killing-off-cowork-and-folding-it-into-claude-launching-claude-docs-and-claude-slides)
- Codex：[Slashdot：Codex CLI](https://developers.slashdot.org/story/25/04/16/1931240/openai-debuts-codex-cli-an-open-source-coding-tool-for-terminals)、[OpenAI：Introducing Codex](https://openai.com/index/introducing-codex/)、[OpenAI：Codex App](https://openai.com/index/introducing-the-codex-app/)、[Help Net Security：Codex 桌面更新](https://www.helpnetsecurity.com/2026/04/17/openai-codex-desktop-update-macos/)
- Trae：[Visual Studio Magazine 2025-01-27](https://visualstudiomagazine.com/articles/2025/01/27/ai-powered-trae-ide-ships.aspx)、[Pandaily：SOLO](https://pandaily.com/byte-dance-launches-standalone-version-of-ai-coding-tool-trae-solo)、[AIbase：Trae 2.0 SOLO](https://www.aibase.com/news/19848)、[Yahoo / SCMP 2025-11-05](https://tech.yahoo.com/ai/claude/articles/tech-war-bytedance-cuts-off-093000669.html)、[AIbase：Trae 移除 Claude](https://www.aibase.com/news/22507)、[TRAE 文档：TraeCode](https://docs.trae.ai/ide/what-is-trae?_lang=en)、[BigGo：字节 8 月重组](https://finance.biggo.com/news/6476d4c7-5e9c-4308-ab3b-35d52407f666)、[Tom's Hardware：Anthropic 新条款](https://www.tomshardware.com/tech-industry/anthropic-blocks-chinese-firms-from-claude)
- Windsurf：[Forbes 2025-06-05](https://www.forbes.com/sites/johanmoreno/2025/06/05/anthropic-cuts-windsurfs-claude-access-before-openai-acquisition/)、[TechCrunch：Cognition 收购](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/)、[VentureBeat：和 Anthropic 重归于好](https://venturebeat.com/programming-development/remaining-windsurf-team-and-tech-acquired-by-cognition-makers-of-devin-were-friends-with-anthropic-again)、[Devin Desktop 更名](https://www.digitalapplied.com/blog/windsurf-becomes-devin-desktop-ide-migration-2026)
- Cursor：[CloudZero：定价](https://www.cloudzero.com/blog/cursor-ai-pricing/)、[Cursor 2.0](https://cursor.com/blog/2-0)、[Cursor CLI beta](https://forum.cursor.com/t/cursor-cli-beta-available-now/126964)
- 其他：[TechCrunch：Meta 记录员工键盘](https://techcrunch.com/2026/04/21/meta-will-record-employees-keystrokes-and-use-it-to-train-its-ai-models/)、[Engadget：Meta 暂停](https://www.engadget.com/2199458/meta-is-pausing-employee-tracking-program-after-it-let-the-whole-company-see-sensitive-data/)、[TechNode：WorkBuddy](https://technode.com/2026/03/09/tencent-launches-openclaw-like-workplace-ai-agent-workbuddy/)、[OpenAI 社区：GPT-6 Blender 演示](https://community.openai.com/t/how-does-gpt-6-actually-generate-3d-models-in-release-demo-via-codex-local-blender-or-mcps-apis/1395391)、[RuntimeWire：GPT-6 Astra](https://runtimewire.com/article/gpt-6-astra-blender-scene-control-stefan-vaskevich)

## 核对方法的局限

- 大部分日期来自新闻报道和官方文档，个别（Claude 桌面版 Code 标签页的首次上线、Devin Desktop 更名、Windsurf 2025-07 恢复直供）来自第三方转述，没找到一手公告；口述稿定稿前建议对这几处再看一眼官方发布说明。
- OpenAI 官方 GPT-6 Astra 页面我这边返回 403，没能读到，所以那一条只能给出“待核”。
- 没有核对的：Trae 国内版的模型列表、各产品在国内的可用性和价格。
