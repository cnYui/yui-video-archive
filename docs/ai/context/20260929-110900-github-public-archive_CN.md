# 建公开仓库 cnYui/yui-video-archive + 目录结构 + AGENTS.md 压缩（2026-09-29）

用户原话：“当前大疆目录下的文件结构，你也可以写到AGENTS.md文件中，AGENTS.md文件的内容需要压缩一部分到docs/ai/context目录中，你查看当前本地的routines中是如何进行AGENTS.md压缩和docs/ai/context创建的，当前项目你也在github上，用cnYui的身份创建一个公开的仓库，用来保存历史的视频和内容”。

## 结果

- 仓库：https://github.com/cnYui/yui-video-archive （公开）。
  - 本地仓库就是 `D:\大疆`（以前不是 git 仓库），分支 `main`，remote `origin`。
  - 初始提交 07f4acc：509 个文件，打包后约 12.5 MB。
- 8 个 Release，每个放一期成片，附件名用英文，中文原名写在附件 label 里：

  | tag | 附件 | 大小 |
  |---|---|---|
  | yuanlai-01 | yuanlai-01-what-is-api.mp4 | 81.6 MB |
  | yuanlai-02 | yuanlai-02-from-talking-to-agi.mp4 | 107.5 MB |
  | yuanlai-03 | yuanlai-03-what-is-jev.mp4 | 52.4 MB |
  | yuanlai-04 | yuanlai-04-model-tier-list.mp4 | 59.9 MB |
  | ai-daily-2026-09-27 | ai-daily-2026-09-27.mp4 | 36.1 MB |
  | ai-daily-2026-09-28 | ai-daily-2026-09-28.mp4 | 85.7 MB |
  | ai-daily-2026-09-29 | ai-daily-2026-09-29.mp4 | 55.7 MB |
  | way-to-agi-02 | way-to-agi-02-claude-video-low-cost.mp4 | 113.2 MB |

  - 放之前从 B 站创作中心（插件、`member.bilibili.com/x/web/archives`）核对过：8 期都是“开放浏览”，本地成片时长和线上一致（差 < 1 s）。
  - 公开下载地址返回 200。
  - Way to AGI #01（BV1XXax6yEwR）本地没有工程文件，没有存档。
- AGENTS.md：
  - 加了「目录结构（2026-09-29）」「GitHub 公开仓库」，并把各期的 BV、待办归拢到一起。
  - 从 339 行 / 70.6 KB 压到 290 行 / 29.2 KB。挪走的原文逐节照抄在 `docs/ai/context/20260929-103800-agents-md-compression_CN.md`。
  - 判据参照本机 routine `github-pr-automation-agents-md-compression`、`sub2api-docs-daily-pipeline`：
    - 一次性的运行 / 操作流水、已被取代的中间状态 → 挪走；
    - 现行规则、坑、待办 → 保留；
    - 拿不准就留；原文照抄。
  - 和那两个 routine 的不同：本项目不删 `docs/ai/context` 里的旧文件（dcg 钩子拦截删除，文件也都在 15 天内）。
- README.md 末尾加了「公开仓库说明」和「视频存档」表；原来的内容没动。

## 收什么、不收什么（`.gitignore` 白名单）

- 默认 `*` 全部忽略，`!*/` 让目录照常往下找。
- 白名单：
  - md、txt、srt、json、jsonl、yaml、py、pyw、ps1、js、css、html；
  - 每期最终封面：`封面/封面_16x9_1920x1080.png`、`_4x3_1440x1080.png`，Way to AGI 是 `04_封面/封面_选定_16x9.png`、`_4x3.png`。
- 排除：
  - 原始素材：`真人素材/`；
  - 第三方素材：整个 `素材/`（山田凉同人像素包仅限个人非商业使用、官方立绘、背景图、BGM、字体、手写笔画数据）、`fonts/`；
  - 新闻相关：新闻截图 `制作/assets/`、新闻原文缓存 `source_pages.json`、候选新闻原文 `candidates.*` / `items.jsonl`、日报抓取日志和快照；
  - 别人的内容：别人视频的转写 `参考分析/`、METR 原始数据 `metr_benchmark_results_*.yaml`、从第三方笔画数据生成的 `handdata.js`；
  - 中间文件和音频：`制作/build/`、`制作/voice/`、`配音/raw/`、`配音/segments/`；
  - 测试和旧稿：`_旧稿/`、`_旧稿_*/`、`_skilltest/`、`_测试_*/`…；
  - 私人内容：`.claude/`；Way to AGI 的展示视频素材、原片截帧、录像原始逐条转写（里面有没用上的重录、上一期的录音）；B 站旧稿清理清单（`20260927-103216-bilibili-cleanup_CN.md`，里面是用户设成“仅自己可见”的稿件）；
  - 目录联接 `AI日报/片头片尾`。
- 坑：
  - `.gitignore` 里中间带 `/` 的规则只匹配仓库根目录，所以 `制作/build/` 要写成 `**/制作/build/`。第一次演练就漏过这个坑。
  - 带后缀的 `_旧稿_日期大字版_20260928/` 没被 `_旧稿/` 匹配到，推送前补了 `_旧稿_*/` 并修正了提交。
- 提交前扫了一遍要收的文件：密钥、token、B 站 cookie、Authorization、邮箱、手机号、IP、“仅自己可见”名单。
  - 命中的都是正常内容：视频画面里打码的 `Bearer sk-••••`、公司公开的销售邮箱、`127.0.0.1`、npm 包名、只有计数的清理进度。
  - 扫描脚本在会话临时目录，没有进仓库。以后在白名单里加类型时，照同样的规则再扫一遍。

## 视频上传的做法

- 附件名不能用中文：GitHub 会把非 ASCII 字符换成点。所以没有用 `gh release create <tag> <文件>`。
- 做法：
  1. 先 `gh release create <tag> --target main --title ... --notes ...` 建空 release；
  2. 再用 `gh api` 直接 POST 到 `https://uploads.github.com/repos/cnYui/yui-video-archive/releases/<id>/assets?name=<英文名>&label=<URL 编码的中文名>`，`--input <本地成片>`。
  - 这样不用在本地复制一份改名的视频。
- release 说明里写了 B 站链接、规格、仓库里对应的目录，以及角色素材的授权说明（山田凉同人素材仅限非商业；鲸鱼娘原型 CC BY-NC-SA 4.0、与 DeepSeek 官方无关）。

## 以后

- 新一期发布后照 AGENTS.md「GitHub 公开仓库」的步骤：commit、push、建 release、README 加一行。日报 routine 还没有自动做这一步，要不要加由用户定。
- `D:\大疆` 现在是 git 仓库，别的会话改的文件会显示为未提交的改动，这是正常的。提交前先看 `git status`，只提交想公开的东西。
