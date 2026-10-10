# 事实核对：先查再写台本

第 1 期的教训：台本写完、配音生成之后才让调研子代理核对，查出 9 句要改（“GPT-6.1 Astra”根本不存在、“ultra code mode”不是官方名、Ultrafast 只有 Astra、Sol 不是最便宜的、人体图谱是转发……），配音返工了好几轮。**这一步在写台本之前做，台本照“能写 / 不能写”清单写。**

## 做法

1. 素材下载完、看过内容后，**立刻**起一个后台调研子代理（`Agent`，general-purpose，`run_in_background`）；它读官方原页，不信搜索摘要；你同时去抽帧、看素材。
2. 子代理产出 `台本/事实核对.md`：①名称对照（官方名 ↔ 帖子里的写法）；②已核实（结论｜来源网址｜读到时间）；③没法核实 / 官方没说 / 与官方不符；④每条帖子说了什么、能不能被官方印证；⑤台本里“能写”和“不能写”；⑥小字注释用的一句话说明（Higgsfield 是什么、Blender MCP 是什么…）。
3. 写台本时每句有出处；写完用清单逐条对（子代理第 7 节还会对照现有台本给修改建议）。
4. 简介里把“官方说的”和“网友说的”分开写，几处有出入的说明写出来（见 publish.md）。
5. **读不到的页面要写明**：openai.com 的文章页（`introducing-*`、`devday-2026-recap`）curl 和 WebFetch 都是 403，只能靠 RSS 摘要、官方文档、更新日志、搜索摘要（标“搜索摘要”）；投稿前让用户在浏览器里看一眼。

## 子代理提示词模板（填空）

> 你是事实核对员。今天是 <日期>。工作环境：Windows，项目目录 D:\大疆。请用中文汇报。
> **背景**：我在做一条中文 B 站视频，展示网友在 X 上晒出的 OpenAI 新模型（<模型名>）实测视频，配旁白。旁白里每一句关于“模型是什么、什么时候发布、价格、速度”的话都必须有官方出处，网友帖子里的说法只能当“某某说”来转述。
> **帖子**（账号、发帖时间 UTC、原文要点）：<逐条列>
> **要核实**：A. OpenAI 官方对 <模型> 的说法：定位、发布日期、API 价格（每百万 token，注意分档）、上下文、可用渠道、官方有没有“Max / Ultra / Ultrafast …”这些档位或名称及含义；B. 帖子里的写法是不是官方名称（给出官方名称对照表）；C. <产品，如 dots> 到底是什么，一句话；D. 一句话各说明帖子里出现的第三方（公司、工具）；E. 帖子里的数字有没有官方价格或评测能印证或反驳。
> **怎么查**：官方页面用 `curl.exe -sL -A "<Chrome UA>" <url>` 抓原文再读，不要只信 WebFetch 的摘要；抓不到（403）再换 WebFetch / WebSearch，并标“搜索摘要”。本机已有 DevDay 2026 主题演讲转写（`独立视频/2026-10_OpenAI-DevDay-2026解读/`，README / 词级转写 `words.py`）。**不要用 Chrome 浏览器插件和内置浏览器**（别的会话在用），不要碰 Fish Audio，只读不改现有文件。
> **输出**：写成 `<本期>\台本\事实核对.md`（结构见上）；150 行内；别抄大段原文（版权），只写事实和转述；最后给 10 行内要点摘要和矛盾 / 存疑点。

## 官方来源（2026-10-02 实测能读的）

| 来源 | 内容 |
|---|---|
| `openai.com/news/rss.xml` | 官方新闻 RSS（标题 + 摘要 + 日期；文章页本身 403） |
| `developers.openai.com/api/docs/changelog`、`/pricing`、`/models`、`/models/<id>`、`/guides/reasoning`、`/guides/ultrafast-mode`、`/guides/model-selection` | API 更新日志、价格（含分档）、型号规格、推理强度、Ultrafast |
| `developers.openai.com/codex/changelog`、`/models`、`/pricing`、`/speed`、`/dots` | Codex 和 dots 的官方文档 |
| `help.openai.com/en/articles/6825453-chatgpt-release-notes` | ChatGPT 更新日志（其余 help 文章 403） |
| `cdn.syndication.twimg.com/tweet-result?id=<ID>&lang=en&token=a` | 官方推文（@OpenAI、@OpenAIDevs）的全文和时间 |
| 本机 DevDay 转写 + 全分辨率幻灯片帧 | 幻灯片上的价格 / 档位以全分辨率帧或官方价格页为准（转写会听错数字） |
| 第三方旁证（只当旁证、标“第三方”） | Artificial Analysis（每任务成本、输出速度）、The Register / TNW / Gizmodo（GPT-6.1 Astra 取消） |

## 2026-10-02 的事实快照（会过期，下一期开工要重核）

- DevDay 2026：9 月 29 日。GPT-6 Astra：9 月 3 日发布的旗舰；GPT-6.1 Sol：9 月 29 日发布，官方说“接近 Astra 的表现、成本更低”；GPT-6 Sol / GPT-6 Luna：9 月 22 日（Luna 是官方说的最省钱的）。
- 价格（每百万 token，单次输入 ≤ 27.2 万）：Astra $10 / $50，Sol $2 / $10（正好 1/5）；缓存读 Astra $1、Sol $0.10；输入超 27.2 万整次请求输入 ×2、输出 ×1.5；Fast ×2；Ultrafast ×6（价目表里只有 Astra）。
- Ultrafast：幻灯片写 8x faster、up to 300 tokens/second；DevDay Recap 口径是 Codex 里最高 8 倍、API 里最高 6 倍（口径不统一，旁白写“最高”）；目前只有 Astra，Sol 之后上线；ChatGPT / Codex 里要 Pro 500。
- dots：ChatGPT 里由 GPT-6 Astra 驱动的常开智能体，有自己的云端电脑。
- **不存在 / 不是官方名**：GPT-6.1 Astra（OpenAI 取消了原定 10 月发布的版本）、ultra code mode（最接近的是 Codex 的 Ultra 子智能体档）、Astra Max ×1.5（Max 是推理强度最高档，×1.5 没有官方对应）。
- 容易写错：Sol 是最便宜的（不是，Luna）、Sol 比 Astra 更强（官方是“接近”）、dots 由 Sol 驱动（官方是 Astra；Dots × Higgsfield 由 Sol 驱动只是 Higgsfield 的说法）、“OpenAI × Magnific”（Magnific 自己的宣传）、帖子里的“快 4 倍 / 成本 4% / $1.50”（没法核实）。

## 写台本的口径

- 官方事实：直接写，旁白里带“官方 / 发布会 / 价格表上”这类出处词；画面小字写来源（“官方价格页”“发布会幻灯片”）。
- 网友的说法：“发帖的人说…”“Higgsfield 说…”；有利益相关的（Higgsfield 是 OpenAI 合作伙伴）在简介里说明；官方没有数据的（快 4 倍）在画面小字里注明。
- 原帖写错的名字：旁白不点版本，小字写“原帖写作 GPT 6.1 Astra，官方没有这个模型”。
- 画面里是 Pro 档（斗兽场四格里 “GPT-6 Astra Pro”）旁白说 “Astra Pro”，别说成标准 Astra。
- 转发作品：旁白和署名都写原作者（“开发者 Ashe 用 Astra 做的人体图谱”，署名“@R_ChajX 转发 · 原作者 @ashebytes”）。
