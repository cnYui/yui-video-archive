# 第 2 期查证 R1：AI 从“会说人话”到今天的技术演进

- 用途：《原LAI如此》第 2 期台本「你的一句话就否定了 AI 一路的努力——AI 是怎么从学会说人话到实现 AGI 的？」的事实底稿
- 查询日期：2026-09-27（所有 URL 均为本次查询）
- 可信度标注：
  - **已核实**：本次打开了一手来源（论文 / 官方博客 / 官方文档 / 官方数据页），原文对得上
  - **较确定**：一手页面打不开（openai.com 对抓取返回 403），用同日可靠报道、搜索引擎给出的官方页面摘要或多个独立来源交叉确认
  - **存疑**：只有二手转述，或多个来源数字不一致

---

## 0. 给台本的一页结论

1. **“AI 就是文字接龙”说对了一半。** 对的一半是：预训练目标就是“根据前文预测下一个 token（词元）”，生成时也是一个 token 一个 token 往外吐。错的一半有三点：
   - 为了把下一个词猜准，模型得学会语法、事实和任务本身（GPT-2 论文原话的意思）；
   - 2022 年起，模型还要经过指令微调和 RLHF，训练目标变成“人更喜欢哪个回答”，不再只是“哪个词最常见”；
   - 2024 年起的推理模型，用“答案对不对”做强化学习的奖励，训练目标是做对题。
   另有可解释性研究发现，Claude 写押韵诗时会提前想好行尾的韵脚（Anthropic，2025-03-27）。
2. **“四个台阶”基本成立，但时间上有重叠，不能说成一个接一个。** 用“哪一年成为主流”来划分最稳妥：
   - 会说人话：2018–2020 预训练 + 放大规模（GPT-1 → GPT-3）
   - 会聊天：2022 指令微调 + RLHF（InstructGPT 1 月，ChatGPT 11 月 30 日）
   - 会思考：2024–2025 用强化学习训练长思维链（o1 2024-09-12，DeepSeek-R1 2025-01-20）
   - 会做事：2023 起工具调用，2024–2026 智能体（function calling 2023-06-13、computer use 2024-10-22、MCP 2024-11-25、Claude Code / Codex 2025）
   重叠的地方：工具调用（2023）比 o1（2024）早；思维链提示（2022-01）比 ChatGPT 早。
3. **AGI 现状（截至 2026-09-27）：没有公认已实现。**
   - 2026-09-03 OpenAI 发布 GPT-6 Astra，总裁 Greg Brockman 说“我个人认为我们到了”，同时承认“每个人的 AGI 定义都不同”。这是个人表态，不是公司正式宣布，也没有经过 2025 年 10 月约定的独立专家小组认证。
   - 负责 ARC-AGI-3 基准的 ARC Prize 明说“我们不认为它是 AGI”。
   - 此前英伟达 CEO 黄仁勋（2026-03）也说过“已经实现 AGI”，同样有争议。
4. **最常见的误传：** 把 ChatGPT 当成第一个大模型或第一个聊天机器人；以为 Transformer 是 OpenAI 发明的；以为 GPT-4 参数量是官方公布的；以为 METR 的“12 小时”是 AI 能连续工作 12 小时。详见第 9 节。

---

## 1. “预测下一个词”到底是什么

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 1.1 | **语言模型（Language Model）** 就是给一段文字算概率：把整句的概率拆成“每个符号在前文条件下出现的概率”的连乘，即 p(x)=∏p(sₙ\|s₁…sₙ₋₁)。GPT-2 论文第 2 节原文就这么写。 | 2019-02 | https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf | 已核实 |
| 1.2 | 用“猜下一个字母”研究语言，最早可追溯到香农 1951 年的论文《Prediction and Entropy of Printed English》：让人看前文、猜下一个字母，估算英文的信息量。“文字接龙”的思路有七十多年历史。 | 1951-01（Bell System Technical Journal 30 卷） | https://onlinelibrary.wiley.com/doi/abs/10.1002/j.1538-7305.1951.tb01366.x ；https://archive.org/details/bstj30-1-50 | 较确定 |
| 1.3 | 用神经网络做语言模型，代表作是 Bengio 等人 2003 年的《A Neural Probabilistic Language Model》，比 n-gram 统计方法好，还能利用更长的上下文。 | 2003（JMLR 第 3 卷） | https://dl.acm.org/doi/10.5555/944919.944966 | 较确定 |
| 1.4 | **token（词元）**：模型读写文字的最小单位。它可以是一个字符、一个词，也可以是半个词，空格和标点也算。OpenAI 帮助中心给的英文经验值：1 token ≈ 4 个字符 ≈ 0.75 个英文单词。中文没有官方统一换算，看分词器。 | 长期有效 | https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them | 较确定（页面经搜索摘要确认） |
| 1.5 | GPT 系列用 **BPE（Byte Pair Encoding，字节对编码）** 切 token：常见字符串合成一个 token，罕见的拆开。GPT-2 词表 50,257 个 token，上下文长度 1024 个 token。 | 2019-02 | GPT-2 论文 §2.2、§2.3（同上 PDF） | 已核实 |
| 1.6 | **预训练目标**：GPT-1 论文写明第一阶段用“标准语言模型目标”，最大化 Σ log P(uᵢ \| uᵢ₋ₖ…uᵢ₋₁)，也就是根据前 k 个 token 预测下一个。 | 2018-06 | https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf （§3.1） | 已核实 |
| 1.7 | GPT-2 官方原话：训练目标很简单，就是“给定前面所有的词，预测下一个词”（predict the next word, given all of the previous words within some text）。 | 2019-02-14 | https://openai.com/index/better-language-models/ | 较确定（openai.com 403，搜索摘要与维基一致） |
| 1.8 | GPT-4 技术报告也写明：GPT-4 是“预训练来预测下一个 token”的 Transformer 模型。到 GPT-4 为止，预训练这一步的目标没有变。 | 2023-03-15（arXiv v1） | https://arxiv.org/abs/2303.08774 | 已核实 |
| 1.9 | GPT-2 论文的推测：语言模型只要容量够大，为了**更好地预测**文本，会开始学会文本里演示的各种任务（翻译、问答等）。这是“预测下一个词”能学出能力的核心逻辑。 | 2019-02 | GPT-2 论文 §2 | 已核实 |
| 1.10 | Anthropic 可解释性研究：虽然模型被训练成一次输出一个词，但它可能在更长的范围上“想”；例如写押韵诗时，Claude 会提前想好要押的词，再写这一行去凑它。 | 2025-03-27 | https://www.anthropic.com/research/tracing-thoughts-language-model | 已核实 |

