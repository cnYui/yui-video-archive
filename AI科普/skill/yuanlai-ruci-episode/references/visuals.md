# 画面：背景、角色动作、scenes.js

引擎是一个 HTML 页面（`制作\engine\index.html`），由 `render.py` 逐帧确定性渲染：每帧暂停所有动画、定位到时刻 t，再调用 `window.renderAt(t)`。时间轴 `timeline.json` 注入为 `window.__DATA__`。模板来自 `assets/engine-template/`，每期只新写 `scenes.js`。

## 画面尺寸：画布和内容舞台

- 视频画面 = **画布**，尺寸是 `episode.json` 的 `canvas`（第 2 期起 **2340×1080**，19.5:9，用户 2026-09-27 要求；没写 = 1920×1080，第 1 期）。封面不受影响，照旧 16:9 + 4:3。
- scenes.js 画在 **1920×1080 的内容舞台**上，舞台在画布里水平居中（2340 宽时在画布 x 210–2130）。**坐标照 1920×1080 写**，和第 1 期一模一样；y 80–900。水平方向看 `episode.json` 的 `layout`：`"center"`（2026-09-28 起新一期默认）内容以舞台 x 960（`ENG.CX`，画布中线，和字幕同一条线）左右对称；没写（第 1–4 期）内容区舞台 x 440–1860。
- 全局层（core.js）铺满整个画布：背景和暗角、左上徽标（贴画布左边）、右上目录（贴画布右边）、左下讲解员（贴画布左边）、字幕（按画布居中）、章节进度条（全宽）、片尾淡出。scenes.js 不碰它们。
- 结果：2340 宽时讲解员和内容区之间的空当从约 70 px 变成约 280 px，目录挪到画布最右边（舞台 x ≈1750–2090），内容区左右都更松；字幕带在舞台上的位置（x 340–1580）和 1920 时一样。

## 版面（每期固定，不要改）

| 区域 | 内容 |
|---|---|
| 左上 | 只有「原LAI如此 #NN」（NN = `episode.number` 两位），贴画布左边。不再有“配音：AI 合成”（用户 2026-09-27 要求删除；AI 合成声明写在简介和创作声明里） |
| 右上 | 「本期目录 CONTENTS」卡片（第 1 期样式），贴画布右边：`question_scene` 最后一句结束时由疑问卡飞入；讲到哪题，哪题橙色编号 + 左侧橙竖条 + 稍放大；讲完打橙色 ✓、文字变暗、放提示音；补充章节期间都不高亮 |
| 左下 | 本期讲解员（山田凉或鲸鱼娘，像素形象）×5 最近邻放大，贴画布左边，全片同一位置同一大小，**不镜像** |
| 内容区 | 居中版面（`layout: "center"`，新一期默认）：以舞台 x 960（`ENG.CX`，画布中线）左右对称，一般不超过 x 190–1730（2340 宽；1920 宽时 x 380–1540 以内才不碰讲解员和目录），y 80–900；章节标题收起后在顶部正中。旧版面（没写 layout）：舞台 x 440–1860，标题收到左上。知识卡、代码卡、流程图、对比表、步骤条都在这里 |
| 底部 | 字幕：按整个画布水平居中（中心 x = 画布宽 / 2：960 或 1170），在进度条上方；Noto Sans SC 700、纸白字墨黑描边，术语橙色。白板版（新一期默认）：56 px 墨黑字白边，单行最宽 1500 px |
| 最底 | 《孤独摇滚！》四色章节进度条（波奇粉 #F2A0BD、虹夏黄 #F6C945、凉蓝 #4A6FD0、喜多红 #E2463F），整片时间、画布全宽，标注“0:33–1:22 章节名”，吉他拨片播放头 |
| 背景 | 默认纯白（`episode.json` 的 `bg_color`，2026-09-28 起新一期默认 `#FFFFFF`；浅色主题见下面「白底」）。没写 `bg_color`（第 1、2 期）：按章节切换，0.8 s 交叉淡化，cover 铺满整个画布，叠在深藏青 #1B2340 上，不透明度 `bg_alpha`（默认 0.22）、模糊 `bg_blur`（默认 10px）、暗角 |

视觉语言沿用片头片尾的“终端小票”：纸白 #EDEAE3、墨黑 #141414、橙 #FF4F1A（重点、箭头、勾）、红 #D8342A（只用于禁止 / 报错）、灰 #6E6A63。动效克制：卡片 0.3–0.4 s 淡入加轻微上移，列表逐条出现，没有弹跳、闪烁、抖动、推拉镜头。

## 背景

