# AI每日日报 → note.com 日文文章（2026-10-10）

## 用户要求
- “routine 发每日日报的时候，同步写一篇文章发到 note.com，用视频的素材来写，现在写一下今天的每日日报，这个平台用纯日文发布。”
- 随后补充：“配图要加上，配图可以从做视频的 html 中拿。”

## 做了什么
- 首篇（10/10 那期，7 条）：https://note.com/quiet_condor4833/n/n8495e3b3bd12 （2026-10-10 16:42 JST 公开；账号 Yui / 悠一 = quiet_condor4833；约 4,400 字；见出し画像 + 7 张配图 + 8 个标签：AIニュース / 生成AI / Anthropic / Claude / OpenAI / DeepSeek / AIエージェント / オープンソース；无料）。
- 新增脚本（`AI日报/skill/ai-daily-news/scripts/`）：
  - `make_note.py`：`check`（必填项、纯日文——汉字不在 Noto Sans JP 字集里算简体字、链接、标签）、`html`（`note/article.html` 粘贴用 + `article.md` 预览）、`cover`（`note/見出し画像_1280x670.png`，沿用日报白底封面 + 鲸鱼娘，字换日文，用 `Noto Sans JP`）、`frames`、`all`。
  - `note_frames.py`：配图。拷贝视频的 HTML 引擎（`制作/vertical` 的 `engine.js`、`assets/`），把 `index.html` 的文字换成日文（`tl_v.js` 的 kicker / t1 / t2 / pts / bigs 换日文，`subs` 清空）、字体换 Noto Sans JP，去掉字幕和进度条，来源框 / 鲸鱼娘 / 数字卡往上收，每条新闻在数字卡亮着的那一刻用 Playwright 截图，裁 1080×1270 再缩到宽 960。英文官方页面的截图留在来源框里；来源是中文页面（IT之家）的条目不放截图，框里放机构名 + 标题 + 来源（引擎自带的 nosnap 版式）。
- 样板：`assets/note-template/article.sample.json`（= 这期的 `note/article.json`）。
- 技能 `ai-daily-news`：顶部说明 + 新增 8e + 第 9 步推送带 note 网址；routine `ai-daily-news-produce` 提示词新增第 5b 条（B 站投稿后做，失败不影响 B 站，`note/note_url.txt` 防重复）。
- `AGENTS.md`：常用网页加 note.com；日报一节加 note 同步说明。

## note 编辑器的坑（2026-10-10 实测）
- 窗口尺寸会变（截图坐标系 1484×750 / 1568×712 / …），按坐标点击靠不住：用 JS、Tab 键、`find` 的 ref。
- 正文用 `ClipboardEvent('paste')`（`text/html`）粘进 `.ProseMirror`，h2 / h3 / ul / strong / a 都保留。**分块粘时每块的第一个块会并进上一块最后一段**（标题被粘进列表项）→ 整篇一次粘。`execCommand('selectAll'/'delete')` 清不掉编辑器，会变成两份；要真键盘 `ctrl+a` + `Delete`。
- 插图：note 的文件输入是现建现用、不挂 DOM。先装拦截：`HTMLInputElement.prototype.click` 遇到 `type=file` 就挂到 body、记进 `window.__cap`（不开系统选择框），再 `find` + `file_upload`。上传后 `figure figcaption` 里粘说明。
- 插入菜单：空段落里 `Tab` → 焦点到「メニューを開く」→ JS `click()` → 点 `textContent === '画像'` 的项。**别按 Return 开菜单**：第一项「AIアシスタント」会弹同意条款对话框（这次点了「キャンセル」，没同意）。悬停出的「+」不稳定。
- 見出し画像：`button[aria-label="画像を追加"]` → 「画像をアップロード」→ 裁剪对话框直接「保存」（1280×670 不用裁）。
- 公開設定页：ハッシュタグ combobox（`type` + `Return`，间隔 1 秒）→ 「投稿する」。发布后弹「バッジ」对话框（10 本目），不用管；关闭它的按钮 JS 点了会跳到バッジ页（无害）。
- 核对用 `https://note.com/api/v3/notes/<key>`：`status`、`eyecatch`、`body` 里 `<img` / h2 / h3 个数、`hashtag_notes`。

## 没做 / 留给用户
- note 里的视频链接指向 B 站稿件；routine 在北京 05:00 前后发 note，B 站定时 06:00 才公开，中间约 1–2 小时链接打不开。用户觉得要紧的话：note 改成 B 站公开后再发（比如放到“分段章节”那个 routine 里），或文章里先不放链接。
- 10/9 那期（用户手动发布的 BV1dCpp6DEyS）没补 note 文章。
- note 的“AI 学習対価還元プログラム”“記事の自動翻訳”保持默认，没动。
