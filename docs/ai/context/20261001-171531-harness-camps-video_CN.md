# 《请选择你的AI Harness 框架阵营》——仿“请选择你的 AI 模型主义”的踩点短视频

日期：2026-10-01。目录：`独立视频/2026-10_请选择你的AI-Harness框架阵营/`。

## 用户要求（按时间）

1. 给了一个 B 站短视频（`C:\Users\yui\Downloads\42206955376-1-192.mp4`，cid 42206955376，UP 主水印“进击の范进”，视频是《请选择你的 AI 模型主义》一类）：“想像这个视频一样做一个类似的视频，就是‘请选择你的 AI 框架主义’。你也写一段相似的文本，找一些比如说 Claude Code、DeepSeek Desktop 这样的配图和文字，然后做一个类似的视频。你可以抽帧来看一下他这个视频怎么做的，而且还要有相同的 BGM。”
2. 改标题：“或者说，修改标题为‘请选择你的AI Harness 框架阵营’”。
3. “这是短视频，没有原声”。
4. “你可以直接使用它的 BGM 和音轨，再加上你设计的、像 PPT 一样卡点的播放视频就可以了，这样你就完成这个任务了。”

→ 范围：**音轨直接用原视频的**（原视频没有人声，只有 BGM，不用配音）；画面自己设计，一页一页翻，翻页卡在节拍上。

## 参考视频分析（2026-10-01）

- 1280×720、30 fps、139.2 s；音轨 AAC 44.1 kHz 立体声；**没有人声**（Silero VAD 在默认阈值下 0 段；Whisper 只吐出一句“中文字幕 李宗盛”，是纯音乐上的典型幻觉）。
- 画面：约 18 页“××主义”，每页纯色底（橙、藏青、白、黑、绿、暗红、紫、黄……），**左边 logo + 型号名，右边大标题 + 一段“他们……”的说明 + 偶尔一句引号外号**（“六边形战士”“金钱的力量”“术业有专攻”……）。同一页里有 2–3 个 logo 时，上下推移轮换；开源 / 闭源两页是 4 个 / 3 个 logo 同屏。右上角的“进击の范进 bilibili”是下载时加的水印，不是画面的一部分，**不要照搬**。
- 转场（逐帧看过）：页内换 logo = 旧的上滑出、新的从下方升起，约 0.8 s；整页切换 = 旧内容淡出 → 底色渐变到新色 → 新内容从左上方滑入落位，约 1 s。
- 页长 4–10 s 不等，**翻页只是大致踩点**（起点和拍点偏差最多约 1.5 拍），不是严格卡点。最后 2:12.5 起黑屏到 2:19，音乐收尾淡出。
- 抽帧、拼图、逐帧差分在 `参考分析/`（f1、sheets、tr、ref_transitions.py）；该目录被 .gitignore 忽略。

## BGM 分析（`参考分析/beat_grid.py`、`analyze_bgm.py`）

- **精确 130.000 BPM**（一拍 0.461538 s，一小节 1.846 s，4 小节 = 16 拍 = 7.385 s）。
- **第 0 拍在 0.503 s**。⚠ 第一次拟合（全频段起音）锁在了反拍上，得到 0.271 s，差半拍；改用低频起音 + 实测鼓点进入时刻校正：实测鼓点进入在 15.24 / 44.78 / 89.12 / 118.66 s，对应 `0.503 + k×0.4615` 的 k = 32 / 96 / 192 / 256（误差 ≤ 30 ms）。**以后凡是用这条 BGM，t0 都用 0.503。**
- 曲子结构（拍序号 k，一小节 = 4 拍）：
  - k 0–31（0.5–15.3 s）：前奏 8 小节，轻；
  - **k 32 鼓点进入 1**（15.27 s）；k 60–63 过门（电平降低）；
  - k 64–95（30.0–44.8 s）：过渡段，低音下滑，k 80 起上升音扫；**k 92–96 整整一小节静音空档**（42.97–44.81 s）；
  - **k 96 鼓点进入 2**（44.81 s），k 128 加层；
  - k 160–191（73.9–88.7 s）：长低谷（−33 dBFS 左右），末尾上升；
  - **k 192 鼓点进入 3**（89.12 s），k 224 加层；
  - **k 256**（118.66 s）最后一段；k 284–287 过门；**k 288 最后一击**（133.42 s），之后是混响尾巴，淡出到 139.2 s。
