# 引擎白底 / 居中开关、两档节目通用约束、402 改用网页版配音（2026-09-28）

## 用户要求

第 3 期投稿、记录写完之后（同一会话「JEV模型视频企划」）：

- “白底做成引擎开关，以后默认白底，同时你看一下当前其他的docs/ai/context中不同分集视频的相同约束，比如视频比例，背景白色，画面内容居中等等”
- 追加：“还有ai配音中，api key额度用完了用浏览器插件来实现配音”

## 结论

1. 《原LAI如此》引擎加了两个开关，写在 `episode.json`，新一期由 `new_episode.py` 默认写好：
   - `"bg_color": "#FFFFFF"`：纯色背景，视频里不用背景图；颜色够浅时自动换浅色主题。`--bg-color none` = 不写（深藏青 + 章节背景图）。
   - `"layout": "center"`：内容以画面中线（舞台 x 960 = 画布中线，和字幕同一条线）居中，章节标题收起后停在顶部正中；右上目录、左下讲解员不动。`--layout old` = 不写（旧版面，内容区 x 440–1860）。
   - 两个都不写 = 和以前完全一样（第 1、2 期新旧引擎逐像素对比一致，见「测试」）。第 3、4 期的白底是开关出现前在各自 scenes.js 里做的，它们的引擎副本不动。
   - 封面不跟 `bg_color` 走：照旧用背景图（第 3 期用户：“封面背景不要变”），纯色封面仍是 cover.json `"plain"`。
2. 两档节目的共同约束逐条核对后，写进 `AGENTS.md` 新的一节「所有视频通用的规则」（画面 2340×1080 + 封面双比例、白底、内容居中、左下讲解员 / 字幕居中 / 全宽进度条 / 右上目录、s1 整期配音和 key 规则、402 改网页版、4 路渲染、台本风格、B 站分区和创作声明）。还没统一、要问用户的三处：白板手写版“边说边画”、字比声音早 1 秒、字号。
3. API 额度用完（402）改用 Chrome 插件操作 Fish Audio 网页版（用户 Plus 账号、S1、整期一次）：《原LAI如此》上午已经改好；这次把《AI每日日报》也改了（原来是停下推送、提示换免费模型 s2.1-pro-free）。已通知日报会话，它核对过没有冲突。

## 《原LAI如此》技能的改动

改之前整份技能备份在 `AI科普/_旧稿/skill_yuanlai-ruci-episode_白底居中开关前_20260928-153924/`。

引擎模板 `assets/engine-template/`：

- `core.js`：读 `EP.bg_color`（只认 `#RRGGBB`，写错了 console.warn 并按没写处理）和 `EP.layout`；新增 `ENG.BG_COLOR`、`ENG.BG_RGB`、`ENG.LIGHT`（相对亮度 > 0.4）、`ENG.CENTER`、`ENG.CX`（960 / 1150）、`ENG.BASE`（“什么都没画”处的底色：背景色，没有就是深藏青）。纯色时 `resolveBackgrounds` 不选图、不建背景 canvas，`#bg` 层整层涂色，开头 0.8 s 从深藏青淡入照旧；`body` 加 `solid` / `light` 类。
- `components.js`：`ENG.surfaceUnder` / `resolveInk` 的底色用 `ENG.BASE`（白底上 `c.label`、`c.bracket` 自动配深色字）；居中版面下 `c.title` / `c.bigWord` 以 `ENG.CX` 居中，章节标题收起到顶部正中（返回值多了 `left`）；疑问卡、`c.statement`、`c.pointList`、`c.summary`、`c.compareTable`、`c.browser`、`c.phone` 不写 x 时以 `ENG.CX` 居中；浅色主题下不画标题 / 大字后面的深色光晕，大字、疑问卡标题、总结落款、步骤条换深色。步骤条完成后的编号原来是 `color: transparent`，改成 `visibility: hidden`（同样看不见，check_layout 不会把透明字当成低对比）。
- `style.css`：末尾加 `body.light` 一节（徽标、目录加深到 .9、去掉 `#barShade`、进度条章节名、`.hdr`、`.note`、卡片 / chip 阴影、`.chip.line`、`.chip.dark`、步骤条），字幕不变。这些值取自第 3、4 期 scenes.js 里用户已经看过的白底配色。
- `check_layout.py`：对比度的底色读背景层（`ENG.BG_RGB`，或第 3、4 期那样 scenes.js 自己涂的 `#bg` 背景色），不再写死深藏青。
- `sync_assets.py`：`bg_color`、`layout` 抄进 assets.js；episode.json 和 timeline.json 不一致时提醒重跑 build_timeline；写法不对时提醒；打印 `bg : solid #FFFFFF …; light theme`、`layout : center …`。
- `scenes.template.js`：分镜草稿的要点卡按 `ENG.CX` 居中；文件头的版面、背景说明改成两种版面。

