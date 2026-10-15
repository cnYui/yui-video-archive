---
name: openai-episode
description: 制作「OpenAI相关」合集一期视频的完整流程：把 X 平台上网友晒的 OpenAI 模型实测视频 / OpenAI 官方发布会画面做成“多放素材少说话”的短片——曼波声线画外音（Fish 故事工作室）+ 中英双语字幕（中文一行 + 英文一行烧进画面，另出三份 SRT）+ 事实核对（官方原文为准、网友说法挂名）+ OpenAI 蓝封面（见 openai-cover）+ B 站投稿。用户提到 OpenAI 相关视频、GPT / Sol / Astra / dots / Codex / DevDay 的模型效果展示或发布会解读、“做下一期 OpenAI”、“用 twittersaver 下载这些视频然后做一个宣传模型的视频”、“和之前 fable5.5 / GPT 模型效果展示那期一样”、给这个合集补字幕 / 补英文时，都用这个技能。
---

**默认发布平台（2026-10-14 用户定）：短视频、长视频在用户未指定平台时仅发 B 站；不打开、不上传其他平台。用户明确要求其他平台时才启用对应流程。平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。**

**上传方式（2026-10-14 用户定）：文件小于 10 MB 且本轮已授权自动上传时，可用 Playwright JS 上传完整文件；达到或超过 10 MB 就提醒用户手动上传。不为自动上传压缩、分块或改用低清版本。用户手动上传后继续填表，已授权发布则读回核对后点击发布。**


# OpenAI相关 · 一期视频的完整流程

