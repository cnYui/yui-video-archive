# 第 3 期事实查证：Jev 模型是什么？和 LLM 有什么区别？

> 查询日期：2026-09-28（北京时间）。
> 来源标注：**官方** = TypeSafe AI 官网、官方博客、开发者文档、官方评测站、官方 X 账号 @typesafeai、官方新闻稿；**一手·CEO 发言** = CEO 本人在 Hacker News 的公开回复（不是正式文档）；**投资方 / 合作方** = DCVC、Vercel、OpenRouter 自己的页面；**二手** = 媒体、博客、个人文章（含第三方实测和推测）。
> 引文说明：按版权规范，全文只保留 1 句英文原文直引（不到 15 个词，在第 5 节）。其余官方表述都是中文转述，并注明页面和小节。需要把原文放上屏幕时，请到对应页面截取。字段名、模型 ID、数字、产品名、文章标题不算引文。

## 结论摘要

1. Jev 是 TypeSafe AI, Inc.（旧金山，2024 年成立）在 2026-09-15 发布的第一个"System One 模型"。你给它一份状态（state）和几道事先定好答案范围的问题，它并行给出每道题的选项、分数或"是"的概率，不生成文字。
2. 只有三种题型：Choice（多选一，最多 255 个选项）、Score（按 2–10 个有序等级打分）、Noul（"是"的概率，CEO 说名字来自 Bernoulli）。Choice 和 Score 另外带 confidence，Noul 不带。
3. 官方价格：输入 0.042 美元 / 百万 token（42 美元 / 十亿 token），输出免费；每次请求 64k token。官方博客说端到端 70–500 毫秒，前沿模型要 3–329 秒，所以快 40–200 倍。
4. 首页的"快 193.6 倍、便宜 444.6 倍"来自 TypeSafe 自己的 4 个工作流评测，官方也说这是"真实收益里偏高的一端"。在这份评测里，Jev 的一致率 67.8%，和 GPT-5.6 Terra（67.9%）差不多，低于最好的 74.1%。
5. "不会幻觉"的准确意思是：答案不会超出你给的选项和类型。官方 FAQ 明说它仍可能选错。"never hallucinates"是 DataCamp 的文章标题，不是官方原话。
6. 架构、参数量、训练数据细节、技术论文都没公开。训练方法 RLCD 只公布了名字和目标。"基于 Transformer""只用合成数据训练"是 TechCrunch 的报道（后者是 CEO 在采访里说的）。
7. 开放时间线（UTC）：9/15 候补名单 → 9/20 宣布人人可用、不用排队 → 9/22 需求太大，暂停注册 → 9/27 恢复注册，新用户不再送免费额度。
8. 它和 Meta / LeCun 的 JEPA 没有关系，官方文档全文没有 JEPA 字样。中文圈常见误读："永不幻觉""快 20–200 倍、便宜 40–400 倍""输出永久免费""每个答案都有置信度"。
9. 最大的不确定：速度、成本、准确率数字都是厂商自测。官方晒出的真实客户案例（Deel）在线上最多只快 4 倍。独立测试发现，它在 0.7–0.9 的置信度区间明显过于自信。

---

## 1. 基本信息

### 公司
- 公司全称 **TypeSafe AI, Inc.**：这是官方使用条款页开头写的法律实体名。隐私政策正文也出现 "Typesafe AI" 的写法，所以两种大小写都有。SiliconANGLE 写作 "TypeSafe AI Inc."。【来源：TypeSafe AI · Terms of Use，https://typesafe.ai/legal/terms ，查询日期 2026-09-28，官方】【来源：TypeSafe AI · Privacy Policy，https://typesafe.ai/legal/privacy-policy ，查询日期 2026-09-28，官方】
- 官网 https://typesafe.ai/ ；开发者文档 https://docs.typesafe.ai/ ；控制台和 Playground https://console.typesafe.ai/ ；评测站 https://evals.typesafe.ai/ ；官方 X 账号 @typesafeai。官网没有单独的定价页（https://typesafe.ai/pricing 返回 404）。【来源：TypeSafe AI 官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 公司自称是"做机器原生、可组合 AI 的前沿 AI 实验室"，2024 年成立，总部在旧金山。【来源：官方新闻稿《TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI》（Business Wire，2026-09-15。Business Wire 原页打不开，改读 Yahoo Finance 转载），https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html ，查询日期 2026-09-28，官方】
- 融资：9/15 结束隐身时宣布 4000 万美元种子轮，由 DCVC 领投。【来源：同上官方新闻稿，查询日期 2026-09-28，官方】【来源：DCVC《TypeSafe emerges from stealth with a new way of doing AI》，https://www.dcvc.com/news-insights/typesafe-emerges-from-stealth-with-a-new-way-of-doing-ai/ ，查询日期 2026-09-28，投资方】
- 估值 2 亿美元：只有 Forbes 报道过，消息源是"知情人士"，新闻稿里没有。Forbes 原文打不开，这里用的是 SiliconANGLE 的转述。【来源：SiliconANGLE《TypeSafe AI exits stealth with $40M to build AI for use by software》，2026-09-16，https://siliconangle.com/2026/09/16/typesafe-ai-exits-stealth-with-40m-to-build-ai-for-use-by-software/ ，查询日期 2026-09-28，二手】【来源：Forbes《This $200 Million Startup Wants To Fix AI's Overconfidence Problem》，https://www.forbes.com/sites/the-prompt/2026/09/15/this-200-million-startup-wants-to-fix-ais-overconfidence-problem/ ，查询日期 2026-09-28，二手，**打不开（403）**】

### 创始团队
- **Diogo Almeida**，联合创始人、CEO。官方团队页说他"共同发明了 RLHF 和 InstructGPT"（也就是 ChatGPT、GPT-4 背后的方法），之前在 Google Brain 工作。能独立核实的是：他是 InstructGPT 论文《Training language models to follow instructions with human feedback》（arXiv:2203.02155，2022-03）的第 4 作者；更早的 RLHF 奠基论文（Christiano 等，arXiv:1706.03741，2017）的作者里没有他。**视频里建议说"InstructGPT 论文作者之一，参与了 ChatGPT 背后的 RLHF 工作"，别说"RLHF 发明人"。**【来源：TypeSafe AI · Team，https://typesafe.ai/team ，查询日期 2026-09-28，官方】【来源：arXiv 2203.02155，https://arxiv.org/abs/2203.02155 ；arXiv 1706.03741，https://arxiv.org/abs/1706.03741 ，查询日期 2026-09-28，一手论文页】
- **Sasha Sheng**，COO，之前是 Meta/FAIR 的研究工程师。【来源：TypeSafe AI · Team，https://typesafe.ai/team ，查询日期 2026-09-28，官方】
- **Erik Gafni**，CTO，连续创业者（创办过 Ravel），做过 Invitae、Freenome 两家独角兽的早期员工。【来源：TypeSafe AI · Team，https://typesafe.ai/team ，查询日期 2026-09-28，官方】
- 团队页说成员来自 OpenAI、Google Brain、Meta/FAIR、Stripe、Airbnb、Plaid、Docker 等公司，在旧金山 Embarcadero 站附近办公。【来源：TypeSafe AI · Team，https://typesafe.ai/team ，查询日期 2026-09-28，官方】
- 发布文章由 Diogo Almeida 署名，文中说公司"隐身了两年"。【来源：官方博客《Introducing System One Models & Jev》，2026-09-15，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- Almeida 在 OpenAI 工作了多久：维基百科写"约四年，2024 年离开"，TechCrunch 写"两年前离开 OpenAI 创办 TypeSafe"。官方页面没有写任期。【来源：Wikipedia《Jev (AI model)》，https://en.wikipedia.org/wiki/Jev_(AI_model) ，查询日期 2026-09-28，二手】【来源：TechCrunch《A new kind of AI model from a ChatGPT inventor is thrilling developers》，Tim Fernholz，2026-09-18，https://techcrunch.com/2026/09/18/a-new-kind-of-ai-model-from-a-chatgpt-inventor-is-thrilling-developers/ ，查询日期 2026-09-28，二手】

### 发布和开放时间线
- **2026-09-15 发布**：同时推出 Jev 和"System One 模型"这个类别，以 early access（候补名单）方式开放。官方博客现在标的日期是 2026-09-15，但发布当天的网页存档里写的是 9/14，后来改过。新闻稿电头是"旧金山，2026-09-15"。Hacker News 发布帖的时间是 2026-09-15 19:25 UTC。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】【来源：官方新闻稿（Yahoo Finance 转载），同上，查询日期 2026-09-28，官方】【来源：Wayback Machine 存档（2026-09-15 20:07 UTC），http://web.archive.org/web/20260915200705/https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方页面存档】【来源：Hacker News《Introducing System One Models and Jev》，https://news.ycombinator.com/item?id=49717558 ，查询日期 2026-09-28，二手（讨论区）】
- **2026-09-20 21:30 UTC（北京时间 9/21 05:30）正式开放**：官方 X 宣布 Jev 对所有人开放、不用候补名单。这就是 "public access / 正式开放"。官方博客上没有单独的开放公告。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2101786156572823624 ，查询日期 2026-09-28，官方】
- **2026-09-22 06:19 UTC（北京时间 9/22 14:19）暂停注册**：官方 X 说需求太大，临时暂停新注册；已经注册的账号照常能用。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2102281508950307159 ，查询日期 2026-09-28，官方】
- **2026-09-27 22:30 UTC（北京时间 9/28 06:30）恢复注册**：官方 X 宣布算力扩容后恢复注册，同时说明新注册用户不再送免费额度。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2104337822350221795 ，以及 https://x.com/typesafeai/status/2104337824292220981 ，查询日期 2026-09-28，官方】
- 注意：官网首页 FAQ 里"怎么开始使用"那一问，现在还写着"加入候补名单"，是没更新的旧文案。【来源：TypeSafe AI 官网首页 FAQ，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方 SDK 版本：Python 包 typesafe-sdk 的首个公开版本 v0.5.7 标注 2026-09-14，之后是 v0.6.0（9/15）、v0.7.0（9/18）、v0.7.1（9/21）、v0.7.2（9/26）。JS SDK @typesafe-ai/sdk 的 v0.5.7 标注 2026-09-11。【来源：TypeSafe Docs · Python SDK Changelog，https://docs.typesafe.ai/sdk/python/changelog ；JavaScript SDK Changelog，https://docs.typesafe.ai/sdk/javascript/changelog ，查询日期 2026-09-28，官方】

