# 全流程：命令、数字、坑（照第 1 期整理）

时间参考：第 1 期从下载到成片约 6 小时，其中真正返工的是配音（事实核对晚了）和字幕（漏了英文）；顺的话抽帧 8 分钟（增量后改一处几十秒）、渲染 4 路 3–4 分钟、混音 1 分钟。

## 0. 开工

1. 读 `D:\大疆\AGENTS.md` 的「所有视频通用的规则」「共同约束」（含中英双语字幕标准）和「OpenAI相关」一节；**看同合集最新一期怎么做**（不只看“上一个会话刚做的那期”）。
2. 问用户（一次问完）：标题 / 封面字各写什么（不重复）、片尾清单、素材链接；是不是转载别人的（转载走 Claude Slides 那条 ASS 做法）。
3. 去 B 站投稿页「加入合集」下拉里看合集（别凭印象说“没有”）。
4. `python scripts/new_episode.py --num 02 --name 短名`；`.gitignore` 补它打印的行。
5. 记录文件：`D:\大疆\docs\ai\context\<时间>-<slug>_CN.md`（用户的要求原话、做法、坑、待办；做完更新）。

## 1. 下载素材（X 平台视频）

用户说“用浏览器插件使用 twittersaver.net 下载这些视频”：
1. Chrome 插件（`mcp__claude-in-chrome__*`，不用内置浏览器）开 `https://twittersaver.net/zh-cn`。**页面有点击劫持广告，别用鼠标点输入框**：`javascript_tool` 用原生 value setter 给 `input[type=text]` 填链接（去掉 `?s=20`）、派发 input / change，再按文字“下载”找到按钮 `.click()`，等 6 s；多条链接用 `browser_batch` 一批做 3 条。
2. 结果页：`get_page_text` 读得到推文文字（长帖会截断）；`read_page`（interactive）读下载链接 `dl.snapcdn.app/get?token=<JWT>`（1 小时有效），**JWT 的 payload 里是真实源地址，核对是 `video.twimg.com` 再下**：`curl.exe -L -A <Chrome UA> -e https://twittersaver.net/ -o <文件> <链接>`，每条取最高清晰度；`ffprobe` 核对规格 / 时长 / 有没有音轨。引用转推会带出被引用那条的视频，用视频 ID 去重。
3. **推文完整文字、发帖时间、引用关系、t.co 展开后的链接**用 X 嵌入接口读（不用登录）：`curl "https://cdn.syndication.twimg.com/tweet-result?id=<帖子ID>&lang=en&token=a"`（JSON：`text`、`created_at`、`quoted_tweet`、`entities.urls[].expanded_url`、`mediaDetails`；长帖的 `note_tweet` 只有 id，全文要去 x.com 页面读）。
4. 文件名 `<账号>_<帖子ID>.mp4`，放 `素材/X平台视频/`，写 `来源.md`（账号、原帖链接、发帖时间、内容转述、规格 · 时长 · 声音、要注意的事实）。**转发的作品标原作者**（第 1 期人体图谱：@R_ChajX 转发 @ashebytes）。
5. 每个视频用 `ffmpeg ebur128` 量响度：`I: -70 LUFS` = 静音；有声的再用 faster-whisper `small` 看有没有人说话（第 1 期 3 条有声的全是音乐 / 环境声，不用翻译）。

## 2. 看素材

- 联系表：先每条抽 12–20 帧拼一张看内容；再按时间标签（每帧左上角写秒数）细看要选段的视频（第 1 期用 `tsheet.py`：ffmpeg 取帧 + PIL 贴标签，3:22 的长片按 5 s 一格），**最后帧的秒数要封顶在时长 − 0.2 s**（否则 ffmpeg 取不到）。
- 选段：每条素材取 2–4 个精彩片段（每段 3–10 s），不要整条放；长片（3 分钟）取 4 段拼 35 s；开场快剪 4 段 × 1.6 s；原片自带的模型标签 / 水印位置要记下来，叠加层避开（见 §4 的 `ui`）。
- 官方画面：DevDay 主题演讲（`独立视频/2026-10_OpenAI-DevDay-2026解读/素材/keynote_video_silent.mp4` + `keynote_audio.weba`）。已核对的入点（秒）：GPT-6.1 Sol 大屏 1198.6（幻灯片 1198.4 出现）、价格表 1207.2（crop `[0.51, 0.23, 0.97, 0.69]`）、Ultrafast 幻灯片 1255–1262、现场造火箭对比 1271–1279（左 Ultrafast / 右普通版）；其余看 DevDay 解读的 `台本/V?_*.json` 和它的 README（词级转写 `words.py` 查时间，别按 YouTube 自动字幕）。幻灯片放大用 range 的 `crop`（占整帧比例，裁出来 16:9 就铺满）。

