# 《How an Anthropic designer uses Claude Slides》合并音视频 + 中文封面 + 中英字幕（2026-10-02）

## 用户的要求（原话）

1. （附英文封面截图 + `Downloads\videoplayback (1).m4a`、`videoplayback (3).mp4`）“你把这两个拼在一个视频中，然后 把封面修改为中文，其他不变”
2. （我在看视频时发来）“你给视频加上中文的字幕，这样就是双语字幕了”
3. （我第一版字幕出来后）“字幕的要求，你看一下当前项目的文件夹中，其他的分集的skill中的字幕要求是什么，然后统一用那个双语标准”

## 做了什么（目录 `独立视频/2026-10_ClaudeSlides设计师用法/`，README 有文件表和重做命令）

- **合并**：`.m4a` = AAC 44.1 kHz 立体声 104.16 s，`.mp4` = H.264 High 1920×1080 24 fps 104.125 s、没有音轨（YouTube 的 DASH 视频流 + 音频流）→ `ffmpeg -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart` → `成片_无字幕.mp4`（两路时长只差 0.04 s，没处理）。
- **英文字幕**：原片没有字幕，只有设计过的画面文字。`制作/02_转写/asr_en.py`（faster-whisper large-v3-turbo、CPU int8、4 线程，88 s，21 段，逐词时间、VAD、提示词放产品名和人名）。校对：Cloud → Claude（2 处）、Claude's slides → Claude Slides、Voice Memo's → Voice Memos；第 11 句的 “for three to read.” 是幻觉，删。
- **中文译文**：我自己译，22 屏，口语短句，产品名不翻，iOS 的 Voice Memos 用“语音备忘录”（`台本/build_cues.py`，`cues.json` 是唯一来源）。第 4 句按逐词时间拆成两屏（“…我叫 Nate，是 Anthropic 的设计师。” / “下面讲讲我怎么用 Claude Slides 做事…”）。
- **字幕标准（第二版，用户第 3 条要求后重做）**：第一版我照 OpenAI 那条的样式做的（中文 54 / 英文 34 px、半透明黑底、可两行、22 屏），用户让我对照其他分集 skill 里的字幕要求、统一用项目的中英双语标准。查到的标准在 `Way to AGI/skill/way-to-agi-episode/references/subtitles.md`（「中英双语」「括号注释」「终检」）和 `pipeline.md` §2，样式 CSS 在该技能模板 `assets/template/制作/03_成片/index.html` 的 `#subs` / `#subZh` / `#subEn`（计算机研究生技能沿用）：中文 52 px / 行高 66（Noto Sans SC 800，墨黑 `#1B1B1F`，白边 10 px 描边）、英文 30 px / 行高 40（600，灰 `#4B5563`，白边 6 px），居中，字幕带 y 922 起（中文在带顶、英文从带顶往下 70 px），各一行不换行；一条 1–2 句、中文 ≤ 约 28 字、英文 ≤ 约 90 字符（括号注释算在内），放不下就拆条；每条开始前 0.1 s 显示到结束后 0.45 s、不叠；括号注释全角、≤ 12 字、约每分钟一条、只写有把握的、英文对应半角括号；术语表全片统一；字幕和成片里听到的一致；SRT 三份（双语 / 中文 / 英文）。OpenAI 那两条（`2026-10_OpenAI视频中文版`、`2026-10_OpenAI-DevDay-2026解读`）用的是另一套，**没统一**，用户没提、另一个会话还在做，没动。
- **按标准重做**：`台本/build_cues.py` 把 22 屏拆成 26 条（长句按逐词时间拆：C02/C03、C06/C07、C16/C17、C18/C19 等），加了术语表和一处括号注释（“Claude Slides（做幻灯片的功能）” / “(the slide-making feature)”）；`制作/00_整片/make_subs.py` 按 CSS 的位置和样式出 ASS（两个事件：中文 `\an5\pos(960,955)`、英文 `\an5\pos(960,1012)`，白边 5 px / 3 px），并用 PIL 量实际宽度，超过 28.5 字 / 90 字符就报出来（26 条全部通过）；三份 SRT 改名 `成片_双语字幕.srt` / `成片_中文字幕.srt` / `成片_英文字幕.srt`（旧名 `字幕_*.srt` 挪进 `_旧稿/`）。
- **字重**：`NotoSansSC.ttf` 是变量字体，默认实例是 wght 100，libass 靠 `\b` 选不准字重 → 用 fontTools `instantiateVariableFont` 切出静态 ExtraBold（800）和 SemiBold（600），族名改成 `NSC800` / `NSC600`，放 `制作/00_整片/fonts/`，ASS 里按族名取，每个约 10 MB、各切 16–20 s。
- **终检**：全片 26 条各抽一帧看了（中英上下位置、一行放得下、白边在米色 / 青绿 / 白界面 / 黑幻灯片上都读得清、没有冲出画面、括号注释读得完）；没有空的 zh / en。
- **中文封面**（`制作/04_封面/make_cover_zh.py`）：用户给的是 1280×720 英文缩略图（橙底、米色卡片、编辑器工具栏、文字框带四个角点；注意它和片头动画的配色是反的——封面橙底米卡，片头米底橙卡）。只涂掉文字框里面，标题改成“Anthropic 设计师 / 如何使用 **Claude Slides**”；Anthropic 和粗体 Claude Slides 直接从原图裁下来贴回去（字体一模一样），中文用 Noto Serif SC 500（Playwright 从 Google Fonts 加载），基线对齐原来两行（y = 523、613），补回光标；`封面_16x9.png`（1280×720，和原图同尺寸）、`封面_4x3.png`（卡片向下接长 240 px，B 站 4:3 位用）。

