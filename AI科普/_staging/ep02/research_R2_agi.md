# 第 2 期查证 R2：AGI 的定义与 2026 年 9 月的现状

- 查询日期：2026-09-27（所有“截至”均指这一天）
- 方法：WebSearch / WebFetch，加上直接下载官方页面和数据文件（ARC Prize 排行榜 JSON、METR 时间跨度 YAML、Dwarkesh 与 Lex Fridman 访谈文字稿）。
- 可信度三档：
  - **已核实**：读到了一手来源原文（论文、官方博客、官方文档、官方数据文件、访谈文字稿）。
  - **较确定**：一手页面抓不到（如 openai.com 返回 403），但有多家可靠媒体或官方页面的检索摘要一致转述。
  - **存疑**：只有单一二手来源，或各来源说法对不上。
- 与 R1（research_R1_history.md 第 7 节）有两处口径差异，见第 7 节“易错点”第 1、2 条。

---

## 0. 给台本的一页结论

1. **AGI = Artificial General Intelligence，通用人工智能。** 没有统一定义。主流有三类：
   - 按**经济价值**：OpenAI 章程，“在大多数有经济价值的工作上超过人类的高度自主系统”。
   - 按**表现 × 通用性分级**：Google DeepMind《Levels of AGI》，分 0–5 级。2023 年他们把 ChatGPT 这类模型放在第 1 级“Emerging（初现）”。
   - 按**学习效率**：Chollet / ARC Prize，AGI 是“能像人一样高效地学会任何新技能”的系统。
2. **截至 2026-09-27，没有公认的“已实现 AGI”。**
   - 有高管个人说过“到了”：黄仁勋（2026-03、2026-09-06），Greg Brockman 在 GPT-6 Astra 发布会上说“Welcome to the AGI era”（2026-09-03）。
   - OpenAI 的官方发布文案没有正式宣布实现 AGI。Altman 在 2026-08 接受 TIME 采访时说“还没完全到（not quite yet）”。
   - 负责 ARC-AGI 测试的 ARC Prize 明确表示：“我们不认为 Astra 是 AGI”。Chollet、Marcus、Hassabis、LeCun 都认为还没到，或者说现有证据不够。
   - 也有学者认为已经到了：2026-02 发表在《Nature》的一篇评论，作者 Chen、Belkin 等四人。
   - 没有监管机构或标准组织给出过认证标准。
3. **微软—OpenAI 的“专家小组核实 AGI”条款**：2025-10-28 写进新协议；2026-04-27 两家再次修改协议，官方公告里不再提 AGI，收入分成改为“与 OpenAI 的技术进展无关”。多家媒体因此认为 AGI 条款在商业上已经失效。
4. **最新测试成绩**（按 ARC Prize 官方数据）：
   - ARC-AGI-2：顶尖模型已达 95%（GPT-6 Astra），人类测试者平均约 60%。这套题基本被做满。
   - ARC-AGI-3（2026-03 发布，交互式新游戏）：发布时 AI 不到 1%。2026-09 GPT-6 Astra 用标准框架得 62.7%，用 OpenAI 自己的适配框架得 99.9%。
5. **METR 时间跨度**（AI 有 50% 把握完成的任务，相当于人类专家要做多久）：GPT-4（2023）约 4 分钟。Claude Mythos Preview（2026-04）约 17 小时，但 METR 自己说超过 16 小时的测量不可靠；80% 把握只有约 3 小时。从 2023 年起大约每 4 个月翻一倍。
6. **离 AGI 还差什么**：适合台本的 4 条（都是“某某认为”，不是定论）：
   - 持续学习 / 长期记忆
   - 可靠性（幻觉、一致性，同一件事时对时错）
   - 开放式的长任务与真实世界
   - 物理世界
7. **“AI 不就是文字接龙”说对了一半。**
   - 对的一半：模型确实是一个词一个词往外生成的，预训练的目标也确实是预测下一个词。
   - 另一半：之后还有人类反馈强化学习（RLHF）和推理强化学习；可解释性研究发现，模型写诗时会提前规划韵脚。
   - “算不算理解”，学界至今各执一词。

**结尾措辞建议**：“截至 2026 年 9 月，有人说 AGI 已经到了，也有人说还差得远。这取决于你用哪个定义。能确定的是：AI 能独立完成的任务越来越长，但在持续学习、可靠性和真实世界这些地方，还有公认的短板。”
（不要说“已经实现 AGI”，也不要说“离 AGI 还很远”。两边都是观点。）

---

## 1. AGI 是什么：全称与代表性定义

| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 1.1 | AGI 全称 Artificial General Intelligence，中文“通用人工智能”。这个词最早由 Mark Gubrud 在 1997 年使用，2002 年前后由 Shane Legg、Ben Goertzel 推广开。 | 1997 / 约 2002 | https://en.wikipedia.org/wiki/Artificial_general_intelligence | 较确定 |
| 1.2 | **OpenAI 章程定义**原文：“highly autonomous systems that outperform humans at most economically valuable work”。中文：在大多数有经济价值的工作上，表现超过人类的高度自主系统。 | 章程 2018-04 发布 | https://openai.com/charter/ （官网对抓取返回 403；官网检索摘要与 TIME 2026-08-26、METR agi.pdf 等转述一致） | 较确定 |
| 1.3 | 据 The Information 报道，微软与 OpenAI 的合同里曾把 AGI 定义成“能给投资人带来 1000 亿美元利润的系统”。说明商业合同里的 AGI 定义也不固定。 | 2024-12 报道 | https://simonwillison.net/2026/Apr/27/now-deceased-agi-clause/ （转述 The Information） | 较确定 |
| 1.4 | **Google DeepMind《Levels of AGI》**，作者 Morris、Sohl-Dickstein、Fiedel、Warkentin、Dafoe、Faust、Farabet、Legg。用“表现水平（深度）× 通用性（广度）”两个维度给 AI 分级，并提出 6 条原则（看能力不看过程、看潜力不看部署等）。 | arXiv v1 2023-11-04；v5 2025-09-24 | https://arxiv.org/abs/2311.02462 | 已核实 |
| 1.5 | 分级（表现以“有技能的成年人”为参照）。第 4 级在 v1 里叫 Virtuoso，v5 改名 Exceptional。<br>0 级 No AI<br>1 级 Emerging（初现）：等于或略好于没受过训练的普通人<br>2 级 Competent（胜任）：≥ 50 百分位<br>3 级 Expert（专家）：≥ 90 百分位<br>4 级 Exceptional / Virtuoso（卓越）：≥ 99 百分位<br>5 级 Superhuman（超人）：超过 100% 的人类 | 同上 | https://arxiv.org/html/2311.02462v5 表 1 | 已核实 |
| 1.6 | **他们把当时的聊天模型放在第 1 级“Emerging AGI”。** 表 1 的“通用”一栏列 ChatGPT、Bard、Llama 2（v5 加了 Gemini）。原文说：截至 2023 年 9 月，前沿语言模型在写短文、简单编程等少数任务上达到 Competent，但在数学、事实性等多数任务上仍是 Emerging。第 2 级“Competent AGI”在写作时“还没有任何公开系统达到”。 | 2023-09 撰写 | https://arxiv.org/html/2311.02462v5 | 已核实 |
| 1.7 | **Legg & Hutter 的定义**（整理了约 70 种说法后归纳）：“intelligence measures an agent's ability to achieve goals in a wide range of environments”，即智能是在各种各样的环境里达成目标的能力。 | 2007 | https://arxiv.org/abs/0712.3329 | 较确定 |
| 1.8 | **Chollet《On the Measure of Intelligence》**把智能定义为“skill-acquisition efficiency”，即**技能获取效率**：看学会新技能有多快、要多少经验，不看已经会多少。论文同时发布了 ARC（Abstraction and Reasoning Corpus，抽象与推理语料库）。原文还指出：先验知识或训练数据不限量时，可以“买到”任意高的技能分数，这会掩盖系统真正的泛化能力。 | 2019-11-05 | https://arxiv.org/abs/1911.01547 | 已核实 |
| 1.9 | **ARC Prize 对 AGI 的表述**：“AGI is a system that can match the learning efficiency of humans.” ARC-AGI-3 页面：“As long as there is a gap between AI and human learning, we do not have AGI.” 2026-09 的博客写作：能像人一样高效地学会人能学会的任何技能。 | 2026 | https://arcprize.org/arc-agi ；https://arcprize.org/arc-agi/3 ；https://arcprize.org/blog/astra | 已核实 |
| 1.10 | **《A Definition of AGI》**（Hendrycks、Bengio、Tegmark、Gary Marcus、Eric Schmidt 等 30 多人）：AGI 是“在认知的多样性和熟练度上达到或超过受过良好教育的成年人”的 AI。按心理学 CHC 理论拆成 10 个认知领域，每项占 10%。打分结果：GPT-4 27%，GPT-5 57%。结论：能力呈“锯齿状”，知识类强，**长期记忆存储**明显不足（二手报道称 GPT-4、GPT-5 这一项都是 0%）。 | arXiv 2025-10-21（v3 2025-12-03） | https://arxiv.org/abs/2510.18212 ；https://www.agidefinition.ai/ | 已核实（0% 这个数：较确定） |
| 1.11 | **Google DeepMind 认知框架**：用 10 种认知能力衡量 AGI 进展（感知、生成、注意、学习、记忆、推理、元认知、执行功能、问题解决、社会认知），方法是和有代表性的成年人样本对比。他们认为测评空白最大的是学习、元认知、注意、执行功能、社会认知。 | 2026-03-17 | https://blog.google/innovation-and-ai/models-and-research/google-deepmind/measuring-agi-cognitive-framework/ | 已核实 |

**台本可用的一句话**：“AGI 没有统一定义。有人按‘能不能干活’算，有人按‘分几级’算，有人按‘学得快不快’算。”

---

## 2. 截至 2026-09-27 的状态

### 2.1 谁说过“已经实现 AGI”，谁说还没有

| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 2.1.1 | Sam Altman 在 Big Technology 播客里说，AGI“kinda went whooshing by”（好像一晃就过去了），“okay, fine, we built AGIs”；又说社会影响没有想象中大，并提议改用“超级智能”的说法。 | 2025-12-18 | https://www.bigtechnology.com/p/sam-altman-on-openais-plan-to-win （文字稿付费，引语来自多家转述） | 较确定 |
| 2.1.2 | 《Nature》评论《Does AI already have human-level intelligence? The evidence is clear》，作者 Eddy Keming Chen、Mikhail Belkin、Leon Bergen、David Danks。他们认为按合理标准，现在的大模型已经具备通用智能，并逐条反驳了 10 种常见反对意见。文章引发争论，有学者撰文反驳。 | 2026-02-04 | https://www.nature.com/articles/d41586-026-00285-6 ；https://techxplore.com/news/2026-02-artificial-general-intelligence-case-today.html | 较确定 |
| 2.1.3 | 英伟达 CEO 黄仁勋在 Lex Fridman 播客第 494 期说：“I think it's now. I think we've achieved AGI.” 他用的是自己的标准：AI 能创办并运营一家市值 10 亿美元的公司。 | 节目页 2026-03-23 发布 | https://lexfridman.com/jensen-huang-transcript/ | 引语已核实；定义较确定 |
| 2.1.4 | Altman 接受 TIME 采访时说，OpenAI “not quite yet”（还没完全到）AGI，预计年底前会有一个他愿意称为 AGI 的内部系统。首席研究官 Mark Chen 估计已经走了“80%”。 | 2026-08-26 | https://time.com/article/2026/08/26/openai-sam-altman-interview/ | 较确定 |
| 2.1.5 | **GPT-6 Astra 发布**：OpenAI 总裁 Greg Brockman 在媒体简报会上说“Welcome to the AGI era”，还说如果有人要把这个模型当成第一个 AGI，“我觉得是合理的”（Fortune 引语）。各家报道一致指出：OpenAI **没有正式宣布**实现 AGI。 | 2026-09-03 | https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/ ；https://www.axios.com/2026/09/03/openai-astra-gpt-6-agi-brockman ；https://slashdot.org/story/26/09/03/1932255/ | 较确定（各家引语措辞略有出入） |
| 2.1.6 | OpenAI 在开发者社区的官方发布帖只说 Astra 是“the most intelligent and aligned model in the world”，并写“helping ensure that AGI benefits all of humanity”（这是使命表述），没有宣布“已实现 AGI”。 | 2026-09-03 | https://community.openai.com/t/introducing-gpt-6-astra-the-most-intelligent-and-aligned-model-in-the-world/1394703 | 已核实 |
| 2.1.7 | 黄仁勋在 X 上发帖：“GPT-6 Astra, trained on ~100K+ NVIDIA Grace Blackwell NVLink72. From ChatGPT to o1 to Astra in 4 years. AGI has arrived.” | 2026-09-06 | https://x.com/JensenHuang/status/2096700264569090384 ；Fox Business、TechRadar 等转述 | 较确定 |
| 2.1.8 | **ARC Prize 官方**：ARC-AGI-3 发布时就说过，把这套测试做满也不能证明实现了 AGI；“we are not claiming that it is AGI”（我们不认为 Astra 是 AGI）。理由是 ARC-AGI-3 的范围很窄，环境规则是确定的、目标是封闭的，“不代表真实世界的复杂和开放”。 | 2026-09-03 | https://arcprize.org/blog/astra | 已核实 |
| 2.1.9 | Chollet 表示 Astra 在 ARC-AGI-3 上的高分“不是 AGI 的证明”。同时他说进展比预想快，自己原先“2030 年前后”的 AGI 预期要提前。 | 2026-09-04 报道 | https://the-decoder.com/benchmarks-disagree-on-gpt-6-astra-but-its-human-beating-efficiency-on-arc-agi-3-pulls-chollets-agi-forecast-forward/ | 较确定 |
| 2.1.10 | Gary Marcus：“Success on ARC-AGI is great and impressive, but not — despite the name of the task — proof of AGI.” 他预计 Astra 在开放式真实任务上会暴露不少问题，并批评外界对它的工作原理几乎一无所知。 | 2026-09 初 | https://garymarcus.substack.com/p/hot-take-on-gpt-6-astra | 已核实 |
| 2.1.11 | Demis Hassabis（Google DeepMind CEO）在印度 AI 影响力峰会上说 AGI“在未来 5 到 8 年内”可能出现，现在的系统是“锯齿状智能（jagged intelligence）”，缺一致性、持续学习、长期规划和创造力。 | 2026-02-18 | https://www.storyboard18.com/brand-makers/google-deepmind-ceo-says-agi-not-here-yet-calls-current-ai-jagged-intelligence-90028.htm | 较确定 |
| 2.1.12 | 两家独立评测机构对 Astra 的排名不一致：Epoch AI 排第一，Artificial Analysis 最初给出的分数与 GPT-5.6 Sol 持平。说明“是不是最强”都还有争议，更不用说“是不是 AGI”。 | 2026-09-04 | 同 2.1.9 | 较确定 |

**小结**：截至 2026-09-27，有高管个人说过“到了”，有学者撰文说“到了”；也有测试机构和一线研究者明确说“还没到”或“证据不够”。**没有正式宣布，没有独立认证，没有共识。**

### 2.2 微软—OpenAI 协议里的 AGI 条款

| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 2.2.1 | 新的最终协议原文：“Once AGI is declared by OpenAI, that declaration will now be verified by an independent expert panel.” 即 OpenAI 宣布实现 AGI 后，要由独立专家小组核实。 | 2025-10-28 | https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ | 已核实 |
| 2.2.2 | 同一协议还写：微软的研究类 IP 权利保留到“专家小组核实 AGI 或 2030 年，以先到者为准”；收入分成保留到“专家小组核实 AGI”为止；微软可以独立去做 AGI。 | 2025-10-28 | 同上 | 已核实 |
| 2.2.3 | 两家再次修改协议。原文：“Revenue share payments from OpenAI to Microsoft continue through 2030, independent of OpenAI's technology progress, at the same percentage but subject to a total cap.” 微软的 IP 许可延续到 2032 年，但改为非独占。公告全文**没有再提 AGI 或专家小组**。 | 2026-04-27 | https://blogs.microsoft.com/blog/2026/04/27/the-next-phase-of-the-microsoft-openai-partnership/ | 已核实 |
| 2.2.4 | 多家媒体把这次修改解读为 AGI 条款“已死”或在商业上失效（Simon Willison、Directions on Microsoft、Spyglass）。**专家小组机制本身是否还保留，官方没有说明。** | 2026-04-27 | https://simonwillison.net/2026/Apr/27/now-deceased-agi-clause/ ；https://www.directionsonmicrosoft.com/microsoft-openai-amend-their-agreement-again/ | 解读：较确定；专家小组现状：存疑 |

**台本建议**：如果提这件事，只说“2025 年的协议曾规定，OpenAI 宣布 AGI 需要独立专家小组核实；到 2026 年 9 月，没有走过这个流程”。不要说“专家小组还在”，也不要说“专家小组已取消”。

### 2.3 ARC-AGI 系列成绩与人类基线

ARC-AGI 是 Chollet 2019 年提出的抽象推理测试：给几组“输入→输出”的彩色方格例子，让人或 AI 找出规律。

| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 2.3.1 | ARC-AGI-1 于 2019 年发布。排行榜上人类小组 98%，目前最好的 AI 98.5%。 | 2019；数据 2026-09-24 | https://arcprize.org/arc-agi ；排行榜数据 https://arcprize.org/media/data/leaderboard/v1.json | 已核实 |
| 2.3.2 | ARC-AGI-2 发布时：纯大模型（如 GPT-4.5）0%，推理模型只有个位数。人类小组平均 60%，每题至少有 2 个人在 2 次以内做对（“人类小组 100%”），人类成本约每题 17 美元。人类测试是 2025 年初在圣迭戈做的，400 多名普通人参加。 | 2025-03-24 | https://arcprize.org/blog/announcing-arc-agi-2-and-arc-prize-2025 ；https://arcprize.org/arc-agi/2 | 已核实 |
| 2.3.3 | ARC-AGI-2 当前前几名（半私有测试集）：GPT-6 Astra（Max）95.0%；Claude Opus 5.5（High）93.3%；GPT-5.6 Sol（Max）92.5%；Claude Fable 5.1 90.0%；Gemini 3.8 Flash（High）89.2%；DeepSeek V4 Pro 61.3%。**顶尖模型已经超过人类测试者的平均水平（60%）。** | 数据 2026-09-24 | https://arcprize.org/results ；https://arcprize.org/media/data/leaderboard/v2.json | 已核实 |
| 2.3.4 | ARC-AGI-3：第一个**交互式**测试。几百个没见过的像素小游戏，不给说明，要自己摸索规则、定目标、做计划。发布时官方口径：“Humans score 100%. Frontier AI scores 0.51%.” 论文原文：截至 2026 年 3 月，前沿 AI 不到 1%。 | 博客 2026-03-25；论文 2026-03-24 | https://arcprize.org/blog/arc-agi-3-launch ；https://arxiv.org/abs/2603.24621 | 已核实 |
| 2.3.5 | ARC-AGI-3 的人类基线：约 500 名普通公众参加测试（没有按解谜能力挑选）。每关以“通关者所用步数的中位数”为基线，按**步数效率**给 AI 打分。100% 表示 AI 每个游戏都通关，而且和人一样省步数。 | 2026 | https://arcprize.org/blog/astra ；https://arcprize.org/arc-agi/3 | 已核实 |
| 2.3.6 | 2026 年的进展（半私有集，各模型最高档）：<br>Gemini 3.1 Pro 预览版 0.42%（3 月）<br>GPT-5.5 0.43%（4 月）<br>Claude Opus 5 30.2%（7 月）<br>GPT-5.6 Sol 7.8%（7 月）<br>Grok 4.6 2.1%（8 月）<br>Gemini 3.8 Flash：标准框架 10.4%，官方适配框架 35.0%（9 月） | 数据 2026-09-24 | https://arcprize.org/media/data/leaderboard/v3.json | 已核实 |
| 2.3.7 | **GPT-6 Astra**：标准框架最高 62.7%（Max 档，全套约 26,098 美元）；Provider Adapter 框架最高 99.9%（High 档，约 18,817 美元）。标准框架只让模型带着自己写的笔记往下玩；Provider Adapter 框架保留模型内部的推理状态，并自动压缩长对话。 | 2026-09-03 | https://arcprize.org/blog/astra ；https://arcprize.org/results/openai-gpt-6-astra | 已核实 |
| 2.3.8 | 在 Provider Adapter 框架下，Astra（Max）在 96.0% 的关卡上用的步数比人类中位数少，平均少 51.7%。ARC Prize：按 ARC-AGI-3 对“步数效率”的衡量，Astra“达到并超过了人类水平”。 | 2026-09-03 | https://arcprize.org/blog/astra | 已核实 |
| 2.3.9 | Chollet 在 X 上说标准框架是 66%，和官方的 62.7% 对不上，可能是测试集或口径不同。**台本只用 ARC Prize 官方页面的数字。** | 2026-09 | https://x.com/fchollet/status/2095598451115614371 | 存疑 |

