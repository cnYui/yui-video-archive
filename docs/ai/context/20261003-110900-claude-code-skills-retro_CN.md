# Claude Code相关 第 3 期复盘 + 技能优化（2026-10-03）

## 用户要求（原话）

“你复盘一下流程，看一下当前claudecode相关的skill有没有可以优化的地方”（第 3 期《You should know 插件》BV1PdHh6QE72 投稿之后）。制作过程见 `20261003-094343-claude-you-should-know-video_CN.md`。

## 复盘结论

- 开工 07:57 → 用户点“立即投稿”09:42（北京时间）= 1 小时 45 分；其中等用户 22 分钟（选封面、定标题、把 mp4 拖进上传页）、配音前让 Tavus 会话用 Chrome / Fish 6 分钟。渲染 4 路 3335 帧每路 90–108 s，`qa_mix` 4 分 45 秒，都不是瓶颈。
- 第 1 期被用户改的四个方向（别讲解要视频、目录 3 条、标题和封面字拆开、配音页面）这期一次做对；用户可见的返工只有封面形象 1 次（我另写脚本画了原创小机器人，被打回）。封面是两期都被打回的环节。
- 我自己发现并修掉的：共用片头片尾当天被别的会话重做（模板过期）、定格点离素材结尾 0.007 s、页面镜头闪空白底、叠加层提前消失、重复画了官方视频里已有的按键提示、封面验收两处误伤、投稿页的坑（创作声明默认空、标签被静默丢）。
- 最大的可压缩时间：事实核对子代理 32 分钟（逐个搜了 1290 个仓库文件）→ 15 分钟时间盒；引擎适配约 40 分钟 → 模板自带 `hold` / `@row` / `note` / `box` 后下一期应当 15 分钟内起步。
- 全文：`Claude Code相关/流程复盘.md`（第 3 期在前：流程表带用时、做对的、返工和前置做法、技能怎么改的、没解决的、下一期清单、数据）。

## 做了什么

1. **新建技能 `claude-code-episode`**（`Claude Code相关/skill/claude-code-episode/`，`C:\Users\yui\.claude\skills\claude-code-episode` 目录联接）
   - `SKILL.md`：11 条硬性要求、「片头片尾（所有视频必加）」一节（和别的技能同格式）、步骤表、文件表、验证说明（包括“没验证的”）。
   - `references/`：`pipeline.md`（全流程、命令、数字、坑）、`facts.md`（事实核对：子代理提示词、15 分钟时间盒、官方来源表、本合集陷阱）、`pages.md`（官方页面 / 推文录屏、叠加层、`hold`）、`voice.md`（Fish 故事工作室空白项目、导出、和别的会话轮流）、`publish.md`（B 站填表：封面两比例分开传、创作声明必选、标签读回、用户改标题只读不写、投后三个接口核对）。
   - `assets/`：`engine-template/`（中英双语引擎，含 `hold`，自带空 `pages.js`）、`script-template/`、`voice-template/`（`build_voice.py` `import_segments.py`）、`submission-template/`、`cover-template/封面候选.json`。
   - `scripts/`：`new_episode.py`（一条命令建一期）、`fetch_x_video.py`（X 嵌入接口取官方直链，断言主机名是 `video.twimg.com`，选最高码率）、`tsheet.py`（带秒数联系表）、`predeliver_check.py`（交付前自查：文件、时长 = 片头 + 正片 + 片尾、2340×1080 / 30 fps、−16±1.5 LUFS、SRT 条数、投稿信息长度限制、封面尺寸和 `check_cover`、片尾条数、`.gitignore` 规则；对第 3 期全过）。
