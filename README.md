# D:\大疆 目录说明

悠一（Yui）的视频项目。按 B 站合集分几类（前三个用户 2026-09-29 定，第四个 2026-09-30 开，Claude Code相关、OpenAI相关 2026-10-02 开）：

| 合集 | 内容 | 发布平台 | 本地目录 |
|---|---|---|---|
| Way to AGI | 悠一出镜 | B 站 + YouTube（B 站合集 / YouTube 播放列表都叫「Way to AGI」） | `Way to AGI/` |
| AI时代计算机专业研究生如何用AI | 悠一出镜 + 录屏，给做科研、写代码的计算机同学 | B 站 + YouTube（B 站合集 / YouTube 播放列表都叫「AI时代计算机专业研究生如何用AI」） | `AI震惊瘫坐时代计算机研究生必须掌握的技能/`（目录名暂没改） |
| 原LAI如此 | 像素讲解员（山田凉 / 鲸鱼娘）的 AI 科普 | 只发 B 站，不上传 YouTube | `AI科普/` |
| AI每日日报 | 鲸鱼娘播每日 AI 新闻 | 只发 B 站，不上传 YouTube | `AI日报/` |
| Claude Code相关 | Claude Code 产品信息：新功能、更新、官方发布（画外音 + 官方演示视频 + 官方页面录屏） | B 站合集「Claude Code相关」；YouTube 待定 | `Claude Code相关/` |
| OpenAI相关 | OpenAI 产品信息和模型实测（画外音 + 网友作品视频 + 官方发布会画面，中英双语字幕） | B 站合集「OpenAI相关」；YouTube 待定 | `OpenAI相关/` |