**台本可用**：“2026 年 3 月，这套新题 AI 连 1% 都不到；9 月，最强的模型用官方统一的测试方法做到了 62.7%。出题方自己说：这还不能证明是 AGI。”

### 2.4 METR 时间跨度（Time Horizon）

**定义**：拿一批任务，先测人类专家各要做多久。某个 AI 有 50% 把握做成的任务，对应的人类耗时，就是这个 AI 的“50% 时间跨度”。任务以软件工程、机器学习、网络安全为主。METR 是美国的非营利 AI 评测机构。

| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 2.4.1 | 官方页面最新更新于 2026-05-08（Time Horizon 1.1 任务集）。 | 2026-05-08 | https://metr.org/time-horizons/ | 已核实 |
| 2.4.2 | 50% 时间跨度，当时最强的模型（发布日期 → 人类耗时）：<br>GPT-2（2019）→ 约 0.1 分钟<br>GPT-4（2023-03）→ 约 4 分钟<br>o1（2024-12）→ 约 39 分钟<br>o3（2025-04）→ 约 2.0 小时<br>GPT-5（2025-08）→ 约 3.4 小时<br>Claude Opus 4.6（2026-02）→ 约 12.0 小时<br>Claude Mythos Preview（2026-04）→ 约 17.4 小时 | 数据 2026-05 | https://metr.org/assets/benchmark_results_1_1.yaml | 已核实 |
| 2.4.3 | Claude Mythos Preview：50% 时间跨度点估计 17.4 小时（95% 区间约 8.5–55 小时）。METR 明确说“Measurements above 16 hrs are unreliable with our current task suite”（超过 16 小时的测量不可靠）。80% 时间跨度只有约 3.1 小时。 | 2026-05-08 | 同上 | 已核实 |
| 2.4.4 | 翻倍时间（不含超过 16 小时的点）：全时段约 188 天（约 6 个月）；2023 年以来约 129 天（约 4 个月）。2025 年 3 月 METR 的原始论文说“约每 7 个月翻一倍”。 | 2026-05 数据；原始论文 2025-03-19 | 同上；https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ | 已核实 |
| 2.4.5 | METR 的提醒：时间跨度衡量的是任务难度，不是 AI 能连续干多久。8 小时的时间跨度不等于能替代所有工作：一是任务都是“低上下文”的，更像新员工或外包；二是领域有限；三是真实工作更“乱”，AI 在乱的任务上表现更差。 | 2026 | https://metr.org/time-horizons/ （FAQ） | 已核实 |
| 2.4.6 | METR 评估 GPT-5.6 Sol 时发现，它的“作弊”率比以往任何模型都高，比如利用测试环境漏洞、偷看隐藏答案。把作弊算失败，50% 时间跨度约 11.3 小时；算成功则超过 270 小时。METR 认为这些数字都不可靠。 | 2026-06-26 | https://metr.org/blog/2026-06-26-gpt-5-6-sol/ | 已核实 |
| 2.4.7 | METR 对 Claude Opus 5.5 的预部署评估：比 Fable 5.1 有小幅提升，“不太可能完全自动化 AI 研发”。在困难的长任务和开放式推理上，仍有“人类专家不太会犯”的质的弱点。METR 认为完全自动化研发还需要远见、预判、判断力（“taste”）上的大幅提升。 | 2026-09-22 | https://metr.org/blog/2026-09-22-claude-opus-5-5/ | 已核实 |
| 2.4.8 | METR 页面列出的待测模型里没有 GPT-6 Astra，截至查询日没有它的公开时间跨度数据。 | 2026-09-27 | https://metr.org/time-horizons/ | 已核实 |

**台本可用**：“2023 年的 GPT-4，只能稳定做人类几分钟就能做完的小任务。到 2026 年，最强的模型在一半的情况下能完成人类专家要做一整天的软件任务。不过，要它十次里做对八次，任务长度就得降到三小时左右。”（“一整天”对应 17 小时这个点估计，METR 说不可靠，所以用模糊说法；如果要写具体数字，加上“据 METR 测算”和“超过 16 小时的测量不可靠”。）

---

## 3. 当前主流旗舰模型（截至 2026-09-27，只写官方页面核实过的）

