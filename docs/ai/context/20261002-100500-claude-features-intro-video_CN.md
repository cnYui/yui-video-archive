# 《Claude mod(模组)发布》制作记录（2026-10-02；已发布 BV1Zoa16CEeU；目录已移到 `Claude Code相关/01_Claude Code模组发布/`）

**标题的演变**：我拟的草稿是“Claude Code 能装模组了！官方这几天发的新东西，一个视频讲完”；成片交付后用户先给整句“标题为：Claude mod(模组)发布！现在你可以修改Claude Code成自己喜欢的样子”（半角括号、全角感叹号）；看了封面后又拆开：**封面上写“Claude mod(模组)发布”，标题用“现在你可以修改Claude Code成自己喜欢的样子”，两处内容不重复**。现用标题已写进 `投稿信息.json`（`make_submission.py` 的 `TITLE`，封面字在 `COVER_TEXT`）、`台本/build_script.py`、`制作/00_整片/build_timeline.py`（画面不显示标题，只是字段）。目录名 `2026-10_Claude最新功能介绍` 还是草稿的叫法，没改。

**发布后更新（2026-10-02）**：用户把成片拖进 B 站投稿页，我用插件填了封面（两个比例）、标题、10 个标签、简介（1695 字）、创作声明、分区，用户在页面里把标题改成“现在你可以让Claude修改自己！Claude新功能：Claude mod”，选了新建的合集「Claude Code相关」后自己点了投稿：**BV1Zoa16CEeU，2026-10-02 10:44 北京时间发布**，254 s，线上封面和本地 `封面_选定_*` 平均像素差 < 1。随后用户新开了合集「Claude Code相关」，本期整个目录移到 `Claude Code相关/01_Claude Code模组发布/`（下文写 `独立视频/2026-10_Claude最新功能介绍/` 的路径都读成这个新路径）；建合集、封面技能、流程复盘见 `20261002-140000-claude-code-series-cover-skill-retro_CN.md` 和 `Claude Code相关/流程复盘.md`。

目录（发布时的位置）：`独立视频/2026-10_Claude最新功能介绍/`（素材 / 台本 / 制作）。成片 `Claude新功能介绍_成片.mp4`（253.75 s = 片头 3.8 + 正片 245.13 + 片尾 4.8，2340×1080、30 fps、−16.0 LUFS、峰值 −1.6 dBFS，52.9 MB）、`Claude新功能介绍_手机预览.mp4`（1560×720，9.7 MB）。版式、流水线照白宫那条（`20261001-181500-white-house-si-accord-video-production_CN.md`）改的；同一天另外两个会话在做 `独立视频/2026-10_ClaudeFable5.5模型介绍/`（记录 `20261002-092500-fable55-intro-video_CN.md`）和 `独立视频/2026-10_OpenAI-DevDay-2026解读/`，三条互不相干，只共用 Fish 页面和渲染时段（见「和别的会话协调」）。

## 用户的要求（原话）

- 起因：“https://x.com/ClaudeDevs/status/2105391694741119047 …/2105721436270993609 …/2105721434807083061 用浏览器插件使用这个网页：https://twittersaver.net/zh-cn，下载这些视频，然后看这里 https://x.com/ClaudeDevs，做一个claude最新的功能的介绍篇，用曼波的配音”
- 中途三条（都在我做的过程中发来，已存进记忆）：
  1. “你可以新建一个空白的fishapi页面来做tts”——以后要（重新）生成配音，新开空白 Fish 页面做，不在共享编辑框里换稿（这一轮配音已经生成完、编辑框已按原样还原，没用上）。
  2. “视频里多出现你下载的视频演示片段，而不是你一味的在说讲解，大家喜欢看视频，不喜欢看你讲解”——**我第一版把大半时间做成了文字卡片（演示视频只占约 36%），看完静帧后用户说的**；于是整个画面表重排：演示视频 107.3 s（44%）+ 官方页面录屏 137.3 s（56%），**没有静态文字卡片**。第一版只渲了静帧，没出过 mp4。
  3. “目录缩短，压缩为三个”——左栏目录从 5 条压到 3 条：模组是什么 / 示例和注意事项 / 顺带三件事（目录框随条目数缩短、垂直居中）。

