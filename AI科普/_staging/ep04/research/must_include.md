# EP03 必上榜三模型资料包：MiMo-V2.6 / Step 5 Preview / Jev

- 用途：《大肥鱼锐评：截至 2026 下半年，国内外大模型从夯到拉》第 03 期，用户指定必须出现的三个模型。
- 检索日期：2026-09-28（下文所有来源的访问日期都是 2026-09-28，来源编号见文末）。
- 标注：`[官方]` = 厂商官网 / 文档 / 模型卡；`[AA]` = Artificial Analysis 第三方实测；`[媒体]` = 新闻报道 / 评测博客；**未核实** = 只有单一二手来源、来源互相矛盾，或本次没能打开原文。
- 引用：除一句核对过原文的官方英文原话外，其余都是转述，不是逐字引文。台本要用原话，请先打开来源核对。
- 档位用参考视频的五档：夯 / 顶级 / 人上人 / NPC / 拉完了。
- AA 排名说明：AA 榜单把同一模型的不同推理档（max / xhigh / high…）分成多行。下文“第 N 名”指合并推理档、去掉已下架型号后的名次，按 2026-09-28 抓取的榜单数据计算 [A1]。

---

## 速览

| | Xiaomi MiMo-V2.6-Pro | StepFun Step 5 Preview | TypeSafe AI Jev（jev-1.13.0） |
|---|---|---|---|
| 一句话 | 小米的万亿参数开源全模态旗舰 | 阶跃的 600B MoE 旗舰预览版，主打 Agent、编程、金融 | 不说话只做选择题的“决策模型” |
| 发布 | 2026-09-22 凌晨（北京时间） | 2026-09-20 11:15（北京时间） | 2026-09-15，限量早期体验 |
| 规模 | 1.02T 总参 / 42B 激活，1M 上下文 | 600B 总参 / 27B 激活，1M 上下文 | 未公开（官方只说它既不小，也不是 LLM） |
| 开源 | MIT，权重已在 Hugging Face | 说是 10-15 开源，许可证未公布；AA 目前标为“专有” | 闭源，只有 API |
| 价格（每百万 token） | ¥3 入 / ¥6 出（$0.435 / $0.87） | ¥7 入 / ¥20 出（$1.00 / $2.70） | 输入 $0.042（= $42 / 十亿），**输出免费** |
| AA 智能指数 | 46.32（开源第 1、全榜第 7） | 43.73（全榜第 11；AA 按专有模型算） | 不适用（不做 AA 那类测试） |
| AA 单题成本 | $0.13 | $0.72 | — |
| 建议档位 | 夯 | 人上人 | 人上人（单独注明“不是聊天模型”） |

---

## 一、Xiaomi MiMo-V2.6 系列

### 1.1 身份
小米 MiMo 团队的第 3 代开源大模型系列，9 月 22 日发布并开源，旗舰 MiMo-V2.6-Pro 是目前 AA 智能指数上分数最高的开源权重模型。

### 1.2 时间线
- 2025-04-30 MiMo-7B；2025-12 MiMo-V2-Flash（309B / 15B 激活）；2026-04-22 MiMo-V2.5 系列 [M27]。
- 2026-06-08 MiMo-V2.5-Pro-UltraSpeed：万亿参数模型生成速度首次超过 1000 tokens/s（最高约 1200），价格是 V2.5-Pro 的 3 倍 [官方 M8]。
- 2026-08-13 澎湃 OS 4 发布，超级小爱 2.0 基于 MiMo-V2.5 系列 [M28][M29]。
- 2026-09-17 MiMo 负责人罗福莉宣布“直播训练”：公开强化学习（RL）全过程，实时显示成本、token、评测分数，连硬件故障也照播；直播页 mimo.xiaomi.com/rl/ [M11]。
- 2026-09-22 凌晨 V2.6 系列发布并开源（IT之家 07:05 发稿；美国时间 9-21，所以 AA 和 VentureBeat 记为 9-21）[官方 M1][M10][M12]。
- 2026-10-21 10:00（北京时间）mimo-v2.5-pro、mimo-v2.5 下线，旧模型名失效 [官方 M5]。

### 1.3 型号阵容
| 型号 | 官方定位（转述）[M1][M2] | 规格 |
|---|---|---|
| mimo-v2.6-pro | 旗舰推理模型：全模态、万亿参数、最强性能 | 稀疏 MoE，1.02T 总参 / 42B 激活 |
| mimo-v2.6-flash | 低成本、高效率的全模态推理模型 | 约 309B–310B 总参 / 15B 激活（各来源四舍五入不同）|
| mimo-v2.6-pro-ultraspeed | Pro 的高速档，官方称性能不变、速度最高 20 倍 | 和 Pro 同一模型的高速推理档（第三方目录描述）|
| MiMo-V2.6-Distill-Qwen-9B | 只开源不上 API，定位 RL 研究 [M3] | 基于 Qwen3.5-9B 的 9B 稠密模型 [M15] |

### 1.4 架构（Hugging Face 模型卡 MiMo-V2.6-Pro-RL [官方 M7]）
- LLM 主干：稀疏 MoE，1.02T 总参 / 42B 激活；70 层（60 层滑动窗口注意力 SWA + 10 层全局注意力 GA）；384 个路由专家，每 token 选 8 个，无共享专家；hidden 6144。
- 多 token 预测（MTP，用于投机解码）：5 层 SWA，每次前向预测后面 7 个 token。
- 视觉：681M 参数 MiMo ViT（28 层）。音频：308M AudioTokenizer + 127M 音频 patch 编码器。
- “natively omnimodal”（原生全模态）指的是：文本、图片、视频、音频都能直接输入同一个模型；输出是文本 [M7][M31]。
- 上下文约 1M token，最大输出 128K [M12][M30]。
- 许可证 MIT，可商用；有 FP8 权重 [M7]。权重在 Hugging Face（合集 huggingface.co/collections/XiaomiMiMo/mimo-v26），多家媒体称 ModelScope 也有 [M3][M15]。
- 自己部署：U365 称 Pro 权重约 573.5 GB [M26]（**未核实**）。

### 1.5 价格（官方按量计费页 [M4]；IT之家确认沿用 V2.5 定价 [M10]）
每百万 token：

| 型号 | 缓存命中 | 输入 | 输出 |
|---|---|---|---|
| mimo-v2.6-pro（= v2.5-pro 价） | ¥0.025 / $0.0036 | ¥3.00 / $0.435 | ¥6.00 / $0.87 |
| mimo-v2.6-flash（= v2.5 价） | ¥0.02 / $0.0028 | ¥1.00 / $0.14 | ¥2.00 / $0.28 |
| mimo-v2.6-pro-ultraspeed | ¥0.25 / $0.036 | ¥30.00 / $4.35 | ¥60.00 / $8.70 |
| 批量 Pro | ¥0.0125 / $0.0018 | ¥1.50 / $0.2175 | ¥3.00 / $0.435 |
| 批量 Flash | ¥0.01 / $0.0014 | ¥0.50 / $0.07 | ¥1.00 / $0.14 |

