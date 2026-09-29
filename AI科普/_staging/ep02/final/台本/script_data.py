# -*- coding: utf-8 -*-
"""《原LAI如此》第 2 期「从学会说人话到AGI」台本数据（审校后定稿，待用户确认）。

题目（用户原话）：你的一句话就否定了ai一路的努力--AI是怎么从学会说人话到实现AGI的?
骨架：四个阶段（接龙 → 对话 → 思考 → 做事），再讲 AGI 到了吗、还差什么。
本版按 _staging/ep02/review_fact.md（major 3 条全改，minor 大部分采纳）和 review_style.md（高、中全改，低优先级大部分采纳）修改。

行的写法（skill/references/pipeline-contract.md 第 3、4 节）：
  ("say", "字幕原文", "TTS 文本", "画面说明")    一段配音 = 一段字幕；段号由 build_script.py 按全片顺序生成
  ("gap", 秒, "画面说明")                        不说话的纯画面停顿
动作只用词表：抬手、吃惊、认真、开心、疑问、收到、好耶、小跳、走动。
事实取自 _staging/ep02/research_R1_history.md（R1）、research_R2_agi.md（R2）和两份审校，查询日期 2026-09-27。
"""

NOTES = [
    "2026-09-27 用户决定：本期只用大肥鱼（DeepSeek 拟人鲸鱼娘）当讲解员，配音用 Fish Audio「苏晓晓」；开场、结尾自称“鲸鱼娘”（用户 2026-09-27 定）；背景用现有 8 张图；片尾：配音 Fish Audio / 制作 Opus 5.5。",
    "动作按 v2 词表重排为 28 个：走动 1、挥手 1、侧耳 1、数一/数二/数三 两组 6、指这里 1、重点 1、吃惊 4、摊手 1、抬手 3、思考 2、手放胸前 1（说到 DeepSeek 开源 R1，她自己就是 DeepSeek 拟人）、"
    "摇头+认真 2、叉腰 2、竖拇指 1、好耶 1（带拉炮）。说话时的小手势、句末点头、看向内容由引擎自动层加，台本不写。大动作 12 个（上限 12）；去掉了小跳，因为它和 S07 的数手指只隔约 12 s。",
    "预计正片 6:28.8（388.8 s，目标 5:40–6:30），加片头 3.8 s、片尾 4.8 s 约 6:37；77 段台词。按 epcommon.est_seconds（5.3 字/秒 + 每句 0.25 s）"
    "+ 每段后 0.25 s + 停顿估算，和 build_script.py 同一算法。分场：S01 0:08 / S02 0:25 / S03 1:02 / S04 0:45 / S05 0:42 / S06 0:57 / S07 1:24 / S08 0:38 / S09 0:28。",
    "三个疑问 → 章节：① AI只是文字接龙吗 → S03；② AI怎么一步步变强 → S04、S05、S06；③ AGI是什么，实现了吗 → S07、S08。"
    "疑问卡和右上角目录都用 episode.json questions 的文字。",
    "章节：开场 / 三个疑问 / 一 学会接龙 / 二 学会对话 / 三 学会思考 / 四 学会做事 / 五 AGI 到了吗 / 六 还差什么 / 总结。"
    "本片的四步统一叫“阶段”（第一个阶段 … 第四阶段），“级”只留给 DeepMind 的 0–5 级，免得“第一级：预训练”和 DeepMind 的“1级”混淆，也避开“AI四级”听成英语四级（2026-09-27 主会话改）。",
    "主线：每个阶段都落在“训练目标多了一条”上（① 预测下一个词 → ② 人更喜欢哪个回答 → ③ 答案对不对），右下角“训练目标”小清单全片保留；"
    "S06 结尾开场气泡回来，“文字接龙”只罩住第一条色带；S09 最后一句回应题目：“对了一半”。",
    "英文全称：GPT、AGI 的英文全称念出来；SFT、RLHF 念中文名 + 简称，英文全称只上屏（框 ①② 里写全）。待用户确认，要念的话正片约长 4 秒。",
    "只上屏、不念的：Transformer 论文名、GPT-1 论文题目、GPT-2 的 15 亿参数、GPT-3“给几个例子就会”、RLHF 常追溯的 2017 年论文、o1 预览版、"
    "R1-Zero 型号名、正式版 R1 的冷启动 SFT、Function Calling / Computer Use 英文名、MCP、2025 年的编程智能体、METR 英文全称和翻倍周期、"
    "OpenAI 章程完整译文、主持人给黄仁勋的标准、ARC 英文全称、ARC-AGI-3 名称、厂商适配框架的 99.9%、《Nature》评论、四条短板的人名出处。",
    "没用的（存疑、过时或偏题）：Altman 的几次说法、Chollet 在 X 上的 66%、媒体里的 98.6%、黄仁勋 2026-09-06 在 X 上的“AGI has arrived”、"
    "微软—OpenAI 2025-10 协议里的专家小组条款（2026-04 协议修改后官方公告未再提及）、缩放定律、Constitutional AI。",
    "人名念中文译名（布罗克曼、黄仁勋、肖莱、杨立昆），英文原名只上屏；引语卡只用文字，不放真人照片。",
    "画面：品牌只用文字，不画 logo；聊天气泡、新闻标题卡、桌面、终端、图表一律标“示意”，不用录屏和真实截图，不写真实媒体名。",
]

