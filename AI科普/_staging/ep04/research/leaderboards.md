# 榜单快照：国内外大模型（截至 2026-09-28）

> 用途：B 站《大肥鱼锐评：截至 2026 下半年，国内外大模型从夯到拉》的数据底稿。全片用**一个分数**、**一个价格**，口径见第 0 节。
> 访问日期：全部 2026-09-28（日本时间上午抓取）。抓法：直接下载各榜单网页里内嵌的数据（Artificial Analysis 的页面数据、OpenRouter 的公开接口、ARC Prize / Epoch / METR 的公开数据文件），不是凭记忆，也不是转述。
> 标注：没标的都是**第三方榜单原始数据**；**【自算】**= 我们用榜单原始数据算出来的（比如按厂商汇总）；**【未核实】**= 只找到二手说法或口径不确定，不要直接上屏。
> 本会话的网页搜索额度已用完，所以没有再搜新闻；所有数字都来自下面列出的网址本身。

## 0. 先看这里：视频统一口径（建议）

- **分数 = Artificial Analysis Intelligence Index v4.3.2（AA 智能指数）**，每个模型取 AA 上**最高的那一档**（多数是 max，Grok 是 xhigh）。AA 页面显示整数，排序用一位小数。对 1.3 节前 40 名，"最高档"就是 AA 模型页默认打开的那一档（例：artificialanalysis.ai/models/claude-opus-5-5 = max），观众自己去查能对上。
- **价格 = AA 的 3:1 混合价**：(3 × 输入价 + 1 × 输出价) ÷ 4，美元 / 百万 token，按标价、不算缓存。AA 数据字段 `price1mBlended0To3To1`。
  - 注意：AA 方法论页现在把 "Blended price" 定义成 **7:2:1（缓存命中 : 输入 : 输出）**，同一个模型数字会小很多（Opus 5.5：3:1 是 $8.00，7:2:1 是 $2.94）。两种口径别混。下表两种都给了。
  - AA 排行榜页面默认那一列价格是 **Cost per Task（每道指数题的平均花费）**，不是每百万 token 价格。有转述文章把它当成了 "blended price"，别跟。
- **第二个价格维度（可选）= 每任务成本**：它算上了模型"话多不多"（推理 token），更接近真实账单。比如 Qwen3.8 Max 标价只要 $2/$6，但每任务 $5.41，快赶上 Opus 5.5 max 的 $5.98。
- **AA 没测或只有估算分的模型**（豆包 Seed 2.x、文心 5.1、混元 Hy4 preview 等）：画面标"AA 未测"，用 LMArena 分数做旁证（第 2 节），不要把不同榜的分数放在同一把尺子上。
- 分数不能跨版本比：AA 在 2026-09-07 换成 v4.3（Terminal-Bench 4.0 等更难的题），整体比 8 月的 v4.1 低一截。只用本文件里这次抓的 v4.3.2 数。

## 1. Artificial Analysis 智能指数（AA Intelligence Index）

### 1.1 版本和构成

- 当前版本 **v4.3.2**（评测页标题和方法论页都写 v4.3.2；v4.3 发布文章日期 2026-09-07）。10 项评测，四大类：

| 类别（权重） | 评测（权重） |
|---|---|
| 智能体 Agents（30%） | AA-Briefcase v1.1（15%）、GDPval-AA v2.1（10%）、AutomationBench-AA（5%） |
| 编程 Coding（20%） | Terminal-Bench 4.0（10%）、SciCode（10%） |
| 通用 General（30%） | AA-Omniscience 准确率（10%）+ 不幻觉率（5%）、GDP.pdf（10%）、AA-LCR v1.1（5%） |
| 科学推理 Scientific Reasoning（20%） | Humanity's Last Exam（10%）、CritPt（10%） |

- 版本变化（方法论页 Version History）：v4.3（2026-09）用 AutomationBench-AA 换掉 τ³-Banking、Terminal-Bench 2.1 换成 4.0（66 题）；v4.3.1 把两两对比的裁判换成 Claude Opus 5 / GPT-5.6 Sol / Gemini 3.8 Flash；v4.3.2 把 GDPval-AA v2.1 的 Elo 锚定到 DeepSeek V4.1 Flash (max) = 1600。v4.2（2026-09）去掉了 GPQA Diamond。
- AA 方法论页说指数的 95% 置信区间小于 ±1%（指数是百分制）。所以相差 1 分以内建议当并列说。
- 本次抓到的数据：674 个模型档位，其中在榜（未下架）270 个，有指数分的 266 个。排行榜页、Opus 5.5 模型页、MiMo-V2.6-Pro 模型页三份内嵌数据逐条对比，分数和价格完全一致。
- "（估）" = AA 数据里 `intelligenceIndexIsEstimated = true`（页面上显示为分数后面带 *），是估算分，不是完整跑完 v4.3.2 的实测分。
- 价格来源（方法论页）：模型首方 API 标价，或各托管商的中位数。

### 1.2 AA 排行榜前 35 行（按"档位"原样排，未下架的）

| # | 模型（AA 显示名） | 厂商 | 指数 | 开放权重 | 输入 / 输出 $/1M | 3:1 混合价 | 7:2:1 混合价 | 每任务成本 | 跑完整个指数 | 速度 tok/s | 发布日 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Claude Opus 5.5 (max with fallback) | Anthropic | 57.6 | 否 | 4 / 20 | $8.00 | $2.94 | $5.98 | $8,708 | 94 | 2026-09-22 |
| 2 | Claude Opus 5.5 (xhigh with fallback) | Anthropic | 56.0 | 否 | 4 / 20 | $8.00 | $2.94 | $3.46 | $4,057 | 88 | 2026-09-22 |
| 3 | Claude Opus 5.5 (high with fallback) | Anthropic | 53.6 | 否 | 4 / 20 | $8.00 | $2.94 | $1.82 | $2,172 | 81 | 2026-09-22 |
| 4 | Claude Fable 5.1 (max with fallback) | Anthropic | 53.4 | 否 | 10 / 50 | $20.00 | $7.17 | $7.63 | $13,129 | 69 | 2026-09-01 |
| 5 | Claude Fable 5.1 (xhigh with fallback) | Anthropic | 53.2 | 否 | 10 / 50 | $20.00 | $7.17 | $5.98 | $9,063 | 67 | 2026-09-01 |
| 6 | GPT-6 Astra (max) | OpenAI | 52.7 | 否 | 10 / 50 | $20.00 | $7.70 | $3.26 | $5,324 | 63 | 2026-09-03 |
| 7 | GPT-6 Astra (xhigh) | OpenAI | 52.4 | 否 | 10 / 50 | $20.00 | $7.70 | $2.31 | $3,803 | 57 | 2026-09-03 |
| 8 | Claude Opus 5.5 (medium with fallback) | Anthropic | 51.2 | 否 | 4 / 20 | $8.00 | $2.94 | $1.34 | $1,627 | 82 | 2026-09-22 |
| 9 | Claude Fable 5.1 (high with fallback) | Anthropic | 51.2 | 否 | 10 / 50 | $20.00 | $7.17 | $3.91 | $5,242 | 57 | 2026-09-01 |
| 10 | GPT-6 Astra (high) | OpenAI | 50.9 | 否 | 10 / 50 | $20.00 | $7.70 | $1.73 | $2,925 | 60 | 2026-09-03 |
| 11 | GPT-6 Astra (medium) | OpenAI | 49.6 | 否 | 10 / 50 | $20.00 | $7.70 | $1.54 | $2,434 | 57 | 2026-09-03 |
| 12 | Claude Fable 5.1 (medium with fallback) | Anthropic | 48.9 | 否 | 10 / 50 | $20.00 | $7.17 | $2.98 | $3,983 | 58 | 2026-09-01 |
| 13 | Muse Spark 1.3 (max) | Meta | 48.1 | 否 | 1.25 / 4.25 | $2.00 | $0.78 | $1.60 | $2,000 | 205 | 2026-09-02 |
| 14 | GPT-6 Sol (max) | OpenAI | 47.5 | 否 | 2 / 10 | $4.00 | $1.54 | $1.06 | $1,550 | 87 | 2026-09-22 |
| 15 | Claude Fable 5.1 (low with fallback) | Anthropic | 46.8 | 否 | 10 / 50 | $20.00 | $7.17 | $2.37 | $3,158 | 58 | 2026-09-01 |
| 16 | Grok 4.7 (xhigh) | SpaceXAI | 46.4 | 否 | 2 / 6 | $3.00 | $1.35 | $3.74 | $4,967 | 83 | 2026-09-21 |
| 17 | Grok 4.7 (high) | SpaceXAI | 46.3 | 否 | 2 / 6 | $3.00 | $1.35 | $2.73 | $3,881 | 83 | 2026-09-21 |
| 18 | MiMo-V2.6-Pro | Xiaomi | 46.3 | 是 | 0.435 / 0.87 | $0.54 | $0.18 | $0.13 | $207 | 44 | 2026-09-21 |
| 19 | GPT-6 Astra (low) | OpenAI | 45.8 | 否 | 10 / 50 | $20.00 | $7.70 | $0.82 | $1,537 | 55 | 2026-09-03 |
| 20 | Qwen3.8 Max (0902) | Alibaba | 45.4 | 否 | 2 / 6 | $3.00 | $1.18 | $5.41 | $4,935 | 39 | 2026-09-02 |
| 21 | Muse Spark 1.3 (xhigh) | Meta | 45.1 | 否 | 1.25 / 4.25 | $2.00 | $0.78 | $1.37 | $1,655 | 261 | 2026-09-02 |
| 22 | GLM-5.3 (max) | Z AI | 44.8 | 是 | 1.4 / 4.4 | $2.15 | $0.90 | $2.01 | $2,503 | 87 | 2026-08-18 |
| 23 | Grok 4.6 (high) | SpaceXAI | 44.3 | 否 | 2 / 6 | $3.00 | $1.35 | $1.86 | $2,352 | 66 | 2026-08-12 |
| 24 | Grok 4.6 (xhigh) | SpaceXAI | 44.2 | 否 | 2 / 6 | $3.00 | $1.35 | $2.32 | $2,830 | 75 | 2026-08-12 |
| 25 | GPT-6 Sol (xhigh) | OpenAI | 44.1 | 否 | 2 / 10 | $4.00 | $1.54 | $0.53 | $865 | 83 | 2026-09-22 |
| 26 | Step 5 Preview | StepFun | 43.7 | 否 | 1 / 2.7 | $1.43 | $0.51 | $0.72 | $929 | 72 | 2026-09-18 |
| 27 | Kimi K3 (max) | Kimi | 43.6 | 是 | 3 / 15 | $6.00 | $2.31 | $2.00 | $3,658 | — | 2026-07-16 |
| 28 | Grok 4.6 (medium) | SpaceXAI | 42.8 | 否 | 2 / 6 | $3.00 | $1.35 | $1.50 | $1,937 | 69 | 2026-08-12 |
| 29 | GPT-6 Sol (high) | OpenAI | 42.8 | 否 | 2 / 10 | $4.00 | $1.54 | $0.37 | $610 | 83 | 2026-09-22 |
| 30 | Claude Opus 5.5 (low with fallback) | Anthropic | 42.3 | 否 | 4 / 20 | $8.00 | $2.94 | $0.55 | $860 | 79 | 2026-09-22 |
| 31 | GPT-5.6 Terra (max) | OpenAI | 42.1 | 否 | 2 / 12 | $4.50 | $1.74 | $1.40 | $2,501 | 102 | 2026-07-09 |
| 32 | GLM-5.3-Flash | Z AI | 41.8 | 是 | 0.15 / 0.5 | $0.24 | $0.098 | $0.25 | $280 | 55 | 2026-08-26 |
| 33 | Gemini 3.8 Flash (high) | Google | 40.9 | 否 | 0.75 / 3.75 | $1.50 | $0.58 | $1.24 | $1,623 | 285 | 2026-09-02 |
| 34 | Qwen3.8 2.4T A95B | Alibaba | 39.9 | 是 | 2 / 6 | $3.00 | $1.18 | $2.16 | $2,633 | 39 | 2026-08-12 |
| 35 | Qwen3.8-Flash-Next | Alibaba | 39.8 | 是 | 0.15 / 0.47 | $0.23 | $0.088 | $0.37 | $363 | 57 | 2026-08-26 |