- 整首 = 72 小节 = **1 张标题页（k 0–15）+ 17 张阵营页（每页 4 小节，k 16–287）+ 收尾页（k 288 起）**，所有段落边界都落在 16 拍的整数倍上。

## 设计（版式、动画、卡点）

- 画面 2340×1080、30 fps（用户的统一画幅），渲染用 Playwright Chromium 逐帧截图（`制作/engine/index.html` + `制作/render_frames.py`），编码用 `制作/encode.py`（PNG 序列 + 原 AAC 直拷，`-filter_threads 1`）。
- 版式照参考：纯色底、左 logo（白色圆角瓦片，下面写产品名）、右标题 / 说明 / 引号外号；内容以画面中线 x = 1170 居中；底部 16 格节拍条（每拍亮一格）。
- 卡点规则：
  - 每页 16 拍，**新页在小节第 1 拍落位**（推入动画 [t−0.25 s, t+0.05 s]，ease-out，落在拍点上）；
  - 第 1 拍标题“盖章”（缩小落位 + 过冲），第 2 拍 logo 弹出，第 3 拍起说明每拍出一行，最后一拍出引号外号；多 logo 页在第 6 / 8 / 11 拍上推轮换；
  - 鼓点进入（k 32 / 96 / 192 / 256 / 288）加一下闪白和推近；
  - k 92–96 的静音空档：“权限主义”页压暗，弹出终端式确认框，第 95 拍打出 y，鼓点进入时翻到“放飞主义”。
- 同步校验：`制作/verify_sync.py`（成片音轨和参考音轨互相关 + 逐帧找每页落位）。小样（5 s）实测音轨偏移 +0 ms。

## 踩过的坑

- 节拍网格第一次拟合差半拍（见上）。**用多种方法交叉验证**：低频起音、鼓点进入的实测时刻、整数拍落点。
- 引擎里“垂直居中”必须在元素显示状态下量（`display:none` 时 `offsetHeight` = 0），否则文字列掉到画面下半部分。
- 写命令时别按进程名杀进程：我写过一条 `taskkill /IM python.exe`，匹配范围是所有 Python，可能误伤别的会话（实际看起来没有杀到，但不该这么写）。只按 PID 杀自己的。
- 在工作树目录里 `cd` 会让会话以为“当前目录就是那个工作树”，读完别人工作树里的文件要 `cd` 回 `D:\大疆`。
- 改目录名前先确认没有 shell 的当前目录在里面（Windows 下会“Permission denied”）。

## 内容方向的两次改动

1. **v1（作废）按类别分**：终端主义 / IDE主义 / 桌面主义 / 放飞主义……每页放 2–3 个产品。用户否掉：“放飞主义是什么”“给我你的文稿”，随后：“**不要，单独的分开来，每个公司你根据特点像一个主义**，比如 claude code 就是一个 xx 主义，然后是 codex，然后是 deepseek harness，然后是 openclaw，然后 hermes 等等”“还有国内的 trae、workbuddy、kimicode 这种”“你都调查一下，核实一下名称”。旧稿在 `台本/_旧稿/台本_v1_按类别分（作废）.json`。
2. **v2（现行）一个产品一页，每个产品一个专属主义**，17 页。名称、定位、特点全部对过官网 / README 原文（用 `curl` 抓原文，不用 WebFetch 的摘要，见 `参考分析/fetch_meta.py`、`fetch_text.py`、`页面原文/`）。每页依据写在 `台本/台本.json` 的 `note`，`制作/build_script_md.py` 生成 `台本/台本.md`。

