# 短视频竖屏版式重设计（2026-10-04）——已定稿

用户选定：**版式 B + 边框 6（粗描边硬阴影）**，背景按方案 B 自带的墨色印花（三张印花每期随机挑一张已进技能模板）。完整记录：`D:\大疆\docs\ai\context\20261004-143000-short-video-layout-b-frame-third-person_CN.md`。

## 这个目录里有什么

| 文件 | 说明 |
|---|---|
| `版式A.png` / `版式B.png` / `版式C.png` | 三个版式方案样图（单框 + 链接条｜单框 + 数字卡｜双横屏，各带一种边框 + 一种背景） |
| `边框总览.png` | 7 种边框（原样 / 窗口式 / 胶带卡片 / 渐变描边 / 取景框 + REC / 粗描边硬阴影 / 显示器） |
| `背景总览.png`、`pattern_color.png` / `pattern_ink.png` / `pattern_orange.png` / `pattern_none.png` | 背景印花（1080×2340 透明 PNG，透明度已烤进去）；`_prev_all.png` 预览、`_icons_sheet.png` 图标总览 |
| `make_pattern.py` | 用 16 个 AI 工具图标生成印花（图标来自 `独立视频\2026-10_请选择你的AI-Harness框架阵营\制作\assets\logos`） |
| `make_layout_options.py` | 用真引擎（image-blaster 那条的 index.html + 真帧 + 真字幕）出上面的版式 / 边框 / 背景样图 |
| `port_to_template.py` | 把定稿版式移植进 `短视频\skill\short-video\assets\engine-template`（已跑过；原文件备份成 `*.bak_版式前`） |

## 状态

- 已移植进技能模板（index.html / engine.js / scenes.js / check_subs.py），技能文档（layout.md / script.md / SKILL.md）已更新；背景库（`assets/backgrounds/`、`new_short.py` 随机挑一张）是另一个会话做的，已保留。
- image-blaster 那条已用新版式 + 第三人称 + GitHub 链接条重渲（成片在 `独立视频\短视频\2026-10_image-blaster推荐\`）。
- 还没做过真正的 dual（叠放）成片；Tavus-Griffin 那条 dual 还是旧版式的副本。
