---
name: short-video
description: 做悠一的竖屏短视频（1080×2340，20 秒到 2 分钟，B 站竖屏 + 抖音）：长视频二次剪辑（双分镜：同一个长视频里两个不冲突的镜头上下同时放，比如人脸 + 电脑操作，AI 配音（声线「温柔男生」）把观点讲得更快更密）或多来源新闻短条（标题 + 单个素材框 + 大数字卡片）；英文讲解的素材做中文同传（声线「温柔男生」，原声压低留着，中文字幕 = 同传、英文字幕 = 原话）。台本照 AI大圆镜 的写法（钩子带数字、短分句、自问自答、泼冷水、金句收尾），中英双语字幕，**不加悠一片头片尾**，封面三个比例（真实画面 + 短钩子 + 箭头）。用户提到“短视频”“竖屏”“抖音”“剪成 20 到 30 秒”“剪成一分钟”“二次剪辑”“把这个长视频做成短视频”“两个分镜放在同一个画面”“像 AI大圆镜 那样”“做一条短的”，或给短视频写稿、配音、出封面、发抖音时，都用这个技能。 悠一自己出镜 / 用自己录的口播原声做短视频时：原声 + 镜像圆角小窗（单框居中在字幕下面，双框缩到下框左下角，场景换版式时顺势移动），ASR 字幕一字不改，见 references/face-window.md。用户给的是好几段口播（几分钟到十几分钟）、要配官方课 / 官网 / 录屏镜头和自画说明卡时走 faceb 版式（每个场景自己选单窗 / 双窗 / 大窗），整条流水线（批量 ASR、剪停顿、生成 plan、扫讲师的脸、定格审计）见 assets/oncam-multiclip/README.md。
---

**默认发布平台（2026-10-14 用户定）：短视频、长视频在用户未指定平台时仅发 B 站；不打开、不上传其他平台。用户明确要求其他平台时才启用对应流程。平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。**

**上传方式（2026-10-14 用户定）：文件小于 10 MB 且本轮已授权自动上传时，可用 Playwright JS 上传完整文件；达到或超过 10 MB 就提醒用户手动上传。不为自动上传压缩、分块或改用低清版本。用户手动上传后继续填表，已授权发布则读回核对后点击发布。**


# 短视频（竖屏）

**Playwright上传规则（2026-10-14复盘）**：用户点名Playwright就直接使用；已有发布授权且原片小于10MB时自动上传，标准传文件报 `DOM.setFileInputFiles: Not allowed` 时使用完整小文件的File/DataTransfer/change流程。达到10MB由用户手动上传，不压缩、不分块、不起上传服务器。B站新投稿已实测成功；连接、JS参数准备、双比例封面、读回核对与防重复投稿见 `references/publish.md`「Playwright：B站小文件自动上传与发布」，历史复盘见 `D:/大疆/短视频/流程复盘.md`第10部分。

**开工前、第一次渲整片前，都重读一遍 `SKILL.md`、`references/layout.md`、`references/script.md`**：这个技能 2026-10-04 一天里改了好几次（第三人称、版式 B + 边框 6、随机背景、同传规则），第 2 条用的是 11:00 的旧版本，渲完才发现，整轮返工。

**标准流程（用户 2026-10-04 定的四段：“我给你素材 → 调用短视频 skill → 生成视频 + 封面×3 + 标题×3 → 我同意后发布四个平台”；2026-10-06 起视频号不再发，当前默认仅 B 站；抖音 / 小红书须用户另行指定）**：① 用户给素材（缺的**一次问完**；**默认值**：仅发 B 站（其他平台仅在用户明确指定时启用）、合集随 B 站（没有就不选）、BGM 默认配、话题抖音 5 个（平台上限）/ 小红书 8–10 个、位置不选、声明“含 AI 生成内容”、小红书“原创声明”开关选开、英文讲解做同传、台本第三人称）→ ② 我按下面步骤 0–5 做成片（**出整片前把引擎副本同步到模板最新版**）→ ③ **交付包，成片一出就一次发给用户**：成片完整路径 + 手机预览、**封面 3×3**（3 个候选 × 竖屏 3:4 / 16:9 / 4:3 = 9 张 + 总览图，标推荐；用户：“封面的话，是3x3，3种每种都要有竖屏、16：9、4：3的封面”）、**标题 3×3**（3 个候选 × 三个平台各自的要求 = 9 个：B 站完整版 ≤ 80 / 抖音 ≤ 30 / 小红书 ≤ 20；用户 2026-10-04 当时要的是 3×4，第四个是视频号短标题 6–16，2026-10-06 视频号不发后去掉）、其余默认项一行摘要、要耳朵听的句子；用户回“封面 X 标题 Y 同意” → ④ 步骤 7：打开本轮指定的平台（默认仅 B 站）、按文件大小自动上传或用户手动上传、我一次填完整并读回核对、点发布（③ 里说了“同意 / 发布”就是授权）、逐个核对线上、关标签并通知排队的下一个。**交付包的消息模板、两条（Tavus、image-blaster）的复盘和踩坑表在 `D:\大疆\短视频\流程复盘.md` 开头和后面。**