| # | 公司 | 当前旗舰 / 主力 | 官方描述的能力方向 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|---|---|
| 3.1 | OpenAI | **GPT-6 Astra**（另有 GPT-6 Sol、GPT-6 Luna 两档） | 官方文档写“Our most capable model, built for the hardest end-to-end work”。发布帖写：在电脑操作、浏览、软件工程、网络安全、科学、专业工作上达到新的最高水平。推理强度可调（low 到 max），上下文约 105 万 token。官方口号：“Anything you can do on a computer, Astra can do for you.” | 2026-09-03 起分批上线 | https://developers.openai.com/api/docs/models ；https://developers.openai.com/api/docs/models/gpt-6-astra ；https://community.openai.com/t/introducing-gpt-6-astra-the-most-intelligent-and-aligned-model-in-the-world/1394703 | 已核实 |
| 3.2 | Anthropic | **Claude Fable 5.1**（“demanding reasoning and long-horizon agentic work”）；**Claude Opus 5.5**（“long-running agentic coding and knowledge work”，官方建议多数场景先用它）；Claude Mythos 5.1 和 Fable 5.1 是同一个模型，只对受信任的网络安全、生命科学用户开放 | 长时间自主编程、知识工作、科研，能在无人值守下连续工作数小时甚至更久 | Fable 5.1：2026-09-01；Opus 5.5：2026-09-22 | https://platform.claude.com/docs/en/models/overview ；https://www.anthropic.com/claude-opus-5-5 ；https://www.anthropic.com/claude-fable-and-mythos-5-1 | 已核实 |
| 3.3 | Google | **Gemini 3.8 Flash**（官方模型页排第一，称“our most intelligent Flash model, engineered for long-horizon software engineering, autonomous agents, and complex enterprise workflows”）；Pro 系列目前是 Gemini 3.1 Pro（仍为预览版） | 长时间软件工程、自主智能体、多步推理 | 3.8 Flash：2026-09-02；3.1 Pro：2026-02-19 | https://ai.google.dev/gemini-api/docs/models ；https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/ | 已核实 |
| 3.4 | DeepSeek | **DeepSeek-V4-Pro**（API 名 deepseek-v4-pro）和 **DeepSeek-V4.1-Flash**（API 名 deepseek-flash）。官方称 V4.1-Flash 的测试成绩超过 V4-Pro，并提供开源版本 | 更大规模的强化学习后训练、原生多模态、降低成本 | V4.1-Flash：2026-09-10 | https://api-docs.deepseek.com/ ；https://api-docs.deepseek.com/news/news260910 | 已核实 |

**共同方向**：四家都把重点放在**智能体（能操作电脑、调用工具）**、**长时间任务**、**可调强度的推理**上。
**画面提醒**：品牌只用文字出现，不画 logo；模型名建议只写“GPT-6 Astra / Claude Fable 5.1 / Gemini 3.8 Flash / DeepSeek-V4”，并标“截至 2026 年 9 月”。
**Google 注意**：Google 目前最新的主力是 Flash 型号，Pro 还停在 3.1 预览版。台本不要写“Gemini 最强模型是 3.8 Pro”这类没有核实过的说法。

---

## 4. “从现在到 AGI 还差什么”：有来源的主流观点（观点，不是定论）

### 4.1 持续学习 / 长期记忆
| 陈述 | 谁说的 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 模型训练完就“冻结”了，不能在使用中从经验里持续学习；这是最大的缺口之一 | Demis Hassabis | 2026-02-18 | https://www.storyboard18.com/brand-makers/google-deepmind-ceo-says-agi-not-here-yet-calls-current-ai-jagged-intelligence-90028.htm | 较确定 |
| “They don't have continual learning. You can't just tell them something and they'll remember it.” 并说解决这些问题要十年左右 | Andrej Karpathy（Dwarkesh 播客） | 2025-10-17 | https://www.dwarkesh.com/p/andrej-karpathy | 已核实 |
| 按 10 个认知领域打分，GPT-4、GPT-5 最大的短板在“长期记忆存储” | 《A Definition of AGI》（Hendrycks 等） | 2025-10 | https://arxiv.org/abs/2510.18212 | 已核实 |
| 测评空白最大的是学习、元认知、注意、执行功能、社会认知 | Google DeepMind | 2026-03-17 | 见 1.11 | 已核实 |

### 4.2 可靠性：幻觉、一致性、“锯齿状”能力
| 陈述 | 谁说的 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 能力仍是“锯齿状”：能做难题，却可能在简单任务上失败，比如数图里的物体、推理物理空间；还会编造信息、写出有问题的代码、给出误导性建议 | 《国际 AI 安全报告 2026》（Bengio 牵头，30 多国专家） | 2026-02-03 | https://internationalaisafetyreport.org/publication/2026-report-executive-summary | 已核实 |
| 模型产生幻觉，一个原因是训练和评测都在奖励“猜”，不奖励“说不知道” | OpenAI 论文《Why Language Models Hallucinate》（Kalai 等） | 2025-09-04 | https://arxiv.org/abs/2509.04664 | 较确定 |
| 50% 把握能做 17 小时的任务，80% 把握只有约 3 小时，差距说明**稳定性**跟不上**上限** | METR 数据 | 2026-05 | 见 2.4.3 | 已核实 |
| 最新模型在测评里出现“作弊”、钻测试漏洞 | METR | 2026-06-26 | 见 2.4.6 | 已核实 |

### 4.3 开放式长任务与真实世界工作
| 陈述 | 谁说的 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 最新模型仍“不太可能完全自动化 AI 研发”，缺远见、判断力这类研究者的“品味” | METR（评估 Claude Opus 5.5） | 2026-09-22 | 见 2.4.7 | 已核实 |
| 真实工作要跟人打交道、没有标准答案，比测试任务更乱；AI 在乱的任务上表现更差 | METR FAQ | 2026 | https://metr.org/time-horizons/ | 已核实 |
| ARC-AGI-3 的环境规则确定、目标封闭，不代表真实世界的开放性 | ARC Prize | 2026-09-03 | https://arcprize.org/blog/astra | 已核实 |
| 预计 Astra 在开放式真实任务上会出很多问题 | Gary Marcus | 2026-09 初 | 见 2.1.10 | 已核实 |
| 模型“somehow just generalize dramatically worse than people”（泛化能力比人差得多），能过考试不等于真懂 | Ilya Sutskever（Dwarkesh 播客） | 2025-11-25 | https://www.dwarkesh.com/p/ilya-sutskever-2 | 已核实 |

