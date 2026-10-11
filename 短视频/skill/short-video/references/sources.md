# 素材：从哪下、怎么下

常用网页记在 `D:\大疆\AGENTS.md`「四个合集和发布平台 → 常用网页」。账号内网页一律用 Chrome 插件（内置浏览器没有登录态）。下载前先 `ListAgents`：Chrome 有别的会话在用就先发消息约。

| 来源 | 做法 |
|---|---|
| X（推特） | `python scripts/fetch_x_video.py <推文链接> … --out <合集>\素材\<YYYY-MM_主题>`：X 公开嵌入接口给 `video.twimg.com` 直链，取最高码率、ffprobe 核对、写 `来源.md`。用户点名用下载站时，用 SaveTwitter（`https://savetwitter.net/zh-cn3`）。 |
| B 站 | 用户指定的站：SnapAny（`https://snapany.com/zh/bilibili`）、备用 ToolsKitHub（`https://toolskithub.com/zh-CN/bilibili-download`）。SnapAny 免费只够解析 4–5 次，之后弹「开通会员」——**别付费**，告诉用户，再用备用站或下面的接口。 |
| B 站（接口，下载站用不了时） | 在已登录的 B 站标签页里：`x/web-interface/view?bvid=` 取 aid / cid → `x/player/playurl?avid&cid&qn=64&fnval=0&platform=html5&high_quality=1` 取 CDN 直链 → `fetch` 成 blob → `<a download>` 存盘。细节和坑见 `docs/ai/context/20261004-095601-ai-dayuanjing-script-style_CN.md`：要在 `api.bilibili.com/x/web-interface/nav` 这种纯 JSON 页里做（space 页是单页应用，点 blob 链接会把页面带走、数据全丢）；同一标签页第二次自动下载会被拦，换新标签页；多个文件拼成一个包一次存。 |
| YouTube（官方频道） | 用户一般直接给下载好的文件（第 1 条是 4K VP9 `webm` 画面 + `weba` 声音）。原声不用时只要画面那个文件。 |
| 官方页面 / 论文 / 推文截图 | `制作\00_整片\capture_pages.py`（填 SPECS）→ `pageShot()`；推文截图用 `platform.twitter.com/embed/Tweet.html?id=…`。 |

- 素材放合集层 `<合集>\素材\<YYYY-MM_主题>\`（用户 2026-10-04：“素材可以公用”，短、长视频共用，别放进 `短视频\` / `长视频\` 里；视频文件本来就不进 git），`common.py` 的 `XV` 指这个子目录，`SRC` 每个一行写清：谁的、什么内容、规格、有没有声；别处已经下过的直接写绝对路径引用，不重复下。
- 子目录里放 `README.md`（或 `来源.md`）记：原链接、作者、发布时间、下载方式和时间、文件大小、挂名怎么写。例：`独立视频\素材\2026-10_image-blaster\`。简介里写清画面来源，声明版权归原作者。
- 别人的视频只做介绍和评论引用：不整段搬运原声，用中文配音重新讲。