- 不按上下文长度分档；缓存写入限时免费；TTS 系列限时免费 [M4]。
- 官方称同等智能下价格是海外模型的 1/20 到 1/60 [M10]。
- UltraSpeed：价格正好是 Pro 的 10 倍。速度官方说“最高 20 倍”，OpenRouter 写“约 10 倍”。截至 9-28 没有找到可信的独立 tok/s 实测，orcarouter 也说还没人发布过能对上这两个说法的测量 [M21]（**速度倍数未核实**）。对比：上一代 V2.5-Pro-UltraSpeed 只贵 3 倍，实测超过 1000 tok/s [M8]。
- Token Plan 订阅 [官方 M6]：Lite ¥39/月（41 亿 Credits）、Standard ¥99、Pro ¥329、Max ¥659；首购 88 折；支持 v2.6-pro / flash 等 8 个模型，**不含 UltraSpeed**；Pro 的 Credits 消耗是 Flash 的 3 倍。
- 免费渠道：
  - 权重 MIT 免费下载（要数据中心级 GPU）。
  - MiMo Studio 网页对话，需登录，没找到公开的用量上限 [M19]。
  - OpenCode Zen 从 9-21 起大约一周免费提供 V2.6-Flash（OpenCode 说免费模型的数据可能被用来改进模型）[M19]。
  - MiMo Desktop（Windows / Mac）同步上线会员订阅，会员价格**未核实** [M10]。

### 1.6 Artificial Analysis 成绩（抓取于 2026-09-28）[AA M9][A1]
- 智能指数 v4.3.2：**46.32**，页面显示 46。
- **开源权重第 1**：GLM-5.3 44.78 第 2，Kimi K3 43.59 第 3。
- 全部模型里排第 7。排在它前面的依次是：Claude Opus 5.5 57.62、Claude Fable 5.1 53.35、GPT-6 Astra 52.67、Muse Spark 1.3 48.09、GPT-6 Sol 47.53、Grok 4.7 46.45。按 AA 原始逐行榜（推理档分开算）排第 18 行。
- 发布时的说法是“和 Grok 4.7 并列、闭源第一梯队 53 分”[M10][M12]。但 AA 记录的 Claude Opus 5.5、GPT-6 Sol、GPT-6 Luna 发布日期也都是 9-22 [A1]，所以“登顶”当天闭源头部又往上拉开了一截。
- 上一代 MiMo-V2.5-Pro 是 25.99 分，这一代涨了约 20 分 [A1][M10]。
- 单题成本 **$0.133**（Grok 4.7 xhigh 是 $3.74，约 28 倍；Step 5 Preview 是 $0.72；Claude Opus 5.5 max 是 $5.98）[A1]。跑完整套指数 MiMo 花 $206.66，Grok 4.7 花 $4,967.35，约 24 倍 [M20]（二手转述 AA）。
- 话痨程度：跑指数输出了 1.4 亿 token，AA 评价比同类平均略多 [M9]。
- 速度：AA 页面写官方 API 输出 **42.5 tok/s**，在同尺寸开源模型里偏低（中位数 84.4）；首 token 4.05 s；榜单数据里“首个答案 token”中位数 **48.8 s**（因为先要思考）[M9][A1]。发布时第三方测的是约 125–134 tok/s [M12][M15][M20]，一周后只剩三分之一左右（原因**未核实**，可能是上线后负载上升）。
- AA 自测分项：HLE 49.4%、Terminal-Bench 4.0 34.8%、SciCode 60.9%、AA-LCR（长上下文）86.3%、AA-Omniscience 知识准确率 34.85% [A1]。
- MiMo-V2.6-Flash：指数 37.88，单题 $0.062，62.4 tok/s [A1]。

### 1.7 厂商自测基准（HF 模型卡原表 [官方 M7]）
| 基准 | V2.6 Pro | V2.6 Flash | V2.5 Pro | Claude Opus 5 | GPT-5.6 Sol | Claude Fable 5 |
|---|---|---|---|---|---|---|
| DeepSWE v1.1 | 71.9 | 67.9 | 19.0 | 74.0 | 73.0 | 70.0 |
| ProgramBench | 26.5 | 26.0 | 12.5 | 37.0 | 25.0 | 33.0 |
| AutomationBench v1.0.6 | **53.1** | 52.3 | 16.0 | 50.3 | 45.8 | 46.2 |
| Toolathlon-Verified | 76.9 | 73.6 | 49.1 | 80.6 | 74.9 | 77.9 |
| GDPval-AA 2.1 | 1673 | — | 1107 | 1708 | 1588 | 1595 |
| Agents' Last Exam | 31.6 | 27.6 | 13.2 | 31.6 | 30.8 | 25.7 |
| Terminal Bench 4.0 | 34.9 | 28.8 | 1.5 | 49.0 | 39.9 | 42.4 |
| Terminal Bench 2.1 | **89.9** | 87.6 | 65.2 | 89.1 | 88.8 | 84.3 |
| OSWorld-Verified | 82.0 | 80.8 | — | 83.4 | 83.0 | 86.0 |
| JobBench | 62.0 | 61.2 | 25.0 | 65.7 | 45.4 | 57.4 |
| CyberGym | 94.0 | **95.1** | 40.0 | — | — | — |
| MiMo Cyber Bench（自家） | 80.2 | 77.2 | **0.0** | — | — | — |
| ExploitBench | 47.9 | 25.3 | 16.6 | 70.0 | 78.5 | 78.0 |
| SEC Bench Pro | 66.3 | 47.5 | 17.7 | — | 79.1 | — |
| MiMo VisualCoding（自家） | 72.3 | 71.5 | — | 70.0 | 73.4 | 69.1 |

- 要点：在旧的 Terminal Bench 2.1、AutomationBench 上略超 Opus 5；换到更难的 Terminal Bench 4.0 落后 14 分，漏洞利用（ExploitBench）落后 30 分；CyberGym 上 Flash 比 Pro 还高。
- 模型卡**没有给 V2.6-Pro 的 SWE-bench Verified / Pro 分数**，用的是 DeepSWE v1.1。IT之家写的“SWE-bench Verified 61.1→66.2、Terminal Bench 2.1 37.1→52.8”是 9B 蒸馏模型做 RL 前后的对比，不是 Pro 的分数 [M10]。
- 训练看板口径（avg@3）：DeepSWE v1.1 上 Pro 58.4→72.6，Flash 48.8→65.7 [M10][M23]。这和模型卡的 71.9 / 67.9 口径不同，别混用。
- VentureBeat 提醒：Agent 类评测都是厂商自己跑的 [M12]。

### 1.8 “直播训练”与 RL 投入
- Pro 和 Flash 各跑 30 步 RL，累计约 75 万条轨迹，不到 6 天。成本 Pro 约 $262 万、Flash 约 $85 万，合计约 **$347 万** [官方 M3][M10][M23]。
- 用时：Pro 5 天 7 小时，Flash 3 天 11 小时 [M22]（二手整理）。
- 每步 1,568 个 prompt × 16 条 rollout，完全异步；单步训练 token 3.5–3.7B；支持 1M 上下文训练 [M10][M11]。
- Pro 成本构成：训练 43.5%、生成轨迹（rollout）43.8%、打分 12.7% [M12]。
- 9-17 直播中途累计已超过 $125 万（IT之家）或 $135 万（新浪），约每小时 $3.1 万 [M11][M23]。
- 直播里公开的故障（二手整理，**未逐条核实**）：Pro 第 17 步 GPU 显存溢出（OOM）重启；中途移除了网络安全（cyber）数据集，原因说法不一；Flash 第 15 步因基础设施误报重启；某节点显存故障 [M22][M17]。
- 最终确认的奖励作弊（reward hacking）轨迹低于 2% [M12]。
- 同时开源：7000+ RL 任务环境、基于 verl / uni-agent / mini-swe-agent 的端到端训练框架、轻量 harness [M3][M10]。
- 高盛按 avg@3 口径估算，训练用了约 4000 / 8000 张 H200 等效卡 [M23]（二手转述，**未核实**）。

