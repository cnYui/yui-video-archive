# 流水线接口约定（引擎模板与脚本共同遵守）

所有路径以 **SERIES = `D:\大疆\AI科普`** 为根（脚本都接受 `--series` 覆盖）。技能目录：`SERIES\skill\yuanlai-ruci-episode\`（下称 SKILL）。

## 1. 目录

```text
SERIES\
  skill\yuanlai-ruci-episode\      本技能（SKILL.md、references\、scripts\、assets\engine-template\）
  片头片尾\                          intro\index.html、outro\index.html、render.py（片头 3.8 s、片尾 4.8 s）
  素材\
    字体\fonts.css + OFL 字体
    角色\山田凉像素素材包\            山田凉原始素材包（只读）
    角色\动作帧\anims.json + 帧目录   山田凉（预设 ryo）引擎用的角色帧（64×64，最近邻放大）+ 动作注册表（anims.json 顶层 actions）
    角色\动作生成器\make_sprites.py   在山田凉素材包副本上拼新动作，输出到 动作帧\（样片阶段 --out 到预览目录）
    角色\大肥鱼像素素材包\            鲸鱼娘（预设 whale；DeepSeek 拟人，素材包叫大肥鱼）：素材\ 是待机 / 口型 / 表情，
      素材\动作帧\anims.json + 帧目录   引擎用的全套帧（key 名、anims.json 格式和 角色\动作帧\ 相同）
    背景图库\*.jpg|webp               用户提供的背景图
    音频\bgm.wav、sfx_pop.wav、sfx_tick.wav
  第NN期_<题目>\                      每一期（由 scripts\new_episode.py 创建）
    episode.json
    台本\script_data.py → 台本.md、配音分段.json
    配音\chunks.json（API 配音：整期一批 C01）、raw\（C01_v1.mp3…、api_takes.json、api_usage.jsonl）、selection.json、segments\<段号>.wav
    制作\engine\（index.html、core.js、style.css、components.js、sync_assets.py 来自模板；scenes.js 每期新写）
    制作\timeline.json、voice\durations.json、voice\alignment.json、build\
    封面\
    第NN期_<题目>_成片.mp4 / _字幕.srt / _章节.txt