| 页 | 产品 | 主义 | 依据（官方原文） |
|---|---|---|---|
| 01 | Claude Code | Unix主义 | “composable and follows the Unix philosophy. Pipe logs into it, run it in CI” |
| 02 | Codex | 沙箱主义 | 默认断网、写权限限于工作区、OS 级沙箱、“reduces approval fatigue” |
| 03 | DeepSeek Harness | 插件主义 | README：“everything-is-a-plugin”，`npx @deepseek-ai/dsh web`，developer preview |
| 04 | Hermes Agent | 成长主义 | “The Agent That Grows With You”，自建技能 + 持久记忆 |
| 05 | Cline | 审批主义 | “Every file edit and terminal command requires your approval” |
| 06 | Devin | 同事主义 | “Your teammate's favorite teammate”，自己开虚拟机测试、录屏 |
| 07 | OpenClaw | 管家主义 | “The AI that really does things”，住在 WhatsApp / Telegram：inbox, email, calendar, flights |
| 08 | Cursor | 野心主义 | “building ambitious software”，“handing off tasks … while you focus on making decisions” |
| 09 | Gemini CLI | 免费主义 | README：Free tier 60 requests/min、1,000 requests/day（个人谷歌账号），Gemini 3，1M token（额度会变） |
| 10 | Kiro | 规范主义 | “turn prompts into executable specs”，需求 → 设计 → 任务 → 并行智能体 → 属性测试 |
| 11 | Pi | 极简主义 | “Pi is a minimal agent harness”，“There are many agent harnesses but this one is yours”，README：没有内置权限系统（OpenClaw 的内核） |
| 12 | TRAE | 全才主义 | trae.cn：“Work、Code、Design 模式一键切换”，接入豆包 / Kimi / GLM / DeepSeek |
| 13 | WorkBuddy | 打工人主义 | 腾讯云：full-scenario desktop AI agent，一句话描述需求、自主规划、交付成果 |
| 14 | Kimi Code | 长文本主义 | 官网：“最高 1M 上下文”，“Kimi Code（KFC）”；README：Video input |
| 15 | Qwen Code | 全栈开源主义 | “The framework and the Qwen models are open-source. They evolve together.” |
| 16 | GitHub Copilot | 原生主义 | “GitHub-native agent … issues and pull requests … /fleet … /plan to merged code” |
| 17 | OpenCode | 不站队主义 | “connect any model from any provider”，75+ providers，Copilot / ChatGPT 订阅可直接登录 |

排序按曲子结构：Cline（审批）正好压在 k92–96 的静音空档，打出 y 之后鼓点进入翻到 Devin（同事）；三次鼓点进入分别是 Codex、Devin、TRAE；长低谷放 Kiro、Pi（规范、极简）；最后一页 OpenCode“不站队”接收尾的“你是哪个阵营？”。

## 名称核实结论（别再写错）

- **DeepSeek**：官方叫 **DeepSeek Harness**（`dsh`，MIT，`deepseek-ai/deepseek-harness`，官网 deepseek.com/en/harness）。**官方有桌面版**：官方仓库 release `dsh-v0.2.0-rc.2`（2026-09-29，预览版）的更新说明写有 macOS／Windows 桌面端（Desktop），用户口头说的 “DeepSeek Desktop” 应该就是它。另有第三方社区做的 “DeepSeek Harness Desktop”（页面自己写 “not an official DeepSeek product”）、社区的 `DeepSeek-TUI`（Hunter Bown）。**我一开始把官方桌面版和第三方那个搞混，对用户说成“官方没有”，说错了**，后来用官方 release 说明更正（晚间核实）。
- **TRAE**：TRAE SOLO 已在 **2026-06-10 改名 TRAE Work**；官网现分 TraeCode / TraeWork，品牌统一写 **TRAE**（The Real AI Engineer）。
- **Kimi**：Python 版 Kimi CLI（`MoonshotAI/kimi-cli`）已归档，由 **Kimi Code CLI**（`MoonshotAI/kimi-code`，MIT）取代；产品名 **Kimi Code**。
- **Windsurf**：官网 windsurf.com 现在直接显示 **Devin Desktop**（Cognition 旗下）。
- OpenClaw 前身 Clawdbot / Moltbot；现由 OpenClaw Foundation 管理，MIT；用 Pi 当内核（README 致谢 Mario Zechner）。
- Pi 官网域名 pi.dev，发布方 Earendil Inc.，npm 包 `@earendil-works/pi-coding-agent`。
- 官网抓取：`openai.com/codex` 对 curl 返回 403，Codex 的依据改用 `developers.openai.com/codex/...` 和 `openai/codex` README。