脚本：`epcommon.py` 加 `BG_COLOR_NEW = "#FFFFFF"`、`LAYOUT_NEW = "center"`；`new_episode.py` 加 `--bg-color`（默认 #FFFFFF，`none` 不写）、`--layout`（默认 center，`old` 不写），`_说明` 和 script_data.py 骨架里的版面说明同步。`build_timeline.py` 不用改（episode.json 的字段整份抄进 timeline）。

文档：SKILL.md（第 0、3、4 步和「画面」原则）、pipeline-contract.md（§2 两个字段、§6、§7 开关和浅色主题）、visuals.md（尺寸、版面表、「背景」一节改成默认白底 + scenes.js 里还要自己管的几件事、坐标系）、cover.md（白底期的 cover.json `bg_file` 要自己填）、lessons.md（白底那一行改成“现在是引擎开关”）、scripts/README.md（new_episode 参数、“改了什么重跑什么”加一行）。

## 《AI每日日报》技能的改动（402）

改之前备份在 `AI日报/_旧稿/skill_ai-daily-news_402网页版前_20260928-155455/`。

- SKILL.md：配音规则加一句；第 4 步 `--batches` 改成“网页版单次放不下整期时才用”；第 5 步 401 照旧停下推送，402 改走网页版（苏晓晓生成器、S1、C01 整期一次贴进去、`read_network_requests` 拿任务编号、《原LAI如此》的 `fetch_check.py --urls … --series D:\大疆\AI日报` 下载成 `配音\raw\C01_v1.mp3`、记 `web_usage.txt`，再 `D voice`；插件连不上、付费 / 额度 / 人机验证就停下推送）；「踩过的坑」网页版那行补上 Plus。
- `scripts/tts_api.py`：402 提示改成“不要替用户充值，也不要换免费模型；按 SKILL.md 第 5 步改用网页版”；`s2.1-pro-free` 注明只在用户点名时用。`scripts/daily.py`：文件头和 `tts --model` 的 help 同步。
- 日报会话回复：和它今天的改动（白底封面、白板版默认、简介 2000 字保护、图片重试）没有冲突，它核对过 py_compile。它问白板手写版要不要移植到《原LAI如此》、谁来做——回复它等用户定，定之前两边都不改《原LAI如此》的引擎做手写。

## 测试

测试目录 `AI科普/_skilltest/bg_center_switch/`（旧引擎 = `before/engine-template/`，即上面备份里的模板）。渲染时没有别的会话在跑 Chromium，一次只跑一个。

- 第 2 期（2340×1080、鲸鱼娘、没有 bg_color / layout）新旧引擎：200 个时刻整帧 PNG **逐像素一致**，角色帧一致，页面无报错（`parity_ep2.py` → `parity_ep2_result.txt`）。
- 第 1 期（1920×1080）四组各 200 个时刻：legacy（旧时间轴）、legacy_terms、v2（67 条自动层）、v2_canvas1920 **全部逐像素一致**，字幕 140 行 HTML 一致（`parity_ep1.py` → `parity_ep1_result.txt`）。
- 新模式（`newmode.py`，第 3 期的时间轴 + 模板的分镜草稿，三种组合各 10 张静帧，拼图 `newmode/sheet_<组>.png`）：
  - white_center（新一期默认）：白底、浅色主题；开场大字、疑问卡、要点卡、总结卡都以画布 x 1170 居中；S03 标题收起后在画布 [1028, 84, 1313, 124]，中心 1170；目录深色底板；开头 0.3 s 是从深藏青淡入的中间色（和第 3、4 期一样）。check_layout：issues 0（3 条 expected 是疑问卡飞进目录）。
  - dark_center：深藏青 + 章节背景图 + 居中，check_layout issues 0。
  - white_old：白底 + 旧版面，标题收到左上（画布 x 650 = 舞台 440），和第 3、4 期的白底一致。
- `new_episode.py`：默认写 `"bg_color": "#FFFFFF"`、`"layout": "center"`，script_data.py 骨架的版面说明跟着变；`--bg-color none --layout old` 两项都不写；`--bg-color white` 报错退出、不建目录。测试期在 `newep/`。

## 待用户定

- 白板手写版“边说边画”要不要移植到《原LAI如此》（用户在日报会话说“之后的视频都做成角色在左下角，视频内容边说边画”，日报记录写“《原LAI如此》之后再移植”）；日报会话说 hand.js、hand_glyphs.py 可以直接搬，科普台本还要写“画什么”。
- 字比声音早 1 秒（日报白板版的 `LEAD`）要不要也用在《原LAI如此》。
- 字号要不要向日报看齐（日报字幕 56 px、要点 41–52 px；《原LAI如此》字幕 44 px、卡片正文约 26–38 px）。
- 仍待反馈：第 3 期的动作多少（AGENTS.md「角色动作尺度」第 03 行）。
