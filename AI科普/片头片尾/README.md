# 悠一片头片尾（所有视频共用，必加）

**用户 2026-10-03：“用片头二，然后把片头片尾统一同步到所有 skill 中……要求所有生成的视频都需要使用片头和片尾。”**

所有合集（原LAI如此、AI每日日报、Way to AGI、AI时代计算机专业研究生如何用AI、OpenAI相关、Claude Code相关、AI实操）和独立视频都用这一套，不另做、不省略。**例外：短视频开头结尾都不加**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”），短视频走技能 `短视频/skill/short-video/`。各技能的 SKILL.md 里都有「片头片尾（所有视频必加）」一节指向这里。

| | 文件 | 时长 | 内容 |
|---|---|---|---|
| 片头 | `intro/index.html` + `intro/data.json` | 4.8 s | Claude 品牌色「对话气泡」：`>` → `{ }` → `</>` → 神经网络（前向传播点亮每一层）→ 收进标 **LLM** 的芯片 → 对话气泡里三个点跳动（第三个是橙色原子）→ 点变成“悠一”、橙点变句号 → 名字居中，淡黄荧光笔划过“AI鼓励师” → 淡到白 |
| 片尾 | `outro/index.html` + 每期的数据 | 9.0 s | 纸飞机丢下一封信，信展开成一页信纸：左栏**参考文献**、右栏**致谢**、感谢语、“—— 悠一”和朱印，之后定格 |

时长以页面里的 `window.DURATION` 为准。脚本里不要写死，用 `pack_info.py`：

```python
import sys; sys.path.insert(0, r"D:\大疆\AI科普\片头片尾")
from pack_info import intro_seconds, outro_seconds, ADD_TO_VIDEO     # 4.8, 9.0, add_to_video.py 的路径
```

SRT、B 站 / YouTube 章节时间 = 正片时间 + `intro_seconds()`。

## 怎么加到视频上

| 场景 | 做法 |
|---|---|
| 《原LAI如此》 | `assemble.py` 自动渲染并拼接；片尾数据 = `episode.json` 的 `outro_references`、`outro_items`、`outro_closing` |
| 《AI每日日报》 | `assemble_wide.py` 自动（2340 宽原生渲染）；`make_episode.py` 把当期新闻写进 `outro_references` |
| 其他所有视频 | `python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data <片尾.json> -o <成片.mp4>`（说明：`AI科普\skill\yuanlai-ruci-episode\references\add-intro-outro.md`） |

## 数据

片头 `intro/data.json`（一般不改）：

```json
{ "name": "悠一", "role": "AI鼓励师", "endColor": "#FFFFFF" }
```

`endColor` 是片头最后淡到的颜色（默认白，接白底正片；`"none"` 不淡）。

片尾（**每期问用户**，不沿用上一期；完整例子 `outro/data.example.json`）：

```json
{
  "references": ["Anthropic，Claude Fable 5.1 模型卡与发布说明，2026-09", "…"],
  "items": [ { "label": "配音", "value": "悠一" }, { "label": "剪辑", "value": "Claude Code（Opus 5.5）" } ],
  "closing": "感谢观看，我们下期再见",
  "signature": "悠一"
}
```

| 字段 | 说明 |
|---|---|
| `references` | 参考文献，字符串，≤ 8 条，每条最多折 3 行；没有就 `[]`（致谢占满整宽） |
| `items`（或 `thanks`） | 致谢 / 制作清单 `{label, value}`，≤ 8 条，label ≤ 4 字最好看 |
| `references_title` / `thanks_title` | 栏目标题，默认“参考文献”“致谢” |
| `closing` | 感谢语（逐笔手写） |
| `signature` | 签名，默认“悠一”；朱印取前两个字 |

`outro/data.json` 是 assemble 的底稿（会被每期的数据覆盖），不要往里写某一期的内容。

## 视觉规范（Claude 品牌色）

| 用途 | 色值 | 出处 |
|---|---|---|
| 大背景 | 米白 `#FAF9F5`（片尾信纸纯白） | Anthropic 官方 brand-guidelines 技能（github.com/anthropics/skills）的 Light；claude.dev CSS |
| 墨色 | `#141413` | 同上 Dark / claude.dev `--bg` |
| 强调 · 橙 | `#D97757`（深橙 `#C15F3C`） | 同上 Orange / claude.dev `--accent` |
| 强调 · 黄 | `#F5DB9A` | claude.dev 官方像素宇航员调色板的小星光黄 |
| 灰 | `#B0AEA5`、`#E8E6DC` | brand-guidelines 的 Mid Gray / Light Gray |

白做大背景，橙、黄只做强调（原子、荧光笔、编号、标签、朱印），不引入别的色相。字体：Noto Sans SC（中文）、Poppins（品牌标题字体，“AI”“LLM”）、马善政楷书（片尾手写缺字时兜底），都是 OFL，在 `fonts/`。

## 技术约定（改页面前看）

- Canvas 2D 逐帧绘制，画面只取决于 t：渲染器每帧调 `window.renderAt(t)`；没有 requestAnimationFrame、定时器、`Date`，随机数都用固定种子。
- 页面设 `window.DURATION`、开始时 `window.__READY__ = false`，字体加载完、排好版再设 `true`。
- 画面宽度：`window.__CANVAS__` > data 的 `canvas` [W, H] > 1920；1920 舞台居中，更宽时背景铺满。`device_scale_factor` > 1（4K 输入）时按设备像素出图（`common/pack.js` 的 `setup()` / `reset()`），不是放大。
- `common/pack.js`（缓动、两栏排版、逐笔手写、纸屑…）、`common/brand.js`（品牌色、符号链的几何和保角变形，从旧片头移植）、`common/handdata.js`（手写笔画表：GB2312 一级 3755 字 + ASCII + 标点；`python build_handdata.py` 重建；从 hanzi-writer-data 来，Arphic 授权，不进 git）。
- 片头片尾源文件只读：要改先在 `候选2026-10/` 那样的副本里试，用户确认再替换。

## 预览 / 出片

```bash
cd D:\大疆\AI科普\片头片尾
python pack_info.py                                                                   # 路径和时长
python render.py intro/index.html --data intro/data.json --width 2340 --sheet out/悠一_片头_sheet.png
python render.py outro/index.html --data outro/data.example.json --width 2340 -o out/悠一_片尾_2340.mp4
```

`out/` 里有当前版本的样片和联系表（不进 git）。

## 历史

- 2026-09-26 起：“终端小票”版（纸白 + 墨黑 + 橙 #FF4F1A，片头 3.8 s 符号变形后打出 UE / 悠一，片尾 4.8 s 制作清单 + 印章）。2026-10-03 挪到 `AI科普\_旧稿\片头片尾_终端小票_20261003\`。
- 2026-10-02 重新设计：第一轮纸纹小主角三版（A 鼓励球 / B 纸飞机 / C 铅笔灯泡）被否；第二轮按“现行片头的符号变形 + Claude 品牌色”做了三版片头（打字机 / 对话气泡 / token 像素）+ B 信纸片尾换品牌色。用户选了对话气泡。全部候选在 `候选2026-10/`，记录 `docs\ai\context\20261002-220024-intro-outro-redesign-candidates_CN.md`。
- 2026-10-03 定稿并同步到所有技能：记录 `docs\ai\context\20261003-093049-intro-outro-sync-all-skills_CN.md`。