## 坑

- 一开始把 “an Anthropic” 当成一个词裁了，结果封面第一行多出 “an”：词间距比我设的阈值（14 px）小，要把阈值降到 5 px 才分得出 “an”（351–441）和 “Anthropic”（456–830）。
- 预览用 `ffmpeg -ss 18 -to 30 -i …` 时 `-ss` 在 `-i` 前，输出时间戳从 0 开始，字幕就按 0 起算，预览里字幕和画面错位（全片渲染没有这个问题）：预览只能看样式，不能对时间。
- 预览（`render.py 20 32`）里字幕按绝对时间、画面从 20 s 起，对不上是预览的问题，全片没有。
- 同时另一个会话（OpenAI DevDay）在重渲 6 条视频，内存只剩 4.9 GB：我只开了一次 whisper（4 线程）和短时间的 ffmpeg，没有开渲染；收到它的消息后回复了。
- 想核对 “for three to read”：看了前后画面、对比 medium / large-v3-turbo 的结果，确认是识别幻觉。

## 没做 / 待办

- 没做配音（用户只要中文字幕）。
- 英文逐字稿、译文、字幕文件和封面图是 Anthropic 视频的衍生品，已在 `.gitignore` 末尾排除；`独立视频/` 整体还是未跟踪状态，没提交 git。
- 目录还在 `独立视频/`；用户后来把这条放进了 B 站合集「Claude Code相关」（第 2 集），但文件夹没挪进 `Claude Code相关/`（要挪的话要同步改 `.gitignore`、README、AGENTS.md、记录里的路径），用户没说就没动。

## 投稿（2026-10-02 16:13，用户让我用 Chrome 插件发）

用户（原话）：“然后你用浏览器插件发布这个视频，标题为：Anthropic设计师教你如何使用Claude，分集选择Claude Code相关”；随后他自己把 `成片_中英字幕.mp4`（17.3 MB，超过插件 10 MB 的上传上限）拖进上传页，说“Claude Slides正在上传，你来填写标题和封面”。我把标题、封面、转载信息、标签、简介、合集都填好后点了“立即投稿”（我把“发布这个视频”当成了投稿的授权；合集 README 里原来写“立即投稿等用户说”，那是第 1 期用户要自己改标题时的规矩，已改成“用户只说填写时等用户说，明说发布并给了标题 / 合集可以直接点”）。

- **结果**：[BV1Yham6gECf](https://www.bilibili.com/video/BV1Yham6gECf/)，aid 117370064668534，2026-10-02 16:13:21（北京时间）发布，状态“开放浏览”，105 s，1920×1080，copyright = 2（转载），已在合集「Claude Code相关」（season 9223239）里，是第 2 集（前面是第 1 期 Claude mod）。接口核对过：标题、两张封面（`cover` 和 `cover43` 是两张不同的图，打开看了：16:9 / 4:3 都是中文标题版）、标签 10 个、来源栏、合集。
- **标题**：Anthropic设计师教你如何使用Claude（24 字，用户给的原话，没改）。
- **转载信息**：这版投稿页（2026-10）没有单独的“类型：自制 / 转载”，转载是在“创作声明”里选“内容为转载”，选完才出现“转载来源”输入框（≤ 200 字，写了 122 字）：转自 https://www.youtube.com/watch?v=NzcRprKWbD8（Claude 官方 YouTube 频道，2026-10-01，原标题《Make presentations with Claude Slides》）。**找来源**：用户没给链接，我先 WebSearch 找到 Claude 官方频道那条《Make presentations with Claude Slides》，再在浏览器里打开核对：发布 2026-10-01（太平洋时间）、时长 1:45（105 s，我们的成片 104.16 s）、描述写的是 “Nate, a designer at Anthropic, talks through an idea on a walk and then turns it into a deck”，和我们字幕里的内容一致。封面上的 “How an Anthropic designer uses Claude Slides” 是缩略图文字，YouTube 标题是另一句。
- **封面**：点“添加封面”进“封面制作”对话框：勾“双比例同步改动” → 上传 `制作/04_封面/封面_选定_16x9.png`（两个比例都变成它）→ 取消勾选 → 点“首页推荐封面（4:3）”→ 上传 `封面_选定_4x3.png` → 用 JS 点 `div.button.submit`（“完成”）。插件的 `file_upload` 对封面小图（150 KB）没问题。
- **标签**（10 个）：Claude Slides / Anthropic / AI做PPT / 设计师 / 语音备忘录 / AI工具 / 中英字幕 / 人工智能 / 效率工具 / claude。B 站自动填的“英语 / 短片 / 学生作品”删掉了（点每个标签的 `svg.close`）。**大写的 “Claude” 被拒**（弹出提示），点推荐标签里的小写 “claude” 才加得上；每个标签要请求校验（提示“标签正在请求校验中”），连着敲会丢，每个后面等 2 s。
- **分区**：人工智能（接口里 tid 231「计算机技术」，和第 1 期一样）。**创作声明** = 内容为转载（没选“含 AI 生成内容”：画面和声音是原片，AI 只翻译了字幕）。
- **简介**（479 字，接口里因为 B 站在前面拼了来源变成 602）：转载来源和链接、这条讲什么（Nate 散步录语音备忘录，再让 Claude Slides 整理成幻灯片）、关于这个版本（画面声音是原片、英文是转写校对、中文是 Claude 翻译、封面把英文换成了中文）、版权声明。用 Quill 的 `setText(text, 'user')` 填进去。
- **没做**：GitHub release（别人的视频，不建）；没挪目录；片头片尾没加（转载别人的视频，用户没说要加）。