- "每任务成本" = AA 的 Cost per Task（跑一道指数题的加权平均花费）；"跑完整个指数" = AA 模型页的 Cost to Run Artificial Analysis Intelligence Index（跑完全部 10 项评测的总花费）。两者差几百到上千倍，别混。
- 速度 = 排行榜的 Median Tokens/s（输出速度中位数）；"—" = AA 没测到。

### 1.3 按模型去重：每个模型只取最高档（视频主表用这个）

| 名次 | 模型 | 取的档位 | 厂商 | 国别 | 指数 | 取整 | 开放权重 | 3:1 混合价 $/1M | 每任务成本 | 跑完整个指数 | 速度 tok/s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Claude Opus 5.5 | max | Anthropic | 美 | 57.6 | 58 | 否 | $8.00 | $5.98 | $8,708 | 94 |
| 2 | Claude Fable 5.1 | max | Anthropic | 美 | 53.4 | 53 | 否 | $20.00 | $7.63 | $13,129 | 69 |
| 3 | GPT-6 Astra | max | OpenAI | 美 | 52.7 | 53 | 否 | $20.00 | $3.26 | $5,324 | 63 |
| 4 | Muse Spark 1.3 | max | Meta | 美 | 48.1 | 48 | 否 | $2.00 | $1.60 | $2,000 | 205 |
| 5 | GPT-6 Sol | max | OpenAI | 美 | 47.5 | 48 | 否 | $4.00 | $1.06 | $1,550 | 87 |
| 6 | Grok 4.7 | xhigh | SpaceXAI | 美 | 46.4 | 46 | 否 | $3.00 | $3.74 | $4,967 | 83 |
| 7 | MiMo-V2.6-Pro | （单档） | Xiaomi | 中 | 46.3 | 46 | 是 | $0.54 | $0.13 | $207 | 44 |
| 8 | Qwen3.8 Max (0902) | （单档） | Alibaba | 中 | 45.4 | 45 | 否 | $3.00 | $5.41 | $4,935 | 39 |
| 9 | GLM-5.3 | max | Z AI | 中 | 44.8 | 45 | 是 | $2.15 | $2.01 | $2,503 | 87 |
| 10 | Grok 4.6 | high | SpaceXAI | 美 | 44.3 | 44 | 否 | $3.00 | $1.86 | $2,352 | 66 |
| 11 | Step 5 Preview | （单档） | StepFun | 中 | 43.7 | 44 | 否 | $1.43 | $0.72 | $929 | 72 |
| 12 | Kimi K3 | max | Kimi | 中 | 43.6 | 44 | 是 | $6.00 | $2.00 | $3,658 | — |
| 13 | GPT-5.6 Terra | max | OpenAI | 美 | 42.1 | 42 | 否 | $4.50 | $1.40 | $2,501 | 102 |
| 14 | GLM 5.3 Flash | max | Z AI | 中 | 41.8 | 42 | 是 | $0.24 | $0.25 | $280 | 55 |
| 15 | Gemini 3.8 Flash | high | Google | 美 | 40.9 | 41 | 否 | $1.50 | $1.24 | $1,623 | 285 |
| 16 | Qwen3.8 2.4T A95B | （单档） | Alibaba | 中 | 39.9 | 40 | 是 | $3.00 | $2.16 | $2,633 | 39 |
| 17 | Qwen3.8-Flash-Next | （单档） | Alibaba | 中 | 39.8 | 40 | 是 | $0.23 | $0.37 | $363 | 57 |
| 18 | DeepSeek V4.1 Flash | max | DeepSeek | 中 | 39.5 | 39 | 是 | $0.52 | $0.27 | $477 | 221 |
| 19 | Claude Sonnet 5 | max | Anthropic | 美 | 38.2 | 38 | 否 | $4.00 | $5.09 | $6,998 | 75 |
| 20 | MiMo-V2.6-Flash | （单档） | Xiaomi | 中 | 37.9 | 38 | 是 | $0.18 | $0.062 | $109 | 62 |
| 21 | GPT-6 Luna | max | OpenAI | 美 | 37.3 | 37 | 否 | $0.20 | $0.068 | $122 | 163 |
| 22 | DeepSeek V4 Pro 0813 | max | DeepSeek | 中 | 36.0 | 36 | 是 | $1.98 | $0.67 | $1,122 | 100 |
| 23 | DeepSeek V4 Flash Vision | max | DeepSeek | 中 | 34.8 | 35 | 否 | $0.66 | $0.31 | $445 | 223 |
| 24 | Qwen3.8 27B | xhigh | Alibaba | 中 | 33.7 | 34 | 是 | $1.12 | $1.01 | $1,336 | 47 |
| 25 | Motif 3 | （单档） | Motif Technologies | 韩 | 33.6（估） | 34 | 是 | — | — | — | — |
| 26 | GPT-5.3 Codex | xhigh | OpenAI | 美 | 32.5（估） | 33 | 否 | $4.81 | — | — | 118 |
| 27 | Motif 3 (Beta) | （单档） | Motif Technologies | 韩 | 32.3（估） | 32 | 否 | — | — | — | — |
| 28 | K2 Horizon 375B A23B | （单档） | Institute of Foundation Models | 阿联酋 | 30.5 | 31 | 是 | — | — | — | — |
| 29 | Gemini 3.1 Pro Preview | （单档） | Google | 美 | 29.7 | 30 | 否 | $4.50 | $0.67 | $1,310 | 118 |
| 30 | MiniMax-M3 | （单档） | MiniMax | 中 | 29.2 | 29 | 是 | $0.52 | $0.51 | $538 | 174 |
| 31 | Nex-N2-Pro | （单档） | Nex AGI | 中 | 28.2（估） | 28 | 是 | — | — | — | — |
| 32 | Solar Pro 4 | （单档） | Upstage | 韩 | 28.2（估） | 28 | 否 | $0.52 | — | — | 93 |
| 33 | Inkling Small | （单档） | Thinking Machines | 美 | 27.8（估） | 28 | 是 | $0.52 | — | — | 208 |
| 34 | JT-4.1 Flash 236B A21B | （单档） | China Mobile | 中 | 27.3（估） | 27 | 否 | — | — | — | — |
| 35 | Quasar 438B | max | Multiverse Computing | 西 | 26.7 | 27 | 否 | $0.90 | $2.02 | $2,504 | 144 |
| 36 | Apodex 1.1 | （单档） | Apodex | 美 | 26.4 | 26 | 否 | $0.97 | $0.46 | $939 | — |
| 37 | GPT-5.5 Instant (June 2026) | （单档） | OpenAI | 美 | 26.0 | 26 | 否 | $11.25 | $0.69 | $1,184 | 147 |
| 38 | MiMo-V2.5-Pro | （单档） | Xiaomi | 中 | 26.0 | 26 | 是 | $0.54 | $0.054 | $138 | 39 |
| 39 | Kimi K2.7 Code | （单档） | Kimi | 中 | 25.8 | 26 | 是 | $1.71 | $0.54 | $993 | — |
| 40 | K2 Horizon MoVA 36B A4B | （单档） | Institute of Foundation Models | 阿联酋 | 25.3 | 25 | 是 | — | — | — | — |

