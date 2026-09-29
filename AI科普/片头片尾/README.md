# 片头 / 片尾 · 终端小票（Terminal Receipt）

片头和片尾都是 HTML 动画，改一下 JSON 就能重新出片，不需要打开任何剪辑软件。

> **2026-09-29 起名字统一为“悠一”**（用户：“之后统一换成悠一”）：`intro/data.json` 的 `name`、`outro/data.json` 的 `signature` 都是 `悠一`，两个页面在没传名字 / 签名时的默认值也改成了悠一。片头走下面说的“光标逐字打字”版，片尾是文字印章；时长、节奏不变（3.8 s / 4.8 s）。新成品：`out/悠一_intro_2340.mp4`（2340×1080、30 fps）、`out/悠一_intro_sheet.png`。下文里的 UE 字标仍然保留：只有明确写 `"UE"` 才会出现。改之前的数据和页面备份在 `AI科普/_旧稿/片头片尾_UE数据_20260929/`。

```
ue-packaging/
├─ intro/index.html      片头（3.8 秒）
├─ intro/data.json       片头数据：名字、tagline
├─ intro/data.tagline.json   带 tagline 的示例
├─ outro/index.html      片尾（4.8 秒）
├─ outro/data.json       片尾数据：制作清单、感谢语、签名
├─ outro/data.stress.json    6 条长文本的压力测试示例
├─ fonts/                字体（全部 SIL OFL 1.1，可商用）
├─ render.py             逐帧渲染器（HTML → MP4 / PNG）
├─ out/                  成片与联系表
└─ _archive/、_qa/        制作过程中的评审和测试文件，与成片无关，确认不需要后可以自行删除
```

---

## 一、片尾：改 `outro/data.json`

```json
{
  "items": [
    { "label": "拍摄", "value": "Pocket 4P" },
    { "label": "剪辑", "value": "ChatCut" },
    { "label": "视频剪辑模型", "value": "Opus 5.5" }
  ],
  "closing": "感谢大家看到最后",
  "signature": "悠一"
}
```

| 字段 | 作用 | 说明 |
|---|---|---|
| `items` | 小票上的每一行“label ······ value” | 建议 1–6 条（最多支持 8 条，多出的会被忽略）。行首编号 01/02… 和底部的 `ITEMS 03` 会自动计算 |
| `label` | 左侧灰色标签 | 建议不超过 6 个汉字 |
| `value` | 右侧内容 | 最长约 40 个字符，中英混排都可以 |
| `closing` | 屏幕上的大字感谢语 | 默认“感谢大家看到最后”。由橙色光标一个字一个字打出来，打完后光标轻闪两下再常亮 |
| `signature` | 橙色印章里的签名 | 默认 `悠一`（文字印章）。写 `UE` 时用和片头一样的自绘字标；写别的名字会自动换成文字印章 |
| `title`（可选） | 小票标题 | 不写就是“本期制作清单” |

**增删条目**：在 `items` 里复制或删除一行 `{ "label": "…", "value": "…" }`。注意两行之间要有英文逗号，最后一行后面不要逗号。例如加一条致谢：

```json
    { "label": "视频剪辑模型", "value": "Opus 5.5" },
    { "label": "特别致谢", "value": "评论区的 @观众昵称一 和 @观众昵称二" }
```

**排版是自动的**，不用手动调字号：

- 条目少的时候字大（默认 3 条时正文约 48px，感谢语约 72px）；条目多、文字长的时候会自动缩小字号、加宽小票，保证不溢出、不出安全框。
- value 太长时最多折成两行。如果内容里有 `·`、`、`、`，`、`/` 这类分隔符，会优先在分隔符处断开，并且让两行长度尽量接近。`@昵称` 不会被拆开。
- 感谢语太长时会在逗号后面自然折成两行，逗号不会出现在行首；两行时光标会跟着换行继续打字。
- 某一行只写了 `label`、`value` 留空：只显示标签，不画点线；只写了 `value`、`label` 留空：这一行作为左对齐的备注显示；两个都空的行会被自动跳过。
- 所有条目在打印完成后同时完整可见：3 条时约 3.8 秒，6 条时约 3.5 秒。最后约 0.58 秒是完全静止的定格画面。

