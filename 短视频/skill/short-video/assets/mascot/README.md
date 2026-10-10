# Claude 官方吉祥物（橙色像素“八爪鱼”）

用户 2026-10-06 看了《Claude官方教程》第 1 期出镜版的三个封面（人脸 / 循环图 / 确认框）说“都不太行”，要“带有 claude 八爪鱼形象的封面”。
**“八爪鱼”= 官方课（Claude Academy · Claude Code 101 · 上下文管理 CC101-06，30.4 s）动画里、Claude Code 欢迎屏上的那只橙色像素吉祥物**：12×8 方块，两个黑眼睛、两侧各一条胳膊、四条腿，品牌橙 #D97757。
它和 `claude-code-cover` 技能（Claude Code相关合集）里的“官方像素宇航员”不是一个东西——两个都是官方形象，别互相顶替，也别自己造别的角色（宇航员被退回过“不是 claude 的形象”）。

- `mascot_sprite.json`：`{"grid": ["..OOOOOOOO..", …8 行], "orange": [215,118,86], "block_src": 42}`，`O` = 橙、`K` = 黑（眼睛）、`.` = 空；从官方帧按 42 px 一格还原，**不重新上色、不改形状**。
- 画面脚本：`scripts/make_mascot_pictures.py <本条目录>` → `制作/04_封面/_src/M_A.png`（官方米色底 + 一只大的）/ `M_B.png`（深色终端底 + `> claude` 提示符）/ `M_C.png`（淡黄底 + 一大三小）；再写进 `candidates_framed.json`（`video` 指向它们，`big` 写压缩的钩子，贴纸写“官方教程 第N期”），`make_cover_framed.py` 加大字 + 边框。
- 什么时候用：**Claude / Anthropic 官方内容**（官方教程、官方新功能、Claude Code）的封面候选里至少放一个带吉祥物的；用户明说要才是首选（第 1 期他选的是 B：深色终端底）。别的公司的内容别用。
- 版权：形象和官方课画面一样归 Anthropic 所有；简介里写来源（“画面来自 Anthropic 官方 YouTube 频道与 Claude Academy，版权归 Anthropic 所有”）。
- 重新取样（官方换了形象时）：`ffmpeg -ss 30.4 -i CC101-06_context-management__eW3oTyfeWZ0.mp4 -frames:v 1 f.png`，在米色底上找橙色连通块，按眼睛方块（≈ 42 px）的大小切成网格即可（第 1 期出镜版做时的脚本思路）。
