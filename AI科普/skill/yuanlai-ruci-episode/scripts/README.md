# scripts 命令速查（按制作顺序）

`S` = 本目录 `D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts`，`<期>` = 本期目录（如 `D:/大疆/AI科普/第02期_Token是什么`）。
每个脚本都有 `--help`；除 render / render_parallel 外都接受 `--series`（默认 `D:/大疆/AI科普`）。共用规则（段号、语速、动作词表、背景轮换、路径、讲解员预设）只在 `epcommon.py` 里改。
讲解员：每期写在 `episode.json` 的 `presenter`（预设 `epcommon.PRESENTERS`：`ryo` 山田凉；`whale` 鲸鱼娘，DeepSeek 拟人，素材包叫大肥鱼）；开场自称、角色帧目录、Fish Audio 音色、封面角色都从这里取，没写 = 山田凉。
画面尺寸：`episode.json` 的 `canvas`（新期 `[2340, 1080]` = 19.5:9；没写 = 1920×1080，第 1 期）→ build_timeline 抄进 `timeline.episode.canvas` → 引擎、render / render_parallel / check_layout、assemble（含片头片尾）都按它出图（`epcommon.canvas_of`、`render.canvas_size` 同一套规则：高 1080、宽 ≥1920 的偶数）。scenes.js 按居中的 1920×1080 内容舞台写坐标。封面不跟它走：永远 16:9 + 4:3。
✋ = 这一步之后停下来等用户确认。