### 为什么说“文字接龙”说对了一半（可直接改写进台本）

- **对的一半**：预训练就是猜下一个 token（1.6、1.7、1.8）；生成时也是一个一个往外吐（1.1 的连乘公式）。
- **错的一半**：
  1. **猜准需要理解。** 要把下一个词猜准，就得先掌握语法、常识和任务（1.9）。GPT-3 不用改参数，给几个例子就能做新任务（见 2.6）。
  2. **训练目标后来变了。** 聊天模型还要经过指令微调和 RLHF，优化的是“人更喜欢哪个回答”（第 3 节）。推理模型用“答案对不对”当奖励（第 4 节）。只做过预训练的模型，才是纯粹的“接龙机器”。
  3. **一次输出一个词，不等于只看下一个词。** 可解释性研究看到了“提前计划”（1.10）。
- 台本措辞建议：“输出方式确实是接龙；但接得好，靠的是它从海量文本里学到的东西，而且后面的训练已经不只是接龙了。”避免说“AI 真的理解了”这种结论性说法，这一点学界仍有争论。

---

## 2. 里程碑：Transformer → GPT-1/2/3 → 缩放定律

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 2.1 | **Transformer** 出自论文《Attention Is All You Need》，8 位作者的工作都在 Google 完成（署名 Google Brain / Google Research；Gomez 署名多伦多大学，脚注写明工作在 Google Brain 期间完成）。论文最初解决的是**机器翻译**，特点是只用注意力机制，不再用循环网络和卷积。 | arXiv v1 2017-06-12；发表于 NIPS 2017 | https://arxiv.org/abs/1706.03762 ；https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf | 已核实 |
| 2.2 | **GPT-1**：OpenAI 论文《Improving Language Understanding by Generative Pre-Training》。做法是两步：先在大量文本上做无监督预训练，再针对具体任务用标注数据微调。12 层、只用解码器（decoder-only）的 Transformer，训练数据是 BooksCorpus（7000 多本未出版的书）。 | 2018-06-11 | 论文 PDF（见 1.6）；日期见 https://en.wikipedia.org/wiki/GPT-1 （引论文日期） | 做法已核实；日期较确定 |
| 2.3 | GPT-1 约 **1.17 亿（117M）参数**：GPT-2 论文表 2 写明最小的 117M 模型“等同于原版 GPT”。 | 2019-02 | GPT-2 论文 §3 | 已核实 |
| 2.4 | **GPT-2**：最大的模型 15 亿（1.5B，表中为 1542M）参数，48 层；训练数据 WebText，800 多万篇网页、约 40GB 文本。OpenAI 当时以担心被滥用为由分阶段发布，完整 1.5B 模型 2019-11-05 才放出。 | 公布 2019-02-14；完整发布 2019-11-05 | GPT-2 论文；https://en.wikipedia.org/wiki/GPT-2 | 规模已核实；日期较确定 |
| 2.5 | **GPT-3**：论文《Language Models are Few-Shot Learners》，**1750 亿（175B）参数**。 | arXiv v1 2020-05-28 | https://arxiv.org/abs/2005.14165 | 已核实 |
| 2.6 | **上下文学习（In-Context Learning，ICL）**：GPT-3 做所有任务都“不做任何梯度更新或微调”，任务说明和几个示例全写在输入文字里。也就是“看几个例子就会做”，参数不变。 | 2020-05-28 | 同上摘要 | 已核实 |
| 2.7 | GPT-3 通过 **OpenAI API** 以内测（private beta）形式开放给开发者，普通人还不能直接聊天。 | 2020-06-11 | https://techcrunch.com/2020/06/11/openai-makes-an-all-purpose-api-for-its-text-based-ai-capabilities/ | 较确定 |
| 2.8 | **缩放定律（Scaling Laws）· Kaplan 2020**：OpenAI 的 Kaplan 等人发现，模型的损失随**参数量、数据量、算力**呈幂律下降，趋势横跨七个多数量级。也就是“放大多少，大概能变好多少”可以提前算。 | arXiv v1 2020-01-23 | https://arxiv.org/abs/2001.08361 | 已核实 |
| 2.9 | **Chinchilla 2022**（DeepMind，Hoffmann 等）：在算力固定时，模型大小和训练数据量应**同比例增长**，模型翻倍，数据也要翻倍。70B 参数的 Chinchilla 与 280B 的 Gopher 用同样算力、4 倍数据，全面超过 Gopher、GPT-3（175B）等更大的模型。 | arXiv v1 2022-03-29 | https://arxiv.org/abs/2203.15556 | 已核实 |
| 2.10 | Chinchilla 训练了约 1.4 万亿 token，折合每个参数约 20 个 token，这个“20 倍”后来成了常用经验值。 | 2022 | https://proceedings.neurips.cc/paper_files/paper/2022/file/c1e2faff6f588870935f114ebe04a3e5-Paper-Conference.pdf | 较确定（“20 倍”是后人从论文数字算出的经验值，不是论文里的定理） |
| 2.11 | **BERT**（Google，2018-10-11 上 arXiv）同样是基于 Transformer 的预训练语言模型，比 ChatGPT 早 4 年。可用来反驳“ChatGPT 是第一个大模型”。 | 2018-10-11 | https://arxiv.org/abs/1810.04805 | 日期已核实；机构较确定 |