- **默认白底**（2026-09-28 用户：“白底做成引擎开关，以后默认白底”）：`new_episode.py` 在 `episode.json` 写 `"bg_color": "#FFFFFF"`，视频里不用背景图，`backgrounds` 可以空着。引擎自动换浅色主题：徽标、章节标题、`.note`、进度条章节名、`.chip.line`、步骤条、开场大字、疑问卡标题、总结落款换深色；标题和大字后面的深色光晕、`#barShade` 去掉；卡片阴影减轻、加细边；右上目录保留深色底板；字幕不变；`c.label` / `c.bracket` 的自动配色和 `check_layout.py` 的对比度按白色算。scenes.js 里要自己管的只有：直接画在背景上、自己写了浅色的字和线（`color: 'var(--paper)'`、`rgba(237,234,227,…)`）——写成 `ENG.LIGHT ? 'var(--ink)' : 'var(--paper)'`；深色半透明的底（`rgba(20,20,20,.4)` 之类）压在白底上会发灰，要实心就写实心色（第 4 期榜单）。深色字的章节标题从中间缩到顶部那 0.6 s 会压过深色内容（第 4 期），让那块内容晚 0.5 s 亮。
- 封面：白板版的封面也是白底（`make_cover.py` 按 `style` 选白板模板；用户 2026-09-28 看了第 3 期白板封面：“可以，你用插件把封面换一下，视频内容也要换一下”）；卡片版的期照旧用背景图库里的一张。见 cover.md。
- 用户要图片背景时（第 1、2 期的样子）：`new_episode.py --bg-color none`，或删掉 `bg_color` 后重跑 build_timeline。下面几条都是图片背景时的做法。
- 背景图由用户提供，放在 `素材\背景图库\`（`NN_描述.jpg|webp`，编号续上）。开工时问用户这期有没有新图；不要自己上网找。
- 在 `episode.json` 的 `backgrounds` 里给每个章节指定一张（文件名）。相邻章节用不同的图；同一张可以在不同章节重复。片头片尾自带画面，不需要背景。
- 画面明亮、颜色很花的图（例如 Q 版贴纸、主视觉）更容易抢内容：放在内容少的章节（开场、总结），或者单独调低 `bg_alpha`。
- 抽帧检查：卡片上的小字、代码卡在任何背景上都清楚；背景里的人物脸不要正好在卡片边缘露出来。

## 讲解员与角色帧

- 每期一位讲解员，写在 `episode.json` 的 `presenter`（`new_episode.py --presenter ryo|whale`）。角色帧来自她的帧目录 `素材\<presenter.frames>\`：山田凉 `素材\角色\动作帧\`，鲸鱼娘（DeepSeek 拟人，素材包叫大肥鱼）`素材\角色\大肥鱼像素素材包\素材\动作帧\`。`sync_assets.py` 把这个目录的 `anims.json`（帧清单、动作注册表 `actions`、`patch_rects`、`anchor` 等几何）写进 `assets.js`。
- 两位讲解员用同一套动作词和帧 key（`reach_m0..2`、`idle_happy_m1`……），台本写法不变。引擎里和角色形状有关的几何（眼睛 / 腿补丁、头部偏移、特效偏移、站位、走入距离）先读她的 `anims.json`，缺了才用山田凉的值（`pipeline-contract.md` §5）。
- 帧还没画完：`sync_assets.py` 会写明“讲解员「鲸鱼娘」缺 xxx”并退出。出草稿用 `--frames` 临时换一个已有的帧目录（相对 `素材\`；不改 episode.json，也不用做 episode.json 副本），例如 `python engine/sync_assets.py --series D:/大疆/AI科普 --frames 角色/大肥鱼像素素材包/素材 --allow-missing`（那里只有待机、口型、表情）：缺帧的动作退回待机，开场走入没有 walk 帧时站着滑入，自动层缺帧的通道自动关掉。assemble 自己跑的 sync_assets 不带 `--frames`，草稿出片先手动跑上面这句，再 `assemble.py --no-sync`。正式出片前要补齐。
- 帧目录整个不存在（或没有 anims.json、没有待机帧 `idle_m0..2`）时 `sync_assets.py` 直接报错退出，加 `--allow-missing` 也不放行（以前会默默画一个占位小人）；报错里会写出同一个素材包里可以临时用的帧目录和完整命令。

## 角色动作

用户的要求（2026-09-27）：「拉炮保留」，而且角色要多一些讲解动作，“而不是简单单纯的站在那边读稿子”。同时仍然是科普视频：内容为主，不激烈切镜头、不频繁走动、不用和知识无关的角色梗，角色不镜像。所以动作分两层：

**1. 自动层（台本不用写）**：引擎按 `episode.json` 的 `auto_gestures` 自己加，幅度都很小。

| 通道 | 做什么 | 大约多少（倍率 1.0） |
|---|---|---|
| 手势 | 说话时手放胸前、合手、轻摊；卡片 / 列表条目 / 代码卡出现时朝内容轻摊并看右 | 约 6 个/分，其中四成左右是朝内容轻摊 |
| 点头 | 句末（。！）头低 1 px、半闭眼 | 约 3 次/分 |
| 看向内容 | 新内容出现、或停顿里，眼睛看右 0.6–0.9 s | 约 2 次/分 |

- 完全确定性（同一期渲染多少次都一样），碰到台本动作、开场走入、正片最后 1 秒自动让开；同一套手臂帧最多连续 2 次。
- 嫌多：先把 `auto_gestures` 改成 `{"gesture": 0.6}`，或 `{"nod": false}` / `{"look": false}` 关掉一个通道，不要去改规则；某一段要安静（例如安全警告的主句）写 `【动作：不动】`。改完重跑 build_timeline。
- 缺帧时对应通道自动关掉（控制台 warn 一次）；第 1 期那种没有 `episode` 的旧时间轴没有自动层。

**2. 台本动作**：写在画面说明里，`【动作：抬手】`、`【动作：数一@第一】`、`【动作：好耶@末尾】`、`【动作：摇头+认真】`。完整词表、默认时长和位置、上限见 `pipeline-contract.md` §4，帧和注册表见 §5。

**用多少**：以 `D:\大疆\AGENTS.md`「角色动作尺度」为准，按上一期用户的反馈定这一期的档位。第 1 期（走入 + 抬手 5 次）用户觉得偏保守；第 2 期档位（`epcommon.ACTION_LIMITS`，`build_script.py` 会数一遍并提醒）：

- 台本动作 20–30 个（约 12–18 s 一个），超过 35 警告；贴纸姿势、小跳、走入都算在内；一段最多 1 个（身体动作 + 表情算 1 个）。
- 大动作（挥手、数一/二/三、重点、思考、摊手、疑问、收到、好耶、小跳）全片 ≤ 12，相邻两个开始时间 ≥ 15 s。
- 贴纸姿势（疑问 / 收到 / 好耶）≤ 4、每章 ≤ 1、相邻两段不能都是贴纸；**好耶（拉炮）1–2 次，至少 1 次**，放在讲完一题或总结。
- 小跳 ≤ 1，只放在 gap（章节结尾或总结）；走动只用于开场走入，不让位。
- 挥手 ≤ 2（开场问好、结尾道谢，走入之后）；数一/二/三 只在台词真的在列举时用，按顺序成组，≤ 2 组；重点 ≤ 4；思考、摊手、叉腰、侧耳各 ≤ 3；竖拇指 ≤ 2；点头、摇头各 ≤ 6。
- 抬手、指这里、看右边、手放胸前、合手、表情不单独限数，受“一段 1 个”约束；同一个身体动作不连续 3 段。

**怎么选**（动作贴着台词走，宁可少一个也不要和台词无关）：

| 台词是 | 用 |
|---|---|
| 介绍右边的内容、列要点 | 抬手；要指到某一行、某个字段用 指这里；只让眼睛看过去用 看右边 |
| “第一……第二……第三……”真的在列举 | 数一 / 数二 / 数三（写 `@第一` `@第二` `@第三` 对准） |
| 关键点、“记住这一点”；“一定要……” | 重点；“一定要”写 `重点+认真` |
| 抛出问题、“为什么会这样？” | 边说边问用 思考；停顿里抛疑问用 疑问（贴纸） |
| “常有人说……”“你可能会问……”“听说……” | 侧耳 |
| 说到“我”“我们”“自己” | 手放胸前 |
| 平静说明、承上启下“接下来我们看……” | 合手 |
| 下结论、“答案就是它” | 叉腰（段首或 `@末尾`） |
| “对”“没错”“就是这样” | 点头 |
| “不是”“别这么做”“千万别把 Key 发给别人” | `摇头+认真`；主句要安静就再加一段 `不动` |
| “就这么简单”“看情况” | 摊手 |
| “这样就可以了”“推荐这么做” | 竖拇指 |
| 反常识的事实 | 吃惊；警告、注意事项用 认真（整段） |
| 讲完一题、操作成功、总结 | 开心（整段）；每期 1–2 次 好耶（拉炮），常写 `@末尾`；“记住了”“明白”用 收到 |
| 开场“大家好”、结尾“感谢大家” | 挥手（开场第 0 秒的 gap 写 走动 = 从左侧走入） |

- 贴纸姿势（疑问 / 收到 / 好耶）、小跳、走动不对口型，放在停顿或一句的末尾；其余动作照常对口型。
- 点头、摇头只在手放下时播放，不要和手势写在同一段。
- 不做：握拳、让位、打叉、捂嘴、指向上方、双手展开；和知识无关的角色表演（弹贝斯、吃草、借钱、怪人、睡觉、饿肚子）一律不用。

交付时告诉用户这期台本动作一共多少个、各是什么（`build_script.py` 会打印），以及自动层各通道的数量（`check_layout.py` 最后会打印 `ENG.autoPlan` 的统计），请用户评价多少是否合适，记进「角色动作尺度」表。

## 新动作帧

需要词表以外的动作时：先问用户。同意后按讲解员分别做：山田凉在 `素材\角色\动作生成器\`（`make_sprites.py` + 素材包部件的副本）里用现有部件拼；鲸鱼娘在她的素材包 `素材\角色\大肥鱼像素素材包\`（见它的 README）里生成。都只用画面右侧那只手、不镜像、只用调色板颜色。帧先输出到预览目录（山田凉：`make_sprites.py --out <目录>`，如 `_skilltest/actions_v2/frames_preview/`），给用户看原型图和样片：样片的期目录在 `episode.json` 写 `"sprites_extra": "<预览目录>"`（或 `sync_assets.py --sprites-extra <目录>`；叠加在本期讲解员的帧目录上，必须是同一个讲解员的帧），引擎就能从预览目录读帧。用户确认后才追加进她的帧目录（`anims.json` 只追加条目和注册表，已有帧不重写），同一批里在 `epcommon.ACTIONS` 加词、在 `pipeline-contract.md` §4–5 加一行，然后删掉 `sprites_extra`。原始素材包 `素材\角色\山田凉像素素材包\` 永远只读。

## 白板版（2026-09-28 起新一期默认）

用户 2026-09-28：“原LAI如此也用手写白板，字提前一秒出现，字幕也同步放大”（同一天《AI每日日报》已经改成白板版）；看过第 3 期的白板测试样片后：“就是这个风格的，没问题”。开关是 `episode.json` 的 `"style": "board"`：`new_episode.py` 默认写好，`--style cards` = 不写（印刷体卡片版，第 1–4 期）。旧一期要换成白板版：加这一项（和 `"layout": "center"`），`new_episode.py --update-engine <期>` 换新引擎，重跑 build_timeline → sync_assets，然后**重写 scenes.js**——卡片版自己搭的卡片、表格还是印刷体，旧版面的坐标（内容中线 1150）放进居中版面也会偏；步骤见 assemble.md「局部返工」和 lessons.md。已发布的期出新版本：先在副本里做完，B 站真的换好了再动本期目录（第 3 期的教训）。

### 样子
- 白底（没写 `bg_color` 也按白色），讲解员在左下角，右上目录是白卡片（顶部橙线），字幕 56 px 墨黑字白边、术语橙色，底部四色进度条照旧。
- 说到的要点边说边手写：黑色记号笔写字，黄色记号笔划波浪线、圈重点，橙色写编号、打勾、小横，红色画叉。印刷体只留小字（小标签、补充说明、出处、落款；`.bNote` 默认 26 px，手机上别再小于 24 px）。代码卡、示意窗口、手机、对比表照旧是印刷体卡片，`c.tape(el)` 贴两条胶带（左上、右下），像贴在白板上。
- 一页别写太满：手写 ≤ 5 行、印刷小字 ≤ 3 行（第 3 期测试：对比表 3 行 × 2 列手写加 8 行小字就偏满）。

### 时间：画面比声音早 1 秒
- `"board_lead"`（默认 1.0）：引擎把整个场景层提前（`renderAt` 用 t + LEAD 求场景），**scenes.js 照声音写时间，不要自己减**。字幕、口型、进度条、目录高亮和打勾（有打勾声）跟声音。
- **章与章之间**（core.js `boardPlan`，自动的）：这一章的**标题**照旧早 1 秒擦掉，下一章的标题早 1 秒写在旧结论上方；这一章的**内容**留到最后一句说完（+0.15 s）才擦；下一章的内容等旧内容擦完再出现（约晚 0.9 s），所以每章第一句别安排要紧的内容。最后一章不自己淡出，由片尾淡出盖住。
- **同一章里翻页**（要自己写）：画面早 1 秒，照声音时刻擦板（`until: 下一句.start`）会把这一页最后一句的字在说出来之前就擦掉（第 3 期测试 D1）。用 `c.flip(这一页最后一句)` → `{out, in}`：这一页 `until: f.out`（画面上在那句说完前 0.15 s 擦），下一页的东西 `at` 不早于 `f.in`。代价：新一页的第一样东西只比它那句早 0.1 s 左右，页里后面的照旧早 1 秒。
- **疑问 → 目录**（自动的）：白板版的 `ENG.tocInTime()` 是疑问场最后一句结束前 0.1 s；每一问缩小飞进目录对应的行再淡出，目录同时出现，接着就是下一章标题。`c.questionCards` 的 `at` 要给每一问开口的时刻：台词和问题原文不一样（“Jev到底是什么”）时，模板先找原文、再找“第一 / 第二 / 第三”，都找不到就挂到第 2、3、4 句——会挂错，自己用 `c.P(c.segId('S02-05'), '到底是什么')` 给。
- 写一个汉字要时间：正常笔速约 0.3 秒（约 9 笔，每笔至少一帧，加抬笔），写快时约 0.12 秒。给了写字窗（`c.hand` 的 `until`，组件自己算的窗口）写不完，**自动写快**；还超出 0.3 s 以上的，`check_layout.py` 报 `hand-slow`。一行尽量 ≤ 12 字，挂在这句话开头写；长行（≥ 10 字）写 2–4 秒，“早 1 秒”只对行首成立。
- 抽帧、check_layout 用的都是**声音时刻**：`render.py --stills 118.6` 看到的场景层是 scenes.js 里 119.6 的内容。

### 自动变成手写的组件（`board.js`，参数和返回值和卡片版一样）
淡出一律叫 `until`（和卡片版一样）；`c.hand` 的 `until` 是“写完的时间窗”，淡出叫 `out`。

| 组件 | 白板版 |
|---|---|
| `c.autoTitle` / `c.title` | 标题写在顶部正中（y 约 60–150），黄色波浪线，下面一行橙色小字 PART 0N；不再从中间缩上去，整章都在（章末按上面的规矩先擦）。内容从 y 250 左右开始 |
| `c.bigWord` | 开场大字手写 + 波浪线，上面橙色小字、下面灰色一行 |
| `c.questionCards` | 手写「你可能也想问」+ 编号问题，念到哪题写哪题；到 `ENG.tocInTime()` 飞进目录（见上） |
| `c.statement` | 手写 lead + 手写大字 main；main 里 `<span class="or">…</span>` 的字划黄线 → `{el, tr, main}`（`main` 是手写那行，可以 `c.handMark(st.main, i0, i1)`） |
| `c.pointList` | 橙色小字 kicker + 手写标题 + 细线 + 手写要点；`mark`：num 编号 / dash 小横 / check 勾 / x 红叉 / none；`sub` 是印刷小字，跟在这一条后面，放不下就放到下面；字号按 `fs × 1.25`（或直接给 `size`）；标题写完才开始写第一条 |
| `c.summary` | 手写「本期总结」+ 编号结论（副句印刷小字）+ 落款，整块以中线居中 |

### 自己画（`hand.js` / `board.js`；坐标是内容舞台坐标，居中版面以 `ENG.CX` = 960 为中线）
- `c.hand({text, x, y, size=64, align='left'|'center'|'right', at, until, out, color, maxW, pen, seed, parent, cue})`：写一行字。y 是这一行的中线，size 是汉字大小；`at..until` 是写的时间窗；`out` 是淡出时刻；`maxW` 超宽就缩小字号 → `{g, x0, y0, x1, y1, t0, t1, size, box(i0, i1), out(t)}`（`box` 是第 i0..i1−1 个字的墨迹外框）。
- `c.handText(html, x, y, o)`：同上，先去掉 HTML 标签，`<span class="or">` / `<b>` 的字划黄线（`mark: 'circle'` 改成圈）。
- `c.handMark(item, i0, i1, {kind: 'circle' | 'underline', at, dur, color})`：圈出 / 划出这一行的第 i0..i1−1 个字，跟这一行一起淡出。
- `c.handUnderline({x0, x1, y, at, dur=0.4, color, w=10, out})` 波浪线（默认黄色记号笔，压在黑字上不盖字）。
- `c.handEllipse({x0, y0, x1, y1, at, dur=0.45, color, w=9, padX, padY, out})` 圈住一个框（外扩按框高算，小字也不会盖到上下行）。
- `c.handArrow({x0, y0, x1, y1, at, dur=0.3, color, w=7, out})`、`c.handLine({x0, y0, x1, y1, at, dur, color, w=5, out})`。
- `c.handRect({x0, y0, x1, y1, at, dur, color, w=6, r=16, out})`：手画的框，`w` 是线宽。
- `c.handNode({x, y, w=300, h=140, text, sub, size=48, at, write, until, color, textColor, pen})`：框 + 框里手写字（流程图的节点）。**这里 `w` / `h` 是框的大小，线宽是 `pen`**；`write` 是框里的字写完的时刻（默认框画完后约 1 秒，写不下自动写快）；`until` 是整个节点淡出的时刻 → `{el, rect, text, x0, y0, x1, y1, t1, tr}`（接箭头用 x0..y1）。
- `c.handCheck({x, y, size=40, at, color})`、`c.handDash({x, y, len=28, at, color})`。
- `c.handGroup()` 建一个组，组件传 `parent: g`，最后 `c.T(g, {o: 1}).to(t, {o: 0}, 0.3)` 整组擦掉。
- `c.tape(el, k)`：`el` 是元素本身，例如 `c.code(...)` 返回值的 `.el`。
- `c.hand` / `c.handArrow` / `c.handRect` / 各组件会自己登记内容提示点（角色自动层会看过去）；`cue: false` 关掉。
- 例子：
  - 短的：模板 `scenes.template.js` 最后「常用写法速查」里的白板一段（两个 `handNode` + vs + 箭头 → `statement` 划线、`handMark` 圈字 → `c.flip` 翻页 → 贴胶带的代码卡 + 手写要点）；
  - 完整的一期：引擎模板里的 `scenes.board_example.js`（第 3 期白板版，约 780 行，只看文档写成、check_layout 0 issues；流程图、对比表、横条、圈重点、贴卡片、翻页都有；它自己的 `FLIP(段号)` 等于 `c.flip(上一句).out`）。

### 笔画数据
- 在 `素材\手写`（目录联接到 `AI日报\素材\手写`：hanzi-writer-data，Arphic Public License；EMS Tech 单线字体，SIL OFL），只读。
- `sync_assets.py` 把 scenes.js、board.js、时间轴、episode.json 里出现过的字都收进 `制作\engine\handdata.js`（第 3 期约 700 字、280 KB）。**scenes.js 里加了新的手写字，先重跑 sync_assets 再 check_layout**（assemble 自己会跑 sync_assets，所以只影响出片前的自查）。
- 没有笔画的字会在 sync_assets 的 `WARN` 里列出来，真要手写就会留空，check_layout 报 `hand-missing`。「」『』【】｜和 ①–⑳ 是手画补上的；“1” 加了一个钩，不会看成 “I”；汉字字距是字号的 0.96 倍（日报是 1.04）。

### 自查：check_layout.py 在白板版多查的
- `intrudes …: hand:…`：手写字的墨迹压到字幕、角色、目录，或出画布（飞进目录的疑问标成 expected）。
- `overlap: A × B`：内容互相压（手写字、印刷小字、卡片 / 代码卡 / 窗口 / 节点 / chip）；这一条卡片版也查。
- `hand-late`：场景淡出时还没写完。`hand-short`：写完后显示不到 0.8 s 就被擦（翻页没用 c.flip，或者写得太晚）。`hand-slow`：写快了也超出写字窗 0.3 s 以上。
- `hand-missing`：缺笔画。`phrase-miss`：`c.P` 找不到的台词短语（它会按兜底比例算时刻，并在控制台 warn；这一条卡片版也查）。
- 分镜草稿（模板里 `draft: true` 的 pointList）不查写字时间。

### 台本里怎么写画面说明
写「手写什么、画什么」，例如 `手写「Jev = 决策模型」，圈「决策」`、`画两个框 LLM / Jev，中间写 vs，箭头指向结论`、`贴一张代码卡（示意）`。一句一个要点，要手写的字短一点（一行 ≤ 12 字）；一章的结论放在最后一两句也没关系（会留到说完）。

## 写 scenes.js

起点：`new_episode.py` 已把 `scenes.template.js` 复制成 `制作\engine\scenes.js`（原样运行就是一份分镜草稿：开场大字、疑问卡飞进目录、每章标题卡 + 按段出现的画面说明卡、总结卡）。完整的第 1 期写法见同目录 `scenes.example.js`；每个组件的参数写在 `components.js` 各函数上方。全局层（背景、角色动作、字幕、进度条、徽标、目录）在 `core.js`，scenes.js 不碰它们。

**坐标系**：scenes.js 里所有 x / y 都是 **1920×1080 内容舞台**的坐标（`c.div`、`c.card`、组件的 `x/y`、挂在 `#scenes` 层上的全片常驻元素都一样），画布多宽都不用改。居中版面（`layout: "center"`）里组件不写 `x` 就以 `ENG.CX`（960）居中：`c.title` / `c.autoTitle` / `c.bigWord`、疑问卡、`c.statement`、`c.pointList`、`c.summary`、`c.compareTable`、`c.browser`、`c.phone`；自己摆的东西用 `ENG.CX - w / 2`，左右两栏就以 `ENG.CX` 为界对称摆（右栏不压目录用 `ENG.safeTop`，左栏不压讲解员）。`c.steps` 是贴右边的步骤条，位置不变。和目录有关的都用 `ENG.tocRect()` / `ENG.safeTop()` / `ENG.tocRowRect()`（舞台坐标，已经按目录在画布上的真实位置换算好），不要写死 1540 之类的数。极少数要用 `getBoundingClientRect()` 量位置再画东西时，页面坐标减 `ENG.OX` 才是舞台坐标（`c.ringOn` 已处理）。`ENG.CW` / `ENG.CH` 是画布尺寸，一般用不到。