## 素材和工具

- logo：`lobehub/lobe-icons` 1.95.1（MIT，商标归各自所有者；57 个 SVG，来源和 sha256 在 `制作/assets/logos/_manifest.json`），Kiro 和 WorkBuddy 用本机已有的官方图标，Pi 是 pi.dev 官网 `logo-auto.svg`。用户 2026-10-01 说过“下载图片用来介绍”，科普类可以。
- 工具：`制作/fetch_logos.py`（下载 + 记清单）、`render_frames.py`、`encode.py`、`verify_sync.py`、`check_layout.py`（逐页量居中 / 边距 / 行宽）、`build_script_md.py`。
- 后台调研子任务没派上用场：它连网页工具都没加载出来就卡住（输出文件一直是 0 KB），停掉了，改成自己用 `curl` 和 WebSearch 查。

（以下为后续：渲染、校验、交付，见文末“进度”。）

## 成片和校验（2026-10-01 17:40）

- 成片：`独立视频/2026-10_请选择你的AI-Harness框架阵营/请选择你的AI-Harness框架阵营_成片.mp4`，2340×1080、30 fps、H.264 High yuv420p（crf 16）、12.3 MB；音轨 = 参考视频的 AAC 直拷（44.1 kHz 立体声）。**无片头片尾、没做封面、未投稿。**
- 渲染：Playwright 4 路并行，4177 帧 131 s；编码 `encode.py`（`-shortest`，成片视频 4173 帧 = 139.10 s，音轨 139.204 s，尾部是全黑 + 静音，不影响）。
- 同步：成片音轨与参考音轨互相关偏移 **+0 ms**；鼓点进入处画面闪白第 1 帧和理论拍点差 0 / +1 帧（第 32、96 拍 +33 ms，第 192、256 拍 0 ms）。音频起音检测用 20 ms 能量窗口会比真实起音早 20–30 ms，别拿它当绝对基准；节拍网格以低频起音相位拟合（2.9 ms 步长）为准。
- 画面：抽 8 帧人工看过（标题页、第 1 页、鼓点进入后闪白、静音空档的确认框、第 9 / 16 页、收尾页）；左边缘没有 ffmpeg 8.0 的黑点；1:1 看文字边缘干净。
- 没跑的：没有用播放器完整看一遍（只能抽帧）；没有做封面；没有加悠一片头片尾。
- 被 `.gitignore` 忽略的：成片、帧、字体、`制作/assets/logos`（第三方商标）、`参考分析/`（参考视频副本、抽帧、网页原文）。会进公开仓库的：脚本、引擎、`台本/台本.json`、`台本/台本.md`。

## 晚间核实后的改动（成片 v2.1，2026-10-01 20:16 重新编码）

后台来了四份调研报告（任务名 “Research camps: always-on, cloud, minimalism, memory” / “Verify Chinese-market harness products” / “Research camps: architecture and philosophy debates” / “Research camps: permissions, multi-agent, specs”，**不是我这轮派出去的**，全文在临时目录 `tasks\ad0946ce61b4ebb67.output`、`ac75706dab9f16174.output`、`aef83fdb03ec12a39.output`、`a875a3b0f33db6d69.output`）。我用官方原文对了其中和 17 页相关的几处，改了四页：