PRONUNCIATION = [
    "大写缩写逐字母读：AI → A I，AGI → A G I，GPT → G P T，SFT → S F T，RLHF → R L H F。",
    "METR 写成“M E T R”、ARC 写成“A R C”（按逐字母规则）。这两家机构自己读作 meter、arc；如果想按机构读法，把 TTS 改成“Meter”“Arc”。",
    "品牌拆词：OpenAI → Open A I，ChatGPT → Chat G P T，InstructGPT → Instruct G P T，DeepSeek → Deep Seek，DeepMind → Deep Mind。",
    "型号：GPT-1 / GPT-2 / GPT-3 / GPT-4 → “G P T 1 / 2 / 3 / 4”，GPT-6 Astra → “G P T 6 Astra”；o1 → “O 1”（字母 O，念成“零一”就重生成），"
    "R1 → “R 1”。R1-Zero、ARC-AGI-3 本版只上屏，不念。试听时重点听有没有读成“杠”或“零”。",
    "英文全称重点听：Generative Pre trained Transformer、Artificial General Intelligence。含糊就在全称前后加逗号，或把这一段单独重生成。",
    "照英文读：token、Transformer、Google、Anthropic、Claude、Agent、Chain of Thought、Astra、Prize。",
    "参数和百分比在 TTS 里写成中文（一点一七亿、一千七百五十亿、十三亿、百分之十五点六、百分之七十一、百分之一、百分之六十二点七）；"
    "“0到5级”“1级”写成“零到五级”“一级”；年份、月日用阿拉伯数字。",
    "“词元”“初现”前后有逗号停顿，保持；“肖莱”“杨立昆”“布罗克曼”“黄仁勋”是人名，听一下声调。",
]

