---
name: cs-grad-ai-episode
description: 制作悠一出镜的《AI震惊瘫坐时代计算机研究生必须掌握的技能》合集视频（B 站 + YouTube 两个平台都发）的完整流程：用户自己录口播（DJI Pocket 4P，SD 卡）→ ASR 逐词识别 → 手写中英字幕条、剪掉口癖和重录 → 出镜帧和口播逐帧对齐 → HTML 逐帧渲染演示画面（出镜画框 + 目录 + 字幕占位）→ 嵌入出镜帧重渲 → 生成双语 SRT → 加悠一片头片尾（三个合集共用模板）→ 发布。用户提到"CS 研究生系列""别再用 VSCode""计算机研究生技能"，或要给这个合集做投稿时，用这个技能。
---

# 《AI震惊瘫坐时代计算机研究生必须掌握的技能》单期制作（悠一出镜）

悠一（英文 Yui）自己出镜讲的 CS 研究生向技能系列。B 站合集 + YouTube 播放列表，**每期两个平台都发**（同 Way to AGI 惯例）。

第 1 期《别再用VSCode了》就是按这套流程做的，是参考实现（只读）：`AI震惊瘫坐时代计算机研究生必须掌握的技能/01_别再用VSCode了/`。

## 路径

| 名称 | 位置 |
|---|---|
| 合集目录 | `D:\大疆\AI震惊瘫坐时代计算机研究生必须掌握的技能\`（每期 `NN_<标题>\`） |
| 本技能 | `D:\大疆\AI震惊瘫坐时代计算机研究生必须掌握的技能\skill\cs-grad-ai-episode\`（`C:\Users\yui\.claude\skills\cs-grad-ai-episode` 是指向它的目录联接） |
| 片头片尾 | `D:\大疆\AI科普\片头片尾\`（**三个合集共用**：片头 3.8 s 打出"悠一"，片尾 4.8 s 制作清单 + "悠一"印章；只读）。加到视频用 `D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py` |
| 共用素材 | `D:\大疆\AI科普\素材\`：`字体\`（OFL，`fonts.css`）、`音频\`（系列 BGM `bgm.wav`、音效） |
| 用户录像 | SD 卡 `H:\DCIM\DJI_001\`（只读，不复制原片）。原片 3840×2160、HEVC 10-bit **HLG**、59.94 fps |

## 每期目录结构

```
NN_<标题>\
  素材\          录屏（OpenScreen 录制）、截图
  制作\
    02_出镜\     剪口播：ingest / asr / make_cues / build_edit / qa_asr
    00_整片\     画面 + 合成：build_timeline / index.html / prep_media / render_all / export_srt
    04_封面\     cutout / cover.html / render_covers
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
用户要稿子时才写。口播体、披露式展开、事实查官方来源并记日期。用户想先看画面再录的，可按稿子估时出一版"录制用"视频（出镜位留空白板提词），录完再按实际口播重排。

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

### 6. 嵌入真实出镜帧（v2）✋（先给用户看 v1 截帧确认构图）
- `prep_media.py cam`：从 `edit/facecam.mp4` 按帧号抽到 `media/cam/f_NNNNN.jpg`（帧号 = 正片时间 × 30，从 0 起，等于 facecam.mp4 直接按帧对齐）
- `index.html`：出镜框 `.inner` 换成 `<img id="camimg">`（去掉提词/进度条/段号占位层）
- `engine.js`：每帧 `setSrc(camImg, \`media/cam/f_${pad(Math.round(t * FPS), 5)}.jpg\`)`
- `render_all.py` → `<标题>_无字幕_v2_出镜版.mp4`

### 7. 字幕 SRT
`export_srt.py`（在 `00_整片\` 里，读 `../02_出镜/edit/edit.json` 里的 cues，时间 = out_s/out_e + 片头 3.8 s）→ 输出三份：`<标题>_v2_双语字幕.srt`、`<标题>_v2_中文字幕.srt`、`<标题>_v2_英文字幕.srt`。
- SRT 的时间已含片头 3.8 s，只对得上加完片头片尾的成片。要烧字幕，就在第 8 步之后烧在成片上，别烧在正片上（第 1 期烧在正片上，字幕整体晚了 3.8 s）。
- cue 超过 28 字的先拆短再导出（第 1 期的 cue 是段落级的，最长 175 字，烧出来一条 6 行）。

### 8. 片头片尾（三个合集共用）✋
每期片尾清单（JSON）问用户后写 `制作\00_整片\outro.json`：
```json
{"items":[{"label":"拍摄","value":"Pocket 4P"},{"label":"剪辑","value":"Claude Code"},…], "closing":"感谢大家看到最后", "signature":"悠一"}
```
然后：
```
python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <v2出镜版.mp4> --outro-data outro.json -o <NN_标题>_成片.mp4
```
再压一份手机预览（1170×540）。自查：片头 3.8 s 打出"悠一"、片尾 4.8 s 印章、响度 −16 LUFS 左右。

### 9. 封面 ✋
`制作\04_封面\`：从 4K 原片挑几帧表情（`ffmpeg -ss <秒> -i <4K原片> -frames:v 1 -q:v 2 <帧.jpg>`），`cutout.py`（本地 birefnet 抠像，白描边）→ 改 `cover.html` 标题 → `render_covers.py` 出三个方案给用户挑。不用 DeepSeek / 鲸鱼娘形象。

### 10. 投稿 ✋（两个平台）
读 `D:\大疆\Way to AGI\skill\way-to-agi-episode\references\publish.md`（投稿流程两个系列完全相同）。
- B 站：插件填标题、封面 16:9 + 4:3、创作声明「含AI生成内容」、标签、简介（章节时间加片头 3.8 s）、合集。「立即投稿」用户自己点。
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
- **片头片尾**：三个合集从 2026-09-29 起都复用 `AI科普\片头片尾`，不自己另做。
- **DeepSeek 形象（鲸鱼娘 / 大肥鱼）只用在《原LAI如此》和《AI每日日报》里**，本合集画面、封面不用。
- 白板演示版先出，确认构图没问题再嵌入真实出镜帧重渲；不要跳过白板版直接出镜，不然构图有问题重渲很贵。
- 字幕的中文按用户实际说的整理（≤28 字一条），英文逐句翻译（≤90 字符）。删了什么都告诉用户。
- 事实（价格、分数、发布时间）查官方来源，画面上写来源和截止日期；拿不准的说法告诉用户。