**2026-10-06 用户的两条决定**：①**视频号之后不发**（“把视频号这个平台移除短视频发布skill”）——发布流程改成 **B 站 / 抖音 / 小红书三个平台**，标题 3×4 改 3×3（不再有视频号短标题 6–16），不再填视频号页、不再约视频号上的“前台”；视频号的旧做法（wujie shadowRoot 填表、短标题 6–16 字、位置选“不显示位置”、合集标题 ≤ 10 字等）原样存在 `references/_archive/视频号发布_已移除_20261006.md`，用户哪天又要发再翻。②**小红书的“原创声明”开关选开**（用户：“原创声明 就是小红书应该选择的”），“内容类型声明”仍选“笔记含AI合成内容”——之前技能里写的“原创声明默认开着、二次剪辑要关”作废；默认值时开时关，每条都读回确认是开；点开开关可能弹《原创声明须知》，要勾选“我已阅读并同意”——**这个同意用户已长期授权给我来勾**（用户 2026-10-06 晚：“《原创声明须知》之后都是你来勾选，我已同意”；以前写的“要用户本人给、先问、routine 不勾”作废）：弹出就直接勾“我已阅读并同意”再点“声明原创”，不用再问。**成片第 0 帧 = 封面**（`cover_frame0.py`）这条用户规则不变（“之后生成的视频统一第一帧为封面”），只是不再为视频号服务。别的技能里的视频号字样这次没动（用户只点名了短视频发布 skill）。

