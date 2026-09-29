# 踩过的坑（第 1 期）

遇到报错或怪现象先查这里。新踩到的坑也补在这里。

## 配音

| 现象 | 原因 | 做法 |
|---|---|---|
| 识别结果把“山田凉”听成“善天良”、“鲸鱼娘”听成“金鱼娘”、Claude 听成别的词 | 识别模型的问题，不一定是念错 | 分数只作参考，专有名词请用户听 |
| `tts_api.py` 报 401 / 402 | key 不对 / 余额不足 | 401：停下告诉用户，key 由用户自己在用户环境变量 `FISH_API_KEY` 里改。402：不替用户充值，改用网页版（用户 Plus 账号，S1，整期一次，voice.md「备用：网页版」） |
| 刚设好 `FISH_API_KEY`，终端里 `$env:FISH_API_KEY` 还是空的 | 已经在运行的程序拿不到新设的用户变量 | `tts_api.py` 会直接读注册表里的用户变量，不用重启；检查时只看“有没有 / 长度”，不打印 key |
| 想用更大的识别模型复核专有名词，结果先下载了 1.6 GB（2026-09-27，`faster-whisper-large-v3-turbo`） | 本机缓存不完整时，按名字加载会自动从 Hugging Face 下载 | 临时复核用 `WhisperModel(名字, local_files_only=True)`，没有缓存就报错而不是下载；要下载先问用户（文件名、来源、大小） |
| 生僻字（第 4 期的“夯”）怎么念都识别不出来；给识别器加了含“夯”的提示词后，念成 hēng 的也被写成“夯” | small 模型词表里几乎没有这个字；提示词会把相近的音都拉成提示里的字 | 复核读音：large-v3-turbo（`local_files_only=True`）、**不给提示词**、按 `配音/segments/` 切好的句子逐段听写，只看含这个字的几段（第 4 期 `配音/_试读/check_hang.py`）；仍拿不准就请用户听 |
| “我是它的拟人”听起来像“女人”（第 4 期 v1） | 两个字连读、s1 的 n / l 不分明 | 台词避开“拟人”，改说“我的原型就是它”；这类容易听岔的词在试读里先听 |

### 网页版配音（API 余额不足时的备用）

2026-09-28 起 API 余额不足（402）时改用网页版，用户已开 Plus（额度和单次长度更大，整期一次生成，模型选 S1），步骤见 voice.md「备用：网页版」。下面是第 1、2 期免费账号时的经验：第 1、2 期是用 Claude in Chrome 插件操作 Fish Audio 网页版做的：免费账号只能用 S1、单次 500 **字节**，`chunk_voice.py`（不带 `--whole`）按场景 ≤480 字节分批，每批 2 个版本，从插件的网络请求里拿任务编号，下载 `platform.r2.fish.audio/tasks/<日期>/<编号>.mp3`（`fetch_check.py --urls`），出现播放器后「生成语音」按钮会移位（改用编辑框里 Ctrl+Enter），Chrome 会拦截同一网站的连续自动下载，插件单次调用约 45 秒上限、偶尔断开。2026-09-27 用户要求以后改用 API（分批生成时各批之间音色有差别）；网页版只在 API 余额不足时用。

## 字幕