> 台本可用的规模对比（官方可核实的数字）：GPT-1 1.17 亿 → GPT-2 15 亿 → GPT-3 1750 亿，两年涨了约 1500 倍。**GPT-4 起 OpenAI 不公布参数量**（技术报告未披露），网上流传的“1.8 万亿”等数字都不是官方数据，不要上屏。

---

## 3. 从“会续写”到“会聊天”：指令微调、RLHF、ChatGPT

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 3.1 | **RLHF 的源头**：Christiano 等（OpenAI 与 DeepMind 合作）2017 年发表《Deep reinforcement learning from human preferences》：不写奖励函数，让人比较两段行为哪个更好，用这种偏好训练智能体。RLHF 比 ChatGPT 早 5 年。 | arXiv v1 2017-06-12 | https://arxiv.org/abs/1706.03741 | 已核实 |
| 3.2 | **指令微调（Instruction Tuning）**：Google 的 FLAN 论文把它定义为“在一批用自然语言指令描述的任务上微调语言模型”，137B 的 FLAN 零样本表现超过 GPT-3。 | arXiv v1 2021-09-03 | https://arxiv.org/abs/2109.01652 | 已核实 |
| 3.3 | **SFT（Supervised Fine-Tuning，监督微调）**：InstructGPT 的第一步。请标注员写出“理想回答”作为示范，用监督学习微调 GPT-3。 | 2022-03-04 | https://arxiv.org/abs/2203.02155 | 已核实 |
| 3.4 | **RLHF（Reinforcement Learning from Human Feedback，基于人类反馈的强化学习）**：InstructGPT 的第二步。让标注员给模型的多个回答排序，训练一个“奖励模型”，再用强化学习继续微调。 | 2022-03-04 | 同上 | 已核实 |
| 3.5 | **关键结论**：人类评估中，**13 亿（1.3B）参数的 InstructGPT 的回答比 1750 亿参数的 GPT-3 更受偏好**，参数少了 100 多倍。说明“会聊天”主要靠对齐训练，不只靠堆参数。 | 2022-03-04 | 同上摘要 | 已核实 |
| 3.6 | OpenAI 官方博客《Aligning language models to follow instructions》发布 InstructGPT，并把它设为 API 默认模型。 | 2022-01-27 | https://openai.com/index/instruction-following/ ；https://www.infoq.com/news/2022/02/openai-instructgpt/ | 较确定 |
| 3.7 | **ChatGPT 发布**：从 GPT-3.5 系列中的一个模型微调而来，用 RLHF 训练，方法与 InstructGPT 相同，只在数据收集上略有不同，改成对话形式。 | 2022-11-30 | https://openai.com/index/chatgpt/ | 较确定（openai.com 403；原句经搜索摘要与多家报道一致） |
| 3.8 | ChatGPT 上线 5 天用户破 100 万（Sam Altman 推文：“ChatGPT launched on wednesday. today it crossed 1 million users!”）。 | 2022-12-05 | https://x.com/sama/status/1599668808285028353 | 较确定 |
| 3.9 | **Constitutional AI（宪法 AI）**：Anthropic 论文《Constitutional AI: Harmlessness from AI Feedback》。人只提供一份原则清单（“宪法”），不再逐条人工标注有害内容；先让模型按原则自我批评、改写，再用模型的偏好判断训练奖励模型做强化学习，称为 **RLAIF（RL from AI Feedback，基于 AI 反馈的强化学习）**。 | arXiv v1 2022-12-15 | https://arxiv.org/abs/2212.08073 | 已核实 |

