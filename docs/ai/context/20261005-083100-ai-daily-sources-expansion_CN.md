# 《AI每日日报》信息源扩充（2026-10-05 记录，工作在 10-04 晚做的；**还没应用到正式收集器**）

## 用户要求（原话）

“每日 ai 新闻的渠道，能不能再扩大一些，你看看还能接入哪些 rss 源”（2026-10-04 傍晚）。做到一半被用户转去做“日报改竖屏短视频”（见 `20261005-083000-daily-vertical-short-layouts_CN.md`），所以停在“副本里验证通过、正式目录没动”。

## 结论

本机实测约 700 个候选地址（公司官方博客 / 新闻室、英文和中文媒体、聚合、新闻信、GitHub 发版、社区生成的 RSS、几份现成的 AI 订阅清单 OPML、Hugging Face 账号、Bluesky 镜像号），**筛出 74 个新源：66 → 140**；副本里整跑一遍 54 秒、0 失败，候选从 472 个涨到 561 个（+19%）。

## 原有源的问题（顺带查出的）

| 源 | 问题 |
|---|---|
| `hn_ai`（hnrss.org） | 九个 OR 的查询一直 502（2026-09-28 起连续失败；简单查询是 200）。改用官方首页 RSS `news.ycombinator.com/rss` + AI 关键词过滤 |
| `aibase_daily` / `aibase_news` / `leiphone_flash`（RSSHub 路由） | 三个实例返回的都是 2026-09-30 以前的旧条目（路由停更），健康表里还显示“正常”。雷峰网改原生 feed `leiphone.com/feed`；aibase 没有原生 RSS（官网是单页应用），留着加了说明 |
| `openai_devdocs` | 最新一条 2026-05-05，152 天没更新；没找到替代地址 |
| RSSHub 实例顺序 | 新增 `rsshub.bestblogs.dev`，放最前（0.5–1 s，路由最全，ChatGPT 更新日志只有它能出）；另外两个常 429 / 503 / 慢 |

## 新增的 74 个（`_待应用_…/sources.yaml` 末尾“2026-10-04 扩充”一段）

- **官方一手 14（tier official）**：ChatGPT 更新日志（RSSHub `/openai/chatgpt/release-notes`，套餐 / 价格 / 功能变更，质量最好）、Gemini 应用博客、Google Labs、NVIDIA 新闻稿、Meta 新闻室（按 AI 关键词过滤，顶替拦爬虫的 ai.meta.com）、Microsoft Source、Ai2、Cohere 更新日志、Thinking Machines、Midjourney 更新、Character.AI、Stability AI、AMD 新闻室、Apple 新闻室。
- **辅助信号 10（signal，同一天同一来源合成一条）**：Cloudflare AI、GitHub Copilot 更新日志、Google Cloud AI、Workspace 更新、AWS 新闻博客、Microsoft Research、Devin / Windsurf（Cognition）、Sakana、transformers 发版、gemini-cli 发版。
- **英文媒体 16 + 简报 1**：Guardian AI、Wired AI、ZDNET AI、The Register AI、IEEE Spectrum AI、CNBC / Bloomberg / NYT / WSJ / BBC 科技（按 AI 关键词过滤）、9to5Google、9to5Mac、SiliconANGLE AI、Unite.AI、The Robot Report、ServeTheHome、The Rundown AI（background）。高产量的都加了 `weight: -1`（单独一家报道时扣 1 分），只当旁证。
- **中文 13**：新智元官网、极客公园、爱范儿、雷峰网、开源中国、InfoQ 中文、cnBeta、虎嗅和品玩（走 RSSHub）、机器之心 / APPSO / 夕小瑶科技说 / DeepTech 的公众号 RSS（个人站 decemberpei.cyou 的静态文件，约每天北京 07:00–09:00 整体刷新一次，每号只留 1–8 篇，没有日期和摘要）。
- **X 的替代 20（xproxy，只当线索）**：Bluesky 上的 @trq212、@bcherny 镜像 + **XGo（xgo.ing）把 X 账号转成的 RSS 18 个**：OpenAIDevs、ChatGPTapp、claudeai、GoogleAI、GoogleDeepMind、GeminiApp、NotebookLM、huggingface、NVIDIAAI、AIatMeta、MSFTResearch、cursor_ai、**Alibaba_Qwen、deepseek_ai、TXhunyuan、Kling_ai、Hailuo_AI（MiniMax）**、FishAudio。ID 取自 `SuYxh/ai-news-aggregator` 的 `feeds/follow.example.opml`；每个约 200 KB、最近 50 条；闲聊多，用 `x_chatter` 排除裸链接 / 回复 / 活动，`weight: -2`；`serial: true` 一个一个抓。之前“X 没有稳定的免费直连”的结论因此有了补充（国产实验室官网都没有公开 RSS，XGo 的官方账号是唯一的一手渠道）。
- **Hugging Face 账号 +23**（`hf_models.orgs`）：蚂蚁 inclusionAI、面壁 openbmb、书生 internlm、美团 LongCat、快手 Kwaipilot / Kolors、通义万相 Wan、Tongyi-MAI、昆仑万维 Skywork、商汤 sensenova、百川，以及 Black Forest Labs、Stability、Lightricks、Microsoft、IBM Granite、Ai2、Cohere、Liquid AI、xAI、Apple、AI21、LG EXAONE。

