# 出镜多段口播 + 官方素材 + 说明卡（faceb 版式）

2026-10-06《Claude官方教程》第 1 期出镜版做出来的整条流水线，收成技能里的一节。**什么时候用**：用户自己录了**好几段**口播（DJI 原片，几分钟到十几分钟），要配官方课 / 官网 / 他自己的录屏镜头 + 自己画的说明卡，字幕 = 他实际说的话，他的脸是镜像小窗。
只有一段口播、画面是页面截图 / 录屏的（《Claude 中文界面》那种）用 `own_voice.py` + `single` / `dual` 版式就够，见 `references/face-window.md`。

**新建一期**：`python scripts/new_short.py --collection <合集> --num NN --name 短名_出镜版 --layout faceb`
会铺好：`台本\talk_lines.py` / `script_data.py`（骨架）、`制作\00_整片\scenes_ep.js`（说明卡小工具）+ `face.json`、`制作\01_口播\`；并把 `common.py` 的 `NATURAL_TIMING` 改成 True、`index.html` 加载 `scenes_ep.js`、`mix_audio.py` 的 BGM 床改 −11 dB / 不抬空档。
**做之前先看真实例子**：`example_ep1\`（第 1 期的 `talk_lines.py` 124 行、`script_data.py` 45 个场景、`scenes_ep.js` 12 张说明卡）；成片 / 记录在 `D:\大疆\Claude官方教程\短视频\01_ClaudeCode是什么_出镜版\` 和 `D:\大疆\docs\ai\context\20261006-172000-claude-official-ep1-on-camera-real-voice_CN.md`，复盘在 `D:\大疆\短视频\流程复盘.md` 第 9 部分。

## 版式 faceb：每个场景自己选窗口

| mode | 窗口 | 字幕 y | 出镜小窗 |
|---|---|---|---|
| `one` | 单窗 1000×569（x 40, y 770；内容 1474×829） | 1498 | 居中在字幕下面 360×360（x 360, y 1664） |
| `two` | 两个窗口上下叠 860×490（x 110；y 680 / 1194；内容各 1474×829） | 1764 | 缩到 240 放左下角（x 40, y 1460） |
| `big` | 一个大窗 860×1004（x 110, y 680；内容 1474×1725，看清文字用） | 1764 | 同 two；大窗里的说明卡内容放 y ≤ 1330、左下角（x < 320 且 y > 1335）留空 |

引擎（`engine.js` 的 `MODES`）按场景的 `mode` 摆窗口，场景开头 0.18 s 淡入 + 轻放大；`single` / `dual` 版式不走这段，和以前逐像素一样（2026-10-06 回归测过：新旧模板同一份台本渲出的静帧只差渲染本身的抖动，`timeline.json` / `frames.js` 完全相同）。
`compose_face.py` 按同一个 mode 换小窗位置、检查字幕不被盖（第 1 期的包装脚本 `compose_face_mixed.py` 已并进去，关键帧逐项对过一样）。

## 流程（每一步的脚本都在 `scripts/`，参数是 `<本条目录>`）

| 步 | 做什么 | 脚本 / 文件 |
|---|---|---|
| 0 | 问清：**顶上两行字**（hook，每一帧都在，第一张静帧就单独给用户看）、封面（Claude / Anthropic 内容放官方吉祥物，`assets/mascot/`）、小红书原创声明开 / 关；`ListAgents` + `ls -t docs/ai/context` | — |
| 1 | 批量 ASR：模型只载一次，每段出逐词 `asr.json`（turbo）+ `asr_medium.json` + 16 kHz wav | `asr_clips.py <素材\出镜_ASR> <原片…> --prompt "专名，…"`（后台跑，CPU 十几分钟） |
| 2 | 写字幕行：每行 = (id, 片段, 起点锚点, 终点锚点, 中文, 英文)；中文 = 他实际说的话（只改听错的专名 / 同音字）；英文忠实直译；`CUTS` 写口误；`UNSURE` 写要他耳朵确认的词 | `台本\talk_lines.py` |
| 3 | 口播母带：`resolve`（锚点对原话，先看一遍）→ `plan`（按能量找静音，> 0.58 s 的停顿缩短、剪口误，不改词序不变速，切点对齐 30 fps 帧、声音按 1600 样点 / 帧同切）→ `media`（`talk.wav` + `tts_narration.wav` + 每段脸）→ `concat`（`talk_face.mp4`，核对帧数 = 母带） | `build_talk.py resolve | plan | media | concat <本条>` → `制作\01_口播\` |
| 4 | 写场景：每场景 mode、lines、kind（clip / card）、top / bottom 选段（`S(src, a, b, w, speed, crop)` / `H(src, a, w)`）、credit；**选段只用核过的安全段，不放讲师的脸** | `台本\script_data.py` |
| 5 | 生成 plan / 录制稿 / tts_edit / 口播稿；**看定格报告**（上窗 / 下窗各报定格几秒，单段 > 3 s 标 ⚠） | `gen_ep.py <本条> --timing 制作\01_口播\timing.json` |
| 6 | 素材表 `common.py` 的 `SRC` / `HAS_AUDIO`（官方课 + 录屏，全部静音）；`face.json`：`src` = `talk_face.mp4`、`start 0`、`crop {cx 0.5, cy 0.5, side 1.0}`（方形已裁）、`mirror true` | `制作\00_整片\` |
| 7 | 说明卡 + 官方镜头的中文小标签；时间全按“字幕行 + 词”挂：`S('T20')` / `E('T20')` / `P('T20','词')` | `制作\00_整片\scenes_ep.js` |
| 8 | `build_timeline.py` → **`check_phrases.py`**（所有 `P()` 的词都在那一行字幕里，一次过，不然渲染会抛错）→ `check_subs.py` → `prep_frames.py` → **`scan_faces.py`**（Haar 扫素材帧里的讲师人脸；联系表看不出短暂切入）→ **`audit_holds.py`**（定格审计）→ `render_all.py --stills-segs`（全场景静帧逐张看 + 点名几张全尺寸） | `scripts/` |
| 9 | 混音（`mix_audio.py`，BGM 床 −11 dB）→ `render_all.py`（**同一时间只跑一个渲染**；机器上有别的实时录屏 / 渲染时 `cmd /c start /B /BELOWNORMAL` + `RENDER_WORKERS=3`）→ `整片_v1.mp4` 改名 `整片_v1_cards无小窗.mp4` → `compose_face.py <本条>`（合成完核对帧数 = base，少了自动重跑一次）→ **`check_face_sync.py`**（单窗时刻小窗和母带人像逐帧比，偏移 0 / ±1 正常）→ `qa_mix.py`（逐句 ASR，低分多半是同音 / 繁体假低分，列给用户听）→ `finish.py` | `scripts/` + 引擎 |
| 10 | 封面（框版 3×3，带吉祥物候选）→ 交付包（**含“顶上这两行字”**）→ 用户同意 → **先把新成片拷成 `_成片_无封面帧.mp4`**（`cover_frame0.py` 现在会自己检查备份是否过期，但别依赖）→ `cover_frame0.py` → 发布 | `make_cover_framed.py` / `make_mascot_pictures.py` / `cover_frame0.py` |

**同步引擎模板到这一期时**（SKILL.md 步骤 5：出整片前把引擎副本同步到模板最新版）保留本条改过的：`common.py`（素材表 + `NATURAL_TIMING`）、`index.html` 里的 `<script src="scenes_ep.js"></script>` 那一行、`mix_audio.py` 的 BGM 常量（`BGM_BED −11`、`BGM_SWELL_DB 0`）、`scenes_ep.js`、`face.json`；`engine.js` / `build_timeline.py` / `prep_frames.py` 直接用模板最新的（已含 faceb）。

## 第 1 期的数据（做下一期时估时间）

5 段 DJI 口播 645.8 s → 母带 574.33 s（17230 帧）；字幕 124 句 / 280 条中英双语条；45 个场景（one 9 / two 24 / big 12，官方课 / 录屏镜头 33、自画说明卡 12），窗口左上角中文小标签 39 个；
整片渲染 2 次（545 s、582 s，3 路）+ 小窗合成 2 次（约 3 分钟）；扫脸 2 轮（第 1 轮 6 段、第 2 轮只剩 1 段误报）；`qa_mix` 124 句里只有 3 条 < 0.8，都已逐条核对。

## 踩过的坑（别再来一遍）

- **顶上两行字写错整片重渲**（约 15 分钟）：沿用了第一版 AI 草稿里随手写的钩子，成片发出去才被指出。→ 第一次静帧就问，交付包里单独写一行。
- **封面三个作废**：做成人脸 / 循环图 / 确认框，用户要的是官方吉祥物。→ Claude / Anthropic 内容的封面候选至少一个带吉祥物（`assets/mascot/README.md`）。
- **按联系表推断“这一段都是屏幕”**：三秒一帧看不出讲师的短暂切入，渲前 `scan_faces.py` 扫出 4 处。→ 选段只用已核过的安全段（记忆 `claude-academy-footage-no-lecturer-face`）。
- **一个窗口定格 10.9 s**：素材比台词短，gen_ep 把最后一帧定格补满，下窗的数字只在 plan.json 里。→ `gen_ep.py` 现在上下窗各报一行，`audit_holds.py` 渲前再查。有意停住讲一张图的可以留（第 1 期留了 10 处 > 3 s 的）。
- **Whisper 把重复短语合并**（“执行这些任务，执行这些命令”只出一遍）：ASR 复核的低分要回到词级时间戳和原片对。
- **Bash heredoc 吞反斜杠**：写含 Windows 路径的文档 / 脚本一律用 Write / Edit 工具，或路径写成正斜杠（`\01` 会变成控制字符）。
- **`cover_frame0.py` 从旧备份重做**：重渲后不先拷备份，会把旧标题的版本放回去。脚本已加过期检查，但换封面前仍先拷。
- **小红书被抢先发布**：用户在场时先在聊天里问清原创声明开 / 关再填；或者每填完一个平台马上发那个平台（记忆 `fill-forms-before-saying-ready`）。