### 型号和版本
- 目前只有一个模型：**Jev 1.13**，模型 ID `jev-1.13.0`。有两个别名：`jev-latest`（最新正式版，也是 SDK 的默认值）和 `jev-preview`（最新预览版）。两个别名现在都指向 `jev-1.13.0`，文档注明"目前没有预览版"。所有模型都走同一个端点 `POST /v1/systemone`，用请求里的 `model` 字段来选。【来源：TypeSafe Docs · Models，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】
- 官网页脚的 "Version 0.01" 是网站自己的装饰性版本号，不是模型版本。有 AI 网页摘要工具把它误读成"Jev v0.01"。【来源：TypeSafe AI 官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 所有账号用同一套权重，不提供按客户微调或 LoRA。想让它适应你的业务，只能靠 state 里放的资料和题目里写的规则。【来源：TypeSafe Docs · Models「Customizing Jev」，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】
- 第三方渠道（不是 TypeSafe 自己的型号）：OpenRouter 在 2026-09-25 上架了 "TypeSafe: Jev Router"（`typesafe/jev-router`），它用 Jev 给每个请求挑选 LLM 和推理强度，官方 X 也宣传了这件事。Vercel AI Gateway（`typesafe-ai/jev`）也能调用 Jev。另据二手文章，Cloudflare Workers AI 上也有。【来源：OpenRouter 模型列表接口，https://openrouter.ai/api/v1/models ，查询日期 2026-09-28，合作方】【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2103612889655353346 ，查询日期 2026-09-28，官方】【来源：Vercel《Jev is the fastest-adopted model in AI Gateway history》，https://vercel.com/blog/ai-gateway-jev-model-launch ，查询日期 2026-09-28，合作方】【来源：Towards Data Science（提到 Cloudflare 渠道），见第 4 节，二手】

### "Jev"这个名字
- 官方解释：名字取自 19 世纪经济学家 William Stanley Jevons（杰文斯）。蒸汽机效率提高后，煤的需求反而上升了（杰文斯悖论）。他们认为"智能"也会这样：成本每降一个数量级，用途就会多出好几个数量级。新闻稿的说法是"向杰文斯悖论致敬"。【来源：官方博客文末 FAQ「名字从哪来」，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】【来源：官方新闻稿（Yahoo Finance 转载），同上，查询日期 2026-09-28，官方】

---

## 2. "System One"这个叫法从哪来

- 官方明确说是受卡尼曼《思考，快与慢》启发：模型类别的名字取自"快速直觉的系统 1"和"缓慢审慎的系统 2"的区分。【来源：官方博客 FAQ「名字从哪来」，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】【来源：TypeSafe Docs · System One（页尾注释），https://docs.typesafe.ai/concepts/system-one ，查询日期 2026-09-28，官方】
- 官方也承认，"系统 1"常让人联想到"容易出错"。他们认为 System One 模型可以比其他方案更可靠，但说理由"以后再讲"，目前没给出论证。【来源：官方博客 FAQ，同上，查询日期 2026-09-28，官方】
- 文档的说法：重点是"快速、聚焦的判断"，也就是"一个懂行的人拿到资料后几秒钟就能做出的直觉判断"。需要长推理的问题，要拆成几个小问题，再在代码里组合。【来源：TypeSafe Docs · Introduction，https://docs.typesafe.ai/introduction ；Docs · Primitives，https://docs.typesafe.ai/primitives ，查询日期 2026-09-28，官方】
- 和 LLM 怎么分工：官方博客有一张对照表，题为"新旧前沿"。表里说 LLM 适合三类事：人在环路里的任务（聊天机器人、copilot、编程智能体）、能自动验证对错的问题（数学证明、内核优化）、快速做 demo。Jev 适合四类事：工作流里的"聪明 if 语句"、在大数据上做 map-reduce、实时应用，以及给 LLM 的提示、推理过程和输出打分、审核、做护栏、查越狱。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- 文档说，Choice 和 Score 的答案带置信度，代码可以据此决定是直接执行，还是升级给人或推理模型处理。首页 FAQ 说，需要长推理的任务（复杂数学、类似下棋的规划）更适合大型推理模型。【来源：TypeSafe Docs · System One，https://docs.typesafe.ai/concepts/system-one ，查询日期 2026-09-28，官方】【来源：官网首页 FAQ「Jev 擅长什么、在哪吃力」，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- **官方并没有把 LLM 正式叫作"System Two 模型"。** 文档只在"应避免的事"里，把"System Two 任务（多层间接推理）"列为 Jev 不该做的。把 LLM 直接叫"系统 2 / System Two"，是媒体和社区的延伸说法，比如 Medium 的 Skeptical AI、腾讯新闻上的稿件、博客园的文章。【来源：TypeSafe Docs · Jev 1.13 jaggedness，https://docs.typesafe.ai/model-jaggedness/jev-1.13 ，查询日期 2026-09-28，官方】【来源：Skeptical AI《LLM vs JEV: The Dual-Process AI Stack》，见第 5 节，二手】
- "Decision model / 决策模型"不是官方的类别名，官方类别名是 System One models。Simon Willison 说他同意 Maggie Appleton 的看法，认为叫 "decision models" 更好。官方文档在介绍训练目标时，也用过 decision models 这个描述。中文圈多译作"决策模型""判断模型""系统一模型"。【来源：Simon Willison《Jev introduces a new shape of LLM—System One, aka Decision Models》，2026-09-21，https://simonwillison.net/2026/Sep/21/jev/ ，查询日期 2026-09-28，二手】【来源：TypeSafe Docs · AI primer，https://docs.typesafe.ai/introduction/machine-learning-primer ，查询日期 2026-09-28，官方】

---

## 3. 工作原理

### 输入
- 一次请求 = 一份 `state` + 若干道 `questions`。state 就是要判断的内容，可以是字符串、JSON 对象或文本数组。比如把一段客服对话、订单记录和退款政策一起放进一个 JSON。目前只收文本，图片、音频、视频还不支持。【来源：TypeSafe Docs · State，https://docs.typesafe.ai/concepts/state ；Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- 每道题包括：你自己起的 ID；`type`（`choice` / `score` / `noul`）；`instructions`，即问题本身，可以是字符串，也可以是对象或数组；`criteria`，即 Choice 的选项表、Score 的有序等级表，或者 Noul 可选的"是 / 否各指什么"。题目 ID 只给你的代码用，不会发给模型。【来源：TypeSafe Docs · Primitives，https://docs.typesafe.ai/primitives ；Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- 题目里可以用反引号括起来的路径，指向 state 里的某个字段，比如 `ticket.messages[0].text`。【来源：TypeSafe Docs · Primitives，同上，查询日期 2026-09-28，官方】
- 英语是主要训练语言。中文等 CJK 文字能处理，但效果不如英语，官方建议先用自己的数据测试。这一点对中文观众值得提。【来源：TypeSafe Docs · Models「Language support」，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】

### 输出
- **Choice**：返回 `choice`（概率最高的选项）、`probabilities`（每个选项的概率，加起来等于 1）和 `confidence`（0–1）。最多 255 个选项。【来源：TypeSafe Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- **Score**：返回 `score`（按概率加权的位置，可以落在两级之间，比如 1.4）、`legend`（等级编号对应的描述）、`probabilities` 和 `confidence`。等级至少 2 个，最多 10 个。【来源：同上，查询日期 2026-09-28，官方】
- **Noul**：只返回 `noul`，一个 0–1 的数，表示"答案是 yes 的概率"，没有单独的 confidence（结果只有是和否两种，一个数就说清了）。它不是布尔值，多少算"是"要由你的代码设阈值。【来源：TypeSafe Docs · Noul，https://docs.typesafe.ai/primitives/noul ，查询日期 2026-09-28，官方】
- Noul 这个名字：CEO 在 Hacker News 上确认，它是 Bernoulli（伯努利分布）的缩写。他还把三种题型比作代码：choice 像 match 语句，score 像排序，noul 像 if 语句。【来源：Hacker News 上 CEO（账号 CompleteSkeptic）的回复，https://news.ycombinator.com/item?id=49718407 ，查询日期 2026-09-28，一手·CEO 发言】【来源：Simon Willison，同上，查询日期 2026-09-28，二手】
- confidence 不是模型另外报的一句"我有多确定"，而是从 probabilities 这个分布算出来的数：分布越集中，数值越高；越平均，数值越低。官方把完整概率也返回给你，你可以用自己的算法。具体公式官方没公布。【来源：TypeSafe Docs · Confidence，https://docs.typesafe.ai/confidence ，查询日期 2026-09-28，官方】
- 每个响应还带 `model`（实际作答的版本号，比如 `jev-1.13.0`）和 `usage`（`input_tokens`、`output_tokens`）。【来源：TypeSafe Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】