### 1.9 和小米手机 / 汽车 / 澎湃 OS 的关系
- 维基百科称 MiMo 是小米“人车家全生态”的核心 AI 模型；雷军 2026 年 3 月宣布未来三年在 AI 上投入至少 87 亿美元 [M27]。
- 澎湃 OS 4（2026-08-13）的超级小爱 2.0 基于 MiMo-V2.5 系列，能跨应用、跨设备执行任务，例如出门前说一句话就把车准备好；首批机型是 Xiaomi 17 系列、Pad 8、REDMI K90 [M28][M29]。
- **V2.6 有没有进手机、汽车：未核实**（发布材料只提 API、MiMo Studio、Desktop、OpenRouter）。

### 1.10 负责人
- 罗福莉，小米 MiMo 大模型负责人，前 DeepSeek 研究员，2025 年底加入小米 [M11][M27][M12]。
- 9-17 她说团队沉寂了近半年，只研究一件事：强化学习到底能扩展到多远 [M11]。发布后她说这 6 天背后是半年的基础研究和工程试错 [M23]。
- 对 VentureBeat：算力极度紧缺的时候，仍然让几十人的团队长期只做一件事——扩展 RL [M12]。

### 1.11 批评与短板
1. 最难的长程编程和安全任务差距明显：Terminal Bench 4.0 34.9 对 Opus 5 的 49.0；ExploitBench 47.9 对 GPT-5.6 Sol 的 78.5 [M7][M17]。
2. 官方 API 慢、先想很久才答：42.5 tok/s，首个答案 token 约 49 s [M9][A1]。
3. 知识面一般：AA-Omniscience 准确率 34.85% [A1][M26]。
4. 社区怀疑刷榜（benchmaxxing）：CellCog、eesel 都提到“国产模型一干真活就露馅”的质疑；eesel 认为 CyberGym 94.0 分亮眼但还没定论 [M15][M17]。
5. 多轮对话退化：某聚合榜首轮排第 74/117，第 2–10 轮掉到第 112/116（U365 转述，原榜**未核实**）[M26]。
6. 实测：kingy.ai 用 3 个日常编程任务测，Pro 和 Opus 5 都拿满 23/23，成本约 $0.03 对 $1.03；但每题只跑一次，说明不了长时间无人值守的稳定性 [M18]。

### 1.12 吐槽素材（都有出处）
- “开源第一”只守了半天：AA 记录 Claude Opus 5.5（57.6）、GPT-6 Sol 都是 9-22 发布，和 MiMo 同一天 [A1]。
- 直播炼丹：6 天烧掉约 $347 万，显存爆了、重启了都在直播里 [M3][M22][M23]。
- 跑分快、干活慢：发布时第三方测 125–134 tok/s，9-28 AA 测官方 API 只有 42.5 tok/s，首个答案要等约 49 秒 [M9][M12][M20]。
- 超高速档：“最高 20 倍速度”，价格也正好 10 倍；上一代超高速档才贵 3 倍 [M4][M8]。
- 自家网络安全榜 MiMo Cyber Bench：上一代 V2.5-Pro 得 0.0 分，这一代 80.2 [M7]。

### 1.13 建议档位：**夯**
理由：开源第一、MIT 随便商用，单题成本只有 Grok 4.7（xhigh）的约 1/28，“便宜又能打”这一项目前没有开源对手。如果节目把“夯”只留给闭源头部，就给**顶级**。

---

## 二、阶跃星辰（StepFun）Step 5 Preview

### 2.1 身份
阶跃星辰新一代旗舰基座模型的预览版，面向真实世界 Agent 任务，重点是 AI 编程、软件工程、专业知识工作和金融。官方发布页标题是《Step 5 Preview：向前一步，智能效率的新一代“帕累托前沿”》[官方 S1]。

### 2.2 规格（逐项核对官方）
| 项目 | 内容 | 核对 |
|---|---|---|
| 架构 | 稀疏 MoE，600B 总参，每 token 激活 27B | ✅ 官方页 [S1] |
| 上下文 | 1M token；最大输出 64K | ✅ [S1][S2] |
| 输入 / 输出 | 文本、图片（每次最多 60 张）、视频（MP4 / QuickTime / Matroska，MP4 < 128 MB，建议 < 5 分钟）进；只输出文本 | ✅ 文档 [S2] |
| 功能 | 工具调用、流式、JSON Mode / JSON Schema、提示缓存、推理强度 low / medium / high | ✅ [S2] |
| 92 层“窄而深” | 媒体转述（MarkTechPost、新智元），官方页正文没看到 | ⚠️ 媒体 [S8][S10] |
| MTP-3、FP8 MoE、KV 缓存卸载；BF16 权重约 1.2 TB | 只见 MarkTechPost | **未核实** [S8] |
| API 模型名 | step-5-preview | ✅ [S2] |

- 发布时间：北京时间 2026-09-20 11:15（UTC 03:15），X 和官网同时发 [S6]。AA 记录的发布日期是 9-18：正式公告前两天，就有一个测试标签为 step-5-preview-b 的评测结果出现在 AA 上 [S5][S9]。
- 开源：官方页写明 10 月 15 日正式开源 ✅ [S1]。
  - **许可证至今没公布**（官方页和文档都没写）[S1][S6]；之前的 Step 3.5 / 3.7 Flash 用的是 Apache 2.0 [S7][S16]。
  - Hugging Face 仓库 stepfun-ai/Step-5-Preview-BF16 在 9-28 访问返回 401，没有公开 [S13]。GitHub 没查（**未核实**）。

### 2.3 价格（官方价格页 [S3][S4]）
| 每百万 token | 输入（未命中缓存） | 输入（命中缓存） | 输出（含思考 token） |
|---|---|---|---|
| step-5-preview | **¥7** / **$1.00** | ¥0.35 / $0.05 | **¥20** / **$2.70** |
| step-3.7-flash | ¥1.35 / $0.20 | ¥0.27 / $0.04 | ¥8.1 / $1.15 |
| step-3.5-flash | ¥0.7 / $0.10 | ¥0.14 / $0.02 | ¥2.1 / $0.30 |

- 没有阶梯折扣；限流等级按累计充值划分 [S4]。
- 和 MiMo-V2.6-Pro（¥3 / ¥6）比：输入贵 2.3 倍，输出贵 3.3 倍。
- 免费：自媒体“赛博禅心”的文章说，模型已接入线下的 AGI Bar，连店内 Wi-Fi 可以免费用一周（从 9-20 起）[S11]（店主是谁**未核实**）。

