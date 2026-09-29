# 第 3 期「Jev 模型是什么？和 LLM 有什么区别？」台本事实审校

- 审校对象：`第03期_Jev模型是什么/台本/script_data.py`，段号按 `台本/台本.md`（S03-12 这种）。台词和画面说明都审了。
- 查询日期：全部是 **2026-09-28**。
- 做法：所有一手页面本轮都重新打开，没有只看 `research_web.md`。
  - 官网首页：FAQ 的回答是折叠内容，静态 HTML 里没有。本轮在浏览器里展开核对，并对照了站点脚本里的原文。
  - 其他官方页面：博客；开发者文档（`llms-full.txt` 全文，外加单页）；评测站（总览页和 4 个工作流分页）。
  - 官方 X：x.com 要登录，改用公共接口 api.fxtwitter.com 读原帖全文和 UTC 时间，再用 syndication.twitter.com 的时间线确认 9/27 之后没有新帖。
  - 第三方和其他：Hacker News（官方 API）、arXiv、Towards Data Science、PriorBench 的 GitHub、Simon Willison 的博客、四篇公众号原文、维基百科、GitHub 和 Hugging Face。
- 结论：**❌ 0 条；⚠️ 9 条（7 条要改台词，2 条只改画面）；另建议补 2 句。**
  - 数字、日期、价格、评测数据、第三方测试数字全部对得上。
  - 问题集中在三类：措辞；出处标注；“官方到底怎么说的”。
  - 另有几条 CHECKLIST 里的出处说明需要更新，见 ⚠️ 部分最后。

---

## 一、❌ 错误

没有发现错误的数字、日期或事实。

---

## 二、⚠️ 需要改措辞

按优先级排：高 → 中 → 低。

### ⚠️-1　S03-13（台词）｜优先级：高

- **原文**：「这个说法，出自卡尼曼的《思考，快与慢》。」
- **问题**：“系统 1 / 系统 2”这对叫法不是卡尼曼首创。
  - 最早是心理学家 Keith Stanovich 和 Richard West 在 2000 年提出的。卡尼曼在书里自己写明，他沿用的是这两人的术语；他 2011 年的书让这个说法出了名。
  - TypeSafe 自己的措辞也很小心：博客 FAQ 说名字“受这本书启发”；文档 System One 页说这是“卡尼曼推广（popularized）的概念”。
  - 说“出自”，观众会以为是卡尼曼发明的。这是常见误解。
- **依据**（2026-09-28 查询）：
  - 官方博客 FAQ「Where do the names … come from?」：https://typesafe.ai/blog/introducing-system-one-models-and-jev
  - 文档 System One 页的 Note：https://docs.typesafe.ai/concepts/system-one
  - 《思考，快与慢》第 1 章节选（Scientific American 刊载，书中说明术语来自 Stanovich 和 West）：https://www.scientificamerican.com/article/kahneman-excerpt-thinking-fast-and-slow/
  - 维基百科 Dual process theory：https://en.wikipedia.org/wiki/Dual_process_theory
- **建议改成**：
  - 字幕：「官方说，这个名字的灵感来自卡尼曼的《思考，快与慢》。」
  - TTS：「官方说，这个名字的灵感，来自卡尼曼的，《思考，快与慢》。」
  - 画面（可选小字）：「“系统一 / 系统二”的叫法最早由心理学家 Stanovich 和 West 提出，这本书让它出了名」

### ⚠️-2　S04-39（台词 + 画面）｜优先级：高

- **原文**：
  - 台词：「官方测了四类工作流：Jev和GPT-5.6 Terra准确度差不多，速度快二十多倍，成本低七十多倍。」
  - 画面：「一致率 67.8% vs 67.9%」「每例用时 0.4 秒 vs 10.1 秒」「每例成本 $0.0004 vs $0.0304」，另有小字。
- **数字核对：✅ 全对**。评测站今天的数据没变。
  - Jev：67.8%、$0.0004、0.4 秒。terra：67.9%、$0.0304、10.1 秒。最高是 sol 的 74.1%。
  - 参考答案是 GPT-6 Astra 和 Claude Fable 5.1（都开高思考档）答案的平均；四个工作流等权平均。
  - 倍数：10.1 ÷ 0.4 ≈ 25；0.0304 ÷ 0.0004 = 76。按页面数字，“二十多倍”“七十多倍”都成立。
  - 评测站只写“terra”，没写全名。OpenAI 的 GPT-5.6 分 Sol / Terra / Luna 三档，博客的并排演示用的也是 GPT-5.6 Terra，所以认定为 GPT-5.6 Terra 是合理的。