**放在哪**（用户 2026-10-04：“在当前项目的所有不同分类的文件夹下，都新创建短视频和长视频两个文件夹，划分开来，素材可以公用”）：一条短视频放 `<合集>\短视频\NN_<短名>\`（合集目录：AI实操 / AI日报 / AI科普 / AI震惊瘫坐…（CS 研究生）/ Claude Code相关 / OpenAI相关 / Way to AGI / 独立视频），素材放合集层 `<合集>\素材\<YYYY-MM_主题>\`（短、长视频共用）。顶层 `D:\大疆\短视频\` 只放这个技能。归哪个合集每条问用户。

**已经做过的短视频（照着学）**：
- 第 1 条《ClaudeDesign设计师用法》（`Claude Code相关\短视频\01_ClaudeDesign设计师用法\`，28 s，压缩改写、不留原声）：ffmpeg 直接合成，记录 `docs/ai/context/20261004-105500-short-video-01-claude-design-ffmpeg_CN.md`。
- 《image-blaster 推荐》（`独立视频\短视频\2026-10_image-blaster推荐\`，59.6 s 定稿，single + 大数字卡 + GitHub 页面录屏 + 曼波同传）：第一条照本技能引擎做的，记录 `docs/ai/context/20261004-111500-image-blaster-short-video_CN.md`；之后用版式 B + 边框 6 + BGM + 彩色背景整条重渲；**2026-10-04 四个平台都发过**（B 站 BV1ncHr6gE4U；用户在交付包里说“同意”后我点的发布，小红书是他自己点的），复盘见 `D:\大疆\短视频\流程复盘.md` 第 2 部分、记录 `docs/ai/context/20261004-160000-image-blaster-final-and-publish_CN.md`。
- 《Tavus-Griffin》（`独立视频\短视频\01_Tavus-Griffin\`，45.5 s）：第一条叠放 dual 的真成片（本技能引擎，版式 B）；加了程序合成 BGM（三选一）、满框封面，**第一条四个平台（B 站 / 抖音 / 小红书 / 视频号）全发过**；复盘 `D:\大疆\短视频\流程复盘.md`，发布踩的坑 `references/publish.md`。
- 第 2 条《Anthropic设计师用Claude做设计》（`Claude Code相关\短视频\02_Anthropic设计师用Claude做设计\`，约 2:18，Design + Slides 两条官方视频合一条，原声 + BGM + 曼波第三人称同传，dual 版式 B + 边框 6 + 随机背景）：ffmpeg 直接合成，记录 `docs/ai/context/20261004-143000-short-video-02-claude-design-slides-interpretation_CN.md`。
- 第 3 条《Claude模组》（`Claude Code相关\短视频\03_Claude模组\`，53 s，single 版式；长视频 `01_Claude Code模组发布` 的二次剪辑：@ClaudeDevs 主帖推文截图 + 三个官方示例演示 + 官方文档页面录屏，**温柔男生**重新讲、第三人称、BGM 床 −10 dB，没有素材原声）：第一条用温柔男生声线——每汉字约 0.22 s（和曼波一样，211 汉字有声 46 s）、Token Weather / Blast Radius / Replay Theater 一次读对。**封面用框版 `scripts/make_cover_framed.py`**（界面截图没有脸，`make_cover.py` 的 full 样式会让字盖住内容、3:4 把面板切掉；框版 = 钩子大字在框外 + 画面缩进边框 6 + 黄贴纸，3 候选 × 3 比例 + 总览，清单写 `制作/04_封面/candidates_framed.json`，`make_candidates.py --select X` 只复制不重出图）。只发抖音 / 小红书 / 视频号（用户点名不发 B 站）。记录 `docs/ai/context/20261004-200900-short-video-03-claude-mods_CN.md`。
- 《不再Review》（`独立视频\短视频\2026-10_不再Review\`，54 s，dual 版式；长视频《一个月合并2000多个PR，却不逐个Review》的二次剪辑：上框 = 访谈并排人像格里裁出的单人上半身（静音）、下框 = 她演讲里的白底幻灯片 + pstack 官方页面录屏，**温柔男生**第三人称重新讲、BGM 床 −9 dB，没有素材原声）：**新增 range 的 `bg` 纯色补边（白底幻灯片）**、访谈人像格 `crop [0.5, 0.06, 1.0, 0.56]` 裁单人，细节写在 `references/layout.md` 末尾；温柔男生每汉字约 0.215 s。封面三个都是 full 满框（A 笑着听的安静帧 / B 讲解特写 / C 提问的帧），`defaults.avoid` 躲名牌。记录 `docs/ai/context/20261005-113000-no-more-review-short-video_CN.md`。
- 《Claude 中文界面》（`独立视频\短视频\2026-10_Claude中文界面\`，62.7 s，single 版式；**第一条悠一出镜的原声版**：用户自己的 DJI 口播原声 + **镜像圆角小窗**（居中在字幕下面）、ASR 字幕一字不改、自然停顿、画面全是页面镜头（语言选择框截图 + 官方帮助页 / 支持地区页 / 封号理由页录屏 + 官方透明度页）；B 站 BV1CWHZ6tEHK / 抖音 / 小红书 10/6 都发了，声明选“个人观点”）：`own_voice.py` / `compose_face.py` / `NATURAL_TIMING` 都是这条做出来的，细节和坑见 `references/face-window.md`，README 在本条目录。
- 《Claude官方教程》第 1 期出镜版（`Claude官方教程\短视频\01_ClaudeCode是什么_出镜版\`，9 分 34 秒，**faceb 版式**：5 段 DJI 口播剪成母带 + 官方课 Claude Academy 的屏幕 / 动画镜头 + 他的两段录屏 + 12 张自画说明卡，45 个场景 one / two / big，124 句中英双语字幕；封面 B = 深色终端 + 官方吉祥物 + “> claude”；B 站 BV15NpF6JEvy / 抖音 / 小红书 10/6 都发了，小红书原创声明待开）：**多段口播流水线、faceb 版式、扫讲师的脸、定格审计、吉祥物封面都是这条做出来的**，已全部收进技能——`assets/oncam-multiclip/README.md`（流程 + 真实例子）、`references/face-window.md`「多段口播」、复盘 `D:\大疆\短视频\流程复盘.md` 第 9 部分、记录 `docs/ai/context/20261006-172000-claude-official-ep1-on-camera-real-voice_CN.md`。

两条路线：**标准路线是本技能的竖屏 HTML 引擎**（能叠标注、页面录屏、大数字卡、链接条，有 `check_subs.py` 和静帧检查）。只要纯双分镜 + 真人原声同传、不要叠加层时，也可以走 **ffmpeg 直接合成**，照第 2 条的脚本（最完整）：`台本/plan.py`（每段 = 原片一个连续片段 + 1–3 句同传 + 上下框子镜头 + 小标签）→ `制作/00_整片/` 的 `check_cuts` `snap_cuts` `build_timeline` `make_bg` `render_scenes` `make_subs` `mix_audio` `render` `qa_mix`；它的 `make_bg.py` 里有用 PIL 画边框 6（橙色硬阴影 + 7 px 黑描边 + 右上角倾斜 3° 的黄贴纸）的现成代码。两条路线出来的版式一样。**走 ffmpeg + ASS 烧字幕时字号要换算**：ASS 的 Fontsize 是行高，写 52 只有 CSS 52 px 的 0.686 倍大，中文 / 英文要写 **76 / 44**（第 2 条的 `make_subs.py` 用 `LIBASS_EM` 换算，`check_subs_render.py` 对成片抽帧量真实字宽；共用的 `bilingual_std.ass_header()` 也已改成 76 / 44）。第 1 条写的是 52，字偏小。

## 硬性要求（用户 2026-10-04 定的）

1. **画布 1080×2340**（“竖屏的比例就是我当前横屏比例竖过来就行”，横屏是 2340×1080），30 fps。
2. **不加悠一片头片尾**（“短视频开头和结尾不要用开场和收尾的视频片段”）：第一帧就是钩子，金句说完 0.8 s 结束；SRT 没有片头偏移。
3. **语言风格照 AI大圆镜**（“语言风格就和上面的那个up主的风格相似即可”）：先读 `D:\大疆\docs\台本风格_AI大圆镜.md`，再读 `references/script.md`。
4. **长视频二次剪辑用双分镜**（对第 1 条：“把这个长视频的两个不冲突的分镜放在同一个画面中出现（比如当前视频里一个人脸一个电脑操作的画面），你控制好时长，同时用ai配音讲解，就是进行二次剪辑，把视频里的观点更快更密集的讲出来”）：`plan.json` 的 `layout: "dual"`，上框 `ranges`、下框 `ranges2`（`references/layout.md`）。时长用户说多少就多少（第 1 条“20秒到30秒”）。
5. **中英双语字幕**（项目标准，字号和横屏一样：中文 52 px + 英文 30 px；竖屏每条中文 ≤ 17 字、英文 ≤ 约 60 字符，自动拆条，`check_subs.py` 按真实字宽量）。**英文讲解的素材做中文同传**（声线见第 9 条；用户 2026-10-04 当时说“如果是英文讲解的话，你要用曼波ai配音做双语同传，还有双语字幕”，后来改用温柔男生）：原声压低留着，中文字幕 = 同传、英文字幕 = 讲解者原话（`references/script.md`「英文讲解的素材」）；**压缩成 20–30 秒的二次剪辑（第 1 条那样）不做同传、不留原声**，重新讲（用户 2026-10-04 答“不要”）。
6. **事实核对在台本之前**（`references/facts.md`）：钩子里的数字和“首次”都要有原文；不学 AI大圆镜 的事实拼接。
7. **背景每条随机挑一张**（用户 2026-10-04：“之前让你生成的背景图片有三张，你都加入到背景图片的选择中，每一期视频随机挑选一张作为背景即可”“这个要求写入skill中”）：三张 AI 工具图标印花在 `assets/backgrounds/`（原色 / 墨色 / 橙色），`new_short.py` 建条目时随机挑（`--bg` 指定、`--bg none` 不用），见 `references/layout.md`「背景印花」。**横版视频也用同一套图标，另有三张 2340×1080 的横版版 `landscape_*.png`**（用户 2026-10-05：“长视频背景也加上和短视频 skill 中相同的背景图片，你设计三张横版的图片……之后横板视频也要随机选一张图片”）：横版的新建脚本（`claude-code-episode` / `openai-episode` / `way-to-agi-episode` 的 `new_episode.py`）自动调 `assets/backgrounds/pick_bg.py` 随机挑；手工用 `python pick_bg.py <本期 00_整片 目录>`（`--pool pattern` 挑竖屏池，`--bg 文件名 | none` 指定 / 不用）。竖屏池只认 `pattern_` 前缀、横版池只认 `landscape_` 前缀，互不串。
8. **画面 = 真实素材**（记忆 `footage-over-explainer-cards`）：不做整屏文字卡片；标题和大数字卡片是唯一的“设计”元素。
9. **配音**：Fish 故事工作室空白项目、声线**「温柔男生」**（用户 2026-10-04：“之后语音合成使用温柔男生这个配音”，贴了故事工作室声音下拉的截图；之前几条用的是曼波「赛马娘（曼波欧耶版）」）、模型沿用 S2 Pro（选完声音看一眼模型下拉）（`references/voice.md`）；曼波每个汉字约 0.22 s、**30 秒封顶 ≤ 约 125 个汉字**——**换声线后字数 / 时长要重测**（先生成一两句量每字秒数，温柔男生的语速待测），专名读音（Nate / Claude / Anthropic）和 sh/x 误听也要重新听；超了删句重生成，不靠加速凑。
10. **渲染统一 4 路、同一时间只跑一个渲染**：开渲前 `ListAgents` 看别的会话，空闲内存 < 6 GB 用 `RENDER_WORKERS=3`（或 2）。
11. **交付包里用户说了“同意 / 发布 / 用封面 X”才算授权发布**（image-blaster：“没问题，打开四个平台，填写信息然后发布”）：授权后仅对本轮指定的平台**一次填完整、读回核对**就点发布，再逐个核对线上；用户只说“填写”时才停在发布前。**小于10MB原片自动上传，达到10MB由用户手动上传；不压缩、不分块**（`references/publish.md`的Playwright专节）。**用户随时可能自己点发布**（Tavus 的四个、image-blaster 的小红书都是他点的）：封面 / 标题 / 话题（抖音**最多 5 个**，小红书 8–10 个）/ 声明（小红书“原创声明”选开）/ 位置（不选）/ 合集都一次填完，没填完就明说“先别点发布”；**拖好视频那条回复里就说清“我填约 20 分钟，期间别点发布，我说‘填好了’再点”**（RL 长文那次用户在我填到小红书时把三个平台连点了发布；出镜版那次他在我填 B 站时先点了小红书的发布，**原创声明没来得及开**，只能发布后进笔记管理再改）。**所以开填之前先确认小红书“原创声明”要开**（默认就是开；《原创声明须知》的同意用户已长期授权给我勾：2026-10-06 晚“之后都是你来勾选，我已同意”），并且每填完一个平台就马上发那个平台。
12. Chrome / Fish / 渲染都可能被别的会话占着：开工先 `ListAgents`、`ls -t docs/ai/context | head`，要用就发消息约，用完说一声。
13. **BGM 默认配**（用户两条都是做完才补：Tavus“加一个 bgm”、image-blaster“还需要给视频加上bgm”）：系列 BGM 垫底，或程序合成三选一（Tavus 那条的 `make_bgm.py`）。两条最后定的都是**BGM 单路比人声低约 14–15 dB**（bed −7 … −11 dB，手机外放听得到）；模板默认 −16 dB 床（低约 20 dB）偏低，先按 −7 … −11 dB 起步；旧模板“有原声就压到 ×0.05”等于听不见，已改 `BGM_DUCK = 1.0`。出成片前 `qa_mix` 看各路响度。
14. **封面统一用框版（用户 2026-10-05 贴了两张封面样图：“标题这里，统一图中的风格并落实到skill中，白色+橙色，重新修改封面并修改投稿视频的封面”）**：大字白字 + 橙字（`accent_line` 那行）、墨色粗描边 + 硬投影，画面缩进“边框 6”（7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸），底是本条的背景印花，和成片同一个版式；有脸的画面（访谈、人像）也用它，**不再用 `make_cover.py` 的 full / shot / split**（老条目留着）。脚本 `scripts/make_cover_framed.py <本条目录>`（读 `制作/04_封面/candidates_framed.json`，出 3 候选 × 3:4 / 16:9 / 4:3 + `候选总览.png`；`--select X` 复制成 `封面_选定_*`），模板 `assets/cover-template/candidates_framed.json`，**用户给的两张样图在 `assets/cover-template/参考样图_用户20261005.jpg`**（米白图标印花底、左边白字 + 橙字大字黑描边、右边画面套黑框 + 橙色硬阴影 + 黄贴纸；做出来先对着它比一眼）；长视频封面同一样式（横版长视频借短视频那条的 `bg.png` 当印花，JSON 里写顶层 `bg`）。**封面一换，要重做成片第 0 帧（`cover_frame0.py`，从 `_成片_无封面帧.mp4` 重来），并把已发布平台上的封面一起换掉**：B 站编辑页（稿件管理 → 编辑 → 封面，两个比例位各传各的）、抖音（内容管理 → 编辑作品 → 点封面缩略图）、小红书（编辑封面 → 清除已上传封面 → 重新上传）。

15. **【已定版，固定规则】悠一出镜 = 镜像圆角小窗，统一这样用（用户 2026-10-06：“当前你做的这个出镜的人脸框我很满意，你也把这个落实同步到 /short-video 中，之后人脸出镜都这样用小窗展示，如果出现两个演示窗口没地方展示人脸的话，我的人脸也可以顺势移动到角落中”）**：用户自己录口播（DJI 原片）时用**他的原声**，不走 Fish；画面里他的脸 = **镜像（hflip）**的 360×360 圆角小窗，边框和成片同一套（7 px 黑描边 + 橙色硬阴影 + 黄贴纸“悠一 出镜”），单框版**居中放在字幕下面**（x 360, y 1664）；**双框版（两个演示窗口叠在一起、下面没地方）缩到 240 放到下框的左下角**，场景在单框 / 双框之间切换时脸缓入缓出地移动 + 缩放（0.35 s；`face.json` 写 `"move": "cut"` 则直接跳过去）；**窗口停着的位置绝不能盖字幕**（`compose_face.py` 自动检查并报警，用户 2026-10-06 特别强调）；plan.json 的场景可写 `"face": "center|bl|tl|tr|hide"` 指定位置。字幕 = ASR 转写，**一字不改**（只改听错的专名 / 同音字），观点句 / 没出处的说法写进交付说明；保持他说话的自然停顿（引擎 `NATURAL_TIMING`）。声明不选“含AI生成内容”（本人原声 + 脸）。用户 2026-10-06 看过真双框画面（字幕不被盖）后确认：“这样设计的没问题，固定写入skill中”。脚本：`scripts/own_voice.py`（asr / build）、`scripts/compose_face.py`（叠小窗）、`assets/face-template/face.json`；完整流程和坑在 `references/face-window.md`。

16. **顶上两行字（hook）每一帧都在，写之前问、第一张静帧就单独给用户看**（《Claude官方教程》第 1 期出镜版：沿用了 AI 草稿里随手写的钩子“小白讲清楚”，成片发出去才被用户指出，**整片重渲约 15 分钟**）：交付包里单独写一行“顶上这两行字（每一帧都在）：…，要改告诉我”；用户说要改，改 `script_data.py` / `录制稿.json` 的 `hook` → 重跑 `build_timeline` → 直接渲（抽帧缓存复用）→ 重做第 0 帧 / 封面 / 已发布的平台。**用户的消息可能是语音输入**（“讲清除”= 讲清楚），字面说不通先猜同音词。
17. **官方课 / 访谈素材只用屏幕 / 动画镜头，不放讲师的脸**（用户要的是“视频 + 官方页面录屏”，不是别人的脸；记忆 `claude-academy-footage-no-lecturer-face`）：选段**只用核过的安全段**；别凭 3 秒一帧的联系表推断“这一段都是屏幕”（第 1 期出镜版推断错了 4 处）；`prep_frames.py` 之后、渲整片之前跑 **`python scripts/scan_faces.py <本条>`**（Haar 扫素材帧，0.2 s 一张；鼠标手形 / 头像图标偶尔误报，看一眼那一帧）。**定格审计**：`scripts/audit_holds.py <本条>`（`gen_ep.py` 渲前也报上下窗各定格几秒），单段 > 3 s 的有意停住讲一张图可以留，其余补素材或改单窗；**所有 `P('Txx','词')` 用 `scripts/check_phrases.py <本条>` 先对一遍字幕**，不然词找不到整条渲染抛错。
18. **Claude / Anthropic 官方内容的封面候选至少一个放官方吉祥物**（用户 2026-10-06 看了人脸 / 循环图 / 确认框三个封面说“都不太行”，要“带有 claude 八爪鱼形象的封面”；“八爪鱼”= 官方课动画里的橙色像素吉祥物，12×8 方块，不是 `claude-code-cover` 的像素宇航员，也**别自己造别的角色**）：`scripts/make_mascot_pictures.py <本条>` 出三张画面（官方米色底 / 深色终端 + `> claude` / 淡黄底一大三小）→ `candidates_framed.json` → `make_cover_framed.py`；素材和用法在 `assets/mascot/README.md`；用户 10/6 选的是 B（深色终端）。别的公司的内容别用。
19. **含 Windows 路径的文档 / 脚本 / memory 用 Write / Edit 工具写，别用 Bash heredoc**：heredoc 会吞反斜杠（`\01` → 控制字符，`\\` → `\`），第 1 期出镜版一次弄脏了交付说明、两个 memory、一份 context 记录；路径写成正斜杠也行。用 Python 做含路径的正则 / 替换，同样先写成文件再跑。

## 步骤

```bash
cd "D:\大疆\短视频\skill\short-video\scripts"
python new_short.py --collection "Claude Code相关" --num 01 --name 短名 --layout dual   # 或 --layout single；建 <合集>\短视频\NN_<短名>\ + 引擎 + 台本骨架 + 配音脚本（.gitignore 已有 **/短视频/*/ 通配规则）
# 悠一出镜、好几段口播 + 官方素材 + 说明卡：--layout faceb（再多铺 talk_lines / script_data / scenes_ep / 01_口播，流程见 assets/oncam-multiclip/README.md）
python tsheet.py <原片> <联系表.png> 1 6 320                 # 整条每秒一帧，分出人脸段 / 操作段
```

| 步 | 做什么 | 文档 |
|---|---|---|
| 0 | 问清：时长、素材（链接 / 文件）、归哪个合集目录、发哪个平台、进哪个 B 站合集；读 `docs/台本风格_AI大圆镜.md`；`ListAgents` | 本文件 |
| 1 | 下素材到 `<合集>\素材\<YYYY-MM_主题>\`（`references/sources.md`），填 `制作/00_整片/common.py` 的 `SRC` / `HAS_AUDIO`；看联系表；**同时起事实核对子代理** | sources.md、facts.md |
| 2 | 台本 `台本/录制稿.json`（`hook` 两行标题、`kicker`、`lines` 的 zh / say / en）+ `台本/plan.json`（场景、`ranges` / `ranges2`、每句从第几秒开口） | script.md、layout.md |
| 3 | `python build_timeline.py --est` → `python check_subs.py` → `python prep_frames.py` → `python render_all.py --stills-segs`（逐张看 `stills/`）；用官方课 / 访谈素材的再加 `scripts/scan_faces.py`（讲师的脸）、`scripts/audit_holds.py`（定格）、`scripts/check_phrases.py`（`P()` 词）——第 16–17 条 | layout.md |
| 4 | 配音（故事工作室）→ `制作/02_配音/import_segments.py` → `build_voice.py --qa` → 重跑 `build_timeline.py` / `prep_frames.py` | voice.md |
| 5 | **先把引擎副本同步到模板最新版**（保留本条的 `common.py`、`capture_pages.py`、`scenes.js` 里的本条叠加层；image-blaster 的 `制作/00_整片/_sync_template.py` 是现成写法）→ `mix_audio.py`（含 BGM）→ `render_all.py`（4 路）→ 出镜版再 `compose_face.py`（合成完自动核对帧数 = base、少了重跑一次）→ `check_face_sync.py`（小窗和口播原片逐帧比，偏移 0 / ±1 正常）→ `qa_mix.py`（混音逐句识别）→ 抽成片帧看 → `finish.py`（成片 + 540×1170 手机预览 + 三份 SRT + 响度） | 引擎文件开头的注释 |
| 6 | **交付包（③）**：封面 3×3（候选 A / B / C × 三个比例 = 9 张 + 总览图，标推荐）+ 标题 3×3（3 个候选 × B 站 / 抖音 / 小红书各自的限长版 = 9 个）+ 成片预览 + 默认项摘要 + 要听的句子 + **“顶上这两行字（每一帧都在）：…，要改告诉我”这一行**（第 16 条；Claude / Anthropic 内容的封面候选至少一个放官方吉祥物，第 18 条），**成片一出就一次发给用户**。**脚本**：填 `制作/04_封面/candidates_framed.json` → `python scripts/make_cover_framed.py <本条>`（框版：白字 + 橙字黑描边、边框 6、黄贴纸、印花底；3 候选 × 3:4 / 16:9 / 4:3 + `候选总览.png`；`--select X` 把选中的复制成 `封面_选定_3x4 / 16x9 / 4x3.png`；老的 `make_candidates.py` 的 full / shot / split 样式不再用）；标题写 `投稿信息.json` 的 `titles` → `python scripts/check_titles.py <本条>`（按各平台要求量字数，也查标题和封面大字别同一句）。模板：`assets/cover-template/candidates_framed.json`、`assets/publish-template/投稿信息.json`（`new_short.py` 建条目时已拷进本条）；`make_cover.py` 单张封面（shot / split / full 三种样式）；image-blaster 的 `制作/04_封面/make_candidates.py` 是它的原型 | 流程复盘.md 开头、publish.md |
| 7 | **同意后发布（④，默认仅 B 站）**：`make_cover_framed.py <本条> --select X` → **`python scripts/cover_frame0.py <本条>` 把选定的封面放进成片第 0 帧**（用户 2026-10-04：“之后生成的视频统一第一帧为封面”——原本为视频号做的，视频号移除后这条规则仍在；约 20 秒，其余帧直接拷贝、原声不动，原片留 `_成片_无封面帧.mp4`；小红书默认封面就是第 0 帧的 3:4 居中裁切；**整片重渲 / 改过标题后，备份是旧的**——脚本现在会比大小 / 时长和三个时刻的帧，发现备份过期就自动用现在的成片重建备份并提醒（2026-10-06 加），但换封面前先自己 `cp 成片 _成片_无封面帧.mp4` 最稳）→ `投稿信息.json` 定稿（核各平台限长）→ 排队 → 打开指定平台投稿页（默认仅 B 站）→ 小于10MB原片自动上传；达到10MB时用 `explorer.exe /select` 选中新成片、写明路径并等用户上传 → 我一次填完整、读回核对 → 点发布（③ 里已授权）→ 逐个核对线上 → 关标签、通知下一个 → 记录：本条 README / `投稿信息.json`、`D:\大疆\短视频\README.md`、合集 README、`docs/ai/context`、AGENTS.md | publish.md |

## 文件

- `references/`：`script.md`（时长和字数、两种稿子、录制稿字段）、`layout.md`（竖屏分区、dual / single、裁切、平台遮挡区）、`sources.md`（X / B 站 / YouTube / 官方页面怎么下）、`voice.md`（温柔男生；曼波时期踩的点也在里面）、`facts.md`（事实核对）、`publish.md`（封面、B 站 / 抖音 / 小红书三个平台的填表和坑；视频号 2026-10-06 起不发，旧做法存档在 `references/_archive/视频号发布_已移除_20261006.md`）、`article-series.md`（**一篇文章 / 一个人的长文 → 好几期短视频**：查人、自称挂名、分期、公开页面录屏、敏感原文别进画面、整稿配音，工具在 `独立视频\短视频\_TimDenning系列\`）。流程复盘在 `D:\大疆\短视频\流程复盘.md`（每条做完补一节，下一条开工前读）。
- `assets/engine-template/`：竖屏引擎（`index.html` `engine.js` `scenes.js` `common.py` `build_timeline.py` `check_subs.py` `prep_frames.py` `render_all.py` `mix_audio.py` `qa_mix.py` `finish.py` `capture_pages.py` `pages.js`）。时间模型、抽帧、页面录屏、配音、混音和 Claude Code相关 引擎一样，换的是版式（标题一直在顶上、上框 / 字幕 / 下框或大数字卡）、字幕上限、画布和收尾（没有片头片尾）。
- `scripts/own_voice.py`（用户自录口播：`asr` 两遍转写、`build` 用原片音轨建 narration / tts_edit / 录制稿 / plan 的 `a` / `NATURAL_TIMING` / `face.json`）、`scripts/compose_face.py`（把镜像圆角小窗叠到卡片版成片上，位置按场景 / 版式缓动；single / dual / **faceb**；合成完核对帧数）、`assets/face-template/face.json`（小窗配置模板）、`references/face-window.md`（位置表、流程、坑、多段口播一节）。
- **出镜多段口播（faceb，2026-10-06）**：`assets/oncam-multiclip/`（`README.md` 流程 + 踩坑；`template/` 骨架 `talk_lines.py` / `script_data.py` / `scenes_ep.js`；`example_ep1/` 第 1 期真实的 124 行字幕、45 个场景、12 张说明卡）；脚本 `scripts/asr_clips.py`（批量 ASR）、`build_talk.py`（resolve / plan / media / concat：剪停顿和口误、帧级精确、母带）、`gen_ep.py`（台本 + 选段 → plan / 录制稿 / tts_edit / 口播稿，带上下窗定格报告）；QA：`scan_faces.py`（扫讲师的脸）、`audit_holds.py`（定格审计）、`check_phrases.py`（`P()` 词核对）、`check_face_sync.py`（小窗逐帧同步）。引擎模板支持 `layout: "faceb"`（`engine.js` 的 `MODES`、`prep_frames.py` 的大窗 1474×1725、`build_timeline.py` 的 mode），single / dual 版式不受影响。
- **官方吉祥物封面**：`assets/mascot/`（`mascot_sprite.json` + `README.md`）、`scripts/make_mascot_pictures.py`（第 18 条）。
- `assets/backgrounds/`：背景印花六张——竖屏三张（`pattern_color.png` `pattern_ink.png` `pattern_orange.png`，每条随机挑一张）+ 横版三张（`landscape_color.png` `landscape_ink.png` `landscape_orange.png`，2340×1080，横版视频每条随机挑一张）；`make_pattern.py` / `make_pattern_landscape.py`（重新生成）、`pick_bg.py`（随机挑一张拷成 `bg.png` + 写 `bg.json`）、`README.md`。
- `assets/script-template/`：`录制稿.json`、`plan.single.json`、`plan.dual.json`、`plan.faceb.json`；`assets/voice-template/`：`build_voice.py`、`import_segments.py`；`assets/cover-template/`：`cover.json`（单张封面）、`candidates.json`（交付包：封面 3×3）；`assets/publish-template/投稿信息.json`（交付包：标题 3×3 + 各平台字段 + 同意状态）。
- `scripts/`：`new_short.py`、`make_cover_framed.py`（**封面统一样式**：框版 3 候选 × 3 比例 + 总览 + `--select`，2026-10-05 起）、`make_cover.py` / `make_candidates.py`（老样式 shot / split / full，只留给老条目）、`check_titles.py`（标题 3×3 限长校验）、`cover_frame0.py`（把选定的封面放进成片第 0 帧；竖屏成片放 3:4、横版长视频放 16:9 居中左右模糊；`--check` 查现在的成片是不是封面帧；原片留 `_成片_无封面帧.mp4`，换封面从它重来；长视频原片第一帧 pts 不是 0 时加 `--pts-tol 0.03`）、`fetch_x_video.py`（X 视频直链）、`tsheet.py`（联系表）。

## 验证过（2026-10-04）

在 scratchpad 里用第 1 条的原片（Claude 官方 YouTube《Build an App With Claude Design》4K VP9）建了两条测试短视频：
- dual：`new_short.py` → `build_timeline.py --est`（15.2 s、7 条字幕）→ `check_subs.py`（中文最宽 884 px / 17 字、英文 857 px / 58 字符、标题三行各一行，没问题）→ `prep_frames.py`（两路各 2 段、8 秒）→ 静帧（上框人脸、下框 4K 裁一半的屏幕，字清楚）→ `render_all.py`（2 路 456 帧 50 秒，0 报错）→ `finish.py`（1080×2340 成片、540×1170 预览、三份 SRT 时间从 0 起）。
- single：静帧里 `big()` 大数字卡、`note()` 说明条位置都对。
- 变速：下框 `"speed": 2.5`（原片 60–79 s 压进 7.8 s），抽出 237 帧、首中尾三帧对得上原片 60 / 70 / 79 s。
- `make_cover.py`：shot（箭头指脸、字避开主角）和 split 两种，三个比例都出得来。

之后第 2 条（image-blaster）照这个引擎做完：真实配音 + 原声同传的 `mix_audio.py`、`qa_mix.py`、4 路渲染都过；它给 `capture_pages.py` 加的 `@top` / `@time` / `@css:` / 别名元组已合进模板（合完和它的副本只差 SPECS 例子）。

**版式 B + 边框 6 + 链接条**（用户 2026-10-04 选定，样图 `D:\大疆\短视频\版式方案_20261004\`）已合进模板的 `index.html` / `engine.js`（边框贴纸）/ `scenes.js`（`linkPill()`、`big()` 默认 y 1658）/ `check_subs.py`（字幕 y 从页面里量），改之前的原文件在 `assets/engine-template/*.bak_版式前`。验证：image-blaster 那条（单框）用新版式整条重渲（1779 帧、4 路 56 s、0 页面报错）、`check_subs.py` 通过、静帧里标题 / 贴纸 / 字幕 / 链接条 / 紧凑数字卡位置都对；dual（两框叠在一起、字幕在下）用真引擎 CSS 在 image-blaster 的副本里摆过一次（上框 680–1170、下框 1194–1684、字幕 1764，截图对），**之后《Tavus-Griffin》做了第一条真正的 dual 成片**（45.5 s，4 路 57 s、1365 帧、0 报错；框里 16:9 比例对、贴纸只贴上框、字幕 y 1764 没被盖；说明条小字缩后只剩 18 px 太小，只写一行；页面录屏的中文译文条要 56 px）。

**发布**：Tavus 那条 2026-10-04 在 B 站（竖屏，BV122H66UEYZ）、抖音、小红书、视频号四个平台都发过（用户自己点的发布；2026-10-06 起视频号不再发），填表的步骤和坑都在 `references/publish.md`（Chrome 插件连不上浏览器时改用 Playwright（插件工具，或桥接脚本 `pw_do.py` + `docs\pw\token.env` 里的令牌），见 `D:\大疆\docs\发布备用_Playwright.md`）。**没验证的**：变速段（`speed`）只在测试里跑过，还没进过真实成片；满框封面还没并进 `scripts/make_cover.py`（参考脚本见 `publish.md`）；BGM 的 `mix_audio.py --bgm` 选项和 `make_bgm.py` 在 Tavus 那条的引擎副本里，还没合进模板。