### 2.4 基准：厂商自报（官方页全表 [S1]）
注意：Step 5 用的是 **High** 推理档，对手用的都是 **Max** 档。

| 基准 | Step 5 Preview (High) | GLM-5.3 | Kimi K3 | GPT-6 Astra | Claude Fable 5.1 | Claude Opus 5 |
|---|---|---|---|---|---|---|
| GPQA Diamond | 93.5 | 91.7 | 93.5 | 96.1 | 93.7 | 93.2 |
| HLE | 46.5 | 42.3 | 46.9 | 54.7 | 59.1 | 54.9 |
| AA-LCR v1.1 | 88.3 | 79.7 | 88.7 | 80.7 | 85.3 | 79.3 |
| DeepSWE v1.1 | 67.7 | 66.9 | 67.5 | 74.1 | 67.4 | 74.0 |
| Terminal-Bench v2.1 | 85.0 | 83.9 | 85.0 | 88.4 | 91.4 | 89.1 |
| Terminal-Bench v4 | 33.3 | **41.9** | 12.6 | 57.9 | 55.8 | 52.3 |
| SWE-Marathon v1.1 | 72.7 | 67.4 | **84.4** | 77.3 | 80.2 | 85.6 |
| StepCodeBench† | 49.0 | 40.2 | 43.9 | 61.0 | — | 63.9 |
| GDPval-AA v2.1 | 1566 | 1645 | 1524 | 1542 | 1735 | 1708 |
| AutomationBench-AA | **51.0（六家最低）** | 62.2 | 58.3 | 68.5 | 59.4 | 56.6 |
| BrowseComp | 88.7 | — | 91.2 | 91.5 | — | 90.2 |
| HLE w/ tools‡ | 59.4 | 62.5 | 56.0 | 57.2 | 65.0 | 63.6 |
| FrontierFinance | 66.4 | 64.1 | 62.6 | 55.0 | — | 69.7 |
| MMMU-Pro | 76.0 | 仅文本 | 81.0 | 87.0 | — | 85.0 |
| GDP.pdf | **14.8** | 11.2 | 22.0 | 31.0 | 26.2 | 21.6 |

- † 标记的 6 项是阶跃自研基准：StepCodeBench、StepCode-Bench-Daily、StepCode-Bench-General、FinStepBench 三项。
- ‡ HLE 带工具这一项：Step 5 和 GLM-5.3 只测纯文本子集，其他模型测全集，官方自己也注明这两种结果不能直接比。
- 官方案例：
  - 24 小时在 H100 上优化 MLA GPU Kernel，约 22 小时后达到 508 TFLOPS，对比里最高。
  - 自动后训练 Qwen3-30B-A3B，AIME24 从 53.3% 提到 60%，和 Opus 5 持平。
  - 约 70% 的评测者认为它能自主完成中高复杂度编程任务。
  - 在一次 Agent 动作里完成 950 次 Web Fetch。
- 官方自己承认：在最难、运行时间最长的编程任务上还有提升空间 [S1]。
- 官方彩蛋：玩《宝可梦 红》，已超过 3,000 步、约 600 万 token，第 3,082 步打赢枯叶道馆拿到第三枚徽章，主线进度约三分之一 [S1]。

### 2.5 基准：第三方（AA，抓取于 2026-09-28）[AA S5][A1]
- 智能指数 **43.73**，页面显示 44，和厂商说的 44 一致；在同价位推理模型里远高于平均（中位数 26）。
- 排名：全部模型里第 11。AA 目前把它标为专有模型、权重未公开，所以**不进开源榜**。如果 10-15 真开源，按分数会是开源第 3（43.73 略高于 Kimi K3 的 43.59，两者都显示 44），这就是国内媒体“跻身全球开源前三”的来源 [S10]。
- 单题成本 **$0.72**。对 Claude Opus 5 max（$5.86）确实约是 1/8，官方“单任务成本为 Opus 5 的 1/8”成立。但它是 MiMo-V2.6-Pro（$0.13）的 **5.4 倍** [A1]。
- 话痨：跑指数输出了 **1.6 亿 token**，同价位中位数是 8800 万 [S5]；整套跑下来花了约 $918–925（不同时间的两次跑法，二手）[S9]。
- 速度：66.4 tok/s（页面）或 72.3（榜单中位数）；首 token 3.05 s；首个答案 token 约 30.7 s [S5][A1]。9-18 那次泄露的评测是 99.8 tok/s [S9]，现在也慢下来了。
- AA 自测分项和厂商数字基本一致：HLE 46.4%，Terminal-Bench 4.0 33.3% [A1]。

### 2.6 评测者指出的短板（“the Gaps”）
- CellCog（9-20）[S6]：
  - 发布时没有权重、没写许可证、没有技术报告、HF 仓库是空的、OpenRouter 上也没有。
  - 自己用 High 档对别人的 Max 档；6 项是自研基准；HLE 带工具这一项不可比。
  - 多模态文档很弱：GDP.pdf 14.8% 对 Astra 的 31.0%。
  - 最长的编程任务上和前沿有差距；发布时没有任何独立评测（后来 AA 补上了）。
- eesel（9-21）[S7]：所有数字都是自报，StepCodeBench 是自家的；社区有人吐槽它两头不讨好、回答里垫了大量废话；eesel 的结论是：想要成熟稳定、经过验证的模型，就先观望。
- orcarouter（泄露评测）[S9]：早期测试者最常抱怨工具调用选错；有人说上下文到 34 万 token 左右会出问题；有内容过滤截断（**未核实**）。

### 2.7 前作
- **Step 3.5 Flash**：2026-02-02 发布（AA 记录；官方博客标注 2026-02-12 更新）[S15][A1]。
  - 196B 总参 / 11B 激活，256K 上下文，Apache 2.0 [S17]。
  - 官方称常用 100–300 tok/s，峰值 350；SWE-bench Verified 74.4% [S15]。
  - AA 指数约 16.6 [A1]。
- **Step 3.7 Flash**：2026-05-29 发布 [S16]。
  - 198B（196B 语言模型 + 1.8B 视觉编码器）/ 约 11B 激活，256K 上下文，Apache 2.0，最高 400 tok/s，Flash 系列第一个多模态版 [S16]。
  - SWE-Bench Pro 56.26%；AA 指数约 19.5 [S16][A1]。
- 所以 Step 5 在 AA 上一口气从 19.5 涨到 43.7，是阶跃第一次挤进第一梯队。

### 2.8 公司处境（2026）
- 基本情况：2023-04-06 在上海成立；CEO 姜大昕（前微软副总裁）[S17][S19]。
- 人事：2026-01-26 旷视联合创始人印奇出任董事长，负责战略节奏和技术方向。核心团队“1+3”：印奇、姜大昕、首席科学家张祥雨、CTO 朱亦博 [S18]。
- 融资：
  - 2026 年 1 月：B+ 轮超过 50 亿元，投资方有腾讯、上海国投先导基金、国寿股权、浦东创投、徐汇资本、厦门国贸、启明创投、五源资本 [S19]。
  - 2026 年 5 月：近 25 亿美元（约 170 亿元）。投资方有华勤、龙旗、豪威、中兴，以及香港投资管理有限公司（港投公司，它在大模型领域只押了阶跃一家）[S19][S20]。
  - 4 个月合计超过 200 亿元 [S19]。