## 二、片头：改 `intro/data.json`

```json
{
  "name": "悠一",
  "tagline": ""
}
```

| 字段 | 作用 | 说明 |
|---|---|---|
| `name` | 片头出现的名字 | 默认 `悠一`（光标逐字打字的版本：芯片收成下划线光标，打出“悠一_”）。写 `UE` 时显示自绘单线字标（E 的中横是橙色“芯片核心”）。写别的名字（如“小元Lab”）也是光标逐字打字的版本 |
| `tagline` | 名字下方的一行小字 | 默认留空；可以写“拆开AI看看”这类不超过约 10 个汉字的短句，会跟着光标逐字打出 |
| `endColor`（可选） | 片头最后约 10 帧的纯色 | 默认墨黑 `#141414`，接暗色正片或片尾都不会闪。如果正片开头很亮，可以改成 `"#EDEAE3"`（纸白） |

片头节奏（名字是 UE 时；悠一等其他名字在 1.5 秒芯片收成光标、1.8 秒起逐字打出，其余相同）：0.2 秒敲出 `>` → `{ }` → `</>` → 1.3 秒变成 AI 芯片 → 芯片先左右分开成 `[ ]`，左半边立起来弯成 U，右半边翻身成 E；芯片核心缩成一小块橙色嵌在墙里跟着走，最后从 E 的竖笔里弹出成为橙色中横，约 1.9 秒成形 → 完整停留约 1.2 秒 → 像终端里全选删除一样把名字清掉 → 光标张开成纯色画面，最后 10 帧纯墨黑，可以直接硬切进正片。

## 三、重新出片

先进入 `ue-packaging` 目录：

```bash
cd ue-packaging

# 片头
python render.py intro/index.html --data intro/data.json -o out/悠一_intro.mp4

# 片尾
python render.py outro/index.html --data outro/data.json -o out/悠一_outro.mp4

# 只想快速看效果：出一张 16 格联系表（几秒钟就好）
python render.py outro/index.html --data outro/data.json --sheet out/悠一_outro_sheet.png

# 看某几个时刻的单帧
python render.py outro/index.html --data outro/data.json --stills 1.5,4.7 --stills-dir out/stills
```

- 成片规格：1920×1080、60fps、H.264（MP4）。
- 如果想保留多个版本，可以复制一份 JSON（比如 `outro/ep12.json`），用 `--data outro/ep12.json` 指定，输出文件名也相应改一下。
- 渲染器如果报 `PAGE ERRORS`（退出码 2），多半是 JSON 格式写错了（常见原因是漏了逗号或引号）。
- 运行环境：Python 3、`pip install playwright pillow` 后执行 `playwright install chromium`，并且需要系统里有 `ffmpeg`。
- MP4 里写入了 BT.709 色彩标记（色域、传递函数、矩阵），导入剪辑软件或上传 B 站时颜色不会被误判。
- 同一个时间点每次渲染得到的画面相同。唯一的例外是片尾印章的颗粒纹理（SVG 滤镜）：单独抽帧和整段渲染相比，个别像素可能差 1–5 个色阶，肉眼看不出来，也不影响成片。

## 四、字体与版权

全部使用 `fonts/` 里的字体，均为 **SIL Open Font License 1.1**，可免费商用（包括 B 站商业视频），授权文件在 `fonts/OFL-*.txt`：

- Noto Sans SC：中文标题、标签、感谢语
- Space Grotesk：英文 value、芯片上的 “AI”
- JetBrains Mono：CREDITS / RECEIPT / ITEMS、条码数字、行首编号
- UE 字标和印章是自绘 SVG 线条，不依赖任何字体。

不使用任何系统字体，也不加载任何网络资源；图标全部是自己画的，没有使用任何公司的 logo。
