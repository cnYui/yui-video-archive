# 下载 @chetaslua 的 X 视频（TwitterSaver）

2026-10-02 09:01 起（本机时间）。

## 用户要求

“用浏览器插件使用这个网页：https://twittersaver.net/zh-cn，下载这些视频：（5 条 `x.com/chetaslua/status/…` 链接）然后保存到素材的文件夹中”

## 结果

- 4 个不同的视频，放在 `独立视频/2026-10_白宫超级智能协议/素材/X平台视频_chetaslua/`（整个 `素材/` 不进 git）：`chetaslua_<推文 ID>.mp4` ×4 + `来源.md`（原帖、发帖时间、内容、规格）。
- 每条取 TwitterSaver 给的最高清晰度：#1、#2 是 1080p，#3 是 1600p（2940×1600），#4 是 1492p（2940×1492）；H.264 + AAC，60 fps；ffprobe 校验过，时长和页面上显示的一致。
- 第 5 条（2104856471016235131）是 @chetaslua 对第 3 条（2101376238703333883）的引用回复，自己没有视频；TwitterSaver 给的是第 3 条的同一个 `video.twimg.com` 文件（把两条的 token 解开，源地址完全一样；也在 x.com 页面上看过）。所以只存了一份，没有重复。
- **放在哪个素材文件夹是我猜的**：用户只说“素材的文件夹”，仓库里有 7 个 `素材/`（`AI日报`、`AI科普`、`AI实操/01_…`、`Way to AGI/02_…/教程_Claude做视频`、`独立视频/` 下三条各一个）。按“最近在用的项目”放进了白宫超级智能协议的素材目录。这些视频和白宫那条没有直接关系（内容是 Fable 5.2 / 5.5、Opus 5.5 的纯 JS 演示）；用户要放别处，把整个 `X平台视频_chetaslua/` 文件夹挪过去就行。

- **更新（同一天稍后）**：用户接着说“你下载完成后，做一个 claude fable5.5 模型介绍的视频，多放素材少说话，用曼波的配音”——这 4 个视频就是那条视频的素材。已把整个 `X平台视频_chetaslua/` 挪到 `独立视频/2026-10_ClaudeFable5.5模型介绍/素材/`（上面“放在哪个素材文件夹是我猜的”那条作废），制作记录见 `20261002-092500-fable55-intro-video_CN.md`。

## 做法和踩到的坑（TwitterSaver）

1. **页面有点击劫持的广告，别用鼠标点它**：第一次 `left_click` 输入框，标签页就被带去了日本文具网站 hansoku-style.jp（没有开新标签，回 twittersaver 重新进即可）。
2. 稳的做法：`navigate` 到 `https://twittersaver.net/zh-cn` → `javascript_tool` 用原生 value setter 给 `input[type=text]` 填链接、派发 input / change，同一段脚本里按文字“下载”找到按钮 `.click()` → 等 5 s。
   - 用 `form_input` 填也行，但 **ref 编号会变**：广告有时多一个“Lesbian, Gay…”小链接，输入框是 ref_7 还是 ref_6、按钮是 ref_8 还是 ref_7 不固定（有一次 `form_input` 打到了按钮上报错）。每次先 `read_page` 看清再用，或者直接用脚本按选择器找。
   - `javascript_tool` 的返回值里带 URL 查询串（`?…`）或 cookie 会被拦（`[BLOCKED: Cookie/query string data]`）：脚本只返回简单字符串；脚本里的链接去掉 `?s=20` 分享参数，不影响解析。
3. 结果页的下载按钮是 `https://dl.snapcdn.app/get?token=<JWT>`（1 小时有效），`read_page` 的 interactive 模式能直接读出 href；JWT 的 payload 里写着真实源地址 `https://video.twimg.com/amplify_video/…/vid/avc1/<分辨率>/<名>.mp4`。下载前先把 payload 解出来，确认源站是 `video.twimg.com`，再 `curl.exe -L -A <Chrome UA> -e https://twittersaver.net/ -o <文件>` 直接下到磁盘：不走浏览器下载栏，也就没有“允许下载多个文件”的提示、不用再从 `Downloads` 里挪。
4. 清晰度从高到低列好几档（1600p / 1080p / 720p / 360p / 270p），按最高的取；竖屏或宽屏的视频高度和 1080p 不一样（这次有 2940×1600、2940×1492），别死找“1080p”。
5. 引用转推 / 回复会带出被引用那条的视频：用 JWT 里的源地址或原帖页面核对，别把同一个视频存两份。
6. 用完关掉了自己开的标签（插件的标签组随之消失）。

## 待办

- 等用户确认放哪个素材文件夹（我按白宫项目的放的）。
- 用到这些画面时片子里要标来源：账号 @chetaslua（`来源.md` 里有每条的原帖链接）。
