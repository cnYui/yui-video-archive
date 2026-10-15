# Claude Code相关

悠一的新合集（2026-10-02 开）：和 Claude Code 有关的产品信息——新功能、更新、官方发布、使用技巧，一条条做成短视频。B 站合集「Claude Code相关」（合集 id 9223239，用户在投稿页里建的）；发 YouTube 与否待用户定。

- 第 1 期从 `独立视频/2026-10_Claude最新功能介绍/` 整个移过来（2026-10-02）。
- 做法照第 1 期：全程画外音（Fish 网页版曼波声线）+ 官方演示视频 + 官方页面录屏，没有静态文字卡片；流程、坑和下一期的清单见 [流程复盘.md](流程复盘.md)（第 3 期在前、第 1 期在后）。
- **整期流程技能 `skill/claude-code-episode/`**（`C:\Users\yui\.claude\skills\claude-code-episode` 是联接，2026-10-03 照第 3 期整理）：`new_episode.py` 一条命令建一期（中英双语引擎模板、台本 / 配音 / 投稿 / 封面候选骨架），`fetch_x_video.py` 下载官方视频，`references/` 写事实核对、页面录屏、配音、B 站投稿，`predeliver_check.py` 交付前自查。做下一期先读它的 SKILL.md。
- 封面技能 `skill/claude-code-cover/`（`C:\Users\yui\.claude\skills\claude-code-cover` 是联接）：**必须有 Claude 的官方像素宇航员（要大，动作可以自己画，不能用自造的角色顶替）和 Claude 品牌色，背景也用品牌色（深色 / 米白 / 品牌橙 / 淡黄）**；`make_candidates.py` 按候选清单一次出 3 个候选 + 验收 + 总览图。