- 上市：
  - 2026 年 4 月完成股改、拆除红筹架构，改名“上海阶跃星辰智能科技股份有限公司”[S19]。
  - 6 月传闻已**秘密递表**港交所，投资方提出的估值最高 120 亿美元，目标年内上市 [S19][S22]。**官方没确认**。
  - 截至 9-28 没有检到公开招股书或聆讯消息（本次搜索额度用完，**未核实**）。
- 收入：2025 年约 5 亿元，2026 年目标 10–12 亿元；员工 400 多人，研发占 80% 以上；副总裁承认暂时还没盈利 [S20]。
- 终端业务：
  - 模型装机量超过 4200 万台；和 OPPO、荣耀等合作，覆盖国内约六成头部手机品牌 [S18]。
  - 和吉利、千里科技做 AgentOS 智能座舱，搭载在吉利银河 M9 [S18]。CES 2026 上银河 M9 展示了基于 Step-Audio 2 的车载语音，首字响应 0.7 s（只见搜索摘要，**未打开原文**）[S23]。
- “AI 六小虎”格局 [S20][S21]：
  - 智谱、MiniMax 2026 年 1 月已在港股上市。
  - 零一万物、百川已经退出基础大模型训练。
  - 月之暗面也在准备 IPO，估值约 180–200 亿美元。
  - 阶跃是剩下还在训练基座模型、正在冲上市的一家。

### 2.9 吐槽素材
- 标题叫“帕累托前沿”（同等智能最便宜）。两天后小米 MiMo-V2.6-Pro 发布：AA 分更高（46.3 对 43.7），单题成本只有它的约 1/5（$0.13 对 $0.72），token 单价也只有它的约 1/2.3 到 1/3.3。这条“前沿”只守了约 48 小时 [S1][A1][M4]。
- 媒体说“跻身全球开源前三”，但权重要 10-15 才放，许可证还没写，HF 仓库访问返回 401，AA 现在把它标成专有模型 [S5][S10][S13]。
- 话痨：跑一套题输出 1.6 亿 token，同价位中位数是 8800 万 [S5]。
- 自己出题自己考：6 项自研基准；自己开 High 档，对手开 Max 档 [S1]。
- 宝可梦：官方彩蛋里 3,082 步才拿到第三枚徽章。另一边连话都不会说的 Jev，在 Claude 帮助下 9-23 已经通关（见第三节）[S1][J12]。

### 2.10 建议档位：**人上人**
理由：分数进了全球前 11、单价也不贵，是阶跃第一次摸到第一梯队。但“帕累托前沿”两天就被小米在分数和价格上双杀，权重和许可证还没兑现，而且话多。

---

## 三、TypeSafe AI 的 Jev

### 3.1 两句话讲明白“System One / 决策模型”（给普通观众）
> 平常的大模型是“写作文”的，你问一句它回一段；Jev 这种“决策模型”是“做选择题”的：程序先把题目和选项写好，它只回“是 / 否、选哪个、打几分”，外加一个“有几成把握”的概率。所以它不会聊天、不会写代码，但几十到几百毫秒就答完、输出不收钱，专门给软件当“自动判断开关”。

- 名字来历：“System One”取自卡尼曼《思考，快与慢》里的“系统 1（快思考）”。“Jev”取自经济学家 William Stanley Jevons（杰文斯悖论：越便宜，用得越多）[J1][J6]。
- Simon Willison 和 Maggie Appleton 觉得叫“decision models（决策模型）”更贴切 [J10]。

### 3.2 公司与创始人
- TypeSafe AI 总部在旧金山，2024 年成立，隐身开发两年，2026-09-15 发布 Jev [J1][J13][J14]。
- CEO **Diogo Almeida**：
  - 在 OpenAI 约 4 年，做过 RLHF、InstructGPT、ChatGPT、GPT-4，2024 年离开 [J13][J14]。
  - 团队页称他是 RLHF 和 InstructGPT 的共同发明人，之前在 Google Brain [J3]。
  - 他自己在博客里的说法更低调：在 OpenAI 帮忙做出了让语言模型会听指令、会和人聊天的方法，这些工作后来成了 ChatGPT 背后的研究 [J1]。
- TechCrunch 的标题是《A new kind of AI model from a ChatGPT inventor is thrilling developers》，正文说他参与打造了 ChatGPT，并参与发明了 RLHF [J9]。核对：
  - 他是 InstructGPT 论文（arXiv 2203.02155，2022-03-04）20 位作者里的**第 4 位** [J21]。
  - RLHF 最早见于 2017 年 Christiano、Leike、Amodei 等人的论文 [J22]。
  - 所以“ChatGPT 发明人”是媒体包装，准确说法是“ChatGPT 核心训练方法 InstructGPT 的主要作者之一”。
- 联合创始人 [J3]：
  - CTO Erik Gafni：连续创业者（Ravel），Invitae、Freenome 早期员工。
  - COO Sasha Sheng：前 Meta / FAIR 研究工程师。
- 融资：**4000 万美元种子轮，DCVC 领投** [J14][J13]；估值 2 亿美元（Forbes 报道，经 SiliconANGLE、维基转述；Forbes 原文 403 打不开）[J18]。其他投资方没有披露 [J16]。

### 3.3 输入和输出
- 输入：一个“state”（字符串、JSON 对象或文本数组）加上一组有类型的问题 [J4][J5]。
  - 只收文本，不收图片、音频、视频。
  - 每次请求最多 64K token，其中 state 加最长问题 32K。
  - 英语最准；中日韩等语言支持但不太稳 [J5]。
- 三种题型 [J4][J10]：
  1. **Noul**（是非题）：给一个陈述，回 0–1 的概率。Noul 是 Bernoulli 的缩写，CEO 在 Hacker News 上确认过。
  2. **Choice**（选择题）：从给定选项里挑一个，回选中项、每个选项的概率、置信度；最多 255 个选项 [J1]。
  3. **Score**（打分题）：按给定档位打分，回分数、各档概率、置信度。
- 所有问题并行、各自独立计算，一次返回，不是一个字一个字往外吐 [J1][J4]。
- 文档里的例子：state 是一封客户邮件，问题“is_urgent（是否紧急）”，返回 `"noul": 1.0` [J8]。
- 做不了的事：聊天、写代码、解释理由 [J6][J16]。

### 3.4 价格
- 输入 **$0.042 / 百万 token = $42 / 十亿 token**；输出**免费**，官方说便宜到不值得计费 [J1][J2][J5]。
- 官网说输入价比 Claude Fable 5.1 低 238 倍（Fable 5.1 输入 $10/M，算下来一致）[J2]。Simon Willison 说它比 GPT-5 Nano（$0.05/M）还便宜 [J10]。
- 官方也承认证明不了这个价格没有补贴，只说预计以后只降不涨 [J1]。
- 限流：每秒 25 万 token、每分钟 1200 次请求，文档说因为需求高正在动态调整 [J5]。TechCrunch 报道发布后需求太大，API 一度没法服务 [J9]。

