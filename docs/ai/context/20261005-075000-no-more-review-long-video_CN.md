# 独立视频长视频《不再 Review》：为什么 AI 时代有人不再逐个 Review PR（2026-10-05）

## 用户要求（原话）

> https://x.com/dotey/status/2106635352609865925?s=20  https://x.com/poteto/status/2106134336705843554?s=20  https://www.youtube.com/live/MN9dGgmLyso?si=3pwHdO8TZWpkD--J youtube视频和twitter链接需要你下载，然后asr，围绕 不再review这个主题做一个长视频，讲解为什么ai时代不再review pr，长视频要加上开头和结尾的开场视频

“开头和结尾的开场视频” = 悠一共用片头片尾（片头 4.8 s、片尾 9.0 s，`pack_info.py` 读时长）。

## 素材（都在 `独立视频/素材/2026-10_不再Review/`，整个目录被 .gitignore 忽略）

| 素材 | 说明 |
|---|---|
| `YouTube直播_MattPocock×poteto/MattPocock_poteto_直播_MN9dGgmLyso.mp4` | Matt Pocock 的 YouTube 直播（2026-10-02 美国时间，65:36，1080p）。yt-dlp 下 137 + 140 合并（用户没点名下载网站，用 yt-dlp；X 视频流程里的 SaveTwitter / iiilab 这次没用）。画面是 Matt（左）、Lauren（右）并排或单人讲话人视图；同目录有 YouTube 自动字幕 json3 |
| `转写/`（interview.json / .txt / _en.srt） | faster-whisper large-v3-turbo CPU int8 词级转写，分两半并行（各约 23 分钟） |
| `X推文/dotey_2106635352609865925.*`、`poteto_2106134336705843554.*` | 两条用户给的推文**都没有视频**：宝玉那条是约 3900 字的长文（X 长推文，嵌入接口只给前面一小段，全文用 `api.fxtwitter.com` 取），引用 Lauren 那条；Lauren 那条是带 YouTube 链接卡片的纯文字。所以“下载”落成了：存全文 + 页面截图（X 嵌入页） |
| `X推文/poteto_演讲视频_2102050467505430555/` | 事实核对子代理找到的 **Lauren 的原始演讲视频**（2026-09-21 在 X 上发的，“here's how i shipped 2,500 PRs last month to production”，38:02，1720×1080 60 fps，3,024,003 次浏览）：tldraw 幻灯片 + 她的头像圆框 + 烧录英文字幕。**用户没点这条，是我加的素材**，只当画外音段的幻灯片画面用（静音、裁掉字幕条和头像）。同样转写（`转写_演讲/`） |

## 事实核对（子代理 15 分钟时间盒 + 我对转写，全文 `独立视频/长视频/2026-10_不再Review/台本/事实核对.md`）

- pstack 不是独立仓库：`github.com/cursor/plugins/tree/main/pstack`，MIT，署名 Lauren Tan；官方“全自动”叫 `autopilot-full`：每个 PR 一个 owner、一组独立验证者出裁决，**只有干净的裁决才允许合并**；另有 `autopilot-stack`（不合并，留给人审）。官方指南 `07-overnight.md` 有一句“You're auditing decisions, not re-reading the whole night.”
- “2500”是她自报：演讲首页写 **2000**，推文写 2500，访谈里她口头说“2000 and 2500”，Cursor Compile 日程写 2,000。所以旁白和字幕**不把 2500 当统计数字**，开场用“2000 多个”，并明说“演讲首页写 2000，推文写 2500”。
- Lauren Tan：X 简介 “Grok @Bot at @SpaceXAI”；Cursor 8 月 14 日被 SpaceX 收购（官方博客）；宝玉写“并入 SpaceXAI”官方没这么说，旁白不写收购。
- 宝玉“半年前说不怎么 Review PR”：他写的是“我记得”，没找到那条推文，旁白写“他记得”。
- 宝玉长文第五部分（模型、Token、2 个 Claude Max 20x 账号、验证不能全交给 AI、方向靠人）是他自己的点评，旁白一律挂名“宝玉说”。

## 做法（流程照 `claude-code-episode` 的引擎模板，加了“原话 + 中文同传”）

- 目录：`独立视频/长视频/2026-10_不再Review/`（台本 / 制作 / 成片）；不属于任何合集。
- 引擎：`制作/00_整片/` 从 `Claude Code相关/skill/claude-code-episode/assets/engine-template/` 拷来改：`build_timeline.py` 加 `dub` 场景（OpenAI-DevDay 的“原话 + 同传”：同传比原话晚 0.3 s、念不完加速 ≤ 1.18、不够就延长片段）、cue 带 `key`（台本里给句子起名字，scenes.js 里 `S('x2_recall')`）；`mix_audio.py` 同传段原声压到固定 −29 LUFS、画外音段 mute，另出 `audio/voice_only.wav` 给 `qa_mix.py` 逐句核对；`prep_frames.py` 加 range 的 `bg`（白底幻灯片用纯色补边，别用暗色模糊底）；`scenes.js` 来源角标 + 讲话人标签 + 数字标注 `stat()`。
- 台本唯一来源 `台本/make_script.py`（生成 `录制稿.json` 和 `plan.json`）。**2026-10-04 起照 AI大圆镜 的写法**：钩子带数字、短分句、泼冷水、金句收尾；第三人称，宝玉、Lauren 直接叫名字；不用“不是……而是……”。
- 配音：Fish 故事工作室空白项目，声线「温柔男生」+ S2 Pro（画外音和同传同一个声线）。
- 画面：访谈同传段 + 她演讲里的幻灯片 + X 推文截图 + pstack README / 官方指南页面录屏（Playwright）。