- 去重后有分数的在榜模型共 187 个。上表只列前 40。
- "取的档位" = AA 数据里的推理强度（effort）标签；"（单档）" = AA 只测了一个设置。Anthropic 的档位在 AA 名称里都带 "with fallback"（全名如 "Adaptive Reasoning, Max Effort, Default Fallback"），具体指什么设置 AA 页面没解释【未核实】。
- 厂商名照 AA 原样：Kimi = 月之暗面，Z AI = 智谱，SpaceXAI = xAI（Grok），LongCat = 美团。

### 1.4 点名模型逐个对照

| 模型 | AA 家族名次 | 取的档位 | 指数 | 开放权重 | 输入 / 输出 $/1M | 3:1 混合价 | 每任务成本 | 跑完整个指数 | 速度 | AA 发布日 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-6 Astra | 3 | max | 52.7 | 否 | 10 / 50 | $20.00 | $3.26 | $5,324 | 63 | 2026-09-03 |  |
| GPT-6 Sol | 5 | max | 47.5 | 否 | 2 / 10 | $4.00 | $1.06 | $1,550 | 87 | 2026-09-22 | 2026-09-22 发布；AA 把 GPT-5.6 Sol 的替代者记为它 |
| GPT-6 Luna | 21 | max | 37.3 | 否 | 0.1 / 0.5 | $0.20 | $0.068 | $122 | 163 | 2026-09-22 | 最便宜的一档：$0.10 / $0.50 |
| GPT-5.6 Terra | 13 | max | 42.1 | 否 | 2 / 12 | $4.50 | $1.40 | $2,501 | 102 | 2026-07-09 | 仍在榜 |
| GPT-5.6 Sol | 已下架 | max | 47.0 | 否 | 4 / 20 | $8.00 | $1.99 | $3,465 | 98 | 2026-07-09 | AA 已标下架，替代者 = GPT-6 Sol，只作对比 |
| GPT-5.6 Luna | 已下架 | max | 37.3 | 否 | 0.2 / 1.2 | $0.45 | $0.18 | $320 | 128 | 2026-07-09 | AA 已标下架，替代者 = GPT-6 Luna |
| Claude Opus 5.5 | 1 | max | 57.6 | 否 | 4 / 20 | $8.00 | $5.98 | $8,708 | 94 | 2026-09-22 | AA 第 1 |
| Claude Fable 5.1 | 2 | max | 53.4 | 否 | 10 / 50 | $20.00 | $7.63 | $13,129 | 69 | 2026-09-01 |  |
| Claude Fable 5 | 已下架 | max | 49.6 | 否 | 10 / 50 | $20.00 | $8.75 | $11,161 | 64 | 2026-06-09 | AA 已标下架，替代者 = Fable 5.1；AA 全名写 Opus 4.8 Fallback |
| Claude Opus 5 | 已下架 | max | 50.8 | 否 | 5 / 25 | $10.00 | $5.86 | $7,275 | 60 | 2026-07-24 | AA 已标下架，替代者 = Opus 5.5 |
| Claude Sonnet 5 | 19 | max | 38.2 | 否 | 2 / 10 | $4.00 | $5.09 | $6,998 | 75 | 2026-06-30 |  |
| Gemini 3.8 Flash | 15 | high | 40.9 | 否 | 0.75 / 3.75 | $1.50 | $1.24 | $1,623 | 285 | 2026-09-02 | Google 在 AA 上的最高分 |
| Gemini 3.1 Pro Preview | 29 | （单档） | 29.7 | 否 | 2 / 12 | $4.50 | $0.67 | $1,310 | 118 | 2026-02-19 | AA 上最新的 Gemini Pro（2026-02），没有更新的 Pro |
| Grok 4.7 | 6 | xhigh | 46.4 | 否 | 2 / 6 | $3.00 | $3.74 | $4,967 | 83 | 2026-09-21 |  |
| DeepSeek V4.1 Flash | 18 | max | 39.5 | 是 | 0.3 / 1.2 | $0.52 | $0.27 | $477 | 221 | 2026-09-10 | DeepSeek 在 AA 上的最高分；Flash 比 Pro 高 |
| DeepSeek V4 Pro 0813 | 22 | max | 36.0 | 是 | 1.32 / 3.96 | $1.98 | $0.67 | $1,122 | 100 | 2026-08-13 |  |
| Qwen3.8 Max (0902) | 8 | （单档） | 45.4 | 否 | 2 / 6 | $3.00 | $5.41 | $4,935 | 39 | 2026-09-02 | 闭源；很费 token |
| Qwen3.8 2.4T A95B | 16 | （单档） | 39.9 | 是 | 2 / 6 | $3.00 | $2.16 | $2,633 | 39 | 2026-08-12 | 千问开放权重最强 |
| Kimi K3 | 12 | max | 43.6 | 是 | 3 / 15 | $6.00 | $2.00 | $3,658 | — | 2026-07-16 | 开放权重里最贵 |
| GLM-5.3 | 9 | max | 44.8 | 是 | 1.4 / 4.4 | $2.15 | $2.01 | $2,503 | 87 | 2026-08-18 | 开放权重第 2 |
| MiniMax-M3 | 30 | （单档） | 29.2 | 是 | 0.3 / 1.2 | $0.52 | $0.51 | $538 | 174 | 2026-06-01 |  |
| Doubao Seed Code | 67 | （单档） | 16.9（估） | 否 | — | — | — | — | — | 2025-11-11 | AA 只有这一个豆包，且是估算分；Seed 2.x 没收录 |
| Hy3（腾讯混元） | 41 | （单档） | 25.3 | 是 | 0.14 / 0.58 | $0.25 | $0.074 | $156 | 85 | 2026-07-06 | Hy4 preview 未收录 |
| ERNIE 5.0 Thinking Preview | 74 | （单档） | 14.3（估） | 否 | — | — | — | — | — | 2025-11-13 | 估算分；ERNIE 5.1 未收录 |
| LongCat 2.0（美团） | 61 | （单档） | 19.1 | 是 | 0.3 / 1.2 | $0.52 | $0.059 | $221 | — | 2026-06-29 |  |
| MiMo-V2.6-Pro | 7 | （单档） | 46.3 | 是 | 0.435 / 0.87 | $0.54 | $0.13 | $207 | 44 | 2026-09-21 | 开放权重第 1 |
| Step 5 Preview | 11 | （单档） | 43.7 | 否 | 1 / 2.7 | $1.43 | $0.72 | $929 | 72 | 2026-09-18 | AA 标为非开放权重 |
| Muse Spark 1.3（Meta，未点名） | 4 | max | 48.1 | 否 | 1.25 / 4.25 | $2.00 | $1.60 | $2,000 | 205 | 2026-09-02 | 闭源，家族第 4，值得一提 |

AA 完全没收录的（截至抓取时，在 OpenRouter 模型目录里已上架）：