## 3. 台本和画面表

**先做事实核对（facts.md），再写台本。**
- `台本/录制稿.json`：`slug`（成片文件名前缀）、`titleCard`（开场标题卡：kick / a 白 / b 蓝最大 / chips）、`outroCard`（片尾卡片：页面画面 + 二维码 + 链接 + 全部来源）、`chapters`（≤ 3 条，名字 ≤ 7 字）、`lines`（`id` `zh` `say` `en`）。
- **2026-10-04 起照 AI大圆镜 的写法**：先读 `D:\大疆\docs\台本风格_AI大圆镜.md`（钩子带数字、来源紧跟、分句 8–12 字、数字密、短问句换挡、泼冷水、金句收尾）；日期仍按下面这条的规矩写。
- 风格：短句口语，一句一个意思；不用“不是……而是……”；中文每句 ≤ 约 20 字；网友的说法挂名；官方事实写出处（“官方价格页”“发布会幻灯片”）；不写具体日期（美国时间 / 北京时间差一天，写“这几天”；官方发布日期要写时标“DevDay 9 月 29 日”这类官方日期）。画外音占比 ≤ 约 31%（第 1 期估算 42%、实际 31%，估时按 6.4 字/秒偏长）。
- `台本/plan.json`：`thumbs`（左栏缩略图取帧）、`card_imgs`（片尾卡片图取帧）、`qr`（二维码文件，OpenCV `QRCodeEncoder` 生成、**用 `QRCodeDetector` 解码核对**，放大要用整数倍并补 ≥ 4 模块白边）、`plan`（场景按先后）。场景字段：
  - `type`：`clip`（若干段素材首尾相接）/ `card`（`dur` 秒的卡片，没有素材画面）；`overlay`：`title`（开场标题）/ `outro`（片尾卡片）/ 默认素材场景；`chapter`：−1 = 开场（左栏都不亮）、0–2 = 第几章、章数 = 片尾（全标“已看”）；
  - `ranges`：`[{src, in, out, crop?, mute?, gain_db?}]`；话比画面长时最后一段接着往下放、放完定格；**定格也可以写成一段**：`{src, in, hold: 秒数}` = 取素材 `in` 那一帧定格这么久（只抽 1 帧、没有原声；`in` 要离素材结尾 ≥ 0.1 s，`build_timeline.py` 会查）。给静止画面（读提示、读解释）配较长的旁白时用，一个节拍一个场景：`[{真实播放的几秒}, {hold}]`（2026-10-03 从 Claude Code相关 第 3 期回补）；
  - `lines`：`[{id, a}]`，`a` = 这句话从场景开头起第几秒开口（前一句没念完就顺延 0.18 s）；
  - `name`（左上角作品名，页面里的英文标题）、`tag`（模型，发布者标的）、`credit`（右上角来源，`@账号 · X · 模型名为发布者所标`）；
  - `caps`：素材上的小字注释 `[{a, b, zh, sub}]`（**b 不能超过场景长度**，`build_timeline.py` 会报）；
  - `ui`：见 §4。
- 左栏缩略图、卡片图和二维码是**画面里唯一不是素材的东西**，片尾卡片只放链接和二维码（让观众自己去玩）。

## 4. 引擎和叠加层

版式：2340×1080、白底；演示区（页面 1504×859，内容坐标 1474×829 不缩放）在 (718, 40)、素材帧抽成 1474×829（宽高比对不上的放大铺满做模糊底、原片居中）；左栏 (118, 470)；字幕带 y 922（中文 52 + 英文 30）；强调色 OpenAI 蓝 `#0285FF`。

素材场景只有三样叠加（`scenes.js`）：左上角“模型 | 作品名”标签、右上角来源、小字注释条；`ui` 控制位置：
- `nt`：作品名标签 `tl`（默认）/ `none`；`cr`：来源 `tr`（默认）/ `br` / `none`；`cap`：注释条 `bl`（默认）/ `br` / `tl` / `tl2`（作品名标签下面，价格表这类左上角有空白的画面；折行 ≤ 540 px）；`stack: true`：标签竖排（近似方形的素材 1:1、0.9:1、1.04:1 两侧有 300 多 px 的模糊边，标签放进去不压素材；来源自动分两行）。
- **素材自己带的标签不要盖**：Higgsfield 的 SOL / ASTRA 在右上角、斗兽场四格的模型名在各格顶上 → 这些场景 `nt: none` / `cr: br` / `cr: none` 并把来源写进注释条的 `sub`；发布会画面左下角有 “OpenAI DevDay” 水印 → `cap: br`。
- 开场标题盖在 4 段快剪上（`overlay: title`）；片尾卡片 `overlay: outro`。

