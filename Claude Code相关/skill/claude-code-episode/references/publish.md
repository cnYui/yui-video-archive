**上传方式（2026-10-14 用户定）：文件小于 10 MB 且本轮已授权自动上传时，可用 Playwright JS 上传完整文件；达到或超过 10 MB 就提醒用户手动上传。不为自动上传压缩、分块或改用低清版本。用户手动上传后继续填表，已授权发布则读回核对后点击发布。**

> 默认发布平台（2026-10-14 用户定）：短视频、长视频在用户未指定平台时仅发 B 站；不打开、不上传其他平台。用户明确要求其他平台时才启用对应流程。平台默认值不代替发布授权；用户已说“发布”时，完成读回核对后直接发布，不重复确认。

# B 站投稿（Chrome 插件填表）

> **备用发布方案（2026-10-14 用户定）**：Chrome 插件连不上浏览器（`tabs_context_mcp` 报错、`unsupported Codex auth method`、`Codex auth token is unavailable`、没有已连接的浏览器）、因此没法填表 / 发布时，不要停在这里等，改用 **Playwright（装了插件就用 `mcp__playwright__*` 工具；没装就用桥接脚本 `D:\大疆\docs\pw\pw_do.py`，它读 `D:\大疆\docs\pw\token.env` 里的令牌直接连用户自己的 Chrome）** 继续：做法、工具对照和注意事项见 `D:\大疆\docs\发布备用_Playwright.md`。只换操作浏览器的工具，本文件的内容和红线（谁点“立即投稿”、视频由谁上传、10 MB）一条不变。

细节的总表在记忆 `bilibili-publish-form-quirks` 和 `AI科普/skill/yuanlai-ruci-episode/references/bilibili.md`、`cover.md`；这里写 Claude Code相关 第 3 期（BV1PdHh6QE72）实际做的一遍。

## 投稿前

- `python make_submission.py` 写 `投稿信息.json`（`title` `tags` `desc` `chapters` `cover_*` `declaration` `category`）和 `制作/_desc_final.txt`。章节时间 = 正片时间 + 片头秒数（读 `pack_info.intro_seconds()`，现在 4.8 s）。
- **标题**：封面写短钩子、标题写完整一句、两边不写同一句；模型 / 功能名用官方写法；不夸成官方没说的（“拦截”“实验功能”）；**用户会在页面里自己改**（第 1 期改了好几次，第 3 期用户先说“标题为：…，或者你想一个新的标题”，又补一句“比如一个视频了解Claude新插件”，最后在页面里手改并自己点了投稿）。用户开始在页面里打字 / 标题字段在变时**只读不写**，线上标题以页面为准，投完用接口读出来同步回文档；线上标题带残留（多余的“：/”）要问用户改不改，别自己改。
- **简介**（≤ 2000 字，第 3 期 1833）：①一句话说这条视频是什么；②章节（`00:00 …`）；③要点（都来自官方推文 / 文档 / 更新日志，注明哪条来自哪）；④几处要说明（官方没写的、演示视频自带的标注不是产品界面、和上一期口径不同的地方、**用户反馈不是官方结论**）；⑤资料来源（链接 + 读的日期）；⑥声明：官方演示视频 / 推文 / 页面来自 @ClaudeDevs 和 Anthropic 官方网站，仅作介绍和评论引用，版权归原作者；**封面里的像素宇航员取自 claude.dev 官方页面，版权归 Anthropic**；功能版本会变以官方文档为准；配音为 AI 生成（曼波声线）；剪辑 Claude Code（模型）。
- 标签 10 个：`claude`（小写）、`Claude Code`、`Anthropic`、`AI编程`、`插件`、`人工智能`、`AI工具`、`编程`、`大模型`、`AI Agent`（第 3 期的线上标签；“新功能”加了被静默丢掉）。

## 上传视频（只能用户来）

插件 `file_upload` 单次 ≤ 10 MB，在插件控制的标签里点“上传视频”也不会弹出系统文件框；绕过大小限制会被权限分类器拦下，不要试。做法：Chrome 插件开 `https://member.bilibili.com/platform/upload/video/frame`（页面上“本地浏览器存在 N 个未提交的视频”是用户别的草稿，**别点“继续编辑”**）→ `mcp__ccd_host__reveal_path` 把成片在资源管理器里选中 → 请用户拖进上传区，拖好说一声。**用户在 Chrome 里全屏看视频 / 别的会话占着 Chrome 前台时，别把投稿页切到前台盖住**，先在消息里说清、等他回话再开。