2. **`claude-code-cover` 优化**（`Claude Code相关/skill/claude-code-cover/`）
   - 新增 `scripts/make_candidates.py`：`封面候选.json`（title + 3 个候选）→ 3 个候选 × 16:9 / 4:3 + 逐张 `check_cover` + 总览图 `候选总览.png`；`--only` 重出、`--select A [--force]` 定稿（复制成 `封面_选定_*`，不重新渲染）；检查封面字和标题重复、行宽 > 12 个汉字宽、候选没差别、TODO 没填。
   - `make_cover.py`：自动缩小宇航员的保底改成 16:9 每格 16、4:3 每格 12（身体宽 20%；原来可缩到每格 12 = 15%，验收不过），可用 `--min-cell-16x9 / --min-cell-4x3` 改；像素小星光不再落在 16:10 会被裁的两侧（不用为安全区验收换 `--seed`）；提示文字改成“字和宇航员抢横向空间”。
   - `check_cover.py`：可一次给多张 PNG（各读同名 `.meta.json`），全部合格退出码 0。
   - `SKILL.md` 重写：硬性要求第 1 条写明“官方形象、不自造”（用户 2026-10-03：“太丑了，而且这都不是 claude 的形象”）、封面协定、流程（候选清单 → `make_candidates.py` → 总览图 → 用户选 → `--select`）、B 站上传改成“双比例同步改动不勾、两个位各传各的”；`references/design.md` 加字号 / 保底说明和三条被否掉的做法。
   - 第 3 期 `制作/04_封面/封面候选.json` 留档（A night + float2「别漏看重点 / Claude 新插件」、B orange + float3「You should know / 官方新插件」、C ivory + stand「它替你盯着 / Claude 的输出」）。
3. **共用引擎模板**：`hold`（定格）的三处改动（`build_timeline.py` `prep_frames.py` `mix_audio.py`）和“定格点离素材结尾 ≥ 0.1 s”的断言回补到 `OpenAI相关/skill/openai-episode/assets/engine-template/`，`references/pipeline.md` 补了 `hold` 写法（只有写了 `hold` 才有行为变化）；两份模板的 `build_timeline.py` 文档串里也写了 `hold`。
4. **文档**：`Claude Code相关/README.md`（技能两条、第 03 行标题 / 状态、规矩 2 / 4 / 5）、`Claude Code相关/流程复盘.md`、`AGENTS.md`（目录树、技能联接、Claude Code相关一节加“复盘和技能优化”条、封面技能适配说明）、根 `README.md` 技能列表；记忆 `claude-code-episode-skill-entry.md`（新）、`claude-code-series-cover-rules.md`（更新）、`MEMORY.md`。

## 验证

- `new_episode.py` 在临时目录建一期 → 填第 3 期的官方视频 → `build_timeline.py --est` → `check_subs.py`（没问题）→ `prep_frames.py` → `render_all.py --stills-segs`：0 报错（第一次报缺 `pages.js`，模板补了空文件），静帧里中英双语字幕、左栏目录、`hold` 定格都对。
- `make_candidates.py` 按第 3 期候选清单重出：A、B 的 16:9 / 4:3 和当时的封面逐像素一致；C 因为小星光避开两侧，不再需要 `--seed 2`；`--select` 的覆盖保护（没加 `--force` 退出码 2）、`--only` 重出、标题重复 / 行宽 / TODO 提示都试过。
- `check_cover.py` 多张验收：第 3 期 A / B / C 全部合格（退出码 0）。
- 所有 `.py`（`ast.parse`）、`.js`（`node --check`）、`.json` 过了语法检查。
- **没验证的**：事实核对子代理、Fish、B 站这几个联网步骤只是照第 3 期实际操作写进文档，下一期照做时页面变了要改文档（SKILL.md 里写明）。

## 没做 / 待办

- 线上标题带残留（“：/”、双空格，用户手改的）：改不改听用户的。
- 合集归属要等过审后用 `x/web-interface/view` 的 `ugc_season` 核对；GitHub release / 提交 git 没做（用户没说）。
- 配音 6 句机器分低（N01 N12 N15 N18 N20 N21）用户没听过；片尾清单是我拟的草稿。
- 两份引擎模板（`openai-episode`、`claude-code-episode`）只差素材表和场景叠加层，以后可以抽成共用引擎（不急）。