CHECKLIST = [
    # 查询日期均为 2026-09-27；“R1 x.x / R2 x.x”指 _staging/ep02 两份查证材料的条目号；“审校”指 review_fact.md。
    # 标“较确定”的出片前用浏览器打开原页再核一次（openai.com 对抓取返回 403）。
    "预训练目标＝根据前文预测下一个 token：GPT-1 论文 §3.1 https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf"
    "（R1 1.6、2.2，已核实）。",
    "Transformer：Google 团队《Attention Is All You Need》，arXiv 2017-06-12，最初用于机器翻译（只上屏）：https://arxiv.org/abs/1706.03762（已核实）。",
    "GPT 全称 Generative Pre-trained Transformer：OpenAI 开发者文档“generative pre-trained transformers or \"GPT\" models”，"
    "https://developers.openai.com/api/docs/concepts（审校，已核实）；GPT-1 论文题目 Improving Language Understanding by Generative Pre-Training（2018）。",
    "参数量 GPT-1（2018-06）1.17 亿、GPT-2（2019）15 亿、GPT-3（2020-05）1750 亿，“GPT-1 到 GPT-3 只隔了两年”：GPT-2 论文表 2、"
    "https://arxiv.org/abs/2005.14165（已核实）；GPT-4 起官方不公布参数量 https://arxiv.org/abs/2303.08774（已核实，只上屏）。",
    "GPT-2 论文 §2 原句“Our speculation is that a language model with sufficient capacity will begin to learn to infer and perform the tasks "
    "demonstrated in natural language sequences in order to better predict them”，同节以翻译为例："
    "https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf（审校，已核实）。"
    "台词只说“推测”“模型够大时”“文本里演示的任务，比如翻译”，不说“语法、常识”。GPT-3 给几个例子就能做新任务、参数不变（只上屏）：https://arxiv.org/abs/2005.14165 摘要（已核实）。",
    "Claude 写押韵诗会先想好韵脚：Anthropic《Tracing the thoughts of a large language model》，2025-03-27，研究对象 Claude 3.5 Haiku，"
    "https://www.anthropic.com/research/tracing-thoughts-language-model（已核实）。",
    "“算不算理解，学界还在争”：2022 年 NLP 研究者调查，问题是“只靠文本训练的模型能否理解语言”，结果几乎对半分，https://arxiv.org/abs/2208.12852（已核实，画面角注按这个问法写）。",
    "SFT / RLHF 做法（人写示范回答做监督微调；人给回答排序 → 奖励模型 → 强化学习）；InstructGPT 有 13 亿、60 亿、1750 亿三个版本，"
    "最小的 13 亿版本输出也比 1750 亿 GPT-3 更受评估者偏好：https://arxiv.org/abs/2203.02155（2022-03-04，已核实）。"
    "现代 RLHF 常追溯到 Christiano 等 2017 年论文 https://arxiv.org/abs/1706.03741（只上屏，不说“最早”）。",
    "InstructGPT 博客 2022-01-27：https://openai.com/index/instruction-following/（较确定，403，出片前浏览器核对“2022 年 1 月”）。",
    "ChatGPT 2022-11-30 发布，“same methods as InstructGPT”、数据收集方式略有不同：https://openai.com/index/chatgpt/（较确定，403，出片前浏览器核对）。",
    "思维链提示：Google（Wei 等），arXiv 2022-01-28，https://arxiv.org/abs/2201.11903（已核实）。",
    "o1：2024-09-12 发布的是 o1-preview 和 o1-mini（画面写“o1（预览版）”），正式版 2024-12-05；用大规模强化学习训练模型用思维链思考："
    "https://openai.com/index/learning-to-reason-with-llms/ （403）、https://simonwillison.net/2024/Sep/12/openai-o1/（审校，已核实）。",
    "DeepSeek-R1：2025-01-20 发布、开源权重 https://www.deepseek.com/en/news/deepseek-r1/（已核实）。“几个月后”＝2024-09 → 2025-01，4 个月。"
    "R1-Zero 不做 SFT、规则奖励（准确性 + 格式）、AIME 2024 pass@1 15.6% → 71.0%、自发出现回头检查（aha moment）；正式版 R1 先做冷启动 SFT（只上屏）："
    "https://arxiv.org/abs/2501.12948v1 §1.1、§2.2（已核实）。画面写「AIME 2024 数学竞赛题」，不用中文译名。",
    "函数调用：2023-06-13（gpt-4-0613 / gpt-3.5-turbo-0613），模型返回函数名和 JSON 参数，由开发者程序执行："
    "https://openai.com/index/function-calling-and-other-api-updates/ （403）、https://simonwillison.net/2023/Jun/13/function-calling/（审校，已核实）。"
    "“比 o1 早了一年多”＝2023-06 → 2024-09，15 个月。",
    "电脑操作 Computer Use：2024-10-22 随升级版 Claude 3.5 Sonnet 公测，https://www.anthropic.com/news/3-5-models-and-computer-use（已核实）。"
    "“一年多以后”＝2023-06 → 2024-10，16 个月。MCP：2024-11-25，https://www.anthropic.com/news/model-context-protocol（已核实，只上屏）。",
    "编程智能体（只上屏）：Claude Code 2025-02-24 研究预览（较确定）、2025-05-22 正式发布（已核实）；Codex CLI 2025-04-16、Codex 云端 2025-05-16（较确定）（R1 5.6–5.9）。",
    "智能体的说法：能自己一步步调用工具、把任务做完的系统（审校建议，只调用一次工具不算）。",
    "METR 全称 Model Evaluation and Threat Research，研究型非营利机构：https://metr.org/about（已核实，只上屏；官网写明读作 meter）。",
    "METR 50% 任务时间跨度的定义：https://arxiv.org/abs/2503.14499、https://metr.org/time-horizons/ FAQ（已核实）。翻倍周期（只上屏）："
    "“约 7 个月（2019 起）”出自 2025-03 论文，“约 3 个月（2024 起，89 天）”出自 https://metr.org/blog/2026-1-29-time-horizon-1-1/ ，画面小字写这两个出处。",
    "METR 数值：GPT-4（2023-03）约 4 分钟（3.99 分钟）；Claude Opus 4.6（2026-02）约 12.0 小时；Claude Mythos Preview（2026-04）约 17.4 小时，METR 注明 16 小时以上测不准"
    "（台词只说“十几个小时”）；Mythos 80% 时间跨度 3.1 小时，是数据页最高（台词“约3小时”）。https://metr.org/time-horizons/ 、https://metr.org/assets/benchmark_results_1_1.yaml"
    "（已核实，数据页更新于 2026-05-08）。GPT-5.6 Sol（2026-06）METR 自己说不可靠，Opus 5.5 的 2026-09-22 报告没给时间跨度（审校）。出片前再看一次有没有新数据。",
    "METR 注意事项：时长是人类耗时、不代表 AI 连续工作时长；任务以软件工程 / 机器学习 / 网络安全为主；多数真实工作要和人打交道、成功标准无法自动打分："
    "https://metr.org/time-horizons/ FAQ（已核实）。",
    "AGI 全称 Artificial General Intelligence，通用人工智能；没有统一定义（布罗克曼本人也说“Everyone has a different definition of AGI”）（已核实）。",
    "OpenAI 章程（2018-04）“highly autonomous systems that outperform humans at most economically valuable work”：https://openai.com/charter/"
    "（403，原句经多方转述一致，审校确认）。台词只说“在大多数有经济价值的工作上超过人类”，画面补全“高度自主的系统”。出片前浏览器核对原句。",
    "Google DeepMind《Levels of AGI》：https://arxiv.org/abs/2311.02462（v1 2023-11-04；v5 表 1）0–5 级；1 级 Emerging（初现）＝等于或略好于没受过训练的人；"
    "ChatGPT 等 2023 年的聊天模型放在 1 级；4 级 v5 起叫 Exceptional（原名 Virtuoso），画面写“卓越”（已核实）。",
    "Chollet《On the Measure of Intelligence》2019-11-05：智能＝技能获取效率，同文提出 ARC（Abstraction and Reasoning Corpus）：https://arxiv.org/abs/1911.01547"
    "（已核实）。ARC Prize：“AGI is a system that can match the learning efficiency of humans”，https://arcprize.org/arc-agi（已核实）。",
    "GPT-6 Astra 2026-09-03 发布（3 日有限预览，4 日向付费用户开放）；布罗克曼（总裁、联合创始人）在闭门媒体简报上说“Welcome to the AGI era.”："
    "https://venturebeat.com/technology/welcome-to-the-agi-era-openai-launches-gpt-6-astra 、"
    "https://fortune.com/2026/09/03/openai-debuts-gpt-6-astra-computer-use-greg-brockman-says-start-of-agi/（审校，已核实）。",
    "OpenAI 没有正式宣布实现 AGI：发布页只称 Astra 为“most intelligent and aligned model”，https://openai.com/index/gpt-6-astra/（403，出片前浏览器核对）；"
    "Fortune 同日报道“did not formally declare”；https://www.techspot.com/news/113739-openai-welcomes-agi-era-gpt-6-astra-first.html（审校，已核实）。"
    "原先引用的 community.openai.com 帖子是社区用户发的，不再作为来源。",
    "黄仁勋：Lex Fridman 播客 #494（页面 2026-03-23），https://lexfridman.com/jensen-huang-transcript/ 。01:55:06 主持人提出标准“start, grow, and run a successful "
    "technology company that's worth more than a billion dollars”；01:56:31 黄仁勋答“I think it's now. I think we've achieved AGI.”，并补充“you didn't say forever”；"
    "同一段他说 10 万个这样的智能体造出英伟达的概率是 0%（审校，已核实）。台词“用的是主持人给的一个标准”。"
    "他 2026-09-06 在 X 上又发“AGI has arrived”（R2 2.1.7，较确定），本期不用。",
    "ARC-AGI-3：2026-03-25 发布，交互式、不给说明的像素小游戏，要自己摸索规则；发布时“Humans score 100%. Frontier AI scores 0.51%”："
    "https://arcprize.org/blog/arc-agi-3-launch（已核实）。台词说“第三代测试”，名称只上屏。",
    "GPT-6 Astra 在 ARC-AGI-3 Semi-Private：Standard harness 62.7%（约 2.6 万美元）；Provider Adapter harness 99.9%（约 1.9 万美元），"
    "这个框架在请求之间保留推理状态并压缩长对话，ARC Prize 说它的成绩应看作“模型加工具”的合并成绩："
    "https://arcprize.org/blog/astra（2026-09-27 WebFetch 打开核对，已核实）、https://arcprize.org/results/openai-gpt-6-astra 。画面两根柱并列。"
    "不用媒体里的 66% / 98.6%。",
    "ARC Prize 原话“While we believe Astra represents meaningful progress towards generalization, we are not claiming that it is AGI.”，"
    "理由之一是测试规则固定、目标封闭，不代表真实世界：https://arcprize.org/blog/astra（已核实）。台词译作“我们没说它就是AGI”，画面引语保留英文。"
    "ARC-AGI-3 页面另有“As long as there is a gap between AI and human learning, we do not have AGI”，所以台词写“也有人不认同”。",
    "“没有独立认证”：截至 2026-09-27 没有任何独立机构认证某个系统是 AGI。微软—OpenAI 2025-10-28 协议曾规定 OpenAI 宣布 AGI 须经独立专家小组核实，"
    "但 2026-04-27 修改协议后官方公告不再提 AGI 和专家小组：https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ 、"
    "https://blogs.microsoft.com/blog/2026/04/27/the-next-phase-of-the-microsoft-openai-partnership/（审校，已核实）。画面不写这条。",
    "《Nature》评论《Does AI already have human-level intelligence? The evidence is clear》（Chen、Belkin、Bergen、Danks，2026-02-04）认为已具备通用智能："
    "https://www.nature.com/articles/d41586-026-00285-6（审校，已核实，只上屏小字，标“有争议”）。",
    "“还差什么”四点的出处（画面小字）：持续学习 Hassabis 2026-02-18“kind of frozen”（较确定）、Karpathy 2025-10-17“You can't just tell them something and they'll remember it”（已核实）；"
    "可靠性 METR 80% 约 3 小时（已核实）、《国际 AI 安全报告 2026》2026-02-03“fabricating information”，说的是 AI 系统普遍问题（已核实）；"
    "开放的真实任务 METR FAQ（已核实）；物理世界 LeCun“they lack a model of the world”，MIT Technology Review 2026-01-22（已核实），台词意译为“不懂真实世界怎么运转”。",
]

