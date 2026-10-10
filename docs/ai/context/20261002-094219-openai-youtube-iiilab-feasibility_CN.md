# OpenAI 频道视频：iiilab 能不能下、曼波配音双语转译能不能做（可行性核对）

2026-10-02 09:20–09:45（本机时间）。

## 用户要求

“https://www.youtube.com/@OpenAI/videos 你看一下这里的视频，是不是能用https://youtube.iiilab.com/ 下载到本地，然后用曼波的ai配音做双语转译”

## 结论

- **iiilab 能用。** 9:10 的《The dots demo, take two》和 53:34 的《OpenAI DevDay 2026 Keynote (FULL)》（直播回放）都解析成功。对 9:10 那条的三条链接（360p 带音轨、1080p 仅视频、英文原声音频）各发一次 1 字节范围请求，都是 `206`，`Content-Range` 的总字节数和页面标的一致：链接不绑 iiilab 服务器的 IP，本机能直接取。
- **没有下载任何视频**：只列了清单、解析、探测。要不要下、下哪几条，等用户定。
- 曼波配音那一段沿用白宫那条的做法，能做；两场 47–54 分钟的主题演讲工作量大很多。
- 版权是主要风险，见下面「版权」。

## 频道现状

- `yt-dlp --flat-playlist` 列 /videos 页前 40 条（只读元数据）：绝大多数是 4 分钟以内的产品 / 客户故事短片（GPT-6 Astra 客户案例、ChatGPT Work 小教程、OpenAI Academy），最短 31 秒。超过 9 分钟的只有 4 条：dots 演示 9:10、Standard Chartered 13:14、Sophos 13:44、Cyber security keynote 47:24。
- 《OpenAI DevDay 2026 Keynote (FULL)》（`Fls_onRviPM`，53:34，2026-09-29）是直播回放，不在 /videos 页，RSS 里有。RSS（`channel_id=UCXZCJLdBC09xxGZ6gcdrc6A`）只给最近 15 条，带发布时间。
- 候选（没看过内容，不知道是讲解为主还是配乐为主）：

| 视频 | ID | 时长 | 发布 | 播放（约） |
|---|---|---|---|---|
| The dots demo, take two \| OpenAI DevDay 2026 | `fHEIw5CcN5U` | 9:10 | 10-01 | 17.3 万 |
| OpenAI DevDay 2026 Keynote (FULL) | `Fls_onRviPM` | 53:34 | 09-29 | — |
| The Defender's Window: Cyber security keynote | `3jDhHA9JGUE` | 47:24 | 09-28 | 2.8 万 |
| Introducing dots, always-on agents… | `uXspbC2srEQ` | 2:28 | 09-29 | 56 万 |
| GPT-Live-1 is now in the API | `OSaP6bJoU44` | 1:17 | 09-11 | 91.4 万 |

## iiilab 实测

9:10 那条（时长 549.5 s）解析出的选项：

| 选项 | itag | 大小 | 说明 |
|---|---|---|---|
| 360p | 18 | 20.1 MiB | **唯一带声音的**（H.264 + AAC，一个文件） |
| 240p / 144p | 133 / 160 | 7.4 / 3.5 MiB | 仅视频 |
| 480p | 135 | 27.0 MiB | 仅视频 |
| 720p | 136 | 46.6 MiB | 仅视频 |
| 1080p | 137 | 91.6 MiB | 仅视频 |
| 音频（英文原声） | 249 | 3.2 MiB | webm / opus，`acont=original lang=en-US` |
| 音频（阿拉伯语） | 140 | 8.5 MiB | m4a，`acont=dubbed-auto lang=ar`，YouTube 自动配音 |

53:34 的主题演讲：360p 128 MiB、480p 165 MiB、720p 320 MiB、1080p 628 MiB、英文原声（itag 251）42 MiB、阿拉伯语自动配音 50 MiB。解析成功，没有探测它的链接。

要记住的：