## 状态

见本文件后面追加的各节。

## 状态（2026-10-05 09:10，用量用完，停在“等 Fish 配音”）

**已做完**（都在 `独立视频/长视频/2026-10_不再Review/` 和 `独立视频/素材/2026-10_不再Review/`）：
- 素材下载、两份词级转写（访谈 / 她的 X 演讲）、宝玉长推文全文、`台本/事实核对.md`；X 嵌入页和 pstack README / 官方指南的页面录屏（`制作/00_整片/capture_pages.py`）。
- 台本 `台本/make_script.py`（改台本只改它，重跑生成 `录制稿.json` / `plan.json`）：90 句（45 句画外音 + 45 句同传），按字数估 464 s（约 7:44，另加片头 4.8 s、片尾 9.0 s）；口径已改成“演讲首页写 2000、推文写 2500”，宝玉的点评一律挂名。后加了她演讲里“whenever you correct your agent”那张表（人眼 Review 是最弱的一层，PR 来得太快“根本不可能”）。
- 引擎（`制作/00_整片/`）：`build_timeline.py` 有 `dub`（原话 + 同传，同传段 `cap_out` 定格）、`mix_audio.py`（同传段原声 −29 LUFS，另出 `audio/voice_only.wav`）、`prep_frames.py` 的 range `bg` 纯色补边、`scenes.js` 的叠加层（key 命名取字幕条）。静帧逐段看过，`check_subs.py` 通过；帧已抽（`media/scr`）。`outro.json`、`make_submission.py`（标题 3 个候选，简介 1988 字）、`.gitignore` 规则、`制作/02_配音/tts_input.txt`、`qa_names.py` 都备好。
- 封面候选 A（Lauren 笑着听 + “不再Review”，**推荐**）/ B（GitHub 贡献曲线 + “2000个PR / 谁来审？”）/ C（并排画面 + “AI自己合并”），16:9 和 4:3 都在 `制作/04_封面/封面_*.png`。

**没做**（按顺序）：
1. **Fish 配音**：声音「温柔男生」+ S2 Pro，故事工作室空白项目。我已在 Chrome 里建好一个空白项目（标签是 hidden，会话结束后可关）；排队时我让给了「开源信息短视频制作」会话（它约 09:15 用完）。轮到时：`powershell -File D:\大疆\docs\ai\tools\chrome_win.ps1 -Action front -Hwnd <窗口句柄>`（含各会话标签组的那个窗口，之前是 272565968），JS 确认 `visibilityState === 'visible'` 再键入；整稿 90 行分 4 段（≤ 25 句 / 段，CDP 超时但文字其实写进去了），用 `crypto.subtle.digest` 对全部 `div.content` 文字的 SHA-256 和 `tts_input.txt` 的比（`'\n'.join(say)` 的哈希是 `205f49b5…ee13`，改过台本要重算），一致才点“生成”；导出“按段落拆分” → `制作/02_配音/import_segments.py <zip>`。
2. `build_voice.py --qa` 和 `qa_names.py`（专名读音要用英文识别器听一遍）→ `build_timeline.py`（真时间，看加速 / 定格）→ `check_subs.py` → `prep_frames.py` → `render_all.py --stills-segs` 重看叠加层时刻（`scenes.js` 里 `stat / note / box` 按 key 取字幕条，时间会随配音变）。
3. `mix_audio.py` → `render_all.py`（4 路，先 `ListAgents`，「长视频制作与素材下载」会话在渲，等它说“渲染完了”）→ `qa_mix.py`（用 voice_only.wav）→ `finish.py`（片头片尾 + 手机预览 + 三份 SRT）→ `predeliver_check.py "<本期目录>"`。
4. 用户选封面（`make_cover.py --select A`）、定标题（`投稿信息.json` 三个候选）、听配音、确认片尾清单；再 `make_submission.py` 重算章节时间；用户拖 mp4 → 我用插件填 B 站表，**用户说“发布”才点**。
5. 文档：`AGENTS.md`「独立视频」一节加一条、`独立视频/README.md` 表加一行、根 `README.md` 视频存档、记忆。

