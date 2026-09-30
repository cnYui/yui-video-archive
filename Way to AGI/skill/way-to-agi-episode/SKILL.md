---
name: way-to-agi-episode
description: 制作悠一出镜的「Way to AGI」合集视频（B 站 + YouTube 两个平台都发）的完整流程：用户自己录口播（DJI Pocket 4P，SD 卡）→ ASR 逐词识别 → 手写并精修中英字幕条（去口癖、术语统一、括号注释）、剪掉口癖和重录 → 出镜画面和口播逐帧对齐 → HTML 逐帧渲染演示画面（出镜画框 + 目录 + 中英字幕）→ 混音 → 4 路渲染正片 → 加悠一片头片尾（三个合集共用的模板）→ 露脸封面三选一 → 用 Chrome 插件填 B 站投稿页和 YouTube Studio。用户提到“Way to AGI”“露脸视频”“出镜视频”“我录好口播了”“把我的口播剪一下加字幕”，或者要给这个合集做封面、投稿、传 YouTube 时，都用这个技能。
---

# 《Way to AGI》单期制作（悠一出镜）

悠一（英文 Yui）自己出镜讲 AI 的视频。B 站合集「Way to AGI」+ YouTube 播放列表「Way to AGI」，**每期两个平台都发**（用户 2026-09-29）。
另外两个合集《原LAI如此》《AI每日日报》只发 B 站，走各自的技能（`yuanlai-ruci-episode`、`ai-daily-news`）。

