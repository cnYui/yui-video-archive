# 第 2 期台本 · 对抗式事实审校

- 审校对象：`_staging/ep02/final/台本/script_data.py`（`台本.md` 由它生成，内容一致，段号取自 `台本.md`）
- 方法：逐句默认有错，打开一手来源核对（论文 PDF、官方博客、官方数据文件、访谈文字稿）。openai.com、axios.com 对抓取返回 403，这两处改用同日报道和 OpenAI 开发者文档交叉核对，表里注明。
- 查询日期：全部为 2026-09-27
- 结论：**blocker 0 条，major 3 条，minor 16 条**。AGI 现状没有说过头；有一处偏保守（S07-59 把 99.9% 写成“另计”）。“文字接龙对了一半”的讲法公允。RLHF、推理模型、函数调用的机制描述没有简化到出错。时间线顺序正确。画面没有要求画真实 logo。

---

## 一、有问题的条目

| 场景/段落 | 原句 | 问题 | 严重程度 | 改法 | 来源 URL | 查询日期 |
|---|---|---|---|---|---|---|
| S07-56 台词 + 画面第二张引语卡 + CHECKLIST 黄仁勋条 | 台词“英伟达的黄仁勋也这么说过，用的是他自己的标准。”画面卡底“他的标准「AI 能做出一家市值 10 亿美元的公司」”。 | **标准是主持人提的，不是黄仁勋自己的。** 文字稿 01:55:06 起，Lex Fridman 先给了一个定义：AI 能“start, grow, and run a successful technology company that's worth more than a billion dollars”，然后问要几年。黄仁勋 01:56:31 答“I think it's now. I think we've achieved AGI.”，接着补充“You said a billion, and you didn't say forever”。同一段里他还说，10 万个这样的智能体造出英伟达的概率是 0%。说成“他自己的标准”，把原话的出处弄错了。 | major | 台词改为“英伟达的黄仁勋也这么说过，用的是主持人给的一个标准。”（字数基本不变）。画面卡底改为「主持人提的标准：AI 能创办并运营一家市值超 10 亿美元的公司」，另加小字「黄仁勋补充：不必长久」。CHECKLIST 同步改。 | https://lexfridman.com/jensen-huang-transcript/ （#494，页面 datePublished 2026-03-23） | 2026-09-27 |
| S03-17 台词 + 画面右栏 ① | “但GPT-2论文推测，要猜准下一个词，就得学会语法、常识和任务本身。”画面「要猜准，得先学会语法、常识、任务」（小字：GPT-2 论文的推测，2019）。 | **论文里没有“语法、常识”这层意思，也没有说“就得”。** GPT-2 论文 §2 原句：“Our speculation is that a language model with sufficient capacity will begin to learn to infer and perform the tasks demonstrated in natural language sequences in order to better predict them”。原意是：模型容量够大时，为了预测得更好，会开始学会文本里演示的任务。台本把论文没说的内容算到了论文头上，“就得”也把推测说成了必然。 | major | 台词改为“但GPT-2论文推测，模型够大时，为了猜准下一个词，会顺带学会文本里演示的任务。”画面改为「为了猜准，会学会文本里演示的任务（翻译、问答…）」，小字不变。 | https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf （§2） | 2026-09-27 |
| S07-61 画面小字 | 「2025-10 微软与 OpenAI 协议：OpenAI 宣布 AGI 须由独立专家小组核实」 | **这是旧条款，放在「独立认证 ✕」旁边会被当成现行机制。** 2025-10-28 的原文确实这么写。可 2026-04-27 两家又改了协议，微软官方公告全文不再提 AGI 和专家小组，收入分成改成“independent of OpenAI's technology progress”。专家小组现在还有没有，官方没有说明。台本自己的 CHECKLIST 也写了“存疑，不写”，画面却写上了。 | major | 首选删掉这行小字。要保留就改成「2025-10 协议曾规定：OpenAI 宣布 AGI 须经独立专家小组核实（2026-04 修改协议后，官方公告未再提及）」。 | https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ ；https://blogs.microsoft.com/blog/2026/04/27/the-next-phase-of-the-microsoft-openai-partnership/ | 2026-09-27 |
| S07-57 台词 + 右栏标题「说没到」 | “也有人说没到。评测组织ARC Prize，按第三种定义出题，看学习效率。” | 说 ARC Prize“说没到”偏强。他们在 Astra 博客里的原话是“we are not claiming that it is AGI”（我们并不宣称它是 AGI），还说把这套题做满也不能证明是 AGI。ARC-AGI-3 页面另有一句“As long as there is a gap between AI and human learning, we do not have AGI”，算是间接说了没到。 | minor | 改成“也有人不认同。”；或者给“说没到”补一位明说没到的人，例如哈萨比斯（2026-02：AGI 可能在未来 5 到 8 年出现，现在的 AI 是“锯齿状智能”）。 | https://arcprize.org/blog/astra ；https://arcprize.org/arc-agi/3 ；https://www.storyboard18.com/brand-makers/google-deepmind-ceo-says-agi-not-here-yet-calls-current-ai-jagged-intelligence-90028.htm | 2026-09-27 |
| S07-59 画面小字 | 「ARC Prize 官方数据 · OpenAI 自己的适配框架成绩另计」 | 写成“另计”有回避之嫌，偏向说不足。ARC Prize 博客和结果页都公开了适配框架的成绩：High 档 99.95%，Max 档 98.55%，博客标题数字写 99.9%。还说 Astra 在 96.0% 的关卡上用的步数比人类基线少。 | minor | 并列两根柱：「标准框架 62.7%」「OpenAI 适配框架 99.9%（保留模型内部推理状态）」，旁边小字「ARC Prize：适配框架成绩不作为标准成绩」。台词不用改。 | https://arcprize.org/blog/astra ；https://arcprize.org/results/openai-gpt-6-astra | 2026-09-27 |
| S07-50 台词 | “OpenAI章程说，AGI要在大多数有经济价值的工作上超过人类。” | 中文意思基本对，但漏了主语“高度自主的系统”。章程原句：“highly autonomous systems that outperform humans at most economically valuable work”。 | minor | “OpenAI章程说，AGI是在大多数有经济价值的工作上，超过人类的高度自主系统。”（多 7 字）或者台词不改，只在画面中文译文里补全。 | https://openai.com/charter/ （403；原句由搜索摘要和多家转述一致确认，章程 2018-04 发布，2026 年没有改过定义） | 2026-09-27 |
| S04-28 台词 + 对比卡 | “人工评估里，13亿参数的它，比1750亿参数的GPT-3更受喜欢。” | InstructGPT 有 1.3B、6B、175B 三个版本。论文结论是“the 1.3B parameter InstructGPT model”也比 175B GPT-3 更受偏好。说成“它”，观众会以为 InstructGPT 就是 13 亿参数，其实 API 默认用的是 175B。 | minor | “人工评估里，它最小的13亿参数版本，都比1750亿参数的GPT-3更受喜欢。”对比卡改成「InstructGPT（最小版）13 亿」。 | https://arxiv.org/abs/2203.02155 | 2026-09-27 |
| S04-26 画面角注 | 「RLHF 方法最早见于 2017 年论文」 | “最早”不准。在 Christiano 等 2017 年这篇之前，已经有从人类反馈、人类偏好学习的强化学习工作，例如 2008–2009 年的 TAMER、2011 年前后的基于偏好的策略学习。2017 年这篇是现代 RLHF 最常引用的源头。 | minor | 「现代 RLHF 常追溯到 2017 年论文（Christiano 等）」 | https://arxiv.org/abs/1706.03741 | 2026-09-27 |
| S05-34 画面 | 时间轴卡片「2024-09-12「o1」」 | 2024-09-12 发布的是 o1-preview 和 o1-mini。正式版 o1 是 2024-12-05。 | minor | 「2024-09-12 o1（预览版）」。台词“2024年9月，OpenAI发布o1”可以不改。 | https://simonwillison.net/2024/Sep/12/openai-o1/ （openai.com 403） | 2026-09-27 |
| S06-44 画面 | 斜率标注「约 7 个月翻倍（2019 起）」「约 3 个月翻倍（2024 起）」，小字「METR，2026-05」 | 两个数字的出处和标注的日期对不上。“约 7 个月”出自 2025-03 论文和 2026-01 TH1.1 博客（2019–2025 年，196 天）；“约 3 个月”出自 2026-01-29 TH1.1 博客（2024 年起 89 天）。标注的 2026-05 数据页给的是另一组：全时段约 188 天（约 6 个月），2023 年起约 129 天（约 4 个月）。 | minor | 二选一：① 全用 2026-05 数据页：「约 6 个月翻倍（2019 起）」「约 4 个月翻倍（2023 起）」；② 数字不改，小字改成「METR 2025-03 论文 / 2026-01 TH1.1 更新」。 | https://metr.org/assets/benchmark_results_1_1.yaml ；https://metr.org/blog/2026-1-29-time-horizon-1-1/ | 2026-09-27 |
| S08-63 台词 | “第一，持续学习：模型训练完就固定了，不能边用边学。” | “不能边用边学”太绝对。S03 画面刚演示过 GPT-3“给几个例子就会 · 参数不变”，也就是上下文学习，两处自相矛盾。哈萨比斯原话是训练完“kind of frozen”，卡帕西说的是“You can't just tell them something and they'll remember it”。 | minor | “第一，持续学习：模型训练完参数就固定了，用的时候学到的东西，留不下来。” | https://www.storyboard18.com/brand-makers/google-deepmind-ceo-says-agi-not-here-yet-calls-current-ai-jagged-intelligence-90028.htm ；https://www.dwarkesh.com/p/andrej-karpathy | 2026-09-27 |
| S08-64 台词 | “要十次做对八次，METR测过的最好模型只能做约3小时的任务，还会编造信息。” | ① 3 小时是人类完成任务的耗时，S06 刚强调过，这里漏了。② “还会编造信息”出自《国际 AI 安全报告 2026》，说的是 AI 系统普遍存在的问题，跟在 METR 那个模型后面，读起来像是那个模型的测试结果。数字本身没错：Mythos Preview 的 80% 时间跨度是 3.1 小时，是数据页里最高的。 | minor | “要十次做对八次，METR测过的最好模型，只能做人类约3小时的任务。而且，模型还会编造信息。” | https://metr.org/assets/benchmark_results_1_1.yaml ；https://internationalaisafetyreport.org/publication/2026-report-executive-summary | 2026-09-27 |
| S07-61、S09-71 台词 | “AGI没有正式宣布” | 没说清是谁没有宣布。黄仁勋 2026-09-06 在 X 上发了“AGI has arrived”，不少媒体标题用的是 declares。 | minor | “没有哪家开发公司正式宣布”。可选：黄仁勋引语卡补一行「2026-09 在 X 上又说：AGI has arrived」。 | https://www.foxbusiness.com/technology/nvidia-ceo-jensen-huang-declares-agi-has-arrived-after-openai-unveils-gpt-6-astra ；https://www.techradar.com/ai-platforms-assistants/chatgpt/jensen-huang-once-again-declares-that-agi-has-arrived-but-his-gpt-6-celebration-feels-like-hes-just-trying-to-sell-next-gen-nvidia-gpus | 2026-09-27 |
| S06-39 台词 | “第四级，学会做事：调用工具、操作电脑。这样的AI叫智能体，Agent。” | 对智能体的定义太宽。智能体一般指能自己规划、多步调用工具去完成目标的系统；只调用一次工具的模型通常不算。 | minor | “能自己一步步调用工具、操作电脑、把任务做完的AI，叫智能体，Agent。” | https://www.anthropic.com/news/3-5-models-and-computer-use （机制参照） | 2026-09-27 |
| S07-52 与全片“第一级…第四级” | “2023年的ChatGPT这类模型，只算第1级“初现”……” | 这不是事实错误，是容易混淆：本片自己的“第一级＝预训练”和 DeepMind 分级的“第 1 级＝初现”用了同一个说法，观众可能以为是同一套分级。 | minor | “只算DeepMind分级里的第1级，初现”。或者把本片的四级改叫“第一步……第四步”。 | https://arxiv.org/html/2311.02462v5 | 2026-09-27 |
| S03-19 画面角注 | 「是否算“理解”：2022 年 NLP 研究者调查几乎对半分」 | 调查问的是“只靠文本训练的模型，在数据和算力足够时，原则上能否理解语言”，不是问当时的模型懂不懂。摘要原话：“split almost exactly in half on questions about … whether language models understand language”。 | minor | 「“只靠文本训练的模型能否理解语言”：2022 年 NLP 研究者调查几乎对半分」 | https://arxiv.org/abs/2208.12852 | 2026-09-27 |
| CHECKLIST “OpenAI 官方发布帖没有宣布实现 AGI”条 | 引用 community.openai.com/t/introducing-gpt-6-astra…/1394703，标“已核实” | 发这个帖子的是社区用户 VeitB，没有 OpenAI 员工标识，不能算官方来源。结论本身没错：OpenAI 发布页称 Astra 为“most intelligent and aligned model”，没有正式称它是 AGI。 | minor | 来源换成 https://openai.com/index/gpt-6-astra/ （出片前用浏览器打开核对），并附 TechSpot、Wikipedia 对发布页的描述。 | https://www.techspot.com/news/113739-openai-welcomes-agi-era-gpt-6-astra-first.html ；https://en.wikipedia.org/wiki/GPT-6_Astra | 2026-09-27 |
| S06-46 画面 | 「2023-03 GPT-4 可接收图片输入」 | 2023-03 发布时，技术报告写的是能接收图片，但图片输入当时只是研究预览，面向普通用户开放是 2023-09。 | minor | 「2023-03 GPT-4 技术报告：可接收图片输入」 | https://arxiv.org/abs/2303.08774 | 2026-09-27 |
| PRONUNCIATION METR 条 | TTS 写作“M E T R” | 不算事实错误。METR 官网写明读作 “meter”。PRONUNCIATION 已经提示，请用户定。 | minor | 维持现状，或者 TTS 改成“Meter”。 | https://metr.org/about | 2026-09-27 |

