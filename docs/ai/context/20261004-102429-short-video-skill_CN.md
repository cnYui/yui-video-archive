# 短视频技能 short-video（2026-10-04）

## 用户原话（同一个会话里，接在 AI大圆镜 文风分析后面）

1. “短视频开头和结尾不要用开场和收尾的视频片段”
2. “需要你做一个短视频的skill”
3. “语言风格就和上面的那个up主的风格相似即可”（AI大圆镜，见 `20261004-095601-ai-dayuanjing-script-style_CN.md`）
4. “竖屏的比例就是我当前横屏比例竖过来就行”（横屏 2340×1080 → 竖屏 1080×2340）

另一个会话（“视频剪辑 20-30秒”，在做第 1 条短视频）转来的用户原话：“之后我也要做短视频，你尝试把这个视频剪辑成20秒到30秒”“配音可以使用曼波配音做翻译……短视频也是需要遵循双语字幕的要求”“短视频的话，需要你把这个长视频的两个不冲突的分镜放在同一个画面中出现（比如当前视频里一个人脸一个电脑操作的画面），你控制好时长，同时用ai配音讲解，就是进行二次剪辑，把视频里的观点更快更密集的讲出来”。

再一个会话同时定了目录规则（用户：“在当前项目的所有不同分类的文件夹下，都新创建短视频和长视频两个文件夹，划分开来，素材可以公用”，记录 `20261004-100500-short-long-folders-image-blaster-video_CN.md`）。技能照这个放：一条短视频在 `<合集>\短视频\NN_<短名>\`，素材在 `<合集>\素材\<YYYY-MM_主题>\`。

## 做了什么

- 技能 `短视频/skill/short-video/`，联接 `C:\Users\yui\.claude\skills\short-video`（PowerShell `New-Item -ItemType Junction`）。
  - `SKILL.md`：11 条硬性要求、步骤表、文件、验证过 / 没验证的。
  - `references/`：`script.md`（时长和字数、dual / single 两种稿子、录制稿字段、自检）、`layout.md`（竖屏分区、平台遮挡区、dual 怎么挑镜头和裁切）、`sources.md`（X / B 站 / YouTube / 官方页面）、`voice.md`（指向 Claude Code相关 的 voice.md + 第 1 条踩的点）、`facts.md`、`publish.md`（封面、B 站、抖音）。
  - `assets/engine-template/`：从 Claude Code相关 的引擎改的竖屏版。改了：`index.html`（1080×2340；标题 kicker + 两行大字一直在；上框 1000×575、内容仍按 1474×829 写再缩 0.6594；字幕 y 1195；dual 时下框 y 1325；整页叠加层 `#ovP`）、`engine.js`（标题、下框 `FR.scr2`、`layer: 'page' / 'b2'`）、`scenes.js`（`big()` 大数字卡、`ovB2`、`note()` / `box()` 的 `lower`）、`build_timeline.py`（`layout`、`ranges2`、`hook` / `kicker`；字幕上限改成中文 17 / 英文 60，靠覆盖 `bilingual_std` 的模块常量，没改共用文件；`LEAD 0`、`TAIL 0.8`；估时 5.6 字/秒）、`prep_frames.py`（两路画面 `scr/`、`scr2/`）、`check_subs.py`（竖屏的宽度、标题、上下框位置）、`render_all.py`（视口、联系表）、`finish.py`（不加片头片尾，SRT 从 0 起，540×1170 预览，静音时响度不报错）、`common.py`（`MAT` = 合集层素材）。没改：`mix_audio.py`、`qa_mix.py`、`capture_pages.py`、配音脚本。
  - `scripts/`：`new_short.py`（`--collection` / `--root`，`--layout dual|single`）、`make_cover.py`（`shot` 真实画面 + 钩子 + 箭头 / `split`，三个比例，字自动缩，字块放在离主角最远的角）、`fetch_x_video.py`、`tsheet.py`。
- 字幕字号和第 1 条对齐：中文 52 px + 英文 30 px（项目标准字号），竖屏每条中文 ≤ 17 字。我一开始用的 60 / 32 px，看到第 1 条的做法后改回标准字号。
- 规则同步：AGENTS.md（目录树、「短视频」一节、片头片尾一节的例外）、`AI科普/片头片尾/README.md`、`add-intro-outro.md`、6 个技能的「片头片尾」一节都写了“短视频不加”；根 README 的技能列表；`短视频/README.md`。
- `.gitignore`：`**/短视频/*/` 的渲染产物、配音原始文件、原片转写、封面中间文件、条目内的 `素材/` 不收。

