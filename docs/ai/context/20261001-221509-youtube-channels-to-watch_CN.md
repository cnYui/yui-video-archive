# YouTube 科技 / 新闻频道监控名单（2026-10-01）

## 任务

用户（2026-10-01，发来 Lenny's Podcast 的频道截图）：“我需要你盯住几个科技账号或者新闻账号。比如说特朗普昨天开了个 AI 的会，如果有一些好的 AI 视频、播客，你就可以调用这个 skill 把视频下载下来。然后我可以写一个 skill，把长视频剪辑成几个短视频片段发到 B 站上。甚至不用做太多操作，只要加一个同声传译就行，也可以简单点评一下然后直接发。”“你可以先帮我看看，可以盯住哪几个账号吗？图中这个博主你联网搜一下，有没有类似的这样的博主，先记录一下”。

本记录 = 候选频道调研和核实结果。**没有下载任何视频，没有改任何技能和脚本。**

## 结论

- 联网搜了 6 轮、再用 YouTube 搜索解析了 5 个频道，核实了 53 个能用的频道（另有 5 个已停更或很少更新、11 个 handle 写错或匹配到别的频道，见后面）。数据时点 2026-10-01 22:15（东京时间），订阅数是 YouTube 页面显示的取整值。核实方法：直接读频道页拿真实频道 ID 和订阅数，再读频道自己的 RSS 看最近上传；Lenny's 的 64 万订阅、1.8K 视频和用户截图一致。
- **先盯 13 个**（下面「先盯清单」）：6 个实时事件源 + 2 个 AI 官方 + 5 个对标 Lenny's 的访谈。评论类（AI Daily Brief、Wes Roth 等）只当“今天什么事热”的线索，不当素材：它们本身就是对别人新闻的二次解读。
- **最像 Lenny's 的**：How I AI（就是 Lenny's 播客网络出品，Claire Vo 主持，30 分钟实操演示）、Latent Space、No Priors、Dwarkesh Patel、Cognitive Revolution；产品向再加 Peter Yang、Aakash Gupta、Greg Isenberg、Every。
- **“特朗普开 AI 会”这类事件，最快的是 白宫、C-SPAN、PBS NewsHour、CNBC Television、TBPN**：TBPN 最新一条的标题是 AI 高管签联合承诺（应该就是白宫协议），CNBC Television 最新一条在谈 OpenAI–Hugging Face 事件，两条都是半天内发的，说明它们当天就覆盖热点。
- **可以不用 API 监控**：每个频道都有免登录的 RSS，58 个都读通了；yt-dlp、ffmpeg 8.0 这台机器上已经装好。
- **版权是这条路的主要风险**：核对了 56 个频道最近 167 条视频的页面，**0 条标了 Creative Commons**（YouTube 上只有标 CC BY 的视频才允许转用）。也就是说，除了白宫这类美国政府作品，其余都是标准 YouTube 许可，搬运需要授权，见「版权和平台规则」。

## 先盯清单（13 个）

