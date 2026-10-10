# 《Claude官方教程》系列① 十期：做到哪了（2026-10-06 中午，用量额度用完时的交接）

用户 2026-10-05 确认计划、2026-10-06 说“开始做第一期的十个视频”。计划看 `Claude官方教程\计划.md`，进度表看 `Claude官方教程\README.md`。

## 已完成
- **事实核对**：十期各一份 `短视频\NN_…\台本\事实核对.md`（五个子代理按官方文档核的；✗ 和“不要讲的”都已改进台本）。要点：`/agents` 创建向导已被官方删掉（第 7 期写了“新版本已删”）；MCP 工具定义现在默认只放工具名（第 9 期按新说法写）；自动模式放行的是“推到当前仓库的分支”、新版本终端新会话默认就是自动模式；Lewis Menelaws 只念名字不讲头衔。
- **台本**：唯一数据源 `Claude官方教程\工具\series_data.py`（每句 zh 字幕 / say 念的字 / en 英文字幕 + 每个场景的画面规则 + 叠加层）。十期各 12–15 句，真实配音后每期约 60–65 s。`python series_data.py` 自检；`python gen_episode.py all [--tts]` 生成各期 `台本\录制稿.json`、`plan.json`、`制作\00_整片\common.py` 素材表、`scenes.js` 叠加层。
- **画面选段**：`plan_spans.py` 按场景的锚点（`at=秒`，可带 `until` / `more` / `cards` / `endcard`）自动把官方视频的镜头拆给上下框（人脸进上框、其余进下框，不够长就从没用过的镜头里就近借，再不够放慢非人脸段到 0.8×）；`check_spans.py` 查素材够不够 / 有没有重叠（现在 10 期都够）。整屏文字标题卡登记在 `TEXT_CARDS`，不当画面用。
- **配音**：Fish 故事工作室空白项目、声线「温柔男生」、S2 Pro。两批：整稿 120 句（`build_fish_doc.py` → 键入 → `split_voice_export.py`）+ 补录 15 句（`voice_extra.py list | split | rebuild`，第 2 期 N03 重配）。各期 `制作\02_配音\tts\seg_raw\final\` 已按新台词顺序排好（旧的备份在 `final_第一批`），`build_voice.py` 已跑（`edit\tts_edit.json` 是真实时长），`gen_episode.py all --tts` 已跑，各期 `mix_audio.py` 的 BGM 床已改 −9 dB。
- **第 1 期已跑到 `build_timeline.py`（64.6 s）和 `check_subs.py`（28 条字幕，没问题）**。
- 识别核对 `asr_all.py`（faster-whisper small 两遍）：第 1–3 期整稿的报告在各期 `台本\配音核对.md`，没有真问题（“终端→中端”“权限→全线”这类是同音误听）。第 4–10 期整稿 + 第 1–3 期补录句的后台识别在跑，报告写到各期 `台本\配音核对.md` / `配音核对_补录.md`（可能已经跑完，看一眼；`<<<`/⚠ 的句子列给用户耳朵听）。

## 下一步（照这个顺序）
1. 每期 `制作\00_整片\`：`build_timeline.py` → `check_subs.py` → `prep_frames.py` → `render_all.py --stills-segs`（逐张看 `stills\`，重点：上下框画面和念白对得上、叠加层 `note()` 没盖住官方画面的名牌 / 角标，用 `docs/ai/tools/overlay_check.py`）→ `mix_audio.py` → `render_all.py`（先 `ListAgents`，一次只跑一个渲染；内存紧时 `RENDER_WORKERS=2`）→ `qa_mix.py` → `finish.py`。**先把引擎副本和模板同步一次**（技能步骤 5）。第 6 期画面要避开 `skip` 里登记的 MultiEdit 配置镜头。
2. 封面 3×3：每期写 `制作\04_封面\candidates_framed.json`（官方视频里 Lewis 的安静帧或终端 / 图示截图，黄贴纸 `官方教程 第N期`，大字想法见下）→ `make_cover_framed.py`；标题 3×3 写 `投稿信息.json` → `check_titles.py`（B 站 ≤80 / 抖音 ≤30 / 小红书 ≤20，统一 `Claude官方教程 第N期｜讲什么`）。
3. 交付包（参照 `独立视频\短视频\_TimDenning系列\make_delivery.py` 改一份）：成片路径 + 手机预览 + 封面总览 + 标题 + 默认项 + 要耳朵听的句子，发给用户；回“封面 X 标题 Y 同意”才发布（B 站 / 抖音 / 小红书；视频号 2026-10-06 起不发；小红书原创声明开 + “笔记含AI合成内容”）。合集「Claude官方教程」三个平台都还没建。
4. 记得告诉用户：Fish 账号里多了两个“未命名项目”（整稿 120 句 + 补录 15 句，可以删）；两批导出共约 1.0 万积分（9196 + 994，另有 1390 的试配音）。
- 封面大字的想法：1「不是聊天框 / 会自己验收」；2「一条命令 / 装好它」；3「先别让它 / 写代码」；4「提示越含糊 / 越费上下文」；5「每次开机 / 像第一天上班」；6「通常照做 / 和一定照做」；7「脏活外包 / 只收结论」；8「别再每次 / 粘贴同一段」；9「代码库之外 / 靠 MCP 接」；10「六种权限 / 怎么选」。

## 踩的坑 / 做法（新会话别重踩）
- **共用 Chrome 窗口**（hwnd 3082854，Tim Denning 会话的 B 站 / 抖音 / 小红书标签在里面）：我的 Fish 标签平时是 hidden；要键入时先 `SendMessage` 给“Tim Denning 观点视频系列”说“我要前台”，再 `chrome_tabs.ps1 -Select "Claude Academy" -Also "Fish"` + `-Front 3082854`，JS 确认 `visibilityState === 'visible'` 再 `computer type`；用完 `-Select "Tim Denning" -Also "创作中心"` 选回并发“前台空了”。Fish 的按钮（新建项目 / 空白项目 / 声音 / 模型 / 生成 / 导出）用 JS `.click()` 在 hidden 标签里也行。
- 键入长文用 `json.dumps(ensure_ascii=True)` 打出转义串再贴，别手敲 `\uXXXX`（第一次把“趁手”敲成了“趋手”）；键入后一定对 SHA-256；改某一块要真点（`triple_click` 坐标，别用 `find` 的 ref——那次点到了时间轴上的块）。
- 估时：温柔男生每个汉字约 0.19–0.21 s、每个英文词另加约 0.3 s 的估法偏长 8%，`line_durs` 已乘 0.92。
- 机器内存只剩 1–3 GB（别的任务也在渲染）：渲染前看 `ListAgents` 和空闲内存。
- 没有提交任何 git。