第 02 期《如何使用Claude来低成本的生成视频》就是按这套流程做的，是参考实现（只读）：`D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\`。拿不准的细节去看它的 `制作/` 和制作记录 `D:\大疆\docs\ai\context\20260928-184726-claude-video-tutorial-production_CN.md`。

## 路径

| 名称 | 位置 |
|---|---|
| 合集目录 | `D:\大疆\Way to AGI\`（每期 `NN_<标题>\`，README 有每期的发布记录） |
| 本技能 | `D:\大疆\Way to AGI\skill\way-to-agi-episode\`（`C:\Users\yui\.claude\skills\way-to-agi-episode` 是指向它的目录联接） |
| 每期模板 | 本技能 `assets\template\制作\`（`02_出镜\` 剪口播、`03_成片\` 画面和合成、`04_封面\`），`scripts\new_episode.py` 拷过去 |
| 片头片尾 | `D:\大疆\AI科普\片头片尾\`（**三个合集共用**：片头 3.8 s 打出“悠一”，片尾 4.8 s 制作清单 + “悠一”印章；只读）。加到视频上用 `D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py` |
| 共用素材 | `D:\大疆\AI科普\素材\`：`字体\`（OFL，`fonts.css`）、`音频\`（系列 BGM `bgm.wav`、音效） |
| 用户录像 | SD 卡 `H:\DCIM\DJI_001\`（只读，不复制原片）。原片 3840×2160、HEVC 10-bit **HLG**、59.94 fps |
| 真人素材 | `D:\大疆\真人素材\`：用户的 vlog、露营素材，和本合集无关，只读，不动 |

## 开工前

1. 读 `D:\大疆\AGENTS.md`（尤其「2026-09-29 三个合集和发布平台」和 Way to AGI 相关几节）和 `docs\ai\context\` 里最新的几份记录。
2. 读 `references/pipeline.md`（每一步的做法和参数）。写字幕前读 `references/subtitles.md`（字幕规范）。投稿前读 `references/publish.md`。出问题先查 `references/lessons.md`。
3. 同一时间只跑一个渲染，4 路并行（用户 2026-09-28 定的统一标准）；开渲前先看有没有别的渲染在跑。

## 流程（✋ = 停下来等用户确认）

### 0. 建目录
`python scripts/new_episode.py --number N --title "标题"` → `D:\大疆\Way to AGI\NN_<标题>\`（`素材\`、`制作\` 模板、README）。
先问清：用了 SD 卡上哪几段录像（编号）、片尾制作清单（**每期问，不沿用上一期**；02 期是 拍摄 Pocket 4P / 剪辑 Claude Code / 视频剪辑模型 Opus 5.5）、有哪些演示素材（录屏、作品视频、截图）。

### 1. 台本（可选）✋
用户要稿子时才写（口播体、披露式展开、事实查官方来源并记日期）。用户想先看画面再录的，可以先按稿子估时出一版“录制用”视频（出镜位留空），录完再按实际口播重排。

### 2. 录像入库、识别
`制作\02_出镜\`：`ingest.py audio` / `ingest.py proxy <编号…>`（抽音频、转 1280×720 代理，原片不动）→ `asr.py`（large-v3-turbo，提示词里故意带口癖，口癖才会被写出来）。

### 3. 字幕条 ✋
`show_asr.py <编号> -w` 看逐词时间，手写 `make_cues.py`：中文按实际说的整理、去口癖和说错重来的半句，英文逐句翻译。名字一律“悠一 / Yui”。
- **写之前先列术语表**（本期的专有名词和写法，拿不准的先问用户，例如 VSCode / VS Code），同时放进 `asr.py` 的 `PROMPT` 和 `make_cues.py` 顶部。
- 规范全在 `references/subtitles.md`：去口癖、术语和常见误识别、碎片条、括号注释（观众听不懂的引用和术语，全角括号、12 字内、约每分钟一条）、中英翻译要求、终检。
- 听不准的词、删掉的内容（说错的数字、不准确的说法）、加了哪些注释，列出来告诉用户。

### 4. 剪口播
`build_edit.py`（口播和出镜画面在同一帧上切）→ `qa_asr.py` 再识别一遍，查剪辑点漏掉的口癖、切掉的半个字，改 `make_cues.py` 重跑。作品展示这类段落，在念完后用 `hold` 留 1.5–2 s 让片段原声出来。
剪完、渲染前按 `subtitles.md` 的「终检」过一遍字幕，用表格（时间 + 改后的字幕）把改动给用户看。

### 5. 画面
`制作\03_成片\`：`build_timeline.py`（按字幕条排画面，SCENES 每期重写）→ `prep_media.py cam`（出镜逐帧）+ 本期演示素材 → 写 `index.html` 的画面（02 期的画面是例子，按本期口播重写；说到哪个词就出哪样东西，用 `tm.at("词")`）→ `render_all.py --stills …` 抽帧自查。我们自己排的中文文字层（标题卡、章节名、要点、标签）配英文小字，见 `subtitles.md`。

### 6. 混音、正片
`mix_audio.py`（口播 −16 LUFS，系列 BGM 很轻地垫着，作品原声有人声时压低、停顿时抬起）→ `render_all.py`（4 路）→ `<NN_标题>_正片.mp4`（不含片头片尾）→ `export_srt.py`（双语 / 中文 / 英文 SRT，时间已加上片头 3.8 s）。

### 7. 片头片尾（三个合集共用）
写本期片尾清单 `制作\03_成片\outro.json`（`{"items":[{"label":"拍摄","value":"Pocket 4P"},…], "closing":"感谢大家看到最后", "signature":"悠一"}`），然后：
`python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data outro.json -o <期目录>\<NN_标题>_成片.mp4`
片头用 `AI科普\片头片尾\intro\data.json`（名字“悠一”）。片头片尾按视频原尺寸（2340×1080）渲染，下面垫 BGM，正片不重新编码。再压一份手机预览（1170×540）。
自查：开头 3.8 s 是打出“悠一”的片头、结尾 4.8 s 是悠一印章的片尾，响度 −16 LUFS 左右，时长 = 3.8 + 正片 + 4.8。

### 8. 封面 ✋
`制作\04_封面\`：从 4K 原片挑几帧表情（挥手、惊讶、讲解），`cutout.py`（本地 birefnet 抠像，只留最大连通块，白描边）→ 改 `cover.html` 的标题 → `render_covers.py` 出三个方案（16:9 + 4:3 + 信息流缩略图）给用户挑，按用户意见组合（02 期：方案三的人像 + 方案一的标题）。4:3 单独排版（标题更大、人更小）。**不用 DeepSeek 形象（鲸鱼娘）。**

### 9. 投稿 ✋（两个平台）
读 `references/publish.md`。视频文件由用户自己选（插件单次上传上限 10 MB）。
- B 站：插件填标题（用户定的）、封面 16:9 + 单独的 4:3、创作声明「含AI生成内容」、分区、10 个标签、简介（Quill setText，章节时间要加上片头 3.8 s）、合集「Way to AGI」。「立即投稿」用户自己点。
- YouTube：在 YouTube Studio 的编辑页填说明（中英）、播放列表「Way to AGI」、不是面向儿童、标签、语言、类别等；自定义缩略图插件传不上，请用户手动传；「发布」用户自己点。

### 10. 记录
`Way to AGI\README.md` 的发布表加一行（B 站 BV 号、YouTube 链接）；`AGENTS.md` 加简短结论；完整过程写进 `docs\ai\context\YYYYMMDD-HHMMSS-<slug>_CN.md`。用户这期提的新规则，以后每期都适用的，也更新到本技能里。

## 原则

- **名字**：悠一（Yui）。开场白是用户自己说的（02 期：“Hello，大家好，我是悠一。”），开场出镜框上有“悠一 Yui”名字条。
- **片头片尾**：三个合集从 2026-09-29 起都复用 `AI科普\片头片尾` 这一套（片头打出“悠一”、片尾“悠一”印章），不自己另做（用户 2026-09-29）。
- **DeepSeek 形象（鲸鱼娘 / 大肥鱼）只用在《原LAI如此》和《AI每日日报》里**，本合集的画面、封面、角色都不用（用户 2026-09-29）。
- 版面：白底；出镜像画框一样框在画面里，不全屏（大框在左 = A；缩到左上角 + 左下目录 = B；作品展示 = C），主体放演示；字幕中英双语、按画面居中；只用 OFL 字体。
- 事实（价格、分数、发布时间）查官方来源，画面上写来源和截止日期；拿不准的说法告诉用户。
- 剪辑：说错的地方删掉而不是配字幕纠正；删改了什么都告诉用户。
- 字幕：和成片里听到的一致；括号注释只放没说出口的话（对齐说话时间的脚本会跳过它）；规范见 `references/subtitles.md`。

## 安全与合规

- 「立即投稿」「发布」永远由用户自己点；不替用户付费，不做账号验证（YouTube 手机验证等由用户自己来）。
- SD 卡原片、`真人素材\`、往期文件只读；用户装了 dcg 钩子拦截删除，清理就移到本期的 `_旧\`。
- 作品展示里的同人动画（银魂、火影、JoJo 等），简介写明版权归原作方。

## 参考文档

| 文件 | 什么时候读 |
|---|---|
| `references/pipeline.md` | 每一步的具体做法、参数、页面结构 |
| `references/subtitles.md` | 写字幕前、交字幕给用户看前：去口癖、术语、括号注释、双语翻译、终检 |
| `references/publish.md` | 填 B 站投稿页、YouTube Studio |
| `references/lessons.md` | 遇到报错或怪现象时 |
| `scripts/new_episode.py` | 建新一期目录 |
