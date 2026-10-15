# Playwright 备用发布 + 10/14 日报有声版替换

2026-10-14，用户：① 把今天的日报做成有人声版并替换 B 站上的无人声版；② 把长 / 短视频技能里依赖 Chrome 插件发布的地方改成“插件连不上浏览器、没法发布时用 Playwright 插件发布”，这次替换就用 Playwright 走一遍看行不行；③ 随后给了 Playwright 扩展的连接令牌，要求写进技能、发布时直接从技能里连本地浏览器。

## 有声版
- `daily.py localtts`（Qwen3-TTS，加速 1.15×）→ voice（识别分 0.89）→ render → gate → 独立复核。复核连判 3 次 fail（见运行记录）：台本 2 处说宽、要点卡说宽、来源截图被裁、5 + 1 + 1 处字幕错条；每轮改完只重做改过的句子（逐句缓存），第 4 轮 pass。成片 5:53（352.8 s）。
- 副产品：`snap_sources.py` 改了（h1 比截图框宽时收窄视口让标题换行，改后要 `--force` 重截）；技能踩坑表加了 3 行（复核反复、cuts 英文段 ≤55 字符、来源截图被裁）。
- 无人声版的成片 / SRT / 台本改前版本都留在 `AI日报/2026-10-14/_旧稿/无人声版_20261014/`。

## B 站替换（Chrome 插件完成）
编辑页「更换视频」→ 确认框「确定」→ 拦住页面现建的 file input → `file_upload` 上传版 → 换新简介 → 「立即投稿」一次 →“稿件投递成功”；线上 `state=-6 修改内容待审核`、新视频 353 s、简介已更新、两个封面蓝色占比 6.9% / 10%（自定义封面保留）。详细步骤和踩坑见 `AI日报/skill/ai-daily-news/SKILL.md` 第 8 步“换已发布稿件的视频”和 `docs/发布备用_Playwright.md` 的“实测记录”。

## Playwright 备用方案
- 共用文档 `docs/发布备用_Playwright.md`；各技能（ai-daily-news、yuanlai-ruci-episode、way-to-agi-episode、claude-code-episode、openai-episode、short-video）的 SKILL.md / publish.md 里加了指向它的一句话；routine 指令文件（`~/.claude/scheduled-tasks/ai-daily-news-produce/SKILL.md`）里“Chrome 插件连不上”改成先切 Playwright。
- Playwright 插件（官方目录里的 `playwright`，Microsoft 的 `@playwright/mcp`）用户没装；写了桥接脚本 `docs/pw/pw_mcp_bridge.py` + `pw_do.py`（自己当 MCP 客户端，用 `npx @playwright/mcp@latest --extension` 连用户自己的 Chrome），令牌放 `docs/pw/token.env`（**公开仓库，被 .gitignore 默认规则挡住，别抄进任何文件**）。
- 实测：连接、打开编辑页、点「更换视频」（要 force click）、确认弹窗都行；**上传文件被 Chrome 拦（DOM.setFileInputFiles “Not allowed”）**，疑似扩展没开「允许访问文件网址」（没验证，要用户自己在 chrome://extensions 里开）。所以 Playwright 路线目前能做到“进到上传这一步”，上传还没通。
- 桥接起法：要用 Bash 的 `run_in_background`（Popen 脱离终端起会在几分钟后被信号带走）。

## 待办 / 风险
- 过审公开后：核对线上简介、给 B 站加分段章节（`_章节.txt`）。
- note 文章 https://note.com/quiet_condor4833/n/n8990c4dbcd8a 仍写“约 4 分 40 秒、没有音声ナレーション”，与新视频不符——要改就在 note 编辑页改 `video` 说明和结尾那句（未动，等用户定）。
- Playwright 上传：开「允许访问文件网址」后重试；或 Playwright 自己的浏览器 + 用户扫码登录一次（登录态留在用户目录里，routine 可复用）。
- routine（10/15 04:32）第一次真跑本地配音 + 备用发布分支，注意看 `配音/raw/local_tts_usage.txt` 和运行记录。
