# 《AI每日日报》流水线搭建与首期试跑

时间：2026-09-27 15:40–17:15（UTC+9）。设计见 `20260927-145456-ai-daily-news-plan_CN.md`。

## 用户这一轮的要求

- 标题 `M月D日，鲸鱼娘带你看看AI圈发生了什么？`；新建合集「AI每日日报」（用户说“分集”，按合集做）；视频 3–4 分钟。
- RSS 用代码抓，频率由我来定；每天怎么跑由用户设 routine，这里只要把“跑一次”做好。
- 配音：浏览器插件操作 Fish Audio 网页版克隆音色（免费）。额度用完时用户切换账号。
- 画面、合成、封面按设计；复用 UE 片头片尾；片尾写新闻来源，**B 站简介也写一份来源**。
- 视频里放原文截图。
- **配音里不要“本期配音由AI合成”这句**，太割裂。之后又说开场屏幕上的这行字也不要，改完就发布；合集要新建。
- 发布用浏览器插件。

## 搭好的东西

```text
D:\大疆\AI日报\
  collector\            sources.yaml（66 个源）、collect.py、seen.sqlite、snapshots\、health\health.md
  skill\ai-daily-news\  SKILL.md（单次运行流程，routine 调它）
    scripts\            daily.py（init / build / voice / render / published / status）
                        make_episode.py（台本.json → episode.json、script_data.py、引擎）
                        snap_sources.py（原文截图）、make_cover.py（封面）、gen_backgrounds.py（背景）
    assets\engine-template\  从《原LAI如此》引擎复制后改的：scenes.news.js（数据驱动，每期不用手写）
    assets\cover-template\   cover.daily.html
  素材\                 字体、音频 → 联接 AI科普\素材\；角色\动作帧 → 联接大肥鱼像素素材包\素材；背景图库\（3 张自己生成的蓝色像素背景）
  片头片尾\             → 联接 AI科普\片头片尾
  2026-09-27\           首期
```

- `C:\Users\yui\.claude\skills\ai-daily-news` 联接到技能目录，Claude Code 已经识别。
- 复用《原LAI如此》的 build_script、chunk_voice、fetch_check、select_takes、segment_audio、build_timeline、mix_audio、assemble、render_parallel（用 `--series D:\大疆\AI日报` 调，不改原文件）。

### 收集器（collect.py）
- `collect`：抓全部源，新条目入库。“新” = 库里没见过的，不看源里写的时间（OpenAI RSS 的时刻是占位值）。一个源第一次抓时，36 小时以前的只入库不当候选。带 ETag，RSSHub 路由按顺序试两个公共实例。
- `export <期目录>`：取上次导出以来入库的新条目 → `items.jsonl`、`candidates.json`、`candidates.md`。导出时重新套一遍过滤规则；按公司名 + 去掉公司名和通用词后的关键词重合聚类；分数 = 来源级别 + 覆盖源数 + 条目数 + 发布类关键词，Google News、Reddit 这类单源条目降权。
- 关键词过滤里的英文词按整词匹配（“AI”不会匹配到 “said”）；Google News 用 SEO 垃圾标题过滤（“Best … prompts”“[2026]”“price prediction” 等）。
- 首跑：66 个源全部成功，0 失败。

### 引擎改动（只改了复制出来的那份）
- `core.js`：左上徽标 `episode.badge_html`、目录标题 `toc_kicker_html`、进度条配色 `bar_colors` 都可以在 episode.json 里改（没写就是《原LAI如此》原样）；预加载 `news[].snap` 截图，第一帧就有图。
- 强调色从橙色换成天蓝 `#3D8BFF`；`sync_assets.py` 只要求 idle 帧（大肥鱼没有 reach、walk）。
- `scenes.news.js`：开场日期大字 → 串讲时今日要闻卡飞进右上目录；每条新闻一场：标题卡 → 来源和日期 → 左栏要点、右栏原文截图（没有截图就一栏）；最后「今日回顾」卡。开场原来有一行“本期配音由 AI 合成”小字，按用户要求删了（`make_episode.py` 不再写 `ai_notice`）。

### 原文截图（snap_sources.py）
- 无头 Chromium 1280×900、1.5 倍像素；隐藏图片、视频、iframe、cookie 和订阅弹层、吸顶栏；把第一个可见的 `<h1>` 滚到顶部，截约 1000×560 的区域（标题、署名、导语）。
- 被拦截或没有 `<h1>` 就换下一个来源，都不行就这一条不放截图。
- 首期 5/5 成功：theverge.com、ithome.com、anthropic.com、qbitai.com、techcrunch.com。

## 首期（2026-09-27）试跑

1. `daily.py init`：候选 304 个（2026-09-26 08:49 → 09-27 14:49 北京时间）。
2. 选 5 条：OpenAI 暂停训练最强模型（The Verge、The Decoder）；澳大利亚参议院传唤 OpenAI 和 Anthropic 的 CEO（IT之家援引路透社）；Claude 算出九圈物理难题（Anthropic 官方博客）；谷歌 TPU 跑 Kimi K3 快 57%（量子位）；Anthropic 向 Akamai 支付 116 亿美元（TechCrunch）。
   - 没选：OpenAI 常驻助手「O」、Claude Sonnet 5.5（都是传闻）；五角大楼拉黑 Anthropic、国会关注中国模型（美国军方、中美政策）。
   - 查原文时纠正了二手报道：IT之家写“几千美元”，Anthropic 原文是“一两千美元”；原文还提到中科院何颂团队也已经算出大部分结果，台本加了这一句。
