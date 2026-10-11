# 独立视频短视频《不再 Review》（长视频《一个月合并 2000 多个 PR，却不逐个 Review》的二次剪辑，2026-10-05）

## 用户要求（原话）

> 长视频做完了之后做短视频，用 /short-video 来做

时长、平台、合集用户都没说，按技能的默认值做：54 s（一个点 + 六拍）、四个平台都发（等用户同意）、B 站不选合集、话题 抖音 5 个 / 小红书·视频号 10 个、声明含 AI 生成内容、台本第三人称、BGM 床 −9 dB。长视频的记录见 `20261005-075000-no-more-review-long-video_CN.md`（素材、事实核对、口径都在那）。

## 做了什么（`独立视频/短视频/2026-10_不再Review/`）

| 步 | 做法 |
|---|---|
| 建条目 | `new_short.py --collection 独立视频 --name 不再Review --layout dual`（背景随机到 `pattern_color.png`）；`common.py` 的 SRC 直接引用长视频的素材：`iv` = Matt 直播（1920×1080，左 Matt 右 Lauren，各 960×1080 的人像格）、`tk` = Lauren 的演讲视频；两个都 `HAS_AUDIO = False`（静音，重新讲） |
| 事实 | 全部沿用长视频 `台本/事实核对.md`，没有新增事实；钩子“一个月 2000 多个 PR，她说自己没有逐个 Review”，旁白不写“合并”也不写 2500（简介里写明 2000 / 2500 是她自报、不是官方统计） |
| 台本 | `台本/make_script.py` 是唯一来源（生成 `录制稿.json` 和 `plan.json`）：12 句 229 汉字，第三人称，AI大圆镜（钩子带数字 → 背书 → 算账 67 个 / 17 小时 → 两样东西（验证、规矩）→ pstack 官方全自动模式 → 合并之后才看 → 泼冷水（很难、撤不回的没答案）→ 金句“Review 没有消失。它从每个 PR 的门口，搬到了早上的提交记录里。”） |
| 画面（dual） | 上框 = 访谈里单人的 960×540 上半身（`crop [0.5, 0.06, 1.0, 0.56]` = Lauren，`[0, 0.06, 0.5, 0.56]` = Matt，x、y 都是 0.5 所以还是 16:9 直接铺满），静音；下框 = 她演讲里的幻灯片（`hold` 定格，`crop` + `bg` 纯色补边：首页 2000 / GitHub 贡献曲线 / High-quality verification / “whenever you correct your agent”那张表）和 pstack README、官方指南的页面录屏（`pageShot {lower:true}`，页面图从长视频的 `media/pages` 拷来）；S8 泼冷水：上框 Lauren “very hard”，下框 Matt 问“有些 PR 是单行道”（直播 3366–3371 s，核对过转写） |
| 引擎副本改动 | **`prep_frames.py` / `build_timeline.py` 加了 range 的 `bg`（纯色补边）**——长视频引擎里有、短视频模板里没有（竖屏的幻灯片要补边）；`mix_audio.py` 的 `BGM_BED` 从 −16 改成 −9 dB（技能定的“BGM 比人声低约 14–15 dB”）。**还没合进技能的 `assets/engine-template/`**（见“待做”） |
| 配音 | Fish 故事工作室空白项目（我自己的 Chrome 窗口；列表页网址是 `/zh-CN/app/story-studio/`，不是 `/app/studio/`），声线「温柔男生」+ S2 Pro，12 句整稿键入（SHA-256 和 `tts_input.txt` 一致）→ 生成 1 次 → 导出“按段落拆分” → `import_segments.py`（12 句文字一致）→ `build_voice.py`：有声 49.2 s（≈ 0.215 s / 汉字）；`--qa` 12 条都 ≥ 0.82（N02 “Lauren Tan”被识别成 Rorantan 0.82，其余 0.92–1.00）；数字读对了（两千 / 六十七 / 十七个小时） |
| 时间轴 / 混音 | 先按字数估时（59 s），配音出来后把每个场景上框素材的长度改成“念白长度 + 0.4 s”（不然场景被素材撑长、句间留 1 s 空白），真实 54.1 s（1624 帧）；混音 −16.0 LUFS，BGM 用系列 `bgm.wav` |
| 渲染 / 成片 | `render_all.py` 4 路 94 s、0 报错；`finish.py`：成片 16.4 MB（1080×2340，−16.0 LUFS，真峰值 −0.9）、手机预览 2.1 MB、三份 SRT（26 条）；抽帧联系表逐 2 s 看过 |
| 封面 | `make_candidates.py`（样式 full 满框，帧取自 `iv`）：A = Lauren 笑着听 Matt 问话的安静帧 + “2000个PR / 没逐个看”（推荐）；B = 她讲解时的特写 + “她怎么 / 把关的？”；C = Matt 提问的帧 + “每个PR / 都看了吗？”。`defaults.avoid` 写了 3:4 躲开左下角名牌（不然露出半个“poteto”）；第一版 C 用 `split` + 演讲首页，图被 `cover` 裁坏（首页文字在整幅图里偏左偏右），改成 Matt 的帧 |
| 标题 / 简介 | 3×4 写在 `投稿信息.json`（事实陈述 / 数字悬念 / 泼冷水 × B 站 / 抖音 / 小红书 / 视频号短标题），`check_titles.py` 全在限内；简介前两行写来源和 AI 声明，正文末尾写清“2000 多个是她自报、她说的是合并之前不逐个看” |