> 台本要点：“会聊天”这一步做了两件事。第一，**SFT**：给模型看人写的标准回答，照着学。第二，**RLHF**：人给回答排序，模型朝人更喜欢的方向改。代表：InstructGPT（2022 年 1 月），ChatGPT（2022 年 11 月 30 日）。

---

## 4. 从“会聊天”到“会思考”：思维链与推理模型

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 4.1 | **思维链提示（Chain-of-Thought Prompting）**：Google 的 Wei 等人发现，在提示里给几个“带中间推理步骤”的例子，大模型就会先写步骤再给答案。PaLM 540B 只用 8 个这样的例子，在 GSM8K 小学数学应用题上达到当时最好成绩。这种能力只在足够大的模型上出现。 | arXiv v1 2022-01-28 | https://arxiv.org/abs/2201.11903 | 已核实 |
| 4.2 | **零样本思维链**：Kojima 等发现，只在答案前加一句“Let's think step by step（让我们一步一步想）”，推理成绩就大幅提升（用 InstructGPT 做 MultiArith，从 17.7% 到 78.7%）。 | arXiv v1 2022-05-24 | https://arxiv.org/abs/2205.11916 | 已核实 |
| 4.3 | **OpenAI o1**（预览版 o1-preview）发布。官方说法：用大规模强化学习教模型“用思维链有效思考”，先想再答。 | 2024-09-12 | https://openai.com/index/learning-to-reason-with-llms/ ；https://simonwillison.net/2024/Sep/12/openai-o1/ | 较确定（openai.com 403） |
| 4.4 | o1 官方结论：性能随**更多强化学习（训练时算力）**和**更长的思考时间（推理时算力，test-time compute）**持续提升。这是“缩放”的第二条路：不只把模型做大，也让它想得更久。 | 2024-09-12 | 同上 | 较确定 |
| 4.5 | **DeepSeek-R1** 发布，开源权重，MIT 协议；官方称推理表现与 OpenAI o1 相当，并同时开源 6 个蒸馏小模型。 | 2025-01-20 | https://www.deepseek.com/en/news/deepseek-r1/ | 已核实 |
| 4.6 | DeepSeek-R1 技术报告（arXiv v1）。**R1-Zero**：直接在基座模型上做大规模强化学习，**不先做 SFT**。 | 2025-01-22 | https://arxiv.org/abs/2501.12948v1 | 已核实 |
| 4.7 | R1-Zero 的奖励是**规则判定**的：①准确性奖励，数学题看最终答案对不对，编程题用编译器跑测试用例；②格式奖励，要求把思考过程写在 `<think>` 标签里。论文说没用神经网络奖励模型，因为容易被模型“钻空子”（reward hacking）。 | 2025-01-22 | 论文 §2.2.2（同上 PDF） | 已核实 |
| 4.8 | R1-Zero 训练中，AIME 2024 数学竞赛题的平均一次通过率从 **15.6% 升到 71.0%**，接近 OpenAI o1-0912。 | 2025-01-22 | 论文 §2.2.4、表 2 | 已核实 |
| 4.9 | **R1-Zero 现象**：没人教，模型的回答自己越变越长（平均长度从几百涨到近万 token），还自发出现“反思”“换思路”等行为。论文展示了一个“顿悟时刻（aha moment）”：模型中途写出“Wait, wait. Wait. That's an aha moment I can flag here.”，然后回头重新检查。 | 2025-01-22 | 论文 §2.2.4、图 3、表 3 | 已核实 |
| 4.10 | R1-Zero 的缺点：可读性差、中英文混杂。所以正式版 **DeepSeek-R1** 先用几千条“冷启动”长思维链数据做 SFT，再做强化学习。“R1 完全没用 SFT”是误传，没用 SFT 的是 R1-Zero。 | 2025-01-22 | 论文 §2.2.4 末、§2.3.1 | 已核实 |
| 4.11 | DeepSeek-R1 论文经同行评审后发表于 **Nature**（645 卷 633–638 页），是首个经同行评审发表的主流开源权重大模型。 | 2025-09-17 | https://www.nature.com/articles/s41586-025-09422-z ；https://ui.adsabs.harvard.edu/abs/2025Natur.645..633G/abstract | 较确定（Nature 页面需登录跳转；arXiv 页注明期刊信息） |
| 4.12 | Nature 论文补充材料披露，R1 这一步的训练花费约 **29.4 万美元**（512 块 H800，约 80 小时），**不含**底座模型 DeepSeek-V3 的成本。常说的“550 多万美元”是 V3 最后一次正式训练的估算，也不含前期研究。 | 2025-09（Reuters 等报道） | https://www.cnn.com/2025/09/19/business/deepseek-ai-training-cost-china-intl ；https://the-decoder.com/deepseek-says-training-its-r1-model-cost-just-294000/ | 较确定 |
| 4.13 | **RLVR（Reinforcement Learning with Verifiable Rewards，可验证奖励的强化学习）** 这个名字出自 Ai2 的 Tülu 3 论文：用能自动判定对错的奖励（如数学答案、代码测试）做强化学习。 | arXiv v1 2024-11-22 | https://arxiv.org/abs/2411.15124 | 已核实（机构 Ai2 为较确定） |
| 4.14 | OpenAI **GPT-5** 发布：一个系统里同时有快速回答模型和深度推理模型（GPT-5 thinking），由实时路由器决定用哪个。“会思考”从单独产品变成默认能力。 | 2025-08-07 | https://openai.com/index/introducing-gpt-5/ | 较确定 |

