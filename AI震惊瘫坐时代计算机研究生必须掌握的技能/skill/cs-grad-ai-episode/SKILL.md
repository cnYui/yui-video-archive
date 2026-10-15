---
name: cs-grad-ai-episode
description: 制作悠一出镜的《AI震惊瘫坐时代计算机研究生必须掌握的技能》合集视频（B 站 + YouTube 两个平台都发）的完整流程：用户自己录口播（DJI Pocket 4P，SD 卡）→ ASR 逐词识别 → 手写中英字幕条、剪掉口癖和重录 → 出镜帧和口播逐帧对齐 → HTML 逐帧渲染演示画面（出镜画框 + 目录 + 字幕占位）→ 嵌入出镜帧重渲 → 生成双语 SRT → 加悠一片头片尾（三个合集共用模板）→ 发布。用户提到"CS 研究生系列""别再用 VSCode""计算机研究生技能"，或要给这个合集做投稿时，用这个技能。
---

**默认发布平台（2026-10-14 用户定）：短视频、长视频在用户未指定平台时仅发 B 站；不打开、不上传其他平台。用户明确要求其他平台时才启用对应流程。平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。**

**上传方式（2026-10-14 用户定）：文件小于 10 MB 且本轮已授权自动上传时，可用 Playwright JS 上传完整文件；达到或超过 10 MB 就提醒用户手动上传。不为自动上传压缩、分块或改用低清版本。用户手动上传后继续填表，已授权发布则读回核对后点击发布。**


# 《AI震惊瘫坐时代计算机研究生必须掌握的技能》单期制作（悠一出镜）

悠一（英文 Yui）自己出镜讲的 CS 研究生向技能系列。B 站合集 + YouTube 播放列表，**每期两个平台都发**（同 Way to AGI 惯例）。

第 1 期《别再用VSCode了》就是按这套流程做的，是参考实现（只读）：`AI震惊瘫坐时代计算机研究生必须掌握的技能/01_别再用VSCode了/`。

## 路径

| 名称 | 位置 |
|---|---|
| 合集目录 | `D:\大疆\AI震惊瘫坐时代计算机研究生必须掌握的技能\`（每期 `NN_<标题>\`） |
| 本技能 | `D:\大疆\AI震惊瘫坐时代计算机研究生必须掌握的技能\skill\cs-grad-ai-episode\`（`C:\Users\yui\.claude\skills\cs-grad-ai-episode` 是指向它的目录联接） |
| 封面模板 | 本技能 `assets\template\制作\04_封面\`：`cover.html`（合集固定版式 = 第 1 期封面的风格，每期拷过去**不改**）、`render_covers.py`、`cutout.py`、`cover.json`（例子 = 第 1 期）。规则见 `references\cover.md` |
| 字幕标准 | `D:\大疆\Way to AGI\skill\way-to-agi-episode\references\subtitles.md`（中英双语、去口癖、括号注释、终检），本合集沿用（用户 2026-10-02 定） |
| 片头片尾 | **所有视频必加**（用户 2026-10-03）。`D:\大疆\AI科普\片头片尾\`：片头 `intro\index.html`（4.8 s，Claude 品牌色「对话气泡」：代码符号 → LLM 芯片 → 气泡里打出“悠一” + “AI鼓励师”）、片尾 `outro\index.html`（9.0 s，信纸：参考文献 + 致谢 + 感谢语 + 悠一朱印）；时长用 `pack_info.py` 读，不写死。源文件只读 |
| 加片头片尾 | `D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py` |
| 共用素材 | `D:\大疆\AI科普\素材\`：`字体\`（OFL，`fonts.css`）、`音频\`（系列 BGM `bgm.wav`、音效） |
| 用户录像 | SD 卡 `H:\DCIM\DJI_001\`（只读，不复制原片）。原片 3840×2160、HEVC 10-bit **HLG**、59.94 fps |

## 片头片尾（所有视频必加）

用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”。所有合集、所有视频共用一套，不另做、不省略、不改模板。**例外：短视频开头结尾都不加**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”；短视频走 `short-video` 技能，见 `D:\大疆\短视频\skill\short-video\SKILL.md`）。

| | 路径 / 命令 | 时长 |
|---|---|---|
| 片头 | `D:\大疆\AI科普\片头片尾\intro\index.html`（数据 `intro\data.json`：悠一 · AI鼓励师） | 4.8 s |
| 片尾 | `D:\大疆\AI科普\片头片尾\outro\index.html`（数据格式见 `outro\data.example.json`） | 9.0 s |
| 本技能怎么加 | `python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data <片尾.json> -o <成片.mp4>`（正片不重编码，片头片尾按视频原尺寸渲染，下面垫系列 BGM） | |
| 时长（脚本里读，别写死） | `D:\大疆\AI科普\片头片尾\pack_info.py` 的 `intro_seconds()` / `outro_seconds()`（`python pack_info.py` 打印路径和时长） | |

- 片头：Claude 品牌色（米白 #FAF9F5 底、墨色 #141413、橙 #D97757 / 黄 #F5DB9A 强调），`>` → `{ }` → `</>` → 神经网络 → LLM 芯片 → 对话气泡里打出“悠一”，下面“AI鼓励师”。
- 片尾：纸飞机送来一页信纸，左栏参考文献、右栏致谢、感谢语、签名和朱印（悠一）。片尾 JSON：`references`（参考文献，字符串，≤ 8 条，可空）、`items`（致谢 / 制作清单 `{label, value}`，≤ 8 条）、`closing`（感谢语）、`signature`（悠一）。**每期问用户**，不沿用上一期、不用模板默认值。
- SRT、B 站 / YouTube 章节时间 = 正片时间 + 片头时长（现在 4.8 s）。
- 交付前自查：开头是片头、结尾是片尾，总时长 = 片头 + 正片 + 片尾。

## 每期目录结构

```
NN_<标题>\
  素材\          录屏（OpenScreen 录制）、截图
  制作\
    02_出镜\     剪口播：ingest / asr / make_cues / build_edit / qa_asr
    00_整片\     画面 + 合成：build_timeline / index.html / prep_media / render_all / export_srt
    04_封面\     cutout / cover.json（本期只改这个）/ cover.html（合集固定模板，不改）/ render_covers