| 模型 | OpenRouter 上架日 | OpenRouter 标价 入/出 $/1M | 说明 |
|---|---|---|---|
| Tencent: Hy4 preview | 2026-08-28 | 0.834 / 2.501 | 腾讯混元新一代预览；OpenRouter 周用量第 4、月用量第 2 |
| Qwen: Qwen3.8 Max Prime | 2026-09-23 | 4 / 12 | Qwen3.8 Max 的 Prime 档，09-23 上架，AA 未测 |
| Z.ai: GLM 5.3 Prime | 2026-09-23 | 2.8 / 8.8 | GLM 5.3 的 Prime 档，09-23 上架，AA 未测 |
| Xiaomi: MiMo-V2.6-Pro-UltraSpeed | 2026-09-21 | 4.35 / 8.7 | 小米高速版：小米称质量相同、输出最快 20 倍（unite.ai 转述）；OpenRouter 标价是 Pro 的 10 倍 |
| ByteDance Seed: Seed 2.1 Turbo | 2026-08-12 | 0.5 / 2.5 | 字节 Seed 2.1；AA 只有 Doubao Seed Code |
| OpenAI: GPT-6 Sol Pro | 2026-09-22 | 2 / 10 | OpenAI 的 Pro 档，AA 未单列 |

### 1.5 开放权重模型排名（每个模型取最高档）

| # | 模型 | 厂商 | 国别 | 指数 | 许可证（AA 记录） | 总参数 / 激活（十亿） | 3:1 混合价 | 跑完整个指数 |
|---|---|---|---|---|---|---|---|---|
| 1 | MiMo-V2.6-Pro | Xiaomi | 中 | 46.3 | MIT | 1020 / 42 | $0.54 | $207 |
| 2 | GLM-5.3 (max) | Z AI | 中 | 44.8 | GLM-5.3 License | 753 / 40 | $2.15 | $2,503 |
| 3 | Kimi K3 (max) | Kimi | 中 | 43.6 | Kimi K3 License | 2800 / 104 | $6.00 | $3,658 |
| 4 | GLM-5.3-Flash | Z AI | 中 | 41.8 | MIT | 320 / 18 | $0.24 | $280 |
| 5 | Qwen3.8 2.4T A95B | Alibaba | 中 | 39.9 | Qwen3.8-Max License | 2400 / 95 | $3.00 | $2,633 |
| 6 | Qwen3.8-Flash-Next | Alibaba | 中 | 39.8 | Qwen Community License 1.0 | 180 / 6 | $0.23 | $363 |
| 7 | DeepSeek V4.1 Flash (max) | DeepSeek | 中 | 39.5 | MIT | 552 / 16 | $0.52 | $477 |
| 8 | MiMo-V2.6-Flash | Xiaomi | 中 | 37.9 | — | — | $0.18 | $109 |
| 9 | DeepSeek V4 Pro 0813 (max) | DeepSeek | 中 | 36.0 | MIT | 1600 / 49 | $1.98 | $1,122 |
| 10 | Qwen3.8 27B (xhigh) | Alibaba | 中 | 33.7 | Apache 2.0 | 27 / — | $1.12 | $1,336 |
| 11 | Motif 3 | Motif Technologies | 韩 | 33.6（估） | — | 314 / 13.2 | — | — |
| 12 | K2 Horizon 375B A23B | Institute of Foundation Models | 阿联酋 | 30.5 | Apache 2.0 | 375 / 23 | — | — |
| 13 | MiniMax-M3 | MiniMax | 中 | 29.2 | MINIMAX COMMUNITY LICENSE | 428 / 23 | $0.52 | $538 |
| 14 | Nex-N2-Pro | Nex AGI | 中 | 28.2（估） | Apache 2.0 | 397 / 17 | — | — |
| 15 | Inkling Small | Thinking Machines | 美 | 27.8（估） | Apache 2.0 | 266 / 12 | $0.52 | — |

- **开放权重第一 = 小米 MiMo-V2.6-Pro，46.3 分**（MIT 许可，1.02T 总参数 / 42B 激活），和闭源的 Grok 4.7 (xhigh) 46.4 分基本并列。AA 模型页、unite.ai 报道（2026-09-21 发布、09-23 更新）说法一致：46 分、每任务 $0.13、跑完整个指数 $206.66。
- 开放权重前 10 名全是中国模型；第一个非中国的是韩国 Motif 3（估算 33.6）、阿联酋 K2 Horizon（30.5）。美国最高的开放权重是 Thinking Machines 的 Inkling Small（估算 27.8）。

### 1.6 容易踩的坑（二手数字对不上的地方）

| 出处 | 它写的 | AA 当前 v4.3.2 实际 | 判断 |
|---|---|---|---|
| BenchLM.ai「AA Intelligence Index Leaderboard (September 2026)」（页面写 2026-09-27 更新） | GPT-5.6 Sol 58.9 第 1、DeepSeek V4 Pro 0813 53.2、Gemini 3.5 Flash 50.2 | GPT-5.6 Sol (max) 47.0（已下架）、DeepSeek V4 Pro 0813 36.0、Gemini 3.5 Flash 32.6（已下架） | 像是旧版本（v4.1）的数，**不要用**【未核实其来源版本】 |
| OpenRouter 排行页「Benchmarks」小组件（数据截至 2026-09-27） | Qwen3.8 Max 53.4，排第 3 | Qwen3.8 Max 0803 版 40.2（已下架）、0902 版 45.4 | 对不上，疑似旧版数据或匹配错，**不要用** |
| 用网页转文字工具读 AA 排行榜（本次调研就遇到过） | 把价格列读成 "Blended Price"：Opus 5.5 max $5.98 | $5.98 是每任务成本；3:1 混合价是 $8.00 | 列名看错 |
| 本目录 `cn_models.md` 0.1 节第二张表"跑完整套指数的成本"一列 | DeepSeek V4.1 Flash $0.27、Qwen3.8 Max $5.41 | 这是每任务成本；跑完整个指数分别是 $477、$4,935 | 列名写错（"贵 20 倍"按每任务成本成立，按总成本约 10 倍） |

## 2. LMArena 文本榜（网站现在在 arena.ai，旧网址 lmarena.ai 自动跳转过去）

- 快照：页面显示 **Sep 25, 2026**；数据里 `voteCutoffISOString = 2026-09-25T22:00:00Z`，共 **8,528,723 票、409 个模型**。默认视图 = Overall（总榜）+ **Style Control（风格控制）开启**。
- 分数是 Bradley-Terry / Elo 式评分；"±" 是置信区间；"区间"= 名次可能的范围（Rank Spread）。标 Preliminary 的是票数还不够的初步分。

### 2.1 前 25 名

| 名次 | 名次区间 | 模型 | 厂商 · 许可 | 分数 | ± | 票数 | 标价 入/出 $/1M |
|---|---|---|---|---|---|---|---|
| 1 | 1–10 | claude-opus-5.5-high | Anthropic · Proprietary | 1509 | ±12 | 2,307 | $4 / $20 |
| 2 | 1–6 | claude-opus-4-6-high | Anthropic · Proprietary | 1505 | ±3 | 76,518 | $5 / $25 |
| 3 | 1–8 | claude-fable-5-high | Anthropic · Proprietary | 1504 | ±4 | 36,462 | $10 / $50 |
| 4 | 1–9 | claude-opus-4-7-high | Anthropic · Proprietary | 1502 | ±4 | 64,007 | $5 / $25 |
| 5 | 1–13 | claude-fable-5.1-max | Anthropic · Proprietary | 1501 | ±7 | 9,942 | $10 / $50 |
| 6 | 2–13 | claude-opus-4-6 | Anthropic · Proprietary | 1498 | ±3 | 80,836 | $5 / $25 |
| 7 | 1–21 | muse-spark-1.2 (xHigh) | Meta · Proprietary | 1496 | ±10 | 3,422 | $1.25 / $4.25 |
| 8 | 3–16 | claude-opus-4-7 | Anthropic · Proprietary | 1495 | ±4 | 65,051 | $5 / $25 |
| 9 | 2–20 | muse-spark-1.3-max | Meta · Proprietary | 1494 | ±7 | 10,036 | $1.25 / $4.25 |
| 10 | 4–20 | gemini-3.8-flash-high（Preliminary） | Google · Proprietary | 1492 | ±5 | 21,728 | $0.75 / $3.75 |
| 11 | 5–20 | claude-opus-5-high | Anthropic · Proprietary | 1491 | ±4 | 55,063 | $5 / $25 |
| 12 | 5–21 | muse-spark-1.1 | Meta · Proprietary | 1491 | ±5 | 34,760 | $1.25 / $4.25 |
| 13 | 5–28 | muse-spark | Meta · Proprietary | 1489 | ±6 | 14,131 | N/A |
| 14 | 7–28 | claude-opus-5-max | Anthropic · Proprietary | 1488 | ±5 | 26,760 | $5 / $25 |
| 15 | 7–28 | gemini-3.7-flash-high（Preliminary） | Google · Proprietary | 1488 | ±5 | 19,044 | $0.75 / $3.75 |
| 16 | 7–28 | kimi-k3-max | Moonshot · Kimi K3 license | 1488 | ±5 | 26,400 | N/A |
| 17 | 8–28 | gemini-3.1-pro-preview | Google · Proprietary | 1487 | ±3 | 119,196 | $1 / $6 |
| 18 | 8–28 | gemini-3-pro | Google · Proprietary | 1485 | ±4 | 41,921 | $2 / $12 |
| 19 | 8–35 | gpt-5.6-sol-xhigh | OpenAI · Proprietary | 1483 | ±5 | 34,258 | $4 / $20 |
| 20 | 11–39 | gemini-3.6-flash-high | Google · Proprietary | 1482 | ±5 | 33,739 | $0.75 / $3.75 |
| 21 | 13–37 | gpt-5.5-high | OpenAI · Proprietary | 1481 | ±4 | 69,008 | $5 / $30 |
| 22 | 13–40 | claude-opus-4-8-high | Anthropic · Proprietary | 1480 | ±4 | 61,560 | $5 / $25 |
| 23 | 8–47 | mimo-v2.6-pro | Xiaomi · MIT | 1480 | ±9 | 4,026 | $0.43 / $0.87 |
| 24 | 13–43 | glm-5.3-max | Z.ai · MIT | 1480 | ±6 | 15,904 | $1.40 / $4.40 |
| 25 | 13–42 | qwen3.8-max | Alibaba · Proprietary | 1479 | ±5 | 21,561 | $1.69 / $5.07 |