### 3.5 速度 / 成本宣称，以及是和谁比的
- 端到端 70–500 ms。官方说在“System One 形状的问题”上比前沿 LLM 快 40–200 倍 [J1]。
- 头条数字 **“193.6x faster, 444.6x cheaper”**（官网注明基于 System One 任务的工作流）来自 TypeSafe 自己的“workflow evals”[J1][J2]：
  - 4 个工作流，由自家模型能力团队编写；官方承认可能有偏差。
  - 标准答案不是人工标注，而是 **GPT-6 Astra 和 Claude Fable 5.1 两个模型答案的平均**。
  - 对照的 LLM 套了 TypeSafe 自己的“System One LLM wrapper”，要输出带概率的结构化决策，本身就更慢更贵。
  - 服务目前放在美国西海岸，评测是从西海岸的笔记本上跑的。
  - 官方自己说，这组数字大概是现实收益的上限。
- Doom 演示：Jev 用 0.114 s、$0.000081；GPT-5.6 Terra 用 8.566 s、$0.013880（这一例约快 75 倍、便宜 171 倍）。每秒 10 次查询约合每小时 $7 [J1][J2][J15]。
- 客户案例（TechCrunch [J9]）：
  - Vercel 把 OpenAI 的 Luna 换成 Jev 做对比，快 5–18 倍，准确率也更高。
  - Bryo AI 做邮件分类，Gemini 略准一点，但贵 10–20 倍。

### 3.6 基准
- **官方故意不发公开基准**。博客 FAQ 原话：“We deliberately chose not to publish performance against public benchmarks.” 还劝大家别看重公开基准，自己做评测 [J1]。
- 第三方只找到 **JevBench**（Benchmark Heaven，v1.4.2.2，2026-09-27 评分；534 道公开题 + 308 道封存题；从德国服务器逐个请求）[J20]：
  - Jev 1.13.0：综合能力 64.7（智能 53.1、校准 76.3），每千次决策 $0.040，延迟中位数 0.65 s，**排第 2**。
  - 第 1 名是社区复刻的 **Imajev-4B**：66.3 分，成本只有 Jev 的 0.55 倍。
  - 参照的大模型（超出“Jev 级”的成本或延迟限制，不参与排名）：
    - GPT-6 Luna (medium)：智能 **97.4**，每千次 $0.14（Jev 的 **3.4 倍**），延迟 1.48 s。
    - DeepSeek V4.1 Flash：智能 94.0，成本是 Jev 的 14.9 倍。
    - Gemini 3.1 Flash-Lite：智能 54.5，成本是 Jev 的 6.6 倍。
  - 这是一个人的公司做的业余项目，还在 Beta，方法没经过同行评审，只能参考。它测出的 LLM 比 Jev 只贵 3–15 倍，远没有官方说的 445 倍。
- 社区在用开源模型复刻 Jev：Kev（基于 Qwen 3.5 做了 0.8B / 4B / 9B）等 [J10]。

### 3.7 能不能用上
- 9-15 起是 **early access**，走候补名单，官方说会尽快把开发者从候补名单放进来 [J1][J16]。
- 通过 console.typesafe.ai 用；有 Python SDK（`pip install typesafe-sdk`）和 JS SDK [J8]。
- 地区：服务在美国西海岸 [J1]；有没有国家 / 地区限制**未核实**。中国大陆能不能用**未核实**。
- HN 上 CEO 给质疑者提供了加速通过候补名单的通道 [J19]。

### 3.8 官方承认的局限（jev-1.13 “jaggedness”文档 [J7]）
- 死抠字面：回答的是你写出来的问题，不是你心里想问的。
- 数不清数，判断不了两个数是否接近。
- 日期当文本读，比较先后不可靠。
- 双重否定、绕弯的指令更容易答错。
- state 里无关内容越多越不准。
- 对抗性内容能把答案带偏。
- 指令和评判标准自相矛盾时会糊涂。
- 不是为生成文字训练的，硬让它生成文字效果差、速度也很慢。
- 另外：只收文本；Tom's Hardware 嫌 64K 上下文太小 [J11]。

### 3.9 开发者和评论者的看法
- **Simon Willison（9-21）[J10]**：
  - 适合各种分类任务：垃圾邮件、贴标签、优先级、排序；他自己在用它给搜索结果重排序。
  - 担心“黑箱又回来了”：只返回一个浮点数，看不出是哪些内容让它判成垃圾邮件。他特别希望没人拿它给求职者排名，怕里面藏着偏见。
  - 小实验：让 Jev 判断湾区每个城市是不是“Good city?”，Cupertino 排第一，East Palo Alto 垫底。
  - 结论：评测比平常更重要，好在它便宜，跑几千条实验只要几美分。
  - 9-22 他还发布了 llm-typesafe 插件。
- **社区整活 [J10]**：
  - jevchat：用 Jev 一个字一个字选出下一个符号，拼成一个“很烂的聊天机器人”。
  - jev-leftpad：用 Jev 算左侧补几个空格。
  - jev-2048：用 Jev 玩 2048。
- **Hacker News**（发布帖 1,984 分、520 条评论，9-28 查看）[J19]：
  - 主要质疑：“不会幻觉”偷换了“类型安全”和“答对”；没有公开基准；架构保密，CEO 说暂时不公开；“noul”这种命名被批对用户很不友好。
  - CEO 自己承认：它也可能很自信地答错。
- **TechCrunch（9-18）[J9]**：说它让开发者兴奋，但也指出它把幻觉问题部分甩给了用户——要用户自己根据置信度决定信不信。
- **The Register（9-16）[J15]**：主要报道 Doom 演示，质疑“零幻觉”这个说法是否公平，因为它的输出本来就不是自然语言。
- **TS2（9-17）[J16]**：标题直说 445 倍成本宣称仍是自测；并指出输出格式能保证合法，但保证不了选的答案是对的。
- **Tom's Hardware（9-21，Bruno Ferreira）[J11]**：转述“最高快 194 倍、便宜 445 倍”，说好不好用要实践说了算；决策由开发者自己负责，Jev 仍会误判，也会被对抗攻击。
- **Tom's Hardware（9-27，Shane Downing）[J12]**：Jev 通关《宝可梦 红》，9-23 进名人堂，但全程靠 Claude Opus 5 当教练：
  - 开发者是 Andrew Boyd（Standard Agents）。Opus 5 看游戏日志、改选项和措辞，改动记录有 474 条。
  - 翻车记录：往四天王科拿（Lorelei）关着的门口撞了 53 次；10 分钟内在岩山隧道的一个梯子上来回 124 次；打完四天王输给冠军的胡地，只好重打四天王。
  - 另一位开发者（Frigade 的 Christian Mathiesen）说，让 Jev 直接按手柄按键的第一版连真新镇都没走出去；他估算每 24 小时成本约 $1–1.70。

### 3.10 吐槽素材
- “零幻觉”是因为它根本不说话：只能从你给的选项里挑。CEO 在 HN 上自己承认也可能很自信地答错 [J1][J19]。
- “快 193.6 倍、便宜 444.6 倍”：题是自家团队出的，标准答案是 GPT-6 Astra 和 Fable 5.1 的平均答案，官方还特意不发任何公开基准。第三方 JevBench 上，GPT-6 Luna 的“智能”分几乎是它的两倍（97.4 对 53.1），却只贵 3.4 倍；综合分还被一个 4B 的社区复刻版超过 [J1][J20]。
- 通关宝可梦靠外援：Claude Opus 5 当教练、改了 474 次规则；它在四天王门口撞墙 53 次，10 分钟爬同一个梯子 124 次 [J12]。
- “ChatGPT 发明人”：实际是 InstructGPT 论文 20 位作者里的第 4 位 [J9][J21]。
- 输出免费到有人硬拿它拼了个聊天机器人（jevchat），HN 网友拿《瑞克和莫蒂》里莫蒂和“死亡水晶”的对话来比喻 [J10]。

