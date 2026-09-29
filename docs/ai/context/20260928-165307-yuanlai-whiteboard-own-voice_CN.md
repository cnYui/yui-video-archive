# 《原LAI如此》白板手写版移植 + 用户自己配音（2026-09-28）

会话：「JEV模型视频企划」。接在 `20260928-155617-engine-white-center-switch_CN.md`（白底 / 居中开关）之后。

## 用户要求

- 本会话：“原LAI如此配音之后需要我来配音，ai配音用来做每日日报，然后原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大，角色动作现在就很合适”
- 用户同一天在日报会话里补充（日报会话写进了 AGENTS.md）：“手写动画要搬到《原LAI如此》，从第五期开始，字比声音早 1 秒，全部统一”；“现在第五期还没打算制作”（不要提前开工）；“其他的内容你都要帮我写好，我配音完成后，你再做后续的事情”；日报仍然全自动。
- 用户另外委托日报会话按技能文档用第 3 期副本测试新的白板版，问题回报给本会话改。

## 结论

1. 白板手写版进了《原LAI如此》引擎模板：`episode.json` 的 `"style": "board"`，`new_episode.py` 新一期默认写（`--style cards` 关）。没写 style 的期逐像素不变。
2. 画面比声音早 1 秒：做成“场景层时钟整体提前”（`board_lead`，默认 1.0）。scenes.js 照声音写时间，不用自己减；字幕、口型、进度条、目录高亮和打勾（有打勾声）跟声音。
3. 字幕 56 px 墨黑字白边，单行最宽 1500 px（和日报一样大）。
4. 配音：新一期默认 `"voice_source": "user"`（`--voice tts` 改回 AI）；录音稿、导入、切句（能跳过重读）由子任务在做，见下面「配音」。
5. 角色动作：用户说现在的量合适 → AGENTS.md「角色动作尺度」第 2–4 期这一档定为标准。

## 白板版怎么做的

- `hand.js`：从日报的 hand.js 原样搬来（笔画、排版、计时、记号笔算法不变），改了：强调色系列橙 #FF4F1A；缺字记进 `ENG.handMissing`；所有组件接受 `parent`（整组淡出）和 `out`（淡出时刻）；每个 `<g>` 带 `data-hand` / `data-text` 给 check_layout 查；新增 `c.handRect`、`c.handLine`、`c.handMark`（圈 / 划一行里的几个字，默认放进那行字所在的组）。
- `hand_glyphs.py`（放进引擎目录，sync_assets 调用）：从日报复制，数据目录改成 `AI科普/素材/手写`（新建的目录联接 → `AI日报/素材/手写`，日报会话确认不会挪）；补了手画的「」『』【】｜和 ①–⑳（圈 + 单线数字）。
- `board.js`（新）：白板版时把 `c.title / c.autoTitle / c.bigWord / c.questionCards / c.statement / c.pointList / c.summary` 换成手写版（参数、返回值兼容）；新增 `c.handText`（HTML → 手写，橙色 span 划黄线）、`c.handNode`（框 + 字）、`c.tape`（胶带）。写字时间窗不会越过场景淡出，窗太短时自动写快一点。
- `board.css`（新）：白底、字幕 56 px 墨黑字白边、目录白卡片 + 橙线、进度条上方白色渐变、印刷小字样式、胶带。
- `core.js`：`BOARD` / `LEAD`；白板版没写 bg_color 也是白底；字幕字号 / 宽度按 `ENG.SUB`；`renderAt` 里场景用 t + LEAD 求值（最后一个场景停在淡出前，等声音到了再淡出）；目录在 `tocInTime + 0.35 − LEAD` 出现，行字墨黑；`body.board`。
- `index.html`：加载 board.css、handdata.js、hand.js、board.js。
- `sync_assets.py`：白板版生成 `handdata.js`（收 scenes.js、board.js、时间轴、episode.json 里出现过的字；第 3 期约 700 字、280 KB），缺字进 WARN；别的期写 `window.__HAND__ = null;`。
- `check_layout.py`：字幕带按 `ENG.SUB`；手写字的墨迹查压字幕 / 角色 / 目录 / 出画布；`hand-late`、`hand-missing` 算 issues。
- `scenes.template.js`：分镜草稿在白板版里从 y 250 写起、每条 ≤ 14 字、场景最后几秒的那条提前写。
- `new_episode.py` / `epcommon.py`：`--style board|cards`、`--voice user|tts`，默认 board / user；`_说明` 和 script_data.py 骨架的画面说明提示同步。
- 文档：visuals.md 新的一节「白板版」、pipeline-contract.md §2 / §7、SKILL.md（第 0、4 步，「画面」原则）、script.md（画面说明写“手写什么、画什么”）、lessons.md 三行、scripts/README.md。
- 改之前的技能备份：`AI科普/_旧稿/skill_yuanlai-ruci-episode_白板和自己配音前_20260928-162020/`。