## 填表（用户拖好之后）

页面的视口大小在上传过程中会变，坐标点击会打偏：弹窗里的按钮、“完成”用 `javascript_tool` 按文字 / 类名点；顶层 `await` 可用，包成 async IIFE 会返回 `{}`；返回内容里带 URL 的 query string 会被拦。上传完成后视口稳定了，坐标点击也可以。

1. **封面**（2026-10-03 定下的做法，6 期换封面验证过）：JS 点文字是“添加封面”的元素 → 弹窗“封面制作”→ **“双比例同步改动”保持不勾**（`label.sync-checkbox` 没有 `bcc-checkbox-checked`）→ JS 点文字含“个人空间封面（16:9）”的元素，`find` 出封面文件输入框（会变成当前选中的位）、`file_upload` 传 `封面_选定_16x9.png` → JS 点文字含“首页推荐封面（4:3）”的元素，同一个文件框传 `封面_选定_4x3.png` → 截图确认两个位各是对应排版（4:3 位两边留灰 = 装的是 4:3 图）→ JS 点 `div.button.submit`（“完成”）。只换了一个位点“完成”会弹“检测到个人空间封面（16:9）未修改…是否同步”：点“不同步，手动编辑”，别点“确认同步”。
2. **标题**：`find` “请输入稿件标题”→ `form_input`；读回 `input[placeholder="请输入稿件标题"]` 的 value 核对。
3. **创作声明**：**默认是空的（必填）**——点下拉（坐标点；用 JS 按类名找不到选项），选“含AI生成内容”；分区默认“人工智能”（tid 231），读一遍对就不动。
4. **标签**：B 站自动填几个（“短片 / 原创 / AE”），点每个标签里的 `svg.close`（派发 click）删，**一次只删一个（会重新渲染），要循环**（`.label-item-v2-container svg.close`，每次等 0.7 s）；再点标签输入框（`find` “按回车键Enter创建标签”，页面里有两个，取表单里那个（ref 小的））→ `type` → `Return` → 等 2 s，**每个标签都要先点一下输入框**；上限 10 个。加完用 `.label-item-v2-container` 读回，**被丢掉的换一个**（“新功能”丢了）；手敲小写带连字符的标签会被悄悄丢掉，要点“推荐标签”里的同名项；大写 `Claude` 会被拒（话题专用标签）。
5. **简介**：`document.querySelector('.ql-container').__quill.setText(文本, 'user')`，读回长度和页面右下角计数。
6. **加入合集**：点“请选择合集”，下拉里选「Claude Code相关」（别凭印象说没有；下拉里有 AI每日日报 / OpenAI相关 / Claude Code相关 / 原LAI如此 / …）。其余默认：不定时、不选话题、不开商业推广。
7. 提交前把标题、封面、标签（10 个）、简介计数、声明、分区、合集过一遍；**停在“立即投稿”前，用户明说“发布”才点**（用户也可能自己在页面里点；点了会跳“稿件投递成功”，页面里的 Quill 等元素消失）。投成功后页面可能自己多开一个视频页标签，一并关；我自己开的标签用完关掉。

## 投完核对（页面里 `fetch`，`credentials: 'include'`，返回只取要的字段）

- `https://member.bilibili.com/x/web/archives?status=is_pubing,pubed,not_pubed&pn=1&ps=3`：`bvid`、`state` / `state_desc`（刚投是 -1“审核中”）、`tid`、`tag`、`duration`（还在处理时是 0）、`desc` 长度、标题、`ptime`（Unix 秒，换算北京时间）。
- `https://member.bilibili.com/x/vupre/web/archive/view?bvid=…`：`archive.cover`（1920×1080）和 `archive.cover43`（1440×1080）要是**两张不同的图**（页面里 `new Image()` 取 naturalWidth / Height）；`videos[0].duration`。
- `https://api.bilibili.com/x/web-interface/view?bvid=…`：`ugc_season` 看合集——**审核中是 -404**，过审后再核对（member 接口里没有 season 字段）。
- 把 BV、时间、线上标题、实际标签写进 `投稿信息.json`、本期 README、`AGENTS.md`、合集 README、根 `README.md` 的视频存档表、记录文件；GitHub release / 提交 git 用户没说就不做。

## 已发布后发现缺东西

- 要换配音 / 画面：只能在编辑页「更换视频」（用户自己选文件），改完状态“修改内容待审核”，要重新过审；不改视频时可以把 SRT 当外挂字幕。
- 漏选合集 / 标题残留：编辑页补（用户要求时才做）。