```

引擎在 `制作\engine\index.html`，所以到 SERIES 的相对路径固定是 `../../../`（素材：`../../../素材/...`）。

## 2. episode.json

```json
{
  "number": 2,
  "title": "Token 是什么",
  "dir_name": "第02期_Token是什么",
  "presenter": {
    "id": "whale",
    "name": "鲸鱼娘",
    "frames": "角色/大肥鱼像素素材包/素材/动作帧",
    "voice_page": "https://fish.audio/zh-CN/m/e7219cb8cfab46bebba2ee570932b0a6/",
    "voice_app": "https://fish.audio/app/text-to-speech/?modelId=e7219cb8cfab46bebba2ee570932b0a6",
    "voice_name": "苏晓晓"
  },
  "canvas": [2340, 1080],
  "bg_color": "#FFFFFF",
  "layout": "center",
  "style": "board",
  "voice_source": "user",
  "target_minutes": [5, 7],
  "question_scene": "S02",
  "questions": [
    {"text": "Token 是什么", "scenes": ["S03"]},
    {"text": "为什么按 Token 收钱", "scenes": ["S04"]},
    {"text": "一句话花了多少钱", "scenes": ["S05", "S07"]}
  ],
  "chapters": {"S01": "开场", "S02": "三个疑问", "S03": "Token 是什么"},
  "backgrounds": {"S01": "01_放学路上_树影.jpg", "S02": "02_斑马线_夕阳.jpg"},
  "bg_alpha": 0.22,
  "bg_blur": 10,
  "intro_tagline": "",
  "outro_items": [{"label": "配音", "value": "Fish Audio"}],
  "outro_closing": "感谢大家看到最后",
  "auto_gestures": true
}
```

- `presenter`：本期讲解员。`new_episode.py --presenter ryo|whale` 把 `scripts/epcommon.py` `PRESENTERS` 里的一项整段写进来：
  - `id`：预设名；`name`：开场自称（`build_script.py` 查“大家好，我是{name}”，并提醒台词里别的讲解员的“我是……”）；
  - `frames`：角色帧目录，相对 `SERIES\素材\`（`sync_assets.py`、`make_cover.py`、`build_script.py` 的帧检查都读它，不再写死 `角色\动作帧`）；
  - `voice_id`：Fish Audio 音色模型 id（API 的 `reference_id`，`tts_api.py` 用它生成；老目录没写时从 `voice_app` / `voice_page` 网址里取）；`voice_page` / `voice_app` / `voice_name`：音色页、网页版生成器（试听示例用）、音色名（`chunk_voice.py` 打印，`台本.md` 写明）。
  - 没有这个字段 = `ryo`（第 1 期）。也可以只写 id（`"presenter": "whale"`），缺的字段按预设补；写了的字段优先。帧没画完、只出草稿时不用改这里：`sync_assets.py --frames <目录> --allow-missing` 临时换帧目录（帧目录不存在时 sync_assets 直接报错，不画占位小人）。可选 `cover`：覆盖封面模板参数（在预设的 `cover` 之上、`封面\cover.json` 之下）。

  | id | name | frames | voice_name |
  |---|---|---|---|
  | `ryo` | 山田凉 | `角色/动作帧` | 山田凉（`…/m/82a7576ebd634931b2926b64fc8e23ac/`） |
  | `whale` | 鲸鱼娘（DeepSeek 拟人，素材包叫大肥鱼） | `角色/大肥鱼像素素材包/素材/动作帧` | 苏晓晓（`…/m/e7219cb8cfab46bebba2ee570932b0a6/`） |
- `canvas`：视频画面尺寸 `[宽, 高]`（用户 2026-09-27：之后的视频都做 19.5:9 → `[2340, 1080]`，`new_episode.py` 默认写这个，`--canvas WxH` 可改）。**没有这一项 = `[1920, 1080]`**（第 1 期、老目录、《AI每日日报》调用 build_timeline 的方式都照旧）。高度只能是 1080，宽度是 ≥1920 的偶数（`epcommon.canvas_of` 检查，不合格 build_timeline 直接停）。`build_timeline.py` 把它抄进 `timeline.episode.canvas`，之后引擎、`render.py`、`render_parallel.py`、`check_layout.py`、`assemble.py`（含片头片尾）都按时间轴里的这个尺寸出图；改了要重跑 build_timeline（口型和混音不受影响）。封面不跟它走：`make_cover.py` 永远出 16:9 1920×1080 + 4:3 1440×1080。
- `bg_color`：视频背景色 `"#RRGGBB"`（2026-09-28 用户：“白底做成引擎开关，以后默认白底”；`new_episode.py` 默认写 `"#FFFFFF"`，`--bg-color none` 不写）。有它 = 纯色背景：`#bg` 层整层涂这个颜色，不画章节背景图、没有暗角（`backgrounds`、`bg_alpha`、`bg_blur` 在视频里不起作用），开头 0.8 s 从深藏青淡入照旧。颜色够浅（相对亮度 > 0.4，白色就是）时引擎换**浅色主题**（§7）。**没有这一项 = 深藏青 + 按章节切换的淡背景图**（第 1、2 期；第 3、4 期是开关出现前在各自 scenes.js 里做的白底）。写法不对（不是 #RRGGBB）按没写处理，sync_assets 提醒。封面不跟它走（`封面\cover.json`，见 cover.md）。改了要重跑 build_timeline。
- `layout`：`"center"` = 内容以画面中线居中（舞台 x 960 = 画布中线，和字幕同一条线；2026-09-28 起新一期默认，`--layout old` 不写）。组件不写 x 时按 `ENG.CX` 居中，章节标题收起后停在顶部正中；右上目录、左下讲解员、字幕、进度条不动。**没有这一项 = 旧版面**（内容区 x 440–1860，组件默认中线 1150，章节标题收到左上 x 440；第 1–4 期）。只认 `"center"`，别的值按没写处理。改了要重跑 build_timeline，scenes.js 里写死的 x 要自己改。
- `style`：`"board"` = 白板手写版（2026-09-28 用户：“原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大”；`new_episode.py` 默认写，`--style cards` 不写）。标题、要点、结论边说边手写（hand.js / board.js），画面比声音早 `board_lead` 秒（默认 1.0），字幕 56 px 墨黑字白边，右上目录白卡片，没写 `bg_color` 也是白底。`sync_assets.py` 另生成 `handdata.js`（本期可能手写的字的笔画）。**没有这一项 = 印刷体卡片版**（第 1–4 期，逐像素不变）。细节见 visuals.md「白板版」。改了要重跑 build_timeline 和 sync_assets。
- `board_lead`（可选）：白板版画面比声音早几秒，默认 1.0；0 = 不提前。
- `voice_source`：`"user"` = 用户自己配音（新增的文件：`配音\录音稿.md` / `录音稿.txt`、`配音\raw\C01_vN.wav`（+ 同名 `.json` 记导入来源）、`配音\raw\pickups\<段号>_vN.wav`（补录）、`配音\raw\asr_words.json`（识别缓存）、`配音\segments\report.json` / `report.txt`）（2026-09-28 用户：“原LAI如此配音之后需要我来配音，ai配音用来做每日日报”；`new_episode.py` 默认写，`--voice tts` 写 `"tts"`）。录音稿、导入、切句见 voice.md。没有这一项 = Fish Audio 合成（第 1–4 期；《AI每日日报》调用这些脚本时也是这样）。
- `questions`：右上角「本期目录」的条目；`scenes` 是讲这一题的章节。讲到不属于任何一题的章节时所有条目不高亮；一题的最后一个章节结束时打勾。
- `backgrounds`：每个章节一张（`素材\背景图库\` 里的文件名），进入新章节时交叉淡化切换。没写的章节按背景图库顺序轮换。有 `bg_color` 时视频不用它（可以空着）。
- `outro_items`：**必须问用户**，不许用默认值。
- `auto_gestures`：角色自动层（§4）。`true`（`new_episode.py` 的默认）开，`false` 关；也可以写成对象分通道调：`{"gesture": 0.6}`（手势密度倍率，默认 1.0）、`{"nod": false}`、`{"look": false}`、`{"weight": true}`（换脚，帧做好前不要开）。改了要重跑 build_timeline（它把 episode 抄进 timeline）。
- `sprites_extra`（可选）：新动作帧还在预览目录、没追加进本期讲解员的帧目录时出样片用，例如 `"_skilltest/actions_v2/frames_preview"`（相对 SERIES，山田凉的预览帧）。`sync_assets.py` 把它叠加在讲解员帧目录上（必须是同一个讲解员的帧）；用户确认、帧追加进帧目录以后删掉这一项。

## 3. 台本数据 `台本\script_data.py`

```python
SCENES = [
    dict(id="S01", title="开场白", char="从左侧走入", rows=[
        ("gap", 1.2, "【动作：走动】背景淡入"),
        ("say", "大家好，我是山田凉。今天给大家介绍 API。", "大家好，我是山田凉。今天给大家介绍 A P I。", "画面说明……"),
    ]),
    ...
]
```

- `("say", 字幕原文, TTS 文本, 画面说明)`；`("gap", 秒, 画面说明)`。
- 开场白里的名字是本期讲解员（`presenter.name`），上例是山田凉那期的写法。
- 段号按全片顺序生成：`S03-12`（场景号-全片序号两位）。
- 动作写在画面说明里：`【动作：抬手】`，写法和词表见 §4。

## 4. 角色动作（动作 v2：自动层 + 台本动作词表）

两层，都由 `core.js` 播放：

- **自动层**（台本不用写）：说话时的小手势（手放胸前、合手、轻摊；卡片出现时朝内容轻摊并看右）、句末点头（头低 1 px、半闭眼）、看向内容。由 `timeline.json` 的 `episode.auto_gestures` 控制（§2）。完全确定性（种子 = 期号 + 段号 / 提示点序号，不用随机数和时间），碰到台本动作自动让开，同一套手臂帧最多连续 2 次。内容提示点由 components 在卡片、列表条目、代码卡、节点、表格行、步骤、示意界面出现时自动登记，scenes.js 里手搭的内容用 `c.cue(t)` 补。规则全文：`_skilltest/actions_v2/SPEC.md`「最终定稿」F.3；`core.js` 的 `planAuto()` 和参考实现 `planner_final.py` 逐条一致。
- **台本动作**：画面说明里写 `【动作：词】`。`@末尾` 放到段尾；`@短语` 从这句里说到该短语时开始（`【动作：数一@第一】`）；`@整段` 覆盖整段（看右边）；`+` 同时写一个身体动作和一个表情（`【动作：摇头+认真】`，算 1 个）。没写 `@` 就用下表的默认位置。

| 台本写法 | 别名 | type / name | 对口型 | 默认时长 · 位置 | 全片上限 | 用在什么台词 |
|---|---|---|---|---|---|---|
| 抬手 | 介绍、请看 | body `reach`（过渡 palm 80 ms，自带看右） | ✓ | 1.2 s · 段首 | — | 指向右侧内容、列要点、“请看这张图” |
| 指这里 | 指着、指向、看这里 | body `point`（斜指右上；过渡 palm；自带看右） | ✓ | 1.4 s · 段首 | — | “看这一行”“这个字段就是 model” |
| 看右边 | 看右侧、看内容 | expr `look_r`（只换眼睛） | ✓ | 1.2 s · 段首；可 `@整段` | — | “我们看右边这张表” |
| 数一 / 数二 / 数三 | 第一 / 第二 / 第三 | body `count1/2/3` + 数字徽章（过渡 reach） | ✓ | 1.6 s · 常写 `@第一` | ≤ 2 组，按顺序 | 台词真的在列举“第一……第二……” |
| 重点 | 注意 | body `finger_up`（竖食指）+「！」 | ✓ | 1.5 s · 段首 | ≤ 4 | “关键是……”“记住这一点”；“一定要”写 `重点+认真` |
| 思考 | 想一想、托腮 | body `think`（托腮，自带看右上）+ 思考泡 | ✓ | 2.0 s · 段首 | ≤ 3 | 边说边抛问题：“为什么会这样？” |
| 摊手 | — | body `shrug` | ✓ | 1.5 s · 段尾 | ≤ 3 | “就这么简单”“看情况” |
| 竖拇指 | 拇指 | body `thumb`（胸前）+ 一颗静止闪光 | ✓ | 1.4 s · 段尾 | ≤ 2 | “这样就可以了”“推荐这么做” |
| 手放胸前 | 胸前 | body `chest`（过渡 chest_mid 90 ms） | ✓ | 1.5 s · 段首 | — | “我”“我们”“自己” |
| 合手 | 双手合握 | body `hold`（过渡 chest_mid） | ✓ | 整段（最长 6 s） | — | 平静说明、承上启下“接下来我们看……” |
| 点头 | 嗯嗯 | head `nod2`（头 +1 并半闭眼，点两下） | ✓ | 0.5 s · 段尾 | ≤ 6 | “对”“没错”“就是这样” |
| 摇头 | 不对 | head `shake`（头 −1 / +1 / −1 px） | ✓ | 0.6 s · 段首 | ≤ 6 | “不是”“别这么做”；常写 `摇头+认真` |
| 挥手 | 招手 | body `wave`（两帧每 280 ms 交替；过渡 reach） | ✓ | 1.6 s · 段首 | ≤ 2 | 开场问好、结尾道谢（第一场 / 最后一场，走入之后） |
| 叉腰 | 就是这样 | body `hip`（画面右侧那只手叉腰） | ✓ | 1.6 s · 段首（也常 `@末尾`） | ≤ 3 | 下结论：“答案就是它” |
| 侧耳 | 听说、有人说 | body `ear`（手拢在耳边，过渡 reach；自带看右）+ 声波 | ✓ | 1.6 s · 段首 | ≤ 3 | “常有人说……”“你可能会问……” |
| 吃惊 | — | expr `surprised` | ✓ | 1.2 s · 段首 | — | 反常识的事实 |
| 认真 | — | expr `determined` | ✓ | 整段 | — | 警告、注意事项 |
| 开心 | — | expr `happy` | ✓ | 整段 | — | 讲完一题、操作成功 |
| 疑问 | — | pose `huh`（贴纸） | — | 1.5 s · 段首 | 贴纸合计 ≤ 4 | 停顿里抛出疑问 |
| 收到 | — | pose `roger`（贴纸） | — | 1.5 s · 段首 | 同上 | “记住了”“明白” |
| 好耶 | — | pose `yay`（贴纸，**带拉炮，用户要求保留**） | — | 1.5 s · 常写 `@末尾` | 1–2（至少 1） | 讲完一题、总结 |
| 小跳 | — | anim `hop` | — | 1.48 s · 只放 gap | ≤ 1 | 章节结尾或总结的停顿 |
| 走动 | — | anim `walk` | — | 1.2 s | 只有开场走入 1 次 | 开场第 0 秒的 gap = 从左侧走入 |
| 不动 | — | auto `off`（控制词） | — | 整段 | — | 这一段不放任何自动动作（安全警告的主句等） |

- 9 个老词（抬手、吃惊、认真、开心、疑问、收到、好耶、小跳、走动）+ 14 个新动作（指这里、看右边、数一/二/三、重点、思考、摊手、竖拇指、手放胸前、合手、点头、摇头、挥手、叉腰、侧耳）= 23 个（侧耳的原型通过了，没有换成鼓掌）；「不动」是控制词，不算动作。
- 不做：握拳、让位 / 归位、打叉、捂嘴吃惊、指向上方、双手展开介绍，以及和知识无关的角色梗。
- 用量（第 2 期档位，写在 `epcommon.ACTION_LIMITS`；`build_script.py` 按估算时长查，`build_timeline.py` 按实际时长再查大动作间隔）：台本动作 20–30 个（约 12–18 s 一个，超过 35 警告）；一段最多 1 个；大动作（挥手、数一/二/三、重点、思考、摊手、疑问、收到、好耶、小跳）≤ 12，相邻两个开始时间 ≥ 15 s；贴纸 ≤ 4、每章 ≤ 1、相邻两段不能都是贴纸；同一个身体动作不连续 3 段；头部动作（点头、摇头）只在手放下时播，不和手势写在同一段。
- 词表、别名、上限只在 `scripts/epcommon.py` 改（`ACTIONS`、`ALIASES`、`ACTION_LIMITS`），两位讲解员共用。`build_script.py` 还会查每个用到的词的帧：在本期讲解员的帧目录（`presenter.frames`）里 = 正常；只在 `sprites_extra` 预览目录里 = 只能出样片；哪里都没有 = `sync_assets.py` 会报缺帧（写明哪个讲解员缺哪个 key）。

时间轴里：`segments[].actions` / `gaps[].actions` = `[{"type","name","start","end"}]`（正片时间，秒）。

## 5. 角色帧 `素材\<presenter.frames>\anims.json`

每位讲解员一个帧目录（山田凉 `角色\动作帧\`，鲸鱼娘 `角色\大肥鱼像素素材包\素材\动作帧\`），key 名和 anims.json 格式都一样，下面的清单以山田凉为例。引擎至少要 `idle_m0..2`、`reach_m0..2`、`walk`（`sync_assets.py` 的必需项），其余缺了就退回待机。

v1（第 1 期就有，20 条，只追加不改）：`idle_m0/m1/m2`、`reach_m0/m1/m2`（12 帧呼吸，嘴型 0/1/2）、`walk`（8 帧）、`idle_surprised|determined|happy_m0..2`（只换眼睛和嘴）、`pose_huh|roger|yay`（贴纸，12 帧，跟 idle 同一个呼吸时钟）、`hop`（7 帧）。

动作 v2（命名固定，见 SPEC F.4 / F.7；帧先出到预览目录 `_skilltest/actions_v2/frames_preview/`，用户确认后才追加进 `动作帧\`）：

| key | 含义 |
|---|---|
| `<body>_m0..2` | 身体帧，12 帧呼吸表 × 嘴型：chest、chest_mid、palm、hold、point、wave_a、wave_b、count1..3、thumb、shrug、think、hip（可选 hip_mid 过渡）、ear |
| `idle_<eyes>_m0..2` | 只有眼睛窗口不同，给引擎当「眼睛补丁」：look_r、look_ur、half |
| `head_<v>_m0..2` | 头部组整体偏移的呼吸帧，条目带 `"head": [dx, dy]`：nod [0,1]、l [−1,0]、r [1,0] |
| `legs_turnout` | 1 帧，只贴 `patch_rects.legs`（换脚，P2） |
| `fx_<名>` | 64×64 透明特效层：digit1..3、exclaim、think（3 帧，播完停在最后一帧）、glint、listen |

- 顶层追加（不动已有条目）：`"version": 2`、`"patch_rects": {"eyes": [21,20,43,29], "legs": [32,58,45,63]}`（PIL 盒子，右下不含）、`"actions"`（动作注册表：body 的 `frames`（列表 = 按 `phase_ms` 交替）、`via` / `via_ms`（两端过渡帧）、`look`（自带视线）、`fx`；head 的 `steps`、`eyes`）。注册表里没有的名字按 `{"frames": 名字}` 播；`core.js` 内置同样的默认表（`ACTION_DEFAULTS`），anims.json 里的同名条目覆盖它。
- 所有呼吸帧共用一个时钟（t × 1000 ms），换姿势时头不跳。过渡帧、分相、视线、特效由注册表决定，缺哪一层就不画那一层（控制台 warn 一次，不报错）；动作本身的帧缺了就退回待机，`sync_assets.py` 会先报出来。
- 合成顺序：身体帧（或头部变体）→ 眼睛补丁（替换 x21..42、y20..28，头部动作时跟着偏移）→ 腿补丁 → 特效层。角色永远不镜像。
- 预览目录要有自己的 `anims.json`；`sync_assets.py --sprites-extra <目录>`（或 episode.json 的 `sprites_extra`）把它叠加在讲解员帧目录上（同名条目覆盖，新条目追加，注册表和几何合并）。

**角色几何（每位讲解员自己的 anims.json 顶层，都可选；缺了用山田凉的值，所以第 1 期画面不变）**：`core.js` 按这些画这位讲解员。

| 键 | 山田凉默认 | 含义 |
|---|---|---|
| `frame_w` / `frame_h` | 64 / 64 | 画布大小 |
| `anchor` | `{"foot_y": 62, "center_x": 31.5}` | 鞋底行、水平中心；角色按它对准屏幕上的同一点 |
| `patch_rects` | `eyes [21,20,43,29]`、`legs [32,58,45,63]`、`head [0,0,64,36]` | 眼睛补丁、腿补丁、旧版（第 1 期）表情盖在身体帧上的行。`sync_assets.py` 会查：表情 / 视线帧和 `idle_m0` 的差别超出 `eyes` 就警告（鲸鱼娘的表情在 x21..42、y22..31，比默认低，要写自己的，例如 `[21,21,43,32]`；手势帧的手别伸进这个框） |
| `stage` | `{"scale": 5, "foot": [210, 1000], "walk_in": -400, "walk_ease": 1.25, "walk_drift": 30, "shadow": {"w": 200, "h": 18, "dy": -10}}` | 放大倍数；`anchor` 落在屏幕哪一点（默认画布 x 50、y 685、320×320）；开场走入的起点（px）和缓动；「走动」的左右漂移；脚下投影（`null` = 不要） |
| `head_offsets` | `head_nod [0,1]`、`head_nod2 [0,2]`、`head_tr1 [1,0]`、`head_tr [2,0]`、`head_tl1 [-1,0]`、`head_tl [-2,0]` | 头部变体的脸偏移（条目自己有 `"head"` 时用条目的），眼睛补丁跟着移 |
| `fx_offset` | 无 | 特效层（数字、「！」、思考泡、闪光、声波）的偏移，`[dx, dy]` 或 `{"fx_digit1": [dx, dy], "*": [dx, dy]}`（精灵像素）；手的位置和山田凉不同、又借用了她的特效帧时用。只做小的挪动：移出 64×64 画布的部分会被裁掉 |

手的位置画在身体帧里、特效画在 64×64 的特效帧里，引擎没有另外的“手坐标”。

## 6. timeline.json（由 scripts\build_timeline.py 生成，不手改）

在第 1 期格式基础上：

- `episode`：episode.json 的内容（含 `auto_gestures`、`presenter`、`canvas`、`bg_color`、`layout`、`style`、`board_lead`、`voice_source`），其中 `backgrounds` 转成相对引擎目录的路径（`../../../素材/背景图库/<文件>`）。**引擎只看这里有没有 `episode` 来决定用不用动作 v2**：没有（第 1 期旧时间轴）就按 v1 播放，逐像素不变（不读注册表、没有自动层）。
- `episode.canvas`：画面尺寸（只在 episode.json 写了 `canvas` 时才有；没有 = 1920×1080）。这是出图尺寸的唯一来源：`render.py` / `render_parallel.py` / `check_layout.py` 按它开浏览器视口并注入 `window.__CANVAS__`，引擎按它排版；`assemble.py` 按它渲染片头片尾（写进 `build/intro_data.json`、`outro_data.json` 的 `canvas`），并要求 episode.json 和时间轴里的一致。
- `segments[].actions`、`gaps[].actions`：type 有 `body`（reach、point、wave、count1/2/3、finger_up、think、shrug、thumb、chest、hold、hip、ear）、`expr`（surprised、determined、happy、look_r）、`pose`（huh、roger、yay）、`anim`（hop、walk）、`head`（nod2、shake）、`fx`（可选，直接放一层特效）、`auto`（off = 不动）。和开场走入重叠的显式动作会被推到走入结束以后（build_timeline 会打印）。
- 自动层**不写进** timeline：引擎在 `buildScenes()` 之后自己算（要用 scenes.js 登记的内容提示点），结果在 `ENG.autoPlan`（`[{type: body|head|look|legs, name, start, end, src: "auto", key}]`），`check_layout.py` 会打印各通道的数量。
- `segments[].pose` 保留（有「抬手」时为 `reach`），兼容第 1 期引擎。
- `mouth`：mix_audio.py 写入的每帧口型。
- `chapters`、`scenes`、`intro`、`outro`、`main_duration`、`total_duration` 与第 1 期相同。

## 7. 引擎版面（固定）

**画布与内容舞台**：页面 = 画布 = 视频画面，`CW × CH` = `timeline.episode.canvas`（没有就是 1920×1080）。scenes.js / components.js 画在一个 **1920×1080 的内容舞台**上（`#scenes` 层），舞台在画布里**水平居中**，偏移 `OX = (CW − 1920) / 2`（2340 宽时 210：舞台在画布 x 210–2130）。所以：