- **问题**：
  1. **“成本低七十多倍”**：按中文编辑的通行做法，减少一般不用倍数表示，应改成“只有它的七十几分之一”。
  2. **精度**：Jev 的 $0.0004 是四舍五入后的数，只有一位有效数字。
     - 它由四个工作流平均而来，分别是 $0.0001、$0.0003、$0.0011、$0.0001。
     - 所以严格算，倍数在约 68–87 倍之间。只能说“七十几”这种约数，任何地方都别写成“76 倍”。
     - 速度这边，四个工作流是 0.3 / 0.5 / 0.5 / 0.4 秒，怎么算都是二十几倍，这个说法稳。
  3. **口径不一致**：台词说“准确度”，画面说“一致率”。
     - 评测站自己用的词是 accuracy，但判对错的标准是两个大模型答案的平均，不是人工标准答案。
     - 建议两处统一，并把“标准是什么”写在横条上。
  4. **漏了官方自己的限定**：博客“Workflow evals”一节写明，被比较的大模型都套了 TypeSafe 自己的适配器，被约束成输出结构化决策；官方也说这样往往更慢、更贵。这会把倍数往对 Jev 有利的方向推，值得写进小字。
  5. **（可选）平均差不多，分开看差别很大**：
     - 发票处理（要核对账单、订单和到货）：Jev 61.8%，Terra 74.7%，差 13 个百分点。这正好呼应 S05-50 的“算数交给代码”。
     - 安全告警反过来：Jev 61.7%，Terra 51.2%。
- **依据**（2026-09-28 查询）：
  - 评测站：https://evals.typesafe.ai/ 及分页 https://evals.typesafe.ai/invoice_processing.html 、https://evals.typesafe.ai/security_incidents.html
  - 官方博客「Workflow evals」一节：https://typesafe.ai/blog/introducing-system-one-models-and-jev
  - GPT-5.6 三档的命名，见 AWS 博客：https://aws.amazon.com/blogs/machine-learning/get-started-with-openai-gpt-5-6-sol-terra-and-luna-on-amazon-bedrock/ （openai.com 和 help.openai.com 对脚本访问返回 403）
- **建议改成**：
  - 字幕：「官方测了四类工作流：Jev和GPT-5.6 Terra准确率差不多，速度是它的二十多倍，成本只有它的七十几分之一。」
  - TTS：「官方测了四类工作流。Jev 和 G P T 五点六 Terra，准确率差不多，速度是它的二十多倍，成本只有它的七十几分之一。」
  - 画面：
    - 第一条横条改成「准确率 67.8% vs 67.9%（以 GPT-6 Astra 和 Claude Fable 5.1 的平均答案为准）」。
    - 小字末尾加「被比较的大模型套了 TypeSafe 的适配器，官方说这样往往更慢更贵」。
  - 如果想完全不受四舍五入影响，可以说「成本不到它的五十分之一」。
  - 顺手把 PRONUNCIATION 里的「70 多倍 → 七十多倍」改成「七十几分之一」。

### ⚠️-3　S05-50（台词 + 画面）｜优先级：高

- **原文**：
  - 台词：「算数、比日期、要推理好几步的题，它也做不好。官方建议交给代码。」
  - 画面：「不适合」栏加「算数、比日期」「多步推理」，箭头指向「交给代码」。
- **问题**：
  - 官方说“交给代码”的，只有算数（含计数）和日期比较。
  - 对“多步推理 / 多层间接”，官方的建议不同：少绕几层；把题拆成几道简单的小题，再在代码里组合；真需要长推理的任务“可能更适合大型推理模型”。
  - 现在一句话把三者都归到“交给代码”，画面箭头也连上了“多步推理”，不准确。
  - 另外，“做不好”是官方自己列的短板，第三方的结果并不一致：
    - PriorBench 测数字比较，13 种写法平均 99.6%，还说官方文档低估了模型。
    - 腾讯科技转述的 JevBench 里，“时间与数字”题只有 26.7%。
    - 所以台词最好点明这是“官方说”。