### 3.11 建议档位：**人上人**（标注“不是聊天模型，赛道不同”）
理由：思路是真新，开发者也真买账（Simon 做了插件，Vercel 做了对比测试）。但数据全是自测、只开放候补名单、普通人既用不上也聊不了。如果节目只看“普通用户能不能直接用”，就放 **NPC**。

---

## 四、放在一起比

| 维度 | MiMo-V2.6-Pro | Step 5 Preview | Jev |
|---|---|---|---|
| 输入价 / 百万 token | ¥3 / $0.435 | ¥7 / $1.00 | $0.042 |
| 输出价 / 百万 token | ¥6 / $0.87 | ¥20 / $2.70 | 免费 |
| AA 智能指数 | 46.32 | 43.73 | — |
| AA 单题成本 | $0.13 | $0.72 | — |
| AA 输出速度（9-28） | 42.5 tok/s | 66.4 tok/s | 70–500 ms 一次决策（官方） |
| 上下文 | 1M | 1M | 64K |
| 开源 | MIT，已开放 | 预告 10-15，许可证未知 | 否 |
| 能聊天 / 写代码 | 能 | 能 | 不能 |

时间巧合：Jev 9-15 → Step 5 9-20 → MiMo-V2.6 9-22（同一天 AA 还收录了 Claude Opus 5.5、GPT-6 Sol、GPT-6 Luna）。

---

## 五、存疑 / 未核实清单
1. MiMo-V2.6-Pro-UltraSpeed 的真实速度倍数：官方说“最高 20 倍”，第三方目录写“约 10 倍”，没有独立实测。
2. MiMo-V2.6 有没有进小米手机、汽车（澎湃 OS 4 用的是 V2.5 系列）。
3. MiMo Desktop 会员价格；MiMo Studio 免费额度。
4. MiMo 直播里的具体故障细节、移除 cyber 数据集的原因（只见二手整理）；高盛算力估计。
5. MiMo “多轮对话从第 74 名掉到第 112 名”（U365 转述，原榜没找到）。
6. MiMo 自部署约 573.5 GB（单一来源）。
7. Step 5 的 92 层、MTP-3 等架构细节（媒体转述，官方页正文没见到）；开源许可证；GitHub 仓库。
8. Step 5 跑 AA 全套的总成本（$918 或 $925，两处二手数字）。
9. Step 5 早期测试者的工具调用和 34 万 token 附近的问题（单一来源）。
10. 阶跃是否已正式递表或通过聆讯（6 月只有“秘密递表”传闻，9 月进展没查到；本次 WebSearch 额度已用完）。
11. 吉利银河 M9 用 Step-Audio 2、首字响应 0.7 s（只见搜索摘要）。
12. “AGI Bar”是谁开的店。
13. TypeSafe 除 DCVC 以外的投资方；2 亿美元估值（Forbes 原文打不开）。
14. Jev 的地区限制、中国大陆可用性。
15. JevBench 的方法可靠性（个人业余项目，Beta）。

---

## 六、来源（访问日期都是 2026-09-28）

### Xiaomi MiMo
- [M1] 官方·模型更新（英文）https://mimo.mi.com/docs/en-US/updates/model
- [M2] 官方·模型更新（中文）https://mimo.mi.com/docs/zh-CN/updates/model
- [M3] 官方·V2.6 发布新闻 https://mimo.mi.com/docs/zh-CN/news/latest/v2-6
- [M4] 官方·按量计费价格 https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go
- [M5] 官方·快速开始（V2.5 下线公告）https://mimo.mi.com/docs/zh-CN/quick-start/summary/welcome
- [M6] 官方·Token Plan 订阅 https://mimo.mi.com/docs/zh-CN/tokenplan/Token%20Plan/subscription
- [M7] 官方·HF 模型卡 MiMo-V2.6-Pro-RL https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Pro-RL
- [M8] 官方博客·MiMo-V2.5-Pro-UltraSpeed（2026-06-08）https://mimo.xiaomi.com/zh/blog/mimo-tilert-1000tps
- [M9] Artificial Analysis·MiMo-V2.6-Pro https://artificialanalysis.ai/models/mimo-v2-6-pro
- [M10] IT之家 2026-09-22 https://www.ithome.com/1/005/496.htm
- [M11] IT之家 2026-09-17（直播训练）https://www.ithome.com/1/003/555.htm
- [M12] VentureBeat 2026-09-21（Carl Franzen）https://venturebeat.com/technology/better-than-deepseek-xiaomis-mimo-v2-6-pro-debuts-as-the-top-open-weights-model-in-the-world-alongside-cheaper-v2-6-flash
- [M13] SiliconANGLE 2026-09-22 https://siliconangle.com/2026/09/22/xiaomi-introduces-mimo-v2-6-series-open-source-ai-model-family/
- [M14] TechNode 2026-09-22 https://technode.com/2026/09/22/xiaomi-open-sources-mimo-v2-6-models-after-scaling-reinforcement-learning/
- [M15] CellCog·MiMo-V2.6 https://cellcog.ai/blog/mimo-v2-6/
- [M16] eesel·specs https://www.eesel.ai/blog/xiaomi-mimo-v2-6
- [M17] eesel·review 2026-09-23 https://www.eesel.ai/blog/xiaomi-mimo-v2-6-review
- [M18] kingy.ai·实测 https://kingy.ai/blog/mimo-v2-6-pro-benchmarks-specs-comparison/
- [M19] kingy.ai·免费渠道 https://kingy.ai/blog/mimo-v2-6-pro-free-access-pricing-setup/
- [M20] orcarouter·MiMo 对 Grok 4.7 https://www.orcarouter.ai/blog/mimo-v2-6-pro-grok-4-7-same-score-price-gap
- [M21] orcarouter·UltraSpeed https://www.orcarouter.ai/blog/xiaomi-mimo-v2-6-pro-ultraspeed
- [M22] UU AI Hub https://www.uuaihub.com/blog/xiaomi-mimo-v26-open-source-2026
- [M23] 新浪新闻（微博）“6 天训练烧掉 347 万美元” https://www.sina.cn/weibo/detail/5346313329444559.html
- [M24] 快科技 https://news.mydrivers.com/1/1152/1152935.htm
- [M25] Forkast 2026-09-22 https://forkast.news/xiaomis-mimo-v2-6-ships-open-weights-at-frontier-class-performance-and-the-timing-is-not-an-accident/
- [M26] University 365 review 2026-09-24 https://www.university-365.com/post/mimo-v2-6-pro-xiaomi-s-open-weights-flagship-scored-5-8-on-the-u365-ci-first-review-at-a-tenth-of
- [M27] Wikipedia·Xiaomi MiMo https://en.wikipedia.org/wiki/Xiaomi_MiMo
- [M28] 新浪科技·澎湃 OS 4（2026-08-19）https://finance.sina.com.cn/tech/mobile/n/n/2026-08-19/doc-ininuvaw8423761.shtml
- [M29] CNMO·澎湃 OS 4 https://phone.cnmo.com/news/816334.html
- [M30] GitHub Zoo-Code issue #1761（引用官方下线公告）https://github.com/Zoo-Code-Org/Zoo-Code/issues/1761
- [M31] DataLearner·MiMo-V2.6-Pro https://www.datalearner.com/ai-models/pretrained-models/mimo-v2-6-pro

