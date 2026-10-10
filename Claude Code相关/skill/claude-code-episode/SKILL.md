---
name: claude-code-episode
description: 制作「Claude Code相关」合集一期视频的完整流程：把 @ClaudeDevs 等官方账号的 X 推文视频 + claude.dev / code.claude.com 官方页面、更新日志做成“多放真实画面少讲解”的短片——曼波声线画外音（Fish 故事工作室空白项目）+ 中英双语字幕（中文一行 + 英文一行烧进画面，另出三份 SRT）+ 事实核对前置（官方原文为准、官方没写的明说）+ 官方像素宇航员封面（见 claude-code-cover）+ 共用片头片尾 + B 站投稿。用户提到 Claude Code 新功能 / 更新 / 插件 / mod（模组）/ 官方发布、ClaudeDevs 的推文或视频、claude.dev 博客、“做下一期 Claude Code相关”、“下载这些视频读文章做一个宣传 Claude 新功能的视频”、“和之前那期 Claude mod / You should know 一样”，或给这个合集补字幕 / 做封面 / 投稿时，都用这个技能。
---

# Claude Code相关 · 一期视频的完整流程

合集在 `D:\大疆\Claude Code相关\`（B 站合集「Claude Code相关」id 9223239，用户在投稿页里建的）。本技能是照第 3 期《You should know 插件》（BV1PdHh6QE72，第一条做中英双语的）整理的，第 1 期《Claude mod 发布》（BV1Zoa16CEeU）和第 3 期的复盘（每步用时、返工原因、技能怎么改的、下一期清单）在 `流程复盘.md`。封面是另一个技能 `claude-code-cover`。

## 硬性要求（前三期踩出来的，每期都满足）

1. **内容只写官方原文能对上的事，事实核对前置**：素材一下完就起后台调研子代理（`references/facts.md`，**15 分钟时间盒**），产出“能写 / 不能写”清单，台本照它写。**推文常常省掉前提**——第 3 期推文只说 “Enable it with”，文档和更新日志才写着“默认关闭、第一方会话 + 遥测开着、组织可用”；官方没写的（用哪个模型、会不会误报、多花不多花额度、源码是否公开）一律写“官方没写”，别猜。日期不写几号（美国时间和北京时间差一天），写“这几天”。
2. **画面 = 真实素材**：官方演示视频 + 官方页面 / 推文录屏（`references/pages.md`）≥ 90%，不做整屏文字卡片；演示视频上叠中文译文条和高亮框（原视频里是英文）；静止的画面用 `hold`（定格）撑到旁白说完，不拉慢素材。
3. **字幕中英双语**：台本每句 `zh` / `say` / `en` 三栏（缺 `en` 引擎直接报错），中文一行 52 px + 英文一行 30 px 烧进画面（y 922 以下），另出三份 SRT（双语 / 中文 / 英文，时间含片头）。标准在 `Way to AGI/skill/way-to-agi-episode/references/subtitles.md`；**复制任何旧引擎之前先对这个标准**（OpenAI 第 1 期漏过英文）。
4. **左栏目录 ≤ 3 条、每条 ≤ 7 字**，说到哪条亮哪条。
5. **配音用 Fish 网页版故事工作室的空白项目**（声音「温柔男生」（用户 2026-10-04：“之后语音合成使用温柔男生这个配音”；之前用「赛马娘（曼波欧耶版）」）、S2 Pro），不碰共享的 TTS 草稿；逐句导出 zip 用 `import_segments.py` 按 metadata.csv 逐句核对文字再放进 `tts/seg_raw/final/`；机器识别分低的句子（多是 Claude / /plugin / 英文名）列给用户**耳朵听**。和别的会话共用 Chrome / Fish 时先 `SendMessage` 约好、轮流用、用完发消息还（`references/voice.md`）。
6. **封面用 `claude-code-cover`**：官方像素宇航员（要大）+ Claude 品牌色，先出 3 个候选让用户选。**别用自己画的原创角色顶替**（第 3 期第一版被用户打回：“太丑了，而且不是 claude 的形象”）；封面协定：只放简短大字、没有小字，标题写详细、两边不写同一句。
7. **片头片尾必加**（用户 2026-10-03）：`finish.py` 调共用的 `add_to_video.py`，时长从 `D:\大疆\AI科普\片头片尾\pack_info.py` 读（现在片头 4.8 s、片尾 9.0 s，**别写死**）；片尾 `outro.json` 要 `references`（参考文献）+ `thanks`（致谢），每期问用户，给的是草稿。**复制模板前先看 `docs/ai/context` 最新几份记录**（共用资产当天会被别的会话改）。
8. **渲染统一 4 路、同一时间只跑一个渲染**（先 `ListAgents` 看别的会话、看空闲内存，< 6 GB 用 `RENDER_WORKERS=3`）；静帧逐张看；出片前 `qa_mix.py`（混音按字幕逐句识别）、抽成片帧、`scripts/predeliver_check.py` 自查。
9. **投稿**：用户把 mp4 拖进 B 站投稿页（插件传不了 10 MB 以上），我用 Chrome 插件填表；**停在“立即投稿”前，用户明说“发布”才点**；用户在页面里手改标题时**只读不写**，线上标题以页面为准；填表时自己点开“加入合集”下拉选「Claude Code相关」（别凭印象）；投完用接口核对（`references/publish.md`）。
10. **Bash 命令文本里别带“递归强删”那个命令的字样**（哪怕只是示例标签文字），dcg 钩子会整条拦掉：不绕，改用 Edit / Write 写文件，或把脚本写成文件再运行。
11. **多个会话同时在干活**：渲染、Chrome、Fish、共用文件都可能被别的会话占着或改过；开工 `ListAgents`、`ls -t docs/ai/context | head`，要用就先发消息约。

## 片头片尾（所有视频必加）

用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”。所有合集、所有视频共用一套，不另做、不省略、不改模板。**例外：短视频开头结尾都不加**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”；短视频走 `short-video` 技能，见 `D:\大疆\短视频\skill\short-video\SKILL.md`）。

| | 路径 / 命令 | 时长 |
|---|---|---|
| 片头 | `D:\大疆\AI科普\片头片尾\intro\index.html`（数据 `intro\data.json`：悠一 · AI鼓励师） | 4.8 s |
| 片尾 | `D:\大疆\AI科普\片头片尾\outro\index.html`（数据格式见 `outro\data.example.json`） | 9.0 s |
| 本技能怎么加 | `finish.py`（调 `python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data <片尾.json> -o <成片.mp4>`；SRT 时间 = 显示区间 + `common.INTRO_SEC`，从模板读） | |
| 时长（脚本里读，别写死） | `D:\大疆\AI科普\片头片尾\pack_info.py` 的 `intro_seconds()` / `outro_seconds()`（`python pack_info.py` 打印路径和时长） | |

- 片尾 JSON：`references`（参考文献，≤ 8 条）、`thanks` / `items`（致谢 / 制作清单，≤ 8 条）、`closing`（感谢语）、`signature`（悠一），放在 `制作\00_整片\outro.json`；**每期问用户**，不沿用上一期。
- SRT、B 站章节时间 = 正片时间 + 片头时长（现在 4.8 s）。
- 交付前自查：`scripts/predeliver_check.py`（总时长 = 片头 + 正片 + 片尾，片尾 JSON 条数不超限）。

## 步骤

```bash
cd "D:\大疆\Claude Code相关\skill\claude-code-episode\scripts"
python new_episode.py --num 04 --name 短名                       # 目录骨架 + 引擎模板（中英双语）+ 台本骨架 + 配音脚本 + 投稿信息脚本 + 随机挑一张横版背景印花（bg.png）；打印要补的 .gitignore 行
python fetch_x_video.py <推文链接> [更多…] --out "<本期>\素材\X平台视频_ClaudeDevs"   # 官方视频：X 嵌入接口给 video.twimg.com 直链，不用 TwitterSaver
python tsheet.py <视频> <联系表.png> 1 5 480                      # 带秒数的联系表，先看素材内容
```

**背景印花**（用户 2026-10-05：“长视频背景也加上和短视频 skill 中相同的背景图片……之后横板视频也要随机选一张图片”）：`new_episode.py` 自动调 `D:\大疆\短视频\skill\short-video\assets\backgrounds\pick_bg.py`，从三张横版印花 `landscape_*.png`（原色 / 墨色 / 橙色）里**随机挑一张**拷成 `制作\00_整片\bg.png`，`bg.json` 记挑了哪张（重渲不会换）；`--bg landscape_ink.png` 指定、`--bg none` 不用（不用时把 `index.html` 里的 `url(bg.png)` 去掉）。模板 `index.html` 的 `html, body` 背景已经是 `#fff url(bg.png) …`；独立视频也是拷这个模板，同样有。