**要点 / 坑**：两条推文都没视频；长推文全文用 `api.fxtwitter.com`；Lauren 的演讲视频是我加的素材（幻灯片 crop 要避开右下头像圆框和字幕条，见 `make_script.py` 的 `crop()`）；dcg 钩子会拦内嵌 Python 里的 `shutil.rmtree`（用 `tempfile.TemporaryDirectory`）；Fish 隐藏标签里 `computer type` 会丢字，必须先前置窗口。

## 状态（2026-10-05 11:30，长视频成片做好，等用户选封面 / 标题、听配音、确认片尾清单）

**做完了**（都在 `独立视频/长视频/2026-10_不再Review/`）：
- **配音**：Fish 故事工作室空白项目（我自己的 Chrome 窗口，标签组名“AI时代PR审查讨论视频”），声线「温柔男生」+ S2 Pro，90 句整稿一次生成、导出“按段落拆分”一次成功，`import_segments.py` 逐句文字一致；有声 289.8 s。
- **时间轴**：正片 437.6 s（不用加速），片头 4.8 + 片尾 9.0 → 成片 451.4 s。`mix_audio.py` 混音 −16 LUFS（同传段原声 −29 LUFS）。
- **渲染**：第一次 4 路 13128 帧；抽成片帧逐个叠加层看（`ov_times.py` 取每个叠加层的起止 → 抽中间那一帧拼表）发现 **288 s“8 × 1万+”数字框（`{right:40, y:40}`）盖住右上角来源角标，还遮了幻灯片标题的后半句**；同时看到**访谈左下角直播自带的“Matt”名牌被说明条（y 690）盖掉一半**。改 `制作/00_整片/scenes.js`：数字框挪到这张幻灯片左下角、不带说明行（`{x:40, bottom:20}`）；访谈上的说明条统一 `NY = 650`（下沿 746 < 名牌上沿 754），`2000 / 2500` 数字框 `bottom: 80`；`note()` 加 `fast` 选项（前后只淡 0.1 s），连着几条同位置的条（b6_q→b6_door、b8_model→b8_token→b8_verify）前一条在后一条开始前 0.1 s 收掉，不再叠影。静帧确认后整片重渲（3 路，内存只剩 4.8 GB，834 s，0 报错）。**教训：渲完要把每个叠加层的中间帧都抽出来看一遍，别只看每场景 3 张静帧；说明条 / 数字框的位置要避开素材自带的名牌和角标。**
- **质检**：`qa_mix.py`（voice_only.wav 逐条识别）90 条，低于 0.8 的只有 2 条：K03（识别写成 2500，原文“两千、两千五百”，数字写法差异，听对了）、**N19“她靠两样东西”被听成“他考了两样东西”（靠 / 考）——要用耳朵听**；0.8–0.9 的几条都是专名 / 他她（Loren Tan / Grog Bot / grovebot）。没跑 `qa_names.py`（整句识别已覆盖，专名读音由用户耳朵听）。
- **`finish.py`**：片头片尾（`add_to_video.py`，正片不重编码）→ `不再Review_成片.mp4` 451.42 s、191.2 MB、−16.2 LUFS、LRA 11.1、真峰值 −0.9 dBFS；手机预览 23.6 MB；三份 SRT 104 条（含片头偏移 4.8 s）。
- **`make_submission.py`**：章节时间（含片头）00:00 … 07:13 共 13 条；章节“宝玉：这个质疑，他半年前也挨过”改成第三人称；标题 3 个候选、简介 1988 字、标签 10 个。
- **`predeliver_check.py`**：全部通过。`封面_选定_16x9 / 4x3.png` 现在是**暂按推荐的 A 复制的**（`make_cover.py --select A`），用户选了别的就 `--select B|C` 再跑一遍 predeliver。
- 片尾清单草稿（`制作/00_整片/outro.json`，**按规矩要用户确认**）：参考文献 4 条（Matt Pocock 直播 / Lauren 的演讲视频 / 宝玉的总结与点评 / pstack 与官方指南）；致谢：画面 Matt Pocock · Lauren Tan、长文 宝玉 @dotey、配音 温柔男生声线（AI 生成）、剪辑 Claude Code（Sonnet 5.5）。

**没做**（按顺序）：
1. 用户选封面（A / B / C）和标题（3 个候选）、听配音（重点 N19“她靠两样东西”，专名 Lauren Tan / poteto / pstack / Grok Bot / SpaceXAI / autopilot-full）、确认片尾清单。
2. 投稿：用户把 mp4 拖进 B 站上传页，我用 Chrome 插件填表；**用户说“发布”才点**；不选合集、分区人工智能、含 AI 生成内容。投稿后把线上标题同步回 `投稿信息.json`，补 README / 根 README 的视频存档 / 独立视频 README 的 B 站链接。
3. Fish 里两个“未命名项目”（长视频 90 句那个 `3fc80d37…`、短视频 12 句那个 `81cd3618…`）可以在用户听完确认不重配之后删。

**同题短视频**见 `docs/ai/context/20261005-113000-no-more-review-short-video_CN.md`（`独立视频/短视频/2026-10_不再Review/`，54 s，dual，交付包已发用户）。