```js
ENG.scene('S03', c => {             // c = 本场上下文
  const s = c.segs();               // 本场全部段；c.seg(0) 第 0 段，c.seg(99) 最后一段；c.segId('S03-12') 按段号
  c.autoTitle(s[0]);                // 章节标题：大字 = 台本这一场的 title（如「三、学会思考」，编号照台本），属于第 N 题时加「PART 0N · 第N个问题」
  c.pointList({ kicker: 'RULES · 调用规则', title: '它主要规定三件事：', at: s[4].start + 0.1,
    items: [{ text: '能调用哪些功能', at: c.P(s[5], '能调用', 0.05) }, { text: '请求的格式', at: c.P(s[5], '请求', 0.4) }] });
});
```

| 类别 | 接口 |
|---|---|
| 取时间（不许写死秒数） | `c.seg(i)`、`c.segs()`、`c.segId('S03-12')`；`c.P(seg, '短语', 兜底比例)` 这一段说到该短语的时刻（忽略空格标点大小写）；`c.find('短语')` 本场里找，找不到 null；`c.at('短语', 兜底)` 找不到用兜底并 warn；`c.gap(seg)` 段后停顿；`c.endTalk()` 本场讲完的时刻；全局 `ENG.tocInTime()`、`ENG.tocRect()`、`ENG.safeTop(y, right, left)`（把卡片顶推到目录下方） |
| 基础 | `c.div(cls, x, y, w, h, html, parent)`、`c.svg(...)`、`c.T(el, init, fx)` 轨道（`.to(t, props, d, ease)` / `.in(t)` / `.out(t)`）、`c.show(el, t0, t1, dy)`、`c.outAll(tracks, t)`、`c.card`、`c.ring`、`c.ringOn(el, t0, t1)`、`c.arrow(x1, y1, x2, y2, color, {w, head, dash})`、`c.chip(html, x, y, {kind, at, until, size})`、`c.label(html, x, y, {w, align, kind: ''\|'s'\|'o', size, weight, on, color, at, until, parent})`、`c.bracket(x, y, w, html, {size, kind, on, labelColor, color, at, until, parent})`（标签字色见下面「标签颜色」） |
| 标题 | `c.title(text, kicker, seg, {morph, cx, cy})`（kicker 传 `''` 就没有小字那一行）、`c.autoTitle(seg, {morph, text, kicker})`（见下面「章节标题」）、`c.bigWord({text, kicker, sub, at})`（开场大字） |
| 疑问卡 | `c.questionCards({at: [...], items?, title?, titleAt?})`：默认用 `episode.questions` 的文字，到飞入时刻缩小飞进对应目录行 |
| 卡片 | `c.statement({kicker, lead, main, at, mainAt, until})`、`c.pointList({x, y, w, kicker, title, items: [{text, sub, at, mark: 'num'\|'x'\|'check'}], at, until, fs, step})`、`c.summary({items: [[主句, 副句]], at: [...], cardAt, sign, signAt})` |
| 代码卡 | `c.code({x, y, w, h, title, kicker, lines: [str \| {t, c, cLate, hide, dim}]})` → `{tr, L}`；`c.focus(card, t, [行号])`、`c.unfocus(card, t)`、`c.reveal(card, i, t)`；着色 `ENG.codeHTML` |
| 图示 | `c.node({x, y, w, h, title, sub, icon, paper, dashed, size, at, until})`、`c.link(A, B, {lane, color, dash, label, at, until})`、`c.flow({nodes, links, until})`、`c.token({text, kind: 'req'\|'res', from, to, at, dur})`、`c.compareTable({kicker, title, tip, cols, colX, rows, foot, at})`、`c.steps({items: [[标题, 副标题]], at, active: [...], done: [...]})` |
| 示意界面 | `c.browser({url \| title, x, y, w, h, at, until})`（返回的 `view(t0, t1)` 放每一屏内容）、`c.phone({title, banner, at, until})` |
| 图标 | `ENG.ICON.{doc, phone, server, key, x, check, lock, user, chat, cloud, chip}`，尺寸 `ENG.ICON_SIZE` |
| 角色（动作 v2） | `c.cue(t, kind)` 登记内容提示点（上面的卡片、列表条目、代码卡 `card.tr.in(t)`、`c.reveal`、节点、表格行、步骤、疑问卡、示意界面出现时已经自动登记；手搭的内容 `c.div` + `c.show` 才需要自己补）：自动层据此让角色朝内容轻摊、看过去，同一场 0.5 s 内的提示点合并成一个；`c.look(t0, t1, 'right' \| 'up')` / `ENG.look(t0, t1)` 让角色在这段时间看向内容（算显式眼睛动作，台本的表情仍然优先；只在有 `episode` 的时间轴生效）。角色本身（动作、口型、自动层）在 core.js，scenes.js 不画角色 |
| 字幕术语 | 引擎内置 API / API Key / Token / JSON / HTTP / SSE / LLM / Prompt；本期还要标橙的写进 `episode.json` 的 `terms`。匹配：长的先标，不和已经标了的重叠；英文 / 数字术语的英文那一边要求旁边不是字母数字（`GPT` 不会在 ChatGPT、GPT-3、GPT4 里变橙，`token` 不会在 tokens 里变橙），中文术语按字面匹配（「生成式预训练Transformer」里的「预训练」照样变橙）。字幕断行不会把术语拆到两行（`build_timeline.py`） |