| 现象 | 做法 |
|---|---|
| 英文单词被拆到两行、出现一两个字的碎行 | `build_timeline.py` 的断行按“原子”（连续的英文、数字、路径不拆）和显示宽度（ASCII 算 0.55）处理，单行 ≤20 宽，碎片合并；不要手改 timeline |
| 第二行以“”一句话，就把AI……”开头（右引号、右括号、句读跑到行首），或者一行以“（结尾（第 2 期 S02-02） | 2026-09-27 起断行按避头尾：”’）》」』】、，。！？；：… 跟在上一行末尾，“‘（《「『【 挪到下一行开头，挪完单行仍 ≤20（放不下就在别处断）。旧时间轴重跑 `build_timeline.py` → `mix_audio.py` 就好（段的时间、口型不变） |
| 一行超过 20 宽（以前一整句不到 22 宽就不拆，碎行合并后最多 24 宽） | 现在严格 ≤20：超宽的一句在最好的断点拆开（句读后 > 中英文交界 > 「的」后 > 英文词之间 > 汉字中间），碎行并不进就把两行重新平分。只有一个不能拆的英文词 / 网址本身超过 20 宽时例外 |
| 屏幕上两行字幕被粘成一行、词之间的空格没了（“GeneralIntelligence”）或行尾的，没了 | 引擎 core.js 会把「≥18 个字符、以英文 / 数字结尾」的一行和「以英文 / 数字开头」的下一行粘起来（给第 1 期旧时间轴里被硬折断的单词用的），粘的时候不加空格。现在的 build_timeline 不会在这种地方断行；老的时间轴重跑 build_timeline |
| 多词术语（Artificial General Intelligence、API Key）被断行拆开，两半都不标橙 | build_timeline 把引擎内置术语和 `episode.json` 的 `terms` 当成不能拆的整体（改了 terms 要重跑 build_timeline） |
| 中文术语后面紧跟英文时不标橙（「生成式预训练Transformer」里的「预训练」） | 旧引擎对所有术语都要求两侧不是英文字母；现在只有英文 / 数字那一边要求词边界，中文那一边按字面匹配，长的先标、不和已标的重叠。已有的期用 `new_episode.py --update-engine` 更新引擎 |
| 字幕时间和声音对不上 | 字幕按 `alignment.json` 的实际时间重新计时；改了配音一定要重跑 `segment_audio.py` 和 `build_timeline.py` |
| 以“。”“”结尾的字幕看起来偏左十几像素 | 全角标点的字形只占字框的一半；引擎把行首 / 行尾的全角标点做了悬挂（core.js `subHTML` + style.css `.hr/.hr2/.hl`），实测 140 行字幕的可见文字中心都在 x = 960 ± 3 px。不要删掉这几条样式 |

## 混音

| 现象 | 原因 | 做法 |
|---|---|---|
| 片头片尾的音乐忽大忽小、正片 BGM 被抽吸 | 单遍 `loudnorm` 是动态模式 | 两遍线性 loudnorm（先测量，再带 `measured_*` 和 `linear=true`） |
| 片头片尾太安静（第 1 期一度 -36 dB） | 片头片尾只有音乐，BGM 被当成背景压低了 | 片头片尾处 BGM 抬高 16 dB，进出正片各 1.2 秒渐变，结果约比人声低 7 dB |

## 画面