---

## 二、专项检查结论

| 检查项 | 结论 | 依据 | 查询日期 |
|---|---|---|---|
| AGI 现状有没有说过头 | 没有。只说“有人说到了”，布罗克曼、黄仁勋都标成个人表态；结论是“没有正式宣布、没有独立认证、也没有共识”。截至 2026-09-27 没查到任何开发公司正式宣布；Wikipedia「2026 in AI」9 月条目只有 BC 省起诉和 Sora API 停用两条。 | Fortune / VentureBeat / TechSpot 2026-09-03；https://en.wikipedia.org/wiki/2026_in_artificial_intelligence | 2026-09-27 |
| AGI 现状有没有说不足 | 略有：99.9% 写成“另计”，见上表 S07-59。可选补充：Altman 2026-08-26 对 TIME 说 OpenAI“not quite yet”，年底前会有他愿意称为 AGI 的内部系统。 | https://time.com/article/2026/08/26/openai-sam-altman-interview/ （经搜索摘要） | 2026-09-27 |
| “文字接龙说对了一半”是否公允 | 公允。对的一半（预训练目标、逐个 token 输出）和另一半（SFT/RLHF、可验证奖励 RL、规划韵脚、学界仍在争）都讲了，也没说 AI“真的理解”。唯一要改的是 S03-17 的论文归属，见上表。 | GPT-1 论文 §3.1；Anthropic 2025-03-27；arXiv 2208.12852 | 2026-09-27 |
| RLHF 机制 | 正确：人写示范做监督微调 → 人给回答排序 → 训练奖励（打分）模型 → 用强化学习往高分改。 | https://arxiv.org/abs/2203.02155 摘要 | 2026-09-27 |
| 推理模型机制 | 正确：思维链提示（2022）只是提示技巧；o1 用大规模强化学习训练模型用思维链思考；R1-Zero 不做 SFT，用规则奖励（准确性 + 格式）。 | Simon Willison 转引 OpenAI 原文；DeepSeek-R1 论文 §1.1、§2.2.2 | 2026-09-27 |
| 智能体、函数调用机制 | 函数调用正确：模型返回描述函数调用的 JSON，由开发者程序执行后把结果交回模型。智能体定义略宽，见 S06-39。 | https://simonwillison.net/2023/Jun/13/function-calling/ | 2026-09-27 |
| OpenAI Charter 中文意思 | 基本准确，漏了“高度自主系统”，见 S07-50。ARC Prize 引语译成“我们并不是说它是 AGI”，准确，比查证材料里的“我们不认为它是 AGI”更贴原文。 | openai.com/charter；arcprize.org/blog/astra | 2026-09-27 |
| 时间线顺序 | 正确。Transformer 2017-06 → GPT-1 2018-06 → GPT-2 2019-02 → GPT-3 2020-05 → InstructGPT 2022-01-27 / CoT 2022-01-28 → ChatGPT 2022-11-30 → 函数调用 2023-06-13 → o1-preview 2024-09-12 → Computer Use 2024-10-22 → MCP 2024-11-25 → R1 2025-01-20 → ARC-AGI-3 2026-03-25 → Astra 2026-09-03。“函数调用比 o1 早一年多”＝15 个月。 | 见下表各行 | 2026-09-27 |
| 画面是否要求画真实 logo | 没有。聊天气泡、新闻卡、桌面、终端都标了“示意 / 虚构、无 logo”，品牌只以文字出现。 | script_data.py 画面说明 | 2026-09-27 |

