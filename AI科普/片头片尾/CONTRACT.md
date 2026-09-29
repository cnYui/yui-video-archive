# UE 片头 / 片尾动画 — 设计与技术规范

## 背景
- 创作者名字：**UE**。B 站 AI 科普系列（暂定名《拆开AI看看》），受众是对 AI 好奇的普通年轻人，调性：聪明、友好、干净、"有一点门槛但好懂"。
- 讲解员是虚拟形象（图片暂未提供），片头片尾**不要**画人物。
- 片头和片尾是**同一套品牌包装**：共用配色、字体、核心图形母题。

## 片头 intro（3.0–4.0 秒）
- 用户原话："简单的科技符号或者 AI 图标的转场，然后我的名字叫 UE，让它出现一下。"
- 必须：科技符号 / AI 图标的转场动画 → "UE" 清晰出现，完整可读至少 ~1 秒 → 干净收尾，方便直接切进正片（比如擦除、闪白、推镜穿越到纯色）。
- 数据：`window.__DATA__ = { name: "UE", tagline: "" }`。tagline 默认为空，设计必须在没有 tagline 时就完整好看；有 tagline（如"拆开AI看看"，≤10 个汉字）时也要能放下。没有 `__DATA__` 时用上面的默认值。

## 片尾 outro（4.5–5.0 秒，不能超过 5 秒）
- 用户原话："展示本期视频的素材来源、拍摄设备、剪辑设备、需要致谢的人，最后再感谢用户看到最后。" 以及"需要有可编辑的动画展示，比如：拍摄：Pocket 4P / 剪辑：ChatCut / 视频剪辑模型：Opus 5.5。'感谢大家看到最后'这句话也写在屏幕上。"
- 数据（可编辑，每期不同）：
  ```json
  { "items": [ { "label": "拍摄", "value": "Pocket 4P" }, ... ], "closing": "感谢大家看到最后", "signature": "UE" }
  ```
  - `items` 1–6 条；label ≤ 6 个汉字；value 最长约 30 个字符（中英混排）。**布局必须自适应**：6 条 + 长 value 不能溢出、不能挤成一团（自动缩字号 / 换列 / 调行距）。
  - `closing` 必须出现在屏幕上；`signature`（UE）以小标识出现，呼应片头。
  - 默认数据见 `outro/data.json`（3 条），压力测试数据见 `outro/data.stress.json`（6 条长文本）。没有 `__DATA__` 时用 `outro/data.json` 的内容作默认值（直接写进页面里）。
- 可读性：所有 credits 条目**同时完整可见至少 2.0 秒**；最后一帧是干净的定格画面（视频在这里结束）。

## 通用视觉要求
- 1920×1080，60fps。文字留在 5% 安全边距内。
- 动效要有质感：缓动（不要 linear 匀速）、错峰叠加、2–3 个节奏重音，不抖动、不闪烁、没有突兀跳帧。
- 不要照抄任何公司的 logo（OpenAI 结、Claude 星芒、Gemini 四角星等）；通用符号（`{ }`、`</>`、芯片、神经网络节点、光标、方块）可以用。
- 不用 emoji（字体回退不可控），图标一律用 SVG / Canvas 自己画。

## 技术规范（必须遵守，否则渲染会出错）
- 每个动画是一个独立 HTML 文件，`html, body` 固定 1920×1080、`margin:0; overflow:hidden`，body 要有明确背景色。
- 页面必须设置 `window.DURATION = <秒>`。
- 渲染器是**逐帧定位**的：每帧会暂停所有 CSS 动画 / Web Animations 并把 `currentTime` 设为 t，再调用 `window.renderAt(t)`（如果定义了）。所以：
  - 可以用 CSS `@keyframes`（配合 animation-delay）、Web Animations API、或在 `renderAt(t)` 里用 Canvas/JS 按 t 画。
  - **禁止**依赖真实时间：`requestAnimationFrame` 循环、`setTimeout`、`Date.now()`、`performance.now()`、CSS `transition`。
  - 随机数必须用固定种子（例如 mulberry32），同一个 t 永远画出同一帧。
  - 依赖数据的布局在脚本加载时同步完成（或设置 `window.__READY__ = false`，布局完成后改为 true）。
- 字体只能用 `fonts/fonts.css` 里的：`'Noto Sans SC'`（中文正文/标题）、`'Space Grotesk'`、`'JetBrains Mono'`、`'Orbitron'`、`'Unbounded'`、`'ZCOOL KuaiLe'`（中文可爱体）。全部 OFL 可商用。不要用系统字体（微软雅黑有商用版权风险）。
- 不加载任何网络资源。

## 渲染命令（在 ue-packaging 目录下运行）
```bash
python render.py <html> --data <json> --sheet <out.png>          # 16 格联系表，最快的检查方式
python render.py <html> --data <json> --stills 0.5,1.8 --stills-dir <dir>   # 指定时刻的单帧 PNG
python render.py <html> --data <json> -o <out.mp4>               # 60fps H.264 成片
```
渲染器会报告 JS 报错和字体加载失败（退出码 2）。用 Read 工具打开 PNG 可以直接看画面。