1. 只有 360p 一个文件带声音。480p / 720p / 1080p 是仅视频，要高清得另取英文原声音频，再 `ffmpeg -i 视频 -i 音频 -c copy` 合。
2. 页面有两个“下载音频”：itag 249（长视频是 251）是英文原声；itag 140 是 YouTube 自动配音的阿拉伯语，别点。按钮没有语言标注，要看链接里的 `xtags`。
3. 链接约 6 小时过期（这批的有效期到 10:59），每次解析重新生成。
4. 一次只能手动解析一条，没有批量。页面自己提示“网页版 YouTube 视频可能下载失败”，还推他们的 Windows 下载软件（广告，没点）。
5. **打开页面时它已经带着一份旧的解析结果**（这次是 DevDay 主题演讲）：先看输入框里是哪条链接再用，别直接点下载。
6. 操作：输入框 `form_input`、解析按钮是个没有文字的图标按钮，`left_click` 用 ref 点；没遇到 TwitterSaver 那种点击劫持。`javascript_tool` 里用 `new URL(href).searchParams` 能把各档的 itag / 大小 / 音轨语言汇成一小段文字（返回值别带 `键=值`，会被拦）。
7. iiilab 不给字幕。这条视频 YouTube 上没有人工字幕，只有自动字幕（`en-orig`、`ja-orig`，以及机器翻译出来的 `zh-Hans` 等），所以英文稿要用 whisper 转音频，自动字幕只当对照。
8. 本机 yt-dlp 2026.08.19 已装，列频道没问题（上一条白宫视频就是用它下的）。超过几条、要合并高清 + 字幕，用它比 iiilab 省事；这次没测 yt-dlp 的实际下载。

## 版权

- 5 个候选的 `yt-dlp --print license` 都是 `NA` = 标准 YouTube 许可，没有 Creative Commons。和 10-01 的调研一致（56 个频道 167 条 0 条 CC）。
- 下载来自己转写、学习没问题；加中文配音后发 B 站是另一回事。`20261001-221509-youtube-channels-to-watch_CN.md` 的「版权和平台规则」写了：没有授权就搬运，对版权方是侵权，加同传和点评不改变这一点，点评越多、引用越短风险越低，但不是免责。我没有查 OpenAI 自己的使用条款，可能另有“可转载”的声明。
- 可选做法：①只留本地，不发布；②只取短片段、以讲解为主、标来源（白宫那条的做法）；③先问 OpenAI 要授权。

## 曼波配音双语转译

- 声音：Fish Audio 网页版「赛马娘（曼波欧耶版）」modelId `561fcedfdf0e4e1399d1bc4930d50c0e`，模型 S2 Pro（用户 10-01 指定，账号级设置），Chrome 插件操作用户的 Plus 账号；不走 API。
- 流水线照白宫那条（`独立视频/2026-10_白宫超级智能协议/制作/00_整片/`）：下载 → whisper large-v3-turbo 逐词转写英文 → 我翻译、压缩到能在原话时间里念完 → Fish 网页版整批生成 → `tts_build.py` 切句 → `qa_mix.py` 逐句识别核对 → `build_timeline.py` 放置（同传比原话晚 0.25 s，念不完加速 ≤ 1.18）→ `mix_audio.py`（原声压到 −29 LUFS）→ `render_all.py`（4 路）→ 可选加悠一片头片尾。
- “双语”我理解成：曼波中文同传 + 原声压低垫底 + 中英双语字幕（上一行英文原句、下一行中文）。白宫那条只有中文字幕。**这是我的理解，待用户确认。**
- 量级（估算，没转写过）：9:10 那条中文约 2,000 字，和白宫那条同一量级；53 分钟的主题演讲约 1.2–1.3 万字，句数近白宫那条的 10 倍，要分很多批生成。

## 待用户定

1. 先下哪几条 / 试跑哪条。建议 9:10 的 dots 演示（iiilab 已验证）：1080p 仅视频 91.6 MiB + 英文原声 3.2 MiB，合计约 95 MiB；放 `独立视频/2026-10_OpenAI视频中文版/素材/`（暂定名，整个 `素材/` 不进 git）。
2. 成片形式：中文同传 + 原声压低 + 中英双语字幕，对不对。
3. 要不要发 B 站；发的话授权怎么办（上面三种做法选哪个）。
4. 两场主题演讲做不做、做哪几段。