---

## 三、已核实的事实

| 场景/段落 | 原句 / 画面文字 | 问题 | 严重程度 | 改法 | 来源 URL | 查询日期 |
|---|---|---|---|---|---|---|
| S03-10 | 预训练＝读海量文本，根据前文预测下一个 token | 已核实（GPT-1 论文 §3.1 标准语言模型目标） | — | — | https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf | 2026-09-27 |
| S03-11 + 画面 | 2017 年 Google 提出 Transformer；《Attention Is All You Need》；最初用于机器翻译 | 已核实（arXiv v1 2017-06-12） | — | — | https://arxiv.org/abs/1706.03762 | 2026-09-27 |
| S03-12/13 | GPT＝Generative Pre-trained Transformer，生成式预训练 Transformer | 已核实（OpenAI 开发者文档：“generative pre-trained transformers or "GPT" models”）；GPT-1 论文题目 Improving Language Understanding by Generative Pre-Training（2018） | — | — | https://developers.openai.com/api/docs/concepts | 2026-09-27 |
| S03-14 + 画面 | GPT-1 1.17 亿（2018）、GPT-2 15 亿（2019）、GPT-3 1750 亿（2020），两年 | 已核实（GPT-2 论文表 2：117M / 1542M；GPT-3 175B，arXiv 2020-05-28） | — | — | GPT-2 论文 PDF（同上）；https://arxiv.org/abs/2005.14165 | 2026-09-27 |
| S03-14 画面 | GPT-4 起官方不公布参数量 | 已核实（技术报告未披露模型规模） | — | — | https://arxiv.org/abs/2303.08774 | 2026-09-27 |
| S03-16 | 训练目标是预测下一个词，回答逐个生成 | 已核实 | — | — | 同 S03-10；Anthropic “trained to output one word at a time” | 2026-09-27 |
| S03-17 画面 | GPT-3 给几个例子就会、参数不变 | 已核实（GPT-3 摘要：不做梯度更新或微调） | — | — | https://arxiv.org/abs/2005.14165 | 2026-09-27 |
| S03-18 + 画面 | Claude 写押韵诗先想好韵脚再写这一行；Anthropic 2025-03-27 | 已核实（研究对象是 Claude 3.5 Haiku，第二行开写前就想好押韵词，再写一行去凑它） | — | — | https://www.anthropic.com/research/tracing-thoughts-language-model | 2026-09-27 |
| S03-19 | 一次输出一个词不等于只想下一个词；学界还在争 | 已核实（Anthropic 原句“may think on much longer horizons”；2022 年调查几乎对半分） | — | — | 同上；https://arxiv.org/abs/2208.12852 | 2026-09-27 |
| S04-22~26 | SFT：人写标准回答，模型照着学；RLHF：人给回答排序 → 打分模型 → 往高分改 | 已核实 | — | — | https://arxiv.org/abs/2203.02155 | 2026-09-27 |
| S04-27 | 2022 年 1 月 InstructGPT | 已核实（官方博客 2022-01-27；论文 v1 2022-03-04） | — | — | https://arxiv.org/abs/2203.02155 ；https://openai.com/index/instruction-following/ （403，日期经同日报道确认） | 2026-09-27 |
| S04-28 | 13 亿 vs 1750 亿，评估者更喜欢 | 已核实（措辞见上表 minor） | — | — | https://arxiv.org/abs/2203.02155 | 2026-09-27 |
| S04-29 + 画面 | 2022-11-30 ChatGPT 发布，方法同 InstructGPT，数据改成对话形式 | 已核实（原文“same methods as InstructGPT, but with slight differences in the data collection setup”） | — | — | https://openai.com/index/chatgpt/ （403，原句经多方一致转述） | 2026-09-27 |
| S05-32/33 | 2022 年 1 月 Google 提出思维链提示；例题写步骤，模型跟着写；只是提示技巧 | 已核实（arXiv v1 2022-01-28） | — | — | https://arxiv.org/abs/2201.11903 | 2026-09-27 |
| S05-34 | 2024 年 9 月 o1，用强化学习训练先想再答 | 已核实（原文“Our large-scale reinforcement learning algorithm teaches the model how to think productively using its chain of thought”） | — | — | https://simonwillison.net/2024/Sep/12/openai-o1/ | 2026-09-27 |
| S05-35 + 画面 | 2025-01-20 DeepSeek-R1，开源权重 | 已核实（MIT 协议，同时开源 R1-Zero 和 6 个蒸馏模型） | — | — | https://www.deepseek.com/en/news/deepseek-r1/ ；https://arxiv.org/abs/2501.12948v1 | 2026-09-27 |
| S05-36 + 画面 | R1-Zero 跳过 SFT 直接 RL；奖励只看答案对不对、格式对不对；正式版先用冷启动数据 | 已核实（§1.1“without relying on supervised fine-tuning”；§2.2.2 Accuracy rewards / Format rewards；正式版“cold-start data before RL”） | — | — | https://arxiv.org/abs/2501.12948v1 | 2026-09-27 |
| S05-37 + 画面 | AIME 2024 一次做对比例 15.6% → 71%；自己学会回头检查（aha moment） | 已核实（“pass@1 score on AIME 2024 increases from 15.6% to 71.0%”；“aha moment … reevaluating its initial approach”） | — | — | https://arxiv.org/abs/2501.12948v1 | 2026-09-27 |
| S06-40/41 + 画面 | 2023-06-13 函数调用；模型给出函数名和参数，程序执行 | 已核实（gpt-4-0613 / gpt-3.5-turbo-0613；模型返回 JSON，由开发者执行） | — | — | https://simonwillison.net/2023/Jun/13/function-calling/ | 2026-09-27 |
| S06-42 + 画面 | 2024-10-22 Anthropic 电脑操作：看屏幕、点鼠标、打字 | 已核实（公测版，“look at a screen, moving a cursor, clicking buttons, and typing text”） | — | — | https://www.anthropic.com/news/3-5-models-and-computer-use | 2026-09-27 |
| S06-42 画面 | 2024-11-25 MCP 开放标准；2025 年 Claude Code、Codex | 已核实，来自 R1 5.5–5.9（MCP、Claude Code GA 已核实；Codex 日期较确定） | — | — | https://www.anthropic.com/news/model-context-protocol ；https://www.anthropic.com/news/claude-4 | 2026-09-27 |
| S06-43 + 画面 | METR 定义：AI 有一半把握做完的任务，人类专家要做多久；Model Evaluation and Threat Research，非营利研究机构 | 已核实（官网“research nonprofit”；FAQ“measure of the difficulty of a task, rather than the time an AI spends”） | — | — | https://metr.org/about ；https://metr.org/time-horizons/ | 2026-09-27 |
| S06-44 | GPT-4 约 4 分钟；2026 年测得最好到十几小时；16 小时以上测不准 | 已核实（YAML：gpt_4 p50 3.99 分钟；Claude Opus 4.6 11.98 小时；Mythos Preview（early）17.41 小时；页面更新于 2026-05-08，注明“Measurements above 16 hrs are unreliable”。GPT-5.6 Sol 2026-06 标准口径 11.3 小时，METR 自己说不可靠；Opus 5.5 的 2026-09-22 报告没给时间跨度） | — | — | https://metr.org/assets/benchmark_results_1_1.yaml ；https://metr.org/blog/2026-06-26-gpt-5-6-sol/ ；https://metr.org/blog/2026-09-22-claude-opus-5-5/ | 2026-09-27 |
| S06-45 + 画面 | 人类耗时 ≠ AI 连续工作时长；50% 成功率；以软件类任务为主 | 已核实（FAQ：“primarily composed of software engineering, machine learning, or cybersecurity tasks”） | — | — | https://metr.org/time-horizons/ | 2026-09-27 |
| S06-46 画面 | 思维链 2022-01 早于 ChatGPT 2022-11；函数调用 2023-06 早于 o1 2024-09 | 已核实 | — | — | 见上各行 | 2026-09-27 |
| S07-48/49 | AGI＝Artificial General Intelligence，通用人工智能，没有统一定义 | 已核实（布罗克曼本人也说“Everyone has a different definition of AGI”） | — | — | https://venturebeat.com/technology/welcome-to-the-agi-era-openai-launches-gpt-6-astra | 2026-09-27 |
| S07-50 画面 | OpenAI 章程（2018）英文原句 | 已核实（原句一致；2018-04 发布，2026 年定义未改） | — | — | https://openai.com/charter/ （403，经搜索摘要确认） | 2026-09-27 |
| S07-51/52 + 画面 | Google DeepMind《Levels of AGI》2023-11；0–5 级（无 AI / 初现 / 胜任 / 专家 / 卓越 / 超人）；ChatGPT 这类在第 1 级初现＝等于或略好于没有相关技能的人 | 已核实（v1 2023-11-04；v5 表 1 Emerging“equal to or somewhat better than an unskilled human”，通用栏列 ChatGPT、Bard、Llama 2、Gemini；第 4 级 v5 改名 Exceptional，原名 Virtuoso） | — | — | https://arxiv.org/abs/2311.02462 ；https://arxiv.org/html/2311.02462v5 | 2026-09-27 |
| S07-53 + 画面 | 肖莱 2019：智能＝技能获取效率；ARC＝Abstraction and Reasoning Corpus | 已核实（arXiv 2019-11-05；ARC Prize：“AGI is a system that can match the learning efficiency of humans”） | — | — | https://arxiv.org/abs/1911.01547 ；https://arcprize.org/arc-agi | 2026-09-27 |
| S07-55 + 画面 | 9 月 3 日 OpenAI 发布 GPT-6 Astra；总裁布罗克曼：“欢迎来到 AGI 时代”；发布简报；他也说每个人的定义都不同 | 已核实（闭门媒体简报，原话“Welcome to the AGI era.”“For me personally, I do think we're there.”；Fortune 称他为 president and cofounder；3 日有限预览，4 日向付费用户开放） | — | — | https://venturebeat.com/technology/welcome-to-the-agi-era-openai-launches-gpt-6-astra ；https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/ ；https://en.wikipedia.org/wiki/GPT-6_Astra | 2026-09-27 |
| S07-56 | 个人表态，OpenAI 没有正式宣布 | 已核实（Fortune：OpenAI did not formally declare；发布页只称“most intelligent and aligned model”） | — | — | 同上；https://www.techspot.com/news/113739-openai-welcomes-agi-era-gpt-6-astra-first.html | 2026-09-27 |
| S07-56 画面 | 「I think we've achieved AGI」— 黄仁勋，2026-03 播客 | 引语和日期已核实；“他的标准”有误，见上表 major | — | — | https://lexfridman.com/jensen-huang-transcript/ | 2026-09-27 |
| S07-58 + 画面 | 3 月的 ARC-AGI-3：没有说明的新游戏，要自己摸索规则；发布时 AI 不到 1%，人类 100% | 已核实（2026-03-25；“There are no instructions, no rules, and no stated goals”；“Humans score 100%. Frontier AI scores 0.51%.”） | — | — | https://arcprize.org/blog/arc-agi-3-launch | 2026-09-27 |
| S07-59 | 9 月 Astra 用标准测法 62.7% | 已核实（Semi-Private 集，Max 档 62.71%，约 2.6 万美元；适配框架见上表 minor） | — | — | https://arcprize.org/blog/astra ；https://arcprize.org/results/openai-gpt-6-astra | 2026-09-27 |
| S07-60 + 画面 | ARC Prize：“我们并不是说它是 AGI”；理由之一是规则固定、目标封闭、不代表真实世界 | 已核实（“we are not claiming that it is AGI”；“deterministic, closed-ended mechanics and goals”；“does not represent the complexity and open-endedness of the real world”） | — | — | https://arcprize.org/blog/astra | 2026-09-27 |
| S07-61 | 截至 2026 年 9 月：没有正式宣布、没有独立认证、没有共识 | 已核实（主语见上表 minor） | — | — | 见第二节 | 2026-09-27 |
| S07-61 画面 | 《Nature》评论（2026-02）认为已具备通用智能，有争议 | 已核实（Chen、Belkin、Bergen、Danks，《Does AI already have human-level intelligence? The evidence is clear》，Nature 650:36–40） | — | — | https://www.nature.com/articles/d41586-026-00285-6 | 2026-09-27 |
| S08-63 画面 | Hassabis 2026-02 · Karpathy 2025-10 | 已核实（Hassabis 2026-02-18 印度 AI 影响力峰会“kind of frozen”；Karpathy 2025-10-17 Dwarkesh 播客） | — | — | 见上表 S08-63 | 2026-09-27 |
| S08-64 画面 | 50% 把握十几小时 / 80% 把握约 3 小时；《国际 AI 安全报告 2026》 | 已核实（Mythos p80 3.10 小时；报告 2026-02-03：“fabricating information, producing flawed code, and giving misleading advice”） | — | — | https://metr.org/assets/benchmark_results_1_1.yaml ；https://internationalaisafetyreport.org/publication/2026-report-executive-summary | 2026-09-27 |
| S08-65 | 真实工作更乱、没有标准答案，AI 做得更差 | 已核实（METR FAQ：多数工作“require interacting with other people and involve success metrics that cannot be algorithmically scored”） | — | — | https://metr.org/time-horizons/ | 2026-09-27 |
| S08-66 + 画面 | 杨立昆：只学文字的模型缺少世界模型（2026-01） | 已核实（“limited to the discrete world of text … they lack a model of the world”） | — | — | https://www.technologyreview.com/2026/01/22/1131661/yann-lecuns-new-venture-ami-labs/ | 2026-09-27 |
| S08-67 | AGI 到没到要看定义；AI 能完成的任务越来越长 | 已核实（METR 趋势，限于其任务集） | — | — | https://metr.org/time-horizons/ | 2026-09-27 |
| S09-69~72 | 总结三条和“对了一半” | 已核实，与正文一致（S09-71 主语见上表） | — | — | — | 2026-09-27 |