## 试过没接的（原因）

- **国内模型公司官网无 RSS**：智谱（z.ai 404）、MiniMax、Kimi、字节 Seed、腾讯混元、小米 MiMo、阶跃、面壁、商汤、讯飞、阿里云博客；sitemap 也没法用（页面少、没有 lastmod）。百度文心博客有 RSS 但 148 天没更新。
- **西方公司无 RSS / 被拦**：Cohere 博客（单页应用）、Perplexity / Ideogram / xAI / Microsoft AI（403）、Meta AI 博客（400）、Black Forest Labs / Runway / ElevenLabs / Suno / Groq / Cerebras / Fireworks / Windsurf 官网（404 或没有）、IBM、Tesla、Intel、Qualcomm。社区仓库（Olshansk / 0xSMW / Turing Institute）里的 xAI、Perplexity、Cohere、Groq、Mistral、Meta AI 都已 69–200 天没更新。
- **更新日志标题是日期、进候选没法用**：ElevenLabs、智谱 docs、Kimi platform。
- **原生 RSS 返回网页 / 超时**：机器之心、36 氪、品玩、智东西、虎嗅（超时）、钛媒体（时通时不通）、第一财经；ai-bot.cn 的 feed 已关。
- **价值低 / 噪声大**：个人博客和新闻信（Zvi、SemiAnalysis、Raschka、Stratechery……）、GitHub Trending、HF 每日论文、arXiv、Product Hunt、Reddit 其余板块（连续请求 429；r/LocalLLaMA 原来就在）、OpenRouter 博客（SEO 文章）、PR Newswire（外语稿多）、Semafor / Axios（太宽）、VentureBeat（38 天没更新）。
- **可用但没接**：YouTube 官方频道 RSS（OpenAI / DeepMind / NVIDIA / Anthropic，`youtube.com/feeds/videos.xml?channel_id=…`，ID 见 `20261001-221509-youtube-channels-to-watch_CN.md`）、个人 X 博主（宝玉、歸藏、小互……每天几十条，太吵）。

## 对 `collect.py` 的四处改动（`_待应用_…/collect.py`，和正式版只差这些）