- **依据**（2026-09-28 查询）：
  - 文档 Jev 1.13 jaggedness（2026-09-17 复核，看表格里的“Do this instead”一栏）：https://docs.typesafe.ai/model-jaggedness/jev-1.13
  - 文档 Introduction「Atomic questions, composed in code」：https://docs.typesafe.ai/introduction
  - 官网首页 FAQ「What is Jev good at? Where does it struggle?」：https://typesafe.ai/
  - PriorBench：https://github.com/priorbench/jev
  - 腾讯科技原文：https://mp.weixin.qq.com/s/ZkfxAuaFrXs9aq8cyraZng
- **建议改成**：
  - 字幕：「算数、比日期它做不好，官方建议交给代码；要推理好几步的题，官方建议拆成几道小题。」
  - TTS：「算数，比日期，它做不好，官方建议交给代码。要推理好几步的题，官方建议，拆成几道小题。」
  - 画面：箭头改成「算数、比日期」→「交给代码」；「多步推理」→「拆成小题（太难就交给推理模型）」。小字不变。

### ⚠️-4　S04-33（画面小字）｜优先级：中

- **原文**：「官方 FAQ · CEO：不生成语言，所以不算语言模型 · 业内推测它也是从语言模型训练来的（未公开）」
- **问题**：后半句不只是“业内推测”。
  - 官方 AI 入门文档写的是：预训练语言模型有两种主要改造路线（RLHF、RLVR），TypeSafe 加了第三种 RLCD。配图也是从“预训练语言模型”分出 RLCD 这条路。
  - HN 上有人问“是不是在预训练底座上做 RLCD”，CEO 回复说对。
  - 真正没公开的，是底座用的哪个模型和架构细节。
  - 台词「官方说，Jev不算LLM，因为它不生成语言」没问题：
    - 博客 FAQ：Jev 既不小，也不是 LLM。
    - 首页 FAQ：能理解语言，但不生成自由文本。
    - CEO 在 HN：严格说不是语言模型，因为它不生成语言。
- **依据**（2026-09-28 查询）：
  - 文档 AI primer：https://docs.typesafe.ai/introduction/machine-learning-primer
  - CEO 的回复：https://news.ycombinator.com/item?id=49718407 （回复对象：https://news.ycombinator.com/item?id=49718350 ）
  - CEO 说“不是语言模型”：https://news.ycombinator.com/item?id=49718437
  - 博客 FAQ「Is Jev just a smaller LLM?」
- **建议小字**：「官方 FAQ · CEO：不生成语言，所以不算 LLM · 官方文档：它是在预训练语言模型上用 RLCD 训练的（底座没公开）」

### ⚠️-5　S03-23（台词）｜优先级：中

- **原文**：「返回的都是数字：交给物流组的概率0.72，退款组0.28；紧急的概率0.96。」
- **问题**：
  - 选择题除了概率，还会返回选中的那个选项（`choice` 字段，比如 "shipping"）。打分题还带 `legend`（等级说明）。
  - 画面代码卡里就能看到 shipping。
  - 和 S07-71 的“直接返回选项、分数和概率”也对不上。
- **依据**（2026-09-28 查询）：
  - https://docs.typesafe.ai/api （Answer types）
  - https://docs.typesafe.ai/primitives （What comes back）
- **建议改成**：
  - 字幕：「返回的是选项和概率：交给物流组的概率0.72，退款组0.28；紧急的概率0.96。」
  - TTS：「返回的是选项和概率。交给物流组的概率，零点七二，退款组，零点二八。紧急的概率，零点九六。」

### ⚠️-6　S06-69（台词 + 画面）｜优先级：中

- **原文**：
  - 台词：「另外，按官方最新的说法，新注册的用户不再送免费额度。」
  - 小字卡：「新用户不送免费额度 · 官方 X 2026-09-27（美国时间）」
- **核对**：
  - 帖子确实存在，时间是 2026-09-27 22:30:08 UTC（美西 9/27 15:30，北京 9/28 06:30），查询时仍是官方最新一条。
  - 但原帖后半句是“希望尽快恢复”。这是暂停，不是取消。