## 测试（`AI科普/_skilltest/board_switch/`）

- 回归：第 2 期 200 个时刻整帧、第 1 期四组各 200 个时刻，新旧引擎逐像素一致（新引擎多加载 board.css / handdata.js / hand.js / board.js）。
- 白板版（`boardtest.py`，第 3 期时间轴 + 模板分镜草稿；另一组把 S04 换成手画示例：两个 handNode + vs + 箭头 → statement 划线、圈字 → 擦掉 → 贴胶带的代码卡 + 手写要点）：页面无报错，check_layout 0 issues；S03 标题第一笔在 30.56 s，声音 31.5 s（早 0.95 s），字幕按声音出现。拼图 `boardtest/sheet_draft.png`、`sheet_demo.png`。
- 自测中修掉的：handNode 把框宽当成线粗（出来一大块黑）；圈字没跟着那行字淡出；一章最后几秒的草稿长句写不完（hand-late）；「」①②③ 没有笔画。

## 配音（已完成，17:57）

由子任务做完，没有改 new_episode / epcommon / 引擎 / 日报的文件。

- 新增：
  - `scripts/record_script.py`：出录音稿 `配音/录音稿.md`（怎么录、读法表、按章节列段号 + 字幕原文）和提词用的 `.txt`；
  - `scripts/import_voice.py`：多个文件按顺序拼接，1 秒静音隔开，出 44.1 kHz 单声道；70 Hz 高通，每个文件线性调到 −20 LUFS，只压极端爆峰，`--denoise` 可选；`--segment <段号>` 补录单句；
  - `scripts/uservoice.py`：共用模块（识别缓存、全局对齐、按停顿切句）。
- 修改 `segment_audio.py`、`select_takes.py`：
  - 只加了 `--user-voice` 参数和一个分支；由 episode.json 的 `"voice_source": "user"` 触发，没有这一项就走原来的代码；
  - 用户模式：对字幕原文做全局对齐，重读、半句、噪音都跳过，同一句读两遍用后一遍；每句单独切；report.txt 列出匹配 < 0.8 的句子、按声音修正的切点、跳过的声音；`select_takes` 用最新导入的一版（`--take` 选旧版）。
- 回归（AI 配音模式，调用方式和 daily.py 一样，和改前脚本逐字节比）：
  - 第 3 期副本：83/83 个文件一致；
  - 日报 9/28 副本：72/72 一致，加 `--hist` 也一致。
- 合成录音测试：第 3 期分句拼成 6:50，分两个文件，里面有读一半停下、一句读两遍、2 秒噪音、音量不同。结果：
  - 78/78 句切出；
  - 语音主体起止误差最多 11 ms；
  - 半句和第一遍都被跳过，并在报告里列出。
