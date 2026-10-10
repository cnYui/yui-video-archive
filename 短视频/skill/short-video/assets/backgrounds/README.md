# 短视频背景库（每条随机挑一张）

用户 2026-10-04：“之前让你生成的背景图片有三张，你都加入到背景图片的选择中，每一期视频随机挑选一张作为背景即可”“这个要求写入skill中”。

| 文件 | 样子 |
|---|---|
| `pattern_color.png` | AI 编程工具图标（Claude Code、Codex、Trae、WorkBuddy、Cursor、Windsurf、Copilot、Gemini CLI……）原色印花，透明度约 11% |
| `pattern_ink.png` | 同一套图标，墨色单色，约 7.5% |
| `pattern_orange.png` | 同一套图标，橙色单色，约 12% |

- 都是 1080×2340 的透明 PNG（透明度已经烤进去），叠在米白底 `#FAF9F5` 上用；有印花时引擎不再画原来的淡点阵。
- 来源：2026-10-04 另一个会话做竖屏版式重设计时生成的（`D:\大疆\短视频\版式方案_20261004\`，`make_pattern.py`；用户当时的要求：“背景可以设计成低透明度的 AI 工具图标重复印花”）。图标取自 `独立视频\2026-10_请选择你的AI-Harness框架阵营\制作\assets\logos`（LobeHub 图标 + 各家官方图标）。
- **怎么用**：`scripts/new_short.py` 建一条时从这里随机挑一张（`--bg pattern_ink.png` 指定、`--bg none` 不用印花），复制成本条的 `制作\00_整片\bg.png`，选了哪张记在 `bg.json`；`build_timeline.py` 读 `bg.json`，引擎把它铺满整个画面。
- **加新背景**：1080×2340 的透明 PNG 放进这个目录就会进随机池（文件名以 `pattern_` 开头；`pattern_none.png` 不算）。重新生成用 `make_pattern.py`（它会把图写到自己所在的目录，并建 `_icons\`）。
- PNG 不进公开仓库（`.gitignore` 白名单不收图片），只在本机；脚本和这份 README 进仓库。

## 横版三张（2026-10-05 加）

用户 2026-10-05：“长视频背景也加上和短视频 skill 中相同的背景图片，你设计三张横版的图片，然后同步到 skill 中，之后横板视频也要随机选一张图片”。

| 文件 | 样子 |
|---|---|
| `landscape_color.png` | 同一套 AI 编程工具图标，原色，约 11% |
| `landscape_ink.png` | 墨色单色，约 7.5% |
| `landscape_orange.png` | 橙色单色，约 12% |

- 2340×1080 的透明 PNG（横版引擎的画面），图标大小 / 疏密和竖屏三张一样（76 px、间距 176×168、每行错半格、随机转 ±14°），种子不同；叠在引擎原来的白底上用（印花很淡，不影响读字）。
- 重新生成：`python make_pattern_landscape.py`（用 `make_pattern.py` 的 `make()`，`_icons\` 里有缓存）。
- **怎么用**：横版的新建脚本（`claude-code-episode` / `openai-episode` / `way-to-agi-episode` 的 `new_episode.py`）自动调 `pick_bg.py <本期 00_整片 目录>`，随机挑一张拷成 `bg.png`、写 `bg.json`（已经有 `bg.json` 就不再随机，重渲不会换；`--bg landscape_ink.png` 指定，`--bg none` 不用——不用时要把 `index.html` 里的 `url(bg.png)` 去掉）。引擎的 `index.html`：`html, body { background:#fff url(bg.png) 0 0/2340px 1080px no-repeat; }`。手工用：`python pick_bg.py <目录> [--pool landscape|pattern] [--bg 文件名|none]`。
- 横版池只认 `landscape_` 前缀、竖屏池只认 `pattern_` 前缀，互不串；加新的横版背景就把 2340×1080 透明 PNG 放进来，文件名以 `landscape_` 开头。
- **还没接的**：白板 / 黑板风的合集（AI科普 原LAI如此、AI日报、CS 研究生）引擎自带背景，没改；要不要也加印花，下次做这几个合集时先问用户。
- 第一条用上的：`独立视频\长视频\2026-10_人人都是UI设计师\`（`制作\00_整片\bg.json`）；封面（橙色印花底）也用同一套图标。