- 价格列是 LMArena 自己标的，和 AA 不一定一样（例：Gemini 3.1 Pro Preview 这里写 $1 / $6，AA 写 $2 / $12）。视频里的价格统一用 AA。

### 2.2 点名模型在 LMArena 文本榜的位置

| 模型 | LMArena 条目 | 名次 | 分数 | ± | 票数 |
|---|---|---|---|---|---|
| Claude Opus 5.5 | claude-opus-5.5-high | 1 | 1509 | ±12 | 2,307 |
| Claude Fable 5.1 | claude-fable-5.1-max | 5 | 1501 | ±7 | 9,942 |
| Muse Spark 1.3 | muse-spark-1.3-max | 9 | 1494 | ±7 | 10,036 |
| Gemini 3.8 Flash | gemini-3.8-flash-high | 10 | 1492 | ±5 | 21,728 |
| Kimi K3 | kimi-k3-max | 16 | 1488 | ±5 | 26,400 |
| Gemini 3.1 Pro Preview | gemini-3.1-pro-preview | 17 | 1487 | ±3 | 119,196 |
| GPT-5.6 Sol（旧） | gpt-5.6-sol-xhigh | 19 | 1483 | ±5 | 34,258 |
| MiMo-V2.6-Pro | mimo-v2.6-pro | 23 | 1480 | ±9 | 4,026 |
| GLM-5.3 | glm-5.3-max | 24 | 1480 | ±6 | 15,904 |
| Qwen3.8 Max | qwen3.8-max | 25 | 1479 | ±5 | 21,561 |
| GPT-6 Astra | gpt-6-astra-max | 26 | 1478 | ±8 | 7,185 |
| DeepSeek V4.1 Flash | deepseek-v4.1-flash-max | 29 | 1477 | ±8 | 6,630 |
| GLM-5.3-Flash | glm-5.3-flash | 35 | 1474 | ±6 | 19,103 |
| ERNIE 5.1（百度） | ernie-5.1 | 45 | 1468 | ±5 | 39,423 |
| GPT-5.6 Terra | gpt-5.6-terra-xhigh | 50 | 1465 | ±4 | 35,323 |
| DeepSeek V4 Pro 0813 | deepseek-v4-pro-high-20260813 | 53 | 1464 | ±7 | 9,857 |
| Claude Sonnet 5 | claude-sonnet-5-high | 54 | 1462 | ±4 | 43,340 |
| GPT-6 Sol | gpt-6-sol-max | 60 | 1457 | ±9 | 4,773 |
| Hy3（腾讯） | hy3 | 62 | 1457 | ±7 | 9,839 |
| Seed 2.0 Pro（字节，LMArena 名 dola-seed-2.0-pro） | dola-seed-2.0-pro | 64 | 1456 | ±3 | 78,783 |
| GPT-6 Luna | gpt-6-luna-max | 86 | 1442 | ±9 | 4,792 |
| MiniMax-M3 | minimax-m3 | 91 | 1440 | ±4 | 56,646 |
| Grok 4.7 | grok-4.7-xhigh | 92 | 1439 | ±9 | 4,114 |
| LongCat（美团，Flash Chat 2602 实验版，不是 LongCat 2.0） | longcat-flash-chat-2602-exp | 98 | 1437 | ±5 | 29,237 |
| Step 5 Preview | 文本榜没有 | — | — | — | — |
| Hy4 preview（腾讯） | 文本榜没有 | — | — | — | — |

- 票数少的新模型区间很宽：Opus 5.5 只有 2,307 票（±12），GPT-6 Sol / Luna、Grok 4.7 都只有 4–5 千票。上屏建议说"前几名 / 前二十左右"，别说精确名次。

## 3. OpenRouter 用量榜（"谁真的在被用"）

- 页面写 "Usage data through Sep 27, 2026"。按 token 数（输入 + 输出）排名；同一模型的免费版 / batch 版分开算。This Week = 截至 2026-09-27（UTC）的最近 7 天，This Month = 最近 30 天（2026-08-29 起）。
- 口径限制（OpenRouter 自己的说明）：只统计走 OpenRouter 的流量，不衡量用户数和花费；token 多只说明用得多，不说明更好。
- 数据特点【自算】：周、月两个窗口里输入 token 都占 97.5%；排行页的 Top Apps 前四是 Hermes Agent、Cline、Kilo Code、Claude Code（智能体 / 编程工具）。我们的解读：这张榜主要反映编程和智能体工具的调用量，便宜、长上下文的模型占便宜。
- 数据来自 OpenRouter 排行页用的公开接口 `openrouter.ai/api/frontend/v1/rankings/models?view=week|month`；排行页内嵌的前 20 名和接口算出的前 20 名是同一批模型。

### 3.1 周榜前 20（2026-09-21 ~ 09-27）

| # | 模型（OpenRouter slug） | 版本 | token 总量 | 其中输出 | 请求数 | 较上期 |
|---|---|---|---|---|---|---|
| 1 | deepseek/deepseek-v4.1-flash-20260910 | standard | 19.58T | 305B | 342M | +24% |
| 2 | z-ai/glm-5.3-flash-20260826 | standard | 16.32T | 212B | 376M | +16% |
| 3 | stealth/space-bunny-alpha | standard | 13.86T | 355B | 171M | 新 |
| 4 | tencent/hy4-preview-20260827 | standard | 9.64T | 83B | 84M | -23% |
| 5 | openai/gpt-5.6-luna-20260709 | standard | 8.53T | 117B | 252M | -12% |
| 6 | deepseek/deepseek-v4-flash-20260731 | standard | 7.82T | 304B | 508M | -17% |
| 7 | nvidia/nemotron-3-ultra-550b-a55b-20260604 | free | 5.67T | 26B | 42M | +26% |
| 8 | xiaomi/mimo-v2.6-flash-20260921 | standard | 5.51T | 73B | 69M | 新 |
| 9 | deepseek/deepseek-v4-flash-20260423 | standard | 3.35T | 217B | 338M | -11% |
| 10 | openai/gpt-6-luna-20260922 | standard | 2.86T | 88B | 127M | 新 |
| 11 | z-ai/glm-5.3-20260816 | standard | 2.80T | 42B | 39M | -7% |
| 12 | xiaomi/mimo-v2.5-20260422 | standard | 2.78T | 29B | 47M | -61% |
| 13 | typesafe/jev-1.13-20260917 | standard | 2.58T | 265B | 813M | +455% |
| 14 | tencent/hy3-20260706 | standard | 2.57T | 42B | 33M | -46% |
| 15 | google/gemini-3.8-flash-20260902 | standard | 2.16T | 66B | 68M | -2% |
| 16 | openai/gpt-5.6-sol-20260709 | standard | 1.68T | 25B | 34M | -20% |
| 17 | meta/muse-spark-1.3-contributor-20260902 | standard | 1.67T | 36B | 36M | -24% |
| 18 | upstage/solar-pro4-20260810 | standard | 1.63T | 17B | 21M | -1% |
| 19 | z-ai/glm-5.2-20260616 | standard | 1.50T | 51B | 53M | -10% |
| 20 | anthropic/claude-sonnet-5-20260630 | standard | 1.46T | 25B | 34M | -4% |

### 3.2 月榜前 20（2026-08-29 ~ 09-27）