- 文档：voice.md「自己录音」（AI 配音一节保留，标“用户点名时才用”）、scripts/README.md（第 4、4′、4″ 行）、SKILL.md 第 2 步（本会话按子任务的建议写）、pipeline-contract.md（新文件清单）、bilibili.md（自己配音的期不写“配音为 AI 合成”）。
- 录音前能做的：没有录音时 `build_timeline.py` 按字数估时长（已有功能），scenes.js、抽帧自查、封面、投稿草稿都先做；录音到了再重跑时间轴、混音、合成。
- 开场和署名（用户 2026-09-28：“开场还是说我是鲸鱼娘，配音署名写UE”）：
  - 开场照旧“大家好，我是鲸鱼娘”，用户本人的声音念；
  - 片尾清单「配音」一栏和 B 站简介写 UE；
  - 已写进 SKILL.md（第 0、7 步和「内容」原则）、voice.md、script.md、bilibili.md。
- 注意：真人录音的第一期，混音后要听一下人声和 BGM 的比例（mix_audio 按人声峰值归一）。
- 只用合成录音测过，第一次真录音时照报告把列出的地方都听一遍。

## 白板测试（日报会话）后的第二轮修改（2026-09-28 18:00–19:00）

日报会话受用户委托，照文档从零写了第 3 期白板版 scenes.js（788 行）并整片渲染（`_skilltest/board_ep03/`）。流程和技术面全部通过，问题清单在那边的 `白板测试_文档问题.md`：文档缺口 D1–D12、组件问题 C1–C10、画面问题 V1–V14。用户看了样片：「就是这个风格的，没问题，然后封面你也要重新生成一下相同的风格」。

改了（都在 engine-template；改前快照 `_skilltest/board_switch/engine_before_fix2/`）：

- **C1 章末结论早消失**（core.js `boardPlan`）：
  - 每场分内容层（S.root）和标题层（S.head，board.js 的 c.title 画在这里）；
  - 标题照旧早 1 秒擦，下一章标题照旧早 1 秒写在旧结论上方；
  - 内容留到最后一句说完 + 0.15 s 再擦，下一章内容等旧内容擦完再淡入；
  - 最后一场不自己淡出（C10）；
  - 用测试者的 scenes.js 抽帧：118.6 标题已擦、结论还在，118.9–119.2 新标题在写、结论还在，119.7 结论擦完，206.9 对比表完整。
- **C2 疑问 → 目录**：白板版 tocInTime = 疑问场最后一句结束前 0.1 s；每一问缩小飞进目录对应的行再淡出，目录同时出现（抽帧确认）。
- **D1 翻页**：新增 `c.flip(sg)` → {out, in}；模板的分镜草稿也改用它。
- **D2 / C6–C8 写字时间**：
  - c.hand 给了 until 且写不完时自动写快（vmax 70、停顿 0.15、每笔 0.012 s），还超出 0.3 s 以上的记进 ENG.handSlow；
  - 组件的固定写字窗改成“到下一件事之前”；handNode 加 write。
- **C3 / C4 / D9 check_layout 新增**：
  - hand-short：写完显示不到 0.8 s 就被擦；
  - hand-slow；
  - overlap：内容互相压，卡片版也查；
  - phrase-miss：c.P 找不到短语会 warn，卡片版也查。
  - 分镜草稿（draft: true）不查写字时间。
- **小项**：
  - C5 圈的外扩按框高算；
  - C9 胶带贴左上、右下；
  - D10 c.hand / handArrow / handRect 登记 cue；
  - V13 汉字字距 0.96；
  - V14 数字 1 加钩；
  - D6 模板找问题开口先原文、再“第一 / 第二…”；
  - D12 pointList 的 sub 放不下就换行。
- **文档**：visuals.md「白板版」按 D1–D12 重写（时间规矩、翻页、各组件参数、笔画数据、自查、台本写法）；SKILL.md 第 4 步；pipeline-contract §7；scripts/README.md；lessons.md 三行。
- **回归**：第 1、2 期新旧引擎逐像素一致（各 150 帧）；测试者的 scenes.js 在新引擎上 check_layout 0 issues。