> 台本要点：“会思考”分两段。
> - **2022 年：提示技巧。** 让模型“先写步骤再答”（思维链），模型本身没变。
> - **2024–2025 年：训练方法。** 用强化学习专门训练“想得久、想得对”，奖励看最终答案对不对（o1、DeepSeek-R1）。
> 反常识点：R1-Zero 没人教它反思，它在强化学习里自己学会了“等等，我再检查一下”。

---

## 5. 从“会思考”到“会做事”：工具、电脑操作、智能体

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 5.1 | **ReAct**（普林斯顿与 Google 的研究者）：让模型交替输出“推理”和“动作”，动作可以是查维基百科之类的外部接口。这是学术界“边想边做”的早期代表。 | arXiv v1 2022-10-06 | https://arxiv.org/abs/2210.03629 | 日期已核实；机构较确定 |
| 5.2 | **Toolformer**（Meta AI）：语言模型可以通过简单的 API 自学使用外部工具（计算器、搜索等）。 | arXiv v1 2023-02-09 | https://arxiv.org/abs/2302.04761 | 日期已核实；机构较确定 |
| 5.3 | **函数调用（Function Calling）**：OpenAI 在 API 中上线。开发者描述函数，gpt-4-0613 和 gpt-3.5-turbo-0613 会判断何时该调用，并输出符合函数签名的 JSON 参数。模型本身不执行函数，由开发者的程序执行后再把结果交回模型。 | 2023-06-13 | https://openai.com/index/function-calling-and-other-api-updates/ ；https://simonwillison.net/2023/Jun/13/function-calling/ | 较确定（openai.com 403，同日报道一致） |
| 5.4 | **Computer Use（电脑操作）**：Anthropic 随升级版 Claude 3.5 Sonnet 推出公测版，让模型“看屏幕、移动光标、点击按钮、输入文字”。官方当时明说它仍在实验阶段，有时笨拙、容易出错。 | 2024-10-22 | https://www.anthropic.com/news/3-5-models-and-computer-use | 已核实 |
| 5.5 | **MCP（Model Context Protocol，模型上下文协议）**：Anthropic 发布并开源。它是一个开放标准，用来把 AI 助手接到数据所在的系统（内容库、业务工具、开发环境）。 | 2024-11-25 | https://www.anthropic.com/news/model-context-protocol | 已核实 |
| 5.6 | **Claude Code** 以研究预览版发布（与 Claude 3.7 Sonnet 同日），这是一个在终端里运行的编程智能体，能读代码、改文件、跑测试、提交代码。 | 2025-02-24 | https://www.anthropic.com/news/claude-3-7-sonnet ；https://techcrunch.com/2025/02/24/anthropic-launches-a-new-ai-model-that-thinks-as-long-as-you-want/ | 较确定 |
| 5.7 | Claude Code **正式发布（GA）**，与 Claude Opus 4 / Sonnet 4 同日；官方称 Opus 4 能在长任务上“连续工作数小时”。 | 2025-05-22 | https://www.anthropic.com/news/claude-4 | 已核实 |
| 5.8 | **Codex CLI**：OpenAI 发布的开源终端编程智能体，与 o3、o4-mini 同日发布。 | 2025-04-16 | https://github.com/openai/codex ；https://en.wikipedia.org/wiki/Codex_CLI | 较确定 |
| 5.9 | **Codex**（云端软件工程智能体）研究预览：每个任务在独立的云端沙盒里跑，能写功能、修 bug、提交 PR 供审核，由基于 o3 的 codex-1 驱动。注意它和 2021 年的同名代码模型 Codex 是两回事。 | 2025-05-16 | https://openai.com/index/introducing-codex/ ；https://visualstudiomagazine.com/articles/2025/05/16/the-return-of-codex-ai-as-an-agent.aspx | 较确定 |
| 5.10 | **METR 任务时长研究**：论文《Measuring AI Ability to Complete Long Tasks》（后来的版本改名为 Measuring AI Ability to Complete Long **Software** Tasks）。指标叫“**50% 任务完成时间跨度**”：AI 能以 50% 成功率完成的任务，人类专家通常要做多久。 | arXiv v1 2025-03-18；博客 2025-03-19 | https://arxiv.org/abs/2503.14499 ；https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ | 已核实 |
| 5.11 | METR 原结论：从 2019 年起，前沿 AI 的这个时间跨度**约每 7 个月翻一倍**；当时的 Claude 3.7 Sonnet 约 **50 分钟**。最新版摘要（v4，2026-07-10）补充：“这一趋势可能在 2024 年加速了。” | 2025-03 / 2026-07 | https://arxiv.org/abs/2503.14499v4 | 已核实 |
| 5.12 | METR《Time Horizon 1.1》更新（任务从 170 个增加到 228 个）：2019–2025 整体仍是约 196 天（7 个月）翻倍；**2024 年以来约 89 天翻倍**（约 3 个月）。Claude Opus 4.5 约 **320 分钟**（置信区间 170–729 分钟），GPT-5 约 214 分钟。 | 2026-01-29 | https://metr.org/blog/2026-1-29-time-horizon-1-1/ | 已核实 |
| 5.13 | METR 估计 Claude Opus 4.6 约 **14.5 小时**（95% 置信区间 6–98 小时），并说明测量噪声极大，因为任务集快被做满了。 | 2026-02（METR 推文） | https://x.com/METR_Evals/status/2024923422867030027 | 较确定 |
| 5.14 | METR 对 Claude Mythos Preview 早期版本的估计是“**至少 16 小时**”（95% 置信区间 8.5–55 小时）；METR 数据页注明“16 小时以上的测量在现有任务集上不可靠”。 | 数据页更新于 2026-05-08 | https://metr.org/time-horizons/ ；https://x.com/METR_Evals/status/2052896621760004602 | “16 小时以上不可靠”已核实；具体数值较确定 |
| 5.15 | **读 METR 图的三点注意**（METR 数据页 + MIT Technology Review 2026-02-05 文章）：①纵轴是“人类完成这个任务要多久”，**不是 AI 能连续工作多久**；②任务主要是软件工程、机器学习、网络安全，**不代表所有工作**；③是 50% 成功率，不是“稳定做到”。METR 也明说这不代表 AI 能自动化大多数真实工作。 | 2026 | https://metr.org/time-horizons/ ；https://www.technologyreview.com/2026/02/05/1132254/this-is-the-most-misunderstood-graph-in-ai/ | 已核实 |
| 5.16 | 截至 2026 年 9 月最新的“会做事”案例：OpenAI 于 2026-09-03 发布 GPT-6 Astra，主打能直接操作浏览器、电子表格和桌面软件（computer use）。 | 2026-09-03 | https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/ | 较确定 |