| 期 | 目录 | 标题 | 状态 |
|---|---|---|---|
| 01 | `01_Claude Code模组发布\` | 现在你可以让Claude修改自己！Claude新功能：Claude mod（用户最后在投稿页里改定的；封面字“Claude mod(模组)发布”） | **已发布**：[BV1Zoa16CEeU](https://www.bilibili.com/video/BV1Zoa16CEeU/)（2026-10-02 10:44 北京时间，4:14，含片头片尾；合集「Claude Code相关」；封面 C：官方教程页底部太空场景 + 放大的像素宇航员；10 个标签，简介 1695 字）；GitHub release 没建 |
| 02 | `独立视频\2026-10_ClaudeSlides设计师用法\`（目录还没挪进来） | Anthropic设计师教你如何使用Claude（用户给的标题；封面字是官方缩略图译成中文的“Anthropic 设计师 / 如何使用 Claude Slides”） | **已发布**：[BV1Yham6gECf](https://www.bilibili.com/video/BV1Yham6gECf/)（2026-10-02 16:13 北京时间，1:45，**转载** Claude 官方 YouTube《Make presentations with Claude Slides》，只加中英双语字幕和中文封面，不含悠一片头片尾；合集「Claude Code相关」第 2 集；10 个标签，简介 479 字）；GitHub release 不建（别人的视频） |
| 03 | `03_YouShouldKnow插件\` | 线上标题：一个视频了解Claude Code 新插件：/YouShouldKnow  Agent Loop 开发里，它替你盯着、帮你复盘（用户在页面里手改的，带多余的“：/”和双空格；我拟的是“一个视频了解 Claude Code 新插件 You should know：Agent Loop 开发里，它替你盯着、帮你复盘”；封面字“别漏看重点 / Claude 新插件”） | **已投稿 [BV1PdHh6QE72](https://www.bilibili.com/video/BV1PdHh6QE72/)（2026-10-03 09:42 北京时间（10:42 东京），审核中，125 s，含新版片头片尾；封面 A）**：用户给了 @ClaudeDevs 的两条推文 + claude.dev 博文；素材 = 官方演示视频 39 s + 推文 / 文档 / 更新日志的页面录屏；**第一条做中英双语字幕的**（中文一行 52 px + 英文一行 30 px 烧进画面 + 三份 SRT）；曼波配音；封面用 `claude-code-cover`（官方宇航员原帧）；事实核对 `台本/事实核对.md`；10 个标签、简介 1833 字；合集归属要过审后用 `ugc_season` 核对；GitHub release 没建 |
| 04 | `04_ClaudeProjects\` | 这个 Claude 的这个 Project，一个视频带你看懂是什么东西（用户给的，原稿写的是 Cloud，我按语音输入误听改成 Claude，他确认“标题用Claude”；封面 A：他抬手展示肌肉那帧 + 大字“Claude / Project 是啥？”，统一框版 + 黄贴纸 Claude Code） | **已投稿 [BV1Hgpg6dELo](https://www.bilibili.com/video/BV1Hgpg6dELo/)（2026-10-10 20:15 北京时间（21:15 东京），审核中，683 s，含片头片尾；合集「Claude Code相关」接口已显示）**：**悠一出镜口播（5 段 DJI 录像剪成 11.1 分钟）+ 官方 4 分钟演示 / 文档 / 推文 / 博客页面**的多素材横屏（2340×1080 三栏版式）；中英双语字幕烧进画面 + 三份 SRT（没传 B 站）；第 0 帧 = 16:9 封面；事实核对 `台本/事实核对.md`、剪辑时删掉的 17 处说法见 `台本/剪辑说明.md`；10 个标签（编程、claude、Claude Code、Anthropic、AI编程、人工智能、AI工具、大模型、AI Agent、Projects）、简介 1155 字（章节 + 要点 + 说明 + 资料来源 + 制作，存 `制作/_desc_final.txt`）、创作声明“含AI生成内容”；**没录“泼冷水 / 边界”那一段**；片尾清单是草稿、没等用户确认就烧进去了；GitHub release 没建 |
| 05 | `05_Sonnet5.5与Haiku5.5\`（原叫 04，同一天另一个会话建了 `04_ClaudeProjects`，用户让这期改成第 5 期） | Opus5.5 VS Sonnet5.5 VS Haiku5.5 !一个视频看懂价格和能力（用户自己定的；我拟的是“Sonnet 5.5 和 Haiku 5.5 怎么选？Haiku 便宜 20 倍，能力差多少？…”；封面 C：官方像素宇航员 bolt 动作，字“价格 + 能力 / 一次看懂”，统一框版） | **已投稿 [BV1fcpi6oEmu](https://www.bilibili.com/video/BV1fcpi6oEmu/)（2026-10-10 13:44 北京时间（14:44 东京），审核中，320 s；合集「Claude Code相关」接口已显示）**：开场 = @ClaudeDevs 官方护蛋演示（Opus 5.5 单干 vs 带 10 个 Haiku 5.5），其余全是官方发布页 / 价格页 / 模型总览 / 推文的页面录屏 + 一张自算的账单对比；温柔男生配音（Fish 故事工作室）；中英双语字幕；事实核对 `台本/事实核对.md`；10 个标签、简介 1988 字；成片第 0 帧 = 封面；配音读音（Fable、个别 Sonnet）用户听了说没问题 |

**短视频**（竖屏 1080×2340，技能 `short-video`，放 `短视频\`；素材放 `素材\`，短、长视频共用）：

| # | 目录 | 内容 | 状态 |
|---|---|---|---|
| 04 | `短视频\04_CCBaga环境工具\`（素材 `素材\2026-10_CCBaga\`） | CCBaga本地归档、浏览器配置、环境一致性与出口核验机制；86.5秒、不出镜、本地Qwen配音、中英双语字幕，明确不保证免封 | **2026-10-14 已发布 [BV1CxpC69ESE](https://www.bilibili.com/video/BV1CxpC69ESE/)（开放浏览）**，只发B站，合集9223239；用户指定封面「Claude永不封号？！」与标题，双比例封面和AI声明均已核验 |
| 01 | `短视频\01_ClaudeDesign设计师用法\`（2026-10-04 从顶层 `短视频\` 挪来；原片在 `素材\2026-10_ClaudeDesign设计师用法\`） | Claude 官方 YouTube《Build an App With Claude Design》二次剪辑成 28 秒（双分镜：人脸 + 电脑操作，曼波中文讲解，不加片头片尾） | 成片已出；配音待用户听，平台 / B 站合集 / 封面待定 |
| 02 | `短视频\02_Anthropic设计师用Claude做设计\`（原片在 `素材\2026-10_Anthropic设计师_ClaudeDesign与Slides\`） | 同一位设计师 Nate 的两条官方视频合成一条（Claude Design 主线 + Claude Slides 第二章，约 2:18）：**保留 Nate 的原声和视频里的 BGM，英语处叠曼波第三人称同传**，中文字幕 = 同传、英文字幕 = 第三人称；双分镜，版式 B + 边框 6，随机背景印花（这条是橙色），字幕在 y 1764，不加片头片尾 | 成片已出；配音待用户听，平台 / B 站合集 / 封面待定 |
| 03 | `短视频\03_Claude模组\`（素材直接引用 `01_Claude Code模组发布\素材\`） | 长视频《Claude mod 发布》二次剪辑成 53 秒（推文截图 + 三个官方示例演示 + 文档页面录屏，温柔男生第三人称讲解，BGM，single 版式 B + 边框 6）；**只发抖音 / 小红书 / 视频号，不发 B 站** | 成片 + 封面 3×3 + 标题 3×4 已发给用户，等“封面 X 标题 Y 同意” |

## 这个合集的规矩

1. **内容 = Claude Code 相关的官方信息**：只写官方原文能对上的事（官方推文、claude.dev 博客 / 教程、code.claude.com 文档、更新日志）；台本每句都有出处，写完用脚本逐条核对（第 1 期 `素材/网页截图/verify_claims.py`，37 条 36 条逐字对上）；官方没公布的不写“发布了”。日期不写具体几号（美国时间和北京时间差一天），写“这几天”。
2. **画面 = 真实素材**：官方演示视频（第 3 期起用 X 公开嵌入接口 + `fetch_x_video.py` 取 `video.twimg.com` 直链；第 1 期用 TwitterSaver、下载前解 JWT 核对源站）+ 自己录的官方页面（Playwright 长图 + 荧光笔，见流程复盘）。演示视频和页面录屏加起来 ≥ 90%，卡片只做过场。
3. **左栏目录最多 3 条**（每条 ≤ 7 字）。配音是 Fish 网页版 S2 Pro 曼波声线，**重新生成要新开空白页面**，别在共享编辑框里换稿。
4. **封面**：用 `claude-code-cover` 技能的 `make_candidates.py` 先出 3 个候选；官方像素宇航员、不自造角色；封面只放两行短而大的字、没有小字，标题写详细、不和封面字是同一句；出 16:9 + 4:3 两张；简介里写官方插画版权说明；B 站上传时“双比例同步改动”不勾、两个比例各传各的。
5. **投稿**：用户把 mp4 拖进 B 站投稿页，我用 Chrome 插件填表；用户只说“填写”时，“立即投稿”等用户说；用户明说“发布这个视频”并给了标题 / 合集（第 2 期）就可以直接点。标题以用户给的 / 在页面里改的为准。**转载别人的视频**：创作声明选“内容为转载”，来源栏写原视频链接 + 频道 + 日期（这版投稿页没有单独的“类型”选项，转载是在创作声明里选的）。片尾清单每期问用户。填表步骤和坑在 `skill/claude-code-episode/references/publish.md`。
6. **片头片尾必加**（用户 2026-10-03：所有生成的视频都要加）：模板 `AI科普/片头片尾/`（片头 4.8 s 对话气泡、片尾 9.0 s 信纸：参考文献 + 致谢），加法 `python AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py <正片> --outro-data <片尾.json>`，SRT / 章节时间加 4.8 s；片尾内容每期问用户。
