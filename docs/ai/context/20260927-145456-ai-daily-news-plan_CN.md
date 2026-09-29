# AI 每日速报：单次运行流程设计（草案 v2）

时间：2026-09-27 14:30–16:30（UTC+9）。v2 按用户同日的新要求改写：信息源只用免费 RSS 并在本机实测；B 站用浏览器插件自动发布；每天的定时由用户自己设成 routine，这里只设计“跑一次”的完整流程。

## 用户要求

- 用 DeepSeek 拟人「大肥鱼」当主播，做第二档节目「AI 每日新闻速报」。
- 盯 RSS 和 X 等社交账号抓信息；抓取时间参考“国外公司多在北京时间 12 点、24 点左右发布”。
- 每天早上中国大陆用户起床前发片。
- 目标是抓取 → 生成视频 → 发 B 站全自动；现阶段要用户审核。
- 追加：
  - 信息源找免费的 RSS（GitHub 上找），在本机实测能不能拿到消息。
  - B 站用浏览器插件自动发布。
  - 每天怎么定时由用户设 routine，这里只做好单次运行的设计。

## 用户确认（2026-09-27，v3）

- **标题**：`M月D日，鲸鱼娘带你看看AI圈发生了什么？`（日期是发布当天）。
- **合集**：新建「AI每日日报」（用户说“分集”，按 B 站的合集理解）。
- **配音**：浏览器插件操作 Fish Audio 网页版（免费，S1），音色「苏晓晓」，不走 API。
- **RSS**：用代码抓。
- **画面、合成、封面**：按本文设计。
- **片头片尾**：复用 UE 片头（3.8 s）和片尾（4.8 s）。片尾清单要写本期新闻的来源。
- **发布**：浏览器插件。
- **时长**：3–4 分钟，也就是 4–5 条。

### 抓取频率（回答用户的问题）

一天抓 4 次：北京 12:30、18:30、00:30 只抓取，04:30 抓最后一次并出片。

依据是各源能留住多少小时的历史（2026-09-27 实测），间隔要比源的历史短，才不会漏：

| 源 | 能留住的历史 | 每天条数 |
|---|---|---|
| 官方博客、HF、GitHub、X 镜像 | 几天到几年 | 0.4–3 |
| The Verge、TechCrunch、MarkTechPost、The Decoder、量子位 | 26–47 小时 | 4–12 |
| Techmeme X Chatter、Google News 中文 | 19–21 小时 | 33–61 |
| Techmeme、Google News 英文 | 14–15 小时 | 21–143 |
| aibase 资讯、IT之家 | 约 7 小时 | 84–184 |
| 36 氪快讯 | 约 3.6 小时 | 112 |

- 夜里国内源更新少，04:30 → 12:30 这 8 小时漏不了什么；白天国内源更新多，所以 12:30 → 18:30 → 00:30 每 6 小时一次；00:30 → 04:30 是美国上午，最后再抓一次。也对应了用户说的 12 点、24 点。
- 36 氪快讯只留约 3.6 小时，而且大多不是 AI，不追求抓全。
- 抓得更勤对视频没有好处（一天只出一期），还更容易被公共 RSSHub 和 GitHub 限流（429）。
- 只抓取的三次不用 Claude，用 Windows 计划任务直接跑 `collect.py` 就行，不花用量；04:30 那次走 routine。

## 结论

1. **信息源全部免费，都在本机实测过**（2026-09-27，见「信息源」）：官方 RSS / 接口 19 个（HF 覆盖 15 家厂商，GitHub 7 个仓库），GitHub 社区生成的 RSS 8 个，X 的替代 7 个，英文媒体和新闻信 17 个，中文 8 个。不需要 X API，也不需要付费聚合服务。
2. **X 没有稳定的免费直连**：Nitter 12 个实例全挂（项目已归档），X 的嵌入接口返回 429，RSSHub 的 X 路由要 X 账号的登录 token。能用的是：
   - Bluesky 上的 X 镜像号（OpenAI、AnthropicAI、xAI、sama、Kimi、Ollama 共 6 个，Bluesky 自带 RSS）；
   - Techmeme X Chatter（每天约 30 条精选 X 帖）。
   这些只当线索，不能单独成条。