| 步 | 做什么 | 文档 |
|---|---|---|
| 0 | 读 AGENTS.md 的「共同约束」和「Claude Code相关」、同合集最新一期、`docs/ai/context` 最近记录；问用户：标题 / 封面字各写什么（不重复）、片尾清单、要用的链接；`ListAgents`；`new_episode.py`；补 `.gitignore` | pipeline.md §0 |
| 1 | 下载官方视频（`fetch_x_video.py`）、看素材（联系表、有没有人声）；**同时起事实核对子代理** | pipeline.md §1–2、facts.md |
| 2 | 台本 `录制稿.json`（zh / say / en）+ 画面表 `plan.json`；`capture_pages.py` 录官方页面 / 推文；`scenes.js` 写叠加层 | pipeline.md §3–4、pages.md |
| 3 | `build_timeline.py --est` → `check_subs.py` → `prep_frames.py` → `render_all.py --stills-segs`（逐张看版面） | pipeline.md §5 |
| 4 | 配音（故事工作室）→ `import_segments.py` → `build_voice.py --qa` → 重跑 `build_timeline.py` / `prep_frames.py` | voice.md |
| 5 | `mix_audio.py` → `render_all.py`（4 路）→ `qa_mix.py` → 抽成片帧 → `finish.py`（片头片尾 + 手机预览 + 三份 SRT） | pipeline.md §6–7 |
| 6 | 封面（claude-code-cover 的 `make_candidates.py`，3 个候选）→ 用户选 → `--select` | claude-code-cover/SKILL.md |
| 7 | `make_submission.py` → 用户拖 mp4 → 填表 → 用户说发布 → 接口核对 → `predeliver_check.py` | publish.md |
| 8 | 记录：`docs/ai/context`、AGENTS.md、合集 README、根 README、`流程复盘.md`、记忆 | pipeline.md §8 |

