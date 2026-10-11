# 本地分支收尾（2026-10-10 晚 – 10-11）

用户：“你看一下本地那些已经完成但还存在的分支，把它们收收尾，该提交的提交，提交完了在本地删掉。”

## 根仓库 `D:\大疆`

收尾前：`main`（领先 origin 3）+ 5 条分支 + 3 个工作树。

| 分支 | 情况 | 处理 |
|---|---|---|
| `claude/exciting-jones-14b7e8` | 9/29，已在 main 里；工作树干净 | 移除工作树、删分支 |
| `claude/bilibili-comment-reply-304462` | 9/29，已在 main 里；工作树有一处没提交的 AGENTS.md「回复评论」段 + 一份记录 `20260929-173338-bilibili-comment-reply_CN.md` | AGENTS.md 那段的内容已经被 B站互动 技能（`references/ui.md`）取代，没搬；记录拷进主目录 `docs/ai/context/`（含观众原话，已加进 .gitignore，不进公开仓库）。补丁存档在会话 scratchpad。移除工作树、删分支 |
| `claude/ai-era-cs-grad-skills-1a823b` | 9/30 已 squash 合并进 main（72c6dc1，原因：分支历史里有原始逐词转写 asr/*.json） | **先把工作树里不进 git 的 27,207 个文件（2.4 GB：第 1 期的混音、出镜 proxy / audio、录屏素材、帧、封面候选）挪回主目录同名目录**（同盘改名、不覆盖；主目录已有的 42 个逐字节相同，跳过），再移除工作树、删分支（-D，squash 过） |
| `claude/sonnet55-haiku55-video` | 主目录当时的分支；那期已发 B 站 BV1fcpi6oEmu，04→05 改名和投稿信息没提交 | 补一次提交（8265d4e）→ main 快进 → 主目录切回 main → 删分支 |
| `claude-projects-video-script` | Claude Projects 长视频，提交信息写着“做到一半”，那个会话当时还在跑 | **没动**（不是“已完成”的） |

之后主目录在 `main`，又按区域分了 9 次提交（fc1cf4b … 7543878）：.gitignore + README + docs 工具、AI每日日报（10/01–10/10）、原LAI如此（技能、片头片尾、第 1–4 期封面）、Way to AGI、CS 研究生技能、Claude Code相关、OpenAI相关 / 短视频技能 / Claude官方教程 / AI实操 / 爱发电、独立视频（已定公开范围的几条）、docs/ai/context 记录。**都只在本地，没有推送**（main 现在领先 origin 14）。

### 没提交的（要用户定 / 要审）

1. **AGENTS.md「待办」里原来就挂着的两项**（“提交前要用户定”）：AGENTS.md 和 B站互动 技能里写着用户住在哪个国家；AGENTS.md、原LAI如此第 5 / 6 期 `episode.json` / `timeline.json` / 第 6 期 `台本.md` 和两份第 5 期记录里有「悠一」声音的 Fish Audio modelId。所以 AGENTS.md、`AI科普/第05期…`、`第06期…`、`_staging/ep05_*`、`B站互动/`、`20260930-194505 / 195953 / 201800` 三份记录没提交。
2. **独立视频里还没写公开范围规则的条目**：AlexandrWang 1–6、Palantir、显得无害、image-blaster、MuseGadgets、text-to-cad、不再Review（短视频）、TimDenning 1–6 + 系列目录、GPU 指南、强化学习两条、论文格式、Claude封号潮，以及白宫协议、Fable5.5、Harness 阵营——同传 / 文章精选类会带别人原话的转写和译文（仓库以往的规矩是不公开），要逐条审过再收。
3. Claude Projects 那个会话的文件（`Claude Code相关/04_ClaudeProjects/` 和它的记录）留给那个会话。

### 新加的 .gitignore 防护（扫出来的个人信息）

- `docs/ai/context/20260929-173338-bilibili-comment-reply_CN.md`、`20261008-140000-douyin-gintama-comment-replies_CN.md`：观众昵称和评论原话；
- `20261001-122000-ai-practice-ep01-workbuddy-miniprogram_CN.md`：账号邮箱；
- `20261004-214700-claude-cost-short-video-approval_CN.md`：所在城市；
- `AI实操/01_…/制作/00_整片/privacy/`（录屏整屏 OCR，含邮箱）和 `privacy_ocr.py`（注释里写着邮箱）。

### 顺手

- 根目录一个误生成的文件 `游戏素材银魂录屏素材2026-10-04_精彩展示_成片抽帧bgm_astats.txt`（bash 吃掉了反斜杠）挪回了它本来的位置 `游戏素材\银魂\录屏素材\2026-10-04_精彩展示\_成片抽帧\bgm_astats.txt`。
- **公开远程上还有一条旧分支** `origin/claude/ai-era-cs-grad-skills-1a823b`（385db12），里面有 9 个原始逐词转写 `asr/*.json`。要不要删远程分支（对外操作），等用户说。

## JoJo 游戏仓库 `游戏素材\JoJo\游戏\`（独立本地仓库）

体验版分支 `demo/prologue-ch1` 已完成：打标签 `demo-20261010`（3a79f76）留底，分支改名为 `main`。之后的工作按章开分支（`ch2` …），做完并回 main 再删。详见 `20261011-*-jojo-ch2-remake_CN.md`。