| 现象 | 做法 |
|---|---|
| 背景太亮、抢内容 | 调低 `episode.json` 的 `bg_alpha`（默认 0.22）、加大 `bg_blur`；第 1 期的明亮 Q 版图用过 0.30 / 9px |
| 用户要纯白（纯色）背景、不用图片（第 3、4 期 2026-09-28） | **现在是引擎开关**（同一天用户：“白底做成引擎开关，以后默认白底”）：`episode.json` 的 `"bg_color": "#FFFFFF"`，`new_episode.py` 默认写好（`--bg-color none` 不写），改了重跑 build_timeline → sync_assets。引擎自动做：`#bg` 整层涂色、不画图（开头 0.8 s 从深藏青淡入）；浅色主题——徽标、`.hdr`、`.note`、`.bLab`、`.chip.line`、步骤条、开场大字、疑问卡标题、总结落款换深色，`c.title` / `c.bigWord` 后面的深色光晕和 `#barShade` 去掉，卡片阴影减轻，目录保留深色底板（.9），字幕不变；`ENG.surfaceUnder`（`c.label` / `c.bracket` 自动配色）和 `check_layout.py` 的底色按背景色算（`ENG.BASE`）。scenes.js 里还要自己管的：直接压在背景上、自己写了 `color: 'var(--paper)'` 或浅色 rgba 的字和箭头（按 `ENG.LIGHT` 换）；深色半透明的底压在白底上发灰，换实心色（第 4 期榜单）；深色字的章节标题从中间缩到顶部那 0.6 s 会压过深色内容（第 4 期榜单），让那块内容晚 0.5 s 亮。第 3、4 期是开关出现前在各自 scenes.js 开头「白底」一段做的（它们的引擎副本是开关出现前的，不用动；要给它们换新引擎，先抽帧核对，scenes.js 里那一段可以删掉）。封面不跟它走：照旧用背景图（第 3 期用户：“封面背景不要变”）；要纯色封面在 cover.json 写 `"plain": "#FFFFFF"`（第 4 期） |
| 白板版 check_layout 报 `hand-late`（场景淡出时这行字还没写完） | 一个汉字约 0.3 秒；场景比声音早 1 秒淡出。这行改短（≤ 14 字）、提前到上一句写，或挪到下一场；组件在窗口太短时已经自动写快，别再手动调 vmax（写太快不像手写）。第 3 期分镜草稿试出来的：一章最后一句才开口的 18 字说明写到了场景结束后 2.6 秒 |
| 白板版 check_layout 报 `hand-missing` / sync_assets 报「手写笔画数据里没有这些字」 | hanzi-writer-data 只有汉字，标点是 hand_glyphs.py 里手画的（已有 ，。、：；！？（）“”《》—…·≤≥～→×✓「」『』【】｜①–⑳）。别的符号换成有的写法，或那一处用印刷体小字（`.bNote`） |
| 白板版一页最后一句的字没说到就被擦了；章末结论比声音早消失（第 3 期白板测试 D1 / C1） | 画面整体早 1 秒，照声音时刻擦板就早了 1 秒。章与章之间引擎已经处理（boardPlan：标题早擦、内容说完再擦）；同一章里翻页用 `c.flip(这一页最后一句)`，这一页 `until: f.out`、下一页 `at ≥ f.in`。check_layout 报 `hand-short` 就是这种情况 |
| 白板版疑问擦掉后空板、目录灰字淡入，没有衔接（第 3 期白板测试 C2） | 已改：疑问在最后一句快说完时一问一问飞进目录对应的行（tocInTime = 最后一句结束前 0.1 s），目录同时出现，接着写下一章标题。scenes.js 里不用再画指向目录的箭头 |
| check_layout 0 issues，画面上内容却互相压（第 3 期白板测试 C4） | 已加 `overlap` 检查（手写字、印刷小字、卡片 / 代码卡 / 窗口 / 节点 / chip 两两比）。放在别的元素里面的不算，卡片压卡片不算 |
| 卡片版的旧期（第 1–4 期）想换成白板版，以为改开关就行 | 开关只把标题、疑问、结论、要点、总结这些组件换成手写。自己搭的卡片、表格、流程图照旧是印刷体；旧版面的坐标（内容中线在舞台 x 1150）放进居中版面也会偏。第 3 期是按白板写法重写了 scenes.js（约 800 行，只参考卡片版的内容）。步骤见 assemble.md「局部返工」 |
| 技能大改以后（例如白板版上线），不知道文档够不够用 | 第 3 期白板测试的做法：<br>① 在副本期里，让子任务**只看技能文档**写 scenes.js，读到哪里不懂、去翻了源码，都记下来（文档缺口 / 组件问题 / 画面问题三张表）；<br>② 整片 4 路出片；<br>③ 看每章最后一句、疑问 → 目录、翻页、片尾这几处过渡帧；<br>④ 查左边缘黑点和响度（−16 LUFS）；<br>⑤ 问题回报给改引擎的会话，改完在同一个副本上复测。<br>记录见 `docs/ai/context/20260928-175836-yuanlai-board-skill-test-ep03_CN.md` |
| 白板版画一个框，出来一大块黑 | `c.handNode` 的 `w` 是框宽，框线粗细是 `pen`；`c.handRect` 的 `w` 才是线粗。第 3 期自测时 board.js 把两者混了，已修 |
| check_layout 报 `overflow-x` / `outside`：给名字卡加高亮框、小标签后 | 框和标签放在名字卡里面，被当成超出名字卡 | 做成名字卡旁边的独立元素（同一个父元素，按名字卡的位置算坐标，`zIndex` 压在上面） |
| 角色左右反了（泪痣、发夹换边；鲸鱼娘的蝴蝶结、尾巴跑到左边） | 永远不要镜像；需要朝左的动作就别用 |
| 画面上是山田凉，可这期该是鲸鱼娘（或反过来） | `episode.json` 没写 `presenter`（= 山田凉）或 `frames` 指错：用 `new_episode.py --presenter` 写的整段，看 `sync_assets.py` 打印的「讲解员」那一行；改完重跑 sync_assets |
| `sync_assets.py` 报「讲解员「鲸鱼娘」缺……」 | 她的帧目录里还没有这些 key：等帧画完；只出草稿就 `sync_assets.py --frames <已有的帧目录> --allow-missing`（不改 episode.json；缺帧的动作退回待机，正式出片前补齐），然后 `assemble.py --no-sync` |
| `sync_assets.py` 报「帧目录不存在」/「没有 anims.json」/「没有待机帧」 | 以前 `--allow-missing` 在这种情况下会默默写出空的角色清单，画面上是一个占位小人；现在一律报错退出。按报错里给的命令用 `--frames` 换成同一个素材包里已有的帧目录（例如 `角色/大肥鱼像素素材包/素材`），不要再做一份改了 frames 的 episode.json 副本 |
| 章节标题的编号不对：一个问题跨几章，每章都显示「二、」 | 旧的 `c.autoTitle` 按「第几个问题」编号。现在大字直接用台本场景的 title（「三、学会思考」），`PART 0N · 第N个问题` 那行按所属问题，不属于问题的章节没有这行；scenes.js 里不用再写 `text: c.sc.title` |
| `c.label` / `c.bracket` 的字放在纸白卡片上看不见（纸白字配纸白底） | 旧引擎标签默认纸白色。现在按背后的底色自动选（浅底墨黑 / 灰，深底纸白，`kind: 'o'` 橙色），`on: 'light'\|'dark'` 或 `color` 可以手动定；`check_layout.py` 会报 `low-contrast`（文字和背后底色对比度 < 1.6）。scenes.js 里不用再写 `.label.style.color = 'var(--ink)'` |
| 同一时刻的静帧，用不同的 `--stills` 列表渲染两次，进度条 / 背景里有几个像素不一样 | 和渲染时跳转过哪些时刻有关（浏览器光栅化），不是画面内容变了。新旧版本对比时要用同一份时刻列表、同样的顺序渲染；成片是逐帧顺序渲染，不受影响 |
| 新旧逐像素对比时，从某一刻起连续一段帧有几个像素不一样（2026-09-27：进度条圆角、片头的线条），单独重跑又完全一样 | 同时开着好几个 Chromium 任务（对比脚本、抽帧、check_layout 一起跑）时，浏览器中途换了光栅化方式。逐像素对比要单独跑，不要和别的渲染并发；有差异先单独重跑一次再下结论 |
| 2340 宽的画面里，用 `getBoundingClientRect()` 量出来的位置画东西，偏右 210 px | 那是页面（画布）坐标；scenes.js 的坐标是 1920×1080 内容舞台的，减 `ENG.OX` 才对（`c.ringOn` 已处理）。和目录有关的用 `ENG.tocRect()` / `ENG.safeTop()`，它们已经是舞台坐标 |
| `check_layout.py` 在疑问卡飞进目录那一刻报 `intrudes toc` | 设计如此（卡片飞进目录）。现在这几行标成 `expected (question card flying into the TOC)`，不计入 issues；飞入时段以外压到目录的才要改 |
| 2340×1080 的期，静帧 / 成片还是 1920 宽 | `timeline.json` 里没有 `episode.canvas`：episode.json 加了 `canvas` 之后没重跑 `build_timeline.py`（sync_assets 会提醒，assemble 会停下） |
| render.py / render_parallel 报 `page is 1920px wide but the frame is 2340px`（退出码 2） | 时间轴是 2340，但本期 `制作\engine\` 还是改尺寸以前的模板（页面只有 1920 宽，右边会空一条）：`new_episode.py --update-engine <期目录>` 后重跑。片头片尾页面太旧也会这样报 |
| 放大后发糊 | 只用最近邻整数倍（`image-rendering: pixelated`） |
| render.py 退出码 2 | 页面报错、字体或文件加载失败（`failed to load file:///…` 带文件地址，见「渲染与合成」第 2 期那条），看它打印的错误；字体只用 `素材\字体\fonts.css` |
| 渲染画面和预期时间不符 | 页面里用了 rAF、setTimeout、Date.now 或 CSS transition；一律改成由 `renderAt(t)` 计算 |
| 画面卡片和台词错位 | scenes.js 写死了秒数；改成按段号 / 台词短语取 `segments[].start` |

