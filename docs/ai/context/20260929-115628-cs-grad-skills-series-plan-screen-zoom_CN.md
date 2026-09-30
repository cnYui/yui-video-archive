# 新系列《AI震惊瘫坐时代计算机研究生必须掌握的技能》：分集大纲 + 录屏自动放大工具调研

- 时间：2026-09-29（UTC+9）上午。
- 起因：
  - 用户：“我下一期节目想做这个，单独新增一个分集，就叫AI震惊瘫坐时代计算机研究生必须掌握的技能，会分为好几集……你觉得每一集应该讲什么内容？”
  - 接着：“因为这个分集我会做很多的录屏演示，你看一下有没有那种开源项目，能够将镜头跟随我的鼠标的，就比如说我要点击一个地方，自动会放大过去”。
- 结论：
  - 大纲 7 集，是草案，等用户确认。
  - 录屏工具先试 Recordly 和 OpenScreen（社区维护版），都免费、有 Windows 安装包、还在维护。还没下载、没试录。

## 分集大纲（草案）

| 集 | 题目 | 要点 |
|---|---|---|
| 1 | 别再用 VSCode 做研究了 | 立论 + 分屏对比同一任务；立场是“VSCode 从主工作台退成查看器”（看 diff、调试、Jupyter 还用它）；放全系列路线图 |
| 2 | 国产模型 API Key 配进 Claude Code 和 Codex | 外壳 + 模型可拆；`base_url` / key / model 三件套；Claude Code 写 `~/.claude/settings.json` 的 `env`，Codex 写 `~/.codex/config.toml` 的 `model_providers`；几家横评；key 不进仓库、录屏打码、设用量上限。Codex 对第三方接口的支持变得快，录前按最新版实测 |
| 3 | git：AI 时代的后悔药 | 研究够用的约 10 个命令；`.gitignore`（数据、checkpoint、日志、`.env`）；diff 要看得懂；AI 动手前先 commit；实验记录写 commit hash；进阶讲 worktree |
| 4 | GitHub：把论文代码读懂、跑通 | README / Issues / fork 与 clone / SSH key / 私有仓库 / `gh`；演示让 agent 读热门论文仓库并跑通一个 batch |
| 5 | 用 Claude Code / Codex 直接上实验室服务器 | 免密、`~/.ssh/config`、`ProxyJump`；A 本地 agent 通过 ssh 执行，B 服务器上装 agent 放 tmux；查空卡 → 训练 → 看日志 → rsync 回本地；共享服务器的安全规矩；代码用 git 同步 |
| 6 | 上下文管理 | 上下文窗口 = 工作记忆；一个任务一个会话、`/clear`、`/compact`；日志用 tail / grep；子代理；`CLAUDE.md` / `AGENTS.md` 当课题记忆（拿本项目当案例） |
| 7（建议加） | 大结局：从一篇论文到第一张结果图 | 把前 6 集串起来走一遍 |

- 贯穿全系列：key 不泄露；没发表的数据、代码发给第三方 API 前先看实验室规定。

## 录屏自动放大工具（2026-09-29 查，星数、版本用 `gh api` 核对）

| 项目 | 许可 | Windows | 状态 | 说明 |
|---|---|---|---|---|
| [webadderall/Recordly](https://github.com/webadderall/Recordly) | AGPL-3.0，免费、没有付费档 | `Recordly-windows-x64.exe`（176 MB），要 Win10 19041+ | 约 3.2 万星，v1.4.0（09-08），09-23 还有提交 | 按鼠标活动给出放大建议，时间轴上能改、能手动加；重绘光标（平滑、动态模糊、点击回弹）；有中文 README；从 OpenScreen 分出来，八成以上代码已不同 |
| [getopenscreen/openscreen](https://github.com/getopenscreen/openscreen) | MIT | `Openscreen.Setup.1.13.0.exe`（220 MB），要 Win10 1903+ | 约 3.3k 星，v1.13.0（09-24），09-28 还有提交 | 放大跟随鼠标，也能手动加，深度 / 时长 / 缓动 / 位置可调；光标平滑、点击效果；界面支持简体中文；GPU 导出（D3D11） |
| [siddharthvaddem/openscreen](https://github.com/siddharthvaddem/openscreen) | MIT | — | 约 4 万星，**2026-06-17 已归档**，停在 v1.5.0 | 原作者把维护交给上面的 getopenscreen，同名同许可。不要从这里下载 |
| [CapSoftware/Cap](https://github.com/CapSoftware/Cap) | AGPL-3.0（部分 MIT） | 从官网下载 | 约 2.3 万星，cap-v0.6.0（09-15） | Studio 模式能放大、4K/60 导出；免费版只限个人使用，商用要买桌面授权（每年 29 美元，或 58 美元买断）。B 站有收益算不算商用拿不准，先不选 |
| [BlankSourceCode/obs-zoom-to-mouse](https://github.com/BlankSourceCode/obs-zoom-to-mouse) | 没写 | OBS 脚本 | 约 1.2k 星，最后更新 2024-06 | 录的时候按快捷键放大，跟着鼠标走；不是点击触发，放大直接录进画面，事后改不了 |

- 两个主推项目的 README 都没写：放大到底是点击、停留还是打字触发；能不能关掉背景和留白（全屏导出）；导出能选的分辨率和帧率；有没有打码。要试录确认。

## 用在这个系列要注意

- **终端段落**：Claude Code / Codex 主要靠打字，鼠标不动，跟着鼠标的自动放大基本不会触发。终端字号调大，重点输出在时间轴上手动加放大。
- **清晰度**：1080p 录屏放大 2 倍只剩 960×540，会糊。显示器支持就用 2K / 4K 录；不行就把放大倍数压在 1.5 倍左右。
- **第 2 集的 key**：README 里两个工具都没写打码。（更正：OpenScreen 官方文档里有“模糊”标注，见 `20260929-125117-screen-zoom-tools-trial_CN.md`。）录的时候仍用临时 key，录完马上在控制台删掉。
- **放进现有版式**：Way to AGI 的画面是 HTML 逐帧渲染（出镜画框 + 目录 + 字幕），录屏只是其中一块。试录时确认能不能关掉背景、留白，导出 30 fps。
- **备选方案**：如果导出的画面塞进出镜版式不顺手，就用 OBS 录原始画面，同时用小脚本记下每次点击的时间和坐标，在现有渲染流程里自动算放大镜头。这样完全可控，也能写进技能。还没做。

## 待用户决定

- 大纲按这 7 集走，还是要调整。
- 新系列算第四个合集吗？只发 B 站，还是 B 站 + YouTube 都发？用不用 Way to AGI 的出镜 + 录屏流程？
- 要不要下载 Recordly 和 OpenScreen 的安装包，用同一段 30 秒操作（GitHub 网页点击 + 终端打字）对比试录。