SCENES = [
    dict(id="S01", title="开场白", char="从左侧走入，停在左下角，挥手问好", rows=[
        ("gap", 1.2, "【动作：走动】背景淡入；左上角「原LAI如此 #02」"),
        ("say", "大家好，我是鲸鱼娘。今天给大家介绍AI从学会说人话到AGI的这条路。",
                "大家好，我是鲸鱼娘。今天给大家介绍，A I 从学会说人话，到 A G I 的这条路。",
                "【动作：挥手】画面中央大字「AI：从学会说人话，到 AGI？」（问号橙色）；下方小字「AGI：通用人工智能」"),
        ("gap", 0.4, "标题大字缩小，淡出"),
    ]),
    dict(id="S02", title="三个疑问", char="说话；“常有人说”侧耳，三个疑问依次数一、数二、数三", rows=[
        ("say", "常有人说：“AI不就是文字接龙吗？”一句话，就把AI这些年的努力全否定了。",
                "常有人说。A I 不就是文字接龙吗？一句话，就把 A I 这些年的努力，全否定了。",
                "【动作：侧耳】右侧一个聊天气泡（示意，虚构对话，无头像、无 logo）：「AI 不就是文字接龙吗？」"),
        ("say", "也有新闻说，AGI已经来了。",
                "也有新闻说，A G I 已经来了。",
                "气泡下方叠一张新闻标题卡（示意，不写真实媒体名、不用 logo）：「AGI 已经来了？」"),
        ("say", "你可能会有三个疑问：",
                "你可能会有三个疑问。",
                "气泡和标题卡缩小移走，右侧出现标题「你可能也想问」"),
        ("say", "第一，AI真的只是文字接龙吗？",
                "第一，A I 真的只是文字接龙吗？",
                "【动作：数一@第一】疑问卡 ①「AI只是文字接龙吗？」弹出（“嗒”）；三张卡的文字都取 episode.json questions"),
        ("say", "第二，AI是怎么一步步变强的？",
                "第二，A I 是怎么一步步变强的？",
                "【动作：数二@第二】疑问卡 ②「AI怎么一步步变强？」弹出（“嗒”）"),
        ("say", "第三，AGI是什么，现在实现了吗？",
                "第三，A G I 是什么，现在实现了吗？",
                "【动作：数三@第三】疑问卡 ③「AGI是什么，实现了吗？」弹出（“嗒”）"),
        ("say", "这期视频，就把这三个问题讲清楚。",
                "这期视频，就把这三个问题讲清楚。",
                "三张疑问卡飞到右上角，成为本期目录"),
        ("gap", 0.6, "转场：目录 ① 高亮"),
    ]),
    dict(id="S03", title="一、学会接龙", char="说话；参数图指这里，“对了一半”重点，押韵诗句尾吃惊，“学界还在争”摊手", rows=[
        ("say", "先说第一个问题。“文字接龙”说的，是AI变强四个阶段里的第一个：预训练。",
                "先说第一个问题。文字接龙说的，是 A I 变强四个阶段里的第一个，预训练。",
                "章节标题「一、学会接龙」；右侧出现色带图（示意，全片复用）：四条横向色带「接龙 / 对话 / 思考 / 做事」（《孤独摇滚！》四色），横轴 2017–2026，每条从起始年份向右延伸到 2026，互相重叠；说到“四个阶段”时四条一起闪一下，然后第 1 条高亮，其余变灰"),
        ("say", "预训练，就是让模型读海量文本。它要根据前文，预测下一个token，中文叫词元。",
                "预训练，就是让模型读海量文本。它要根据前文，预测下一个 token，中文叫词元。",
                "一行字「今天天气很」→ 右边三个候选「好 / 热 / 冷」，各带一条概率条（示意）；说到“词元”时，这行字切成几段彩色小块，标「token（词元）」"),
        ("say", "模型结构，用的是2017年Google提出的Transformer。",
                "模型结构，用的是2017年 Google 提出的 Transformer。",
                "时间轴卡片 2017「Transformer」，小字「Google《Attention Is All You Need》· 最初用于机器翻译」"),
        ("say", "OpenAI用它做出了GPT：生成式预训练Transformer。",
                "Open A I 用它做出了 G P T，生成式预训练 Transformer。",
                "「GPT」三个大字母，T 连线到 Transformer 卡；下方中文「生成式 / 预训练 / Transformer」"),
        ("say", "英文全称是Generative Pre-trained Transformer。",
                "英文全称是，Generative Pre trained Transformer。",
                "三个英文单词依次出现，首字母 G、P、T 高亮；小字「GPT-1 论文：Improving Language Understanding by Generative Pre-Training，2018」"),
        ("say", "GPT-1到GPT-3只隔了两年，参数从1.17亿涨到了1750亿。",
                "G P T 1 到 G P T 3，只隔了两年，参数从一点一七亿，涨到了一千七百五十亿。",
                "【动作：指这里】柱状图（对数刻度，示意）：GPT-1 1.17 亿（2018）/ GPT-2 15 亿（2019）/ GPT-3 1750 亿（2020）；角注「参数：模型里靠训练调出来的数值」「GPT-4 起官方不公布参数量」"),
        ("say", "“文字接龙”这个说法，对了一半：",
                "文字接龙这个说法，对了一半。",
                "【动作：重点】柱状图收起；大字「文字接龙：对了一半」，下面两栏「对的一半」｜「另一半」"),
        ("say", "训练目标确实是预测下一个词，回答也是一个词一个词生成的。",
                "训练目标，确实是预测下一个词，回答，也是一个词一个词生成的。",
                "左栏两条逐条出现：① 预训练目标＝预测下一个 token ② 回答逐个 token 生成；小字「这里的“词”指 token」；右下角出现「训练目标」小清单（示意，全片保留）第 ① 行「预测下一个词」"),
        ("say", "但GPT-2论文推测：模型够大时，为了猜准，会顺带学会文本里演示的任务，比如翻译。",
                "但 G P T 2 论文推测，模型够大时，为了猜准，会顺带学会文本里演示的任务，比如翻译。",
                "右栏 ①「为了猜准，会学会文本里演示的任务（翻译、问答…）」（小字：GPT-2 论文的推测，2019）；下方小输入框（示意）：「苹果 → apple / 香蕉 → banana / 葡萄 → ？」→「grape」，标「GPT-3（2020）· 给几个例子就会 · 参数不变」"),
        ("say", "Anthropic还发现，Claude写押韵诗时，会先想好韵脚，再写这一行。",
                "Anthropic 还发现，Claude 写押韵诗时，会先想好韵脚，再写这一行。",
                "【动作：吃惊@末尾】右栏 ②：一行英文诗示意，行尾的韵脚词先亮起，前面的词再逐个出现；小字「Anthropic（Claude 的开发公司）可解释性研究，2025-03-27 · 研究对象 Claude 3.5 Haiku」"),
        ("say", "一次输出一个词，不等于只想着下一个词。至于算不算“理解”，学界还在争。",
                "一次输出一个词，不等于只想着下一个词。至于算不算理解，学界还在争。",
                "【动作：摊手】右栏 ③「逐个输出 ≠ 只想下一个」；角注「“只靠文本训练的模型能否理解语言”：2022 年自然语言处理（NLP）研究者调查几乎对半分」"),
        ("say", "接龙只是第一个阶段。往后，训练目标还多了两条。",
                "接龙只是第一个阶段。往后，训练目标还多了两条。",
                "色带图后三条依次闪一下；「训练目标」清单下方出现两个空行「② ？」「③ ？」"),
        ("gap", 0.6, "目录 ① 打勾；目录 ② 高亮"),
    ]),
    dict(id="S04", title="二、学会对话", char="说话；两步训练抬手，13 亿胜 1750 亿句尾吃惊", rows=[
        ("say", "第二个问题：AI是怎么一步步变强的。第二阶段，学会对话：听懂指令，按要求回答。",
                "第二个问题，A I 是怎么一步步变强的。第二阶段，学会对话。听懂指令，按要求回答。",
                "章节标题「二、学会对话」；色带图第 2 条（2022 起）高亮"),
        ("say", "靠两步训练。第一步，监督微调，简称SFT。",
                "靠两步训练。第一步，监督微调，简称 S F T。",
                "【动作：抬手】流程卡「两步训练」；框 ①「SFT · Supervised Fine-Tuning · 监督微调」（英文全称只上屏，首字母 S、F、T 高亮）"),
        ("say", "人写出标准回答，模型照着学。",
                "人写出标准回答，模型照着学。",
                "框 ① 内：一张「人写的标准回答」→ 模型"),
        ("say", "第二步，基于人类反馈的强化学习，简称RLHF。",
                "第二步，基于人类反馈的强化学习，简称 R L H F。",
                "框 ②「RLHF · Reinforcement Learning from Human Feedback · 基于人类反馈的强化学习」（英文全称只上屏，首字母 R、L、H、F 高亮）"),
        ("say", "人给回答排序，训练出一个打分模型，再让AI朝高分去学。",
                "人给回答排序，训练出一个打分模型，再让 A I 朝高分去学。",
                "框 ② 内动画：回答 A / B / C 被拖动排序 →「打分模型」→ 箭头回到 AI；角注「现代 RLHF 常追溯到 2017 年论文（Christiano 等）」"),
        ("say", "2022年1月，OpenAI用这套方法，做出了InstructGPT。",
                "2022年1月，Open A I 用这套方法，做出了 Instruct G P T。",
                "时间轴卡片 2022-01「InstructGPT」"),
        ("say", "人工评估里，它最小的13亿参数版本，都比1750亿参数的GPT-3更受欢迎。",
                "人工评估里，它最小的十三亿参数版本，都比一千七百五十亿参数的 G P T 3，更受欢迎。",
                "【动作：吃惊@末尾】对比卡：左「InstructGPT（最小版）13 亿」小方块，右「GPT-3 1750 亿」大方块，左边亮起「评估者更喜欢」；小字「InstructGPT 论文，2022」"),
        ("say", "同年11月30日，ChatGPT发布，也是这么训练的。",
                "同年11月30日，Chat G P T 发布，也是这么训练的。",
                "时间轴卡片 2022-11-30「ChatGPT 发布」（文字，不用 logo）；小字「方法同 InstructGPT，数据改成对话形式」"),
        ("say", "从这个阶段开始，训练目标多了一条：人更喜欢哪个回答。",
                "从这个阶段开始，训练目标多了一条，人更喜欢哪个回答。",
                "「训练目标」清单第 ② 行亮起「人更喜欢哪个回答」（橙色）"),
        ("gap", 0.5, "色带图第 3 条亮起"),
    ]),
    dict(id="S05", title="三、学会思考", char="说话；开场思考，说到 DeepSeek 开源 R1 手放胸前，“回头检查”吃惊", rows=[
        ("say", "第三阶段，学会思考：先写出推理步骤，再给答案。",
                "第三阶段，学会思考。先写出推理步骤，再给答案。",
                "【动作：思考】章节标题「三、学会思考」；一张卡「问题 → 步骤 1 → 步骤 2 → 答案」"),
        ("say", "2022年1月，Google提出了思维链提示。",
                "2022年1月，Google 提出了思维链提示。",
                "时间轴卡片 2022-01「思维链提示 Chain-of-Thought（CoT）」（英文名只上屏）"),
        ("say", "例题里写出步骤，模型就会跟着写。这还只是提问技巧。",
                "例题里写出步骤，模型就会跟着写。这还只是提问技巧。",
                "提示框示意：一道带解题步骤的例题 + 一道新题，模型输出也先列步骤；角标「提示技巧 · 模型没变」"),
        ("say", "2024年9月，OpenAI发布o1。它用强化学习，专门训练模型先想再答。",
                "2024年9月，Open A I 发布 O 1。它用强化学习，专门训练模型先想再答。",
                "时间轴卡片「2024-09-12 o1（预览版）」，角标「训练方法 · 强化学习」"),
        ("say", "几个月后，DeepSeek开源了R1。",
                "几个月后，Deep Seek 开源了 R 1。",
                "【动作：手放胸前】时间轴卡片 2025-01-20「DeepSeek-R1 · 开源权重」"),
        ("say", "它的试验版跳过监督微调，直接做强化学习。奖励只看答案对不对、格式对不对。",
                "它的试验版，跳过监督微调，直接做强化学习。奖励只看，答案对不对，格式对不对。",
                "流程卡标题「R1-Zero（试验版）」：「基座模型 → 强化学习」（SFT 一格划掉）；奖励两格「✓ 答案对不对」「✓ 格式对不对」；角注「正式版 R1：先用少量冷启动数据做 SFT，再强化学习」"),
        ("say", "训练中，它做数学竞赛题，一次做对的比例从15.6%升到了71%。",
                "训练中，它做数学竞赛题，一次做对的比例，从百分之十五点六，升到了百分之七十一。",
                "折线图（示意）：15.6% → 71.0%，标「AIME 2024 数学竞赛题 · R1-Zero 论文数据」"),
        ("say", "它还自己学会了回头检查。",
                "它还自己学会了回头检查。",
                "【动作：吃惊】折线旁弹出思考气泡「Wait… 再检查一下」（示意），角注「论文称 aha moment」"),
        ("say", "这个阶段，训练目标又多了一条：答案对不对。",
                "这个阶段，训练目标又多了一条，答案对不对。",
                "「训练目标」清单第 ③ 行亮起「答案对不对」（橙色）"),
        ("gap", 0.5, "色带图第 4 条亮起"),
    ]),
    dict(id="S06", title="四、学会做事", char="说话；函数调用抬手，“能做多长的任务”思考，注意事项摇头+认真，“回到那句话”句尾叉腰", rows=[
        ("say", "第四阶段，学会做事：一步步调用工具、操作电脑，把任务做完。这样的AI叫智能体。",
                "第四阶段，学会做事。一步步调用工具，操作电脑，把任务做完。这样的 A I 叫智能体。",
                "章节标题「四、学会做事」；标签「智能体 Agent」（英文只上屏），下方一条小流程「目标 → 调工具 → 看结果 → 再调工具 → 完成」（示意）"),
        ("say", "2023年6月，OpenAI上线了函数调用。",
                "2023年6月，Open A I 上线了函数调用。",
                "【动作：抬手】时间轴卡片 2023-06-13「函数调用 Function Calling」"),
        ("say", "模型说出要调哪个函数、传什么数据，由程序去执行。",
                "模型说出要调哪个函数，传什么数据，由程序去执行。",
                "流程图：模型 →「函数名 + 要传的数据（JSON，示意）」→ 程序执行 →「结果」→ 回到模型"),
        ("say", "一年多以后，Anthropic推出电脑操作：模型看屏幕、点鼠标、打字。",
                "一年多以后，Anthropic 推出电脑操作。模型看屏幕，点鼠标，打字。",
                "屏幕画面框（虚构桌面，示意，不用真实截图）→ 光标移动 → 点击 → 输入框出现文字；时间轴卡片 2024-10-22「电脑操作 Computer Use」"),
        ("say", "那它能做多长的任务？评测机构METR是这样算的：",
                "那它能做多长的任务？评测机构 M E T R，是这样算的。",
                "【动作：思考】标题卡「能做多长的任务？」；小字「METR：Model Evaluation and Threat Research（模型评估与威胁研究）· 非营利研究机构」"),
        ("say", "找出AI有一半把握做完的任务，再看人类专家要做多久。",
                "找出 A I 有一半把握做完的任务，再看人类专家要做多久。",
                "定义卡「50% 任务时间跨度」两步逐条出现：① AI 成功率 50% 的任务 → ② 人类专家完成它要多久"),
        ("say", "2023年的GPT-4，大约4分钟。2026年测到的最好成绩，是十几个小时。",
                "2023年的 G P T 4，大约四分钟。2026年测到的最好成绩，是十几个小时。",
                "折线图（对数纵轴，示意）：「GPT-4 约 4 分钟（2023）」→「2026 年测到最好：十几小时」，16 小时以上画成虚线框、标「测不准」；两段斜率标注「约 7 个月翻倍（2019 起）」「约 3 个月翻倍（2024 起）」；小字「数据：METR 2026-05 · 翻倍周期：METR 2025-03 论文 / 2026-01 更新」"),
        ("say", "注意，这是人类要花的时间，不代表AI能连续干这么久。而且主要是软件类任务。",
                "注意，这是人类要花的时间，不代表 A I 能连续干这么久。而且，主要是软件类任务。",
                "【动作：摇头+认真】三条注意事项逐条出现，前面各一个橙色「!」：「人类耗时 ≠ AI 连续工作时长」「50% 成功率」「以软件类任务为主」"),
        ("say", "函数调用比o1还早了一年多，所以这几个阶段是交叠着往前走的。",
                "函数调用，比 O 1 还早了一年多，所以这几个阶段，是交叠着往前走的。",
                "色带图放大到画面中央：四条色带全部亮起，重叠区域加斜线；两处标注「思维链提示 2022-01 早于 ChatGPT 2022-11」「函数调用 2023-06 早于 o1 2024-09」；“做事”色带上两个小标记（只上屏）「2024-11 MCP 工具接入开放标准」「2025 编程智能体陆续发布」"),
        ("say", "回到那句话：“文字接龙”说的，只是预训练的目标和输出的方式。",
                "回到那句话。文字接龙说的，只是预训练的目标，和输出的方式。",
                "【动作：叉腰@末尾】开场的聊天气泡回来，「文字接龙」四个字只罩住第一条色带；「训练目标」清单 ①②③ 并列"),
        ("gap", 0.8, "目录 ② 打勾；目录 ③ 高亮"),
    ]),
    dict(id="S07", title="五、AGI 到了吗", char="说话；三种定义依次数一、数二、数三，“个人表态”摇头+认真，62.7% 句尾吃惊", rows=[
        ("say", "最后一个问题：AGI是什么。全称Artificial General Intelligence。",
                "最后一个问题，A G I 是什么。全称，Artificial General Intelligence。",
                "章节标题「五、AGI 到了吗」；三个英文单词依次出现，首字母 A、G、I 高亮"),
        ("say", "中文叫通用人工智能。它没有统一定义，常见的有三种。",
                "中文叫通用人工智能。它没有统一定义，常见的有三种。",
                "下方中文「通用人工智能」；三张空卡「定义 ① ② ③」"),
        ("say", "第一种看工作：OpenAI章程说，AGI要在大多数有经济价值的工作上超过人类。",
                "第一种看工作，Open A I 章程说，A G I 要在大多数有经济价值的工作上，超过人类。",
                "【动作：数一@第一种】卡 ①「看工作」：OpenAI 章程（2018）译文「在大多数有经济价值的工作上胜过人类的高度自主系统」，英文原句小字 highly autonomous systems that outperform humans at most economically valuable work"),
        ("say", "第二种分等级。Google DeepMind给AGI分了0到5级。",
                "第二种分等级。Google Deep Mind 给 A G I 分了零到五级。",
                "【动作：数二@第二种】卡 ②「分等级」：0–5 级阶梯（0 无 AI / 1 初现 / 2 胜任 / 3 专家 / 4 卓越 / 5 超人）；小字「Google DeepMind《Levels of AGI》，2023-11」"),
        ("say", "按这个分法，2023年的ChatGPT这类模型只到1级“初现”：和没受过训练的人差不多。",
                "按这个分法，2023年的 Chat G P T 这类模型，只到一级，初现，和没受过训练的人差不多。",
                "阶梯第 1 级亮起，标「2023 年的聊天模型」；旁注「初现 Emerging：等于或略好于没受过训练的人」"),
        ("say", "第三种看学习效率。肖莱2019年提出：智能，就是学会新技能有多快。",
                "第三种看学习效率。肖莱2019年提出，智能，就是学会新技能有多快。",
                "【动作：数三@第三种】卡 ③「看学习效率」：François Chollet（肖莱，AI 研究者）2019《On the Measure of Intelligence》，「智能＝技能获取效率」"),
        ("say", "那现在实现了吗？有人说到了。",
                "那现在实现了吗？有人说到了。",
                "三张卡缩到右侧边栏；右侧日期条「截至 2026-09」；左栏标题「说到了」"),
        ("say", "9月3日，OpenAI发布GPT-6 Astra，总裁布罗克曼说：“欢迎来到AGI时代。”",
                "9月3日，Open A I 发布 G P T 6 Astra。总裁布罗克曼说，欢迎来到 A G I 时代。",
                "引语卡（只用文字，不放真人照片）「Welcome to the AGI era」— Greg Brockman（OpenAI 总裁），2026-09-03 媒体简报；小字「他也说：每个人对 AGI 的定义都不同」"),
        ("say", "但这是个人表态，OpenAI没有正式宣布。",
                "但这是个人表态，Open A I 没有正式宣布。",
                "【动作：摇头+认真】引语卡加标签「个人表态」和一行「OpenAI 官方：未正式宣布实现 AGI」"),
        ("say", "英伟达的黄仁勋也这么说过，用的是主持人给的标准。",
                "英伟达的黄仁勋也这么说过，用的是主持人给的标准。",
                "第二张引语卡（只用文字，不放真人照片）「I think we've achieved AGI」— 黄仁勋（英伟达 CEO），2026-03 播客；标签「个人表态」；卡底「主持人提的标准：AI 能创办并运营一家市值超 10 亿美元的公司」，小字「黄仁勋补充：不必长久」"),
        ("say", "也有人不认同。评测组织ARC Prize，就是按第三种定义出题的。",
                "也有人不认同。评测组织 A R C Prize，就是按第三种定义出题的。",
                "右栏标题「不认同」；边栏定义卡 ③ 闪一下；小字「ARC = Abstraction and Reasoning Corpus（抽象与推理语料库），肖莱 2019 年提出」"),
        ("say", "他们3月出了第三代测试：没有说明的新游戏，要自己摸索规则。",
                "他们3月出了第三代测试。没有说明的新游戏，要自己摸索规则。",
                "测试名卡「ARC-AGI-3 · 2026-03」；像素小游戏网格示意（虚构，不用真实题目），角上问号「规则？」"),
        ("say", "刚发布时，前沿AI的得分不到1%。",
                "刚发布时，前沿 A I 的得分，不到百分之一。",
                "柱状对比（示意）：「2026-03 前沿 AI < 1%」「人类 100%」"),
        ("say", "9月，Astra用标准测法做到了62.7%。",
                "9月，Astra 用标准测法，做到了百分之六十二点七。",
                "【动作：吃惊@末尾】第三根柱子升起「2026-09 GPT-6 Astra 62.7%（标准测试框架）」；旁边一根浅色柱「厂商适配框架 99.9%」，小字「ARC Prize：适配框架保留推理状态，成绩算“模型 + 工具”」「ARC Prize 官方数据」"),
        ("say", "但ARC Prize自己说：“我们没说它就是AGI。”",
                "但 A R C Prize 自己说，我们没说它就是 A G I。",
                "引语卡「we are not claiming that it is AGI」— ARC Prize，2026-09-03；小字「理由之一：测试规则固定、目标封闭，不代表真实世界」"),
        ("say", "截至2026年9月，实现AGI这件事：没有哪家公司正式宣布，没有独立认证，也没有共识。",
                "截至2026年9月，实现 A G I 这件事，没有哪家公司正式宣布，没有独立认证，也没有共识。",
                "结论卡三格依次出现：「正式宣布 ✕」「独立认证 ✕」「共识 ✕」；小字「也有学者认为已具备通用智能（《Nature》评论，2026-02），有争议」"),
        ("gap", 0.5, "结论卡停留，目录 ③ 保持高亮"),
    ]),
    dict(id="S08", title="六、还差什么", char="说话；“第一，持续学习”抬手，最后一句句尾叉腰", rows=[
        ("say", "那还差什么？常被提到的有四点。",
                "那还差什么？常被提到的有四点。",
                "章节标题「六、还差什么」；要点卡四个空格 ①②③④，角标「观点 · 均有出处」"),
        ("say", "第一，持续学习。模型训练完，参数就固定了，用的时候学到的东西留不下来。",
                "第一，持续学习。模型训练完，参数就固定了，用的时候学到的东西，留不下来。",
                "【动作：抬手】① 持续学习；小字「Demis Hassabis（Google DeepMind CEO）2026-02 · Andrej Karpathy 2025-10」"),
        ("say", "第二，可靠性。按十次做对八次算，测过的最好模型，只能做人类约3小时的任务。",
                "第二，可靠性。按十次做对八次算，测过的最好模型，只能做人类约三小时的任务。",
                "② 可靠性；小条形对比（人类耗时）「50% 把握：十几小时」「80% 把握：约 3 小时」；小字「METR 2026-05」"),
        ("say", "而且，模型还会编造信息。",
                "而且，模型还会编造信息。",
                "② 下加一行「会编造信息」；小字「《国际 AI 安全报告 2026》」"),
        ("say", "第三，开放的真实任务。实际工作比测试题乱，也没有标准答案，AI做得更差。",
                "第三，开放的真实任务。实际工作比测试题乱，也没有标准答案，A I 做得更差。",
                "③ 开放的真实任务；小字「METR 时间跨度页 FAQ」"),
        ("say", "第四，物理世界。杨立昆认为，只学文字的模型，不懂真实世界怎么运转。",
                "第四，物理世界。杨立昆认为，只学文字的模型，不懂真实世界怎么运转。",
                "④ 物理世界；小字「Yann LeCun（杨立昆）2026-01 · 原话：缺少世界模型（world model）」"),
        ("say", "AGI到没到，要看用哪个定义。能确定的是：AI能完成的任务越来越长。",
                "A G I 到没到，要看用哪个定义。能确定的是，A I 能完成的任务越来越长。",
                "【动作：叉腰@末尾】四格要点同时可见；上方一条细箭头「任务越来越长 ↑」"),
        ("gap", 0.5, "目录 ③ 打勾"),
    ]),
    dict(id="S09", title="总结", char="说话；“对了一半”句尾竖拇指，最后一句句尾好耶（拉炮）", rows=[
        ("say", "最后总结一下。",
                "最后总结一下。",
                "总结卡标题「本期总结」"),
        ("say", "第一，预训练确实是在预测下一个词，但不只是接龙。",
                "第一，预训练确实是在预测下一个词，但不只是接龙。",
                "总结卡 ①「预训练＝预测下一个词，但不只想下一个词」"),
        ("say", "第二，接龙之后又加了三个阶段：人的反馈教它对话，答案对错教它思考，工具让它能做事。",
                "第二，接龙之后又加了三个阶段。人的反馈教它对话，答案对错教它思考，工具让它能做事。",
                "总结卡 ②「对话 ← 人的反馈｜思考 ← 答案对错｜做事 ← 工具」，旁边缩小版色带图和「训练目标」清单"),
        ("say", "第三，AGI没有统一定义。到2026年9月，没有公司正式宣布实现，也没有共识。",
                "第三，A G I 没有统一定义。到2026年9月，没有公司正式宣布实现，也没有共识。",
                "总结卡 ③「AGI：没有统一定义；截至 2026-09 无正式宣布、无共识」（三条同时可见，可截图）"),
        ("say", "下次再听到“AI不就是文字接龙”，你可以说：对了一半。",
                "下次再听到，A I 不就是文字接龙，你可以说，对了一半。",
                "【动作：竖拇指@末尾】开头那个聊天气泡再次出现，下面多了一条回复「对了一半。」"),
        ("say", "我是鲸鱼娘，我们下期见。",
                "我是鲸鱼娘，我们下期见。",
                "【动作：好耶@末尾】右下角「原LAI如此」"),
        ("gap", 0.5, "淡出到片尾"),
    ]),
]
