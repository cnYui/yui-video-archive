# 《AI每日日报》9月29日这期 + 配音改成只用网页版（2026-09-29）

## 结果

- 线上：**BV1MKaJ6XEDd**，标题「9月29日，鲸鱼娘带你看看AI圈发生了什么？」。344 秒，2340×1080，已进合集「AI每日日报」。
- 发布方式：routine 填好了 B 站投稿页，但没有点投稿。用户在那个标签页里自己点了「立即投稿」，时间是北京 09-29 08:42（B 站接口 `pubdate` = 1790642519）。
  - 线上简介 1728 字，和本地 `投稿信息.json` 一致。
- 已执行 `daily.py published --bv BV1MKaJ6XEDd --date 2026-09-29`：7 条写进 `collector/aired.jsonl`。之后由分段章节 routine 加章节；`AI每日日报_0929_章节.txt` 就是线上这一版的时间。
- 7 条新闻：
  1. Claude Sonnet 5.5 发布（Anthropic 官方、文档、TechCrunch）
  2. 英伟达智能体安全平台（英伟达新闻稿、Anthropic 博客）
  3. 华为开源盘古训练代码（IT之家、GitCode、动点科技）
  4. 千问打通夸克网盘（IT之家、手机中国）
  5. Gems 将迁移成 skills（9to5Google）
  6. Shopify 让 AI 帮你结账（Shopify 更新日志、TechCrunch）
  7. AMD 收购 World Labs（AMD 新闻稿、TechCrunch）

## 线上这一版有 AI 复核指出、但没来得及改的问题

用户发的是第 2 版成片。AI 复核判 fail 的 4 处，在第 3 版台本里改好了，但第 3 版没有出片：

1. **第 7 条 AMD 的截图**：AMD 新闻稿页顶部有深色横幅遮罩，截图几乎整块是暗的。成片约 4:56–5:32 白板上贴的是一张近黑的卡片。
2. **第 6 条第 7 句**：「亚马逊和阿迪达斯是拦着 AI 智能体下单」。TechCrunch 原文写阿迪达斯时带着 “apparently!”，依据只是一条个人推文，不能当成事实。
3. **第 6 条第 6 句**：「Shopify 说，合作的智能体有 Muse 和 Instinct」。这是 TechCrunch 的说法，Shopify 更新日志里没有。
4. **第 4 条要点**：「生成复习计划海报」把两个例子连成了一个词。

这几处都没有改线上视频。要不要改（换视频要重新过审）由用户决定。

## 过程（北京时间）

- 07:25 开工：routine 本该北京 03:30 开工，实际晚了很多，开工时已经过了 05:55，所以做完直接投稿、不定时。
  - 开工检查：`FISH_API_KEY` 在，Chrome 插件能连上。
- 选题和核对：两个子代理并行核实 8 条。
  - Workbench 改名 Playground 是 8 月 18 日的旧闻，没选。
  - 其余 7 条都逐条用 WebFetch 看了原文。
- 第 1 版：API 配音（5562 字节，识别分 0.890）→ 出片 5:52。
  - gate 挡住：谷歌帮助中心（support.google.com）页面里有 74 个隐藏字符。
  - TechCrunch 那篇 Gems 报道侧栏里有 “repeat the instructions”，也会被当成注入，所以不能拿来替换。
  - 第 5 条最后只用 9to5Google 重写。
- 第 2 版：API 配音（5622 字节，0.880）→ 出片 5:43，gate 只差 AI 复核。
  - 复核在跑的时候，先把 B 站投稿页填好了（没点投稿）。
  - 复核判 fail，就是上面那 4 处。
- 第 3 版：按复核意见改了台本，AMD 改截 TechCrunch 那篇，截图正常。
  - 整期重新配音时 API 返回 **402**（余额用完）。
  - 按技能改用网页版，页面一次生成了两个版本。这时用户说 9/29 已经自己发布了，任务结束。
- API 用量：2 次请求，11,184 字节，约 0.17 美元。

## 配音改成只用网页版（用户 2026-09-29：“之后都用网页版来配音”）

改动：

- `AI日报/skill/ai-daily-news/scripts/daily.py`：
  - 新命令 `webvoice --task <编号> [--task <编号2>] [--probe]`：
    1. 在 `platform.r2.fish.audio/tasks/<日期>/<编号>.mp3` 找音频。地址里的日期是哪个时区还没确认，所以按 UTC 的今天、前一天、后一天都试。
    2. 文字对不上的旧版本挪进 `配音/raw/_旧稿_*`。
    3. 下载成 `配音/raw/C01_vN.mp3`；短于 60 秒会报错。
    4. 把这版用的文字记进 `api_takes.json`，select_takes 只在当前文字的版本里挑。
    5. 在 `web_usage.txt` 记一行，state 记 `tts`（`source: web`）。
  - `tts` 不带 `--api` 直接退出，提示用网页版。
  - `build` 和 `status` 的“下一步”提示改成网页版。
- `SKILL.md`：
  - 第 5 步重写成网页版流程。
  - 开工检查不再查 `FISH_API_KEY`。
  - 用户规则、第 7 步重做流程、第 9 步运行记录一栏都跟着改。
  - 踩坑表加了 4 行。
- routine `ai-daily-news-produce` 的指令和描述：配音改成网页版 + `webvoice`；安全规则里的“API 余额不足”改成“网页版弹付费或额度不足”；报告里的“API 字节数”改成“配音用量”。
- AGENTS.md「所有视频通用的规则」表格和日报一节同步改了。

网页版实测（第 3 版台本，两个任务 `bd822d88…`、`a2bc5821…`）：

- 按一次 Ctrl+Enter 出两个**完整**版本：334.5 s 和 333.6 s。
- 在测试目录 `AI日报/_旧稿/_测试_网页配音_20260929/` 跑了 `webvoice` → `voice`：挑中 v2，识别分 0.888，切成 58 句，配音共 318.6 s。
- 页面上的操作：
  - 编辑框是 Tiptap（ProseMirror）。用 `document.execCommand('insertText', …)` 一次贴入整期，返回 `innerText === 原文` 核对。
  - 字数计数按 UTF-8 字节算（5692/15000）。
  - 模型下拉要是「Fish Audio S1」。
  - 在页面里 `fetch` 任务接口会被跨域拦下，任务编号只能从 `read_network_requests` 拿。

没有改《原LAI如此》的技能。它的 `references/voice.md` 里写的还是“API 优先、402 再用网页版”；那边现在由用户自己录音，AI 配音只在用户点名时用。以 AGENTS.md 的共用规则为准。
