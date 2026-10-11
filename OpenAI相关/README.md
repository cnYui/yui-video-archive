# OpenAI相关

悠一的新合集（2026-10-02 开）：和 OpenAI 有关的产品信息和模型实测，一条条做成短视频。做法照 `Claude Code相关/`：全程画外音（Fish 网页版曼波声线）+ 真实素材（网友作品视频、官方发布会画面），少放静态文字卡片；发 B 站合集「OpenAI相关」（用户已建）；YouTube 待定。**做新一期用技能 [`skill/openai-episode/`](skill/openai-episode/SKILL.md)（整条流程 + 中英双语引擎模板）和 [`skill/openai-cover/`](skill/openai-cover/SKILL.md)（封面）**；第 1 期做错的地方和前置做法见 [流程复盘.md](流程复盘.md)。

- 第 1 期 `01_GPT模型效果展示/`：9 个 X 平台网友作品（Sol / Astra）+ 发布会官方画面 + 曼波画外音，成片 3:27（含悠一片头片尾）。**已投稿 [BV1wYaU6oEbw](https://www.bilibili.com/video/BV1wYaU6oEbw/)（2026-10-02 21:14 JST，封面用 B；我投稿时漏选了合集，这条还没在「OpenAI相关」里）**；用户没有先听配音，片尾清单用的是草稿内容；**成片只有中文一行字幕**，英文没烧进画面——台本补了每句 `en`，三份 SRT（`01_GPT模型效果展示/GPT模型效果展示_双语字幕.srt` 等）在成片旁边。进度、做法和坑见 `docs/ai/context/20261002-172700-openai-gpt-models-showcase-video_CN.md`，事实核对见 `01_GPT模型效果展示/台本/事实核对.md`，投稿草稿见 `01_GPT模型效果展示/投稿信息_草稿.md`。

## 这个合集的规矩（沿用 + 这期新加的）

1. **事实只写官方原文对得上的**；网友的说法一律挂名（“发帖的人说”“Higgsfield 说”），不当事实；官方没有的名字（GPT-6.1 Astra、ultra code mode）不写成官方模型 / 模式，原帖写错的在小字里注明。
2. **画面 = 真实素材**：网友作品视频 + 官方发布会画面；下载前解 JWT 核对源站是 `video.twimg.com`；每条标来源账号、转发的标原作者。
3. **字幕中英双语**：中文一行 52 px + 英文一行 30 px 烧进画面，另出三份 SRT（双语 / 中文 / 英文）；台本每句 `zh` / `say` / `en` 三栏，缺 `en` 引擎直接报错。标准见 `Way to AGI/skill/way-to-agi-episode/references/subtitles.md`，引擎模板和 `check_subs.py` 在 `skill/openai-episode/`。
4. 左栏目录最多 3 条（每条 ≤ 7 字）；配音 Fish 网页版 S2 Pro 曼波声线，**用故事工作室的空白项目做，不动共享的 TTS 草稿**（做法见 `skill/openai-episode/references/voice.md`）。
5. **封面**：OpenAI 蓝 #0285FF + 黑底白字 + 左蓝竖线，不放 OpenAI 标志；封面字和标题不写同一句；出 16:9 + 4:3；用技能 `skill/openai-cover/`（版式已固定，出 A / B / C 三个候选让用户选）。
6. **片头片尾必加**（用户 2026-10-03：所有生成的视频都要加）：模板 `AI科普/片头片尾/`（片头 4.8 s 对话气泡、片尾 9.0 s 信纸：参考文献 + 致谢），加法 `python AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py <正片> --outro-data <片尾.json>`，SRT / 章节时间加 4.8 s，片尾内容每期问用户；投稿由用户把 mp4 拖进页面，我用插件填表，用户点“立即投稿”；**填表时自己点开“加入合集”下拉选「OpenAI相关」，别凭印象说没有**。
7. **事实核对在写台本之前**：素材下载完就起后台调研子代理读官方原文，台本照“能写 / 不能写”清单写（`skill/openai-episode/references/facts.md`）。
