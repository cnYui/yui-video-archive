# 日报配音改用本机开源 TTS（女声）

2026-10-14，用户要求：看 routine 里 B 站《AI每日日报》那个，“现在没有配音；找本地能运行的 TTS 模型，人机声音就可以；用免费的，不要再用别人收费的；用女声；替换掉原先工作流里用浏览器插件去网页里生成声音的模块”。

## 背景
- Fish Audio Plus 积分用完（1,681 / 250,000，10/28 刷新），10/12、10/13、10/14 三期只能发“无人声 + BGM”版（Windows Huihui 引导音轨定字幕时间，`DAILY_SILENT=1`），见 `AI日报/运行记录.md`。
- routine = 本机定时任务 `ai-daily-news-produce`（东京 04:30），指令文件 `C:\Users\yui\.claude\scheduled-tasks\ai-daily-news-produce\SKILL.md`，技能 `AI日报/skill/ai-daily-news/SKILL.md`（`~/.claude/skills/ai-daily-news` 是它的联接）。

## 选型（机器：Core Ultra 5 225H 14 核、31 GB、Intel Arc 核显，没有 NVIDIA；同一份 10/13 台本，Whisper small 识别分，Fish 版 0.86，gate 门槛 0.75）
| 模型 | 识别分 | 速度（CPU） | 结论 |
|---|---|---|---|
| Kokoro-82M v1.1 中文（sherpa-onnx int8，sid 3） | 0.70（前 300 字） | 1.1–1.4× 实时 | 没接 |
| MeloTTS 中英（sherpa-onnx，单一女声） | 0.74（整期 0.715–0.74） | 0.35× 实时（整期 2 分钟） | 备选（过不了 0.75 的概率大） |
| **Qwen3-TTS-12Hz-0.6B-CustomVoice（Vivian）** | **0.867（加速 1.15 倍后 0.874）** | 单句 5.4×、8 句一批 1.7× 实时（整期 709 s） | **主力** |
Qwen3-TTS：阿里开源、Apache-2.0；中文女声 Vivian（明亮）/ Serena（温柔）。

## 改了什么
- 新增 `AI日报/skill/ai-daily-news/scripts/local_tts.py`：切句（≤70 字）→ 按长度排序、8 句一批合成 → 逐句缓存（`配音/local_<引擎>/`，断了续跑、改几句只重做几句）→ 拼成 wav；不正常时长的句子自动换种子重做。引擎 `qwen`（venv-qwen）/ `melo`（sherpa-onnx）/ `sapi`（Windows Huihui，PowerShell System.Speech，只做无人声版的引导音轨）。
- `daily.py` 新增 `localtts`（`--engine auto|qwen|melo|sapi`、`--speaker`、`--tempo`、`--seed`、`--timeout`）：auto = 先 qwen，报错或超过 2700 s 换 melo；qwen 默认再加速 1.15 倍（ffmpeg atempo，原速 5.5 字/秒比苏晓晓 6.35 慢）；写 `配音/raw/C01_vN.mp3`、`api_takes.json`、`local_tts_usage.txt`、state 的 `tts` 阶段；`render` 看到 `silent` 自动设 `DAILY_SILENT=1`；B 站简介里的 AI 声明按引擎写（`voice_note`）。`webvoice` / `tts --api` 代码留着但不再调用。
- 技能 SKILL.md：第 5 步重写、规则 / 路径 / 开工检查 / 踩坑表更新；Fish 网页版旧做法存档到 `AI日报/skill/ai-daily-news/references/_archive/Fish网页版配音_已停用_20261014.md`。
- routine 指令文件：配音改 `localtts`（后台、3600000 ms 超时），开工检查、安全、结束前关标签页、最终报告里去掉 Fish；兜底 = 先修环境，修不好才退到无人声版（用户 10/13 定的）。
- AGENTS.md：日报配音一栏和“AI 配音一律用 Fish 网页版”那条（日报例外）。
- 模型和环境在 `AI日报/素材/本地TTS/`（gitignore 的“素材/”之下，不进 git），说明见那里的 README.md；试听样例在 `素材/本地TTS/试听/`。

## 验证
- 用 10/13 台本在 `AI日报/_试跑_本地TTS/` 全流程跑到 `daily.py voice`：qwen 整期 709 s、加速后 374.2 s，选版分 0.872，切 60 段、`total voice` 355.9 s（> 285）；`--engine auto --timeout 5` 触发 qwen 超时后自动换 melo 成功；sapi 引导音轨 5 s 出完；简介 AI 声明三种引擎都对。
- **没做**：用新配音跑完整 `render`（4 路渲染）和 gate；耳朵听感（我只能用语音识别打分）——用户先听 `素材/本地TTS/试听/` 的样例。

## 风险 / 待办
- qwen 整期约 12 分钟 + 载入，比 Fish 网页版（约 2 分钟）长；routine 台本写完得晚于北京 ~05:15 就可能赶不上 06:00 定时（技能已有“05:00 前后压条数”的规则）。
- 英文名读音：Meta 被听成 Mate / META，识别分 0.87 主要被这类拖低；真读错的词在台本 `tts` 里写近音。
- 10/12–10/14 三期已发的是无人声版，没重做；要不要补配音版由用户定（需要重新渲染 + 改稿件，B 站改视频要重新审核）。
- 下次 routine（10/15 东京 04:32）是第一次真跑，注意看 `配音/raw/local_tts_usage.txt` 和运行记录。