### "校准（calibrated）"是什么意思
- 官方的定义是：在大量预测里，标 0.2 概率的结果应该约有 20% 真的发生，标 0.8 的约有 80% 发生。这说的是一大批预测的统计规律，不保证任何单个答案正确。【来源：TypeSafe Docs · AI primer，https://docs.typesafe.ai/introduction/machine-learning-primer ；Docs · System One，https://docs.typesafe.ai/concepts/system-one ，查询日期 2026-09-28，官方】
- 官方建议把置信度分三档用：高就自动执行；中就谨慎处理（请人确认、送复核或补充信息）；低就不执行，转给人或别的系统。阈值要按出错的代价来定。【来源：TypeSafe Docs · Confidence，https://docs.typesafe.ai/confidence ，查询日期 2026-09-28，官方】

### 为什么能并行，"非自回归"指什么
- LLM 是一个 token 接一个 token 地顺序生成，每个 token 都依赖前一个；官方对照表把它的采样方式标为"顺序"。Jev 在一次查询里生成所有输出。官方博客的"并排演示"一节说，Jev 是并行输出所有概率，不是逐 token 自回归生成。媒体说的"非自回归（non-autoregressive）"就是这个意思，但这个词是媒体的概括（比如 MindStudio 的标题），官方博客的说法是"不逐 token 自回归地生成"。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】【来源：MindStudio《Jev Explained: Typesafe AI's Non-Autoregressive System-1 Model》，2026-09-18，https://www.mindstudio.ai/blog/jev-system-one-model-launch ，查询日期 2026-09-28，二手】
- 能并行的原因有两个。第一，每道题都只看同一份 state，题和题互相独立，一道题的答案不会变成另一道题的上下文。第二，CEO 在 HN 上说，输出里根本不允许出现字符串或任何序列结构，这样所有输出都能并行算出来，所以不收输出 token 费。官方说多加几道题，响应时间几乎不变。【来源：TypeSafe Docs · Introduction，https://docs.typesafe.ai/introduction ；Docs · Primitives，https://docs.typesafe.ai/primitives ，查询日期 2026-09-28，官方】【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49719122 ，查询日期 2026-09-28，一手·CEO 发言】
- 首页 FAQ 的解释是：用并行计算代替顺序生成。它还打了个比方，说从顺序到并行的跨越，就像 Transformer 取代 RNN。这只是比喻，不说明 Jev 用了什么架构。【来源：官网首页 FAQ「为什么能这么快、这么便宜」，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 代价是：同一次请求里的题不能互相依赖。如果后一道题要用前一道题的答案，需要在代码里再发一次请求。【来源：TypeSafe Docs · Primitives「When one question depends on another」，https://docs.typesafe.ai/primitives ，查询日期 2026-09-28，官方】

### 底层架构、参数量、训练
- 官方只说用了"新的模型架构、并行采样器（parallel sampler）和新的训练算法 RLCD"，没有公开架构细节、参数量、权重或技术论文。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ；官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- CEO 在 HN 上说，架构"暂时不公开"，团队讨论过写论文。【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718824 ，查询日期 2026-09-28，一手·CEO 发言】
- **是不是 Transformer：官方没说。** TechCrunch 报道说它"基于 Transformer"，还说外界猜测它是在某个开源权重的 LLM 基础上做的，Almeida 对架构不肯多谈。【来源：TechCrunch，同上，查询日期 2026-09-28，二手】
- 是不是从大语言模型训练出来的：官方 AI 入门文档的配图，把 RLCD 画成预训练语言模型之后的第三条后训练路线，另外两条是 RLHF 和 RLVR。HN 上有人据此推测"RLCD 是在预训练底座上做的"，CEO 对这条评论回复"没错"。但官方 FAQ 又说 Jev"既不小，也不是 LLM"；CEO 也说它"严格说不是语言模型，因为它不生成语言"。【来源：TypeSafe Docs · AI primer，https://docs.typesafe.ai/introduction/machine-learning-primer ，查询日期 2026-09-28，官方】【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718407 、https://news.ycombinator.com/item?id=49718437 ，查询日期 2026-09-28，一手·CEO 发言】【来源：官方博客 FAQ「Jev 只是更小的 LLM 吗」，同上，查询日期 2026-09-28，官方】
- **参数量：未公开。** 官方文档全文检索不到参数量；Towards Data Science 和 KDnuggets 的作者也说没公开。【来源：TypeSafe Docs 全文，https://docs.typesafe.ai/llms-full.txt ，查询日期 2026-09-28，官方】【来源：Towards Data Science、KDnuggets，见第 5 节，二手】
- **训练方法 RLCD**（Reinforcement Learning for Calibrated Decisions，校准决策强化学习）：官方只讲了目标：模型不生成文本，只输出决策和概率，而且概率越高，答对的可能越大。对照的是 RLHF（优化成人喜欢的回答）和 RLVR（优化能被程序验证的奖励）。具体算法没公开。【来源：TypeSafe Docs · AI primer，同上；官方博客对照表，同上，查询日期 2026-09-28，官方】
- 训练数据：官方博客 FAQ 说数据全部自己制作，也不会用客户数据训练；文档也写明 Jev 不用客户的请求和响应训练。"只用合成数据训练"这个说法，来自 CEO 接受 TechCrunch 的采访。另外 TechCrunch 把方法名写成了 "from calibrated decisions"，官方的写法是 "for"。【来源：官方博客 FAQ，同上；TypeSafe Docs · Models「Data handling」，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】【来源：TechCrunch，同上，查询日期 2026-09-28，二手】
- 第三方推测，**只供参考，别当事实**：Archer Hume 用大约 1 万次 API 调用反推，认为它像一个因果 Transformer：state 只编码一次、各题之间互相隔离、直接读出概率，可能还用了稀疏 MoE；它的分词器和 Qwen 最接近。这些都是推测。【来源：Archer Hume《Jev's Architecture Unmasked》，2026-09-17，https://archerhume.com/posts/jevs-architecture-unmasked/ ，查询日期 2026-09-28，二手·第三方推测】【来源：Mike E.《Jev, three days in: what is known, what is guessed, and what it is good for》，2026-09-18，https://aiwithmike.substack.com/p/jev-three-days-in-what-is-known-what ，查询日期 2026-09-28，二手】

---

## 4. 速度、延迟、成本、定价、上下文（每个数字的出处）

### 定价和使用限制（官方文档里直接写着的，最可靠）
- 价格：输入 0.042 美元 / 百万 token（也就是 42 美元 / 十亿 token），只按输入 token 收费，输出免费。首页的价格卡写的也是每十亿输入 token 42 美元。【来源：TypeSafe Docs · Models，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】【来源：官网首页价格卡，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方博客里的对比：现有 LLM 的输入价是 0.20–10 美元 / 百万 token，输出大约贵 5 倍；Jev 的输出"便宜到不值得计量"，所以免费。【来源：官方博客对照表，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- 首页说，Jev 的输入价比 Claude Fable 5.1 低 238 倍。【来源：官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 需要更高额度要找销售（sales@typesafe.ai）。官网没有单独的定价页。【来源：TypeSafe Docs · Models，同上，查询日期 2026-09-28，官方】
- 免费额度：官方 X 在 9/27 说，新注册用户不再送免费额度（说明之前送过）。之前送了多少：二手网站说是 5 美元（例如 explainx.ai《Jev General Availability: No Waitlist, $5 Free Credit (2026)》，只看到搜索结果里的标题，没打开）。Flavio Copes 指出官方文档没写免费额度，本文件也没在官方页面找到具体金额。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2104337824292220981 ，查询日期 2026-09-28，官方】【来源：explainx.ai，https://explainx.ai/blog/jev-general-availability-no-waitlist-2026 ，查询日期 2026-09-28，二手（未打开）】【来源：Flavio Copes《How to get access to Jev and an API key》，2026-09-24，https://flaviocopes.com/jev-api-key/ ，查询日期 2026-09-28，二手】
- 上下文：每次请求最多 64k token；state 加上最长的那道题不超过 32k。【来源：TypeSafe Docs · Models，同上，查询日期 2026-09-28，官方】
- 速率限制：每秒 25 万 token、每分钟 1200 次请求。官方说这些数字会随着 GPU 到位动态调整，可能不另行通知。【来源：TypeSafe Docs · Models，同上，查询日期 2026-09-28，官方】
- 题型上限：Choice 最多 255 个选项；Score 2–10 个等级。【来源：TypeSafe Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- 错误码：401（key 无效）、422（请求格式不对）、429（超出速率限制）、529（服务过载）。【来源：同上，查询日期 2026-09-28，官方】