**章节标题**（`c.autoTitle(seg, o)`）：
- 大字 = 台本 `script_data.py` 里这一场的 `title`（timeline 的 `scenes[].title`），原样照用，编号也照台本：一个问题跨几章时台本写「二、学会对话」「三、学会思考」「四、学会做事」，屏幕上就是这样，不会按问题都变成「二、」。
- 小字 `PART 0N · 第N个问题` 按这一场属于 `episode.questions` 的第几题（上例三章都是 `PART 02 · 第二个问题`）；不属于任何一题的章节（补充章节、总结）没有这行小字。
- 场景没写 title 时才退回 `episode.chapters[场景]` + 按题号加「一、」。`o.text` / `o.kicker` 可以手动覆盖（`kicker: ''` = 不要小字），`o.morph` 等同 `c.title`。
- 每题一章的期（第 1 期）编号和以前一样；第 1 期的数据套 autoTitle 得到「一、API 是什么 / 二、“已接入”接的是什么 / 三、API Key 是什么」+ PART 01–03，和它成片里手写的标题一致。

**标签颜色**（`c.label`、`c.bracket` 下面那行字；`kind` 默认 `''`）：
- 字色跟着背后的底色走：在纸白卡片、chip、气泡、示意窗口、浅色格子里（`parent` 是卡片，或者叠在本场之前建好的卡片上面）是墨黑 `#141414`（`kind: 's'` 灰 `#6E6A63`）；在深色背景、深色节点、代码卡、色带图面板、橙色块上是纸白 `#EDEAE3`（`kind: 's'` 纸白 72%）。`kind: 'o'` 永远橙色。
- 看的是标签出现那一刻（`at`）它中心下面画着什么：引擎在这一场搭好后把轨道算到那一刻再判断，所以卡片已经淡出的位置按深色背景算。
- 想固定就写 `on: 'light'`（按浅底配色）/ `on: 'dark'`（按深底配色）；要别的颜色写 `color`（`c.bracket` 的标签用 `labelColor`，它的 `color` 是括号线的颜色，默认橙）。不要再在 scenes.js 里手动 `.style.color = 'var(--ink)'`。