| 页 | 改动 | 依据（原文核实） |
|---|---|---|
| 05 Cline 审批主义 | 不再写“每一步都要点头”，改成 Plan 模式聊方案 → 确认后切 Act → 高风险操作照样要点头 | Cline 官方 CLI 文档：`--auto-approve` 默认 `true`（“Default to start in act mode with auto-approve enabled”）；README / Auto Approve 文档讲的是 Plan/Act 和对高风险操作保持控制 |
| 14 Kimi Code | **长文本主义 → 蜂群主义**（“Agent Swarm能同时派出上百个”，外号“人海战术”） | K2.5 官方博客：up to 100 sub-agents、up to 4.5x；Kimi Code CLI 文档有 `AgentSwarm` 工具。Agent Swarm 是 harness 层的特色，1M 上下文是模型的特色。具体上限（报告说 CLI 128、K2.6 300）没核实，只写“上百个” |
| 15 Qwen Code | “模型也开源” → “Qwen系列也有开源模型”，外号“不被任何厂商绑定” | README 原话 “The framework and the Qwen models are open-source”；但旗舰 Qwen3.8-Max（2026-08-03）是否开放权重没核实 |
| 17 OpenCode | “手上有的订阅” → “Copilot、ChatGPT订阅直接登录” | OpenCode 官网只列这两个；报告说 2026-02 因 Anthropic 法务要求去掉了 Claude 订阅登录（PR #18186，未核实） |

只重渲了这四页前后的帧（`render_frames.py --range … --force`，三段共约 966 帧，29 s），整条重新编码；上一版（第一次发给用户的）在 `制作/_旧稿/`。校验：音轨偏移 +0 ms，4 页抽帧看过。

另外：
- **DeepSeek 官方有桌面版**（`dsh-v0.2.0-rc.2` 更新说明，2026-09-29，预览版，macOS / Windows），我之前对用户说“DeepSeek Desktop 是第三方的”说错了，已在上面的“名称核实结论”、AGENTS.md 和 `台本/台本.json` 的 note 里更正；画面用的是官方名 DeepSeek Harness，没变。
- WorkBuddy：官方更新日志首个版本 v4.5.0 是 2026-03-04，03-09 是媒体报道的上线日（只在 note 里，画面没有日期）。

### 后台报告里和这条视频无关、但以后可能用得上的要点（**都是报告里的说法，我没逐条核实，用之前要回原页面对**）

- **OpenClaw**：仓库 2025-11-24 创建；Clawdbot → Moltbot（2026-01-27，Anthropic 来信）→ OpenClaw（01-29/30）；Steinberger 2026-02-14 宣布加入 OpenAI，OpenClaw 转入基金会（2026-07-08 公布 501(c)(3)）；2026-03 国内“养龙虾”热，各家都出了 Claw；腾讯 QClaw 2026-09-24 宣布 12-24 停服、迁到 WorkBuddy；用 Pi 当内核。
- **Pi**：四个工具（read / write / edit / bash）、默认不设权限弹窗（作者原话“YOLO by default”）、没有子代理 / 计划模式；110k+ stars；DeepSeek Harness 用了它的 pi-ai 库。
- **Hermes Agent**：2026-02-25 首次公开发布，2026-06-05 出桌面版；`hermes claw migrate` 可从 OpenClaw 迁移。
- **产品变动**：Cursor 2026-08-14 被 SpaceX 收购（cursor.com 博客）；Windsurf 2026-06-02 变 Devin Desktop；Roo Code 2026-05-15 关停；iFlow CLI 2026-04-17 停止；TRAE SOLO 2026-06-10 改名 TRAE Work，2026-08-24/25 字节把 TRAE、扣子并入豆包、推豆包工作；阿里通义灵码 2026-05-20 改名 Qoder CN、千问办公 2026-08-03；智谱 ZCode（Apache-2.0，“GLM 官方 Harness”）2026-09-20 开源；小米 MiMo Code（MIT）2026-06-10。
- **“Harness” 这个词**：Hashimoto 2026-02-05 的文章里提出 “harness engineering”，OpenAI 02-11、LangChain 02-17 跟进；DeepSeek 招聘稿里的公式 “Model + Harness = Agent”；国内媒体用“马具”“爱马仕（Hermes）派 vs 龙虾（OpenClaw）派”。
- **路线之争**：Claude Code 2026-03-31 因 npm 包带 source map 泄露源码（v2.1.88），出现 clean-room 仿制 claw-code（195k stars）；Anthropic 对第三方 harness 的订阅政策反复（2026-01-09、04-04 收紧，05-13 又放开一部分）；OpenAI 反向，2026-09-29 DevDay “Sign in with ChatGPT” 给 16 个第三方；“删掉 80% 提示词”（Boris Cherny，YC）vs “harness 就是产品”（Harrison Chase 等）。
- **“放飞”的真实写法**：Claude Code `--dangerously-skip-permissions`；Codex `--dangerously-bypass-approvals-and-sandbox`（别名 `--yolo`）；Gemini CLI `--approval-mode=yolo`；Copilot CLI `--yolo`；Cursor 现在叫 “Run Everything”；Cline “YOLO Mode”；Pi 没有开关（默认就是）。Anthropic 2026-08-07 博客：用户对 97% 的权限弹窗点了允许（可做梗）。
- **多智能体**：Kimi Agent Swarm（K2.5，100 个）；Claude Code agent teams（2026-02-05，实验性）、dynamic workflows；Codex 子代理上限降到 6；Copilot CLI `/fleet`（2026-02-17）；Cursor 2026-08-19 “子代理各用自己的机器”。**规范驱动**：Kiro（2025-07 预览、11 月 GA）、GitHub spec-kit、OpenSpec、BMAD；批评者叫它“Markdown 里的瀑布”。