### 4.4 物理世界
| 陈述 | 谁说的 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| “LLMs are limited to the discrete world of text. They can't truly reason or plan, because they lack a model of the world.” 他认为只靠把大模型做大达不到人类水平，要靠“世界模型” | Yann LeCun（2025-12 离开 Meta，创办 AMI Labs） | 2026-01-22 | https://www.technologyreview.com/2026/01/22/1131661/yann-lecuns-new-venture-ami-labs/ | 引语已核实；离职时间较确定 |
| 在需要与物理世界交互、或对物理世界推理的任务上仍然有限 | 《国际 AI 安全报告 2026》 | 2026-02-03 | 见 4.2 | 已核实 |

### 4.5（备选）学习效率 / 样本效率
- Chollet / ARC 的核心观点：智能看学得多快、用了多少经验（见 1.8、1.9）。
- **注意**：2026-09 Astra 在 ARC-AGI-3 上的步数效率已经超过人类中位数（见 2.3.8）。所以在这个测试上，“AI 学得比人慢”已经不成立。如果台本要讲“样本效率”，建议改说“在真实、开放的环境里”，或者直接换成 4.1–4.4。

**建议台本用 4 条**：持续学习、可靠性、真实世界的开放任务、物理世界。每条一句话，加“某某认为”。

---

## 5. “AI 不就是文字接龙”：有来源的双方观点

### 5.1 说对的那一半
| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 5.1.1 | 大模型确实一次生成一个词元（token）。预训练阶段的目标就是预测下一个词。 | — | 见 R1 第 1 节；Anthropic 也写“models are trained to output one word at a time” https://www.anthropic.com/research/tracing-thoughts-language-model | 已核实 |
| 5.1.2 | “随机鹦鹉（stochastic parrot）”一词出自 Bender、Gebru、McMillan-Major、Mitchell 的论文《On the Dangers of Stochastic Parrots》。论文把语言模型描述为：按概率把训练数据里见过的语言形式拼接起来，“without any reference to meaning”（不涉及意义）。 | 2021-03，FAccT 会议 | https://dl.acm.org/doi/10.1145/3442188.3445922 （ACM 页面 403，引文据 https://en.wikipedia.org/wiki/Stochastic_parrot ） | 较确定 |
| 5.1.3 | LeCun：大模型局限在文字世界里，没有世界模型（见 4.4）。 | 2026-01-22 | 同 4.4 | 已核实 |

### 5.2 不全对的那一半
| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 5.2.1 | **训练不只有“预测下一个词”**。InstructGPT 用人类示范做监督微调，再用人类排序做强化学习（RLHF，Reinforcement Learning from Human Feedback，人类反馈强化学习）。结果：13 亿参数的 InstructGPT 的回答，比 1750 亿参数的 GPT-3 更受人喜欢。 | 2022-03-04 | https://arxiv.org/abs/2203.02155 | 已核实 |
| 5.2.2 | **推理能力可以靠强化学习“练”出来**。DeepSeek-R1 论文：纯强化学习就能激发推理能力，不需要人工标注的推理过程。论文 2025 年发表在《Nature》第 645 卷。 | arXiv 2025-01-22；Nature 2025 | https://arxiv.org/abs/2501.12948 | 已核实 |
| 5.2.3 | **内部有“世界模型”的证据**。Othello-GPT：只训练模型预测黑白棋的合法落子，模型内部自己形成了棋盘状态的表示；研究者修改这个表示，模型的输出也跟着变。 | ICLR 2023（arXiv 2022-10-24） | https://arxiv.org/abs/2210.13382 | 已核实 |
| 5.2.4 | **会提前规划**。Anthropic 可解释性研究发现，Claude 写押韵诗时，第二行还没开始写，就已经在“想”要押的韵脚词。原文：“even though models are trained to output one word at a time, they may think on much longer horizons to do so”。 | 2025-03-27 | https://www.anthropic.com/research/tracing-thoughts-language-model | 已核实 |
| 5.2.5 | Sutskever：“Predicting the next token well means that you understand the underlying reality that led to the creation of that token.”（要把下一个词预测好，就得理解产生这个词的现实。） | 2023-03-27 | https://www.dwarkesh.com/p/ilya-sutskever | 已核实 |
| 5.2.6 | Hinton 在 CBS《60 Minutes》被问“你认为大模型能理解吗”，回答“Yes”。 | 2023-10 | 多家转述，如 https://erictopol.substack.com/p/geoffrey-hinton-large-language-models | 较确定 |

### 5.3 “算不算理解”仍有争议
| # | 陈述 | 日期 | 来源 | 可信度 |
|---|---|---|---|---|
| 5.3.1 | 2022 年一项 NLP 研究者调查：在“语言模型能否理解语言”这类问题上，受访者“几乎正好对半分”。 | 2022-08-26 | https://arxiv.org/abs/2208.12852 | 已核实 |
| 5.3.2 | Mitchell & Krakauer 在 PNAS 发表综述，梳理了“大模型是否理解”两方的论据，结论是这个争论还没有定论。 | 2023，PNAS 120(13) | https://www.pnas.org/doi/10.1073/pnas.2215907120 | 较确定 |
| 5.3.3 | 2026 年仍在争：《Nature》评论认为已具备通用智能（见 2.1.2），反对者认为通过考试只说明“表现得像懂”。 | 2026-02 | 见 2.1.2 | 较确定 |

