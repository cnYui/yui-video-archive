# 《Tim Denning 的 36 条忠告》竖屏短视频系列（独立视频，2026-10-05）

用户 2026-10-05：“https://x.com/Tim_Denning/status/2013552215097778231 他这个也能做成好几期短视频，你查一下他是谁，然后用他的头衔来讲述文章中他的观点，可以分好几期来讲，用他的配图”。

- 文章：Tim Denning（@Tim_Denning，澳洲作家）《I'm 38. If You're in Your 20's or 30's, Read This.》36 条忠告。X 长文 2026-01-20；Substack（Modern Freedom）首发 2025-01-21，两个版本正文一致。
- “头衔”= 他自己的简介：X 写 “Writer with 1B+ views that made me 7+ figures”，Substack 写 “Aussie writer with 1B+ views that made me $6M+. Quit my banking job in 2021.”。**全是自称**，每期第 2 句挂“简介自称”，银行十年 / 2021 辞职写“自述”（第三方履历：NAB 2011–2018，之后 ARQ / Cognizant，2021 年离开的是 Cognizant）。事实核对在 `独立视频\素材\2026-10_TimDenning38岁忠告\事实核对.md`。
- 配图：文章里只有一张封面图（Substack 页面标注 **Image Credit-Midjourney**，Midjourney 生成），没有别的内嵌图。成片画面 = Substack 文章页面录屏（深色页 + 橙色荧光 + 黄色中文译文条）、作者主页（简介、23.8 万订阅）、X 推文卡片、作者照 / X 横幅 / 派对封面（只在第 5 期钩子里出现，已收紧到脸）。派对图（亮片裙的年轻女性）**不做封面**（平台审核风险）。

## 6 期

| 期 | 目录 | 主题（选的忠告号） | 估有声 |
|---|---|---|---|
| 1 | `2026-10_TimDenning忠告1_35岁分水岭` | 冒险、标准、常规路、情绪（1、4、5、6） | 73 s |
| 2 | `2026-10_TimDenning忠告2_那把小刀` | 口袋刀比方（Jason Pargin）+ 执念 + 疯子 + 难事（3、12、8） | 63 s |
| 3 | `2026-10_TimDenning忠告3_别爬公司梯子` | 梯子、早晨 1 小时、托儿所、融资、昵称（9、10、34、35、15） | 63 s |
| 4 | `2026-10_TimDenning忠告4_别装清高` | 计分板、懂钱、人性、“1000 变 12 万”没给方法（16、17、36） | 45 s |
| 5 | `2026-10_TimDenning忠告5_朋友会换父母不会等` | 朋友、孩子、父母（7、2、29、32） | 62 s |
| 6 | `2026-10_TimDenning忠告6_忙是低地位` | 忙、安静、多巴胺、游戏、心流、新闻（13、14、19、28、31、21） | 49 s |

跳过的（过审风险 / 没内容）：11 黑暗期、18 读理财书、20 吃素、22 写作、23 买比特币、24 城市 / 郊区、25 电动车、26 运动、27 戒酒（含性病半句）、30 养老院（死亡体验）、33 宗教；13 里 heroin / 自杀比喻两句（页面截图也特意截开，不带进画面）。

## 工具（这个目录，不进 git：`.gitignore` 的 `**/短视频/*/` 通配）

| 文件 | 做什么 |
|---|---|
| `series_data.py` | **唯一的数据源**：6 期台本（zh / say / en）+ 画面表（页面高亮点、照片、大数字卡）+ 页面图规格；`python series_data.py` 自检（句数 / 字数 / 估时 / 引用的短语在不在 / 禁用“他她我”和“不是…而是…”） |
| `capture_series_pages.py` | 无头 Chromium 一次截全部页面（Substack 文章按标题切段、作者主页、推文嵌入页），算所有高亮点坐标 → `素材\…\页面\`；单句片段用 420 宽视口（`vw=420`，折行放大成“引语卡”） |
| `check_marks.py` | 把高亮框画在页面图上，输出到 `页面\_check\` 检查 |
| `make_engine_lib.py` + `engine_lib\` | 引擎库：从《人人都是 UI 设计师》短视频的引擎副本快照（贴纸 / 来源小字 / 温柔男生估时 / BGM −9 dB），`scenes_lib.js` 是本系列自己写的（pageShot 深色页高亮、photoShot、big） |
| `gen_episode.py N\|all` | 从数据生成 / 刷新某一期：`new_short.py` 建目录 + 引擎 + 台本 + `scenes.js` + 页面图 / 照片 |
| `check_all.py [N…] [--real]` | 逐期 `build_timeline` → `check_subs` → `prep_frames` → 静帧，汇总到 `_check_all.log` |
| `build_fish_doc.py` / `split_voice_export.py` | 6 期合成一份 Fish 整稿（95 句，一个空白项目一次键入 / 生成 / 导出）；导出 zip 按 metadata.csv 核对后拆回各期的 `tts\seg_raw\final\` |
| `series_covers.py` | 封面候选（作者照 / 页面截图加橙色高亮 / X 横幅 × 3 比例）→ 各期 `制作\04_封面\` |
| `series_publish.py` | 标题 3×4、简介、话题、标签写进各期 `投稿信息.json` |
| `_patch*.py` | 一次性补丁（留着当记录，可删） |

## 做法要点 / 踩的坑

- 页面截图的高亮匹配：Substack 的 `<em>` 会把一句话切成几个文字节点，技能引擎的 `capture_pages.py` 逐节点匹配会退回整块高亮；这里改成“拼接全部文字节点再映射回 Range”。
- 敏感原文不能带进画面：“Shorter lessons” 列表里 23（比特币）、27（戒酒 / 性病）、30（死亡）和 13 里 heroin / su!cide 都在相邻行，页面截图要紧贴要讲的那一行（`li_range` / `para_lines`），并检查底部几行像素是不是背景色。
- 单句片段在 640 宽下只有一行小字、框里很空：用 420 宽视口重截，折成 2–4 行，放大约 1.5 倍。
- dcg 钩子会把命令里 JS 的 `=>` 误判成重定向而拦掉整条命令：把补丁脚本用 Write 写成文件再运行，别在命令行里内联 heredoc。
- Fish：6 期合成一份整稿，只开一次空白项目（95 句 / 约 2400 字符），其余步骤照技能 `references/voice.md`。

- **封面（2026-10-05 夜用户改版）**：`make_cover_photobg.py`——文章配图铺满做背景、字写在图上，字样统一“2800万浏览 / 推特万字长文 / 解读(N)”，候选 A 整张 / B 紧裁到脸 × 3 比例；旧框版挪进各期 `制作/04_封面/旧版_框版/`，`series_covers.py` 已被取代。