写完用 `python engine/check_layout.py`（在 `制作\` 下）查文字溢出、压字幕 / 角色 / 目录 / 进度条、出画布，以及 `low-contrast`（文字颜色和背后的底色几乎一样，对比度 < 1.6，例如纸白字在纸白卡片上、墨黑字在深色背景上；会写出字色、底色和底的 class）。它按时间轴的 canvas 开页面，报的位置是画布坐标（2340 宽时 = 舞台坐标 + 210）。疑问卡飞进目录那一刻压到目录是设计如此：这几行标成 `expected (question card flying into the TOC)`，不算进 issues。

通用规则：
- 画面按段号或台词短语取时间（`segments[].start/end`、`gaps[]`），**不许写死秒数**：配音重生成后时长会变。
- 不用 requestAnimationFrame、setTimeout、Date.now、CSS transition；随机数用固定种子。
- 内容区不要压到左下角色（舞台 x < 440）和底部字幕区（y > 900）；也不要画到舞台外面（x < 0 或 > 1920）：1920 宽时那就是出画，2340 宽时虽然看得见，但会碰到角色、徽标、目录。
- 界面、代码卡标“示意·已简化”；Key 打码；品牌只写文字不画 logo；实操不录屏，用“步骤卡 + 示意界面”。

## 抽帧自查

```bash
python scripts/render.py <期目录>/制作/engine/index.html --data <期目录>/制作/timeline.json --stills 12.5,40,95.2 --stills-dir <期目录>/制作/build/stills
python scripts/render.py <期目录>/制作/engine/index.html --data <期目录>/制作/timeline.json --sheet <期目录>/制作/build/sheet.png --sheet-count 24
```

静帧和联系表按时间轴的 canvas 出图（2340×1080；联系表缩略图保持画面比例）；要临时看别的尺寸加 `--size 1920x1080`。

用 Read 看图：每个章节开头、每个新卡片出现后、每个动作的中间帧（台本动作的时刻看 `timeline.json` 的 actions；自动层的时刻在页面里读 `ENG.autoPlan`，`ENG.charState(t)` 能直接看某一刻角色用的帧、眼睛、特效；`ENG.presenter` 是本期讲解员，`ENG.charGeom` 是她的几何）。确认画面上是本期讲解员、不是另一位。发现问题改 scenes.js 或台本画面说明，不要改 timeline.json。