## v3 提速（2026-10-01 20:40，成片约 1:15）

用户的三条要求：
1. “开头的那一段，音乐不变，速度变为2倍速来展示”；
2. “然后把下面的17个。。。 这一段文字删除”（标题页的副标题“17 个 Harness · 17 种主义 · 选一个站队”）；
3. “中间所有的视频展示时间都缩短一半，现在是16个节拍的话，就缩短为8个节拍”。

我的理解和做法（用户没细说的地方是我定的）：
- 标题页：动画 2 倍速（三行标题在第 0 / 0.5 / 1 拍盖章，16 个 logo 每 0.45 拍弹一个，第 7 拍前弹完），**占 8 拍**（原来 16 拍）；副标题删掉，三行标题整体下移 28 px 重新垂直居中。
- 每页 **8 拍**（3.69 s）：页内出字节奏也整体 2 倍速（标题 0、logo 0.5、说明每半拍一行、外号最后），4 拍内出齐，剩 4 拍读。
- 总长 = 标题 8 拍 + 17 页 × 8 拍 + 收尾；**音乐不变速，只裁短**：整条视频缩到约 1:15，音乐在第 160 拍（74.35 s，鼓点撤掉、下行扫频的自然收尾处）再留 1.2 s，最后 1.5 s 淡出（`encode.py` 按台本 `dur`、`audio_fade` 裁和淡出，AAC 256k 重编码，不再整条直拷）。
- 页边界仍然落在曲子的结构点上（页起点 = 8 + 8i 拍）：第 4 页（k32）= Codex 压第一次鼓点进入，第 11 页（k88–95）= Cline 压第 92–96 拍的静音空档，第 12 页（k96）= Devin 压第二次鼓点进入。**为此调整了页的顺序**：Claude Code → DeepSeek Harness → OpenClaw → Codex → Cursor → Gemini CLI → TRAE → Hermes → Kiro → Pi → Cline → Devin → WorkBuddy → Kimi Code → Qwen Code → GitHub Copilot → OpenCode。收尾页从 k144（66.97 s）起，视频最后 1.6 s 淡出黑。
- 只有鼓点进入 1、2 用上了；第 3、4 次鼓点进入（k192、k256）和最后一击（k288）因为音乐裁短不再出现。
- 引擎新增台本字段：`slide_beats`、`intro_beats`、`intro.speed`、`intro.pop_step`、`audio_fade`；`render_frames.py` 加了 `--force`；`verify_sync.py`、`build_script_md.py` 按新结构生成。旧的 4177 帧挪进了 `制作/_旧稿/frames_每页16拍版_139秒`，上一版成片在 `制作/_旧稿/成片_v2.1_每页16拍_整首音乐139秒_20261001-2016.mp4`，上一版台本在 `台本/_旧稿/台本_v2.1_每页16拍（整首音乐版）.json`。
- 校验：2267 帧 = 75.567 s，音轨 75.55 s，和参考音轨互相关偏移 +0 ms，最后 1.5 s 能量 −12 → −28 dBFS 淡出；抽帧看了开头、第 1 页、收尾和淡出。渲染 58 s，编码约 1 分钟。