| 组 | 频道 | 为什么盯 |
|---|---|---|
| 实时事件 | [@WhiteHouse](https://www.youtube.com/@WhiteHouse) | 现场讲话、签字、会议全程直播；美国政府作品，片段最稳（上一条白宫视频就从这里取） |
| 实时事件 | [@cspan](https://www.youtube.com/@cspan) | 国会听证和会议全程直播，AI 听证找这里；C-SPAN 自己主张版权，用前另查它的使用条款 |
| 实时事件 | [@PBSNewsHour](https://www.youtube.com/@PBSNewsHour) | 会后问答、新闻解读；上一条白宫视频用过它的西翼外问答 |
| 实时事件 | [@CNBCtelevision](https://www.youtube.com/@CNBCtelevision) | 财经新闻直播切片，AI 相关多（最新一条在谈 OpenAI-Hugging Face 事件） |
| 实时事件 | [@TBPNLive](https://www.youtube.com/@TBPNLive) | 每天直播 2–3 小时的科技脱口秀，最新一条标题是 AI 高管签联合承诺（应是白宫协议）；要自己切片 |
| 实时事件 | [@BloombergTech](https://www.youtube.com/@BloombergTech) | 彭博科技频道，AI 产业报道和访谈 |
| AI 官方 | [@OpenAI](https://www.youtube.com/@OpenAI) | 产品发布直播、演示 |
| AI 官方 | [@anthropic-ai](https://www.youtube.com/@anthropic-ai) | 最近几条是 1 分钟短片，偶有长访谈；30 天只有 3 条 |
| 访谈（对标） | [@LennysPodcast](https://www.youtube.com/@LennysPodcast) | 参照物（用户已订阅） |
| 访谈（对标） | [@howiaipodcast](https://www.youtube.com/@howiaipodcast) | Lenny's 播客网络出品（Claire Vo），约 30 分钟的 AI 工作流实操演示 |
| 访谈（对标） | [@DwarkeshPatel](https://www.youtube.com/@DwarkeshPatel) | 前沿实验室和研究者的长访谈，也有历史、地缘主题；最近几条是切片 |
| 访谈（对标） | [@LatentSpacePod](https://www.youtube.com/@LatentSpacePod) | AI 工程师视角，讲产品和工具怎么做出来 |
| 访谈（对标） | [@NoPriorsPodcast](https://www.youtube.com/@NoPriorsPodcast) | 投资人 / 创业视角的 AI 访谈 |

备选（需要时加）：访谈类 Y Combinator、a16z、Sequoia、20VC、Big Technology、Hard Fork、All-In、Cognitive Revolution、Machine Learning Street Talk、AI Engineer、Every、Peter Yang、Aakash Gupta、Greg Isenberg、Cheeky Pint；官方类 Google DeepMind、NVIDIA；新闻类 Reuters、AP、The Information。

## 全部核实过的频道

列说明：「30 天」= 最近 30 天上传条数（RSS 只给最近 15 条，写 ≥15 表示 15 条全在 30 天内，实际更多）；「最近几条」= 最近 3–4 条的时长，单位分钟，「短」= 75 秒以内（Shorts / 切片）；频道 ID 用来拼 RSS。

### 实时事件：政府、通讯社、新闻台、科技新闻

| 频道 | 订阅 | 最近上传 | 30 天 | 最近几条（分钟） | 频道 ID | 备注 |
|---|---|---|---|---|---|---|
| [@WIRED](https://www.youtube.com/@WIRED) | 13M | 2 天前 | ≥15 | 1/3/23 | `UCftwRNsjfRo08xYE31tkiyw` | 科技媒体，短片 + 偶尔 20 分钟以上的访谈 |
| [@wsj](https://www.youtube.com/@wsj) | 6.7M | 14 小时前 | ≥15 | 8/2/2 | `UCK7tptUDHh-RYDsdxO1-5QQ` | 综合财经新闻，近期条目与 AI 无关 |
| [@PBSNewsHour](https://www.youtube.com/@PBSNewsHour) | 5.38M | 14 小时前 | ≥15 | 11/57/8 | `UC6ZFN9Tx6xh-skXCuRHCDpQ` | 会后问答、新闻解读；上一条白宫视频用过它的西翼外问答 |
| [@business](https://www.youtube.com/@business) | 5.16M | 22 小时前 | 10 | 短/24/10 | `UCUMZ7gohGI9HcU9VNsr2FJQ` | Bloomberg Originals，制作类财经内容，不是实时新闻 |
| [@AssociatedPress](https://www.youtube.com/@AssociatedPress) | 4.67M | 1 小时内 | ≥15 | 24/短/短（直播 1） | `UC52X5wxOL_s5yw0dQk7NtgA` | 综合新闻、有现场直播，量大，要关键词过滤才有 AI |
| [@Reuters](https://www.youtube.com/@Reuters) | 4.33M | 1 小时内 | ≥15 | 短/短/30（直播 1） | `UChqUTb7kYRX8-EiaN3XFrSQ` | 综合新闻、有现场直播，量大，要关键词过滤才有 AI |
| [@CNBC](https://www.youtube.com/@CNBC) | 4.17M | 1 天前 | ≥15 | 21/短/1 | `UCvJJ_dzjViJCoLf5uKUTwoA` | 最近几条是调查 / 纪录类长视频，实时性不如 CNBC Television |
| [@TheVerge](https://www.youtube.com/@TheVerge) | 3.52M | 1 小时内 | ≥15 | 1/短/2 | `UCddiUEpeqJcYeBxX1IVBKvQ` | 科技媒体，近期多为 1–2 分钟短片 |
| [@CNBCtelevision](https://www.youtube.com/@CNBCtelevision) | 3.41M | 1 小时内 | ≥15 | 4/短/1 | `UCrp_UI8XtuYfpiqluWLD7Lw` | 财经新闻直播切片，AI 相关多（最新一条在谈 OpenAI-Hugging Face 事件） |
| [@WhiteHouse](https://www.youtube.com/@WhiteHouse) | 3.33M | 17 小时前 | ≥15 | 57/短/59（直播 2） | `UCYxRlFDqcWM4y7FfpiAN3KQ` | 现场讲话、签字、会议全程直播；美国政府作品，片段最稳（上一条白宫视频就从这里取） |
| [@cspan](https://www.youtube.com/@cspan) | 1.95M | 2 小时前 | ≥15 | 9/44/短（直播 1） | `UCb--64Gl51jIEVE-GLDAVTg` | 国会听证和会议全程直播，AI 听证找这里；C-SPAN 自己主张版权，用前另查它的使用条款 |
| [@BloombergTech](https://www.youtube.com/@BloombergTech) | 739K | 19 小时前 | ≥15 | 11/44 | `UCrM7B7SL_g1edFOnmj-SDKg` | 彭博科技频道，AI 产业报道和访谈 |
| [@TechCrunch](https://www.youtube.com/@TechCrunch) | 676K | 17 小时前 | ≥15 | 31/2/2 | `UCCjyq_K1Xwfg8Lndy7lKMpA` | 科技新闻短片，偶有长访谈 |

### AI 公司官方频道

| 频道 | 订阅 | 最近上传 | 30 天 | 最近几条（分钟） | 频道 ID | 备注 |
|---|---|---|---|---|---|---|
| [@NVIDIA](https://www.youtube.com/@NVIDIA) | 2.24M | 1 小时内 | ≥15 | 短/2/短 | `UCHuiy8bXnmK5nisYHUd1J5g` | 近期多为短片；主题演讲也发在这里 |
| [@OpenAI](https://www.youtube.com/@OpenAI) | 2.08M | 2 天前 | ≥15 | 短/54/3（直播 1） | `UCXZCJLdBC09xxGZ6gcdrc6A` | 产品发布直播、演示 |
| [@GoogleDeepMind](https://www.youtube.com/@GoogleDeepMind) | 928K | 8 天前 | 5 | 短/44/短 | `UCP7jMXSY2xbc3KCAE0MHQ-A` | 模型发布和研究访谈 |
| [@anthropic-ai](https://www.youtube.com/@anthropic-ai) | 809K | 8 天前 | 3 | 1/1/1 | `UCrDwWp7EBBv4NwvScIpBDOA` | 最近几条是 1 分钟短片，偶有长访谈；30 天只有 3 条 |

### 访谈 / 播客（对标 Lenny's）

| 频道 | 订阅 | 最近上传 | 30 天 | 最近几条（分钟） | 频道 ID | 备注 |
|---|---|---|---|---|---|---|
| [@lexfridman](https://www.youtube.com/@lexfridman) | 5.05M | 14 天前 | 1 | 217/316/193 | `UCSHZKyawb77ixDdsGog4iWA` | 热门，但更新慢、单条 3–5 小时 |
| [@ycombinator](https://www.youtube.com/@ycombinator) | 2.4M | 3 天前 | ≥15 | 2/30/2 | `UCcefcZRL2oaA_uBNeo5UOWg` | 创业与 AI 访谈、演讲 |
| [@lexclips](https://www.youtube.com/@lexclips) | 1.64M | 9 天前 | ≥15 | 31/6/11 | `UCJIfeSCssxSC_Dhc5s7woww` | Lex 的切片号 |
| [@DwarkeshPatel](https://www.youtube.com/@DwarkeshPatel) | 1.43M | 14 小时前 | ≥15 | 短/短/1 | `UCXl4i9dYBrFOabk0xGmbkRA` | 前沿实验室和研究者的长访谈，也有历史、地缘主题；最近几条是切片 |
| [@allin](https://www.youtube.com/@allin) | 1.15M | 17 小时前 | ≥15 | 53/51/短 | `UCESLZhusAkFfsNsApnjF_Cg` | 科技 + 政策 + 时政脱口秀；时政内容要注意口径 |
| [@GregIsenberg](https://www.youtube.com/@GregIsenberg) | 722K | 2 天前 | 11 | 19/30/26 | `UCPjNBjflYl0-HQtUvOx0Ibw` | 创业点子 + AI 工具，20–30 分钟 |
| [@aiDotEngineer](https://www.youtube.com/@aiDotEngineer) | 652K | 22 小时前 | ≥15 | 19/22/25 | `UCLKPca3kwwd-B59HNr-_lvA` | AI Engineer 大会演讲，20 分钟上下，偏技术 |
| [@LennysPodcast](https://www.youtube.com/@LennysPodcast) | 640K | 1 天前 | ≥15 | 短/29/17 | `UC6t1O76G0jYXOAoYCm153dA` | 参照物（用户已订阅） |
| [@peterdiamandis](https://www.youtube.com/@peterdiamandis) | 536K | 14 小时前 | ≥15 | 短/短/2 | `UCvxm0qTrGN_1LMYgUaftWyQ` | Moonshots，技术趋势访谈 |
| [@AcquiredFM](https://www.youtube.com/@AcquiredFM) | 333K | 17 天前 | 1 | 215/2/短 | `UCyFqFYfTW2VoIQKylJ04Rtw` | 商业史长播客（最近一条 215 分钟），月更，和 AI 新闻不强相关 |
| [@a16z](https://www.youtube.com/@a16z) | 299K | 19 小时前 | ≥15 | 短/52/50 | `UC9cn0TuPq4dnbTY-CBsm8XA` | 投资人访谈和产业观点 |
| [@sequoiacapital](https://www.youtube.com/@sequoiacapital) | 253K | 7 天前 | 11 | 短/2/短 | `UCWrF0oN6unbXrWsTN7RctTw` | 创业与 AI 访谈，近期多为短片 |
| [@LatentSpacePod](https://www.youtube.com/@LatentSpacePod) | 238K | 17 小时前 | ≥15 | 40/95/短 | `UCxBcwypKK-W3GHd_RZ9FZrQ` | AI 工程师视角，讲产品和工具怎么做出来 |
| [@TheInformation](https://www.youtube.com/@TheInformation) | 227K | 7 小时前 | ≥15 | 49/2/短（直播 1） | `UCoKqUtcUtf8QPb0GWxe5e7Q` | 科技媒体，有直播节目 |
| [@20VC](https://www.youtube.com/@20VC) | 222K | 1 天前 | ≥15 | 短/短/短 | `UCf0PBRjhf0rF8fWBIxTuoWA` | 近期三条都是短片 |
| [@MachineLearningStreetTalk](https://www.youtube.com/@MachineLearningStreetTalk) | 220K | 2 天前 | ≥15 | 74/短/短 | `UCMLtBahI5DMrt0NPvDSoIRQ` | 偏研究和学术的 AI 访谈 |
| [@TBPNLive](https://www.youtube.com/@TBPNLive) | 142K | 12 小时前 | ≥15 | 30/180/125（直播 2） | `UC-DRzaGnL_vtBUpCFH5M0tg` | 每天直播 2–3 小时的科技脱口秀，最新一条标题是 AI 高管签联合承诺（应是白宫协议）；要自己切片 |
| [@howiaipodcast](https://www.youtube.com/@howiaipodcast) | 120K | 1 小时内 | ≥15 | 短/短/46 | `UCRYY7IEbkHLH_ScJCu9eWDQ` | Lenny's 播客网络出品（Claire Vo），约 30 分钟的 AI 工作流实操演示 |
| [@PeterYangYT](https://www.youtube.com/@PeterYangYT) | 110K | 2 天前 | ≥15 | 18/23/45 | `UCnpBg7yqNauHtlNSpOl5-cg` | 产品经理视角的 AI 工具实操，20–45 分钟 |
| [@NoPriorsPodcast](https://www.youtube.com/@NoPriorsPodcast) | 97.5K | 2 天前 | ≥15 | 短/短/43 | `UCSI7h9hydQ40K5MJHnCrQvw` | 投资人 / 创业视角的 AI 访谈 |
| [@hardfork](https://www.youtube.com/@hardfork) | 67.1K | 1 小时内 | ≥15 | 2/短/短 | `UCZcR2SVWaGWNlMqPxvQS3vw` | 《纽约时报》科技播客 |
| [@Alex.kantrowitz](https://www.youtube.com/@Alex.kantrowitz) | 66.8K | 12 小时前 | ≥15 | 短/59/短 | `UCye1YedIypHffYb8k6Gp9wg` | Big Technology Podcast，AI 公司负责人访谈（近期有 Claude Code 负责人 Boris Cherny） |
| [@EveryInc](https://www.youtube.com/@EveryInc) | 48K | 17 小时前 | 13 | 33/24/15（直播 2） | `UCjIMtrzxYc0lblGhmOgC_CA` | Every 出品（Dan Shipper 的 AI & I 在这里），有直播 |
| [@growproduct](https://www.youtube.com/@growproduct) | 46.4K | 7 天前 | 10 | 74/短/短 | `UCsHBhXybRz2CCfpU0hWp7ow` | Aakash Gupta，AI 产品经理访谈 |
| [@CognitiveRevolutionPodcast](https://www.youtube.com/@CognitiveRevolutionPodcast) | 45.1K | 19 小时前 | ≥15 | 175/133/191（直播 2） | `UCjNRVMBVI30Sak_p6HRWhIA` | 研究者、创始人、政策人士访谈；单条常 2–3 小时 |
| [@CheekyPint](https://www.youtube.com/@CheekyPint) | 1.7K | 9 天前 | 14 | 短/短/短 | `UCXi7Hg2nSB40ujzM2CMtF-Q` | 新频道（25 个视频），访谈；最近一条是 Bret Taylor 谈 OpenAI 董事会 |

### AI 评论 / 快讯（当选题线索，不当素材）

| 频道 | 订阅 | 最近上传 | 30 天 | 最近几条（分钟） | 频道 ID | 备注 |
|---|---|---|---|---|---|---|
| [@Fireship](https://www.youtube.com/@Fireship) | 4.29M | 19 小时前 | 13 | 5/7/6 | `UCsBjURrPoezykLs9EqgamOA` | 开发者向短科普，约 5–7 分钟 |
| [@TwoMinutePapers](https://www.youtube.com/@TwoMinutePapers) | 1.84M | 7 天前 | 7 | 5/5/5 | `UCbfYPyITQ-7l4upoX8nvctg` | 论文解读，约 5 分钟 |
| [@mreflow](https://www.youtube.com/@mreflow) | 1.01M | 1 天前 | ≥15 | 短/短/35 | `UChpleBmo18P08aKCIgti38g` | Matt Wolfe，AI 工具和新闻 |
| [@matthew_berman](https://www.youtube.com/@matthew_berman) | 638K | 2 天前 | ≥15 | 10/17/短 | `UCawZsQWqfGSbCI5yjkdVkTA` | AI 新闻和工具评论（注意 handle 带下划线） |
| [@AIDailyBrief](https://www.youtube.com/@AIDailyBrief) | 586K | 17 小时前 | ≥15 | 20/38/26 | `UCKelCK4ZaO6HeEI1KQjqzWA` | 近乎每日一期，20–40 分钟的 AI 新闻评论 |
| [@aiexplained-official](https://www.youtube.com/@aiexplained-official) | 452K | 7 天前 | 3 | 33/25/29 | `UCNJ1Ymd5yFuUPtn21xtRbbw` | 深度评论，30 天 3 条 |
| [@TheAiGrid](https://www.youtube.com/@TheAiGrid) | 398K | 5 小时前 | 13 | 11/9/8 | `UCbY9xX3_jW5c2fjlZVBI4cg` | AI 发布快评 |
| [@WesRoth](https://www.youtube.com/@WesRoth) | 328K | 1 小时内 | ≥15 | 32/15/16 | `UCqcbQf6yw5KzRoDDcZ_wBSw` | 每日快讯式评论 |
| [@NateBJones](https://www.youtube.com/@NateBJones) | 325K | 10 小时前 | ≥15 | 1/25/31 | `UC0C-17n9iuUQPylguM1d-lQ` | AI 新闻与策略，短片 + 25–30 分钟长片 |
| [@TheRundownAI](https://www.youtube.com/@TheRundownAI) | 199K | 2 天前 | ≥15 | 2/短/短 | `UC8LUzR34nNX8KH3Edd0un1g` | AI 快讯，近期多为短片 |

## 不盯的（核实过）

| 频道 | 订阅 | 原因 |
|---|---|---|
| [@AIatMeta](https://www.youtube.com/@AIatMeta) | 39.8K | 最后上传在 217 天前 |
| [@AndrejKarpathy](https://www.youtube.com/@AndrejKarpathy) | 1.71M | 只有 17 个视频，最后上传在 581 天前，不会有新内容 |
| [@Bg2Pod](https://www.youtube.com/@Bg2Pod) | 103K | RSS 里最后一条在 112 天前，30 天 0 条（只有 46 个视频），可能转了平台或停更，要的话再确认 |
| [@RedpointAI](https://www.youtube.com/@RedpointAI) | 30.4K | 最新一条在 28 天前，30 天 1 条，月更 |
| [@stripe](https://www.youtube.com/@stripe) | 112K | 最新一条在 28 天前，30 天 1 条，月更 |

**写 handle 时踩过的坑**（核实时 404 或匹配到别的频道）：

- Big Technology Podcast 是 `@Alex.kantrowitz`，`@BigTechnology` 是个葡语频道；
- Bloomberg 科技频道是 `@BloombergTech`，`@BloombergTechnology`、`@BloombergTV` 都 404，`@technology` 是个 41 订阅的空号；
- Matthew Berman 是 `@matthew_berman`（带下划线），`@MatthewBerman` 是 57 订阅的别人；
- Every 是 `@EveryInc`，`@every` 是 72 订阅的空号；The Verge 是 `@TheVerge`；Aakash Gupta 是 `@growproduct`；
- Unsupervised Learning 是 `@RedpointAI`；`@danshipper`、`@LightconePodcast` 都 404（YC 的 Lightcone 播客应该在 YC 自己的频道里，没核实）。

## 版权和平台规则

- **核对结果**：56 个频道、最近 167 条视频，0 条标 CC。含白宫、OpenAI、Anthropic、Lenny's，都没标 CC，也就是默认的标准 YouTube 许可。这只是 YouTube 页面上的许可标记；我没有逐家查它们各自的使用条款，有的可能另有“可剪辑转载”的声明。
- **白宫例外**：白宫视频是美国联邦政府作品，在美国不享有版权（17 U.S.C. §105），所以是最稳的素材；上一条白宫协议视频的白宫片段就是这么用的。但画面里夹带的第三方素材、音乐不在此列；上一条还用了 PBS NewsHour 的会后问答片段，那部分不是政府作品，属于下面“其余”的情况。
- **其余**：没有授权就下载、同传、剪成短片发 B 站，对版权方来说是侵权。加中文同传和点评不改变这一点；点评越多、引用片段越短，风险越低，但不是免责。上一条白宫视频的做法（只取几个现场片段、以讲解为主）比“长视频切片 + 同传”稳得多。
- **YouTube 条款**：用 yt-dlp 这类工具下载不在 YouTube 允许的范围内，风险主要在 YouTube 账号和 IP 上。
- **B 站**：投稿选「转载」并写明出处是平台要求，不等于获得授权；版权方投诉就会下架。
- 可行的路：① 事件类优先取政府来源；② 访谈类先写信问版权方要授权（我没问过，不知道对方会不会同意）；③ 只做以点评为主、片段只作引用的形式。这不是法律意见。

## 怎么监控（草案，没做）

- **频道 RSS（Atom）**：`https://www.youtube.com/feeds/videos.xml?channel_id=<频道 ID>`。免登录、免 key；只给最近 15 条；有标题、发布时间、观看数，**没有时长和是否直播**，要再读 watch 页（页面里有 `lengthSeconds`、`isLiveContent`；核对版权时就是这么读的）。
- **直播**：白宫、C-SPAN、TBPN 都在直播。直播在 RSS 里是开播时就出现、还是结束后才出现，没实测，要拿一次真实的直播验证。
- **轮询和过滤（建议）**：事件类 10–15 分钟一次，其余 1–2 小时一次；用标题关键词（AI、superintelligence、Trump、Altman、Amodei、Huang…）加时长（滤掉 ≤2 分钟的短片）筛选。新闻通讯社每天几十条，必须过滤。
- **复用日报的抓取器**：`AI日报/collector/collect.py` 已经是 RSS 抓取 + `seen.sqlite` 去重（GitHub 的 `releases.atom` 也是 Atom，用的 `kind: rss`），YouTube 频道 RSS 可以直接套。**但别加进日报的 `sources.yaml`**：那是日报候选新闻的来源表，会把访谈和直播混进日报；另做一张监控源表。
- 下载用 yt-dlp（`C:\Users\yui\AppData\Local\Programs\Python\Python312\Scripts\yt-dlp`），切片、转写、混音沿用现有流水线（白宫视频的同传做法见 `20261001-181500-white-house-si-accord-video-production_CN.md`）。
- 按 AGENTS.md：用户没明确说“下载”时，下载是要先问的动作。监控到新视频先推送给用户挑，不自动下载（待用户定，见下）。

## 待用户定

1. 先盯的名单：用上面 13 个，还是加减；要不要让我用 Chrome 插件（只读）看一遍用户 YouTube 的订阅列表当补充，避免重复。
2. 范围：只做白宫 / 政府这类授权没问题的事件源，还是也做播客；做播客的话授权怎么办（见版权一节）。
3. 发现新视频后：只推送给用户挑，还是自动下载。
4. 热门频道（Dwarkesh、Lex、All-In 等）在 B 站可能已经有人在搬，我没查；要不要先在 B 站搜一轮，避开撞车，把速度快、没人做的放前面。
5. 监控和流水线要不要做成技能（盯频道 → 筛选 → 下载 → 转写 → 切片 → 同传 → 投稿页）。

## 机器可读清单（先盯 13 个）

```yaml
- {handle: "WhiteHouse", channel_id: "UCYxRlFDqcWM4y7FfpiAN3KQ", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCYxRlFDqcWM4y7FfpiAN3KQ"}
- {handle: "cspan", channel_id: "UCb--64Gl51jIEVE-GLDAVTg", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCb--64Gl51jIEVE-GLDAVTg"}
- {handle: "PBSNewsHour", channel_id: "UC6ZFN9Tx6xh-skXCuRHCDpQ", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UC6ZFN9Tx6xh-skXCuRHCDpQ"}
- {handle: "CNBCtelevision", channel_id: "UCrp_UI8XtuYfpiqluWLD7Lw", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCrp_UI8XtuYfpiqluWLD7Lw"}
- {handle: "TBPNLive", channel_id: "UC-DRzaGnL_vtBUpCFH5M0tg", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UC-DRzaGnL_vtBUpCFH5M0tg"}
- {handle: "BloombergTech", channel_id: "UCrM7B7SL_g1edFOnmj-SDKg", group: "实时事件", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCrM7B7SL_g1edFOnmj-SDKg"}
- {handle: "OpenAI", channel_id: "UCXZCJLdBC09xxGZ6gcdrc6A", group: "AI 官方", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCXZCJLdBC09xxGZ6gcdrc6A"}
- {handle: "anthropic-ai", channel_id: "UCrDwWp7EBBv4NwvScIpBDOA", group: "AI 官方", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCrDwWp7EBBv4NwvScIpBDOA"}
- {handle: "LennysPodcast", channel_id: "UC6t1O76G0jYXOAoYCm153dA", group: "访谈（对标）", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UC6t1O76G0jYXOAoYCm153dA"}
- {handle: "howiaipodcast", channel_id: "UCRYY7IEbkHLH_ScJCu9eWDQ", group: "访谈（对标）", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCRYY7IEbkHLH_ScJCu9eWDQ"}
- {handle: "DwarkeshPatel", channel_id: "UCXl4i9dYBrFOabk0xGmbkRA", group: "访谈（对标）", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCXl4i9dYBrFOabk0xGmbkRA"}
- {handle: "LatentSpacePod", channel_id: "UCxBcwypKK-W3GHd_RZ9FZrQ", group: "访谈（对标）", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCxBcwypKK-W3GHd_RZ9FZrQ"}
- {handle: "NoPriorsPodcast", channel_id: "UCSI7h9hydQ40K5MJHnCrQvw", group: "访谈（对标）", rss: "https://www.youtube.com/feeds/videos.xml?channel_id=UCSI7h9hydQ40K5MJHnCrQvw"}
```

## 来源

- 候选频道：[The 11 Best AI Podcasts to Listen to in 2026](https://divbyzero.com/blog/best-ai-podcasts/)、[10 Best AI Podcasts in 2026, Ranked by Focus and Depth](https://fast.io/resources/best-ai-podcasts-2026/)、[25 Best AI YouTube Channels to Follow in 2026](https://usefulai.com/feeds/youtube-channels)、[Announcing a brand-new podcast: “How I AI” with Claire Vo](https://www.lennysnewsletter.com/p/announcing-a-brand-new-podcast-how)；这些榜单只用来找名字，订阅数、更新频率、许可都是自己读 YouTube 核实的。
- 白宫协议的现场报道（说明当天各台都在覆盖）：[PBS NewsHour](https://www.pbs.org/newshour/politics/watch-trump-announces-accord-signed-by-top-ai-companies-to-self-police-development)、[The National Desk](https://www.youtube.com/watch?v=MIQbREtOj5g)、[Fox Business](https://www.foxbusiness.com/video/6405926413112)。