- **依据**：https://x.com/typesafeai/status/2104337824292220981 （经 api.fxtwitter.com 读取，2026-09-28 查询）
- **建议改成**：
  - 字幕：「另外，按官方最新的说法，新注册的用户暂时不送免费额度。」
  - TTS：「另外，按官方最新的说法，新注册的用户，暂时不送免费额度。」
  - 画面：「新用户暂不送免费额度（官方说会尽快恢复）· 官方 X 2026-09-27（美国时间）」
  - 出片前再看一次官方 X。

### ⚠️-7　S03-11（画面小字）｜优先级：低

- **原文**：「09-21 起开放注册（北京时间）」
- **问题**：
  - 9/21 05:30（北京时间）官方宣布不用排队。
  - 但 9/22 14:19 就暂停了新注册，9/28 06:30 才恢复。
  - “起”字暗示一直开放着。而 S06-69 引用的，正是 9/28 恢复注册的那条帖子。
- **依据**（2026-09-28 查询，经 api.fxtwitter.com 读取）：
  - 开放：https://x.com/typesafeai/status/2101786156572823624 （2026-09-20 21:30:43 UTC）
  - 暂停：https://x.com/typesafeai/status/2102281508950307159 （2026-09-22 06:19:04 UTC）
  - 恢复：https://x.com/typesafeai/status/2104337822350221795 （2026-09-27 22:30:08 UTC）
- **建议改成**：「09-21 开放注册，中间暂停过，09-28 恢复（北京时间）」。嫌长就写「现已开放注册（09-28 恢复，北京时间）」。

### ⚠️-8　S04-37（台词）｜优先级：低

- **原文**：「就算只问“急不急”，LLM也得先写一段字，程序再去读这段字。」
- **问题**：
  - “一段字”说重了。LLM 可以只回一个词，或一小段 JSON；TypeSafe 自己的评测，就是把大模型约束成结构化输出来比的。
  - 准确的区别是：LLM 总得先一个 token 一个 token 地生成文字，程序再解析；Jev 直接给数值。
- **依据**（2026-09-28 查询）：
  - 文档 Introduction：用 LLM 输出结构化决策，要先生成、再解析回来。https://docs.typesafe.ai/introduction
  - 博客对照表的“Outputs”一行，和“Workflow evals”一节：https://typesafe.ai/blog/introducing-system-one-models-and-jev
- **建议改成**：
  - 字幕：「就算只问“急不急”，LLM也得先生成文字，程序再去解析这段文字。」
  - TTS：「就算只问急不急，L L M 也得先生成文字，程序再去解析这段文字。」
  - 画面示意可以保留，但 LLM 那句建议缩短（比如「是，因为……」），别暗示一定是长段落。

### ⚠️-9　S05-59（台词 + 画面）｜优先级：低

- **原文**：
  - 台词：「官方推荐：Jev先判断，有把握的交给代码直接处理，没把握的转给人或大模型。」
  - 画面：高置信度 →「代码直接处理」。
- **问题**：
  - 官方的“意图路由”里，有把握的请求按类别分流：有的交给固定代码（比如查订单），有的交给专门的大模型（比如产品问题、退货）。没把握的转人工。
  - System One 页说，没把握时升级给人或推理模型。
  - 所以“没把握的转给人或大模型”是对的；“有把握的交给代码”说窄了。
- **依据**（2026-09-28 查询）：
  - https://docs.typesafe.ai/patterns/intent-routing
  - https://docs.typesafe.ai/concepts/system-one
  - https://docs.typesafe.ai/confidence
- **建议改成**：
  - 字幕：「那两者怎么配合？官方推荐：Jev先判断，有把握的直接按结果分流，没把握的转给人或大模型。」
  - TTS：「那两者怎么配合？官方推荐，Jev 先判断。有把握的，直接按结果分流。没把握的，转给人或大模型。」
  - 画面：高置信度 →「代码 / 专门的模型」。S05-61 画面里“一部分请求在「代码直接处理」这里结束”不用改。

### 台本文件里需要更新的出处说明

这些不上屏，但会影响后面的核对。

1. **CHECKLIST 第 19 条**说“留一个‘以上都不是’……不是官方原话”，**不对**。
   - 官方文档的 Primitives 页和 Choice 页都明确建议：选项可能覆盖不全时，加一个 `other` 或 `none of the above` 选项。
   - PriorBench 的十条建议里也有这一条。
   - S05-56 可以在画面加小字「官方文档也这么建议」。
   - 依据：https://docs.typesafe.ai/primitives 、https://docs.typesafe.ai/primitives/choice 、https://github.com/priorbench/jev