**待用户确认 / 我已经提醒的**：
- 每页只有 3.7 s，4 行字（约 55 个字）出齐后只剩约 2 s 读，**读不完**；可以每页只留 2 行。
- 我把“音乐不变”理解成“不变速、不改曲子，只是裁短”。如果用户其实想保留整首音乐（2:19）而每页缩到 8 拍，就得再加 17 个产品（后台报告里有现成的候选：智谱 ZCode、阿里 Qoder、小米 MiMo Code、腾讯 CodeBuddy、字节 DeerFlow、Antigravity、Amp、Goose、Warp、Zed 等），要另外写主义、核实、找 logo。

## v4 文案待审（2026-10-01 晚）

用户看完 v3：“视频节奏没问题的，就是这些主义 我觉得你设定的还是有些问题，你重写一个版本，然后先给我文字，我通过了你在做视频”。**没说具体哪几个有问题**，所以先自查，再整体重写，**文字通过之前不做视频**。

我自查出的三类问题：① 名字要解释才懂（Unix主义、野心主义、原生主义、全才主义），参考视频的“主义”都是一眼能懂的大白话；② 抓的是文档里的细节，不是大家选这个产品的理由；③ 每页 4 行、约 55 字，3.7 s 读不完。

v4 的做法：每个主义 = 这一派“最看重的一件事”，名字用大白话；文字压成 3 行 + 外号（约 40 字）；页序按用户的原话排（Claude Code、Codex、DeepSeek Harness、OpenClaw、Hermes，再国产 TRAE、WorkBuddy、Kimi Code，再其余），所以页边界要重新对曲子（鼓点进入 1 = 第 4 页 OpenClaw，第 11 页 Cline 压静音空档，第 12 页 Devin 压鼓点进入 2）。

| 变化 | v3 → v4 | 原因 |
|---|---|---|
| Claude Code | Unix主义 → **生态主义** | Unix 要解释；Skills / Hooks / MCP / 子代理 / 插件 + 各处都能接，是它最被认的特点（官方文档） |
| OpenClaw | 管家主义 → **龙虾主义** | “养龙虾”是新华社都在用的说法（2026-03-18、03-23） |
| TRAE | 全才主义 → **全能主义** | 更口语（Work / Code / Design 三模式） |
| Devin | 同事主义 → **外包主义**（备选：同事主义） | 更直白；“同事最喜欢的同事”留作外号 |
| Cursor | 野心主义 → **IDE主义** | 野心要解释；Cursor 3 官方博客写明继续投入 IDE，随时能进编辑器 |
| GitHub Copilot | 原生主义 → **GitHub主义** | 原生要解释 |
| 其余 11 个 | 名字不变，文字重写 / 压缩 | |

草稿在 `台本/台本_v4_待审.json`（现行 `台本/台本.json` 没动）；通过后：覆盖 `台本.json` → `build_script_md.py` → 整条重渲（约 1 分钟）→ 编码 → 校验。`render_frames.py` 新增环境变量 `SCRIPT_JSON`，可以对草稿单独跑 `check_layout.py`（17 页全部放得下）。

## v5 文案待审：哲学流派版（2026-10-01 夜）

用户看完 v4 后，贴来一版“哲学流派”风格的主义（应该是拿 v4 的文字让别的模型改的）：每个产品配一个真哲学流派，带“出处 + 解释 + 金句”，要求“你综合一下下面的这种，然后再给我一版”。**文字通过之前不做视频。**