| # | 模型（OpenRouter slug） | 版本 | token 总量 | 其中输出 | 请求数 | 较上期 |
|---|---|---|---|---|---|---|
| 1 | z-ai/glm-5.3-flash-20260826 | standard | 57.53T | 1,411B | 1,496M | +1644% |
| 2 | tencent/hy4-preview-20260827 | standard | 56.35T | 497B | 485M | +15390% |
| 3 | openai/gpt-5.6-luna-20260709 | standard | 51.92T | 1,000B | 1,821M | +140% |
| 4 | deepseek/deepseek-v4-flash-20260731 | standard | 44.00T | 1,674B | 2,151M | +4% |
| 5 | deepseek/deepseek-v4.1-flash-20260910 | standard | 40.28T | 640B | 674M | 新 |
| 6 | xiaomi/mimo-v2.5-20260422 | standard | 21.03T | 175B | 327M | -29% |
| 7 | nvidia/nemotron-3-ultra-550b-a55b-20260604 | free | 18.68T | 90B | 143M | +27% |
| 8 | deepseek/deepseek-v4-flash-20260423 | standard | 18.01T | 959B | 1,862M | -24% |
| 9 | tencent/hy3-20260706 | standard | 16.59T | 265B | 244M | -51% |
| 10 | stealth/space-bunny-alpha | standard | 13.86T | 355B | 171M | 新 |
| 11 | z-ai/glm-5.3-20260816 | standard | 11.72T | 204B | 186M | +713% |
| 12 | google/gemini-3.8-flash-20260902 | standard | 7.97T | 188B | 202M | 新 |
| 13 | z-ai/glm-5.2-20260616 | standard | 7.80T | 220B | 234M | -48% |
| 14 | openai/gpt-5.6-sol-20260709 | standard | 7.59T | 98B | 138M | +77% |
| 15 | minimax/minimax-m3-20260531 | free | 7.05T | 58B | 91M | +532% |
| 16 | moonshotai/kimi-k3-20260715 | standard | 6.70T | 108B | 111M | +11% |
| 17 | meta/muse-spark-1.3-contributor-20260902 | standard | 6.68T | 114B | 111M | 新 |
| 18 | upstage/solar-pro4-20260810 | standard | 6.41T | 70B | 158M | +388% |
| 19 | minimax/minimax-m3-20260531 | standard | 6.14T | 107B | 122M | -14% |
| 20 | anthropic/claude-sonnet-5-20260630 | standard | 5.93T | 97B | 121M | +26% |

点名模型的周用量名次：Claude Opus 5.5 第 25（1.08T）、MiMo-V2.6-Pro 第 26（1.07T）、GPT-6 Astra 第 27（1.03T）、DeepSeek V4 Pro 0813 第 28（1.02T）、GPT-6 Sol 第 31（0.77T）、Claude Fable 5.1 第 35（0.62T）、Grok 4.7 第 47（0.37T）、Qwen3.8 Max (0902) 第 57（0.26T）、Gemini 3.1 Pro Preview 第 70（0.20T）、LongCat 2.0 第 191。Step 5 Preview、ERNIE 5.x、豆包 Seed 2.0 Pro 不在 OpenRouter 目录里（字节只有 Seed 2.0 Mini/Lite/Code、Seed 2.1 Turbo，用量都很小）。

### 3.3 按厂商汇总【自算】

**周**：全部 520 个模型合计 145.8T token、6.67B 次请求。

| 厂商前缀 | token | token 占比 | 请求占比 | `total_usage` 占比【未核实：推测是花费】 |
|---|---|---|---|---|
| deepseek | 33.19T | 22.8% | 20.0% | 8.1% |
| z-ai | 21.10T | 14.5% | 7.4% | 10.7% |
| openai | 18.46T | 12.7% | 17.7% | 26.3% |
| stealth | 13.86T | 9.5% | 2.6% | 0.0% |
| tencent | 12.22T | 8.4% | 1.9% | 0.4% |
| xiaomi | 9.64T | 6.6% | 2.0% | 0.5% |
| google | 6.90T | 4.7% | 17.7% | 12.5% |
| nvidia | 6.63T | 4.5% | 1.1% | 0.1% |
| anthropic | 5.27T | 3.6% | 2.2% | 28.6% |
| qwen | 2.64T | 1.8% | 6.3% | 2.2% |
| typesafe | 2.58T | 1.8% | 12.2% | 0.4% |
| meta | 2.28T | 1.6% | 0.7% | 1.1% |

**月**：全部 544 个模型合计 543.5T token、25.19B 次请求。

| 厂商前缀 | token | token 占比 | 请求占比 | `total_usage` 占比【未核实：推测是花费】 |
|---|---|---|---|---|
| deepseek | 116.45T | 21.4% | 21.7% | 8.0% |
| openai | 81.38T | 15.0% | 20.7% | 26.8% |
| z-ai | 78.22T | 14.4% | 8.0% | 10.8% |
| tencent | 72.98T | 13.4% | 4.4% | 0.7% |
| google | 30.28T | 5.6% | 18.4% | 12.7% |
| xiaomi | 28.74T | 5.3% | 1.7% | 0.3% |
| nvidia | 24.02T | 4.4% | 1.1% | 0.1% |
| anthropic | 21.39T | 3.9% | 2.4% | 27.6% |
| stealth | 14.84T | 2.7% | 0.7% | 0.0% |
| minimax | 14.52T | 2.7% | 1.0% | 0.3% |
| qwen | 9.38T | 1.7% | 6.4% | 2.4% |
| meta | 8.52T | 1.6% | 0.6% | 0.8% |

- 这是用接口原始数据按 slug 前缀（厂商）加总的，不是 OpenRouter 官方的 Market Share 图（官方那张按请求数算）。`total_usage` 字段没有官方说明，从数值看像是美元花费，只作参考。

## 4. 其他常被引用的综合榜（只取和排前沿有关的头部数字）

### 4.1 Epoch Capabilities Index（ECI，Epoch AI）

- 数据文件 `epoch.ai/data/eci_scores.csv`，2026-09-28 下载；收录的最新模型发布日是 2026-09-09（DeepSeek V4.1 Flash）。**还没收录** Claude Opus 5.5、GPT-6 Sol / Luna、Grok 4.7、MiMo-V2.6、Step 5 Preview。

| # | 模型 | 机构 | ECI | 区间 | 发布日 | 权重 |
|---|---|---|---|---|---|---|
| 1 | GPT-6 Astra | OpenAI | 166.6 | 163.0–172.03 | 2026-09-03 | Closed weights |
| 2 | Claude Fable 5.1 | Anthropic | 165.0 | 161.64–169.61 | 2026-09-01 | Closed weights |
| 3 | Claude Fable 5 | Anthropic | 163.6 | 160.56–167.57 | 2026-06-09 | Closed weights |
| 4 | Claude Opus 5 | Anthropic | 162.67 | 159.96–166.52 | 2026-07-24 | Closed weights |
| 5 | GPT-5.5 Pro | OpenAI | 162.45 | 159.23–166.64 | 2026-04-23 | Closed weights |
| 6 | GPT-5.6 Sol | OpenAI | 161.99 | 159.64–165.92 | 2026-07-09 | Closed weights |
| 7 | GPT-5.6 Terra | OpenAI | 159.31 | 156.74–162.32 | 2026-07-09 | Closed weights |
| 8 | GPT-5.5 | OpenAI | 159.25 | 156.96–162.39 | 2026-04-23 | Closed weights |
| 9 | GPT-5.4 Pro | OpenAI | 159.12 | 156.65–162.44 | 2026-03-05 | Closed weights |
| 10 | Claude Opus 4.8 | Anthropic | 158.3 | 156.27–161.02 | 2026-05-28 | Closed weights |
| 11 | Gemini 3.7 Flash | Google DeepMind | 157.72 | 155.64–160.59 | 2026-08-13 | Closed weights |
| 12 | Kimi K3 | Moonshot | 157.68 | 155.12–160.65 | 2026-07-16 | Open weights |
| 13 | Gemini 3.8 Flash | Google DeepMind | 157.13 | 154.95–161.31 | 2026-09-02 | Closed weights |
| 14 | GPT-5.4 | OpenAI | 156.92 | 155.07–159.26 | 2026-03-05 | Closed weights |
| 15 | Muse Spark 1.3 | Meta AI | 156.89 | 154.66–159.44 | 2026-09-02 | Closed weights |

- 国产最高：Kimi K3 第 12（157.68）、Qwen 3.8 Max（0803 版）第 17（156.69）、GLM-5.3 第 22（155.56）、DeepSeek V4 Pro 0813 第 24（155.39）、DeepSeek V4.1 Flash 第 28（155.01）、MiniMax-M3 第 62（147.0）。ECI 把 GLM-5.3 记为 Closed weights，和 AA（开放权重）不同。

### 4.2 ARC Prize：ARC-AGI-3 和 ARC-AGI-2（半私有测试集）

- 数据文件 `arcprize.org/media/data/evaluations.json` + `models.json`（排行页用的就是这两个）。ARC-AGI-3 是交互式游戏环境；"Provider Adapter" 是另一种测试外壳（保留推理状态、压缩长对话），分数和标准外壳差很多，**必须分开说**。

ARC-AGI-3（每个模型 + 外壳组合取最高那一档）：