2. **CHECKLIST 第 14 条**说“业内推测它也是从语言模型底座训练出来的”，见 ⚠️-4：官方文档自己就是这么画的。
3. **CHECKLIST 第 2 条和 NOTES** 的“只上屏‘9 月 21 日起开放注册’”，见 ⚠️-7。
4. **CHECKLIST 第 19 条**的出处可以升级：PriorBench 的原始报告已经找到（下面“查不到”第 2 条），不必只写“据 TDS 转述”。
5. **research_web.md 第 4 节**推算“193.6 倍接近 Jev 和最慢的 sonnet 5 相比”，有误。
   - workflow 模式下最慢的是 DS v4 pro（86.5 秒），不是 sonnet 5（78.1 秒）。
   - 这个推算本来就是猜测。台本没用，保持不用。
6. **CHECKLIST 第 13 条**（出片前用浏览器核对 FAQ 原句）和**第 10 条**（出片前再核评测站）：本轮都核过了，没有变化。
7. **wechat_notes.md** 记的发布时间，比公众号页面时间戳各晚 1 小时，可能是按日本时间记的。
   - 页面上是：差评 2026-09-27 00:12，腾讯科技 2026-09-26 19:18（北京时间）。
   - 台本只用了日期，不影响。

---

## 三、建议补充

控制在 2 句。

### 补充 1：S04-42 后补半句“LLM 加结构化输出也能管住格式”

- **原因**：第三点区别现在只说“LLM 可能格式出错，也可能编出你没给的选项”，观众容易以为只有 Jev 不会编选项。这是 HN 发布帖里最主要的质疑之一。
  - 其实 LLM 加上结构化输出 / 约束解码，也能被限定在给定选项里。TypeSafe 自己的评测，就是这样把大模型约束成结构化决策来比的。
  - 官网 FAQ 回答“和 JSON mode、结构化输出有什么不同”时，也承认能让 LLM 输出合法 JSON，只是认为硬套格式会浪费一部分能力。
  - Jev 真正不同的地方是：直接给出每个选项的概率；不逐字生成；输出不能是开放文字。
- **依据**（2026-09-28 查询）：
  - 官网首页 FAQ「How is this different from JSON mode or structured outputs?」：https://typesafe.ai/
  - 博客“Workflow evals”一节（System One LLM wrapper）
  - TypeSafe 官方 GitHub 上的 system-one-adapter-python，用大模型 API 实现同一个接口：https://github.com/typesafe-ai/system-one-adapter-python
  - HN 上的这条质疑：https://news.ycombinator.com/item?id=49718492
- **建议句**（接在 S04-42 后面，或者只做成画面小字）：
  - 字幕：「当然，给LLM加上结构化输出也能管住格式，只是官方认为这样会浪费它一部分能力。」
  - TTS：「当然，给 L L M 加上结构化输出，也能管住格式，只是官方认为，这样会浪费它一部分能力。」
  - 只上屏的版本：「LLM 加结构化输出也能限定选项；官方 FAQ：硬套格式会浪费一部分能力」

### 补充 2：点明“Jev 本身没开源”

- **原因**：S03-29 画面出现“开源模型 Laya”，逛逛GitHub 的标题还写着“把 Jev 模型开源了”，观众很容易以为 Jev 开源了。
  - 实际上，TypeSafe 没公开权重、参数量、训练数据和完整架构。CEO 在 HN 上说架构暂时不公开。
  - 官方 GitHub 上只有 SDK、agent skill 等工具；Hugging Face 上搜不到 Jev。
  - 想用 Jev，只能通过 API：官方 API，或者 OpenRouter、Vercel 这类转接平台。
  - Laya 是别人做的类似模型，仓库 2026-09-18 才建。
- **依据**（2026-09-28 查询）：
  - TypeSafe 官方 GitHub 仓库列表：https://github.com/typesafe-ai
  - Hugging Face 按作者 typesafe / typesafe-ai、按关键词 jev-1.13 搜索，都没有结果
  - CEO 谈架构：https://news.ycombinator.com/item?id=49718824
  - TDS 原文：https://towardsdatascience.com/jev-vs-llms-when-ai-moves-from-generation-to-decision-making/
  - Laya 仓库：https://github.com/NandhaKishorM/laya