| # | 命令 | 做什么 |
|---|---|---|
| 1 | `python S/new_episode.py --number N --title "题目" --presenter ryo\|whale [--canvas 2340x1080] [--bg-color #FFFFFF\|none] [--layout center\|old] [--style board\|cards] [--voice user\|tts]` | 建 `第NN期_题目/`：episode.json（含完整的 presenter，默认 ryo；`canvas` 默认 `[2340, 1080]`；`bg_color` 默认 `"#FFFFFF"` = 白底、视频不用背景图，`none` = 不写；`layout` 默认 `"center"` = 内容以画面中线居中，`old` = 不写；`style` 默认 `"board"` = 白板手写版，`cards` = 不写；`voice_source` 默认 `"user"` = 用户自己配音，`tts` = Fish Audio 合成）、台本/script_data.py 骨架（开场“大家好，我是{讲解员}”）、制作/engine/（模板；scenes.js 起点）；讲解员的帧目录还没有 anims.json 时提醒。测试期加 `--dest D:/大疆/AI科普/_skilltest` |
| 1′ | `python S/new_episode.py --update-engine <期>` | 引擎模板更新后刷新本期引擎（不动 scenes.js 和 episode.json，被换下的文件进 `_旧稿/`）。老目录要改成 2340×1080：先这一步，再在 episode.json 加 `"canvas": [2340, 1080]`，从 7 往下重跑 |
| 2 | `python S/build_script.py <期>` | 写完 script_data.py 后生成 台本/台本.md（写明本期讲解员和音色）、配音分段.json；报开场白不是“大家好，我是{讲解员}”、台词里别的讲解员的“我是……”、词表外动作、动作用量（总数、一段多个、大动作间隔、贴纸、好耶至少 1 次、数一→数二→数三 顺序……）、动作帧在不在讲解员的帧目录、角色梗、“待写”、超时长 ✋ |
| 3 | `python S/chunk_voice.py <期> --whole [--force]` | 配音/chunks.json = 整期一批 C01（自己录音和 AI 配音都要这一步；它打印的音色和“下一步 tts_api.py”只对 AI 配音有用）。不带 `--whole` = 旧的按场景 ≤480 字节分批（网页版用，《AI每日日报》的 daily.py 也这样调，行为不变） |
| 4 | `python S/record_script.py <期>` | **自己录音**（2026-09-28 起默认，episode.json `"voice_source": "user"`；做法见 references/voice.md「自己录音」）：→ 配音/录音稿.md（怎么录 + 读法表 + 按章节每句的段号和字幕原文，英文 / 数字每章第一次出现时提示「读作」）、配音/录音稿.txt（提词用，一句一行，没有段号）✋ 把录音稿发给用户录 |
| 4′ | `python S/import_voice.py <期> <文件1> [文件2 …] [--denoise] [--limit auto\|on\|off] [--no-level]`；补录一句：`… --segment S03-12 <文件>` | 用户的录音（wav / m4a / mp3 / 手机视频）按给的顺序转成 44.1 kHz 单声道、文件之间 1 秒静音 → 配音/raw/C01_vN.wav + .json（N 往后编，不覆盖）；70 Hz 高通，每个文件线性调到 -20 LUFS（个别爆峰让音量调不上去时才自动压峰），`--denoise` 降噪；还没有 chunks.json 时自动跑 3。补录 → 配音/raw/pickups/<段号>_vN.wav，6 会用最新的补录替换这一句 |
| 4″ | `python S/tts_api.py <期> [--dry-run] [--takes 1] [--only C01]` | **AI 配音：《原LAI如此》不再用；用户点名要 AI 配音时才用（AI 配音现在只用于《AI每日日报》；episode.json `voice_source` 写 `"tts"` 或不写）。** Fish Audio API（key 读用户环境变量 `FISH_API_KEY`，不打印不保存）用本期讲解员的音色（`presenter.voice_id`）、模型 s1 生成 → 配音/raw/C01_v1.mp3；只补“还没有和当前文字一致的版本”的批次，`--only C01` 再加一个版本；打印字节和费用（s1 每百万字节 15 美元，一期约 0.09 美元），记到 配音/raw/api_usage.jsonl；401/402 直接停 |
| 5 | `python S/select_takes.py <期> [--take C01_v2.wav]` | 语音识别给每个版本打分 → 配音/selection.json。自己录音：只看导入的 .wav，**用最新导入的一版**（`--take` 指定别的），和字幕原文比对（台本的字找到多少、多出多少字），带词时间的识别缓存在 配音/raw/asr_words.json 给 6 用。AI 配音：每批选分最高的 ✋（请用户试听整期）。《AI每日日报》的 daily.py 也调它（可带 `--hist`），行为不变 |
| 6 | `python S/segment_audio.py <期>` | 按段切音频 → 配音/segments/*.wav、report.txt、制作/voice/durations.json、alignment.json。自己录音：整期全局对齐（重读、读了一半停下、噪音都跳过，同一句读两遍用后一遍），每句按前后的停顿单独切，有补录的句子用最新补录；report.txt / report.json 列每句的匹配度（< 0.8 = 可能读错 / 漏读 → 4′ `--segment` 补录）、按声音修正过切点的句子、跳过的声音（≥ 0.8 s，带原文件里的时间）✋ 请用户听报告里列出的句子。AI 配音的切法不变（daily.py 也调）。两个脚本都有 `--user-voice`（测试用：不看 episode.json 按自己录音处理） |
| 7 | `python S/build_timeline.py <期>` | → 制作/timeline.json（含 episode（连同检查过的 canvas）、actions、toc）、chapters_bilibili.txt；canvas 写法不对（不是高 1080、宽 ≥1920 的偶数）直接停下；报动作重叠、大动作间隔（实际时长）、缺背景、超时长；和开场走入重叠的动作推到走入之后。字幕断行：单行 ≤20 宽，英文词 / 路径 / 橙色术语（内置 + episode.json `terms`）不拆，避头尾（”）。，… 不放行首，“（《 不放行尾），细则见 references/assemble.md §1 |
| 8 | `python S/mix_audio.py <期>` | → timeline 的 mouth、制作/build/mix.wav（-16 LUFS）。每次 build_timeline 提示要重跑就重跑 |
| 9 | `python <期>/制作/engine/sync_assets.py --series D:/大疆/AI科普` | → engine/assets.js、assets.css（素材相对路径 + 缺素材检查，缺了退出码 1）。打印时间轴的 canvas；episode.json 的 canvas 和时间轴里的不一样时提醒重跑 7。角色帧和她的 anims.json（注册表、patch_rects、anchor 等几何）从 `presenter.frames` 读，缺帧时写明哪个讲解员缺哪个 key；缺的动作帧只出草稿加 `--allow-missing`（退回待机）。她的帧目录还没有时加 `--frames <相对 素材/ 的目录>` 临时换一个（如 `角色/大肥鱼像素素材包/素材`，不改 episode.json），再 `assemble.py --no-sync`；帧目录不存在 / 没有 anims.json / 没有待机帧 idle_m0..2 时直接报错（`--allow-missing` 也不放行，不再出占位小人），报错里给出可用的 `--frames`。assemble 会自动跑（不带 --frames）。新动作帧还在预览目录时加 `--sprites-extra <目录>`，或在 episode.json 写 `sprites_extra`（assemble 重跑时也生效） |
| 10 | `python S/render.py <期>/制作/engine/index.html --data <期>/制作/timeline.json --stills 12.5,40 --stills-dir <期>/制作/build/stills` | 抽帧自查（`--sheet 文件.png --sheet-count 24` 出联系表，缩略图保持画面比例）；尺寸取 data 里的 canvas（时间轴 `episode.canvas` 或片头片尾 data 的 `canvas`），没有就 1920×1080，`--size 2340x1080` 可强制；退出码 2 = 页面报错（包括页面比画面窄：本期引擎是改尺寸以前的，先 1′） |
| 11 | `python <期>/制作/engine/check_layout.py`（在 `<期>/制作/` 下） | 按 canvas 开页面，查卡片文字溢出、压字幕（画布居中 1240 宽）/ 角色 / 目录 / 进度条（全宽）、出画布、`low-contrast`（文字和背后的底色几乎同色，对比度 < 1.6：纸白字在纸白卡片上、墨黑字在深色背景上）；疑问卡飞进目录那一刻压到目录标成 `expected`，不计入 issues；位置是画布坐标（2340 宽时 = 舞台坐标 + 210）；最后打印台本动作和自动层（`ENG.autoPlan`）各通道的数量 |
| 12 | `python S/assemble.py <期> [--workers 4] [--skip-main]`（默认 4 路，2026-09-28 用户定：所有渲染统一 4 路并行） | 片头 + 正片 + 片尾（都按 canvas 原生渲染，片头片尾 data 带 `canvas`）→ `<期>/第NN期_题目_成片.mp4`、`_字幕.srt`、`_章节.txt`；outro_items 为空、episode.json 和时间轴的 canvas 不一致、各段尺寸不是 canvas、帧数或时长不对、页面报错都会停下 ✋ |
| 13 | `python S/make_cover.py <期> [--html-only]` | 按 episode.json 的 `style` 选模板（cover.json 写 `"style"` 可改）：`board` = 白板版 `cover.board.html`（白底、手写标题，笔画用本期引擎的 hand.js / hand_glyphs.py，写进 `封面/_handdata.js`；第一次运行出骨架 `{t1, t2, sub, hl, sprite}`），其他 = 小票卡片；封面 16:9（1920×1080）/ 4:3（1440×1080）+ `封面_预览.png`（不跟视频的 canvas 走）；角色是本期讲解员（她帧目录的 `reach_m2/00.png`，没有时先用 `idle_m0` 并提醒），套用讲解员预设的封面参数（`PRESENTERS[id]["cover"]`） ✋ |

其他：
- 网页版配音（2026-09-27 起停用，第 1、2 期用过）：`python S/fetch_check.py <期> C02 <url1> <url2>`（或 `--urls 文件`）下载网页版生成的录音并打分，`select_takes.py --hist` 找回历史记录里的录音。现在只在需要复查老期时用。
- `uservoice.py`：自己录音的共用部分（4′、5、6 用，不是命令）：识别缓存、字幕原文和识别结果的全局对齐（跳过重读）、按停顿切句和修正识别时间。改切句规则只改这里。
- `python S/render_parallel.py <html> --data timeline.json --workers 4 -o main.mp4 [--size WxH] [--stagger 0.7]` — assemble 用的底层正片渲染（尺寸 = 时间轴 canvas；各路相隔 --stagger 秒启动；卡住自动重启续渲，缺帧或尺寸不对退出码 1，页面报错退出码 2；加载失败带文件地址，引擎重试救回来的图片不算报错）。
- `python S/add_to_video.py <视频.mp4> --outro-data <片尾清单.json> [-o 输出.mp4] [--no-music]` — 给真人素材等别的视频加片头片尾（名字 / 签名是悠一；BGM 用 `素材/音频/bgm.wav`），片尾清单先问用户。片头片尾按原视频尺寸渲染：16:9 用 1920×1080 页面按比例缩放（和以前一样），比 16:9 宽（2340×1080 等）开同比例的宽画布、构图居中铺满全宽。临时文件放在输出文件旁边（`_tmp_add_to_video_*`，跑完自动清掉），不用系统 / 会话临时目录。
- Windows 下超过 260 个字符的路径 Python 打不开：会话临时目录（scratchpad）就是这种长路径，脚本要读的副本、临时文件都别放那里（放本期 `制作/build/` 或视频旁边）。
- `python D:/大疆/AI科普/素材/角色/动作生成器/make_sprites.py [--out <预览目录>]` — 山田凉的新动作帧（先问用户；先出到预览目录给用户看，确认后才追加进 动作帧/；只追加，不改已有帧和原始素材包）。鲸鱼娘的帧在她的素材包 `素材/角色/大肥鱼像素素材包/` 里生成（见它的 README）。

## 台本里的动作写法（画面说明里）

写法：`【动作：词】` 用默认位置；`@末尾` 放到段尾；`@短语` 从这句里那个短语开始（`【动作：数一@第一】`）；`@整段` 覆盖整段（看右边）；`+` 一个身体动作加一个表情（`【动作：摇头+认真】`，算 1 个）；`【动作：说话】` 不产生动作。完整词表、上限：`references/pipeline-contract.md` §4；怎么选：`references/visuals.md`「角色动作」。

| 类 | 词（别名）· 默认时长 · 位置 |
|---|---|
| 讲解 | 抬手（介绍、请看）1.2 s · 指这里（指着、指向、看这里）1.4 s · 看右边（看右侧、看内容）1.2 s，可 `@整段` · 手放胸前（胸前）1.5 s · 合手（双手合握）整段 ≤ 6 s · 叉腰（就是这样）1.6 s · 侧耳（听说、有人说）1.6 s；以上都在段首 |
| 列举 | 数一 / 数二 / 数三（第一 / 第二 / 第三）1.6 s，常写 `@第一`，按顺序成组 ≤ 2 组 · 重点（注意）1.5 s 段首，≤ 4 |
| 语气 | 点头（嗯嗯）0.5 s 段尾，≤ 6 · 摇头（不对）0.6 s 段首，≤ 6 · 思考（想一想、托腮）2.0 s 段首，≤ 3 · 摊手 1.5 s 段尾，≤ 3 · 竖拇指（拇指）1.4 s 段尾，≤ 2 |
| 表情 | 吃惊 1.2 s 段首 · 认真 整段 · 开心 整段（叠在口型上） |
| 贴纸 | 疑问 · 收到 · 好耶（拉炮，1–2 次、至少 1 次，常写 `@末尾`）各 1.5 s，不对口型；合计 ≤ 4、每章 ≤ 1、相邻两段不能都是贴纸 |
| 其他 | 挥手（招手）1.6 s，开场 / 结尾各 ≤ 1 · 小跳 1.48 s 只放 gap，≤ 1 · 走动 1.2 s 只用于开场走入 · 不动（这一段不加自动动作） |

第 2 期档位（`epcommon.ACTION_LIMITS`）：台本动作 20–30 个、一段最多 1 个、大动作（挥手、数一/二/三、重点、思考、摊手、疑问、收到、好耶、小跳）≤ 12 且间隔 ≥ 15 s。说话时的小手势、句末点头、看向内容是自动层（episode.json `auto_gestures`），不用写；嫌多先调 `{"gesture": 0.6}`。

## 改了什么要重跑什么

| 改动 | 重跑 |
|---|---|
| 台词文字（自己录音的期） | 2 → 3 `--force` → 4（新录音稿）→ 改了的句子补录（4′ `--segment`，每句一个文件）或整期重录（4′ → 5）→ 6 → 7 → 8 → 12 |
| 只改 TTS 文本（自己录音的期） | 2 → 7 → 12（人读的是字幕原文，录音不用动） |
| 用户补录了几句 / 整期重录了 | 4′ → （整期重录才要 5）→ 6 → 7 → 8 → 12 |
| 台词文字 / TTS 文本（AI 配音的期） | 2 → 3 → 重新配音 4″–6 → 7 → 8 → 12 |
| 只改画面说明（含动作） | 2 → 7 → 12（build_timeline 会说 mouth 和混音是否仍有效，无效就先 8） |
| episode.json 的章节名、背景、terms、auto_gestures | 7 → 12 |
| episode.json 的 canvas（画面尺寸） | 7（口型、混音不变）→ 9 → 11 → 10 看版面 → 12（不能 `--skip-main`） |
| episode.json 的 bg_color（背景色）/ layout（居中版面） | 7 → 9 → 11 → 10 看版面（scenes.js 里写死的浅色字、x 坐标要自己改）→ 12（不能 `--skip-main`） |
| episode.json 的 style（白板版）/ board_lead | 7 → 9（生成 handdata.js）→ 11（多查 hand-late / hand-short / hand-slow / hand-missing / 手写字压字幕）→ 10 看版面 → 12（不能 `--skip-main`） |
| 白板版 scenes.js 里加了新的手写字 | 9（重新收字进 handdata.js）→ 11 → 10 → 12（assemble 自己也会跑 9，只是自查前要先跑） |
| 换讲解员（episode.json 的 presenter） | 改开场 / 结尾自称 → 2 → 3 → 配音（自己录音：自称那几句补录 4′ `--segment` → 6；AI 配音：用新音色重新配音 4″–6）→ 7 → 8 → 12 → 13 |
| 只改 presenter.frames（例如讲解员的帧画完了） | 12（assemble 会先跑 sync_assets）→ 13 |
| 讲解员的帧还没画完，先出草稿 | 9 加 `--frames <已有的帧目录> --allow-missing` → 12 加 `--no-sync` |
| 技能的引擎模板更新了 | 1′ → 7 → 8 → 9 → 11 → 12 |
| episode.json 的 questions（打勾时刻变了） | 7 → 8 → 12 |
| 只改 scenes.js | 10 / 11 自查 → 12（不能加 `--skip-main`）；白板版在 scenes.js 里写了新的手写字，先跑 9（sync_assets 重新收字进 handdata.js），不然 check_layout 报 hand-missing |
| 只改片尾清单 / BGM 音量 | 12 `--skip-main`（BGM 音量先 8） |