3. **单次运行建议北京 04:30 触发（东京 05:30）**。
   - 美国公司官方博客 60% 发在北京 23:00–04:00。
   - 12 点对美国公司不成立（只占 1%），但国内厂商 90% 在北京 11:00–23:00 发。
   - 量大的中文源（36 氪快讯、IT之家）一天只抓一次会漏，所以另设“只抓取”模式，可以在北京 12:30、00:30 各加一次。这也对应用户说的 12 点、24 点。
4. **每次运行只停一次 ✋**：成片和审稿单做好后，等用户回复“发”，插件再点「立即投稿」。
5. **插件上传 10 MB 的限制能解决**：第 1 期 3 分钟片段两遍编码压到 9,880,828 字节（总码率约 440 kbps，1080p），静态画面抽帧对比看不出差别。速报画面同样以静态为主。上传版按时长算码率、压到 ≤9 MB 留余量；转场和动作帧在第一次成片时再看。
6. **默认不用定时发布**：审核通过就立即投稿；B 站自己的审核一般几分钟到几小时，07:00 前上线不保证。（调研说定时发布至少提前 4 小时；2026-09-27 投稿页实测这个账号是 5 分钟后到 15 天内，要准点上线也来得及。）
7. **合规**：
   - 分区选「人工智能」（2026-09-27 投稿页只有一级分区，没有 AI资讯 可选）。
   - 创作声明选「含AI生成内容」（原先叫“该视频使用人工智能合成技术”）。用户 2026-09-27 定：配音和画面都不出现“本期配音由 AI 合成”（太割裂），只在简介里写。
   - 账号名和简介不用“新闻”“报道”（已定的标题和合集名都不含这两个词）。
   - 不做电视演播室风格（v1 的“主播台”取消）；不碰时政、地缘、出口管制。
8. **周二到周六固定更新**：周日那期美国、国内都只有约 5%；周一那期美国 2%、国内 16%。周一有国内大新闻就出短版，没有就休息。

## 单次运行