```

注意：本系列用 `00_整片\`（而非 Way to AGI 的 `03_成片\`），因为白板演示和出镜整合在同一渲染里。

## 开工前

1. 读 `D:\大疆\AGENTS.md`（尤其「AI震惊瘫坐时代计算机研究生必须掌握的技能」相关节）。
2. 同一时间只跑一个渲染，4 路并行（`render_all.py`，4 workers）；开渲前先确认没有别的渲染在跑。

## 流程（✋ = 停下来等用户确认）

### 0. 建目录
建 `NN_<标题>\制作\02_出镜\`、`NN_<标题>\制作\00_整片\`、`NN_<标题>\素材\`；从第 1 期把 `02_出镜\`（ingest、asr、build_edit、qa_asr 等脚本）和 `00_整片\`（render_all、prep_media、build_timeline、engine.js、lib.js、index.html、hand.js 等）作为模板拷过去，按本期修改。
先问清：SD 卡上哪几段录像（编号）、片尾制作清单（**每期问，不沿用上一期**）、有哪些演示素材（录屏文件、截图）。

### 1. 台本（可选）✋
用户要稿子时才写。口播体、披露式展开、事实查官方来源并记日期。**2026-10-04 起照 AI大圆镜 的写法**，先读 `D:\大疆\docs\台本风格_AI大圆镜.md`。用户想先看画面再录的，可按稿子估时出一版"录制用"视频（出镜位留空白板提词），录完再按实际口播重排。

### 2. 录像入库、识别
`制作\02_出镜\`：`ingest.py audio` / `ingest.py proxy <编号…>`（抽音频 + 转 1280×720 代理，原片不动）→ `asr.py`（faster-whisper large-v3-turbo，提示词里故意带口癖）。

### 3. 字幕条 ✋
`show_asr.py <编号> -w` 看逐词时间，手写 `make_cues.py`：中文按实际说的整理、去口癖和重录的半句，英文逐句翻译。听不准的词、删掉的内容列出来告诉用户。

### 4. 剪口播
`build_edit.py` → 输出 `edit\narration.wav`、`edit\facecam.mp4`（1280×720 30 fps，帧时间戳按 `setpts=N/30/TB` 重编）、`edit\edit.json`（每条字幕的 out_s/out_e 等）→ `qa_asr.py` 再识别一遍查剪辑漏洞。

### 5. 白板版画面（v1）
`制作\00_整片\`：
- `build_timeline.py`（按字幕条排画面，SCENES 每期重写；出镜框留空白板提词占位）→ 更新 `timeline.json` / `timeline.js`。
- `prep_media.py icons` + `prep_media.py hand`（图标 + 手写笔画）
- `audio\mix.wav` 复制自 `edit\narration.wav`（先在 `build_edit.py` 里生成，再拷过来）
- `render_all.py` → `<标题>_无字幕_v1_白板版.mp4`（出镜位是占位框，里面有段号和提词）
- 抽帧 `render_all.py --stills-auto` 自查：字压到出镜框/目录没有、字幕带对不对、说到的东西有没有出来
- **中英双语字幕烧进画面**（用户 2026-10-02 定，标准同 Way to AGI `references/subtitles.md`）：`index.html` 要有字幕带 `#subs`（y 922 起、高 130、全宽居中）、`#subZh`（Noto Sans SC 800、52/66 px、墨黑 `#1B1B1F`、白边 10 px）、`#subEn`（600、30/40 px、灰 `#4B5563`、白边 6 px，带顶往下 70 px）；`engine.js` 里 `subAt(t)`（每条开始前 0.1 s 显示到结束后 0.45 s，不和下一条重叠），每帧写 `subZh.textContent` / `subEn.textContent`——这两段照 `D:\大疆\Way to AGI\skill\way-to-agi-episode\assets\template\制作\03_成片\index.html` 的 `#subs` CSS 和「引擎」节抄。**第 1 期的 `index.html` / `engine.js` 没有这两段**（当时只导出了 SRT，成片没带字幕），拷模板时要补上。一条字幕 1–2 句，中文 ≤ 28 字、英文 ≤ 90 字符，各一行不换行，超了拆条。

