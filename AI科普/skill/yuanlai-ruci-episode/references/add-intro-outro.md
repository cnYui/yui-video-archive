# 给任意视频加片头片尾（悠一）

**所有视频都要加片头片尾**（用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”）。**例外：短视频不加**（用户 2026-10-04：“短视频开头和结尾不要用开场和收尾的视频片段”）。《原LAI如此》《AI每日日报》由 assemble 自动加；其余所有视频（Way to AGI、CS 研究生、OpenAI相关、Claude Code相关、AI实操、独立视频、用户自己拍的视频）都用这个脚本加。

模板：`D:\大疆\AI科普\片头片尾\`（2026-10-03 起 Claude 品牌色版；以前的“终端小票”版在 `AI科普\_旧稿\片头片尾_终端小票_20261003\`）。

| | 内容 | 时长 |
|---|---|---|
| 片头 `intro\index.html` | 米白底，`>` → `{ }` → `</>` → 神经网络 → LLM 芯片 → 对话气泡里三个点变成“悠一”、橙点变句号 → 名字居中，黄色荧光笔划过“AI鼓励师” → 白 | 4.8 s |
| 片尾 `outro\index.html` | 纸飞机丢下一封信，展开成信纸：左栏参考文献、右栏致谢、感谢语、“—— 悠一”和朱印 | 9.0 s |

时长以页面的 `window.DURATION` 为准，脚本里用 `D:\大疆\AI科普\片头片尾\pack_info.py` 的 `intro_seconds()` / `outro_seconds()` 读，不写死。

```bash
python "D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py" "<视频.mp4>" --outro-data "<片尾.json>"
python "D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py" "<视频.mp4>" -o "<输出.mp4>" --outro-data "<片尾.json>"
python "D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts/add_to_video.py" "<视频.mp4>" --outro-data "<片尾.json>" --no-music
```

用技能里的这份：BGM 取 `素材\音频\bgm.wav`。`片头片尾\add_to_video.py` 是第 1 期时的旧副本，BGM 路径指向 `第01期_什么是API\制作\audio\bgm.wav`，不要再用。

- 输出默认在原视频旁边：`<名字>_片头片尾.mp4`，**原文件不动**。
- 片头片尾按原视频的分辨率和帧率渲染（4K 用 2 倍像素渲染，不是放大）；正片 H.264 不重编码，直接拼接，画质不变。
- 比 16:9 宽的视频（例如 2340×1080 = 19.5:9、3120×1440）：页面按视频的比例开成更宽的画布（高 1080，宽 = 视频宽 ÷ 缩放），并把 `canvas` 传给页面：内容居中、米白背景铺满全宽，不拉伸。脚本会打印 `intro / outro page 2340x1080 at scale 1`。
- 16:9 的视频（1920×1080、3840×2160…）用 1920×1080 的页面按比例渲染。比 16:9 窄的视频（4:3、竖屏）片头片尾暂不支持（会被拉伸）。
- 片头片尾下面垫一小段系列 BGM，比口播低约 7 dB；`--no-music` 改成静音。
- 片头最后淡到白（`intro\data.json` 的 `endColor`），接白底正片不闪。

## 片尾内容要先问

片尾是一页信纸：左栏“参考文献”、右栏“致谢”、底部感谢语和签名。每个视频的实际情况不同：**用户没告诉你就问**（本期用到了哪些论文 / 文档 / 官方页面 / 视频，要感谢谁、制作清单），不要用模板里的默认值。写成一个 JSON 传给 `--outro-data`（完整例子：`片头片尾\outro\data.example.json`）：

```json
{
  "references": [
    "Anthropic，Claude Fable 5.1 模型卡与发布说明，2026-09",
    "Vaswani et al.，Attention Is All You Need，NeurIPS 2017"
  ],
  "items": [
    {"label": "配音", "value": "悠一"},
    {"label": "剪辑", "value": "Claude Code（Opus 5.5）"},
    {"label": "特别感谢", "value": "评论区提问的每一位朋友"}
  ],
  "closing": "感谢观看，我们下期再见",
  "signature": "悠一"
}
```

- `references` 字符串，≤ 8 条，每条最多折 3 行；没有就写 `[]`，致谢一栏会占满整宽。
- `items`（也可以写成 `thanks`）`{label, value}`，≤ 8 条；label ≤ 4 字最好看。
- 栏目标题默认“参考文献”“致谢”，要改写 `references_title` / `thanks_title`。
- 字号按内容自动缩（42 → 20 px），4.5 s 前全部写完，之后定格。
- 标题、感谢语、签名是逐笔手写（`common\handdata.js`，GB2312 一级 3755 字 + ASCII；没有笔画的字用马善政字体补）。

不要改 `片头片尾\outro\data.json` 本身，把本次的 JSON 放在视频旁边（不要放会话临时目录：那里的路径可能超过 260 个字符，Windows 上 Python 打不开）。脚本自己的临时文件放在输出文件旁边（`_tmp_add_to_video_*`，跑完自动清掉）。

## 交付前检查

- `ffprobe` 看分辨率（和原视频一样）、帧率、时长 ≈ 4.8 + 原时长 + 9.0（脚本最后一行会打印）。
- 完整解码一遍（`ffmpeg -v error -i out.mp4 -f null -`）没有报错。
- 在两个接缝处各抽一帧看画面，听一下片头到口播的音量衔接；宽画面再看一眼片头片尾两边没有空白边、构图居中；片尾最后一帧看参考文献和致谢没有被截断。
- SRT / 章节时间要加片头时长（4.8 s），只对得上加完片头片尾的成片。
