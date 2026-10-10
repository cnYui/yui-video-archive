# 短视频版式重设计（版式 B + 边框 6）、背景印花、GitHub 链接条、第三人称（2026-10-04）

接 `20261004-111500-image-blaster-short-video_CN.md`。用户看完 image-blaster 成片后连着提了几条，这份记录它们和做法。

## 用户要求（原话，按先后）

1. “短视频的布局你需要重新设定一下，标题位置不变的情况下，视频页面可以向下移动一些，字幕也往下移动一些，三个元素中间保留大一些的间距，有的时候会出现两个横屏视频，这个也需要你设计一下，你用图片来展示即可，给我三个例子，我来选一下”
2. “github的链接你也可以在展示github截图的时候，在视频中展示几秒”
3. “短视频skill中，你也给展示的横屏视频做几种边框，不然一个视频放在上面很单调，你也可以设计一个背景图片，比如说是充满不同ai工具图标的 低透明度的重复印花的背景图片，claudecode codex trae workbuddy等等，用低透明度贴到当前米白色背景中”
4. “对了，短视频skill中加上一点，要使用第三人称来描述，而不是用 我 开头，比如当前视频就是作者第一人称的描述，需要你修改为第三人称，比如直接叫他推特的名字”
5. 看了样图后：“用方案B，边框为6”（B = 宽松版式，6 = 粗描边硬阴影；背景他没单独点，按 B 自带的墨色印花）。
6. （转给另一个会话的话）“之前让你生成的背景图片有三张，你都加入到背景图片的选择中，每一期视频随机挑选一张作为背景即可”——另一个会话（写 short-video 技能的）已做进模板。

## 做了什么

- **样图**（`D:\大疆\短视频\版式方案_20261004\`）：`make_layout_options.py` 用真引擎（image-blaster 的 index.html + 真帧 + 真字幕）出 `版式A/B/C.png`（每张：单框 + GitHub 链接条｜单框 + 数字卡｜双横屏，各带一种边框 + 一种背景）、`边框总览.png`（7 种：原样 / 窗口式 / 胶带卡片 / 渐变描边 / 取景框 + REC / 粗描边硬阴影 / 显示器）、`背景总览.png`（无 / 原色 / 墨色 / 橙色）。浅灰块标平台遮挡区（顶栏、底部文案区、右侧按钮）。
- **背景印花**：`make_pattern.py`——16 个 AI 编程工具图标（Claude Code、Codex、Trae、WorkBuddy、Cursor、Windsurf、Copilot、Gemini CLI、Kiro、Antigravity、Cline、OpenCode、Qoder、CodeBuddy、OpenHands、Devin；来自 `独立视频\2026-10_请选择你的AI-Harness框架阵营\制作\assets\logos`）→ Playwright 渲 256×256 透明 PNG → PIL 染色 → 错位网格 + 随机旋转，出 `pattern_color.png`（原色 11%）、`pattern_ink.png`（墨色 7.5%）、`pattern_orange.png`（橙色 12%）、`pattern_none.png`。单色版必须用 `lobe_*.svg` 的轮廓版（满版方块图标染单色会变一整块）。
- **版式 B + 边框 6（用户选定）**：标题 280–570 不动；single：视频框 770–1339（间距 200）、字幕 1498–1608（间距 160）、信息条 1658 起（紧凑数字卡 205 px / 链接条 96 px，不同时出现）；dual（两个横屏）：两框叠在一起（860×490、间隔 24）、字幕在下 1764；边框 = 7 px 黑描边 + 橙色硬阴影 + 右上角黄贴纸（文字 = 当前场景来源 credit，`engine.js` 每帧更新）。
- **GitHub 链接条**：`linkPill()`（scenes.js），image-blaster 里 N02 / N09 两个仓库页场景亮 `github.com/neilsonnn/image-blaster`；“要两个 key”仍用数字卡。
- **第三人称**：先核实讲解者——作者 **@neilsonks**（Neilson Koerner-Safrata，World Labs），原帖 https://x.com/neilsonks/status/2055013782771134479 （2026-05-14，126.5 s 视频，有 2560×1440 版本；作者主页 neilsonks.com 列着这个链接），@liambraus 是转发。N01 改成“@neilsonks 五月发布了一套 Claude 技能……”（语音念“尼尔森五月发布了……”，去掉“今天”——那是原帖当天），N03 去掉“你”；两句在 Fish 里新建只有这两句的空白项目重配，导出后放进 `制作\02_配音\tts\seg_pick_v3\`，其余 9 句沿用上一版配音；画面角标 `@liambraus` → `@neilsonks · X（原帖）`。
- **image-blaster 成片重做**：套新版式（本条副本的 `index.html` / `engine.js` / `scenes.js` / `check_subs.py`，旧的备份成 `_index_旧版式.html` 等）、重建配音轨、重渲（4 路 56 s，0 页面报错）、`check_subs.py` 通过、`qa_mix.py` 11 句时间对（N01 / N03 / N09 机器分低，同音误识，仍要用户听）；旧成片 / SRT 归档 `台本\_旧稿\v2_第一人称_旧版式成片\`。
- **移植进技能模板**（`短视频\skill\short-video\assets\engine-template\`）：`index.html`（边框贴纸、位置、缩放、紧凑数字卡、`.linkpill`、字幕 y、头部注释）、`engine.js`（贴纸）、`scenes.js`（`big()` 默认 y 1658、`linkPill()`）、`check_subs.py`（字幕 y 从页面量）；移植脚本 `版式方案_20261004\port_to_template.py`，原文件备份 `*.bak_版式前`。另一个会话已加的背景机制（`assets/backgrounds/` 随机挑一张 → `bg.png` + `body.hasbg`、`new_short.py --bg`、变速 `speed`、`capture_pages` 新标记）都保留。技能文档：`references/layout.md`（新坐标、边框 / 贴纸 / 链接条 / 背景）、`references/script.md`（新增「第三人称」）、`SKILL.md`「验证过」。
- dual（叠放）用真引擎 CSS 在 image-blaster 副本里摆过一次（上框 680–1170、下框 1194–1684、字幕 1764），截图对；**还没做过真正的 dual 成片**（Tavus-Griffin 那条 dual 还是旧版式的副本）。

## 坑 / 备忘

- 在 bash 里用 heredoc 写含大量引号 / 反斜杠的 Python 会报 `unexpected EOF`：用 Write 工具写文件再运行；Playwright 的 `page.evaluate` 里的 JS 用 `r"""…"""`。
- Fish 工作室列表加载慢，点太早会误点到别的会话的项目；要用 `find` 取“新建项目”的 ref 再点，进编辑页后用 `document.querySelectorAll('div.content')` 核对是不是自己的空白项目（这次误点开了别的会话的项目，只看了一眼、没改）。
- 视频框下移后，右下角会被抖音点赞 / 评论按钮栏盖住一点，关键内容别放右下角。
- 背景印花图标是各家商标，只当低透明度装饰；用户 10-02 对 OpenAI 封面“不放 OpenAI 标志”的规矩针对封面，这里 Codex 图标是用户点名要的。

## 待办

- 用户听 N01 / N03 / N09 配音；封面；平台和合集；背景要不要换原色 / 橙色（现在用墨色，每期随机选已进模板，image-blaster 这条是固定墨色）。
- 原帖有 2560×1440 版本，放大裁切的画面会更清楚；换源要重核各 range 时间点。
- 做第一条真正的 dual 成片时验证叠放版式。