- scenes.js 的坐标一律是舞台坐标，和第 1 期一样写（y 80–900），不用管画布多宽；第 1 期的 `scenes.example.js`、第 2 期的 scenes.js 不用改。水平方向：居中版面（`layout: "center"`，新一期默认）内容以舞台 x 960（`ENG.CX`，画布中线，和字幕同一条线）左右对称，自己写坐标就用 `ENG.CX - w / 2`；旧版面（没写 layout）内容区 x 440–1860（`ENG.CX` = 1150）。
- 开关（core.js 从 `timeline.episode` 读，缺了读 assets.js 的副本）：`ENG.CENTER`（居中版面）、`ENG.CX`（内容中线：960 / 1150）、`ENG.BG_COLOR`（`'#FFFFFF'` 或 null）、`ENG.BG_RGB`、`ENG.LIGHT`（浅色主题）、`ENG.BASE`（“什么都没画”的地方的底色：背景色，没有就是深藏青 #1B2340；`ENG.surfaceUnder`、`c.label` 自动配色、`check_layout.py` 的对比度都按它算）。
- `ENG.tocRect()`、`ENG.tocRowRect(i)`、`ENG.safeTop(y, right, left)` 返回 / 接受舞台坐标（2340 宽时目录在舞台 x ≈1750–2090，一部分在舞台右边以外），卡片照样用它们避开目录，疑问卡照样飞进目录。
- `ENG.CW`、`ENG.CH`（画布）、`ENG.OX`（舞台在画布里的 x）、`ENG.canvas`、`ENG.stage`；`ENG.W` / `ENG.H` 仍是舞台的 1920 / 1080。要用 `getBoundingClientRect()` 量出来的位置当舞台坐标，先减 `ENG.OX`（`c.ringOn` 已经这样做）。
- 舞台不裁切：内容可以画出舞台（例如飞进目录的疑问卡），出了画布才会被裁掉；`check_layout.py` 按画布查出界。