3. 台本 829 字、5 条；第一版开场有“本期配音由AI合成”，按用户要求删掉。另外存了 `台本_完整5条.json`（带那句的原版）和 `台本_测试3条.json`（额度不够时的缩短版，没用上）。
4. 配音 7 批（2,219 字节）：第一个账号剩 1,166 积分，配完 C01–C03 后用户切换账号，配 C04–C07。新账号默认模型是 S2.1 Pro，切回 S1 保持一致。每批 2 个版本，选分：C01 0.904、C02 0.924、C03 0.927、C04 0.916、C05 0.767、C06 0.783、C07 1.000。C05、C06 低分主要是英文名：Inferact、DeepSeek、Akamai（识别成“阿坎麦”）、Anthropic（“安索皮”）。
5. 配音合计约 130 秒。检查时发现开场自称“大肥鱼”，和标题、《原LAI如此》讲解员预设 whale（自称鲸鱼娘，用户在第 2 期定的）不一致，改成“我是鲸鱼娘”，只重配了 C01（新账号，选分 0.829，识别成“金鱼娘”，要听）。
6. 成片 `AI每日日报_0927_成片.mp4`：2:30.2（片头 3.8 + 正片 141.6 + 片尾 4.8），1080p30，34 MB；上传版 8.37 MB（视频 364 kbps）；封面 16:9 + 4:3；审稿单事实核对 0 处提示（116亿/18亿 按“亿 = 0.1 billion”换算后都能在原文找到）。
   - 第一次出片后改了两处模板：结尾回顾卡加 2 秒停留（结尾那句只有 2.8 秒，卡片看不清）；片尾第二行来源的标签写“来源（续）”（原来是空白，看着没对齐）。
   - 正片比 3–4 分钟短：「苏晓晓」语速快，模板字数改成 1100–1450。
7. 用户要求去掉开场屏幕上的 AI 小字，重新出片（上传版 8,372,873 字节），然后发布。
8. 插件投稿（北京时间 16:03）：**BV1Etah6TExW**，https://www.bilibili.com/video/BV1Etah6TExW 。
   - 同时新建合集「AI每日日报」（16:02，正常显示），本期已在合集里。
   - 标签 10 个：AI资讯、人工智能、大模型、AI日报、OpenAI、谷歌、Kimi、鲸鱼娘、大肥鱼、Anthropic（“Claude”是话题专用词，加不上）。
   - 创作声明「含AI生成内容」；分区「人工智能」；简介 979 字（章节 + 来源 + 说明）。
   - 投稿后转码 360P–1080P 都完成，状态“审核中”。`daily.py published` 已把 5 条写进 `collector\aired.jsonl`。

## 发现的问题 / 限制

- Fish Audio 网页版免费额度：1 积分 = 1 字节，每次生成（含 2 个版本）扣一次，每月 8,000，约够 3 期。靠用户切换账号。备选：Fish Audio API 的 `s2.1-pro-free` 模型（0 元、不要信用卡、公平使用、请求可能被拿去训练）。
- 两个说话人会弹 Plus 付费墙：编辑器里只留「苏晓晓」一个说话块。
- 「苏晓晓」S1 语速约 6.35 字/秒：829 字只有约 2:15 正片，低于 3–4 分钟。模板已改成 1100–1450 字。
- 英文专有名词的读法要用户听（Anthropic、Akamai、Inferact）。可以在 `tts` 里写中文近音，但要用户先定读法。
- 公共 RSSHub 不稳定（19 个只有 2 个能用，常 429 / 502）；Meta AI、xAI 官网抓不到，靠社区 RSS 和媒体。
- B 站投稿页（2026-09-27，已写进 SKILL.md 第 8 步）：
  - 创作声明的选项现在叫「含AI生成内容」。
  - 分区下拉只有一级分区，选「人工智能」，没有 AI资讯 可选。
  - 定时发布：这个账号是 5 分钟后到 15 天内（调研说至少提前 4 小时，以投稿页为准）。
  - 简介是 Quill 编辑器，行首“1. ”会自动变成有序列表、编号重复（“4. 4.”）。这次用 `__quill.deleteText` 删掉多余编号；`daily.py` 已改用 ① ②。
  - 创建合集的输入框用 `type` 后计数不动，要用原生 setter 赋值再派发 input / change。
  - 插件 `javascript_tool` 的返回值里带 HTML 或图片网址会被拦（“Cookie/query string data”）。
  - 投稿成功后点“查看进度”，地址栏的 `bvid=` 就是 BV 号。

## 待办

- [x] 首期投稿：BV1Etah6TExW（等 B 站审核）。
- [ ] 用户设 routine：北京 04:30 跑技能 `ai-daily-news`；可选用 Windows 计划任务在 12:30、18:30、00:30 跑 `collect.py collect`。