## 渲染与合成

- 正片并行数：2026-09-28 用户定：所有渲染统一 4 路并行（assemble.py / render_parallel.py 默认 4）。以前用 10 路（14 核机器，约 2.5 分钟渲染 6 分钟正片），但两个会话同时各开 10 路时内存耗尽、渲染卡死（见下面 2026-09-28 那条）。
- 各段先统一编码参数（30 fps、x264、bt709），再用 concat 分离器直接拼接。
- 只调 BGM 音量时用 `assemble.py --skip-main`，画面不用重渲。
- 2026-09-27 起视频是 2340×1080（`canvas`）：assemble 直接按 canvas 原生渲染片头片尾（页面自己居中、铺满全宽），不用 1920 渲染再补边或拉伸。
- 2340 宽的视频左边缘每隔 72 行有一小段黑线（x 0–4，纸白底上很明显，深色底上不容易看出来）：ffmpeg 8.0 用多线程滤镜把 JPEG 截图（yuvj420p）转成 yuv420p 时的 bug（1920 宽没有；PNG 管道、H.264 重编码没有）。`render_parallel.py`、`add_to_video.py`、`render.py -o` 的 ffmpeg 现在都加了 `-filter_threads 1`（x264 照样多线程，速度不受影响）。自己另写的「Chromium 截 JPEG → ffmpeg → x264」管线（例如从 render_parallel 复制出去的版本）也要加。
- `add_to_video.py` 同一个视频跑两次，成片逐帧 md5 可能不一样：它的开页方式（非整数 / 2 倍缩放）每次启动浏览器可能整帧差 ±1 个色阶。判断版面有没有变，比截图、看最大差值（≤1 就是这种噪声），不要比 md5。
- 2026-09-27 技能联调：10 路并行时有一路 Chromium 在 `Page.screenshot` 上卡了 30 s 超时退出，旧版 render_parallel 没检查，成片短了 32 秒（330.6 s / 应为 362.4 s）还照常输出。现在 render_parallel 会重启浏览器从卡住的帧续渲、检查每段帧数，assemble 再核对正片帧数和成片时长。看到 `restart browser, resume` 是正常的自愈；看到 `FAILED` 就重跑 assemble.py。
- 2026-09-27 第 2 期：正片 11556 帧都渲完了，assemble 却停下——10 路里 9 路报 `PAGE ERRORS: ['Failed to load resource: net::ERR_FAILED', …]`（每路 7–22 条，共 143 条，不带文件名），另一路 `Page.goto` 30 s 超时。原因：引擎开页时预加载全部角色帧（鲸鱼娘 115 个动作、约 1300 张 PNG；山田凉只有 20 个），几路 Chromium 同时加载、机器又忙时，个别 file:// 请求偶发失败；旧引擎把失败的图当成空图不画，那次的 main.mp4 逐帧比对有 15 帧角色整个没了或只剩一块眼睛补丁（part_06 `head_nod_m0#0`、part_07 `head_tl_m2#0`）。事后单开、10 路、16 路同开都没再复现，和当时机器上同时跑的任务有关。现在：引擎 `loadImg` 失败后按 0.1 / 0.3 / 0.8 / 1.5 / 3 s 重试（`?r=N`，同一个文件，像素不变），记在 `window.__IMG_RETRIED__` / `__IMG_FAILED__`，6 次都失败才 `console.error('image failed: …')`；`render.py` 的 open_page 按文件地址核对，引擎救回来的不算报错（打印一行 `image loads failed and were retried by the engine … all recovered`），救不回来的报 `failed to load file:///…`（带地址）；片头片尾这类没有重试记录的页面照旧每条都算。render_parallel 各路相隔 0.7 s 启动（`--stagger`）；第一次开页就超时的那一路，重启后的片段直接当 part_NN.mp4（以前会被当成缺帧、整段重渲）。已有的期 `new_episode.py --update-engine` 才有重试。看到 `failed to load` 先看那个文件在不在：在就是偶发，重跑 assemble。
- 2026-09-28 两个会话（第 3、4 期）前后脚各开了 `assemble.py --workers 10`：20 个 2340 宽的无头 Chromium 同时渲染，几分钟后内存和页面文件耗尽（`WinError 1455 页面文件太小`、`MemoryError`、x264 `malloc … failed`），各路反复 `restart browser, resume` 后停住不动，输出目录不再更新。处理：先用 `ListAgents` 或进程列表（`Get-CimInstance Win32_Process`，命令行带期目录）确认有没有别的会话在渲染；有就轮流渲染（对方跑完发消息再开），或者两边都降到 `--workers 4` 以内（本机 32 GB，那次空闲物理内存只剩约 4–5 GB）。卡住后用 `taskkill /PID <assemble 的 PID> /T /F` 只结束自己那棵进程树，把残缺的 `制作/build/main_parts` 移到本期 `_旧稿/`，再重跑 assemble。

