# 片头片尾定稿（对话气泡 + 信纸），同步到所有技能，所有视频必加（2026-10-03）

## 用户要求

> 用片头二，然后把片头片尾统一同步到所有skill中，你加一个片头片尾的路径到所有的skill中，要求所有生成的视频都需要使用片头和片尾

“片头二” = 2026-10-02 第二轮品牌色候选里的「对话气泡」（`AI科普/片头片尾/候选2026-10/品牌色版/2_对话气泡/`）；片尾 = 同一轮的 B 版信纸换 Claude 品牌色（`品牌色版/outro/`）。设计过程见 `20261002-220024-intro-outro-redesign-candidates_CN.md`。

## 做了什么

### 1. 定稿进共用模板 `AI科普/片头片尾/`

- 旧“终端小票”版（intro/、outro/、README.md、CONTRACT.md、out/ 里的样片）挪到 `AI科普/_旧稿/片头片尾_终端小票_20261003/`（git 历史里也有）。
- `intro/index.html` + `data.json`（`{name: 悠一, role: AI鼓励师, endColor: #FFFFFF}`），4.8 s。
- `outro/index.html` + `data.json`（assemble 的底稿：`references: []`，致谢两项示例，会被每期数据覆盖）+ `data.example.json`（完整例子），9.0 s。
- `common/pack.js`（从候选复制，**加了 device pixel ratio**：`setup()` 按 FW×1080×dpr 分配画布，每帧 `P.reset(ctx)`；add_to_video 给 4K 输入开 `device_scale_factor 2`，以前 Canvas 页面会被放大发虚）、`common/brand.js`（品牌色 + 符号链）、`common/handdata.js`（`build_handdata.py` 生成：GB2312 一级 3755 字 + ASCII + 标点，1.6 MB，不进 git；任意感谢语都能逐笔手写）。
- `fonts/fonts.css` 加了 Poppins（Medium / SemiBold / Bold）和马善政（OFL，文件不进 git）。
- 片尾页面的数据合并改成“第一个非空数组”：assemble 把 episode 的 `outro_items` 合进 data.json，data.json 里空的 `thanks` 不能盖掉它。
- `pack_info.py`：路径 + `intro_seconds()` / `outro_seconds()`（读页面 `window.DURATION`）+ `ADD_TO_VIDEO`。各技能的 SRT / 章节脚本从这里读，模板再换也不用改脚本。
- `render.py` 加 `--width`（传 `window.__CANVAS__`），联系表按宽画面比例。
- `README.md` 重写（用法、数据、品牌色出处、技术约定、历史）。

### 2. 流水线脚本

| 文件 | 改动 |
|---|---|
| `AI科普/skill/yuanlai-ruci-episode/scripts/epcommon.py` | `INTRO_DEFAULT` 3.8 → 4.8、`OUTRO_DEFAULT` 4.8 → 9.0（读不到页面时的兜底） |
| `…/assemble.py` | 片尾数据加 `references = episode.outro_references`；文档串 |
| `…/new_episode.py` | episode.json 模板加 `"outro_references": []`，说明里写清三项都要问用户 |
| `…/add_to_video.py`、`build_timeline.py`、`build_script.py` | 文档串 / 提示文字 |
| `AI日报/skill/ai-daily-news/scripts/assemble_wide.py` | **片头片尾改成 2340 原生渲染**（data 带 `canvas`，删掉 1920 渲染后补边的 WIDEN_VF），加尺寸检查；片尾传 `references` |
| `…/make_episode.py` | 新增 `outro_refs(news)`：每条新闻一行“标题（来源名 / 来源名）”写进 `outro_references`；`outro_items` 只剩形象、视频制作模型（来源不再挤在致谢里） |
| `Way to AGI/…/assets/template/制作/03_成片/export_srt.py` | `INTRO = pack_info.intro_seconds()`（以前写死 3.8） |
| `OpenAI相关/…/assets/engine-template/common.py` | `INTRO_SEC = pack_info.intro_seconds()`（以前写死 3.8） |
| `Way to AGI/…/build_timeline.py`、`scripts/new_episode.py` | 文字说明 |

### 3. 技能文档：每个出视频的技能都加「片头片尾（所有视频必加）」一节

路径表 + 本技能怎么加 + 时长从 `pack_info.py` 读 + 片尾每期问用户 + SRT / 章节加 4.8 s + 交付前自查。

- `yuanlai-ruci-episode`：SKILL.md（路径表、新一节、开工前要问的片尾项、附加一节）；references：`add-intro-outro.md`（重写）、`assemble.md`、`pipeline-contract.md`、`script.md`、`visuals.md`。
- `ai-daily-news`：SKILL.md（路径表、新一节、新闻来源进参考文献栏、render 步骤说明）。
- `way-to-agi-episode`：SKILL.md（路径表、新一节、第 6 / 7 步、投稿章节时间）、`references/pipeline.md`、`publish.md`。
- `cs-grad-ai-episode`：SKILL.md（路径表、新一节、第 7 / 8 / 10 步、原则）。
- `openai-episode`：SKILL.md（硬性要求第 10 条 + 新一节）、`references/pipeline.md`、`subtitles.md`。
- `claude-code-cover`、`openai-cover`：只做封面，末尾加「视频本身：片头片尾必加」指过去。
- `bilibili-reply` 不出视频，没加。
- 合集 README：`独立视频/`、`AI实操/`、`Claude Code相关/`、`OpenAI相关/` 都写了“片头片尾必加”和命令。
- `AGENTS.md`：「片头片尾：所有视频必加，所有合集共用一套」一节重写；目录树、CS 研究生、给任意视频加片头片尾、日报来源、待办（旧视频 / 已做好未投稿的视频要不要换新片头片尾；日报 2340 原生渲染这条划掉）。

## 验证

- `add_to_video.py` 给 3 秒 2340×1080 测试视频加片头片尾：输出 16.82 s = 4.80 + 3.00 + 9.00，2340×1080、30 fps、有音轨；接缝处抽帧正常。
- assemble 用的 `scripts/render.py`（data 带 canvas，30 fps）：片头 144 帧、片尾 270 帧，都是 2340×1080，退出码 0。
- 4K（`device_scale_factor 2`）：画布 3840×2160，名字边缘清晰。
- 日报片尾用 10-03 那期的 7 条新闻试排：参考文献一栏放得下（两条折两行），致谢两项。
- Way to AGI / OpenAI 模板 `-W error` 导入通过，读到 4.8。

## 没做 / 待用户定

- 已做完的视频没有重出。按新规则，**已做好但还没投稿的**（独立视频 OpenAI DevDay 解读 6 条、dots 中文同传等）应该换新片头片尾再投（SRT 也要按 4.8 s 重出），要不要做问用户。已发布的不动。
- 日报明天（10-04）的 routine 是新片头片尾的第一次全自动运行；`make_episode.py`、`assemble_wide.py` 的改动只在副本数据上试过渲染，没有整期跑过。
