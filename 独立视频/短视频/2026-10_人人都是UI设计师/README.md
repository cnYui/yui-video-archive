# 人人都是 UI 设计师：5 条设计规则（竖屏短视频，66.6 s）

长视频《人人都是 UI 设计师：20 条设计军规》（`独立视频/长视频/2026-10_人人都是UI设计师/`）的竖屏短版：1080×2340，不加片头片尾，第三人称、配音「温柔男生」（Fish 故事工作室 S2 Pro）、中英双语字幕、版式 B + 边框 6 + 随机背景印花（`制作/00_整片/bg.json`）。文章是 X 用户龙海（@longhaiqwe123）2026-10-03 的长文，规则出自《Refactoring UI》；对比图用长视频的素材（`独立视频/素材/2026-10_人人都是UI设计师/图片/`，不拷）。

选的 5 条：13 颜色（钩子 + 色阶）、06 按钮分主次、09 间距 20 / 20 → 20 / 10、14 浅底深字、17 图上文字。结构：钩子 → 背书（推文 + 书官网）→ 5 条规则 → 泼冷水 → 金句。

| 路径 | 内容 |
|---|---|
| `人人都是UI设计师_竖屏短版_成片.mp4` / `_手机预览.mp4` / 三份 `_字幕.srt` | 成品（成片第 0 帧还没换成封面，用户选定封面后跑技能的 `cover_frame0.py`） |
| `台本/script_src.py` | 台本数据源（zh 字幕 / say 配音 / en 英文字幕）；`python script_src.py` 生成 `录制稿.json`、`plan.json`、`台本.md`、`制作/02_配音/say_lines.txt` |
| `制作/00_整片/` | 引擎：`build_panels.py`（读长视频的 marks 生成 `panels.js` / `pages.js`）、`build_timeline.py`、`mix_audio.py`、`render_all.py`、`finish.py`、`qa_mix.py`、`check_subs.py`；`stills/` 是静帧联系表 |
| `制作/02_配音/` | `say_lines.txt`、`import_segments.py`（Fish 导出 zip）、`build_voice.py [--qa]` |
| `制作/04_封面/` | 候选 A / B / C × 3:4 / 16:9 / 4:3 + `候选总览.png`（和长视频同一套，脚本在长视频的 `制作/04_封面/make_cover_framed.py`）；`封面_选定_*` 先放 A |
| `投稿信息.json` | 标题 3×4（`check_titles.py` 核过限长）、四个平台的默认项；用户回“封面 X 标题 Y 同意”后再写各平台字段 |

## 重做流程
```bash
cd 台本 && python script_src.py                       # 改台词后（say 变了要回 Fish 重配）
cd ../制作/02_配音 && python import_segments.py "<segments*.zip>" && python build_voice.py --qa
cd ../00_整片
python build_timeline.py && python prep_frames.py     # 配音时长变了之后
python render_all.py --stills-segs                    # 每个场景 3 张静帧 + 联系表，逐张看
python mix_audio.py && python render_all.py           # 4 路渲染（先 ListAgents 看别的会话在不在渲，空闲内存 < 6 GB 用 RENDER_WORKERS=3）
python qa_mix.py && python finish.py
```
记录：`docs/ai/context/20261005-105255-ui-designer-short-video_CN.md`。
