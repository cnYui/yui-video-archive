# 人人都是 UI 设计师：20 条设计军规（长视频，约 8:30 + 片头片尾）

把 X 用户龙海（@longhaiqwe123）2026-10-03 的长文《人人都是 UI 设计师》做成一条长视频：文章从《Refactoring UI》里精选 20 条设计规则，每条配一张“错误做法 / 正确做法”的前后对比图；视频逐条过，画面全是真实素材（推文、书官网、20 张对比图、墨问笔记页面），不放整屏文字卡片。

- 素材（共用，短视频也能用）：`独立视频/素材/2026-10_人人都是UI设计师/`（文章全文 JSON / Markdown、21 张原图、下载脚本、来源说明；整个 `素材/` 不进公开仓库）。
- 形式：2340×1080、白底 + 淡淡的 AI 编程工具图标印花（`制作/00_整片/bg.png`，横版三张 `landscape_*.png` 里随机挑的一张，`bg.json` 记了哪张；2026-10-05 起横版视频都有）、全程画外音（Fish 故事工作室「温柔男生」S2 Pro）、中英双语字幕烧进画面（中文 52 px + 英文 30 px，y 922 起）、左栏目录 3 条（起步与层级 / 空间与排版 / 颜色与细节）+ 20 个进度点 + 当前规则卡片，片头 4.8 s / 片尾 9.0 s 用共用模板。
- 引擎：照 Claude Code相关 的引擎模板（`Claude Code相关/skill/claude-code-episode/assets/engine-template/`）改的，**新增了“文章 + 配图”这一类视频要用的几种镜头**（见下），以后“把一篇带图的 X 文章 / 博客做成长视频”可以直接拷这个目录。

## 目录
| 路径 | 内容 |
|---|---|
| `台本/script_src.py` | 台本数据源（开场 / 20 条规则 / 结尾，每句 zh / say / en）；`python script_src.py` 生成 `录制稿.json`、`plan.json`、`rules_meta.json` 并检查字幕宽度 |
| `台本/steps.json` | 每条规则“讲到哪句 / 哪个词时，焦点在 ✕ 还是 ✓、亮哪几个高亮框”，数据覆盖自动生成的步骤（自动步骤按台词里的“左边 / 右边”排） |
| `台本/marks/marks_*.json` | 20 张图的面板位置（✕ / ✓ 两个面板的外框）和要框出来的差异点（原图像素坐标），两个标注子代理量的 |
| `台本/事实核对.md` | 每条台词的依据、图和文章对不上的地方、不能写的 |
| `制作/00_整片/` | 引擎：`index.html` `engine.js` `scenes.js`（`ruleShot` 规则对比镜头、`pageShot` 页面录屏、`tocShot` 书目录滚动 + 计数、`wall` 缩略图墙、`imgStill` 单图推近）、`build_rules.py`（合并标注 / 台本 / 图片 → `rules.js`）、`capture_pages.py`（推文 / 书官网 / 墨问页面截图 + 高亮位置）、`build_timeline.py` `mix_audio.py` `render_all.py` `finish.py` `qa_mix.py` |
| `制作/02_配音/` | 配音：`say_lines.txt`（逐句要念的字）、`import_segments.py`（整稿 zip）、`import_regen.py`（重生成几句的 zip）、`build_voice.py [--qa]`、`qa_rest.py`、`check_names.py`（英文识别器听专名） |
| `制作/04_封面/` | `make_cover_framed.py` → 候选 A / B / C × 3:4 / 16:9 / 4:3 + `封面_总览.png`（白字 + 橙字、黑描边、框里放 ✕ / ✓ 对比图，橙色印花底；`封面_选定_*` 先放 A，等用户选）；第一版进 `_旧稿/` |
| `make_submission.py` → `投稿信息.json`、`制作/_desc_final.txt` | B 站标题候选 / 标签 / 简介（含章节时间） |

## 新增的镜头（以后同类视频直接用）
- **规则对比镜头 `ruleShot`**：对比图的 ✕ 面板 / ✓ 面板分别裁出来。三种视图：`both`（两个面板叠放或并排，右侧 / 下方说明栏，按宽高自动选能放得最大的）；`L` / `R`（讲到哪边，那个面板从叠放位置“推”到铺满演示区，说明条在下方，讲完缩回；放大不到 1.25 倍的图改成另一边变暗）。高亮框带短标签（优先放在框右边，避开别的框）。图 13 这种上下两层的图用两套面板（`sets`），按讲到的句子切换。
- **缩略图墙 `wall`**：20 张 ✓ 面板铺成 5×4，来一张亮一张，说到哪条哪张放大发光。
- **书目录滚动 `tocShot`**：官网目录（点“See all the chapters”展开后的 50 章）整页滚动，对应章名依次刷荧光笔，右上角计数“文章覆盖 N / 50 章”。
- **页面镜头 `pageShot`**：深色页面（书官网首屏）里荧光笔看不见，改成橙色边框；支持 `@rect:x,y,w,h` 手动框选。
- **左栏**：目录 + 20 个进度点 + 当前规则卡片（编号、标题、书里的英文章名和页码、“记住”一句），没有规则时目录垂直居中。

## 重做流程
```bash
cd 台本 && python script_src.py                       # 改台词后
cd ../制作/00_整片
python capture_pages.py                               # 页面截图（只在页面要重截时）
python build_rules.py                                 # 标注 / steps 改了之后
python build_timeline.py && python prep_frames.py     # 配音时长变了之后
python render_all.py --stills-segs                    # 每个场景 3 张静帧 + 联系表，逐张看
python mix_audio.py && python render_all.py           # 4 路渲染（先 ListAgents 看别的会话在不在渲，空闲内存 < 6 GB 用 RENDER_WORKERS=3）
python qa_mix.py && python finish.py                  # 混音逐句复核、加片头片尾、手机预览、三份 SRT
```