### 速度和延迟（各官方渠道说法不一，见第 11 节）
- **"40–200 倍"的出处**：官方博客对照表说，TypeSafe 端到端响应 70–500 毫秒；前沿模型要 3–329 秒（这个数博客链接到了第三方网站 llm-benchmarks.diegoromero.es）；在"System One 型"问题上、智能水平相当时，快 40–200 倍。比较对象是笼统的"前沿模型"，没有指定具体模型和任务。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- 官方博客自己列的注意事项：公布的速度一般是从他们在美国西海岸的笔记本电脑上测的（服务目前也部署在西海岸）；成本方面，他们"无法证明价格没有补贴"。【来源：官方博客「Evidence / Technical Results」一节，同上，查询日期 2026-09-28，官方】
- **"193.6 倍 / 444.6 倍"的出处**：官网首页大字写着快 193.6 倍、便宜 444.6 倍，脚注说是"基于 System One 任务的工作流"。博客承认这组数来自他们自己的工作流评测，并说"很可能处在真实收益的偏高一端"。【来源：官网首页，https://typesafe.ai/ ；官方博客「Workflow evals」一节，同上，查询日期 2026-09-28，官方】
- 首页大字下面还有一张演示卡：TypeSafe 用时 0.114 秒、花费 0.000081 美元；LLM 用时 8.566 秒、花费 0.013880 美元。The Register 说演示里的 LLM 是 GPT-5.6 Terra。按这组数算，只快约 75 倍、便宜约 171 倍，和大字不是同一组对比。官方博客还说，那段并排演示用的是高度简化的查询和很短的输入，对 Jev 更有利；他们选 GPT-5.6 Terra 是因为觉得它平均智能和 Jev 最接近。【来源：官网首页，同上，查询日期 2026-09-28，官方】【来源：官方博客「Side-by-side demonstration」一节，同上，查询日期 2026-09-28，官方】【来源：The Register《TypeSafe AI debuts model for machines that plays Doom》，Thomas Claburn，2026-09-16，https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711 ，查询日期 2026-09-28，二手】
- **官方工作流评测站的原始数据**：4 个工作流分别是安全告警、智能体运行记录审查、发票处理、客服。参考答案是 GPT-6 Astra 和 Claude Fable 5.1（都开高思考档）答案的平均；其他模型用厂商的默认推理档。四个工作流等权平均后，每个案例的结果如下：
  - Jev：一致率 67.8%，每例 0.0004 美元，0.4 秒
  - OpenAI terra：67.9%，0.0304 美元，10.1 秒
  - OpenAI sol：74.1%，0.0836 美元，23.3 秒（一致率最高）
  - OpenAI luna：66.8%，0.0033 美元，12.9 秒
  - Anthropic opus 5：73.1%，0.1761 美元，37.8 秒
  - Anthropic sonnet 5：67.8%，0.1174 美元，78.1 秒
  - Anthropic haiku 4.5：53.6%，0.0195 美元，12.5 秒
  - DeepSeek v4 pro：65.5%，0.0413 美元，86.5 秒；v4 flash：64.4%，0.0059 美元，51.9 秒（页面标为 "DS v4"；图例里的提供方有 Fireworks，推测是通过它调用的）
  - 以上都是"拆成工作流"的版本。同一套规则如果写成一整段提示词，每个 LLM 的成绩都更差，比如 terra 从 67.9% 降到 61.6%。评测页上模型只写简称；官方博客里提到的是 GPT-5.6 Terra。
  【来源：TypeSafe Workflow evals，https://evals.typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方博客自己列的评测偏差：工作流是他们模型能力团队的人做的，可能有偏；参考答案偏向 OpenAI 和 Anthropic 的模型；被比较的 LLM 都套了 TypeSafe 自己的"System One LLM 适配器"，让它们也输出结构化决策，这样通常更慢、更贵。【来源：官方博客「Workflow evals」一节，同上，查询日期 2026-09-28，官方】
- **本文件的推算（不是官方说明）**：193.6 倍接近 Jev 和最慢的 sonnet 5 相比（78.1 秒 ÷ 0.4 秒 ≈ 195）；444.6 倍接近和最贵的 opus 5 相比（0.1761 ÷ 0.0004 ≈ 440）。也就是说，两个数字很可能各自挑了最有利的对比对象。评测站没有写明是怎么算的。【来源：根据 https://evals.typesafe.ai/ 的数据推算，查询日期 2026-09-28，推算】
- 新闻稿和投资方用的是另一套说法：延迟"低于 100 毫秒"，"最多快 100 倍、也便宜 100 倍"。【来源：官方新闻稿（Yahoo Finance 转载），同上，查询日期 2026-09-28，官方】【来源：DCVC，同上，查询日期 2026-09-28，投资方】
- 文档里还有几种说法：大多数查询约 100 毫秒完成；实时场景写的是 150 毫秒；"便宜 100 倍"。【来源：TypeSafe Docs · How to build with TypeSafe，https://docs.typesafe.ai/concepts/how-to-build-with-system-one ；Docs · Example use cases，https://docs.typesafe.ai/concepts/use-case-map ，查询日期 2026-09-28，官方】
- **官方晒出的真实客户案例（Deel）**：在旁路跟跑真实线上流量时，"最多快 4 倍"；离线测试快 2–3 倍。准确率方面，重复问题匹配从 70% 升到 97%，费用分类从 50% 升到 86%（以人工审核为标准）。这些是官方 X 转述的客户数据，没有公布对比的基线细节。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2103321896553210029 ；https://x.com/typesafeai/status/2103321894661595551 ，查询日期 2026-09-28，官方】
- 官方博客的 Doom 演示：每秒查询 10 次，约 7 美元 / 小时。输入是文字形式的游戏状态，不是游戏画面。【来源：官方博客「Fun Demos」一节，同上，查询日期 2026-09-28，官方】

### 第三方测出的数字（二手）
- Towards Data Science 作者 Nhu Hoang 在 Banking77 数据集（3080 条银行客服消息，77 个类别）上实测：Jev 准确率 81.1%，在本地运行的 Qwen3-Coder-Next 是 76.4%。中位延迟 245 毫秒对 249 毫秒；作者说这不算干净的对比，因为 Qwen 在本地跑，Jev 是从日本访问远程服务器。【来源：Towards Data Science《Jev vs. LLMs: When AI Moves from Generation to Decision-Making》，2026-09-25，https://towardsdatascience.com/jev-vs-llms-when-ai-moves-from-generation-to-decision-making/ ，查询日期 2026-09-28，二手·第三方实测】
- 同一篇文章转述了 Every.to 的测试：每段检查的中位用时，Jev 0.35 秒，Claude Fable 5.1（高推理档）8.83 秒。【来源：同上，查询日期 2026-09-28，二手转述】

---

## 5. "不会幻觉 / never hallucinates"：谁说的，什么意思

- 官方的原始说法有两处。第一处是官方博客：开头说 Jev 放弃了字符串生成、专为结构化输出优化，所以 "can't hallucinate"；对照表里还说模型"从不犯类型错误"。第二处是官网首页：有一块大标题写着 "Zero Hallucinations"（零幻觉），下面的说明是"每个决策都带置信估计"。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ；官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方给的依据在博客"幻觉与类型安全"一节：他们认为两者本质相关。图里 LLM 的结构化输出错误率、工具调用错误率来自 OpenRouter 的数据；Jev 的 0% **不是实测出来的**，而是因为"答案一定符合 schema"，所以直接填了 0%。【来源：官方博客「Hallucination and Type-safety」一节，同上，查询日期 2026-09-28，官方】
- **官方自己的限定**（本文件唯一一句英文直引，出自官网首页 FAQ「Jev 还会出错吗？」的回答）："Jev guarantees the shape of its answers, not that every decision is correct." 同一段回答还举了例子：你给出几个类别，它不会编出列表以外的类别，但可能选错。【来源：官网首页 FAQ，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方文档的限定：校准说的是一批预测的整体情况，不保证单个答案正确。【来源：TypeSafe Docs · System One，https://docs.typesafe.ai/concepts/system-one ；Docs · AI primer，https://docs.typesafe.ai/introduction/machine-learning-primer ，查询日期 2026-09-28，官方】
- CEO 在 HN 上的回应：有人指出"它输出不了非法类型，但可以输出一个完全错误的合法值"。CEO 说这对所有机器学习模型都成立，并认为说随机森林会"幻觉"不公平。另一处他承认，这类模型是概率性的，也可能"很自信地答错"。还有人说"类型安全不等于事实正确"，他回复非常同意。【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718767 、https://news.ycombinator.com/item?id=49718780 、https://news.ycombinator.com/item?id=49719080 ，查询日期 2026-09-28，一手·CEO 发言】
- **"never hallucinates" 是 DataCamp 的文章标题**（作者 Matt Crabtree，2026-09-16），不是 TypeSafe 的原话。文章正文的解释是：输出被 schema 约束，所以不可能出现非法值或类型错误。【来源：DataCamp《Jev: TypeSafe's System One Model That Never Hallucinates》，https://www.datacamp.com/blog/system-one-models-jev ，查询日期 2026-09-28，二手（curl 访问被 403 拦截，改用 WebFetch 读取）】
- 官方开发者文档里找不到"不会幻觉"的说法。这个说法只出现在博客和首页这类宣传文字里。【来源：TypeSafe Docs 全文，https://docs.typesafe.ai/llms-full.txt ，查询日期 2026-09-28，官方】
- **给视频用的准确说法**："不会幻觉"指的是不会给出你规定范围以外的答案，也不会出格式错误；不等于答案一定对。它可能在合法选项里选错，而且可能选错时还很自信。