## 文件

- `references/`：`pipeline.md`（全流程、命令、数字、坑）、`facts.md`（事实核对：子代理提示词、官方来源、本合集的常见陷阱）、`pages.md`（官方页面 / 推文录屏、叠加层、`hold`）、`voice.md`（Fish 故事工作室 + 导出 + 和别的会话轮流）、`publish.md`（B 站填表、封面两比例、标签、用户改标题、投后核对）。
- `assets/engine-template/`：引擎模板（`index.html` `engine.js` `scenes.js` `common.py` `build_timeline.py` `check_subs.py` `prep_frames.py` `mix_audio.py` `render_all.py` `qa_mix.py` `finish.py` `capture_pages.py` `outro.json` 和一个空的 `pages.js`）；`assets/script-template/`（台本骨架）、`assets/voice-template/`（`build_voice.py` `import_segments.py`）、`assets/submission-template/make_submission.py`、`assets/cover-template/封面候选.json`（给 `claude-code-cover` 的 `make_candidates.py`）。
- `scripts/`：`new_episode.py`、`fetch_x_video.py`、`tsheet.py`、`predeliver_check.py`。
- 引擎版式：2340×1080、白底；演示区页面 1504×859（内容坐标 1474×829 不缩放）在 (718, 40)；左栏 (118, 470)；字幕带 y 922；强调色 #FF4F1A。时间模型：场景（`clip` / `card`）+ 场景里的 `lines: [{id, a}]`；`ranges` 里 `{"src", "in", "out"}` 是素材段，`{"src", "in", "hold": 秒}` 是定格。

## 验证过

模板在 2026-10-03 从第 3 期整理；`new_episode.py` 在临时目录建出的骨架，填上第 3 期的素材后跑通了 `build_timeline.py --est` → `check_subs.py` → `prep_frames.py` → `render_all.py --stills-segs`（0 报错，静帧里中英字幕、左栏目录、`hold` 定格都对）；`fetch_x_video.py` 下载的第 3 期推文视频和已用的文件逐字节一样（11,958,366 字节）；`predeliver_check.py` 对第 3 期全部通过；`claude-code-cover/make_candidates.py` 按第 3 期的候选清单重出，A / B 和当时的封面逐像素一致；所有 py / js / json 过了语法检查。**没验证的**：`fetch_x_video.py` 之外的联网步骤（事实核对子代理、Fish、B 站）都是照第 3 期的实际操作写的，下一期照做时若页面变了要改文档。