| # | 条目 | 厂商 | 得分 | 花费（数据里的 cost 字段，美元） |
|---|---|---|---|---|
| 1 | GPT-6 Astra - Provider Adapter (High) | OpenAI | 99.95% | 18,817 |
| 2 | GPT-6 Astra (Max) | OpenAI | 62.71% | 26,098 |
| 3 | Gemini 3.8 Flash - Provider Adapter (High) | Google | 35.00% | 4,522 |
| 4 | Claude Opus 5 (High) | Anthropic | 30.16% | 20,657 |
| 5 | Gemini 3.8 Flash (High) | Google | 10.37% | 4,398 |
| 6 | GPT-5.6 Sol (Max) | OpenAI | 7.78% | 25,064 |
| 7 | Grok 4.6 (XHigh) | xAI | 2.11% | 5,612 |
| 8 | Claude Opus 4.8 (High) | Anthropic | 1.52% | 10,000 |
| 9 | GPT-5.6 Terra (Max) | OpenAI | 0.80% | 7,918 |
| 10 | GPT-6 Luna - Provider Adapter (Max) | OpenAI | 0.59% | 237 |

- ARC-AGI-3 里**还没有** Claude Opus 5.5、Claude Fable 5.1、Grok 4.7、国产模型。Anthropic 最高是 Claude Opus 5 (High) 30.16%。排行页注释写"只显示花费低于 $10,000 的系统"，但数据里 ARC-AGI-3 的 cost 多数超过 $10,000，这个字段的含义【未核实】（可能是整套环境的总花费）。

ARC-AGI-2 前 10（人类测试组 100%）：

| # | 条目 | 得分 | 每题花费 $ |
|---|---|---|---|
| 1 | GPT-6 Astra (Max) | 95.00% | 1.12 |
| 2 | GPT-6 Astra (XHigh) | 93.33% | 0.83 |
| 3 | Claude Opus 5.5 (High) | 93.33% | 0.41 |
| 4 | GPT-5.6 Sol (Max) | 92.50% | 1.44 |
| 5 | Claude Opus 5.5 (XHigh) | 92.50% | 0.67 |
| 6 | GPT-6 Astra (High) | 92.08% | 0.67 |
| 7 | GPT-6 Astra (Medium) | 92.08% | 0.48 |
| 8 | Claude Opus 5.5 (Max) | 91.67% | 1.85 |
| 9 | Claude Opus 5 (Max) | 90.42% | 2.06 |
| 10 | GPT-5.6 Sol (XHigh) | 90.00% | 1.04 |

### 4.3 METR 任务时长（Time Horizon 1.1）

- 页面「LAST UPDATED May 8, 2026」，数据文件 `metr.org/assets/benchmark_results_1_1.yaml`。**2026 下半年发布的模型一个都没测**，不能用来排本期的模型。METR 自己说超过 16 小时的测量在现有题库上不可靠。

| 模型（METR 数据里的名字） | 发布 | 50% 成功时长 | 区间 | 80% 成功时长 |
|---|---|---|---|---|
| claude_mythos_preview_early_inspect | 2026-04-07 | 17.4 小时 | 8.5–55.1 小时 | 3.1 小时 |
| claude_opus_4_6_inspect | 2026-02-05 | 12.0 小时 | 5.3–60.6 小时 | 1.2 小时 |
| gemini_3_1_pro | 2026-02-19 | 6.4 小时 | 3.9–11.6 小时 | 1.5 小时 |
| gpt_5_2 | 2025-12-11 | 5.9 小时 | 3.3–13.6 小时 | 1.1 小时 |
| gpt_5_3_codex | 2026-02-05 | 5.8 小时 | 3.2–13.6 小时 | 0.9 小时 |
| gpt_5_4 | 2026-03-05 | 5.7 小时 | 3.1–12.8 小时 | 0.9 小时 |
| claude_opus_4_5_inspect | 2025-11-24 | 4.9 小时 | 2.7–10.4 小时 | 0.8 小时 |

- 翻倍时间（2023 年以来）：约 129 天（区间 104–158 天）。

### 4.4 编程：SWE-bench Pro（Scale 官方榜）和 DeepSWE（Epoch 收录）

- Scale 的 SWE-bench Pro 公开集排行（labs.scale.com/leaderboard/swe_bench_pro，旧址 scale.com/leaderboard/swe_bench_pro_public 会跳转）**没更新到 2026 下半年的模型**：第 1 是 Muse Spark 1.1（61.50 ±3.10），第 2 是 gpt-5.4 (xHigh)（59.10 ±3.56），然后 Muse Spark 55.00、claude-opus-4-6 (thinking) 51.90、gemini-3.1-pro (thinking) 46.10。没有 Claude 5.x、GPT-6、Kimi K3、GLM-5.3。**不建议拿来排本期模型**。厂商发布会上自报的 SWE-bench Pro 数字另见 intl_models.md / cn_models.md（都是厂商口径）。
- DeepSWE（Datacurve；Epoch 基准数据里收录的最新成绩，`epoch.ai/data/eci_benchmarks.csv`）：

| # | 模型 | 设置 | DeepSWE | 发布日 |
|---|---|---|---|---|
| 1 | GPT-6 Astra | gpt-6-astra_xhigh | 74.1% | 2026-09-03 |
| 2 | Gemini 3.8 Flash | gemini-3.8-flash_high | 73.8% | 2026-09-02 |
| 3 | Claude Opus 5 | claude-opus-5_max | 73.6% | 2026-07-24 |
| 4 | GPT-5.6 Sol | gpt-5.6-sol_max | 72.7% | 2026-07-09 |
| 5 | Claude Fable 5 | claude-fable-5_xhigh | 69.9% | 2026-06-09 |
| 6 | GPT-5.6 Terra | gpt-5.6-terra_max | 69.6% | 2026-07-09 |
| 7 | GLM-5.3 | glm-5.3_max | 69.0% | 2026-08-14 |
| 8 | Kimi K3 | kimi-k3_max | 68.5% | 2026-07-16 |

- 同一份 Epoch 数据里的 FrontierMath Tier 4（v2，私有题）：GPT-6 Astra 97.6%、Claude Fable 5 90.2%、Claude Fable 5.1 87.8%；Remote Labor Index：GPT-6 Astra 20.8%、Claude Fable 5.1 17.9%。

## 5. 交叉对照：同一个模型在几个榜上的位置

| 模型 | AA 指数（家族名次） | 3:1 混合价 | LMArena 文本（名次 / 分） | OpenRouter 周用量（名次 / token） | Epoch ECI（名次 / 分） |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 57.6（1） | $8.00 | 1 / 1509 | 25 / 1.08T | 未收录 |
| Claude Fable 5.1 | 53.4（2） | $20.00 | 5 / 1501 | 35 / 0.62T | 2 / 165.0 |
| GPT-6 Astra | 52.7（3） | $20.00 | 26 / 1478 | 27 / 1.03T | 1 / 166.6 |
| Muse Spark 1.3 | 48.1（4） | $2.00 | 9 / 1494 | 17 / 1.67T | 15 / 156.89 |
| GPT-6 Sol | 47.5（5） | $4.00 | 60 / 1457 | 31 / 0.77T | 未收录 |
| Grok 4.7 | 46.4（6） | $3.00 | 92 / 1439 | 47 / 0.37T | 未收录 |
| MiMo-V2.6-Pro | 46.3（7） | $0.54 | 23 / 1480 | 26 / 1.07T | 未收录 |
| Qwen3.8 Max (0902) | 45.4（8） | $3.00 | 25 / 1479 | 57 / 0.26T | 26 / 155.28 |
| GLM-5.3 | 44.8（9） | $2.15 | 24 / 1480 | 11 / 2.80T | 22 / 155.56 |
| Step 5 Preview | 43.7（11） | $1.43 | 未上榜 | 不在 OpenRouter | 未收录 |
| Kimi K3 | 43.6（12） | $6.00 | 16 / 1488 | 21 / 1.39T | 12 / 157.68 |
| GPT-5.6 Terra | 42.1（13） | $4.50 | 50 / 1465 | 38 / 0.54T | 7 / 159.31 |
| GLM-5.3-Flash | 41.8（14） | $0.24 | 35 / 1474 | 2 / 16.32T | 41 / 151.9 |
| Gemini 3.8 Flash | 40.9（15） | $1.50 | 10 / 1492 | 15 / 2.16T | 13 / 157.13 |
| DeepSeek V4.1 Flash | 39.5（18） | $0.52 | 29 / 1477 | 1 / 19.58T | 28 / 155.01 |
| Claude Sonnet 5 | 38.2（19） | $4.00 | 54 / 1462 | 20 / 1.46T | 20 / 156.34 |
| GPT-6 Luna | 37.3（21） | $0.20 | 86 / 1442 | 10 / 2.86T | 未收录 |
| DeepSeek V4 Pro 0813 | 36.0（22） | $1.98 | 53 / 1464 | 28 / 1.02T | 24 / 155.39 |
| Gemini 3.1 Pro Preview | 29.7（29） | $4.50 | 17 / 1487 | 70 / 0.20T | 29 / 154.92 |
| MiniMax-M3 | 29.2（30） | $0.52 | 91 / 1440 | 22 / 1.37T | 62 / 147.0 |
| Hy3（腾讯） | 25.3（41） | $0.25 | 62 / 1457 | 14 / 2.57T | 未收录 |
| LongCat 2.0（美团） | 19.1（61） | $0.52 | 未上榜 | 191 / 0.01T | 未收录 |
| Doubao Seed Code（字节） | 16.9（估）（67） | — | 未上榜 | 不在 OpenRouter | 未收录 |
| ERNIE 5.0 Thinking Preview（百度） | 14.3（估）（74） | — | 未上榜 | 不在 OpenRouter | 未收录 |
| Hy4 preview（腾讯） | AA 未收录 | — | 未上榜 | 4 / 9.64T | 未收录 |
| ERNIE 5.1（百度） | AA 未收录 | — | 45 / 1468 | 不在 OpenRouter | 未收录 |
| Seed 2.0 Pro（字节） | AA 未收录 | — | 64 / 1456 | 不在 OpenRouter | 未收录 |