## 下载（TwitterSaver，Chrome 插件）

三条都是 @ClaudeDevs 发的，取最高清晰度 1080p，放在 `素材/X平台视频_ClaudeDevs/`（整个 `素材/` 不进 git），来源和规格写在同目录 `来源.md`：

| 文件 | 内容 | 规格 |
|---|---|---|
| `ClaudeDevs_2105391694741119047.mp4` | 10-01 发的 claude.dev 新主页；视频是站里的像素小游戏 | 30.05 s，60 fps，有声（不用原声） |
| `ClaudeDevs_2105721434807083061.mp4` | 10-02 的“You can now mod Claude Code”主帖；视频是 Token Weather → Blast Radius → Replay Theater 三个官方示例的连播，底部带英文说明条 | 71.77 s，30 fps，无声 |
| `ClaudeDevs_2105721436270993609.mp4` | 同一串里的回复：Token Weather 在深色终端里的真实演示（18% → 67% → 81%） | 23.77 s，30 fps，无声 |

做法（照 `20261002-090113-x-videos-chetaslua-download_CN.md`）：插件打开 TwitterSaver，`javascript_tool` 用原生 value setter 给输入框填链接、按文字“下载”点按钮（不用鼠标点输入框：点击劫持广告）；结果页 `read_page`（interactive）读出 `dl.snapcdn.app/get?token=…`；**下载前把 JWT 解开，断言源站是 `video.twimg.com`**，再 `curl.exe -L -A <UA> -e https://twittersaver.net/` 下到磁盘，ffprobe 核对。主帖下面还有 Blast Radius、Replay Theater 各自的单独视频，用户没列进清单，没下（连播里都有）；没有再下别的视频。

## 看 @ClaudeDevs 主页（访客视图）

- 插件里的 Chrome 没登录 X（右侧是“登录或注册”），我没碰任何登录；访客视图的时间线只给了 6 条：10-02 的 mods 串、10-01 的 claude.dev、9-29 的 Sonnet 5.5 使用指南 / 评测文章 / Sonnet 5.5 发布转发。`get_page_text` 只会取第一条 `article`，要用脚本 `document.querySelectorAll('article')` 一条条取（访客视图里没有 `data-testid`、没有 `time`，只能按文字）。
- mods 串共 8 条：主帖 + Token Weather / Blast Radius / Replay Theater 三个示例（各带视频）+ 分享（Claude 目录）+ 示例仓库 + 官方博客 + 一条网友回复。
- 公开的 syndication 时间线接口（`syndication.twitter.com/srv/timeline-profile/…`）这台机器上只返回 2 KB 的壳，没用。

## 事实依据（全部是官方原文，2026-10-02 读的；台本里每句话都能对上）

- ClaudeDevs 帖子串；https://claude.dev/blog/getting-started-with-claude-code-mods/ （Addy Osmani，Oct 01）；https://claude.dev/mods/ 、/terminal/；https://code.claude.com/docs/en/plugins/mods/overview ；https://claude.dev/blog/building-with-claude-sonnet-5-5/ （Sep 28）；https://claude.dev/blog/automating-eval-design-and-hillclimbing/ （Sep 28）。claude.com/blog/claude-code-mods 在这个浏览器里正文渲染不出来（DOM 里没有文章文字），没读到，内容和 claude.dev 教程一致。
- 要点（也是台本的骨架）：模组 = 装在插件里的 JS/TS 小程序，能改行为 / 改界面 / 换上自己的功能；Claude Code ≥ 2.1.287、默认开着；CLI 和桌面版 Code 标签页能用，VS Code 扩展的聊天面板只跑钩子不画界面；`/plugin` 装；**不在沙盒里、权限等同 Claude Code、能读环境变量里的密钥**；`claude plugin validate` 装之前先列出 hooks / calls；/diff 和 AGENTS.md 支持本身就是内置模组；Blast Radius 官方自己说是“安全网，不是权限系统”（只看命令文字，$(…)、别名、脚本能绕过去）。
- Sonnet 5.5：5.5 家族第二个（前面是 Opus 5.5）；比 Sonnet 5 快 30% 以上、单价没变、多数任务最多便宜 30%；`/model sonnet`，Claude Code 里默认模型仍是 Opus 5.5。评测：claude-api 技能的 `/claude-api build-eval`、`/claude-api hillclimb`；客服工单示例（保留的 14 张没见过的工单上准确率 78.6% → 90.5%，成本约五分之一）。