### 6. 嵌入真实出镜帧（v2）✋（先给用户看 v1 截帧确认构图）
- `prep_media.py cam`：从 `edit/facecam.mp4` 按帧号抽到 `media/cam/f_NNNNN.jpg`（帧号 = 正片时间 × 30，从 0 起，等于 facecam.mp4 直接按帧对齐）
- `index.html`：出镜框 `.inner` 换成 `<img id="camimg">`（去掉提词/进度条/段号占位层）
- `engine.js`：每帧 `setSrc(camImg, \`media/cam/f_${pad(Math.round(t * FPS), 5)}.jpg\`)`
- `render_all.py` → `<标题>_无字幕_v2_出镜版.mp4`

### 7. 字幕 SRT
`export_srt.py`（在 `00_整片\` 里，读 `../02_出镜/edit/edit.json` 里的 cues，时间 = out_s/out_e + 片头时长，用 `pack_info.intro_seconds()` 读，现在 4.8 s）→ 输出三份：`<标题>_v2_双语字幕.srt`、`<标题>_v2_中文字幕.srt`、`<标题>_v2_英文字幕.srt`。
- SRT 的时间已含片头（4.8 s），只对得上加完片头片尾的成片。要烧字幕，就在第 8 步之后烧在成片上，别烧在正片上（第 1 期烧在正片上，字幕整体晚了 3.8 s）。
- cue 超过 28 字的先拆短再导出（第 1 期的 cue 是段落级的，最长 175 字，烧出来一条 6 行）。

### 8. 片头片尾（所有视频必加）✋
每期片尾（参考文献 + 致谢，JSON）问用户后写 `制作\00_整片\outro.json`：
```json
{"references":["本期用到的论文 / 文档 / 官方页面…"], "items":[{"label":"拍摄","value":"Pocket 4P"},{"label":"剪辑","value":"Claude Code"},…], "closing":"感谢观看，我们下期再见", "signature":"悠一"}
```
然后：
```
python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <v2出镜版.mp4> --outro-data outro.json -o <NN_标题>_成片.mp4
```
再压一份手机预览（1170×540）。自查：片头 4.8 s（对话气泡打出"悠一" + "AI鼓励师"）、片尾 9.0 s（信纸：参考文献 / 致谢没截断）、响度 −16 LUFS 左右、时长 = 4.8 + 正片 + 9.0。

### 9. 封面 ✋
读 `references\cover.md`。**版式固定**（用户 2026-10-02 定：“就用这样的风格就行，人物背后有浅蓝色强调，黑色文字加上橙色和黄色提亮”）：白底点阵 + 左上橙色胶囊「计算机专业 · AI 基础功」+ 第一行黑字 + 第二行橙字黄色荧光（+ 官方图标）+ 右边真人抠像（白描边）+ 人物背后浅蓝圆，就是第 1 期封面的样子。
`制作\04_封面\`：从本技能 `assets\template\制作\04_封面\` 拷 `cover.html`、`render_covers.py`、`cutout.py`、`cover.json`（**cover.html 不改**）→ 从 4K 原片挑 2–3 帧（`ffmpeg -ss <秒> -i <4K原片> -frames:v 1 -q:v 2 face_src/<编号>_<秒>.jpg`，默认安静的帧，动作帧用户点名才用）→ `cutout.py`（本地 birefnet 抠像，白描边）→ 改 `cover.json`（第一行、第二行、官方图标、人像、候选；胶囊不改；`[方括号]` 标橙色 / 荧光）→ `python render_covers.py` 出每个候选的 16:9 + 4:3 + `封面_候选_预览.png`（自检：字超安全区、进底部 12%、压人像、字被缩太小）→ 打开 PNG 看一眼 → 给用户挑 → `python render_covers.py --select N` 出 `封面_选定_16x9.png` / `封面_选定_4x3.png`。候选之间只换人像帧或封面字，不换版式和颜色。封面字和标题不重复。不用 DeepSeek / 鲸鱼娘形象。

### 10. 投稿 ✋（两个平台）
读 `D:\大疆\Way to AGI\skill\way-to-agi-episode\references\publish.md`（投稿流程两个系列完全相同）。
- B 站：插件填标题、封面 16:9 + 4:3、创作声明「含AI生成内容」、标签、简介（章节时间加片头 4.8 s）、合集。「立即投稿」用户自己点。
- YouTube：Studio 填说明（中英）、播放列表、非面向儿童、标签、类别；缩略图请用户手动传；「发布」用户自己点。
- 上传成片到 GitHub Release：`gh api repos/cnYui/yui-video-archive/releases/tags/<tag> --jq .id` 拿 id → `gh api --method POST … --input <成片路径>`（具体命令见 `AGENTS.md` 的「Releases 上传」节）。

### 11. 记录
`AI震惊瘫坐时代计算机研究生必须掌握的技能\README.md` 发布表加一行（B 站 BV 号、YouTube 链接）；`AGENTS.md` 加简短结论；完整过程写进 `docs\ai\context\YYYYMMDD-HHMMSS-<slug>_CN.md`。

## 关键参数（来自第 1 期实测）

- 画面尺寸：2340×1080，30 fps，白底
- 出镜框大框（版式 A，开场/结尾）：`CAM.A = {x:120, y:150, w:1156, h:666}`
- 出镜框小框（版式 B，pip 左上角）：`CAM.P = {x:48, y:48, w:696, h:402}`，版式切换时框移动 0.7 s
- 出镜帧放大（大框 1.06、小框 1.3），对脸 `transform-origin 55.5% 38%`（按本期机位微调）
- 录像原片 HLG 10-bit，代理和出镜帧**不做色彩转换**直接转 8-bit（直接转肤色最自然；02期试过 zscale+hable 和 BT.709，都不如直接转）
- `build_edit.py` 拼接出镜视频必须按帧重编时间戳（`setpts=N/30/TB`）；直接 `-c copy` 会有时间戳空档，导致口型越往后越慢（02 期多出 74 帧 = 2.5 s）
- `render_all.py` ffmpeg x264 CRF 16，必须加 `-filter_threads 1`（ffmpeg 8.0 在 2340 宽多线程时左边缘会出黑点）
- 录屏工具：**OpenScreen**（Microsoft Store 1.13.0，用户已装）

## 原则

- **名字**：悠一（Yui）。开场出镜框上有"悠一 Yui"名字条（0.4–5.6 s）。
- **片头片尾**：所有视频必加（用户 2026-10-03），共用 `AI科普\片头片尾`（见上面「片头片尾」一节），不自己另做。
- **DeepSeek 形象（鲸鱼娘 / 大肥鱼）只用在《原LAI如此》和《AI每日日报》里**，本合集画面、封面不用。
- 白板演示版先出，确认构图没问题再嵌入真实出镜帧重渲；不要跳过白板版直接出镜，不然构图有问题重渲很贵。
- 字幕按 Way to AGI 的 `references/subtitles.md`：中文按用户实际说的整理（≤28 字一条），英文逐句翻译（≤90 字符），中英都烧进画面（52 / 30 px，y 922 以下，见第 5 步）并导出三份 SRT。删了什么都告诉用户。
- 封面用合集固定模板（`references/cover.md`），每期只改 `cover.json`；版式、颜色、字体、字号、人像位置不每期重排，也不再提议换风格（2026-10-02 给过深色 / 蓝色色块 / 黄底三版，用户都没要）。
- 事实（价格、分数、发布时间）查官方来源，画面上写来源和截止日期；拿不准的说法告诉用户。