## 浏览器与投稿页

| 现象 | 做法 |
|---|---|
| 插件上传视频失败 | 单次上限 10 MB；视频由用户手动上传 |
| 本机起服务器让页面取文件，Chrome 弹“访问本地网络”，页面卡死 | 不要这么做；权限提示请用户点「阻止」后刷新 |
| 标签“Claude”加不上 | 话题专用标签，换别的词 |
| 填完标签分区变成 vlog | B 站自动改分区；最后再把分区改回「知识」 |
| 新建合集时名字计数不刷新 | 对 input 派发 `input`、`change` 事件 |
| 用户说“看我浏览器里打开的网页 / 公众号”，`tabs_context_mcp` 却只有一个新标签页（第 3 期） | 插件只能看到它自己标签组里的标签页，看不到用户自己开的；请用户把链接贴过来（或把那几个标签拖进 Claude 标签组），在插件新开的标签页里读。微信公众号文章用 `get_page_text` 能读到全文 |
| 按截图坐标点输入框，结果点空、ctrl+a 选中整页（第 3 期投稿页标题框） | 截图和点击之间页面滚动了。输入框一律 `find` 拿 ref → `scroll_to` → 点 ref，再输入；输完用 `javascript_tool` 读回 value 核对 |
| 投稿后线上简介是空的（第 3 期：填写时 `getText()` 读回 559 字，用户点了投稿，接口 `desc` 长度 0；2026-09-28 晚才发现） | 原因没查实（编辑器里有字、表单数据没更新，或提交时没带上）；第 4 期和日报同样用 setText 写的都正常。以后：`setText(简介, 'user')` 之后看简介框的计数 `N/2000`；用户投稿后按 bilibili.md §9 用接口 `x/web-interface/view` 核对 `desc` 长度；为空就告诉用户，用户同意后在编辑页补回（要重新过审） |
| 已发布稿件的编辑页：截图超时、`find` 看不到封面弹窗、按截图坐标点偏（第 3 期 2026-09-28） | 用 `javascript_tool` 读状态、点按钮（「封面设置」`.cover-module-main .edit-text`；「完成」是 `.cover-editor-content-right-bottom` 里的 `div.button.submit`）；「更换视频」由用户自己点。见 bilibili.md §10 |