## 5. 时间轴、抽帧、版面自查

```bash
cd "<本期>\制作\00_整片"
python build_timeline.py [--est]    # --est：配音还没出，按字数估时间（出版式小样）；看“字幕 N 条（超长没拆开：…）”和【注意】（注释超出场景）
python check_subs.py                # 字幕版式自检（中英各一行、不超出画面、演示区不压字幕带）
python prep_frames.py               # 抽帧（增量：media/scr/_manifest.json；约 5,800 帧、768 MB）
python render_all.py --stills-segs  # 每个场景 3 张静帧 + 联系表（stills/_sheet_segs_*.png）
python render_all.py --stills 16.5 18.0   # 指定时刻
```
- **静帧要逐张看**（第 1 期靠它抓到：价格表注释压住 $50.00、竖排标签换行太碎、片尾来源行被裁）。
- 配音还没出时先 `--est` 排版面；配音出来后重跑 `build_timeline.py` + `prep_frames.py`（只重抽变了的段）。
- 改了 CSS / 叠加层不用重抽帧，直接重出静帧。

## 6. 混音、渲染、复核

- `mix_audio.py`：画外音 −16 LUFS（两遍 loudnorm，线性）；素材原声每个素材拼起来量一次拉到 −21 LUFS、有人说话压 −9 dB；发布会画面 `gain_db: -10`；系列 BGM（`AI科普/素材/音频/bgm.wav`）−16 dB 垫底、有原声的素材段里压到 ×0.05、没人说话也没素材声时抬 +8 dB；整片按 −16 LUFS 拉，**不要被峰值限成 −18**（只有个别几秒接近 −1 dBFS，用软限幅压）。`HAS_AUDIO` 里静音 / 无音轨的素材一定写 False。
- **渲染**：先 `ListAgents`、看空闲内存（`Get-CimInstance Win32_OperatingSystem`），空闲 ≥ 6 GB 用 4 路，否则 `$env:RENDER_WORKERS=3`；`python render_all.py`（后台跑，`run_in_background`）→ `整片_v1.mp4`；只改了一个场景：`python render_all.py --worker K A B`（K = 路号、A B = 那一路的起止帧，`parts/part_K.json` 里有）再 `python render_all.py --concat`（要带同样的 `RENDER_WORKERS`）。每路约 160–240 s。
- **复核（出片前必做）**：`python qa_mix.py > qa_mix_report.txt`（把混音按字幕逐句切出来识别，和字幕比；看每条窗口里是不是对应那句话、有没有叠音 / 放错位置；这个声线的 sh/x、q/x、Sol、dots 会被听错，**分数低不等于读错，要用户耳朵听**）；从成片抽 15–20 个时刻的帧拼联系表看（片头、标题卡、官方画面、每个作品、片尾卡片、片尾清单）。

## 7. 收尾（finish.py）

`python finish.py`：悠一片头片尾（`AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py`，正片不重编码）→ `<slug>_成片.mp4`、`_手机预览.mp4`（1560×720）、三份 SRT、响度报告（目标 −16 LUFS，真峰值 ≤ −0.5 dBFS 都行）。片尾 `outro.json`（`references` 参考文献：官方页面、发布会、网友原帖；`items` 致谢：实测画面 / 官方画面 / 资料 / 配音 / 剪辑 / 视频剪辑模型，各 ≤ 8 项）是草稿，**每期问用户**。片头 4.8 s、片尾 9.0 s，**所有视频必加**。

## 8. 记录和文档

- 投稿后：`投稿信息.json`（BV、提交时间、实际标签）、本期 README / `AGENTS.md`「OpenAI相关」一节 / 根 `README.md` 的视频存档表 / `docs/ai/context` 记录；新坑写进记忆。GitHub release 和提交 git：用户没说就不做。
- 渲染产物（`media/`、`parts/`、`stills/`、`frames.js`、`timeline.*`）和第三方作品原帧做的封面不进公开仓库（`new_episode.py` 打印要加的 `.gitignore` 行）。
- 目录清理：用户的 dcg 钩子会拦递归删除和某些 `mv`（`mv … 2>/dev/null` 会被当成 mv 到 `/dev/null`），不要的文件挪进 `_旧稿/`，不绕。

## 9. 并行（省时间）

调研子代理（事实核对）、渲染、抽帧、混音复核都可以放后台；浏览器操作（下载、Fish、投稿）串行；同一时间只一个渲染；和别的会话共用 Chrome、渲染、Fish 时先 `SendMessage` 约好。