- Muse Spark 1.3 的 OpenRouter 用量取的是 `muse-spark-1.3-contributor`（第 17）；普通版 `muse-spark-1.3` 第 37（0.56T）。
- Qwen3.8 Max 的 LMArena 条目只写 qwen3.8-max，没注明是 0803 还是 0902 版。

## 6. 意外发现（锐评素材，数字都在上面的表里）

1. **Anthropic 包揽 AA 前 5 个档位**，而且第 1 名 Opus 5.5（57.6）标价 $4 / $20，比排在它后面的 Fable 5.1 和 GPT-6 Astra（都是 $10 / $50）便宜一半多。LMArena 文本榜第 1 也是 Opus 5.5（不过只有 2,307 票）。
2. **开放权重第一 MiMo-V2.6-Pro 46.3 分 ≈ Grok 4.7 46.4 分**。跑完整个 AA 指数只花 $207，Opus 5.5 max 要 $8,708（约 42 倍），Fable 5.1 max 要 $13,129。代价是慢：输出 44 tok/s。
3. **开放权重前 10 全是中国模型**；美国最高的开放权重是 Thinking Machines 的 Inkling Small（估算 27.8；实测分最高的是 Inkling 25.0），gpt-oss-120b 只有 12 分。
4. **Google 没有新 Pro**：AA、LMArena、OpenRouter、Epoch、ARC 五处，最新的 Gemini Pro 都还是 2026-02 的 3.1 Pro Preview（AA 29.7 分，家族第 29）。Google 在 AA 上最强的是 Gemini 3.8 Flash（40.9），但它速度 285 tok/s，在 LMArena 排第 10，ARC-AGI-2 89.17%。
5. **Meta 回来了**：闭源的 Muse Spark 1.3 在 AA 家族排第 4（48.1），LMArena 第 9，3:1 价只要 $2。
6. **DeepSeek 的 Flash 比 Pro 强**：V4.1 Flash 39.5 > V4 Pro 0813 36.0；V4.1 Flash 还是 OpenRouter 周用量第 1（19.58T）。按厂商加总，DeepSeek 占 OpenRouter 周 token 的 22.8%【自算】。
7. **便宜的在被用，贵的在赚钱**：OpenRouter 周用量前 2 都是便宜 Flash（DeepSeek V4.1 Flash、GLM-5.3-Flash），Opus 5.5 只排第 25；Anthropic 占 token 3.6%，但 `total_usage`（像是花费）占 28.6%【自算，total_usage 含义未核实】。
8. **Qwen3.8 Max 很“能说”**：标价 $2 / $6，每任务却要 $5.41（接近 Opus 5.5 max 的 $5.98），跑完指数 $4,935，速度 39 tok/s，是前 20 里最慢的之一。
9. **Kimi K3 是最贵的开放权重模型**：$3 / $15，比闭源的 GPT-6 Sol（$2 / $10）还贵；但 LMArena 第 16、Epoch ECI 第 12，国产里在“人类偏好”和 ECI 上都最高。
10. **榜单之间打架**：GPT-6 Astra 在 AA 家族第 3、ECI 第 1、ARC-AGI-3 第 1，但 LMArena 只排 26；Grok 4.7 在 AA 家族第 6，LMArena 排 92。
11. **ARC-AGI-3 被 GPT-6 Astra 一家打穿**：标准外壳 62.71%，换 Provider Adapter 外壳 99.95%；其他模型最好是 Gemini 3.8 Flash（Adapter）35.00%、Claude Opus 5 30.16%。
12. **Sonnet 5 掉队**：Claude Sonnet 5 (max) 只有 38.2，低于 7 个国产开放权重模型，每任务还要 $5.09。
13. **腾讯 Hy4 preview 在 AA、LMArena 文本榜、Epoch ECI 上都没有分数，却是 OpenRouter 月用量第 2（56.35T）、周用量第 4**；匿名模型 stealth/space-bunny-alpha 周用量第 3。

## 7. 来源（全部 2026-09-28 访问）

| # | 内容 | 网址 |
|---|---|---|
| 1 | AA 排行榜（表格 + 内嵌数据：分数、价格、每任务成本、速度、开放权重） | https://artificialanalysis.ai/leaderboards/models |
| 2 | AA 模型页（内嵌全部模型的 3:1 / 7:2:1 混合价、跑完整个指数的总花费、许可证、参数量） | https://artificialanalysis.ai/models/claude-opus-5-5 |
| 3 | AA 模型页（交叉核对用） | https://artificialanalysis.ai/models/mimo-v2-6-pro |
| 4 | AA 智能指数评测页（v4.3.2，10 项评测） | https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index |
| 5 | AA 文章：v4.3 发布（2026-09-07，权重表） | https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3 |
| 6 | AA 方法论：智能指数版本历史、置信区间 | https://artificialanalysis.ai/methodology/intelligence-benchmarking |
| 7 | AA 方法论：价格定义（Blended = 7:2:1；价格取首方或中位数） | https://artificialanalysis.ai/methodology |
| 8 | unite.ai：Xiaomi’s New Flagship Model Leads Open-Weight Rankings With a Score of 46（2026-09-21 发布，09-23 更新） | https://www.unite.ai/xiaomis-new-flagship-model-leads-open-weight-rankings-with-a-score-of-46/ |
| 9 | LMArena / arena.ai 文本榜（快照 2026-09-25 22:00 UTC） | https://arena.ai/leaderboard/text （lmarena.ai/leaderboard/text 跳转） |
| 10 | OpenRouter 排行页（数据截至 2026-09-27） | https://openrouter.ai/rankings |
| 11 | OpenRouter 排行接口（周 / 月） | https://openrouter.ai/api/frontend/v1/rankings/models?view=week ；?view=month |
| 12 | OpenRouter 模型目录（上架日、标价） | https://openrouter.ai/api/v1/models |
| 13 | Epoch ECI 页面 | https://epoch.ai/eci （epoch.ai/benchmarks/eci 跳转） |
| 14 | Epoch ECI 分数数据 | https://epoch.ai/data/eci_scores.csv |
| 15 | Epoch 基准成绩数据（DeepSWE、FrontierMath 等） | https://epoch.ai/data/eci_benchmarks.csv |
| 16 | ARC Prize 排行页 | https://arcprize.org/leaderboard |
| 17 | ARC Prize 数据 | https://arcprize.org/media/data/evaluations.json ；https://arcprize.org/media/data/models.json |
| 18 | METR 任务时长页（最后更新 2026-05-08） | https://metr.org/time-horizons/ |
| 19 | METR 数据 | https://metr.org/assets/benchmark_results_1_1.yaml |
| 20 | Scale SWE-bench Pro 排行 | https://labs.scale.com/leaderboard/swe_bench_pro （scale.com/leaderboard/swe_bench_pro_public 跳转） |
| 21 | BenchLM（二手转述，数字过时，只作反例） | https://benchlm.ai/benchmarks/artificialanalysis |

## 8. 没核实 / 需要注意

- ARC-AGI-3 数据里 `cost` 字段的含义（总花费还是别的）【未核实】。
- OpenRouter 接口 `total_usage` 字段是否等于美元花费【未核实】；3.3 节第五列只作参考。
- BenchLM、OpenRouter 小组件上的 AA 分数和 AA 本站对不上，原因（旧版本还是匹配错）【未核实】；视频只用 AA 本站数字。
- LMArena 条目 qwen3.8-max 是哪个版本（0803 / 0902）【未核实】。
- AA 只收录了豆包的 Doubao Seed Code（估算）、文心的 ERNIE 5.0 Thinking Preview（估算）；豆包 Seed 2.x、文心 5.1、混元 Hy4 preview 没有 AA 分数。给这几家打分只能用 LMArena 或厂商自报（cn_models.md），要在画面上注明口径不同。
- 各榜更新节奏不同：AA 已收录到 2026-09-22 发布的模型；LMArena 票数截至 09-25；OpenRouter 截至 09-27；Epoch ECI 收录到 09-09 发布的模型；METR 停在 05-08。