### 独立评测、批评和局限性讨论
- The Register：说它"无幻觉"不是公平比较，因为它根本不输出自然语言；结构化的答案也可能是错的。【来源：The Register，同上，查询日期 2026-09-28，二手】
- KDnuggets（Abid Ali Awan，2026-09-21）："零幻觉"更接近"零越界输出"，不等于"零错误决策"。给任意标签做零样本分类，在 NLP 里早就有了，比如 facebook/bart-large-mnli；Jev 新在架构和产品形态上。【来源：KDnuggets《What Everyone Is Getting Wrong About TypeSafe AI's Jev》，https://www.kdnuggets.com/what-everyone-is-getting-wrong-about-typesafe-ais-jev ，查询日期 2026-09-28，二手】
- Simon Willison（2026-09-21）：他在标题里把 Jev 称为"一种新形态的 LLM"，认为它适合做垃圾信息检测、打标签、排序和搜索结果重排。他的不安是：Jev 比 LLM 更像黑箱，只返回一个浮点数，看不出判断依据；偏见问题应该放在首位，他希望没人用它给求职者排序。他让 Jev 给湾区各城市回答"是不是好城市"，结果 Cupertino 排第一、East Palo Alto 排最后。他的结论是：做评测和实验比普通 LLM 项目更重要，好在它很便宜，跑几千次实验只要几美分。【来源：Simon Willison，同上，查询日期 2026-09-28，二手】
- Towards Data Science 的独立实测：置信度正好是 1.00 的 1516 条消息里，对了 97.1%，仍然错了 44 条。0.7–0.9 这一段平均置信度 0.81，实际只对了 53%；0.9–0.99 这一段平均置信度 0.95，只对了 79%。也就是说，中间这一段明显过于自信。把低置信的消息转给 Qwen 处理的级联方案，结果全都比只用 Jev 更差。文章还转述了别人的测试：PriorBench 给 Jev 30 条不属于任何类别、又没有"以上都不是"选项的消息，Jev 每一条都硬选了一个类别，而且置信度都在 0.99 以上；scienthoon 测得 Score 题的校准误差（ECE）是 0.325，远差于 Choice 的 0.082 和是非题的 0.079。【来源：Towards Data Science，同上，查询日期 2026-09-28，二手·第三方实测 / 转述】
- VentureBeat（Louis Columbus，2026-09-21）：Octomind 的一位工程师在输入里伪造了一段"用户已提前批准"的工具输出，结果 Jev 判断"应该拦截"的概率从 0.76 降到 0.48，说明提示注入能影响它的判断。官方文档也承认，Jev 默认不会把 state 当作恶意内容来防。【来源：VentureBeat《Companies are putting Jev in charge of AI agent decisions — and prompt injection can influence the verdict》，https://venturebeat.com/security/companies-are-putting-jev-in-charge-of-ai-agent-decisions-and-prompt-injection-can-influence-the-verdict ，查询日期 2026-09-28，二手（curl 读不到正文，改用 WebFetch 读取）】【来源：TypeSafe Docs · Jev 1.13 jaggedness「Adversarial content」，https://docs.typesafe.ai/model-jaggedness/jev-1.13 ，查询日期 2026-09-28，官方】
- TechStock²：193.6 倍、444.6 倍都是自己测的。评测不是和客观的标准答案比，而是和两个大模型的平均概率比；被比较的 LLM 还套了 TypeSafe 自己的适配器。【来源：TechStock²《TypeSafe AI Raises $40 Million for Jev, but Its 445× Cost Claim Is Still Self-Tested》，2026-09-17，https://ts2.tech/en/typesafe-ai-raises-40-million-for-jev-but-its-445x-cost-claim-is-still-self-tested/ ，查询日期 2026-09-28，二手】
- Hacker News 发布帖（查询时 1984 分、520 条评论）里有代表性的质疑：速度对比是拿苹果比橘子；"不会幻觉"的说法站不住；它本质上像以前的编码器模型或零样本分类器；官方说"不是 LLM"，文档却显示它是从 LLM 衍生出来的；也有人说，如果把 LLM 也限定在同一组标签里输出，LLM 同样不会"编出第四个选项"。【来源：Hacker News，https://news.ycombinator.com/item?id=49717558 ，查询日期 2026-09-28，二手（讨论区）】
- Skeptical AI（Medium，2026-09-21）：支持"系统 1 + 系统 2 双过程架构"的说法，但把 Jev 和 LeCun 的 JEPA 放在一起讲（见第 9 节，这种混搭没有依据）。文中还说 RLCD 能"确保"85% 置信度对应 85% 准确率，这比官方的说法更绝对。网页直接访问是 403，本文件通过作者的 RSS 读到了全文。【来源：Skeptical AI《LLM vs JEV: The Dual-Process AI Stack》，https://medium.com/@skeptical_ai/llm-vs-jev-the-dual-process-ai-stack-1eb29f95d1dc ，查询日期 2026-09-28，二手】
- 官方自己列出的"已知毛病"（针对 jev-1.13，2026-09-17 复核）：
  - 按字面理解问题。
  - 不会算数，也数不准。
  - 把日期当成文本，比较日期不可靠。
  - 多跳推理和双重否定会让它变差。
  - state 里无关的信息越多越不准。
  - 对抗性内容和提示注入会影响结果。
  - instructions 和 criteria 互相矛盾时会混乱。
  - 同一个问题分别用 Noul 和 Choice 问，数值不一定对得上；一个问题和它的反面各问一次，两个概率加起来也不一定等于 1。
  - 不适合生成文本。
  【来源：TypeSafe Docs · Jev 1.13 jaggedness，https://docs.typesafe.ai/model-jaggedness/jev-1.13 ，查询日期 2026-09-28，官方】

---

## 6. 典型用途和"不适合做什么"

### 官方举的用途
- 官方博客对照表列的用途：工作流里的"聪明 if 语句"（分类、路由、打分、抽取、分支）；在大数据上做 map-reduce；实时应用；给 LLM 的提示、推理过程和输出打分、审核、做护栏、查越狱。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- 官方文档的用例地图，按决策类型分：
  - 分类
  - 检测（垃圾信息、欺诈、紧急情况、越狱、敏感数据）
  - 打分
  - 路由（工具调用、升级处理、模型路由、客服队列）
  - 搜索和检索（RAG 的上下文）
  - 排序
  - 校验（引用是否支撑结论、是否违反政策、工具调用是否出错）
  - 给传统机器学习模型提供特征
  - 结构化数据抽取
  行业例子有客服、内容审核、保险理赔、金融犯罪、法务合规、电商、广告、游戏、招聘等。【来源：TypeSafe Docs · Example use cases，https://docs.typesafe.ai/concepts/use-case-map ，查询日期 2026-09-28，官方】
- 和智能体（agent）有关的官方例子：模型路由，让 Jev 决定每个提示交给哪个 LLM；LLM 护栏，检查每一次输入、输出和工具调用；给智能体的这一轮挑技能（Skill suggestion 案例：从 182 个技能里最多挑 1 个）；意图路由，决定交给固定代码、专门的 LLM 还是人工。【来源：TypeSafe Docs · Example use cases，同上；Docs 索引 llms.txt 里的 Guardrails for LLMs、Skill suggestion 等案例，https://docs.typesafe.ai/llms.txt ；Docs · Intent routing，https://docs.typesafe.ai/patterns/intent-routing ，查询日期 2026-09-28，官方】
- "选哪个工具、工作流是继续、重试、问用户还是停下"这组说法出自 Vercel 的博客（合作方）。TypeSafe 文档里对应的是"路由"类下的工具调用和升级处理，没有专门写"是否结束"。【来源：Vercel，同上，查询日期 2026-09-28，合作方】【来源：TypeSafe Docs · Example use cases，同上，查询日期 2026-09-28，官方】
- 要注意的是，官方文档说 System One 是用来构建"AI 驱动的软件"的，不是用来做智能体的：它不写代码，也不自己决定下一步做什么，流程由你的代码控制。【来源：TypeSafe Docs · How to build with TypeSafe，https://docs.typesafe.ai/concepts/how-to-build-with-system-one ，查询日期 2026-09-28，官方】
- 官方演示有三个：打 Doom（每秒决策 10 次）；维基百科跳转竞速（每一步都要从几百到几千个链接里挑，超过 255 个选项时先逐个打分再挑）；智能家居助手。【来源：官方博客，同上；TypeSafe Docs · Demos，https://docs.typesafe.ai/demos ，查询日期 2026-09-28，官方】
- 官方 X 晒出的 Deel 用例：匹配重复提问、从 36 个指标里挑 1 个、拦截涉及个人隐私的请求、判断客服对话要不要转人工、按三级分类给工单打标签、把费用归到大约 55 个类别里。官方的总结是：每一个都是从一个已知的集合里挑。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2103321892421865838 ，查询日期 2026-09-28，官方】

