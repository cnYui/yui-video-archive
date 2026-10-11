# 片头 / 片尾候选 · Claude 品牌色版（2026-10-02 第二轮）

用户看过第一轮（纸纹小主角三版）后：“都不太好看。你按照当前使用的开场和收尾，当前的开场的风格我很喜欢，从计算机的符号一路变形变化成悠一，但是配色我不是很喜欢，你可以查一下 claude 官方的品牌色，然后用品牌色制作三种开场；收尾的话，你用相同的 claude 品牌强调色，用 B 版本的结尾的视频即可，修改一下配色。claude 品牌色中，白色用来做大背景，橙色和黄色用来强调。”

片头方向定稿：**方向 2「对话气泡」**（用户：“方向 2 是对的，把 AI 这个 LLM 元素加进去”），另两版一起做出来对比。

**2026-10-03 定稿**：用户“用片头二”。片头 2 + 这里的片尾已经复制进正式模板 `AI科普/片头片尾/intro|outro`（路径改成模板自己的 `common/`、`fonts/`，pack.js 加了 device pixel ratio），所有视频必加；这里只作设计存档，不要再从这里取文件。

## 品牌色（来源）

| 用途 | 色值 | 出处 |
|---|---|---|
| 大背景 | 米白 `#FAF9F5` | Anthropic 官方 brand-guidelines 技能（github.com/anthropics/skills）的 Light；claude.dev 深色主题正文色 |
| 墨色（线条、字） | `#141413` | 同上 Dark；claude.dev `--bg` |
| 强调 · 橙 | `#D97757`（深橙 `#C15F3C`） | 同上 Orange / claude.dev `--accent`、`--accent-deep` |
| 强调 · 黄 | `#F5DB9A` | claude.dev 像素宇航员调色板里的小星光黄（`Claude Code相关/skill/claude-code-cover/assets/brand.json`） |
| 次要灰 | `#B0AEA5`、`#E8E6DC` | brand-guidelines 的 Mid Gray / Light Gray |
| 字体 | Poppins（标题，OFL）+ Noto Sans SC | brand-guidelines 指定标题字体 Poppins；中文仍用 Noto Sans SC。像素版用方舟像素字体 12px（OFL） |

规则：米白做大背景，橙、黄只做强调（原子、高亮、标签、朱印），不引入别的色相；片头收尾落到纯白 `#FFFFFF`，接白底正片不闪。

## 三版片头（都从现行片头的符号链开始：`>` → `{ }` → `</>` → 芯片；橙色“原子”一路不断）

| 版本 | 时长 | 符号链之后 |
|---|---|---|
| **1 打字机 · 发送** `1_打字机/` | 4.3 s | 芯片收成光标 → 先打小字“AI鼓励师”，回车换行打大字“悠一” → 光标闪两下 → 全选变成淡黄高亮 → 回车“发送”：整段像一条消息向上飞出 → 白 |
| **2 对话气泡（定稿方向）** `2_对话气泡/` | 4.8 s | `</>` 两个括号收成神经网络两端的节点，中间节点弹出、连线，一次前向传播（信号从左到右点亮每一层，橙色脉冲沿连线跑）→ 网络收进芯片，芯片标 **LLM** → 芯片滑到左下，右上冒出对话气泡 → 气泡里三个点跳动（正在输入，第三个点是橙色原子从芯片里飞出来的）→ 两个点变成“悠一”，橙点变成句号 → 气泡、芯片退场，名字移到画面中央 → 淡黄荧光笔划过，打出“AI鼓励师” → 句号闪一下 → 白 |
| **3 token 流 · 像素** `3_token像素/` | 4.8 s | 芯片滑到左边，从右侧引脚一粒一粒吐出 token（小方块），沿弧线飞过去拼成像素字“悠一”（方舟像素字体 12 px 点阵，一个点一个 token，最后一粒橙色的是句号）→ 像素“升采样”：方块收缩、清晰的黑体浮现，芯片退场、名字居中 → 像素小字“AI鼓励师”逐列亮起（淡黄底）→ 像素溶解到白 |

片头数据 `intro/data.json`：`{ "name": "悠一", "role": "AI鼓励师", "endColor": "#FFFFFF" }`（`endColor: "none"` 不淡）。

## 片尾（B 版信纸 × 品牌色）`outro/`

和第一轮 B 版同一条动画（飞机丢信、信纸展开、两栏写出、署名、朱印），只换配色：米白大背景、信纸纯白、墨色字、编号 / 标签 / 朱印橙色、两个栏目标题下的荧光笔划线淡黄、云浅灰。9.0 s。数据字段同第一轮（`references`、`thanks` / `items`、`closing`、`signature`、`references_title`、`thanks_title`），见 `../README.md`。

## 看效果

- `out/1_打字机_片头_2340.mp4`、`out/2_对话气泡_片头_2340.mp4`、`out/3_token像素_片头_2340.mp4`、`out/片尾_2340.mp4`（2340×1080、60 fps、无声）
- `out/品牌色三版_连播.mp4`：片头 1 → 2 → 3 → 片尾
- `out/*_sheet.png` 联系表，`out/stills_*` 单帧

## 重新出片

```bash
cd D:\大疆\AI科普\片头片尾\候选2026-10
python render_preview.py 品牌色版/2_对话气泡/intro/index.html --data 品牌色版/2_对话气泡/intro/data.json --width 2340 -o 品牌色版/out/2_对话气泡_片头_2340.mp4
python render_preview.py 品牌色版/outro/index.html --data 品牌色版/outro/data.json --width 2340 -o 品牌色版/out/片尾_2340.mp4
```

## 文件

```
品牌色版/
├─ common/brand.js      品牌色、现行片头的符号链（几何 + 保角变形 + 原子 + 引脚 + 标签）移植到 Canvas，三版共用
├─ fonts/               Poppins（Medium / SemiBold / Bold）、方舟像素字体 12px（zh_hans，woff2），brand-fonts.css；都是 OFL
├─ 1_打字机/ 2_对话气泡/ 3_token像素/   各 intro/index.html + data.json
├─ outro/               片尾（index.html 由 ../B_纸飞机/outro 改配色而来）+ data.json
└─ out/
```

依赖上一级的 `common/pack.js`（缓动、淡出、两栏排版、手写等）和 `common/handdata.js`（片尾手写标题）。

## 挑定之后要做的事

同 `../README.md` 最后一节：换到 `../../intro`、`../../outro`；时长变了（片头 3.8 → 4.3 / 4.8 s，片尾 4.8 → 9.0 s），所有写死 3.8 的脚本、技能文档要改；`assemble.py` / `assemble_wide.py` 传 `outro_references`；AGENTS.md 同步。