- **建议**（二选一）：
  - 改 S06-63：
    - 字幕「补充一下：Jev没有开源，只能通过API调用。想自己试试，分三步。」
    - TTS「补充一下，Jev 没有开源，只能通过 A P I 调用。想自己试试，分三步。」
  - 或者只改 S03-29 小字：「类似思路的开源模型：Laya（据逛逛GitHub；不是 Jev，Jev 本身没开源）」

---

## 四、✅ 核对无误的简表

全部是 2026-09-28 查询的结果。

| 段号 | 说法（台词 / 画面） | 核对结果和依据 |
|---|---|---|
| S01-01 画面 | TypeSafe AI 的 System One 模型 · 2026-09 | ✅ 官方博客，2026-09-15 |
| S02-02 | 最近 AI 圈都在聊 | ✅ 描述性说法。HN 发布帖 https://news.ycombinator.com/item?id=49717558 ，中英文媒体都有报道 |
| S02-03 | 不聊天、不写文章、一个字都不生成、只做判断 | ✅ 文档 Jev with coding agents：不生成文本、不写代码、不对话 https://docs.typesafe.ai/introduction/coding-agents |
| S02-04 | 官网写着“快 193.6 倍”“零幻觉 Zero Hallucinations” | ✅ 首页大字是“193.6x Faster, 444.6x Cheaper”，脚注写“基于 System One 任务的工作流”；另有“Zero Hallucinations”一块。大字没写和谁比，“比大模型”来自下方演示卡（对面标的是 LLMs）和博客的说明，可以这么说 |
| S03-11 台词 | 美国创业公司 TypeSafe AI，2026 年 9 月中旬发布 | ✅ 博客署 Sep 15, 2026；新闻稿电头“SAN FRANCISCO, September 15, 2026” https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html |
| S03-11 画面 | 旧金山 · 2024 年成立 | ✅ 新闻稿写明 2024 年成立、总部在旧金山 |
| S03-11 画面 | 2026-09-15 发布（美国时间） | ✅ 新闻稿 19:00 UTC，HN 帖 19:25 UTC；北京时间已是 9/16 |
| S03-11 画面 | CEO Diogo Almeida：InstructGPT 论文作者之一 | ✅ arXiv 2203.02155，20 位作者中排第 4 https://arxiv.org/abs/2203.02155 。没用“RLHF 共同发明人”（公司和文档自己的说法）是对的 |
| S03-11 画面 | 名字取自经济学家杰文斯（Jevons） | ✅ 博客 FAQ：取自 William Stanley Jevons |
| S03-11 画面 | 和 LeCun 的 JEPA 没有关系 | ✅ 官网、博客、文档全文都没有 JEPA 或 LeCun；名字来源另有官方说明 |
| S03-12 | 官方类别名 System One 模型 | ✅ 博客、文档 |
| S03-14 | 系统一快、靠直觉；系统二慢、靠推理 | ✅ 博客 FAQ；《思考，快与慢》节选 |
| S03-15 | 懂行的人几秒钟就能下的判断；小字“快速、聚焦的判断” | ✅ 文档 Introduction 和 System One 页 |
| S03-16～18 | 不生成文字；材料叫 state；一次可问多道题；题型三种 | ✅ 文档 Introduction、API reference |
| S03-19 | 选择题；最多 255 个选项 | ✅ API reference：每个 Choice 最多 255 个选项 https://docs.typesafe.ai/api |
| S03-20 | 打分题；2–10 个等级 | ✅ API reference：至少两级，最多 10 级 |
| S03-21 | 是非题 = 为真的概率；Noul 取自 Bernoulli | ✅ 文档没写名字来源。出处是 CEO 在 HN 的回复 https://news.ycombinator.com/item?id=49718407 ，Simon Willison 也转述了 |
| S03-22 | 三题一起发、一起算、一起返回；代码卡 POST /v1/systemone、model / state / questions | ✅ 文档 Introduction（所有题并行、互相隔离）；API reference |
| S03-23 画面 | 返回体字段 | ✅ 数值是示意，字段都对：choice / probabilities / confidence；score；noul 没有 confidence。Score 等级从 0 编号，1.3 落在 0–2 之间是合理的 |
| S03-24 | 概率校准过，标 0.8 的大约八成对；小字“说的是整体，不保证单个答案” | ✅ 文档 AI primer、System One 页 |
| S03-25 | 输入 $0.042 / 百万 token，输出免费 | ✅ 文档 Models 页：$42 / 十亿 token，只按输入收费，输出免费 https://docs.typesafe.ai/models |
| S03-26 | 70–500 毫秒（端到端）；小字“在美国西海岸测” | ✅ 博客对照表；博客 Evidence 一节说测速多在西海岸。文档另有“约 100 毫秒”“150 毫秒”的说法，台词只引了博客，没问题 |
| S03-28 | 只输出判断的分类模型早就有；BERT，2018 | ✅ arXiv 1810.04805，2018-10-11 |
| S03-29 | 传统分类模型的类别一般在训练时定好；Jev 每次现写、不用重新训练；Laya | ✅ CEO 在 HN 说完全不用训练 https://news.ycombinator.com/item?id=49719245 ；文档说所有账号共用一套权重；Laya 仓库存在。**可选小字**：现写类别的“零样本分类”2019 年就有（Yin 等，arXiv 1909.00161），CEO 也认可 Jev 基本就是零样本分类器 https://news.ycombinator.com/item?id=49718727 。Jev 新在通用、一次多题、概率校准 |
| S04-32 | LLM 的全称；ChatGPT、DeepSeek 背后都是它 | ✅ |
| S04-33 台词 | 官方说 Jev 不算 LLM，因为它不生成语言 | ✅ 画面后半句见 ⚠️-4 |
| S04-35/36 | LLM 逐 token 顺序生成；Jev 一次并行输出 | ✅ 博客对照表“Sampling”一行 |
| S04-38 | LLM 输出按 token 收费，比输入贵（约 5 倍）；Jev 只收输入 | ✅ 博客对照表“Cost”一行 |
| S04-40 | 这是厂商自己测的 | ✅ |
| S04-41 | 193.6 倍，官方博客自己也说偏高 | ✅ 转述忠实。博客原话是：首页的 193.6 倍、444.6 倍就出自这组工作流评测，并预计它们处在 "on the higher end of real world gains"。画面用“偏高的一端”最贴切 |
| S04-41 | 真实客户的线上数据最多快 4 倍；客户 Deel；小字“官方 X 转述” | ✅ 2026-09-25 03:13 UTC 的帖子：跟跑线上流量最多快 4 倍，离线测试 2–3 倍 https://x.com/typesafeai/status/2103321896553210029 ；同一串的首帖点名 @deel |
| S04-42 | LLM 可能格式出错、编出没给的选项 | ✅ 可以补半句，见补充 1 |
| S04-43 | Jev 只能在给的选项里选；“零幻觉”指的就是这个 | ✅ 文档 Primitives：答案只会落在你给的选项里；首页 FAQ：不会编出列表以外的类别 |
| S04-44 | 引语卡英文原句和中文译文 | ✅ 浏览器里展开首页 FAQ「Can Jev still get things wrong?」核对，和画面英文**逐字一致**（13 个词）。中文“只保证答案的形状，不保证每个判断都对”忠实 |
| S04-45 | 只给数字不给理由；Simon Willison：比 LLM 更像黑箱 | ✅ 文档 System One 页：不生成推理解释。Simon 2026-09-21 的文章专门有一节讲 Jev 让机器学习更倒回黑箱 https://simonwillison.net/2026/Sep/21/jev/ |
| S05-47 | 适合高频、简单、标准明确的判断 | ✅ 这是概括。首页 FAQ 说 Jev 是为常识性判断设计的 |
| S05-48 | 工单分类、内容审核、检索相关性、模型路由；小字“用例地图” | ✅ 用例地图里都有：Customer support、Moderation and trust and safety、Search and retrieval、Model routing https://docs.typesafe.ai/concepts/use-case-map |
| S05-49 | 不写文章、不聊天、不写代码 | ✅ 文档 Jev with coding agents |
| S05-51 | 中文能用但不如英文；小字“Models 页” | ✅ 文档 Models 页「Language support」 |
| S05-53/54 | 《杀戮尖塔》：三张防御牌 17 / 20 / 18，结束回合 21，选了结束回合；“防御”的概率被拆成三份 | ✅ 差评原文（2026-09-27 00:12 北京时间）https://mp.weixin.qq.com/s/aFkhX2xJoiGssaWBXywOwg |
| S05-55 | 选项里没正确答案也硬选、很自信；30 条、置信度 ≥ 0.99；据 TDS 转述 | ✅ TDS 原文如此；PriorBench 自己的报告也写着：没有“以上都不是”选项时，30 条里一条都没识别出来，置信度 0.99。小字可以直接标「PriorBench 独立评测（GitHub，2026-09-20）」 |
| S05-56 | 留一个“以上都不是” | ✅ 而且官方文档本来就这么建议，见 ⚠️ 部分“需要更新的出处说明”第 1 条 |
| S05-58 | 说有八成把握的题，实际只对一半多；0.81 vs 53%；Banking77 | ✅ TDS（Nhu Hoang，2026-09-25）：置信度 0.7–0.9 这一段，平均 0.81，只对了 53% |
| S05-60 | 先问 Jev 再问大模型反而更慢更贵；649 → 1087 毫秒（据腾讯科技） | ✅ 腾讯科技原文（2026-09-26）：记忆检索实验里加了一道 Jev 判断，总延迟从 649 毫秒升到 1087 毫秒，每千次的费用“翻了两倍多” |
| S05-61/62 | 省钱的前提是替大模型挡掉一部分请求；两者分工 | ✅ 意图路由页：贵的资源只给真正需要的请求 |
| S06-64 | 在控制台注册、创建 API Key；console.typesafe.ai | ✅ 官方 X 9/27 的帖子指向 console.typesafe.ai；Quick start 写明 Key 在 console.typesafe.ai/keys 领 |
| S06-65 | 在控制台的 Playground 里填材料、加题、看结果 | ✅ Quick start https://docs.typesafe.ai/introduction/quickstart |
| S06-66 | 官方 Python / JavaScript 工具包；pip install typesafe-sdk；client.system_one(state=…, questions=…)；Key 从环境变量读 | ✅ SDK 页；Quick start（环境变量是 TYPESAFE_API_KEY） |
| S06-67 | 置信度分三档：高自动执行、中请人确认、低转人或别的系统；阈值按出错的代价定 | ✅ Confidence 页 https://docs.typesafe.ai/confidence |
| S06-68 | 上线前拿自己的数据测，尤其是中文 | ✅ Models 页：非英语先用自己的内容测；Confidence 页：用自己的数据定阈值 |
| S07-71～73 | 总结三条 | ✅ 和正文一致；“快、便宜”在画面上标了“厂商自测” |