> 台本要点：“会做事”靠三样东西。
> 1. **工具调用**：模型输出“要调用哪个函数、参数是什么”，程序去执行（2023-06）。
> 2. **操作电脑**：看截图、点鼠标、打字（2024-10）。
> 3. **标准接口**：MCP 让工具接入有统一格式（2024-11）。
> 把这些串起来，再加上能长时间推理的模型，就是“智能体（Agent）”，例如编程智能体（2025）。
> 能上屏的量化数据：METR 的“50% 任务时间跨度”，2019 年以来约 7 个月翻倍，2024 年以来更快（约 3 个月）。必须同时说明这是软件类任务、50% 成功率、测的是人类耗时。

---

## 6. 多模态（一句话即可）

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 6.1 | GPT-4 是一个“大规模多模态模型”，可以接收**图像和文字输入**，输出文字；技术报告**没有公布参数量和架构细节**。 | 发布 2023-03-14；arXiv v1 2023-03-15 | https://arxiv.org/abs/2303.08774 ；https://techcrunch.com/2023/03/14/openai-releases-gpt-4-ai-that-it-claims-is-state-of-the-art/ | 已核实 |

建议：多模态不单独成台阶，一句话带过即可，比如“2023 年起，模型还能看图”。它和“说人话 → 聊天 → 思考 → 做事”这条主线关系不大，展开会超时长。

---

## 7. AGI 现状（截至 2026-09-27）

> 这部分可能由别的查证任务细查。这里只列与“结尾落点”直接相关、本次已查到的事实，方便台本结尾措辞。

