# Meta Muse Gadgets 开源短视频 — 状态与交接（2026-10-05 10:5x）

用户原话：“做一个这个开源信息的短视频，四平台发布”（四条 X 帖：@natfriedman、@alexandr_wang ×2、@AYi_AInotes）。归 **独立视频**（Meta 自己的新品，不属于 OpenAI相关 / Claude Code相关）。

## 状态
**2026-10-05 四个平台都已发布并核对线上。** 用户 11:58 回“封面 A 标题 1 同意，并行发布”（= 授权发布），12:06 拖好成片；我在 Chrome 共用窗口里用自己的标签组“✅开源信息短视频制作”一次填完整、读回核对、点发布：**视频号 12:14 → 抖音 12:18 → 小红书 12:23（页面按北京时间显示 11:23）→ B 站 12:29（BV1fQHp6HEjt）**。15:0x 回头核对：B 站“开放浏览”（tid 231、10 个标签、`cover` 1920×1080 / `cover43` 1440×1080 两张图都对）、抖音内容管理“已发布”（封面 A）、小红书笔记管理有这条（不在“审核中”里）、视频号视频管理第一条；四个标签已关。逐平台的字段和替换项在 `投稿信息.json` 的 `published`。**还没做**：用户没说要补合集（独立视频不选）；抖音 / 小红书 / 视频号的作品链接（B 站有 BV）没记。发布前的状态记录（保留作参考）：
- 12:0x 之前：成片已出，交付包已发给用户，等“封面 X 标题 Y 同意”；没有发布任何平台。
- 成片 `MuseGadgets开源_成片.mp4`（1080×2340、76.43 s、−16.0 LUFS、21.2 MB）、`_手机预览.mp4`、三份 SRT（35 条中英双语）；配音 Fish「温柔男生」S2 Pro，BGM 系列 bgm.wav 床 −7 dB（空档比人声低约 9 dB、说话时约低 14 dB）；背景印花 pattern_color。
- 封面 3×3：`制作/04_封面/候选总览.png`（A 推荐：Nat 帖里五台设备合影 +“Meta开源 / AI硬件”；B：Home Link 3D +“免费送 / 5000台”；C：Connection 图 +“只开源 / 手脚”），框版 `make_cover_framed.py`（本条拷了一份在 04_封面）。
- 标题 3×4 在 `投稿信息.json` 的 `titles`（已过 `check_titles.py`）；简介草稿在 `desc_draft`；话题 / 声明 / 位置按默认（抖音 5 个、小红书 / 视频号 10 个，“含 AI 生成内容”，视频号不显示位置，没有合集）。
- 机器识别分低、要用耳朵听的句子：**N01（“一千多颗星”被听成“核心”）、N05（“示例项目”被听成“视力项目”）、N07（“发货”被听成“发火”）**；Nat 读成接近“Net”，属英语 /næt/ 正常读法。

## 用户同意之后（技能 short-video 的步骤 7，`references/publish.md`）
1. `python D:\大疆\短视频\skill\short-video\scripts\make_candidates.py <本条目录> --select X`（框版只复制成 `封面_选定_3x4 / 16x9 / 4x3.png`）→ `python …\scripts\cover_frame0.py <本条目录>`（成片第 0 帧换成选定封面，视频号用）。
2. `投稿信息.json`：把选中的标题写进 `bilibili.title / douyin.title / xiaohongshu.title / weixin_channels.short_title`，`desc` 用 `desc_draft`（抖音 / 小红书 / 视频号描述第一行放完整标题 + 话题），`approval` 记下选择和时间。
3. `ListAgents` 排队用 Chrome；`explorer.exe "/select,<成片完整路径>"` 并确认窗口弹出；用户拖原片进四个上传区；一次填完整、读回核对；点发布；逐个核对线上（B 站三个接口 / 抖音内容管理 / 小红书笔记管理 / 视频号视频管理）。**简介要写**：美国时间、画面来源（AYi 动画非官方）、AI 配音、BGM、版权；Muse 目前只在部分地区可用、Home Link 仅限美国、token 条款。
4. “两天多”到 2026-10-06 03:21（日本时间）之前有效，之后要改“三天”。