---

## 五、查不到 / 打不开

1. **649 → 1087 毫秒的原始实验**：腾讯科技原文只写了“GitHub 上的一组 Agent 记忆检索实验”，没给项目名，也没给链接，一手出处没追到。台本已标“据腾讯科技”，可以用。
2. **PriorBench 的原始报告**：已找到，是 https://github.com/priorbench/jev （2026-09-20 建）。它的 README 和 TDS 的转述一致，不再算“查不到”。
3. **评测站“terra”的全名**：页面只写“terra”（归在 OpenAI 名下）。根据 GPT-5.6 分 Sol / Terra / Luna 三档（见 AWS 博客），加上博客并排演示用的是 GPT-5.6 Terra，推断是同一个模型。但评测站本身没写全名。
4. **首页 193.6 倍、444.6 倍是怎么算的**：官方没写。research_web.md 的推算有误（见 ⚠️ 部分）。台本没用这个推算。
5. **Deel“最多快 4 倍”的对比细节**：官方 X 只说是和前沿大模型比、跟跑线上流量，没给对比的具体模型和样本量。
6. **控制台内部界面**（API Keys 页、Playground）：要登录，没进去看，是按 Quick start 文档核对的。画面本来就是示意，不影响。
7. **打不开或只能间接读的页面**：
   - x.com 要登录，官方帖子都是经 api.fxtwitter.com 读的原文和 UTC 时间。
   - 用 syndication.twitter.com 的时间线确认了 9/27 22:30 UTC 之后没有新帖。这个接口可能有缓存，出片前再看一次。
   - openai.com 和 help.openai.com 对脚本访问返回 403，GPT-5.6 的三档命名改用 AWS 博客确认。
   - 其余页面本轮都正常打开了。