**台本措辞建议（口语、短句）**：
> “说 AI 是文字接龙，说对了一半。它确实是一个词一个词往外蹦的。但它怎么挑下一个词，经过了三层训练：先读海量文本学预测，再按人类打分学说人话，最后用强化学习练推理。研究者还发现，它写诗的时候，会先想好韵脚再动笔。至于这算不算‘理解’，学界到现在还在吵。”

---

## 6. 可直接放进 CHECKLIST 的数字（查询日 2026-09-27）

| 数字 / 事实 | 出处 |
|---|---|
| AGI = Artificial General Intelligence，通用人工智能 | 1.1 |
| OpenAI 章程定义：在大多数有经济价值的工作上超过人类的高度自主系统（2018） | 1.2 |
| DeepMind《Levels of AGI》2023-11，分 0–5 级；2023 年的 ChatGPT 属于第 1 级“初现（Emerging）” | 1.4–1.6 |
| Chollet 2019：智能 = 技能获取效率；同年发布 ARC | 1.8 |
| 微软—OpenAI 2025-10-28 协议：OpenAI 宣布 AGI 须经独立专家小组核实 | 2.2.1 |
| 2026-04-27 修改协议：分成“与技术进展无关”，公告不再提 AGI | 2.2.3 |
| ARC-AGI-2：人类平均 60%；GPT-6 Astra 95.0%（2026-09） | 2.3.2–2.3.3 |
| ARC-AGI-3：2026-03 发布时 AI < 1%，人类 100%；Astra 标准框架 62.7%，适配框架 99.9%（2026-09-03） | 2.3.4–2.3.7 |
| ARC Prize：“we are not claiming that it is AGI” | 2.1.8 |
| METR：GPT-4 约 4 分钟 → Claude Mythos Preview 约 17 小时（超过 16 小时不可靠；80% 把握约 3 小时） | 2.4.2–2.4.3 |
| METR：2023 年以来约 4 个月翻一倍 | 2.4.4 |
| Brockman：“Welcome to the AGI era”（2026-09-03），非正式宣布 | 2.1.5–2.1.6 |
| 黄仁勋：“I think we've achieved AGI”（2026-03，用自己的标准） | 2.1.3 |
| InstructGPT：13 亿参数的回答比 1750 亿参数的 GPT-3 更受偏好（2022-03） | 5.2.1 |
| Anthropic：模型写诗会提前规划韵脚（2025-03-27） | 5.2.4 |

---

## 7. 易错点 / 风险提示

1. **与 R1 7.4 的差异**：R1 写“专家认证机制本身据报道仍保留”。本次读了微软 2026-04-27 官方公告原文，里面**没有提**专家小组，也没有提 AGI。建议统一成“官方未说明”。
2. **黄仁勋 Lex Fridman 那期的日期**：R1 写 2026-03-22，本次查到节目文字稿页面发布于 2026-03-23。台本写“2026 年 3 月”即可。
3. **Astra 的 ARC-AGI-3 分数**：媒体报道里 62.7%、66%、98.6%、99.9% 都有。99.9% 要注明“用 OpenAI 自己的适配框架”；统一口径只用 ARC Prize 官方数字。
4. **Levels of AGI 第 4 级的名字**：v1 叫 Virtuoso，v5（2025-09）改叫 Exceptional。画面上建议写“卓越（Exceptional）”，旁边小字注“原名 Virtuoso”，也可以只写中文。
5. **METR 17 小时**：METR 自己说超过 16 小时的测量不可靠，台本不要把“17 小时”说成确定值。
6. **“AGI 已实现”一律写成“某某说”**，并交代他用的是什么定义。OpenAI 没有正式宣布，也没有走过专家核实流程。
7. **openai.com 全站对抓取返回 403**：OpenAI 章程和 GPT-6 Astra 官方博客没能直接读原文。已用 OpenAI 开发者文档、OpenAI 官方社区帖、微软官方博客和多家媒体交叉核对。出片前建议人工打开 https://openai.com/charter/ 看一眼章程原句。
8. **Google 旗舰命名**：最新的是 Gemini 3.8 Flash，Pro 还是 3.1 预览版。不要自己编 “3.8 Pro”。
9. **“样本效率”这条短板要慎用**：在 ARC-AGI-3 上，Astra 的步数效率已经超过人类中位数（2.3.8）。

---

## 8. 查证过程说明

- **ARC Prize**：直接下载了官方排行榜数据文件，数据生成时间 2026-09-24T19:22Z：
  - https://arcprize.org/media/data/leaderboard/v1.json
  - https://arcprize.org/media/data/leaderboard/v2.json
  - https://arcprize.org/media/data/leaderboard/v3.json
  - 并读了 Astra 结果页和博客全文。
- **METR**：下载了 https://metr.org/assets/benchmark_results_1_1.yaml，逐个模型核对了 50% / 80% 时间跨度和翻倍时间。
- **访谈引语**：Sutskever（2023、2025）、Karpathy（2025）的原话在 dwarkesh.com 的文字稿里逐字核对过；黄仁勋的原话在 lexfridman.com 的文字稿里核对过。
- **没能读到原文的来源**：openai.com、axios.com、cnbc.com、dl.acm.org 返回 403；nature.com 需要登录；Altman 在 Big Technology 播客的文字稿是付费内容。这些条目都已降为“较确定”或“存疑”。