## 文件操作

- 用户装了 dcg 钩子，`rm -rf` 等删除命令会被拦：不要绕过，改成移动到 `_旧稿\`。
- Windows 下 `~/.claude` 深层路径可能超过 MAX_PATH，Python 打不开时改用 `cat` 管道。会话临时目录（scratchpad，路径本身就有两百多个字符）也一样：脚本要读的文件（episode.json 副本、片尾清单）和临时文件都别放那里，放在本期 `制作\build\` 或视频旁边。换讲解员帧目录用 `sync_assets.py --frames`，不用做副本；`add_to_video.py` 的临时文件放在输出文件旁边（`_tmp_add_to_video_*`，跑完自动清掉）。
- 往 Bash heredoc 里嵌 Python 补丁容易转义出错；改代码用 Edit，或整文件重写。第 3 期两次遇到：heredoc 里是很长、带中文引号（“”）的 Python 脚本时，Bash 报 `unexpected EOF while looking for matching` 整段没执行；改成用 Write 工具把脚本写到会话临时目录再 `python 脚本.py`（脚本本身放临时目录没问题，它要读写的期目录文件用绝对路径）。
- **已发布的期要出新版本**（第 3 期 2026-09-28 晚：卡片版 → 白板版）：
  - 新版本全部在副本里做完：`_skilltest` 下用 `new_episode.py --dest` 建同名期，复制台本、配音、episode.json 里的目录 / 章节 / terms / 片尾清单。
  - 等用户在 B 站真的换了（提交修改），再把本期目录换过来：旧的移进本期 `_旧稿\`，episode.json 在原文件上改。
  - 用户改主意就不动本期目录。第 3 期这次先搬进了本期目录，用户随后说「这期已经发布了，先不动」，又还原成和线上一致的卡片版。白板版留在本期 `_旧稿\白板版_未发布_20260928-191806\` 和 `_skilltest\board_ep03\`。
- 同一台机器上常有别的会话在做别的期（2026-09-28 第 3、4 期同时做）。暂存目录按期分开（`_staging/epNN/`），文件名带本期后缀；给子任务指定输出文件前先看那个文件是否已存在——第 3 期的审校子任务写 `_staging/ep03/review_fact.md` 时覆盖了第 4 期会话同名的审校，靠那个会话的记录才原样找回。渲染也要错开（见「渲染与合成」）。