| # | 陈述 | 时间 | 来源 | 可信度 |
|---|---|---|---|---|
| 7.1 | **AGI（Artificial General Intelligence，通用人工智能）没有统一定义。** OpenAI 章程的定义是“在大多数具有经济价值的工作上超过人类的高度自主系统”。 | 章程 2018 起 | https://simonwillison.net/2026/Apr/27/now-deceased-agi-clause/ （引 OpenAI 章程） | 较确定 |
| 7.2 | Google DeepMind 的 Morris、Legg 等人提出“AGI 分级”，按**深度（表现水平）**和**广度（通用性）**两个维度划分等级。 | arXiv v1 2023-11-04 | https://arxiv.org/abs/2311.02462 | 已核实 |
| 7.3 | 微软与 OpenAI 的新协议规定：OpenAI 宣布实现 AGI 后，要由**独立专家小组**认证。 | 2025-10-28 | https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ | 已核实 |
| 7.4 | 2026-04-27 两家再次修改协议，微软的收入分成改为“与 OpenAI 的技术进展无关”，AGI 条款在商业上失去作用；专家认证机制本身据报道仍保留。 | 2026-04-27 | 同 7.1 | 较确定 |
| 7.5 | 英伟达 CEO 黄仁勋在 Lex Fridman 播客里说“I think we've achieved AGI”，前提是他自己设定的标准（AI 能做出一家市值 10 亿美元的公司，哪怕不长久）；同一期节目又说 10 万个智能体造出英伟达的概率是零。 | 2026-03-22 | https://www.techradar.com/ai-platforms-assistants/i-think-weve-achieved-agi-er-jensen-i-dont-think-we-have ；https://finance.yahoo.com/news/nvidia-ceo-jensen-huang-claims-agi-has-been-achieved-can-create-billion-dollar-businesses-172225126.html | 较确定 |
| 7.6 | 据报道，Sam Altman 在 Forbes 专访中说 OpenAI“基本上已经造出了 AGI”，微软 CEO 纳德拉公开反驳。 | 2026-02 | https://www.therundown.ai/articles/sam-altmans-openai-succession-plan | 存疑（只有二手转述，没读到 Forbes 原文） |
| 7.7 | **GPT-6 Astra**（2026-09-03）：OpenAI 总裁 Greg Brockman 在发布简报中说“Welcome to the AGI era”“我个人认为我们到了”，但也说“每个人对 AGI 的定义都不同”“交给读者自己判断”。各报道一致认为这**不是 OpenAI 的正式 AGI 宣布**，也没有走 7.3 的独立专家认证。 | 2026-09-03 | https://venturebeat.com/technology/welcome-to-the-agi-era-openai-launches-gpt-6-astra ；https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/ ；https://thenextweb.com/news/openai-gpt-6-astra-brockman-agi-claim-us-voluntary-prerelease-review-eu-article-92-evaluations | 较确定（引语各家略有出入） |
| 7.8 | ARC Prize 独立验证：GPT-6 Astra 在 ARC-AGI-3（交互式新环境推理测试）上，**标准测试框架 62.7%**，OpenAI 提供的适配框架 99.9%；在 96% 的关卡上用的步数比人类中位数少。ARC Prize 原话：“我们不认为它是 AGI”，并称即使把基准做满也不能证明实现了 AGI。 | 2026-09-03 | https://arcprize.org/blog/astra | 已核实 |
| 7.9 | 媒体报道中 Astra 的 ARC-AGI-3 分数不一致（98.6%、99.9%、66%、62.7% 都有），**只用 ARC Prize 官方数字**。 | 2026-09 | 对比 7.7 与 7.8 的来源 | 已核实（不一致本身已核实） |

> 结尾措辞建议：“截至 2026 年 9 月，有公司高管说 AGI 已经到了，但这是个人判断，没有公认标准，也没有独立认证。负责相关测试的机构自己也说，这还不是 AGI。”不要说“已经实现 AGI”，也不要说“离 AGI 还很远”，两边都是观点。

---

## 8. “四个台阶”能不能成立

| 台阶 | 靠什么技术 | 关键年份 / 代表 | 结论 |
|---|---|---|---|
| ① 会说人话 | Transformer + 大规模预训练（预测下一个 token）+ 放大规模（缩放定律） | 2017 Transformer；2018 GPT-1；2019 GPT-2；2020 GPT-3、Kaplan 缩放定律 | **成立。** 注意“说人话”指写出通顺的文字，还不会按指令办事 |
| ② 会聊天 | 指令微调（SFT）+ RLHF（后来还有 RLAIF） | 2022-01 InstructGPT；2022-11-30 ChatGPT | **成立。** 最硬的证据：1.3B 的 InstructGPT 比 175B 的 GPT-3 更受偏好 |
| ③ 会思考 | 思维链（2022 年是提示技巧）→ 用可验证奖励的强化学习训练长推理（2024–2025） | 2022-01 CoT；2024-09-12 o1；2025-01-20 DeepSeek-R1 | **成立，但要分清**：2022 年是“提示方法”，2024 年起才是“训练方法” |
| ④ 会做事 | 函数调用 / 工具使用 + 电脑操作 + MCP 标准接口 + 长任务能力 | 2023-06-13 function calling；2024-10-22 computer use；2024-11-25 MCP；2025 Claude Code、Codex；METR 时间跨度 | **成立，但和③时间重叠**：工具调用 2023 年就上线了，比 o1 早。可以说“2025 年前后，做事能力因为推理变强而真正好用了” |

**建议台本表述**：“这四步是四种能力先后成为主流，不是严格一个接一个。”画面上的时间轴可以画成四段有重叠的色带，不画成四个互不相交的台阶。

**缺的一块（可选一句）**：每一步背后都有“放大规模”：先放大参数和数据（2020–2022），后放大推理时的思考量（2024 起）。

---

## 9. 常见误传清单