之后（日报会话在做，结果记在 AGENTS.md 第 3 期那一节）：

- 用户看了白板封面：「可以，你用插件把封面换一下，视频内容也要换一下」。
- 已发布的第 3 期（BV1WsaG64EwD）封面和视频换成白板版：用这一轮的引擎在测试期重渲，成片和封面放进第 3 期目录，旧的移进 `_旧稿`，编辑页由日报会话操作，视频由用户上传，「提交」由用户点。
- 白板封面由日报会话并进技能：make_cover.py 在 `style: board` 时走白板版，模板 `assets/cover-template/cover.board.html`，cover.md。SKILL.md 第 6 步和 README 的 make_cover 行等它做完由本会话补。

## 白板封面并进技能、第 3 期目录换成白板版（日报会话做，19 点前后）

- `scripts/make_cover.py` 按 episode.json 的 `style` 自动选模板（cover.json 可用 `"style"` 改选）。`board` 走 `assets/cover-template/cover.board.html`：白底、手写标题、讲解员在左下角。笔画用本期引擎的 hand.js / hand_glyphs.py，只收封面上的字，写进 `封面/_handdata.js`。别的期照旧用小票模板。`references/cover.md` 已重写。回归：小票版和原图逐像素一致。备份：`AI科普/_旧稿/skill_yuanlai-ruci-episode_白板封面前_20260928-182335/`。
- 本会话随后补了几处：
  - SKILL.md 第 0 步：白板版的期不用背景图，也不用问；
  - SKILL.md 第 6 步、scripts/README.md 第 13 行；
  - visuals.md「背景」、new_episode.py 的提示；
  - AGENTS.md 背景白色那一行。
- 第 3 期目录已经换成白板版：
  - 卡片版的东西移进 `第03期_Jev模型是什么/_旧稿/卡片版_换白板前_20260928-183039/`；
  - episode.json 加了 `style: board`、`layout: center`，没加 voice_source（第 3 期是 AI 配音）；
  - 字幕、章节文件和卡片版逐字节一样。
- 日报会话提到 29.9 s 一帧进度条有亚像素差异。本会话两边各开两次新页面渲染同一时刻，全部逐像素一致，说明引擎是确定性的，那次差异不是引擎造成的。
- B 站编辑页（换封面、用户上传新视频、用户点「提交」）由日报会话操作，结果记在 AGENTS.md 第 3 期那一节。
- **后来**：用户说「这期已经发布了，先不动，你做得很好，把内容复盘一下更新skill」。结果：
  - 第 3 期不换，B 站编辑页什么都没提交，线上还是卡片版；
  - 日报会话把本期目录还原成卡片版（和发布时一致），白板版整套放在 `第03期_Jev模型是什么/_旧稿/白板版_未发布_20260928-191806/`，测试期 `_skilltest/board_ep03` 也还在；
  - 日报会话在做复盘，改 bilibili.md、SKILL.md 第 7 / 8 步、lessons.md、assemble.md；visuals.md 的缺口由本会话补。
- 日报会话用接口查出第 3 期**线上简介是空的**（desc 长度 0）。投稿时本会话用 Quill setText 写进去、getText() 读回是 559 字，但没存上，原因待查（第 4 期同样是 setText，请日报会话一并查）。补不补等用户定。
- 复盘（用户对日报会话说「把内容复盘一下更新skill」）：
  - 日报会话改了 bilibili.md（§6 看计数、§9 投稿后核对、§10 已发布稿件的修改）、SKILL.md 第 7 步、lessons.md 5 条、assemble.md「卡片版旧期换白板版」；
  - 对照 36 条问题又找出 3 个文档缺口，本会话已补：
    - README「只改 scenes.js」先跑 sync_assets；
    - 完整例子放进技能 `assets/engine-template/scenes.board_example.js`（第 3 期白板版，不会被加载，visuals.md 指向它）；
    - visuals.md「旧一期换白板版」改成要重写 scenes.js。