### 官方说的"不适合"
- 不生成文本、不写代码、不聊天、不解释自己的推理过程；也不能替代 Claude Code、Cursor 这类编程智能体背后的 LLM。【来源：TypeSafe Docs · Jev with coding agents，https://docs.typesafe.ai/introduction/coding-agents ；Docs · System One，https://docs.typesafe.ai/concepts/system-one ，查询日期 2026-09-28，官方】
- 需要长推理的任务（复杂数学、类似下棋的规划）更适合大型推理模型。【来源：官网首页 FAQ，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 数学、计数、精确数值、日期比较要交给代码；多跳推理、在 state 里塞大量无关信息、对抗性内容，都要小心。【来源：TypeSafe Docs · Jev 1.13 jaggedness，https://docs.typesafe.ai/model-jaggedness/jev-1.13 ，查询日期 2026-09-28，官方】
- 只接收文本，不接收图片、音频、视频；非英语的效果较差。【来源：TypeSafe Docs · Models，https://docs.typesafe.ai/models ；Docs · State，https://docs.typesafe.ai/concepts/state ，查询日期 2026-09-28，官方】
- 据 Flavio Copes 描述，控制台欢迎页还列出了"System 2 任务、专业领域、任何生成类任务"。控制台要登录才能看，本文件没法直接核对。【来源：Flavio Copes，同上，查询日期 2026-09-28，二手】
- 一个矛盾：官方用例地图里有"招聘"（评估简历、给能力打分、匹配岗位），而 Simon Willison 恰好明确担心有人用 Jev 给求职者排序，因为其中的偏见很难发现。【来源：TypeSafe Docs · Example use cases，同上，查询日期 2026-09-28，官方】【来源：Simon Willison，同上，查询日期 2026-09-28，二手】

---

## 7. 和 LLM 的区别（逐条）以及怎么配合

速查表（每行的出处见表下的逐条说明）：

| 维度 | 普通 LLM | Jev |
|---|---|---|
| 输出 | 任意文本（回答、代码、JSON 等），软件要先解析、校验 | 事先定义好的类型化答案：选项、分数、"是"的概率 |
| 生成方式 | 一个 token 接一个 token 顺序生成 | 一次请求里所有题并行算出，不逐 token 生成 |
| 速度（官方口径） | 端到端 3–329 秒 | 70–500 毫秒 |
| 计费 | 输入、输出都收费，输出更贵 | 只收输入，0.042 美元 / 百万 token；输出免费 |
| 置信度 | 可以让它"说"一个置信度，官方认为往往过于自信、前后不一致 | 直接返回概率分布；Choice 和 Score 还有 confidence |
| 可解释性 | 能给出理由（理由不一定可靠） | 只有数字，没有理由（Simon Willison 批评它更像黑箱） |
| 写文章、聊天、写代码 | 能 | 不能 |
| 输入 | 非结构化数据（如文本），偏向一条条对话消息 | 只收文本，偏向结构化的程序状态 |
| 训练目标 | RLHF（人喜欢的回答）或 RLVR（能验证的奖励） | RLCD（概率要校准的决策） |
| 典型场景 | 聊天、写作、编程智能体、开放式推理 | 分类、路由、打分、审核、护栏、大批量判断 |

逐条说明：
- 输出、生成方式、速度、计费、置信度、输入、训练目标、典型场景这几行，出自官方博客的对照表。【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- "只收文本、不能写文章聊天写代码"出自官方文档。【来源：TypeSafe Docs · System One，https://docs.typesafe.ai/concepts/system-one ；Docs · Jev with coding agents，https://docs.typesafe.ai/introduction/coding-agents ，查询日期 2026-09-28，官方】
- Noul 没有 confidence 字段。【来源：TypeSafe Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- "只有数字、没有理由"的批评。【来源：Simon Willison，同上，查询日期 2026-09-28，二手】
- 实际速度差距取决于任务：官方的客户案例（Deel）线上最多快 4 倍；TDS 测试里 Jev 和本地 Qwen 的中位延迟几乎一样。【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2103321896553210029 ，查询日期 2026-09-28，官方】【来源：Towards Data Science，同上，查询日期 2026-09-28，二手·第三方实测】

两者怎么配合：
- 意图路由（官方模式）：Jev 先给请求分类。有把握的交给固定代码或专门的 LLM 处理，没把握的转给人工。【来源：TypeSafe Docs · Intent routing，https://docs.typesafe.ai/patterns/intent-routing ，查询日期 2026-09-28，官方】
- LLM 护栏（官方案例）：进出 LLM 应用的每条消息，都用一次 Jev 请求检查一遍，再按危险概率和严重程度决定放行、复核、拦截还是改道。【来源：TypeSafe Docs 索引 llms.txt，Guardrails for LLMs 案例，https://docs.typesafe.ai/llms.txt ，查询日期 2026-09-28，官方】
- 抽取级联（官方案例 SDE cascade）：小模型先抽取，Jev 负责校验，必要时再交给推理模型，用更低的成本拿到大模型的大部分质量。【来源：同上，查询日期 2026-09-28，官方】
- 官方文档的通用说法：置信度低的时候，升级给人或推理模型。【来源：TypeSafe Docs · System One，同上，查询日期 2026-09-28，官方】
- 合作方的产品：OpenRouter 的 Jev Router 用 Jev 给每个请求挑选 LLM 和推理强度。【来源：OpenRouter 模型列表接口，https://openrouter.ai/api/v1/models ，查询日期 2026-09-28，合作方】【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2103612889655353346 ，查询日期 2026-09-28，官方】
- 二手的概括：LangChain 的博客说"开放式推理和生成交给 LLM，沿途快速的结构化决策交给 Jev"，还提供了模型路由中间件和工具调用风险拦截中间件。这句话是 LangChain 说的，不是 TypeSafe 说的。【来源：LangChain《What Is Jev? A Guide to TypeSafe AI's System One Model》，https://www.langchain.com/blog/building-a-harness-with-jev ，查询日期 2026-09-28，二手】
- 一个反例：TDS 实测里，把 Jev 没把握的消息转给另一个 LLM，整体准确率反而下降了。知道哪道题难，不等于别的模型能答对。【来源：Towards Data Science，同上，查询日期 2026-09-28，二手·第三方实测】
- 官方评测还说明一点：把任务拆成工作流（代码加上多个窄问题）之后，每个 LLM 自己也都更准、更便宜、更快。所以"拆题"本身就是收益的来源之一，不全是 Jev 的功劳。【来源：TypeSafe Workflow evals，https://evals.typesafe.ai/ ，查询日期 2026-09-28，官方】

---

## 8. API 用法示意（用来画示意卡片）

- 端点：`POST https://api.typesafe.ai/v1/systemone`。请求头：`Authorization: Bearer <API Key>` 和 `Content-Type: application/json`。【来源：TypeSafe Docs · API reference，https://docs.typesafe.ai/api ，查询日期 2026-09-28，官方】
- 请求体有三个必填字段：`state`、`model`（比如 `"jev-latest"`）和 `questions`（题目 ID 对应题目对象）。题目对象包括 `type`、`instructions` 和 `criteria`。【来源：同上，查询日期 2026-09-28，官方】
- 响应体包括：`model`（实际作答的版本号）、`answers`（题目 ID 对应答案对象）和 `usage`（`input_tokens`、`output_tokens`）。答案对象都带 `type`，其余字段按题型不同：Noul 是 `noul`；Choice 是 `choice`、`probabilities`、`confidence`；Score 是 `score`、`legend`、`probabilities`、`confidence`。【来源：同上，查询日期 2026-09-28，官方】
- 其他入口：网页版 Playground（console.typesafe.ai/playground）；Python SDK（`pip install typesafe-sdk`，读取环境变量 `TYPESAFE_API_KEY`，默认用 `jev-latest`，调用方法是 `client.system_one(...)`）；JS SDK `@typesafe-ai/sdk`；列出可用模型用 `GET /v1/models`。【来源：TypeSafe Docs · Quick start，https://docs.typesafe.ai/introduction/quickstart ；Docs · Models，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】

**示意卡片**：按官方字段名自己编写，内容和数值都是虚构的，不是官方示例，也不含真实 key。

```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <你的 API Key>
Content-Type: application/json
```