**全局层铺满画布**（core.js，canvas 坐标）：

- 左上：只有「原LAI如此 #NN」（NN = episode.number 两位），贴画布左边（x 40）。**没有**"配音：AI 合成"。
- 右上：本期目录（第 1 期样式：半透明深色卡片、「本期目录 CONTENTS」，进行中橙色编号 + 左侧橙竖条 + 稍放大，完成橙色 ✓ + 文字变暗 + 提示音，未开始灰色编号），贴画布右边（右边缘在 CW − 40）。在 `question_scene` 的最后一句结束时由疑问卡飞入。
- 左下：本期讲解员 ×5（位置由她 anims.json 的 `anchor` / `stage` 算，默认画布 x 50、y 685、320×320，都是画布坐标），全片固定位置，不镜像。
- 底部：字幕**按整个画布水平居中**（中心 x = CW / 2：1920 宽时 960，2340 宽时 1170），在章节进度条上方；单行最宽 1240（舞台 x 340–1580，和 1920 时一样）。
- 最底：《孤独摇滚！》四色章节进度条（整片时间，含片头片尾），全宽 CW。
- 背景：有 `bg_color`（新一期默认 #FFFFFF）时 `#bg` 层整层涂这个颜色，不画图、没有暗角，开头 0.8 s 从深藏青淡入（片头收尾是墨黑，接得上）；没有时按章节切换（0.8 s 交叉淡化），cover 铺满整个画布，叠在深藏青 #1B2340 上，不透明度 `bg_alpha`（默认 0.22）、模糊 `bg_blur`（默认 10 px）、暗角 15%（按画布中心）。片尾前的淡出也是整个画布。
- 白板版的章与章之间（core.js `boardPlan`）：每场分内容层（`S.root`）和标题层（`S.head`，board.js 的 `c.title` 画在这里）；标题在场景时刻 E − 0.36 擦（画面上早 LEAD 秒），内容留到最后一句说完 + 0.15 s（画面时刻，夹在 E − LEAD − 0.36 和 E − 0.36 之间）再淡出 0.3 s；下一场的内容层等上一场内容擦完再淡入；最后一场不自己淡出。疑问场 `ENG.tocInTime()` = 最后一句结束前 0.1 s（卡片版 0.75 s）。
- 白板版（`style: "board"`；`body.board`，board.css）：白底；字幕 56 px 墨黑字白边（`#subs` 从 y 918 起，单行最宽 1500 px，`ENG.SUB`）；右上目录白卡片、行字墨黑；进度条上方白色渐变。场景层时钟比声音早 `ENG.LEAD` 秒（默认 1）：`renderAt(t)` 用 t + LEAD 求场景（最后一个场景停在淡出前，等声音到了再淡出），字幕、口型、进度条、目录高亮和打勾、片尾淡出用 t；目录在 `ENG.tocInTime() + 0.35 − LEAD` 出现。手写层见 visuals.md「白板版」。
- 浅色主题（`bg_color` 够浅；`body.light`，style.css 末尾一节）：徽标、章节标题（`.hdr`）、`.note`、进度条章节名、`.chip.line`、步骤条、开场大字、疑问卡标题、总结落款换深色；章节标题和开场大字后面的深色光晕、进度条上方的深色渐变（`#barShade`）去掉；卡片 / chip 阴影减轻、加一圈细边；右上目录保留深色底板（加深到 .9）；字幕不变（纸白字墨黑描边）。scenes.js 里自己写的浅色字（`color: 'var(--paper)'`、浅色 rgba）要自己按 `ENG.LIGHT` 换。
- 片头片尾（`SERIES\片头片尾\intro|outro\index.html`）读 data 的 `canvas`（或 `window.__CANVAS__`）：1920 时和原来逐像素一样；更宽时构图居中，纸色 / 墨色底、纹理、四角裁切标（画面 5% 安全区）、片头收尾的整屏墨黑铺满全宽。