触发：routine 让 Claude 按以后的 `ai-daily-news` 技能跑当天这一期。一期一个目录 `daily\YYYY-MM-DD\`。

| # | 步骤 | 谁做 | 产物 | 约用时 |
|---|---|---|---|---|
| 1 | 抓取 | 脚本 `collect.py` | `items.jsonl`（本期新条目）+ 原文快照 | 1–2 分钟 |
| 2 | 去重聚类 | 脚本 | `candidates.json` | 秒级 |
| 3 | 选题 | Claude | `picks.json`：3–5 条 + 理由，落选的也列出来 | 3–5 分钟 |
| 4 | 台本 + 核对 | Claude + `check_script.py` | `台本.json`（每句对应来源）、核对结果 | 约 5 分钟 |
| 5 | 配音 | Fish Audio | 每句一个音频、字幕时间、口型 | 1–3 分钟 |
| 6 | 画面、合成、封面 | 脚本（沿用《原LAI如此》引擎） | `成片.mp4`、`上传版.mp4`（≤9 MB）、`字幕.srt`、`章节.txt`、`封面\`、`投稿信息.json` | 3–5 分钟 |
| 7 | ✋ 审核 | 用户 | `审稿单.md`；用户回复“发”，或者说改哪里 | — |
| 8 | 发布 | Claude + Chrome 插件 | B 站稿件、`发布记录.json`（BV 号） | 3–5 分钟 |
| 9 | 收尾 | 脚本 | 已播清单、来源健康报告 | 秒级 |

机器时间合计约 20–30 分钟：04:30 触发，05:00 左右可以审。

- **断点续跑**：每步产物落盘，`state.json` 记到哪一步；中断后从断点接着跑，不重复抓取、不重复配音。
- **只抓取模式**：只跑第 1 步、入库，给量大的中文源用。
- **什么算新条目**：`seen.sqlite` 里没见过的就是新的，不看源里写的时间（OpenAI RSS 的时刻是占位值）。第一次运行只收 36 小时内的。
- **改稿**：改哪句就只重做那句的配音和后面的步骤。
- **没人回复**：到北京 07:30 还没收到“发”，这期不发，并进第二天。
- **要在这台电脑上跑**：发布要用本机 Chrome 里的插件和 B 站登录，渲染要用 D 盘素材、Playwright、ffmpeg。桌面版的定时任务在本机执行；云端 routine 要先确认能连到这台电脑的 Chrome 和文件。

### 1. 抓取

- `sources.yaml` 写每个源的级别、抓取方式（RSS / 接口 / 网页比对）、过滤规则、备用地址。
- 抓到的每条记：源、网址、标题、摘要、源里写的时间、抓到的时间、原文快照路径。原文第一次看到就存下来（核对用，也防事后改稿）。
- 带 ETag / If-Modified-Since，每个网站限速。
- RSSHub 路由按顺序试：自建实例（如果装了）→ rsshub.ktachibana.party → rsshub.isrss.com；都不行就跳过，并写进来源健康报告。
- 某个源连续几次失败或一直没更新（改版、社区脚本停了），在审稿单里提示。
- 只追加、不删除；清理时移到 `_旧稿\`（用户有 dcg 钩子）。

### 2. 去重聚类

- 网址规范化去重。
- 同一事件（官方稿 + The Verge + Techmeme + X 镜像）按公司、时间和标题相似度合成一条：官方稿作主来源，其他作旁证。

### 3. 选题

- 优先级：
  1. 新模型、新产品发布或正式上线；
  2. 价格、额度、API 变更；
  3. 国产模型动态（DeepSeek、Qwen、Kimi、GLM、MiniMax 等）；
  4. 头部公司的大合作、融资、人事；
  5. 有产品意义的研究；
  6. 大面积宕机。
- 不收：客户案例、营销稿、游戏推广、传闻和爆料、时政和地缘、出口管制、股价。
- 硬规则：每条要有官方来源，或者至少两家可靠媒体。X 镜像和社区帖只当线索。
- 记“已播”清单，避免重复；同一件事有新进展可以跟进。
- 候选不够 3 条就出短版，不凑数。

### 4. 台本 + 核对

- 结构（约 3 分钟）：
  - 开场一句：“早上好，我是大肥鱼，今天是 9 月 28 日。”后面接“本期配音由 AI 合成”，屏幕同时显示 2 秒。
  - 每条 30–45 秒：
    - 发生了什么：谁、什么、哪天；
    - 2–3 个关键信息：型号、价格、开放范围，官方给的跑分写“官方称”；
    - 对国内用户有什么影响：能不能用、有没有 API、多少钱。
  - 结尾一句：“来源都在简介里。”
- 沿用 AGENTS.md「台本风格规则」：短句、口语、不要 AI 腔、不用“不是……而是……”、直接给干货。
- 新闻另加三条：
  - 不用“炸裂”“王炸”这类夸张词。
  - 大肥鱼是 DeepSeek 的形象，报道 DeepSeek 时保持中立。
  - 源里没写具体几点就不说几点，只说哪天。
- 自动核对（结果写进审稿单）：
  - 台本里的每个数字、日期、型号都要能在原文快照里找到（配一张换算表，例如“1.6 万亿”=“1.6T”）；
  - 每条至少一个来源网址；
  - 逐句标出原文依据，找不到的标“无依据”；
  - 查 B 站敏感词和夸张词清单。
- 英文名的读法单独做一张表（GPT、Claude、Qwen 等怎么念），写进 TTS 文本，字幕原文不变。

### 5. 配音

- 用户选定：浏览器插件操作 Fish Audio 网页版（免费），和第 1 期同一套做法（`AI科普\skill\yuanlai-ruci-episode\references\voice.md`）：
  - 音色「苏晓晓」：https://fish.audio/zh-CN/m/e7219cb8cfab46bebba2ee570932b0a6/ ；免费账号用 S1。
  - 每批 ≤480 字节，每批 2 个版本，抓 CDN 地址下载，faster-whisper 打分选版本，再按句切开、对齐字幕。
  - 3–4 分钟约 900–1200 字，也就是 6–8 批，约 10 分钟。
  - 插件连不上就停下来告诉用户，不换别的配音方式。
- 口型沿用 `mix_audio.py` 的按音量生成。
- 备用（以后要无人值守再说）：Fish Audio API。免费模型 `s2.1-pro-free`；付费模型每百万字节 15 美元，一期约 0.04 美元。
- 不用真人声优的克隆音色：北京互联网法院 2024 年判过，声音权益延伸到能被认出来的 AI 声音。

### 6. 画面、合成、封面

- 沿用《原LAI如此》的 HTML 逐帧渲染引擎，新做“速报”版面：
  - 左上：「AI每日日报 · 9月28日 周一」；
  - 右侧：新闻卡（公司名用文字色块，不画 logo）+ 2–3 个要点 + 来源和日期；
  - 左下：大肥鱼；
  - 底部：今日条目进度条 + 居中字幕；
  - 配色用大肥鱼的藏青 / 蓝 / 白 / 金，和《原LAI如此》的四色区分开。
- 引擎要改：现在写死了山田凉的动作帧目录（`素材\角色\动作帧\`），并要求有 `reach`、`walk`。要加“角色包”参数（episode.json 指定角色）。大肥鱼暂时只用待机、说话口型和三个表情，自动手势层关掉。
- 片头片尾：复用 UE 片头（3.8 s）和片尾（4.8 s）。片尾清单自动写本期新闻来源（片尾最多 6 条、每条约 30 字，来源多就分两行）。
- 封面模板：大日期 + 头条几个字 + 大肥鱼，自动出 16:9 和 4:3。
- 两个版本：
  - `成片.mp4`：存档用，CRF 16；
  - `上传版.mp4`：按时长算码率，两遍编码到 ≤9 MB（3 分钟约 400 kbps），给插件上传。
- 其他输出：字幕、章节（每条新闻一章，填 B 站分段章节）、`投稿信息.json`（标题、标签、简介）。

### 7. ✋ 审核

- `审稿单.md` 内容：
  - 今日条目：标题、台词、来源链接、核对结果；
  - 预计时长；
  - 落选的候选（方便换条）；
  - 来源健康提示。
- 用户回复：
  - “发”：进入第 8 步；
  - “第 2 条换成 X”或“这句改成……”：只重做受影响的部分，再给用户看。
- 这一步在 routine 的会话里进行。开了 Remote Control 就能在手机上看和回复；要实测。

### 8. 发布（Chrome 插件）

按第 1 期的踩坑清单（`AI科普\skill\yuanlai-ruci-episode\references\bilibili.md`）：

1. 打开投稿页，`file_upload` 上传 `上传版.mp4`。
2. 填：
   - 标题：`9月28日，鲸鱼娘带你看看AI圈发生了什么？`；
   - 标签：AI资讯、人工智能、大模型、AI日报 + 当天的公司名 + 大肥鱼（话题专用标签换别的词）；
   - 封面：16:9 和 4:3 两个比例；
   - 简介：今日条目（`mm:ss`）、每条来源、说明（信息截至北京时间 04:30；内容由 AI 生成；形象署名，非 DeepSeek 官方）；
   - 合集：「AI每日日报」，第一次要新建；
   - 创作声明：“该视频使用人工智能合成技术”。
3. 分区最后设：「人工智能 → AI资讯」。填标签会让 B 站自动改分区，所以放在最后再核对一遍。
4. 等上传和转码完成，截图核对。
5. 用户已经回复“发”，才点「立即投稿」，然后记下 BV 号。
- 《原LAI如此》仍然是“立即投稿由用户自己点”。速报的发布由用户在会话里每期说“发”来授权。以后要去掉这一步，要用户另外决定。

### 9. 收尾

- 更新“已播”清单和来源健康报告。
- 下一期运行时，顺便记上一期的播放、完播、点赞，用来调选题权重。

## 信息源（2026-09-27 本机实测）

“新鲜”指最新一条距测试时间多久。实测脚本在会话临时目录，以后改写成 `collect.py`。

### A. 官方一手（直接抓，不依赖第三方）

| 源 | 地址 / 方式 | 状态 |
|---|---|---|
| OpenAI News | `openai.com/news/rss.xml` | 可用；时刻是占位值；按 category 过滤客户案例 |
| OpenAI 开发者文档 | `developers.openai.com/rss.xml` | 可用，辅助信号 |
| Claude 平台更新日志 | `platform.claude.com/docs/en/release-notes/feed.xml` | 可用，只有日期 |
| Claude Code 更新日志 | `code.claude.com/docs/en/changelog/rss.xml` | 可用，1 天前 |
| Anthropic Newsroom | 网页比对 `anthropic.com/news` | 可用（没有官方 RSS） |
| Google AI 博客 / DeepMind / Google Research | `blog.google/technology/ai/rss/`、`deepmind.google/blog/rss.xml`、`research.google/blog/rss/` | 可用，时间准确 |
| Mistral | `mistral.ai/news/rss` | 可用 |
| NVIDIA、Hugging Face 博客、AWS ML、Apple ML | 各自 RSS | 可用；NVIDIA 游戏推广多，要过滤 |
| DeepSeek | `api-docs.deepseek.com/sitemap.xml` 里的 `/news/newsYYMMDD` | 可用（RSSHub 的 DeepSeek 路由今天返回空） |
| Qwen 博客 | `qwen.ai/api/v2/article/retrieval?language=zh-CN&type=qwen_ai` | 可用，40 篇（`language` 必须是 `zh-CN` 或 `en-US`） |
| HF 模型上传 | `huggingface.co/api/models?author=<org>&sort=createdAt&direction=-1` | 可用；15 家：deepseek-ai、Qwen、moonshotai、zai-org、MiniMaxAI、XiaomiMiMo、tencent、baidu、stepfun-ai、ByteDance-Seed、openai、google、meta-llama、mistralai、nvidia；跳过量化版本 |
| GitHub 发版 | `github.com/<org>/<repo>/releases.atom` | 可用；openai-python、anthropic-sdk-python、python-genai、claude-code、codex、ollama、vllm |
| 服务状态 | `status.openai.com/history.rss`、`status.anthropic.com/history.rss` | 可用；只报大面积故障 |

不可用：OpenAI Engineering RSS（403）、Meta AI 博客（400）、xAI 新闻页（403）、Microsoft AI 博客 RSS（410）。

### B. GitHub 社区生成的 RSS（GitHub Actions 每小时抓官网）

| 源 | 地址（`raw.githubusercontent.com/` 下） | 新鲜 |
|---|---|---|
| xAI 新闻 | `0xSMW/rss-feeds/main/feeds/feed_xai_news.xml` | 5 天 |
| Claude 博客 | `Olshansk/rss-feeds/main/feeds/feed_claude.xml` | 2 天 |
| Anthropic Research | `Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml` | 2 天 |
| Anthropic News | `Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml`（备用：`taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml`） | 4 天 |
| OpenAI 开发者博客 | `Olshansk/rss-feeds/main/feeds/feed_openai_developer.xml` | 4 天 |
| Cursor 博客 | `Olshansk/rss-feeds/main/feeds/feed_cursor.xml` | 4 天 |
| AI 研究合集 | `0xSMW/rss-feeds/main/feeds/feed_ai_research.xml` | 2 天 |

- 仓库：Olshansk/rss-feeds（691★，今天还在更新）、0xSMW/rss-feeds、taobojlen/anthropic-rss-feed。
- 停更或不可靠：Olshansk 的 xAI（5 月以后没更新，改用 0xSMW 的）、Meta AI（7 月 27 日以后没有新文章，RSSHub 也一样，可能是官网没发）、Mistral（用官方 RSS）、Perplexity、The Batch、Cohere、Anthropic Engineering、Ollama。
- 社区脚本随时可能停；健康报告会盯着。

### C. X（推特）的免费替代

| 源 | 地址 | 新鲜 |
|---|---|---|
| OpenAI（X 镜像） | `bsky.app/profile/openai.xmirror.bot/rss` | 11 小时 |
| AnthropicAI（X 镜像） | `bsky.app/profile/anthropicai.xmirror.bot/rss` | 1.4 天 |
| xAI（X 镜像） | `bsky.app/profile/xai.xmirror.bot/rss` | 1.4 天 |
| sama（X 镜像） | `bsky.app/profile/sama.xmirror.bot/rss` | 1.4 天 |
| Kimi（X 镜像） | `bsky.app/profile/kimi-moonshot.xmirror.bot/rss` | 4.7 天 |
| Ollama（X 镜像） | `bsky.app/profile/ollama.xmirror.bot/rss` | 3.3 天 |
| Techmeme X Chatter | `bsky.app/profile/xchatter.techmeme.com/rss` | 1 小时；每天约 30 条 |

- 镜像号是第三方做的“非官方镜像”，延迟和完整性没法保证。
- 没有镜像的：claudeai、googledeepmind、deepseek、qwen、zai、minimax、mistral、meta、karpathy 等。
- 试过不行的：
  - Nitter 12 个实例（451 / 403 / 域名失效 / 已关停，项目已归档）；
  - X 嵌入接口（429）；
  - `x.com/<账号>/index.xml`（返回网页）；
  - RSSHub 的 X 路由（要 X 账号 token，公共实例没配）。
- Anthropic（`anthropic.com`）和 Hugging Face（`hf.co`）在 Bluesky 有官方号，但 RSS 是空的（不发帖）。

### D. 英文媒体和新闻信（交叉验证；Meta、xAI 等的消息靠这些）

| 源 | 地址 | 备注 |
|---|---|---|
| Techmeme | `techmeme.com/feed.xml`；Bluesky `techmeme.com` | 24 小时内 19 条 |
| The Verge AI、TechCrunch AI、Ars Technica AI、MIT TR AI | 各自 RSS | |
| The Decoder、MarkTechPost | `the-decoder.com/feed/`、`marktechpost.com/feed/` | 24 小时内各 6 条 |
| Simon Willison | `simonwillison.net/atom/everything/` | |
| Hacker News（AI 关键词、≥150 分）、r/LocalLLaMA 日榜 | `hnrss.org/newest?q=…&points=150`、`reddit.com/r/LocalLLaMA/top/.rss?t=day` | 只当线索 |
| Google News 搜索 | `news.google.com/rss/search?q=<关键词>+when:1d&hl=en-US&gl=US&ceid=US:en` | 24 小时 100 条；按公司名各开一个查询 |
| 新闻信：Import AI、Latent Space、Interconnects、Last Week in AI、TLDR AI、Ben's Bites | Substack / 官网 RSS | 周更为主，只作背景 |

不可用：smol AINews（9 月 9 日以后停更）、artificialintelligence-news（返回网页）。

### E. 中文

| 源 | 地址 | 备注 |
|---|---|---|
| 量子位 | `qbitai.com/feed` | 直连可用 |
| IT之家 | `ithome.com/rss/` | 直连可用，要按关键词过滤 |
| readhub 每日早报 | `api.readhub.cn/daily`（接口，JSON） | 直连可用 |
| Google News 中文 | `news.google.com/rss/search?q=大模型+OR+DeepSeek+when:1d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans` | 24 小时 66 条 |
| aibase AI日报、aibase 资讯 | RSSHub `/aibase/daily`、`/aibase/news` | 公共实例可用 |
| 36 氪快讯 | RSSHub `/36kr/newsflashes` | 公共实例可用；量大，要按关键词过滤 |
| 雷锋网快讯 | RSSHub `/leiphone/newsflash` | 公共实例可用 |

不可用：机器之心 RSS（空）、36 氪直连 RSS（空）、何夕2077 AI 日报（证书和 RSS 地址都有问题）、橘鸦 AI 早报（没找到 RSS；它本身就是 B 站上的 AI 早报节目，算竞品）。

### F. RSSHub

- 公共实例测了 19 个：`rsshub.app` 返回 403，只有 rsshub.ktachibana.party 和 rsshub.isrss.com 能用，而且经常 429 / 502 / 503。
- 可用的路由：`/qwen/blog`、`/anthropic/news`、`/aibase/*`、`/readhub/daily`、`/36kr/newsflashes`、`/qbitai/*`、`/leiphone/newsflash`。`/deepseek/news` 返回空，`/openai/chatgpt/release-notes` 和 `/twitter/*` 不可用。
- 想稳定就在本机用 Docker 自建（免费；这台电脑装了 Docker Desktop）。要装需要用户同意。

## 发布时间实测（2026-09-27）

方法：抓下表各源 2024-09 以来的发布时间戳，换算成北京时间，统计各时段占比。只用带真实时刻的源。

| 类别（条数） | 07–11 | 11–14 | 14–19 | 19–23 | 23–04 | 04–07 |
|---|---|---|---|---|---|---|
| 美国官方博客（258）：DeepMind、Google AI、Google Research、NVIDIA、AWS | 2% | 1% | 13% | 16% | **60%** | 9% |
| 美国发版信号（346）：OpenAI / Anthropic / Google SDK、Claude Code、Codex 的 GitHub 发版 + HF 模型上传 | 12% | 6% | 18% | 13% | **34%** | 18% |
| 国内厂商（295）：DeepSeek、Qwen、Kimi、智谱、MiniMax 的 HF 上传和 GitHub 建仓 | 7% | **24%** | **39%** | **27%** | 4% | 0% |
| 英文科技媒体（125）：Techmeme、The Verge、TechCrunch 等 | 15% | 4% | 2% | 20% | **43%** | 16% |

按星期（早上 7 点那期收录的条数占比）：

| | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |
|---|---|---|---|---|---|---|---|
| 美国官方 | 2% | 11% | 20% | 22% | 21% | 19% | 5% |
| 国内厂商 | 16% | 20% | 15% | 18% | 11% | 14% | 5% |

- 最近两周每期平均约 7 条一手候选（中位数 7），去掉客户案例、游戏推广后通常剩 3–5 条。
- **OpenAI 官方 RSS 的时刻是占位值**：86% 是整点，集中在 GMT 00:00 和 10:00。GPT-5 实际在美西上午 10 点发布，RSS 里写的是 GMT 00:00 和 10:00。
- HF 上传比官宣早（先传模型再发公告），只作参考。
- **11 月 1 日美国结束夏令时**，美国上午整体晚 1 小时（北京 00:00–05:00）。04:30 触发时，美西 12:30 以后发的进第二天。

## B 站和合规（2026-09-27 调研）

- **定时发布**：
  - 投稿页代码里默认最早提前 4 小时、最晚 15 天；服务器会按账号下发实际范围，登录后在开关旁边能看到。
  - 2026-09-27 实测：这个账号投稿页显示 5 分钟后到 15 天内。
  - 定时稿件会先审核，状态显示“通过审核，等待定时发布中”。
- **审核时长**：没有官方时限。网上说法从几分钟到几小时，忙时约 24 小时；4 小时后可以找客服催审。
- **分区**（2025 年改版后）：「人工智能」下有 AI学习、**AI资讯**、AI杂谈。备选「科技数码 → 科技数码综合」。不用「资讯」区（含时政）。
- **AI 标识**：
  - 依据是《人工智能生成合成内容标识办法》（2025-09-01 施行）第 10 条：上传者要主动声明，并使用平台的标识功能。勾 B 站创作声明满足这一条（调研方的理解，不是法律意见）。
  - GB 45438-2025 对合成语音要求语音提示或节奏提示，所以原方案在片头加一句配音声明。用户 2026-09-27 否决（太割裂），配音和画面都不加，靠创作声明 + 简介。以后想加又不割裂，可以考虑标准里的节奏提示。
  - 像素主播是手画的，不算 AI 生成形象。
- **新闻许可**：
  - 《互联网新闻信息服务管理规定》管的是时政、经济、军事、外交等公共事务和突发事件；个人申请不了许可。
  - AI 产品和行业动态一般不在范围内（律所意见，不是官方口径）。
  - 实际边界：注明来源；账号名和简介不用“新闻”“报道”；不做电视演播室那种画面（清朗 2023）；不碰时政、制裁、中美政策。
- **形象授权**：大肥鱼同人形象“不可商用”（CC BY-NC-SA / ZipZipPipe 声明），开激励、充电或接商单前要重新评估。
- **自动上传工具**（用户已选插件，只作记录）：biliup-rs 2025-11-30 归档并入 biliup（v1.2.9，2026-09-26）；B 站开放平台“暂未开通个人开发者的申请入驻”。

## 目录（建议）

```text
D:\大疆\AI日报\                系列根（给《原LAI如此》的脚本当 --series 用）
  collector\  sources.yaml、collect.py、seen.sqlite、snapshots\、health\
  素材\       字体、音频 → 目录联接到 AI科普\素材\ 的对应目录
              角色\动作帧 → 目录联接到 AI科普\素材\角色\大肥鱼像素素材包\素材（同样的 anims.json 格式）
              背景图库\  速报自己的背景（自己生成，蓝色系）
  片头片尾\   → 目录联接到 AI科普\片头片尾（只读复用）
  skill\ai-daily-news\  单次运行的技能：SKILL.md、scripts\（新写或改过的脚本）、assets\engine-template\（速报版面）、assets\cover-template\
  2026-09-28\  每天一期，直接放在系列根下（引擎按 ../../../素材/ 找素材）：
              state.json、items.jsonl、candidates.json、picks.json、台本.json、episode.json、台本\、配音\、制作\、
              成片.mp4、上传版.mp4、封面\、审稿单.md、投稿信息.json、发布记录.json
```

- 能直接复用的《原LAI如此》脚本（不改原文件，用 `--series D:\大疆\AI日报` 调）：chunk_voice、fetch_check、select_takes、segment_audio、build_timeline、mix_audio、render_parallel、assemble。
- 要新写或复制后改的：`collect.py`、`台本.json` → `script_data.py` / `episode.json` 的转换、核对脚本、审稿单、速报版面（引擎模板复制一份改）、封面模板。
- 素材只通过目录联接读取，不往 `AI科普\` 里写东西。

## 要搭的东西（按顺序）

1. `collect.py` + `sources.yaml`（按上面实测的源）+ `seen.sqlite`。先连跑几天“只抓取”，看每天的条数和误报。
2. 大肥鱼接入引擎（角色包参数），出一张速报版面样片给用户看。
3. 配音：插件操作 Fish Audio 网页版（「苏晓晓」，S1），沿用第 1 期的分批、下载、打分、切句脚本。
4. `ai-daily-news` 技能：选题规则、写稿规则、`check_script.py`、审稿单模板。
5. 速报片头、封面模板、上传版编码。
6. 插件发布流程，按第 1 期的踩坑清单。
7. 我陪着用当天的真实新闻完整跑一次；用户审核、发布没问题后，再设 routine。

## 成本

- 信息源：0。
- 配音：Fish Audio `s2.1-pro-free` 免费；付费模型一期约 0.04 美元（每月约 1 美元）。
- 选题、写稿、发布：routine 里 Claude 的用量。
- 这台电脑在触发时要开着：插电，合盖不睡眠。

## 待用户决定

v3 已定：标题、合集、配音、RSS、片头片尾、发布、时长（见文首）。还剩下面几项，没说就按默认：

1. **上线时间**：默认审核通过后立即投稿（07:00 前上线不保证）。要准点 07:00 可以用定时发布（这个账号最早 5 分钟后，2026-09-27 实测）。
2. **AI 标识**：已定（2026-09-27）：配音和画面都不出现，创作声明选「含AI生成内容」+ 简介写明。
3. **自建 RSSHub**（Docker）：默认不装，用公共实例，挂了就跳过那几个中文源。
4. **routine 在哪跑**：要能用这台电脑的 Chrome 插件和 D 盘文件。
5. **片尾清单**：「新闻来源」（按本期自动填，最多两行）、「形象 大肥鱼同人（上善无形 / ZipZipPipe）」、「视频制作模型 Opus 5.5」，结束语“感谢大家看到最后”，署名 UE。原来还有「配音 Fish Audio · 苏晓晓（AI 合成）」，用户 2026-09-27 要求去掉。