- DeepSeek 形象（鲸鱼娘 / 大肥鱼素材包）只用在原LAI如此和 AI每日日报里，两个出镜合集都不用。
- 片头片尾所有合集共用 `AI科普/片头片尾/`（片头打出“悠一”，片尾“悠一”印章），2026-09-29 起每期都用。
- 技能：原LAI如此 `yuanlai-ruci-episode`、AI每日日报 `ai-daily-news`、Way to AGI `way-to-agi-episode`、AI时代计算机专业研究生如何用AI `cs-grad-ai-episode`、Claude Code相关的整条流程 `claude-code-episode` 和封面 `claude-code-cover`、OpenAI相关的整条流程 `openai-episode` 和封面 `openai-cover`、竖屏短视频 `short-video`（`短视频/`，2026-10-04 开）（都在各自目录的 `skill/` 下，`C:\Users\yui\.claude\skills\` 里是联接）。
- `AI科普/`、`AI日报/` 暂时保留原名：技能联接和每天的日报抓取计划任务都写死了这两个路径，改名前要先改好这些引用。
- 其他：`真人素材/`（日常 vlog、露营等原始拍摄素材，只读，不动）、`docs/ai/context/`（每次任务的记录）、`AGENTS.md`（项目记忆，Claude 每次开工先读）。

## 公开仓库说明

这里是 https://github.com/cnYui/yui-video-archive ，保存已发布视频的内容和制作过程：

- 台本、字幕、章节、投稿信息、封面；
- 制作技能和脚本（视频是用 Claude Code 逐帧渲染出来的）；
- 每次任务的记录（`docs/ai/context/`）。

视频成片放在 [Releases](https://github.com/cnYui/yui-video-archive/releases)，每期一个。

不在这个仓库里的：

- 原始拍摄素材；
- 第三方素材：
  - 山田凉像素素材包是《孤独摇滚！》的同人作品，仅限个人非商业使用；
  - 鲸鱼娘是 DeepSeek 的网友拟人，原型 上善无形（CC BY-NC-SA 4.0），女仆造型 ZipZipPipe，与 DeepSeek 官方无关；
  - 还有背景图、BGM、字体、手写笔画数据；
- 新闻网站截图和原文；
- 渲染中间文件。

所以仓库里的工程不能直接重新渲染；视频中出现的这些素材，版权归原作者。

## 视频存档

| 合集 | 期 | 标题 | B 站 | 成片 |
|---|---|---|---|---|
| 原LAI如此 | 01 | 是什么API？凉前辈来教你！ | [BV1L4a46HE6U](https://www.bilibili.com/video/BV1L4a46HE6U/) | [yuanlai-01](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-01) |
| 原LAI如此 | 02 | 你的一句话就否定了AI一路的努力——AI是怎么从学会说人话到实现AGI的？ | [BV1nhav6DEsP](https://www.bilibili.com/video/BV1nhav6DEsP/) | [yuanlai-02](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-02) |
| 原LAI如此 | 03 | Jev模型是什么？和LLM有什么区别？鲸鱼娘带你看 | [BV1WsaG64EwD](https://www.bilibili.com/video/BV1WsaG64EwD/) | [yuanlai-03](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-03) |
| 原LAI如此 | 04 | 大肥鱼锐评：2026下半年国内外大模型，从夯到拉 | [BV1t7aG6wEK5](https://www.bilibili.com/video/BV1t7aG6wEK5/) | [yuanlai-04](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-04) |
| 原LAI如此 | 05 | 朱自清《荷塘月色》AI率62%？论文AIGC检测到底在测什么 | [BV1wqYw6aEd1](https://www.bilibili.com/video/BV1wqYw6aEd1/) | [yuanlai-05](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-05) |
| 原LAI如此 | 06 | 点了“深度思考”，AI那几十秒到底在想什么？ | [BV1r6Yw6bEJ7](https://www.bilibili.com/video/BV1r6Yw6bEJ7/) | [yuanlai-06](https://github.com/cnYui/yui-video-archive/releases/tag/yuanlai-06) |
| AI每日日报 | 9/27 | 9月27日，鲸鱼娘带你看看AI圈发生了什么？ | [BV1Etah6TExW](https://www.bilibili.com/video/BV1Etah6TExW/) | [ai-daily-2026-09-27](https://github.com/cnYui/yui-video-archive/releases/tag/ai-daily-2026-09-27) |
| AI每日日报 | 9/28 | 9月28日，鲸鱼娘带你看看AI圈发生了什么？ | [BV1PFaa6LE3V](https://www.bilibili.com/video/BV1PFaa6LE3V/) | [ai-daily-2026-09-28](https://github.com/cnYui/yui-video-archive/releases/tag/ai-daily-2026-09-28) |
| AI每日日报 | 9/29 | 9月29日，鲸鱼娘带你看看AI圈发生了什么？ | [BV1MKaJ6XEDd](https://www.bilibili.com/video/BV1MKaJ6XEDd/) | [ai-daily-2026-09-29](https://github.com/cnYui/yui-video-archive/releases/tag/ai-daily-2026-09-29) |
| Way to AGI | 01 | 被Claude Opus5.5生成视频能力吓到震惊瘫坐，没想到是这样实现AGI的 | [BV1XXax6yEwR](https://www.bilibili.com/video/BV1XXax6yEwR/) | 本地没有工程文件，没有存档 |
| Way to AGI | 02 | 如何使用Claude来低成本的生成视频 | [BV1s2aV6cELo](https://www.bilibili.com/video/BV1s2aV6cELo/) · [YouTube](https://youtu.be/EDWhMPfmZcE) | [way-to-agi-02](https://github.com/cnYui/yui-video-archive/releases/tag/way-to-agi-02) |
| AI时代计算机专业研究生如何用AI | 01 | 震惊瘫坐时代计算机同学必须掌握的AI基础功（一） | [BV14zao6REeR](https://www.bilibili.com/video/BV14zao6REeR/) · [YouTube](https://youtu.be/0zfFPuBQRoc) | [cs-grad-ai-01](https://github.com/cnYui/yui-video-archive/releases/tag/cs-grad-ai-01) |
| Claude Code相关 | 01 | 现在你可以让Claude修改自己！Claude新功能：Claude mod | [BV1Zoa16CEeU](https://www.bilibili.com/video/BV1Zoa16CEeU/) | 待建（要先定提交 git） |
| Claude Code相关 | 02 | Anthropic设计师教你如何使用Claude（转载 + 中英字幕） | [BV1Yham6gECf](https://www.bilibili.com/video/BV1Yham6gECf/) | 不建（别人的视频） |
| Claude Code相关 | 03 | 一个视频了解Claude Code 新插件 You should know（用户在页面里改过，线上标题带多余的“：/”） | [BV1PdHh6QE72](https://www.bilibili.com/video/BV1PdHh6QE72/) | 待建（要先定提交 git；含官方演示视频和页面截图，建不建由用户定） |
| OpenAI相关 | 01 | OpenAI 新模型 GPT-6.1 Sol 来了！做游戏、做地球，效果震撼瘫坐 | [BV1wYaU6oEbw](https://www.bilibili.com/video/BV1wYaU6oEbw/) | 待建（要先定提交 git；含网友作品和发布会画面，建不建由用户定） |
| 独立视频 | — | 国内订阅Codex/Claude教程！（非中转非代充） | [BV1pqaz6AEJP](https://www.bilibili.com/video/BV1pqaz6AEJP/) | 待建（过审后） |
| 独立视频 | — | 一个月合并2000多个PR，却不逐个Review：SpaceXAI工程师Lauren Tan怎么做到的？（访谈 + 演讲原话同传） | [BV1jEHs6XEne](https://www.bilibili.com/video/BV1jEHs6XEne/) | 待建（要先定提交 git；tag 建议 independent-no-more-review；别人的素材，成片是否进公开仓库要先问） |