## 验证

在 scratchpad 里用第 1 条的原片（Claude 官方 YouTube《Build an App With Claude Design》，4K VP9 webm，只读引用）建了三条测试：
- dual：`build_timeline.py --est`（15.2 s、7 条字幕）→ `check_subs.py`（中文最宽 884 px / 17 字，英文 857 px / 58 字符，没问题）→ `prep_frames.py`（两路各 2 段，8 秒）→ 静帧（上框人脸、下框 4K 裁 0.5×0.5 的屏幕，字清楚）→ `render_all.py`（2 路，456 帧 50 秒，0 报错）→ `finish.py`（1080×2340 成片 4.8 MB、预览、三份 SRT 从 0 起）。
- single：`big()`、`note()` 的位置对。
- `make_cover.py`：第一版字压在人头上、箭头太短，改成“字放离主角最远的角”后三个比例都对。
- `new_short.py --root …/某合集/短视频` 建在对的位置、合集层 `素材\` 自动建；`--collection 不存在的合集` 会报错。

**没验证**：真实配音下的 `mix_audio.py` / `qa_mix.py`（静音轨测的；代码和横屏引擎同一份）；抖音发布页；B 站竖屏投稿。

## 和第 1 条（另一个会话）的关系

- 第 1 条用 ffmpeg 直接剪（上下分屏 + ASS 字幕），开工时 1080×1920；我把用户定的 1080×2340 转告了它。它做完会把脚本和坑发过来，到时补进 references（可能要把它的 ffmpeg 做法作为“不用 HTML 引擎的快速路线”写进去，或者让下一条照技能的引擎做一遍对比）。
- 它补的（第一次消息）：曼波 S2 Pro 在短稿上约 5.5 字符/秒（后来更正为按汉字算：每个汉字约 0.22 s，30 秒 ≤ 约 125 汉字）；故事工作室的“00:00:42:25”是播放头；小测试会残留区块。已写进 `references/voice.md`。
- 会话「视频素材文件夹结构」在用这个技能的 single 版式做第二条（image-blaster 推荐，`独立视频\短视频\2026-10_image-blaster推荐\`，拷的是 10:17 的模板快照）。和现在的模板只差 `build_timeline.py`（估时 5.6 字/秒、打印）和 `common.py`（`MAT` 合集层素材），已发消息告诉它；它做完会把坑和改过的脚本发过来。

## 等用户

- 每条短视频归哪个合集、发哪些平台、进哪个 B 站合集。
- 第 1 条现在在顶层 `短视频\` 下，按新的目录规则要不要挪进某个合集的 `短视频\`（例如 `Claude Code相关\短视频\`），等它做完、用户定。

## 第 1 条做完后补的（10:55 左右）

另一个会话发来脚本清单和坑（它的 README、`20261004-105500-short-video-01-claude-design-ffmpeg_CN.md`）。补进技能的：
- **语速按汉字算**：每个汉字约 0.22 s（含英文词和标点），30 秒封顶 ≤ 约 125 汉字。`build_timeline.py --est` 改成数汉字 × 0.225 s；`script.md` 的字数表、`voice.md` 改了。
- **变速**：它的下框操作录屏用了 0.85–4×、人脸 0.9–1.1×。引擎加了 `"speed"`（`build_timeline.py` 算时长和延长、`prep_frames.py` 用 `setpts`、`scenes.js` 的 `V()` 换算），只允许静音段；测试：下框 2.5×（原片 60–79 s → 7.8 s），首中尾帧对得上。第一次跑抽了 506 帧——`-t` 是输出时长，要用变速后的时长，已改。
- 切点逐帧看（全屏人脸放大过程、模糊转场、文件名标签）、人脸素材不够长就首尾复用：写进 `layout.md`。
- Fish：改区块用 `find` 的 ref（窗口大小会变）、“重新生成”是整稿重来、zip 里 mp3 / wav 混着；faster-whisper 收 numpy 按 16 kHz：写进 `voice.md`。
- 加速凑时长作废（它试过 1.15×）：删句重生成。
- 第 1 条成片是 1080×2340、28.28 s，版式和技能的分区对齐。技能里把它写成“ffmpeg 直接合成的另一条路，纯双分镜不要叠加层时也可以照它做”。
- 模板改了 `build_timeline.py` `prep_frames.py` `scenes.js`，已告诉在用 10:17 快照的「视频素材文件夹结构」会话。

## 第 2 条（image-blaster，single 版式）做完后补的（11:30 左右）

会话「视频素材文件夹结构」照技能引擎做完第 2 条（`独立视频/短视频/2026-10_image-blaster推荐/`，59.3 s，记录 `20261004-111500-image-blaster-short-video_CN.md`）。补进技能的：
- **新规矩**：用户对它说“如果是英文讲解的话，你要用曼波ai配音做双语同传，还有双语字幕”（它第一版自己写解说、丢了原声，被纠正）。`script.md` 加了「英文讲解的素材 = 曼波中文同传」一节：逐词转写 → 静音处切句 → 同传晚 0.4 s → 原声 `HAS_AUDIO: True` 压低（−21 LUFS，说话时再 −9 dB）→ 中文字幕 = 同传、英文字幕 = 原话；自己的插句 range 写 mute。SKILL.md 第 5 条、`voice.md`、技能描述、AGENTS.md、记忆都改了。和第 1 条（压缩 28 秒、原声没留）的冲突列为等用户定。
- `capture_pages.py` 的 `@top` / `@time`（GitHub relative-time 在 shadow DOM）/ `@css:` / 别名元组合进了模板（合完只差 SPECS 例子）。
- `layout.md`：一大段同传写成一个场景多个相邻 range；每个场景末尾加 `{in, hold}`，不然素材会放到下一个镜头；自己的解说段 mute。
- `voice.md`：同传长句约 7.4 字/秒（短句专名多约 4.5 汉字/秒），估时只当上限；多区块 Ctrl+A 只选第一个区块的清法；导出下拉要点两次；Claude → 骷髅 / Cloud、中旬 → 中心的同音误识用 initial_prompt 解决。
- `new_short.py`：不写 `--num` 就用 `YYYY-MM_` 前缀（独立视频的命名）。

## 用户的四个决定 + 背景随机（14:00–14:30）

- 用户：“1.先不动 2.要 3.要移动 4.不要”——原LAI如此开场保留；12 个参考视频（+ 4 个下载打包文件）移进回收站；第 1 条挪进 `Claude Code相关/短视频/01_ClaudeDesign设计师用法/`（原片 webm / weba 挪到 `Claude Code相关/素材/2026-10_ClaudeDesign设计师用法/`，加 README；`config.py` / `gridframes.py` 两处素材路径改了；第一次 Move-Item 报“正在使用中”是我自己的 Bash 当前目录在里面）；压缩成 20–30 秒的二次剪辑不做同传、不留原声。相关文档（AGENTS.md、各 README、技能、记忆、`台本风格_AI大圆镜.md`、原LAI如此技能）都改了。
- 用户 2026-10-04：“之前让你生成的背景图片有三张，你都加入到背景图片的选择中，每一期视频随机挑选一张作为背景即可”“这个要求写入skill中”。我这个会话没生成过背景图；问了四个在做视频的会话，“视频剪辑 20-30秒”指出是 `短视频/版式方案_20261004/` 里的 `pattern_color` / `pattern_ink` / `pattern_orange`（1080×2340 透明 PNG，AI 编程工具图标低透明度印花，另一个会话做版式重设计时用 `make_pattern.py` 生成的；`pattern_none` 只是点阵，不算）。用户确认写进 short-video 技能。
  - 三张 + `make_pattern.py` 拷进 `assets/backgrounds/`，写了 README。
  - `new_short.py`：随机挑一张拷成 `制作/00_整片/bg.png`，`bg.json` 记选了哪张（`--bg` 指定、`--bg none` 不用；文件名不对先报错、不建目录）。
  - `build_timeline.py` 读 `bg.json` → `TL.bg`；`engine.js` 加 `hasbg`；`index.html` 的 `body.hasbg` 铺背景、关点阵。
  - 测试：三张各渲一张静帧（标题、字幕照样清楚）；随机 4 次挑到 color / ink / ink / color；指定、none、错名都对。第一次静帧没印花，是因为测试的原片刚被我挪走、`build_timeline.py` 报错没写出新时间轴（输出被我丢掉了），改测试路径后正常。
  - 同时另一个会话（做版式重设计的）在 14:19–14:26 把用户选的“方案 B + 边框 6”改进模板（`index.html` / `engine.js` / `scenes.js` / `check_subs.py`、`layout.md`），它的注释和 `layout.md` 里也写了背景随机；我发消息说明了背景这几行，之后不碰那几个引擎文件，等它改完。
- 14:40 左右：「视频素材文件夹结构」会话把用户选的版式 B + 边框 6 + GitHub 链接条合进了模板（我的背景几行保留了），它留在 `engine-template/` 里的 4 个 `*.bak_版式前` 我挪到 `assets/_旧稿/engine-template_版式前_20261004/`（`new_short.py` 会把模板目录里的文件逐个拷进每一条），`new_short.py` 改成只拷文件、跳过子目录和 `*.bak*`。用合并后的模板从 `new_short.py` 起 single / dual 各跑一遍（build_timeline → check_subs → prep_frames → 静帧），都通过；新版式 + 随机背景画面正常。
- 之后「视频素材文件夹结构」会话用新版式重渲了 Tavus-Griffin 那条（第一条 dual 真成片，45.5 s），自己合了 scenes.js（`pageShot` 的 `{lower:true}`、dual 底部译文条 56 px）和 layout.md；请我合我管的两处，已合：`build_timeline.py` 的说话人标签 `who`（拆条时算进标签宽度，subs 写 who）、`mix_audio.py` 第一句 a = 0 时下标变负的 bug（`if k < 0: seg, k = seg[-k:], 0`）。测过 who 标签（静帧里橙色 Nate 标签正常、check_subs 通过）。script.md 的录制稿字段补了 `who`。
- 15:00 左右：「视频剪辑 20-30秒」会话做完第 2 条（Design + Slides 合一条，约 2:18，原声 + BGM + 曼波第三人称同传，ffmpeg 路线，版式 B + 边框 6 + 随机背景，记录 `20261004-143000-short-video-02-claude-design-slides-interpretation_CN.md`），给了六条经验，已补进技能：SKILL.md 开头加“开工前、第一次渲整片前重读 SKILL.md + layout.md + script.md”（它第一轮用了 11:00 的旧技能，整轮返工），“已经做过的短视频”列表 + 两条路线（ffmpeg 路线以第 2 条的脚本为准，`make_bg.py` 有 PIL 画边框 6 的代码）；layout.md 切点加“人脸视频切换时 0.3–0.6 s 的灰白播放键帧、要看 4–8 fps 联系表”和人脸复用办法；script.md 第三人称补“不用他 / 她 / his / her、官方金句照原样、掌舵念不准换定方向”；voice.md 补故事工作室“新建项目”第一次点常被吞、同传 + 原声时质检用互相关量错位、两个模型都低才算问题。
- 15:20 左右，同一个会话又给了三条（用户对它说“字幕字号同步技能”“加 bgm”）：
  - **ASS 字号偏小（全项目）**：libass 的 Fontsize 是行高，写 52 只画出 CSS 52 px 的 0.686 倍；要写 76 / 44。改了共用的 `Way to AGI/skill/way-to-agi-episode/scripts/bilingual_std.py`（加 `LIBASS_EM = 0.686`、`ZH_ASS` / `EN_ASS`，`ass_header()` 用 76 / 44；调用它的只有它自己和已做完的 OpenAI视频中文版，影响只在以后新出的 ASS），`subtitles.md`、AGENTS.md 的双语标准一节、short-video SKILL.md 的 ffmpeg 路线都写了。之前用 ASS 烧的成片（OpenAI视频中文版、ClaudeSlides、第 1 条竖屏短视频）字偏小，没重做，告诉用户。
  - **BGM**：模板 `mix_audio.py` 的 `BGM_DUCK` 0.05 → 1.0（有原声也不压）、`BGM_SWELL_DB` 8 → 5；`voice.md` 加了 BGM 一条。
  - **dual 封面**：`publish.md` 指向第 2 条的 `make_cover_short.py`，暂不并进 `make_cover.py`。