```json
{
  "model": "jev-latest",
  "state": "我前天买的耳机还没发货，明天出差前必须收到，不然就退款！",
  "questions": {
    "team": {
      "type": "choice",
      "instructions": "这条消息该交给哪个组？",
      "criteria": { "shipping": "发货、物流", "refund": "退款、退货", "tech": "产品故障" }
    },
    "urgent": { "type": "noul", "instructions": "消息是否表达了紧急？" },
    "anger": {
      "type": "score",
      "instructions": "客户有多生气？",
      "criteria": ["平静", "不满", "非常愤怒"]
    }
  }
}
```

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "team":   { "type": "choice", "choice": "shipping",
                "probabilities": { "shipping": 0.72, "refund": 0.28, "tech": 0.0 },
                "confidence": 0.55 },
    "urgent": { "type": "noul", "noul": 0.96 },
    "anger":  { "type": "score", "score": 1.3,
                "legend": { "0": "平静", "1": "不满", "2": "非常愤怒" },
                "probabilities": { "0": 0.0, "1": 0.7, "2": 0.3 },
                "confidence": 0.45 }
  },
  "usage": { "input_tokens": 320, "output_tokens": 60 }
}
```

画卡片时注意：
- 题目 ID（team / urgent / anger）只是给代码看的名字，不会发给模型，所以问题要完整写在 `instructions` 里。【来源：TypeSafe Docs · Primitives，https://docs.typesafe.ai/primitives ，查询日期 2026-09-28，官方】
- Noul 返回的是概率，不是 true / false；多少算"是"，由代码里的阈值决定。【来源：TypeSafe Docs · Noul，https://docs.typesafe.ai/primitives/noul ，查询日期 2026-09-28，官方】
- 官方说英语效果最好、中文较差。卡片用中文示意没问题，但别让人以为中文和英文一样准。【来源：TypeSafe Docs · Models，同上，查询日期 2026-09-28，官方】
- confidence 的算法官方没公布，只说是从概率分布算出来的，所以示意数值不要当真。【来源：TypeSafe Docs · Confidence，https://docs.typesafe.ai/confidence ，查询日期 2026-09-28，官方】

---

## 9. 容易混淆的东西

### Jev 和 JEPA 不是一回事
- JEPA（Joint Embedding Predictive Architecture，联合嵌入预测架构）是 Meta / Yann LeCun 提出的自监督学习架构。它在表示（嵌入）空间里，用输入的一部分去预测另一部分，代表作是 2023-06-13 发布的 I-JEPA。【来源：Meta AI《I-JEPA: The first AI model based on Yann LeCun's vision for more human-like AI》，https://ai.meta.com/blog/yann-lecun-ai-model-i-jepa/ ，查询日期 2026-09-28，一手（Meta 官方）】
- TypeSafe 的官网、博客和开发者文档全文都没有出现 JEPA 或 LeCun。Jev 的名字来自经济学家 Jevons（见第 1 节）。两者的公司、目的和原理都不同，没有已知的关系。【来源：本文件对 https://docs.typesafe.ai/llms-full.txt 和官网页面的全文检索，查询日期 2026-09-28，官方】
- 混淆的一个来源：Medium 上 Skeptical AI 的文章，把"TypeSafe 的 Jev 和更广义的 JEPA 范式"写在同一句里，好像它们是一类东西，这没有任何官方依据。也有中文文章专门澄清两者不同，比如 EggStriker 和 Challen 王的文章。【来源：Skeptical AI，同上，查询日期 2026-09-28，二手】【来源：EggStriker《「JEV」是什么：TypeSafe AI 首个 System One 模型 Jev——已发布功能、价格、发布时间与接入方式》，https://www.eggstriker.com/blog/jev-typesafe-system-one-2026 ；Challen 王《读懂 Jev：从分类器到决策模型》，https://challenwang.com/projects/jev-explained.html ，查询日期 2026-09-28，二手】

### Jev 和分类模型、BERT 类编码器模型
- 相同点：都是"输入文本，输出类别概率"，都不生成文字。HN 上有人把 Jev 概括成"零样本分类器"，CEO 回复"完全正确"。也有人把它叫"大型分类模型"，CEO 回复"很准确"，只补充说他更愿意用"零样本"而不是"指令微调"来形容。【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718727 、https://news.ycombinator.com/item?id=49719101 ，查询日期 2026-09-28，一手·CEO 发言】
- 不同点（官方和 CEO 的说法）：传统分类器的类别在训练时就定死了，需要标注数据来训练。Jev 是通用模型，类别和评分标准在每次请求里用自然语言现写，不需要训练（CEO 说"完全不用训练"；文档说不给客户做微调，所有账号共用一套权重）。另外，它一次能问好几道题，并返回校准过的概率。【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49719245 ，查询日期 2026-09-28，一手·CEO 发言】【来源：TypeSafe Docs · Models「Customizing Jev」，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】
- 二手观点：KDnuggets 认为，给任意标签做零样本分类并不新（比如 2019–2020 年流行的 facebook/bart-large-mnli），新的是架构、校准训练和产品形态。TDS 指出，BERT 类分类器的标签通常在训练时就固定了；它还提到 2025 年有个叫 Laya 的开源模型，用 ModernBERT 编码器试过类似的思路（但不能据此推断 Jev 的架构）。另外，官网首页那张模型谱系小图里，"berts" 字样旁边标着 "<low intelligence>"（低智能）。【来源：KDnuggets，同上；Towards Data Science，同上，查询日期 2026-09-28，二手】【来源：官网首页，https://typesafe.ai/ ，查询日期 2026-09-28，官方】

### Jev 和 LLM 的结构化输出、JSON mode、function calling
- 官网首页 FAQ 的说法：合法的 JSON 只是让软件能读懂；强迫 LLM 输出这种格式，可能会浪费它的一部分能力。System One 模型从一开始就是为结构化决策训练的，返回带校准概率的类型化答案，代码可以据此决定是执行、补充信息还是升级处理。【来源：官网首页 FAQ「和 JSON mode / 结构化输出有什么不同」，https://typesafe.ai/ ，查询日期 2026-09-28，官方】
- 官方文档的说法：可以用 Jev 替换那种"让 LLM 返回 JSON"的脆弱提示词，换成天生就返回类型化值的调用。【来源：TypeSafe Docs · Jev with coding agents，https://docs.typesafe.ai/introduction/coding-agents ，查询日期 2026-09-28，官方】
- CEO 在 HN 上的观点：OpenAI 那种约束解码会让模型变笨。只屏蔽不合法的 token 不够，因为模型本来就给不合法的 token 分了概率，说明它已经"困惑"了。这是 CEO 的个人观点，没有公开数据支持。【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718849 ，查询日期 2026-09-28，一手·CEO 发言】
- 公平地讲：LLM 用结构化输出或约束解码，也能保证输出合法的 JSON，HN 上有人指出过。Jev 真正的区别有三点：一是直接给出每个选项的概率分布和 confidence；二是不逐 token 生成，所以快，而且输出免费；三是不能输出开放式的文字。【来源：HN 讨论，https://news.ycombinator.com/item?id=49718492 ，查询日期 2026-09-28，二手】【来源：官方博客对照表，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- function calling：官方有一个案例，把自然语言的交易指令变成对普通函数的调用。但它只对"取值来自固定列表"的参数有效（枚举、布尔、多选）：函数名和参数都变成 Choice 题来选。自由文本的参数它生成不了；官方建议先用正则表达式或生成模型抽出候选，再让 Jev 来挑。【来源：TypeSafe Docs · Function calling 案例，https://docs.typesafe.ai/cookbooks/function_calling ；Docs · Jev 1.13 jaggedness「Generation」，https://docs.typesafe.ai/model-jaggedness/jev-1.13 ，查询日期 2026-09-28，官方】

---

## 10. 中文圈的报道口径

常见叫法：Jev 模型、决策模型、判断模型、System One 模型 / 系统一模型、"快思考模型"、"反 LLM 新物种"、"基模"。

比较准确的：
- 卡码笔记《Jev模型正式开放：System One决策模型、API价格与用法，和GPT-6 Astra、Claude Fable 5.1怎么选》（最后更新 2026-09-23）：讲清了"正式开放不等于开源"；"零幻觉"只是"不会返回类型以外的答案"；193.6 倍 / 444.6 倍是 TypeSafe 自己的评测，官方也承认偏高；中文场景要自己评测。缺点是没提 9/22 暂停注册。【来源：https://notes.kamacoder.com/llm/news/jev-model-public-access.html ，查询日期 2026-09-28，二手】
- eigent.ai 中文博客《什么是 Jev？TypeSafe AI 的 System One 模型详解》：基本准确，强调数据是厂商自报的、校准说的是一批预测的整体情况；但仍写着"处于早期访问阶段"，已经过时。【来源：https://www.eigent.ai/zh-CN/blog/typesafe-ai-jev-system-one-models ，查询日期 2026-09-28，二手】

有明显误读或夸大的：
- **"永不幻觉""消灭幻觉"**：极道的文章《ChatGPT共同发明人发布Jev基模：号称永不幻觉、比GPT快200倍》（页面打不开，只看到搜索结果里的标题）；腾讯新闻上的《Jev模型：又快又便宜，消灭幻觉，轻松打败顶流LLM》。官方的原意只是"答案不越界"，而且官方承认它会选错。【来源：https://www.jdon.com/94896-typesafe-jev-system-one-model-launch.html （打不开）；https://news.qq.com/rain/a/20260919A099H700 ，查询日期 2026-09-28，二手】
- **"快 20–200 倍、便宜 40–400 倍"**：腾讯新闻那篇和 36氪《输出token永久免费，Jev爆火后，开源版也跟着火了》都这么写，博客园《2026年完整指南：什么是 Jev？TypeSafe「系统一模型」如何让 AI 决策快 200 倍、便宜 400 倍》直接放在标题里。官方博客（包括发布当天的存档）只写了"快 40–200 倍"，首页写的是"快 193.6 倍、便宜 444.6 倍"，新闻稿写的是"最多 100 倍"，都没有"20–200 倍"或"40–400 倍"。知乎上还有标题写"响应速度快200倍"的文章（只看到搜索结果标题）。【来源：https://www.36kr.com/p/3991444838857731 ；https://www.cnblogs.com/sing1ee/p/23040079 ；腾讯新闻，同上；https://zhuanlan.zhihu.com/p/2083623440221738481 （未打开），查询日期 2026-09-28，二手】
- **"输出 token 永久免费"**：官方只说输出免费，因为"便宜到不值得计量"；同时也说无法证明价格没有补贴，还预计价格会降。官方没有承诺"永久"。【来源：36氪，同上，查询日期 2026-09-28，二手】【来源：官方博客，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- **"每个答案都带置信度"**：Noul 没有单独的 confidence 字段。不过官方博客和首页自己也写了"所有答案都带置信度"，宣传文字和开发者文档本身就不一致。博客园那篇沿用了这个说法。【来源：博客园，同上，查询日期 2026-09-28，二手】【来源：TypeSafe Docs · Noul，https://docs.typesafe.ai/primitives/noul ，查询日期 2026-09-28，官方】
- **"上下文 32K"**：博客园那篇这么写。官方的规定是每次请求 64k，state 加上最长的那道题不超过 32k。【来源：博客园，同上，查询日期 2026-09-28，二手】【来源：TypeSafe Docs · Models，https://docs.typesafe.ai/models ，查询日期 2026-09-28，官方】
- **把首页演示卡（0.114 秒对 8.566 秒）当成"193.6 倍"的出处**：博客园那篇这么写，但两组数算不到一块（演示卡只相当于约 75 倍）。【来源：博客园，同上，查询日期 2026-09-28，二手】
- **"Boolean"**：AIHub《Jev - TypeSafe AI 推出的首个 System One 决策模型》把是非题叫 Boolean，官方名称是 Noul；该页还写着"需要通过候补名单"，已经过时。【来源：https://www.aihub.cn/ai-model/typesafe-jev/ ，查询日期 2026-09-28，二手】
- **把第三方的推测写成事实**：腾讯新闻那篇列出"在 1200 道 MMLU 题上期望校准误差 0.0313""推测是稀疏 MoE，活跃参数约 100 亿"。这些来自社区博主通过 API 反推（Archer Hume 等人），不是 TypeSafe 公布的；官方明确说不发布公开基准测试成绩。【来源：腾讯新闻，同上，查询日期 2026-09-28，二手】【来源：官方博客 FAQ「在公开基准上表现如何」，https://typesafe.ai/blog/introducing-system-one-models-and-jev ，查询日期 2026-09-28，官方】
- **"反 LLM 新物种"**：Tony Bai《刚刚，TypeSafe 发布“反 LLM”新物种 JEV：0.1 秒出结果、宣称零幻觉、比大模型便宜上百倍》。官方的定位是和 LLM 互补：CEO 说更大的希望不只是抢 LLM 的市场，而是让 AI 更多地进入软件的核心流程。"0.1 秒"对应的是首页演示卡上的 0.114 秒。【来源：https://tonybai.com/2026/09/20/jev-typesafe-system-one-model-intro/ ，查询日期 2026-09-28，二手】【来源：HN 上 CEO 的回复，https://news.ycombinator.com/item?id=49718875 ，查询日期 2026-09-28，一手·CEO 发言】
- **往机器人、具身智能上蹭**：36氪《Jev爆火，具身智能迎来大救星？》、搜狐《Jev三天14万人涌入，但真正该兴奋的是做机器人的那批人》。官方没有发布过任何机器人相关的东西；社区里开车、无人机之类的 demo 都跑在模拟器里，MindStudio 也提醒过这一点。"14 万人"来自 VentureBeat 转述 Almeida 的话（36 小时内从候补名单放行约 14 万人），在官方渠道没找到原文。【来源：https://www.36kr.com/p/3994311534384773 ；https://www.sohu.com/a/1078631648_123000789 ，查询日期 2026-09-28，二手】【来源：MindStudio，同上；VentureBeat，同上，查询日期 2026-09-28，二手】
- **开放日期**：36氪写"9 月 21 日全面开放"，这是按北京时间算的；官方 X 的发帖时间是 UTC 9 月 20 日 21:30。【来源：36氪，同上，查询日期 2026-09-28，二手】【来源：TypeSafe AI 官方 X，https://x.com/typesafeai/status/2101786156572823624 ，查询日期 2026-09-28，官方】

---

## 11. 查不到或有矛盾的地方

1. **官方各渠道的速度和成本倍数不一致。** 博客说 70–500 毫秒、快 40–200 倍；新闻稿和 DCVC 说低于 100 毫秒、最多快 100 倍并便宜 100 倍；文档说大多约 100 毫秒、实时场景 150 毫秒、便宜 100 倍；首页大字说快 193.6 倍、便宜 444.6 倍；首页演示卡只相当于约 75 倍 / 171 倍；Deel 的真实部署最多快 4 倍。视频里建议只用一种说法并讲明出处，比如"官方博客称端到端 70–500 毫秒"。
2. **193.6 / 444.6 是怎么算的，官方没写。** 本文件按评测站的数据推算，它们分别接近"对比最慢的 sonnet 5"和"对比最贵的 opus 5"的倍数，这是推测，不是官方说明。评测站也没写样本数量，"711 个案例"只在 TDS、aiwithmike 这类二手文章里出现过。
3. **"便宜 40–400 倍""快 20–200 倍"查不到官方出处。** 维基百科、DataCamp、LangChain（写的是"最多快 200 倍、便宜 400 倍"）和多篇中文文章都这么写，但官方博客和首页里都找不到，包括 9/15 当天的网页存档。据一条 HN 评论，HN 发布帖最初的标题就用了 "40-400x cheaper and 20-200x faster"，这可能是源头，但无法核实。【来源：HN 评论，https://news.ycombinator.com/item?id=49719001 ，查询日期 2026-09-28，二手】
4. **"不会幻觉"。** 官方宣传文字（博客的 "can't hallucinate"、首页的 "Zero Hallucinations"）和官方 FAQ、文档里的限定（会选错；校准不保证单个答案）同时存在。准确的意思是"不越界、不出类型错误"。"never hallucinates"是 DataCamp 的标题，不是官方原话。开发者文档里没有"不会幻觉"这种说法。
5. **"所有答案都带置信度"**（博客、首页）和 API 文档（Noul 没有 confidence 字段）不一致。
6. **Jev 算不算 LLM，说法矛盾。** 官方 FAQ 说它"既不小，也不是 LLM"，CEO 说它"严格说不是语言模型"。但官方 AI 入门文档把 RLCD 画成预训练语言模型之后的一条后训练路线，CEO 也认可"在预训练底座上做 RLCD"。Simon Willison 直接称它"一种新形态的 LLM"。视频里可以说"它很可能也是从大语言模型底座训练出来的，只是不再生成文字"，并注明这是推断。
7. **架构说法各不相同。** 官方只说"新架构"；TechCrunch 说"基于 Transformer"；DataCamp 说它"和 Transformer LLM 很不一样"（措辞含糊）。The Register 把 RLCD 说成一种"架构"，但官方明确 RLCD 是训练方法。MindStudio 说它像软件一样"确定"，而官方 FAQ 说他们追求的是"一致性"（意思相近的输入给出相近的判断），不是"确定性"。参数量、权重、论文都没公开。
8. **"只用合成数据训练"** 只见于 TechCrunch 对 CEO 的采访，官方博客的说法是"数据全部自己做"。
9. **创始人背景。** "共同发明 RLHF"是公司自己的说法，能核实的是他是 InstructGPT 论文的作者。他在 OpenAI 工作了多久（维基百科说"约四年"），没找到一手出处；团队页还写了他在 Google Brain 的经历。另外，MindStudio 和一些搜索摘要把名字写成了 "Diego Almeida"，正确的是 Diogo Almeida。
10. **估值 2 亿美元** 只来自 Forbes（消息源是知情人士），Forbes 原文打不开；新闻稿没提估值；TechStock² 说融资公告里没有披露正式估值。
11. **能不能注册，状态变了好几次。** 9/20 开放 → 9/22 暂停 → 9/27 恢复（不再送免费额度）。首页 FAQ 仍写"加入候补名单"；AIHub、eigent 等仍写"早期访问 / 候补名单"；"5 美元免费额度"只见于二手文章，官方文档没写具体数目。出片前建议再看一次官方 X。
12. **价格能否持续。** 博客说"无法证明价格没有补贴"，首页 FAQ 说"按现在的价格能盈利"，两句话有点矛盾。"永久免费"是媒体的说法。
13. **官方文档内部的小矛盾。** 同一个"多题并行提问"的案例，Primitives 页写"便宜 11.5 倍、快 9.6 倍"，案例页和 llms.txt 写"便宜 12.2 倍、快 10.0 倍"。博客日期现在显示 9/15，发布当天的存档显示 9/14。
14. **中文稿件里的"MMLU 校准误差 0.0313""稀疏 MoE、约 100 亿活跃参数"** 来自第三方反推，官方没有发布过任何公开基准成绩。
15. **"36 小时 14 万人"** 只见于 VentureBeat 转述 Almeida 的话。"Vercel 近 13% 付费团队 24 小时内用上"（36氪、VentureBeat）这个具体数字，我读到的 Vercel 博客正文里没有；正文说的是 18 小时内达到约十分之一的团队，24 小时内使用的付费团队数是以往任何新模型的两倍多。13% 可能来自图表或其他页面，没有核实。
16. **打不开或只能间接读取的页面：**
  - Forbes 两篇：403，打不开。
  - Business Wire 新闻稿原页：拒绝访问，改读 Yahoo Finance 转载。
  - DataCamp、VentureBeat：用 curl 访问被拦截，改用 WebFetch 读取。
  - Medium 上 Skeptical AI 的文章：403，改从作者的 RSS 读到全文。
  - 极道（jdon）：返回空页面。
  - console.typesafe.ai：显示 Cloudflare 验证页，控制台内容只能转引 Flavio Copes 的描述。
  - 知乎专栏：没有打开。
  - Wayback 的 CDX 查询接口：临时不可用，改用 availability 接口取到了 9/15 的博客和首页存档。
