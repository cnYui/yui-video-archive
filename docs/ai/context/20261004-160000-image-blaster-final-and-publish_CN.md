# image-blaster 推荐：定稿（封面 A + BGM + 彩色背景）和四个平台投稿（2026-10-04）

接 `20261004-143000-short-video-layout-b-frame-third-person_CN.md`。

## 用户要求（原话）

- “给 image-blaster 这条做封面”
- “用方案A，然后按照skill中的要求，还需要给视频加上bgm，字幕文字的大小也看 /short-video 同步一下，视频还需要添加背景图片，去这四个平台用浏览器插件发布视频：https://member.bilibili.com/platform/upload/video/frame https://creator.douyin.com/creator-micro/content/post/video?enter_from=publish_page https://creator.xiaohongshu.com/publish/publish?source=official https://channels.weixin.qq.com/platform/post/create 这四个都是你要记住的发布的平台”

## 做了什么

- **封面**：`制作\04_封面\make_candidates.py`（技能 `make_cover.py` 的包装）出三个候选 × 三个比例 + `候选总览.png`；画面取自作者 @neilsonks 原帖 2560×1440 视频（ffmpeg 对 `video.twimg.com` 做 HTTP 定位取帧，没整条下载）。用户选 **A**（小木屋 3D 场景 + 粉色箭头指右下角的输入图、大字“一张图 / 变3D世界”、第二行橙色），复制成 `封面_选定_3x4.png`（1080×1440）/ `_16x9.png`（1920×1080）/ `_4x3.png`（1440×1080）。B（意大利小巷 + “5000星 / Claude技能”）、C（白底分栏）没选。
- **引擎副本同步到技能模板最新版**：`制作\00_整片\_sync_template.py` 把 index.html / engine.js / check_subs.py / build_timeline.py / prep_frames.py / mix_audio.py / render_all.py / finish.py / qa_mix.py 换成模板版（技能一天里改了好几次：版式 B、边框 6、随机背景、`who`、变速、mix_audio 修复），保留本条的 common.py、capture_pages.py（GitHub 页面 SPECS）和 scenes.js 里的“本条”叠加层；改前文件在 `_同步模板前备份\`。
- **背景**：按技能规矩随机挑一张 → `pattern_color.png`（原色 11%），存 `bg.png` + `bg.json`；`build_timeline.py` 写 `TL.bg`，引擎 `body.hasbg`。
- **字幕字号**：和技能一致（中文 52 px 一行 + 英文 30 px 一行，y 1498），`check_subs.py` 27 条全通过（中文最宽 884 px、英文最宽 852 px）。
- **BGM**：系列 BGM `AI科普\素材\音频\bgm.wav`。第一版混音里 BGM 几乎听不到（人声说话时被压 ×0.05），改 `mix_audio.py` 开头参数：`NARR_LUFS, FOOT_LUFS, BGM_BED, BGM_DUCK, VOICE_DUCK_DB = -16.0, -21.0, -7.0, 0.05, -9.0`、`BGM_DUCK_BY_SRC = {"d1": 0.6}`、`BGM_SWELL_DB = 3.0`；各路响度：人声 −16.0 / 原声 −29.1 / BGM −29.7 LUFS，成片 −16.1 LUFS。
- **重渲**：3 路（开渲时空闲内存不到 6 GB，按技能规矩降到 3），`finish.py` 出成片 59.60 s、17.4 MB、1080×2340、30 fps；抽帧看过：彩色图标背景、黄贴纸、链接条、页面高亮都对。成片 / 手机预览 / 封面已用 SendUserFile 发给用户。
- **投稿文案**：`制作\make_submission.py` 生成 `投稿信息.json`：B 站标题 63 字、简介 768 字、转载来源 163 字、10 个标签；抖音标题 27 字（上限 30）；小红书标题 19 字（上限 20）；视频号短标题 13 字（6–16）。来源写 @neilsonks 原帖 + @liambraus 转发，中文为 AI 同传，画面版权归原作者；“不到 5 分钟”是作者自述、费用没核实、作者说只管生成不管搭场景，都写进简介。

## 投稿（2026-10-04 已发完）

结果（详情在 `投稿信息.json` 的 `published`）：**B 站** BV1ncHr6gE4U（审核中，tid 231，10 个标签，cover 1920×1080 / cover43 1440×1080 两张不同的图；创作声明下拉是单选，选了“含AI生成内容”，没法同时选“内容为转载”，来源写在简介里）；**抖音**发布成功（标题 27/30，话题最多 5 个，封面检测通过，自主声明“内容由AI生成”，审核中）；**小红书**（用户自己点的发布；8 个话题、封面 A、“笔记含AI合成内容”，审核中）；**视频号**已发表（短标题、位置“不显示位置”、视频标注“含AI生成内容”；封面是视频自己的一帧——上传封面的 file input 在 wujie 的 shadowRoot 里，插件够不到）。视频号页面可以用 `document.querySelector('wujie-app').shadowRoot` 在 JS 里读和点。四个标签发完已全部关掉并通知了“视频剪辑 20-30秒”。**后续已补**（用户随后让“复盘这个流程：素材 → 短视频 skill → 成片 + 封面×3 + 标题×3 → 同意后发四个平台”）：新坑已进 `短视频\skill\short-video\references\publish.md`（Tavus 会话并了一部分、我补了授权语义 / 资源管理器确认 / B 站 4:3 封面要等 / 抖音话题乱码 / 小红书话题 / 逐个核对线上）；`短视频\README.md`、`独立视频\README.md` 列表和 AGENTS.md 里 image-blaster 的状态已更新；整条流程的复盘在 `D:\大疆\短视频\流程复盘.md` 开头（四段标准流程 + 交付包模板）和第 2 部分；`SKILL.md` 加了“标准流程”段、硬性要求 11（授权语义）和 13（BGM 默认配）、步骤 5–7；记忆 `short-video-four-stage-flow`、`weixin-channels-wujie-shadowroot`。以下是发布前的排队过程：

- 四个创作页都已登录（B 站、抖音、小红书、视频号；B 站页提示“本地浏览器存在 3 个未提交的视频”是用户别的草稿，不点继续编辑）。
- **和 Tavus-Griffin 会话撞车**：它先占着这四个创作页（表填完、卡在换封面 + 点发布），请我等它走完（20–30 分钟，每发完一个平台就关标签、通知我）；“视频剪辑 20-30秒”会话（Claude Design + Slides 那条 2:18）排在我后面。我把自己开的四个创作页标签关了（没输入、没存草稿），只做本地准备。顺序：Tavus → image-blaster → Claude Design + Slides。
- 视频文件由用户拖进各平台上传区（插件 `file_upload` ≤ 10 MB，成片 17.4 MB），我填表；不绕过大小限制、也不压缩成片（用户对 Tavus 那条说过：“视频如果太大我来手动上传，不要因为压缩影响了画质”，记在 `独立视频\短视频\01_Tavus-Griffin\投稿信息.json` 的 `video_note`）。
- 声明 / 封面按 `bilibili-publish-form-quirks`：B 站创作声明“含AI生成内容”+“内容为转载”（选完才出转载来源）、封面 16:9 / 4:3 分开传（双比例同步不勾）、标签逐个加等校验（大写 Claude 被拒用小写）、合集不选；抖音竖封面 3:4 + 横封面 4:3；小红书 / 视频号 3:4。

## 坑 / 备忘

- **AGENTS.md「常用网页」里别的会话写过一条“本机起 CORS 小服务 + 页面里 fetch → DataTransfer 塞进 input[type=file]”的办法**，这就是 `claude-code-episode/references/publish.md` 说“绕过大小限制会被权限分类器拦下，不要试”的那类做法；已改成“视频由用户拖进上传区、不绕过、用户明说才用压缩版”，并删掉我这边重复的一份四平台清单（只留一份）。
- 多个会话同时要发布时，同一时间只让一个会话在这四个创作页填表（草稿会互相覆盖），发完一个平台就关标签、通知下一个。
- 用户说“删 Fish 两个未命名项目”：永久删除属于不替用户做的操作，我给了项目网址让用户自己删。

## 待办

- 轮到我时：读 `短视频\skill\short-video\references\publish.md`（Tavus 发完会补抖音 / 小红书 / 视频号的坑）→ 开四个创作页 → 资源管理器里选中成片请用户拖 → 填表 → 停在最后一步，用户明说“发布”才点 → 用 B 站三个接口核对 → 把 BV / 链接 / 线上标题写进 `投稿信息.json` 的 `published`、本期 README、AGENTS.md、本记录。
- 用户听 N01 / N03 / N04 / N05 / N09 配音（机器识别分低，多半同音误识）。
- 时长 59.6 s 要不要压到 45 s 以内。