合集在 `D:\大疆\OpenAI相关\`（B 站合集「OpenAI相关」，用户建的，里面已有 DevDay 解读 4 条等；本技能第 1 期《GPT-6.1 Sol / GPT-6 Astra 模型效果展示》BV1wYaU6oEbw 是照这条流程做的）。做法从 2026-10-02 早上的《Claude Fable 5.5 模型介绍》一路传下来：**全程画外音 + 真实素材 + 左栏目录 + 字幕在下面**，不放出镜框、不做整屏文字卡片。每一步的细节、命令、坑在 `references/`，复盘（做错的地方）在 `D:\大疆\OpenAI相关\流程复盘.md`。

## 硬性要求（第 1 期踩出来的，每期都满足）

1. **字幕必须中英双语**：台本每句写 `zh` / `en` / `say` 三栏，引擎里中文一行 52 px + 英文一行 30 px 烧进画面（y 922 以下），成片同时出三份 SRT（双语 / 中文 / 英文）。第 1 期漏了英文，是因为我复制了 Fable 那套中文单行引擎、没看同合集 DevDay 那批已经统一的双语做法。细节见 `references/subtitles.md`。
2. **事实先查再写台本**：开工就让调研子代理按官方原文核对（模型名、日期、价格、渠道、网友帖子里的数字和名字），产出“能写 / 不能写”清单，台本照它写；网友的说法一律挂名（“发帖的人说”），官方没有的名字不写成官方（第 1 期查出“GPT-6.1 Astra”根本不存在）。流程和提示词见 `references/facts.md`。台本写完再改事实 = 配音返工。
3. **画面 = 真实素材**：网友作品视频 + 官方发布会画面（用 DevDay 主题演讲的无声画面 + 单独音频），不做整屏文字卡片；素材画面 ≥ 90%，画外音不超过约 31%（Fable 同档）。
4. **左栏目录 ≤ 3 条、每条 ≤ 7 字**（缩略图 + 名字，说到哪条亮哪条）。
5. **配音用 Fish 网页版故事工作室的空白项目**（声音「温柔男生」（用户 2026-10-04：“之后语音合成使用温柔男生这个配音”；之前用「赛马娘（曼波欧耶版）」）、S2 Pro），不碰所有标签页共享的 TTS 编辑框；逐句导出再拼。`references/voice.md`。
6. **开工先问用户**：标题写什么 / 封面字写什么（两边不重复；**封面和标题的协定**（用户 2026-10-03：「封面文字中最下面一行的小字可以删除，因为用户根本看不见……封面中的文字要简略要大，标题则需要详细，这个规则对我目前做的所有的视频skill都要生效」）：封面上只放几个**简短的大字**（关键词 / 钩子），**不放最下面那行小字**（副标题、说明、清单、来源署名之类，缩到信息流里根本看不见）；**标题写详细**，把封面放不下的信息（时间、数量、对象、结论……）写进标题，不和封面是同一句。例：封面「大模型 / 谁夯谁拉？」→ 标题「2026下半年大模型谁夯谁拉？18个模型锐评」。系列名、期号这类合集标识照旧。）、片尾（参考文献 + 致谢）、素材链接；**自己去 B 站投稿页的“加入合集”下拉里看有没有 OpenAI 合集**（第 1 期我没点开就说“没有”，其实用户已经建好了）。
7. **渲染统一 4 路、同一时间只跑一个渲染**（先 `ListAgents` 看别的会话在不在渲染、看空闲内存，< 6 GB 用 `RENDER_WORKERS=3`）；出片前把混音按字幕逐句识别一遍（`qa_mix.py`）、抽成片帧看一遍版面。
8. **投稿**：用户把 mp4 拖进 B 站投稿页（253 MB 插件传不了），我用 Chrome 插件（Chrome 插件连不上浏览器时改用 Playwright（插件工具，或桥接脚本 `pw_do.py` + `docs\pw\token.env` 里的令牌），见 `D:\大疆\docs\发布备用_Playwright.md`）填表；用户明说“发布 / 填表发布”才点“立即投稿”；投完用接口核对。`references/publish.md`。
9. 封面：**用 `openai-cover` 技能**（OpenAI 蓝 + 黑底，版式固定，先出 3 个候选让用户选）。
10. **片头片尾必加**（用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”）：`finish.py` 调共用的 `add_to_video.py`，见下面「片头片尾」一节。

## 片头片尾（所有视频必加）

用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”。所有合集、所有视频共用一套，不另做、不省略、不改模板。**例外：短视频开头结尾都不加**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”；短视频走 `short-video` 技能，见 `D:\大疆\短视频\skill\short-video\SKILL.md`）。

| | 路径 / 命令 | 时长 |
|---|---|---|
| 片头 | `D:\大疆\AI科普\片头片尾\intro\index.html`（数据 `intro\data.json`：悠一 · AI鼓励师） | 4.8 s |
| 片尾 | `D:\大疆\AI科普\片头片尾\outro\index.html`（数据格式见 `outro\data.example.json`） | 9.0 s |
| 本技能怎么加 | `finish.py`（调 `python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data <片尾.json> -o <成片.mp4>`（正片不重编码，片头片尾按视频原尺寸渲染，下面垫系列 BGM）；SRT 时间 = 显示区间 + `common.INTRO_SEC`，从模板读） | |
| 时长（脚本里读，别写死） | `D:\大疆\AI科普\片头片尾\pack_info.py` 的 `intro_seconds()` / `outro_seconds()`（`python pack_info.py` 打印路径和时长） | |

- 片头：Claude 品牌色（米白 #FAF9F5 底、墨色 #141413、橙 #D97757 / 黄 #F5DB9A 强调），`>` → `{ }` → `</>` → 神经网络 → LLM 芯片 → 对话气泡里打出“悠一”，下面“AI鼓励师”。
- 片尾：纸飞机送来一页信纸，左栏参考文献、右栏致谢、感谢语、签名和朱印（悠一）。片尾 JSON：`references`（参考文献，字符串，≤ 8 条，可空）、`items`（致谢 / 制作清单 `{label, value}`，≤ 8 条）、`closing`（感谢语）、`signature`（悠一）。`outro.json` 放在 `制作\00_整片\`。**每期问用户**，不沿用上一期、不用模板默认值。
- SRT、B 站 / YouTube 章节时间 = 正片时间 + 片头时长（现在 4.8 s）。
- 交付前自查：开头是片头、结尾是片尾，总时长 = 片头 + 正片 + 片尾。


## 步骤（每步的命令和坑在 `references/pipeline.md`）

```bash
cd "D:\大疆\OpenAI相关\skill\openai-episode\scripts"
python new_episode.py --num 02 --name 短名            # 目录骨架 + 引擎模板（中英双语字幕）+ 台本骨架 + 封面规格 + 随机挑一张横版背景印花（bg.png）；打印要补的 .gitignore 行
```
**背景印花**（用户 2026-10-05：横版视频背景加上和短视频相同的印花，之后随机选一张）：`new_episode.py` 自动调 `D:\大疆\短视频\skill\short-video\assets\backgrounds\pick_bg.py`，从三张横版印花 `landscape_*.png`（原色 / 墨色 / 橙色）里**随机挑一张**拷成 `制作\00_整片\bg.png`，`bg.json` 记挑了哪张（重渲不会换）；`--bg landscape_ink.png` 指定、`--bg none` 不用（不用时把 `index.html` 里的 `url(bg.png)` 去掉）。模板 `index.html` 的 `html, body` 背景已经是 `#fff url(bg.png) …`。
然后在 `<本期>\制作\00_整片\` 里：

| 步 | 做什么 | 脚本 / 文档 |
|---|---|---|
| 1 | 下载素材（TwitterSaver，解 JWT 核对源站，X 嵌入接口读全文和时间）、写 `素材/X平台视频/来源.md` | pipeline.md §1 |
| 2 | 看素材：带时间标签的联系表、有没有人声、响度 | pipeline.md §2 |
| 3 | 事实核对（后台调研子代理）→ 台本 `录制稿.json`（zh / say / en）+ 画面表 `plan.json` | facts.md、pipeline.md §3 |
| 4 | 填 `common.py` 素材表 → 配音（故事工作室）→ `build_voice.py` | voice.md |
| 5 | `build_timeline.py` → `check_subs.py` → `prep_frames.py`（增量）→ `render_all.py --stills-segs` 看版面 | pipeline.md §5 |
| 6 | `mix_audio.py` → `render_all.py`（4 路）→ `qa_mix.py` → 抽成片帧自查 | pipeline.md §6 |
| 7 | `finish.py`（悠一片头片尾 + 手机预览 + 三份 SRT + 响度报告） | pipeline.md §7 |
| 8 | 封面（openai-cover）、投稿信息草稿 | publish.md |
| 9 | 用户把 mp4 拖进投稿页 → 插件填表 → 投稿 → 接口核对 → 补 AGENTS.md / README / 记录 / 记忆 | publish.md |

## 文件

- `references/`：`pipeline.md`（全流程、命令、坑）、`subtitles.md`（双语字幕标准在这个合集里怎么落地）、`facts.md`（事实核对流程 + 子代理提示词模板 + 官方来源）、`voice.md`（Fish 故事工作室配音）、`publish.md`（B 站投稿页填表、合集、核对）。
- `assets/engine-template/`：引擎模板（`index.html` `engine.js` `scenes.js` 和 `common.py` `build_timeline.py` `check_subs.py` `prep_frames.py` `mix_audio.py` `render_all.py` `qa_mix.py` `finish.py` `outro.json`），从第 1 期整理，字幕改成中英双语；`assets/voice-template/build_voice.py`；`assets/script-template/`（台本 / 画面表骨架）。
- `scripts/new_episode.py`：新建一期。
- 引擎的版式（2340×1080、白底、OpenAI 蓝强调色、演示区 1504×859 在 (718, 40)、左栏 (118, 470)、字幕带 y 922）和叠加层的写法（`ui`：`nt` / `cr` / `cap` / `stack`）见 `references/pipeline.md` §4。
- 带原话同传（把发布会里的英文原话配中文同传）的片子，引擎要用 `独立视频/2026-10_OpenAI-DevDay-2026解读/制作/00_整片/build_timeline.py` 的 `clip` 块（本模板没有这部分）。

## 验证过

模板在 2026-10-02 用第 1 期的台本（加了英文）跑过：时间轴和已发布成片逐句一致（198.7 s / 5961 帧）、25 条字幕、三份 SRT 导出正常；精简计划 + 一条故意写很长的句子出静帧、`check_subs.py` 通过（中文最宽 1240 px、英文最宽 1204 px、演示区下沿 899 ≤ 912；长句自动拆成 3 条、中英断点对得上）。