我的综合做法：
- 17 个主义、顺序、出处、金句基本沿用用户贴的（顺序和 v4 一致：Claude Code → … → OpenCode，所以曲子对位不变：Codex 之后的 OpenClaw 压鼓点进入 1、Cline 压静音空档、Devin 压鼓点进入 2）：有机主义 / 批判主义 / 折衷主义 / 此在主义 / 潜能主义 / 百科全书主义 / 工具理性主义 / 单子论 / 先验主义 / 无为主义 / 契约主义 / 自律主义 / 在场主义 / 内在主义 / 普惠主义 / 解放主义 / 悬置主义。
- 画面版：标题 + 出处小字 + 3 行 + 金句；原来的长解释不上画面（存在草稿的 `why` 字段，可放简介）。
- 事实对回官方原文：Codex 默认断网 / 写权限限于工作区；Cline 只写“高风险操作要点头”（新版 CLI 默认自动批准）；Qwen 写“Qwen系列也有开源模型”（旗舰是否开放权重没核实）；Pi 没有权限弹窗；Kimi 子代理在独立上下文里并行；Gemini 的 1000 次是 README 现在的说法。
- 改了用户贴的两处：Gemini CLI 的金句“能白嫖，是普世价值”换掉（“普世价值”在国内是敏感词）→“能白嫖，才是真普惠”；英文括号里三处不准（先验主义不是 Transcendentalism，应为 Apriorism；在场主义不是 Presentism；潜能主义不是 Dynamism），画面里只放中文。
- 提醒用户：Qwen 页金句是马克思口号的戏仿（备选“开源的尽头是解放”）；康德用了 3 次（批判主义、先验主义、自律主义）。

草稿 `台本/台本_v5_待审.json`（字段 `tag` = 出处、`why` = 解释；`check_layout.py` 17 页放得下；**引擎还没做“出处小字”这一行**，通过后再加）。现行 `台本/台本.json` 没动。

### v5 通过后的制作（2026-10-01 21:10 起）

用户：“没问题，就这样。”（含我提的三个待定点：Qwen 的马克思口号戏仿金句保留、康德出现三次不换、每页出处 + 3 行 + 金句的字数不变。）
- 引擎加了“出处小字”：标题下面一行（36 px、70% 透明度），在标题和 logo 之后出现，说明行往后顺延一格（8 拍里 3.0 拍内出齐）；`check_layout.py` 17 页放得下（文字列高 602 px）。
- `台本/台本.json` 换成 v5（`台本_v5_待审.json` 的内容）；上一版（v3，产品特点主义）归档为 `台本/_旧稿/台本_v3_产品主义版（生态、沙箱、插件…）每页8拍.json`；上一版成片在 `制作/_旧稿/成片_v3_产品主义版（生态沙箱插件…）每页8拍_1分15秒_20261001-2040.mp4`。`build_script_md.py` 生成的 `台本.md` 带出处和解释。
- 开渲染前另一个会话（白宫超级智能协议）正在 4 路渲染、空闲内存只剩 3.2 GB，按“同一时间只跑一个渲染”的约定，等它跑完再开。
- 踩坑：Bash 钩子 dcg 把我脚本字符串里写的说明文字（含删除命令字样）当成真删除命令拦了；写脚本时别在字符串里带这类字样，或者改用 Write 工具写文件。
- 结果（21:19，成片 v5）：另一个会话渲完后我 4 路渲染 2267 帧（82 s）；出处小字第一版 36 px 偏小，调到 40 px、透明度 0.8 后重渲（86 s）再编码。成片 `请选择你的AI-Harness框架阵营_成片.mp4`：2340×1080、30 fps、75.57 s、9.8 MB，音轨 75.55 s（和参考音轨互相关偏移 +0 ms，最后 1.5 s 能量 −13 → −28 dBFS 淡出）。逐页看过 17 页的实际画面（出处小字 + 3 行 + 金句都放得下），抽帧看过开头、第 1 页、契约主义出字过程、收尾和淡出。没有用播放器完整看一遍。

## 进度

- [x] 参考视频抽帧、转场分析、BGM 节拍分析
- [x] 渲染引擎、小样、编码和同步校验管线
- [x] 研究：17 个产品的名称、定位、特点核实（官网 / README 原文），logo 下载并记清单
- [x] 台本 v2（一产品一主义）、整条渲染、编码、同步校验
- [x] 后台报告核实后改了四页并重新编码（成片 v2.1）
- [x] 提速：开头 2 倍速、删副标题、每页 8 拍、音乐裁到自然收尾处（成片 v3，1:15）
- [x] v5 文案（哲学流派版）用户通过，做成成片 v5（21:19）
- [ ] 用户看成片 v5、定稿
- [ ] 封面（B 站 16:9 + 4:3）、悠一片头片尾（用户没要，要的话再做）、投稿