## 台本（`台本/`）

- `build_script.py` → `录制稿_v1.json`（唯一来源）+ `录制稿_v1.md`（给人读）；`plan_v1.json` = 画面表（30 个镜头：每个镜头一个 vo 块；带 `bg` 的放官方演示视频，不带的是页面录屏；`captions` = V3 底部英文说明条的中文翻译）。
- 58 句、约 1580 个字（曼波声线约 6.3 字 / 秒）；3 章。开场一句话抛结论，三个示例各一段，安全提醒，最后“三步上手”。
- 风格按 AGENTS.md：短句口语、不用“不是……而是……”（官方那句“a safety net, not a permission system”写成“只是一道安全网，不能当权限系统用”）、不写具体日期（美国时间和北京时间差一天）、笑点打流程和命令（删库跑路、看到暴风雨别再塞大文件、像看比赛回放）。

## 画面（`制作/画面表.md` 有 30 个镜头的逐条表）

- 演示视频（44%）：开场快剪（V3 三个示例各 1.8 s）→ 今天讲的四件事（V2 + V3 快剪）→ N06 三段“改行为 / 改界面 / 加功能”→ Token Weather 真实终端演示（原速，播完定格在 Storm 81%，叠橙色框、档位图例、“≈80 行”）→ Blast Radius → Replay Theater（×1.37）→ Playground 一句话（V2 片段 + 小标签）→ claude.dev 小游戏（5 段 1.1 s 快剪，×1.10）→ 结尾两段 V2。
- 官方页面录屏（56%）：教程开头（设置、权限规则…逐词刷）、How a mod works 的代码、The shortcut 的提示词、docs 的安装 / 在哪能用 / 版本 / 内置模组表、Blast Radius 之后的“安全网”原话、What a mod can reach 列表、validate 的真实输出、Turn mods on or off、Sharing your mod 的三条命令、claude.dev 首页、Sonnet 5.5 使用指南（开头段、Choosing 段、In Claude Code 段）、评测文章（开头两条命令、Figure 8 图表）。
- 左栏目录 3 条；章节标签只在演示视频上；每个演示视频右上角“画面：ClaudeDevs · X”；页面录屏的顶栏是真实 URL。

## 官方页面录屏的做法（新写的，`制作/00_整片/capture_pages.py` + `scenes.js` 的 `pageShot`）

- Playwright（viewport 800 宽、2 倍像素 → 图宽 1600）打开官方页面，按“起点文字”把小节截成长图（`media/pages/*.png`，共 19 张），同时用 Range / 块元素算出要高亮的句子在图里的位置，存 `pages.json` / `pages.js`（`window.PG`）。
- `pageShot(从哪句, 到哪句, 页面名, [[高亮句, 时刻, 中文译文?], …], {start})`：铺满演示区宽度；浏览器顶栏（三个圆点 + URL）；每条高亮出现前 0.95 s 开始往它那里滚，滚到画面偏上三分之一；荧光笔从左刷到右，后面的出来时前面的变淡；底部一条深色中文译文条。比窗口还高的元素（图表）顶部对齐、用橙色边框而不是填色。
- 页面镜头之间快切（`ovPage`，0.1 s）：用默认 0.35 s 交叉淡化会两页文字叠在一起。
- 踩到的坑：①起点文字会命中正文里同名的引用而不是标题 → 起点写 `#标题` 只在 h1–h4 里找；②句子里夹着链接就被切成两个文字节点，单节点匹配不到 → 用句子前半段，或 `@@` 前缀（高亮包含这句话的整个段落）；③`#sel:选择器`（例：`figure.art-fig`）圈图表；④宽度 800 时文档站是手机布局，没有侧栏，字大小合适；⑤Sonnet 博客开头段下面的图是“代码画画”演示，参考照片在 X 上有社区注释说没经摄影师同意 → 截图高度按“下一个 figure 的顶部”算，不放那两张图；⑥X 的访客视图截不到回复，Playground 那句改成演示视频上的小标签。

