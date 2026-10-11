# OpenAI DevDay 2026 解读（独立视频，6 条短片）

素材是 OpenAI DevDay 2026 主题演讲全程（53 分 34 秒，YouTube 官方直播回放，用户 2026-10-02 给的三个文件）。按发布的内容拆成 6 条独立短片：曼波声线中文画外音讲解 + 发布会原话片段（原声压低、中文同声传译）+ 幻灯片 / 现场演示画面。2340×1080，字幕、版式和《白宫超级智能协定》同一套。

**状态（2026-10-02）**：6 条成片都做好了，在 `成片/`（含悠一片头 3.8 s + 片尾 4.8 s）。**没投稿**；封面做好了（`制作/04_封面/`，每条 16:9 + 4:3，OpenAI 蓝 #0285FF，`make_covers.py` 生成）；等用户听配音、定片尾清单（`制作/00_整片/outro.json` 是草稿）、标题。

| 条 | 成片 | 时长 | 内容（发布会时间） |
|---|---|---|---|
| V1 | `成片/V1_Dots_成片.mp4` | 87.2 s | Dots 全天在线的 AI 助理：产品短片、云端电脑、短信 / 电话、可用范围（2:24–8:00、17:22） |
| V2 | `成片/V2_Space_成片.mp4` | 97.0 s | ChatGPT Space、Holly 现场演示、Slack 里转给 Dot、每天修几十个 bug、专家 Dots（8:20–18:25） |
| V3 | `成片/V3_GPT-6.1-Sol和Ultra-Fast_成片.mp4` | 88.8 s | GPT-6.1 Sol 价格是 Astra 的 1/5、缓存输入 95% 折扣、Ultra Fast 8 倍速度、火箭对比、Pro 500 / Pro 200（19:39–22:15） |
| V4 | `成片/V4_Decisions-API和AI研究实习生_成片.mp4` | 101.7 s | Decisions API 几分之一秒的响应、Luna 模型做选择、AI 研究实习生目标达成、Tejal 的数据（22:13–27:20） |
| V5 | `成片/V5_Codex上云和Agents-API_成片.mp4` | 95.1 s | Codex 全面上云、Security Cloud、Agents API、AWS、Private Intelligence、最快的 API（28:14–31:25；40:31） |
| V6 | `成片/V6_登录插件和Marketplace_成片.mp4` | 97.5 s | 12 亿周活、用 ChatGPT 登录、插件扩展、被发现、OpenAI Marketplace（44:09–47:35） |

标题草稿在各条 `台本/V?_*.json` 的 `title`（用户没定）。

## 目录

```text
素材/                 keynote_video_silent.mp4（1080p、29.97 fps、无声）、keynote_audio.weba（和画面同一起点，差 0.03 s）、keynote_youtube_cc_en.srt（YouTube 自动字幕，文字有错，只用来定位）
素材/转写/             keynote.json / .txt / keynote_en.srt（本机 faster-whisper large-v3-turbo 词级转写）、chatcut_transcript_nots.md（ChatCut 的整场转写稿，文字准、无时间戳）
台本/                 V?_*.json：每条一个，lines（字幕 zh / 念的字 say / 讲话人 who）+ plan（卡片、发布会画面的入点、同传锚点）
成片/                 6 条成片（含片头片尾）
制作/00_整片/          common.py、build_timeline.py → prep_frames.py → mix_audio.py → render_all.py（4 路）→ qa_mix.py → package.py（加片头片尾）；check_in_points.py（每段入点画面联系表）；index.html、engine.js、scenes.js；outro.json（片尾清单草稿）；out/V?/ 是各条的产出（timeline、frames、media 抽帧、mix.wav、整片）
制作/02_配音/          make_lines.py → （Fish 网页版生成）→ asr.py → tts_pick.py（逐句挑版本）→ tts_build.py → tts_qa.py；tts/raw/A_v1.mp3、A_v2.mp3 = 整套 84 句一次生成的两个版本；edit/ 是挑好版本的口播和每句时间
制作/transcribe_keynote.py、merge_transcripts.py、words.py   整场转写、合并、查某段时间的逐词时间
```

做一条（例 `V1`）：`python build_timeline.py V1` → `prep_frames.py V1` → `mix_audio.py V1` → `render_all.py V1`（同一时间只跑一个渲染）→ `qa_mix.py V1` → `package.py V1`。用法见每个脚本开头的说明；`out/V?/media/` 是抽出来的帧（共约 1.6 GB，渲完可以删，`prep_frames.py` 能重做）。