| 误传 | 事实 | 依据 |
|---|---|---|
| ChatGPT 是第一个大模型 | GPT-3（2020-05）、BERT（2018-10）、GPT-2（2019-02）都更早；ChatGPT 是“第一个火出圈的聊天产品”，底层是 GPT-3.5 系列 | 2.4、2.5、2.11、3.7 |
| ChatGPT 是第一个聊天机器人 | 1966 年 MIT 的 ELIZA（Weizenbaum，Communications of the ACM 1966 年 1 月）就能按关键词规则和人对话 | https://dl.acm.org/doi/10.1145/365153.365168 （较确定） |
| Transformer 是 OpenAI 发明的 | 是 Google 团队 2017 年的论文，最初用于机器翻译；GPT 里的 T 就是 Transformer | 2.1 |
| AI 就是在数据库里搜答案 | 预训练是学习“预测下一个 token”的概率，回答是逐个生成的，不是检索原文（联网搜索是后来加的工具） | 1.1、1.6 |
| “文字接龙”就是全部 | 只描述了预训练和输出方式；聊天模型还有 SFT、RLHF，推理模型还有基于答案对错的强化学习 | 第 1、3、4 节 |
| GPT-4 有 1.8 万亿参数 | OpenAI 官方从未公布 GPT-4 参数量 | 6.1 |
| 模型越大一定越好 | Chinchilla：同样算力下，70B 模型多喂数据能赢 280B 的 Gopher；InstructGPT：1.3B 比 175B 更受偏好 | 2.9、3.5 |
| 思维链是 o1 发明的 | 思维链提示 2022-01 就提出了；o1 的新意是用强化学习**训练**模型去用思维链 | 4.1、4.3 |
| DeepSeek-R1 完全没用人工数据 / 没做 SFT | 没做 SFT 的是 R1-Zero；正式版 R1 用了几千条冷启动数据先做 SFT | 4.10 |
| DeepSeek-R1 只花了 560 万美元 | 560 万美元是 V3 最后一次训练的估算；R1 那一步约 29.4 万美元；两者都不含前期研发 | 4.12 |
| METR 说 AI 能连续工作 14 小时 | 纵轴是人类完成该任务的耗时，是 50% 成功率，而且主要是软件任务 | 5.15 |
| RLHF 是 ChatGPT 才有的 | 2017 年就有论文（Christiano 等），InstructGPT 2022 年 1 月已用于 API | 3.1、3.6 |
| 某公司已经宣布实现 AGI | 截至 2026-09-27 只有高管的个人表态（Brockman、黄仁勋等），没有公司正式宣布，没有独立认证，也没有学界共识 | 7.5–7.8 |
| Codex 就是 2021 年那个代码模型 | 2025 年的 Codex 是新的编程智能体（CLI 4 月、云端 5 月），只是沿用了名字 | 5.8、5.9 |

---

## 10. 台本 CHECKLIST 可直接引用的数字

| 数字 | 出处 | 可信度 |
|---|---|---|
| Transformer 论文 2017 年 6 月（arXiv 2017-06-12），Google | arXiv 1706.03762 | 已核实 |
| GPT-1 2018 年 6 月，1.17 亿参数 | GPT-1 论文 + GPT-2 论文表 2 | 已核实（具体日 6-11 较确定） |
| GPT-2 2019 年 2 月，15 亿参数 | GPT-2 论文 | 已核实 |
| GPT-3 2020 年 5 月，1750 亿参数 | arXiv 2005.14165 | 已核实 |
| Kaplan 缩放定律 2020 年 1 月 | arXiv 2001.08361 | 已核实 |
| Chinchilla 2022 年 3 月，70B 胜 280B | arXiv 2203.15556 | 已核实 |
| InstructGPT 2022 年 1 月（论文 3 月），1.3B 胜 175B | arXiv 2203.02155 | 已核实 |
| ChatGPT 2022 年 11 月 30 日 | OpenAI 官方页 | 较确定 |
| 思维链 2022 年 1 月 | arXiv 2201.11903 | 已核实 |
| o1 2024 年 9 月 12 日 | OpenAI 官方页 | 较确定 |
| DeepSeek-R1 2025 年 1 月 20 日；AIME 15.6% → 71.0%（R1-Zero） | DeepSeek 官方 + arXiv 2501.12948 | 已核实 |
| 函数调用 2023 年 6 月 13 日 | OpenAI 官方页 | 较确定 |
| Computer use 2024 年 10 月 22 日 | Anthropic 官方 | 已核实 |
| MCP 2024 年 11 月 25 日 | Anthropic 官方 | 已核实 |
| Claude Code 2025 年 2 月预览、5 月正式版 | Anthropic 官方 | 较确定 / 已核实 |
| METR：约 7 个月翻倍（2019 起），2024 年起约 3 个月 | arXiv 2503.14499；METR TH1.1 | 已核实 |
| GPT-6 Astra 2026 年 9 月 3 日；ARC-AGI-3 标准框架 62.7% | ARC Prize 官方 | 已核实 |

---

## 11. 查证过程说明

- openai.com 全站对 WebFetch 返回 403，OpenAI 官方博客的日期和原句靠搜索引擎摘要、同日可靠报道（Simon Willison、TechCrunch、InfoQ）和维基百科交叉确认，统一标为“较确定”。出片前如能用浏览器打开 openai.com 核对一遍，可升为“已核实”。
- Nature 页面需要登录跳转，R1 的 Nature 信息来自 arXiv 页面的期刊引用和 ADS 摘要页。
- GPT-6 Astra、黄仁勋、Altman 的 AGI 相关表态都晚于模型知识截止时间，全部来自本次联网检索。Astra 的引语各家报道略有出入，上屏只用 ARC Prize 官方数字和“个人认为”“不是正式宣布”这类稳妥说法。