## 配音（Fish 网页版，Chrome 插件）

- 用户的 Plus 账号，声音「赛马娘（曼波欧耶版）」modelId `561fcedfdf0e4e1399d1bc4930d50c0e`，模型 **S2 Pro**（用户上次指定，账号级设置；打开页面时下拉就是 S2 Pro）。整期一次生成（58 段，本地 1736 字、Fish 计数 4166 / 15000），出两个版本（247.2 s、242.4 s），`tts/raw/N_v1.mp3`、`N_v2.mp3`；用量记录 `制作/02_配音/web_usage.txt`。数字写汉字、斜杠命令写“斜杠 plugin”（`build_script.py` 的 `to_say`）。
- 流程：编辑框原来是日报 10/02 稿（`AI日报/2026-10-02/配音/chunks.json` 的 C01，1 段 2276 字，SHA-256 前 16 位 `f25113a45db767ac`）→ 核对一致 → 换成本期稿（58 段，`f50848b5b62ca589`）→ `find` 出“生成语音”按钮真实点击 → 约 3 分钟 → **音频直接 curl `platform.r2.fish.audio/tasks/<UTC 日期>/<任务编号>.mp3`**（同事先发现的：这次 200；日期是 UTC 日期；任务编号从 `read_network_requests`（urlPattern `api.fish.audio`）里拿，生成前先 `clear: true`）→ 把日报稿贴回并核对哈希 → 关标签。
- 识别：`asr.py`（faster-whisper large-v3-turbo，CPU，提示词放了本期专名）→ `tts_build.py`（支持 `EDIT_DIR` 环境变量，可把 v1 / v2 各拼一份对比）→ `tts_qa.py` 逐句复核。**按句挑版本**：v2 比 v1 高 0.04 以上才用 v2（17 句用 v2：N04、N05、N07、N11、N16、N17、N21、N25、N30、N33、N37、N42、N43、N52、N54、N57、N60），整期 243.2 s（`edit/choice.json`）。
- **逐句复核**：挑完之后仍有 17 句 < 0.85（N07、N10、N11、N12、N18、N19、N20、N28、N32、N34、N46、N48、N54、N55、N56、N58、N60），列在 `制作/02_配音/qa_pick.txt`（每句带 v1 / v2 分数和 whisper 听到的）。多数是曼波声线的 sh/x、q/x、d/z 音被 whisper 听成别的字（“三件事”→“三件信”、“权限”→“前线”、“八十行”→“巴西行”、“Claude”→“Cloud”、“以上”→“以下”）；同一句话在不同位置识别结果还不一样（N58 的“2.1.287以上”听成“以上”，N11 的同一句听成“以下”），所以按声线的老毛病处理。**机器没法判断的，要用户耳朵听**：尤其 N11 和 N60 的“以上 / 以下”、N12 的 AGENTS.md、N60 的 claude.dev。

## 和别的会话协调

- Fish 编辑框草稿在标签页之间共享：先用 `SendMessage` 告诉对方我要占用，对方（Fable 5.5 那条、OpenAI DevDay 那条）用完 / 我用完都互相发“完成”，各自按 C01 还原。对方还提醒：页面刚加载完第一下点“生成语音”可能没反应，点之前看按钮状态。
- 渲染：同一时间只跑一个。开渲前 `ListAgents` + 看进程；DevDay 那个会话答应我渲染期间不开新的重任务，我渲完发了“渲染完成”。Fable 5.5 的会话在 AGENTS.md 里记了“内存不够用 `RENDER_WORKERS=3`”，我这条没改 render_all.py，4 路。

## 流水线（`制作/00_整片/`，相对白宫那条新写 / 改动的地方）