## 做了什么（简）
- 素材：`独立视频\素材\2026-10_MuseGadgets开源\`（`来源.md` 有出处）：推文 JSON / 配图、AYi 15 s 动画、官网 8 张项目卡片、Home Link 3D 组件高清帧；录制 / 合成脚本在 `制作\01_素材录制\`（`cap_cards.py`、`cap_widget_stills.py`、`make_widget_clip.py`、`make_cards_clip.py`、`make_conn_clip.py`、`make_schedules.py`、`fix_plan.py`）。
- 页面截图：`制作\00_整片\capture_pages.py`（推文用美西时区；GitHub；官网 640 宽切片；`S_terms` = 官网 Token Terms）。
- 台本 v2：`台本\录制稿.json`；事实核对 `台本\事实核对.md`（写的是 v1，v2 改动见下）。
- **独立事实核对子代理的意见已并进 v2**：去掉“七十个 PR”（22 合并 / 37 开着 / 11 关闭，作者身份不明）；“美国时间 10 月 2 日”；“示例项目”（官网叫 Project Ideas，7 个是第三方板子）；“能让”；“先到先得”；新增 N08 = token 条款（`gadgets.muse.ai/sdk-terms`：仅限个人非商用、最多 50 台、不能卖 / 公开上架、Meta 可随时暂停或收回、非受支持产品；Apache 2.0 只管代码）；收尾“开源的是手脚，大脑还在 Meta 的云上”是编辑总结，依据 token 配对 + 官网 Connection 图里的 “Muse VM”。

## 要改台词 / 重配时的重做顺序
改 `录制稿.json` → Fish 故事工作室新建空白项目（温柔男生 + S2 Pro，按顺序键入要改的句子的 `say`）→ 生成 → 导出“按段落拆分” → `制作\02_配音\import_picks.py "<zip>" N01 N02 …` → `build_voice.py --qa` → `制作\00_整片\build_timeline.py` → `制作\01_素材录制\make_schedules.py`（词级识别 N05 / N06 / N09，重渲轮播 / Home Link / 收尾三个片段，写 `sched.js`）→ `fix_plan.py` → `build_timeline.py` → `check_subs.py` → `prep_frames.py` → 静帧自检（`render_all.py --stills-segs`）→ `mix_audio.py` → 渲染前 `ListAgents` → `render_all.py`（4 路，约 96 s）→ `qa_mix.py` → `finish.py`。只改混音时：`mix_audio.py` → `render_all.py --concat` → `finish.py`。

## 踩坑（本条新摸出的）
- **Chrome 共用窗口**：各会话的标签都在 Chrome 窗口里（标签名带“属于‘…’群组”）；UIA（`AutomationElement.FromHandle(窗口)` → `ControlType.TabItem` → 名字含自己的组名 → `SelectionItemPattern.Select()`）能选中自己的标签；窗口最小化先 `ShowWindow(9)` + 按一下 Alt 再 `SetForegroundWindow`。**`computer type` 在 hidden 标签里也能键入**（字母、换行都对，偶尔 CDP 超时但实际已打完，用 JS 读回确认），前提是编辑器 `ProseMirror-focused`；没聚焦就打字会触发 Fish 的页面快捷键（误触发过一次生成）。`ref` 点击在 hidden 标签里有时没反应，用坐标点。关掉自己组最后一个标签，组就没了；用户会在这个窗口全屏看 B 站，别抢前台。
- **Fish 编辑器**：多块文档里 Ctrl+A 只选第一块、**Delete 键会删掉最后一块，清字用 Backspace**；新建空白项目后第一块是示例句，单块时 Ctrl+A 再键入即可。
- **Playwright 录官网**：CDP screencast 的帧只有 CSS 像素大小；要高清用 `Page.captureScreenshot` 的 `clip.scale`（约 6–7 fps）；官网轮播 `[class*=exampleTrack]` 先匹配到外层 DIV（有遮罩），真正滚动的是 UL；第 1 张卡片图延迟渲染，要多等；推文嵌入页的时间按浏览器时区显示。
- 经 shell 传带反斜杠的路径会被吃（`\2026` 变成控制字符）：路径一律用 Write / Edit，或在 Python 里用 `chr(92)`。
- `libx264 yuv420p` 要偶数宽高：素材框 1474×829 的片段做成 1474×830。