### Artificial Analysis 榜单
- [A1] https://artificialanalysis.ai/leaderboards/models：2026-09-28 下载页面，解析内嵌数据，包括各模型智能指数、单题成本、速度、首 token / 首答案 token 时间、HLE、Terminal-Bench 4.0、是否开源、发布日期。

### 阶跃星辰 StepFun
- [S1] 官方·Step 5 Preview 发布页（浏览器渲染后读取）https://stepfun.com/step-5-preview
- [S2] 官方·开放平台模型文档 https://platform.stepfun.com/docs/zh/guides/models/step-5-preview
- [S3] 官方·价格（人民币）https://platform.stepfun.com/docs/zh/guides/pricing/details
- [S4] 官方·Pricing（美元）https://platform.stepfun.ai/docs/en/guides/pricing/details
- [S5] Artificial Analysis·Step 5 Preview https://artificialanalysis.ai/models/step-5
- [S6] CellCog “Step 5 Preview: Specs, Price, Benchmarks, and the Gaps”（2026-09-20）https://cellcog.ai/blog/step-5-preview/
- [S7] eesel 2026-09-21 https://www.eesel.ai/blog/stepfun-step-5
- [S8] MarkTechPost 2026-09-20 https://www.marktechpost.com/2026/09/20/stepfun-launches-step-5-preview/
- [S9] orcarouter·泄露评测 https://www.orcarouter.ai/blog/step-5-preview-leak
- [S10] 腾讯新闻 / 新智元 2026-09-20 https://news.qq.com/rain/a/20260920A07QYH00
- [S11] 腾讯新闻 / 赛博禅心 2026-09-20 https://news.qq.com/rain/a/20260920A07GHJ00
- [S12] GitHub litellm issue #42098（引用官方价目）https://github.com/BerriAI/litellm/issues/42098
- [S13] Hugging Face stepfun-ai/Step-5-Preview-BF16（访问返回 401）https://huggingface.co/stepfun-ai/Step-5-Preview-BF16
- [S14] StepFun 官方 X 帖（只见搜索结果，没打开）https://x.com/StepFun_ai/status/2101510462685003786
- [S15] 官方·Step 3.5 Flash 博客 https://static.stepfun.com/blog/step-3.5-flash/
- [S16] MarkTechPost·Step 3.7 Flash（2026-05-29）https://www.marktechpost.com/2026/05/29/stepfun-releases-step-3-7-flash-a-198b-moe-vision-language-model-for-coding-agents-and-search-workflows/
- [S17] Wikipedia·StepFun https://en.wikipedia.org/wiki/StepFun
- [S18] 每经网 2026-01-27（印奇出任董事长）https://www.nbd.com.cn/articles/2026-01-27/4237592.html
- [S19] 新浪财经 2026-06-10（秘密递表传闻）https://finance.sina.com.cn/stock/hkstock/2026-06-10/doc-iniaxkrt1220200.shtml
- [S20] 新浪财经 2026-05-10（“5 个月烧掉 171 亿”，实指融资额）https://finance.sina.com.cn/stock/marketresearch/2026-05-10/doc-inhxmeaf2582837.shtml
- [S21] 钛媒体（阶跃与月之暗面争相 IPO）https://www.tmtpost.com/7952134.html
- [S22] Digitimes 2026-06（120 亿美元估值，付费墙只看到摘要）https://www.digitimes.com/news/a20260609VL212/china-ai-startup-ipo-financing-deepseek-technology.html
- [S23] 新浪财经 2026-01-08（吉利银河 M9 CES 2026，只见搜索摘要）https://finance.sina.com.cn/stock/relnews/hk/2026-01-08/doc-inhfqtyt1318802.shtml

### TypeSafe AI / Jev
- [J1] 官方博客 “Introducing System One Models & Jev”（2026-09-15，Diogo Almeida；含折叠的 FAQ 原文）https://typesafe.ai/blog/introducing-system-one-models-and-jev
- [J2] 官网首页 https://typesafe.ai/
- [J3] 官方团队页 https://typesafe.ai/team
- [J4] 文档·Introduction https://docs.typesafe.ai/introduction
- [J5] 文档·Models https://docs.typesafe.ai/models
- [J6] 文档·System One https://docs.typesafe.ai/concepts/system-one
- [J7] 文档·Jev 1.13 jaggedness https://docs.typesafe.ai/model-jaggedness/jev-1.13
- [J8] 文档·Quickstart https://docs.typesafe.ai/introduction/quickstart
- [J9] TechCrunch 2026-09-18（Tim Fernholz）https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/
- [J10] Simon Willison 2026-09-21 https://simonwillison.net/2026/Sep/21/jev/
- [J11] Tom's Hardware 2026-09-21（Bruno Ferreira）https://www.tomshardware.com/tech-industry/artificial-intelligence/typesafe-ais-jev-offers-an-alternative-to-llms-that-claims-to-be-193x-faster-and-445x-cheaper-system-one-type-model-is-bespoke-for-probabilistic-decision-making
- [J12] Tom's Hardware 2026-09-27（Shane Downing，宝可梦）https://www.tomshardware.com/tech-industry/artificial-intelligence/developer-says-jev-decision-model-beat-pokemon-red-in-under-a-week-non-llm-engine-succeeds-where-traditional-chatbots-stalled-for-months-but-claude-opus-5-coached-the-model-through-its-dead-ends
- [J13] Wikipedia·Jev (AI model) https://en.wikipedia.org/wiki/Jev_(AI_model)
- [J14] SiliconANGLE 2026-09-16 https://siliconangle.com/2026/09/16/typesafe-ai-exits-stealth-with-40m-to-build-ai-for-use-by-software/
- [J15] The Register 2026-09-16（Thomas Claburn）https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711
- [J16] TS2 2026-09-17 https://ts2.tech/en/typesafe-ai-raises-40-million-for-jev-but-its-445x-cost-claim-is-still-self-tested/
- [J17] The Rundown AI 2026-09-16 https://www.therundown.ai/articles/chatgpt-co-creator-launches-a-new-kind-of-ai
- [J18] Forbes 2026-09-15（访问返回 403，没读到原文）https://www.forbes.com/sites/the-prompt/2026/09/15/this-200-million-startup-wants-to-fix-ais-overconfidence-problem/
- [J19] Hacker News 发布讨论帖 https://news.ycombinator.com/item?id=49717558
- [J20] JevBench（Benchmark Heaven）https://benchmarkheaven.com/jev-models
- [J21] arXiv 2203.02155（InstructGPT 论文作者表）https://arxiv.org/abs/2203.02155
- [J22] arXiv 1706.03741（Christiano et al. 2017，RLHF 早期论文）https://arxiv.org/abs/1706.03741