## 要用耳朵听的句子

N02（Lauren Tan、SpaceXAI、Grok Bot 的读法）、N08（pstack）、N07（lint）。机器识别都对得上，只是英文专名的读法要人耳朵确认。

## 踩的点 / 新规律

- **Fish 列表页是 `/zh-CN/app/story-studio/`**；新建项目弹窗里点“空白项目”，默认声音 Ethan、模型 S2.1 Pro：点声音卡的 ⇄ → 弹窗“最近使用”里点「温柔男生」→ 卡片上的“使用”→ 弹窗问当前章节还是所有章节选“所有章节”；模型下拉选 S2 Pro。从不是前台的标签页做这些会丢字：先 `chrome_front.ps1 -TabKey "故事工作室 |"` 把我自己窗口里要用的那个标签选中并前置，JS 确认 `visibilityState === 'visible'`；用完 `-Action back` 最小化还给 Claude。
- **场景长度由“念白 + 0.4 s”和上框素材总长两者取大**：素材比念白长，场景就被撑长、句间留空；上框 range 要略短于念白，让念白说了算（最后一段会接着往下放）。
- 访谈人像格裁单人：`crop [0.5, 0.06, 1.0, 0.56]`（上半身，16:9 直接铺满）比整格 8:9 加模糊底好看得多；封面里要避开名牌。
- 竖屏版 `.zhnote` 是 46 px（缩 0.57 后约 26 px），dual 下一条说明条 ≤ 16 字放得下。

## 待做

1. 用户回“封面 X 标题 Y 同意”→ `make_candidates.py <本条> --select X` → `cover_frame0.py <本条>`（成片第 0 帧 = 选定封面）→ 定稿 `投稿信息.json`（把选中的标题写进各平台字段）→ 排队（**四个创作页的队伍：日报 RSS 源扩展 → 短视频制作（Claude封号潮）→ 长视频制作与素材下载 → 我**）→ 开四个页、`explorer.exe /select` 选中新成片、用户拖原片 → 我一次填完整、读回核对 → 点发布 → 逐个核对线上 → 关标签、通知下一个。
2. 把 `bg` 补边合进技能 `assets/engine-template/`（`prep_frames.py` / `build_timeline.py` 各几行，已在本条验证），并在 `短视频\流程复盘.md` 记一节。
3. 发布后补：本条 README、`投稿信息.json` 的 published、`独立视频\README.md` 的 B 站链接、`短视频\README.md`、AGENTS.md。