1. `serial: true` 的源排在其他源之后一个一个抓（间隔 0.5 s）：XGo 这类第三方限流严。
2. 首次抓取时**没有日期的条目只留 feed 里的前 10 条**（`FIRST_UNDATED_KEEP`）：副本试跑发现 ChatGPT 更新日志末尾 14 条 2023 年的老条目没有日期，原逻辑会当新条目、又是 official 级，涌进明天的候选。
3. “第一次抓”按 `(源, org)` 判断（`hf_models` 每个条目带 org）：新加的 Hugging Face 账号不会把过去 7 天的模型当候选倒灌。
4. `candidates.md` 展示条数 80 → 100（候选池涨了 19%；`SKILL.md` 第 1 步写的“前 80 个”要同步改）。

## 副本试跑看到的

- 新源在最近 36 小时里入库 132 条（cnBeta 26、新智元 14、虎嗅 11、公众号 12、Guardian 6……）；周末，官方源几乎没有新帖，**官方源的效果要工作日才看得出**。
- 前 80 名里 19 个候选涉及新源，其中 7 个原有大新闻多了旁证（例：Gemini 免费版降级 3 → 5 个来源、OpenAI 安全负责人离职 4 → 6）。高产量媒体单源条目分数略高于原来排在末尾的国内单源条目，挤掉了几条（例：Suno Speech）——所以给它们加了 `weight: -1`，并把展示条数提到 100。
- 偶发：`xg_hailuo`（XGo）第一遍超时（25 s），第二遍 3.8 s 正常。

## 依赖和风险

- **XGo（api.xgo.ing）**：第三方商业服务（XGo 本身是 X 增强工具），没有公开的账号查找接口，地址里的 ID 只能从清单里拿；服务变了 / 收费 / 限流会整批失效，健康表会报出来，不影响别的源。
- **rsshub.bestblogs.dev**：BestBlogs 项目的公共 RSSHub，没有认证；另外两个实例是兜底。
- **decemberpei.cyou 公众号 RSS**：个人站，没有日期，停更了看不出来（健康表只看得到“无日期”）。
- 这些都只当线索 / 交叉验证，**选题硬规矩不变**：每条要有官方来源，或至少两家可靠媒体；X 镜像、HN、Reddit 只当线索。

## 怎么应用 / 回退

```bash
cd "D:\大疆\AI日报\collector"
cp _待应用_信息源扩充_20261005/sources.yaml sources.yaml
cp _待应用_信息源扩充_20261005/collect.py collect.py
python collect.py collect          # 首次抓取：新源 36 小时以前的条目只入库不当候选；约 55 秒
python collect.py health           # 看有没有失败的
```

然后把 `AGENTS.md`（目录结构里的“sources.yaml（66 个源）”）和 `AI日报/skill/ai-daily-news/SKILL.md`（“66 个免费源”、第 1 步“前 80 个”）里的数字改成 140 / 100。回退：这两个文件在 git 里是干净的，`git checkout -- AI日报/collector/sources.yaml AI日报/collector/collect.py` 即可；`seen.sqlite` 只追加，不用回退。

## 文件

`D:\大疆\AI日报\collector\_待应用_信息源扩充_20261005\`：`sources.yaml`、`collect.py`（改好的）、`probe.py`（批量测地址，复用 collect.py 的 `parse_feed`）、`discover.py`（从公司主页自动找 RSS / sitemap）、`测试结果_第 1–7 批.json`（每个地址的状态码、条数、最新条目时间、近 7 天条数）、`自动发现_公司主页.txt`。参考的订阅清单：`RSS-Renaissance/awesome-AI-feeds`、`alan-turing-institute/ai-rss-feeds`、`SuYxh/ai-news-aggregator`、`vishalshar/awesome_ML_AI_RSS_feed`。

## 没做的（要的话再说）

- 通用 `sitemap` 抓取方式（给没有 RSS 的公司官网，类似 DeepSeek 那个）：国内实验室的官网 sitemap 太薄，收益有限。
- YouTube 官方频道、个人 X 博主；自建 RSSHub（Docker，要用户同意）。
- 应用后第一个工作日（10-06 周一）看一遍 04:30 导出的 `candidates.md`：新源有没有把好题挤出去、XGo 的闲聊有没有漏进前 100。