- `build_timeline.py`：vo 块可带 `bg`（官方演示视频）：`parts` 多段拼接，`rate = 素材总长 / 画外音块时长`（限制 0.75–1.5；`min_rate`、`max_rate` 可单独定），素材短就在最后一帧定格（`hold_from`），长就在块尾截断；每块可设 `gap`（镜头在句中换时写 0）；`captions` 把来源视频底部英文说明条换算成成片时间；`bar` = 底部条当标题；最后一个镜头的演示视频铺到片尾（不然片尾 1.4 s 是空白）。
- `prep_frames.py`：每段 `setpts=PTS/rate` 再 `fps=30` 抽成 1636×920（`-t` 是输出时长，要除以 rate）。
- `engine.js` / `index.html`：**底部中文说明条**——V3 自带英文说明条（原图 y 931 起、色 `#FAF8F4`），用同色条盖住、换成中文，跟着变速走，右下角“示例 n / 3”；seg.bg 时只显示 clip 叠加层；页面镜头快切；`#toc` 随条目数缩短。
- `mix_audio.py`：只剩画外音（−16 LUFS）+ 系列 BGM（−16 dB）。
- `stills_at.py`：按“字幕条号 + 秒数”取静帧（`python stills_at.py N05+1.0 …`）；注意同一天连续跑两次会覆盖 `_sheet_t_1.png`。
- 版面复查发现并改掉的：开场胶囊挡住 Blast Radius 对话框 / Replay 面板标题 → 开场改成快剪 + 底部条当标题；图例和“≈80 行”叠在一起 → 图例提前收；`E('N41') + 1.0` 这种越过段落边界的结束时刻会叠上下一张；页面镜头交叉淡化重影；Sonnet 页露出有争议的图；评测图表整块填黄看不清 → 边框；结尾“≥ 2.1.287”标签压住上一个标签；片尾空白。

## 封面（`制作/04_封面/`）

**封面 C（现用；用户 2026-10-02）**：“封面太丑了，https://claude.dev/blog/getting-started-with-claude-code-mods/ 这是他们这次官方的文档，你核对一下视频的内容是否正确，然后你看看能不能使用最后底部的这个作为背景？封面中出现的内容和标题不要重复，封面出现：Claude mod(模组)发布这几个字，标题则用：现在你可以修改Claude Code成自己喜欢的样子”（附了教程页底部太空场景的截图）。我出了 3 张候选背景（`_src/scene/_cands.png`：a 宽、b 中、c 紧裁），用户回“用第三种，claude的形象大一点的”。

- **核对视频内容**：`素材/网页截图/verify_claims.py` 把视频里 37 条说法逐条对到官方教程页原文，36 条逐字对上；唯一差异是 Replay Theater 示例：教程图注写 5 处修改 / 3 个文件，官方 X 视频里是 6 处 / 4 个文件，旁白跟着官方视频讲。
- **背景**：教程页最底部 `footer .scene` = 一张 2 倍分辨率的星空 canvas（灰色点阵的月牙、土星、星点）+ `.astro-stage` 里的 DOM 像素宇航员（身体 `#D97757` = Claude 的品牌橙，头盔浅灰线，黄色小星光，会飘动）。`04_封面/capture_scene.py` 用 Playwright 深色模式、viewport 1440、设备像素比 6 截 4 帧（`_src/scene/s6_0..3.png`，8550×4056；宇航员 6 倍下依然清晰，星空是 2 倍放大的），选第 0 帧（带两个黄色小星光）。
- **合成**（`make_cover2.py`，`python make_cover2.py` 出正式图，`python make_cover2.py variants` 出对比稿到 `_src/variants/`）：①把宇航员按颜色抠成透明小图（橙 / 白 / 黄像素，向外胀 10 px 暗边，眼睛的洞用灌水补上；灰色星点亮度 ≤ 140，不会被选中）；②擦掉宇航员的星空按“第三种”（3 倍、宇航员原在画面 72% / 64%）裁出来，**只提亮灰色星点**（`BG_LIFT = 1.7`，按饱和度加权，橙色和黄色不动）；③宇航员放大到 5–6.4 倍（候选图里约 3 倍；16:9 里身体约 415 px 宽）贴回去；④叠字：Noto Sans SC 900，白色 “Claude mod” + Claude 橙 “(模组)发布”（半角括号照用户写法），字下垫一圈和底色一样的暗边（`-webkit-text-stroke` + `paint-order: stroke fill`）挤掉紧贴字边的星点。16:9 是 1920×1080，4:3 是 1440×1080；B 站首页卡片会把 16:9 裁成 16:10（左右各切约 96 px），字和宇航员都收在 96–1824 之间。
- 输出 `封面_C_16x9.png`、`封面_C_4x3.png`，`封面_选定_16x9.png` / `封面_选定_4x3.png` = C（用户还没最后确认）。旧的 A 深色 / B 米色（三个演示界面拼贴）和 `make_cover.py` 挪进了 `04_封面/_旧稿/`，没删。
- **踩到的**：①我一开始把整张背景整体提亮，宇航员的橙色变桃色、头盔线发白 → 只提亮灰色星点；②叠一层暖色光晕反而发脏，去掉；③直接按宇航员裁 5 倍以上时，一小簇三连星点正好落在第一行字尾巴上，读成省略号 → 改成把宇航员抠出来，星空另按 3 倍裁，就能单独选星空的倍数和位置；④整张 8550×4056 图转 `int64` 要 800 MB，用 `uint8` 比较；⑤宇航员头盔的“虚线”是原图像素台阶，不是抠图缺口（对比过原图和抠出的透明图）。
- 版权：背景和宇航员是官方页面的真实截图（Anthropic 的插画，没重画）；简介里写了“封面背景取自 claude.dev 官方教程页底部的太空插画，版权归 Anthropic”。

（旧稿 A / B 的做法：`_旧稿/make_cover.py`，标题字《Claude Code 能装「模组」了》+ 官方演示里三个最有辨识度的界面 `_src/br.png`、`rt.png`、`tw.png`，各出 16:9 和 4:3。）

## 渲染和检查

- 4 路渲染 7354 帧 224 s，页面 0 报错；`整片_v1.mp4` 45.4 MB。渲染时物理空闲只有约 1 GB、提交内存 69 / 73 GB（别的会话的 whisper 一直占着），没出事，但已经贴着上限。
- 成片抽样帧和静帧一致；加片头片尾（`add_to_video.py`，片头 3.8 s、片尾 4.8 s，音乐垫在画外音下面 −3 dB 相对语音）。
- 音轨检查：`qa_mix.py` 的慢速版（large-v3-turbo）CPU 被占着一分钟一句，跑了 13 句就停了（`qa_mix_report_partial_large.txt`）；改成 `QA_MODEL=small QA_BEAM=1` 的快速版只看位置对不对（`qa_mix_report.txt`）：58/58 句都跑完，**没有哪句的识别结果更像相邻句，位置都对**；small 模型分数低的几句（N20、N28、N36、N48、N56、N31、N42、N61）large 模型逐句复核时分数是正常的或本来就低，是 small 的识别误差，不是声音问题。**这条只有一条画外音声轨、按块首尾相接（`gap: 0`），不会像白宫那条那样叠声。**

## 待办 / 没做

- 用户听一遍成片的配音（重点见 `qa_pick.txt`）；定片尾清单（`制作/00_整片/outro.json` 是草稿，按规矩每期都要用户确认）；看封面 C（`制作/04_封面/封面_选定_*`）；标题已定（见上），`投稿信息.json` 已按新标题和简介重生成。
- 投稿：用户把 mp4 拖进 B 站投稿页后，我用插件填表（标签逐个 + Enter、简介用 `type` 打字、创作声明含AI生成内容、分区人工智能、不选合集）；“立即投稿”由用户点。YouTube 未定。
- 发布前重看官方页面：Claude Code 版本号（2.1.287）、Sonnet 5.5 默认模型 / 价格、“官方正往 Playground 仓库里加示例”会过期；标题 / 简介里的“这几天”按 10 月 2 日算。
- 没提交 git（用户没说）；`独立视频/` 整体还是未跟踪状态。
