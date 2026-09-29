# B 站自动投稿工具调研（GitHub 开源 + 官方开放平台）

- 时间：2026-09-28（UTC+9），下午。第 4 期会话「大肥鱼锐评模型排行视频」做的。
- 起因：第 4 期成片 60 MB，Claude in Chrome 插件一次最多往网页传 10 MB。用户先说“你尝试用脚本选择一下文件看看行不行”：插件 `file_upload` 被拒（`total upload size would exceed 10 MB`）。用户又说“你上github查一下有没有开源的b站视频自动发布的插件，看看能不能拿过来使用”。
- 结论：**biliup 能用，但要用户拍板**：它走 B 站非公开接口，一上传就直接投稿，还要装软件、扫码登录。这一期用户仍然手动上传（BV1t7aG6wEK5）；要不要引入 biliup，**待用户决定**。

## 为什么浏览器插件做不到

- 浏览器规定网页里的本地文件必须由人来选，扩展和网页脚本都拿不到硬盘上的文件。所以“全自动”只能靠本机程序直接连 B 站。
- 不做的绕法：
  - 把文件切块、用脚本在页面里拼回去：等于绕过插件的上传限制。
  - 本机起服务器让页面来取：第 1 期试过，Chrome 弹“访问本地网络”，页面卡死。
  - 压到 10 MB 以内：6 分钟以上的 2340×1080 会糊。
- 《AI每日日报》现在就是压成 ≤9 MB（约 150 kbps）的上传版再用插件传。

## 找到的项目（2026-09-28 查）

| 项目 | 状态 | 说明 |
|---|---|---|
| [biliup/biliup](https://github.com/biliup/biliup) | MIT，约 5.4k 星，活跃（v1.2.10 于 09-27 发布，PyPI 1.2.9 于 09-26 发布） | 录播 + 投稿工具，带命令行 `biliup upload`、`biliup append`、`biliup season list/sections/add/remove/sort`（合集）、`biliup login/renew`、`biliup comments/reply`，还有 WebUI（默认只绑 127.0.0.1:19159） |
| [biliup/biliup-rs](https://github.com/biliup/biliup-rs) | 2025-11-30 归档，并入 biliup | 旧的 Rust 命令行版 |
| [dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload) | MIT，约 15k 星，2026-03 更新 | 多平台一键发布；B 站部分就是包装 biliup，第一次运行会自动下载 biliup。多一层，没必要 |
| [Nemo2011/bilibili-api](https://github.com/Nemo2011/bilibili-api) | 2026-07-06 收到 B 站委托律所的函件后永久关停、归档 | Python 库，原来有 video_uploader。不用 |
| bilibili-API-collect | 2026-01-28 收到律师函，停止维护并删除（[IT之家](https://www.ithome.com/0/917/481.htm)） | B 站非公开接口文档 |
| 同期收函的还有 | BiliRoaming、[BiliTools](https://github.com/btjawa/BiliTools)（2026-07-06），PiliPala（2025-07） | B 站对逆向非公开接口的项目态度很严 |

## biliup 能填哪些字段（读源码 `crates/biliup/src/uploader/bilibili.rs` 的 `Studio` 结构，2026-09-28）

- 命令行参数：
  - `--title`、`--desc`、`--tag`（逗号分隔）、`--cover`、`--dynamic`。
  - `--tid`（旧分区，默认 171）、`--tid-v2`（新版分区）。
  - `--dtime`（定时，10 位时间戳，至少 4 小时后）。
  - `--copyright`、`--source`、`--no-reprint`、`--charging-pay`。
  - `--is-only-self`（仅自己可见）。
  - `--up-selection-reply`、`--up-close-reply`、`--up-close-danmu`。
  - `--extra-fields`（任意附加提交参数）。
  - `--line`（上传线路）、`--limit`（并发）、`--submit`（web / app / client 接口）。
- 合集：投稿后用 `biliup season add <小节ID> --vid BV…`。
- 没有的：
  - 创作声明「含AI生成内容」没有专门参数（字段名不知道，不去逆向找）。
  - 4:3 封面没有单独参数。
  - 没有“存草稿”：`upload` 就是提交稿件（接口 `x/vu/web/add/v3` 或 `x/vu/app/add`）。
- 登录：
  - `biliup login` 支持短信、账号密码、扫码、浏览器、网页 Cookie 几种方式。
  - 凭证存在 `cookies.json`，可以用 `-u/--user-cookie` 指定位置。这个文件就是账号的完整登录状态。
- 安装：
  - `uv tool install biliup`，装在单独的环境里。本机已有 uv 0.9.29。
  - Windows 包 `biliup-1.2.9-cp39-abi3-win_amd64.whl` 21.7 MB，依赖 yt-dlp、aiohttp、pillow、requests、streamlink、rsa。
  - 或者用 Release 里的桌面安装包。还没装。

## B 站开放平台（官方）

- [开放平台文档](https://open.bilibili.com/doc) 里有「服务端视频稿件投递」：
  - 流程：文件上传预处理 → 分片上传 → 合片 → 封面上传 → 稿件提交 → 分区查询。
  - 单个 ≤100 MB 的文件可以一次上传（`openupos.bilivideo.com/video/v2/upload`）。
  - 另有稿件查询、编辑、删除。
  - 权限 Scope `ARC_BASE`，要申请权限，还要用户授权。
- 稿件提交接口 `arcopen/fn/archive/add-by-utoken` 的字段：
  - 有：title（<80）、cover、tid、no_reprint、desc（**<250 字**）、tag（总长 <200）、copyright、source、topic_id、mission_id。
  - 没有：合集、定时、创作声明。
  - 提交后要审核；非正式会员一天最多 5 个稿件。
- **个人用不了**：「入驻」页写着“暂未开通个人开发者的申请入驻”。要营业执照、盖章公函，应用地址的 ICP 备案要和主体一致。

## 如果以后要用 biliup，建议的流程（待用户同意）

1. 用户在自己的终端运行 `biliup login`，用手机扫码。`cookies.json` 放在用户目录（不进项目、不进任何同步目录），Claude 不读它的内容、不在对话里出现。
2. 用 `--is-only-self 1`（仅自己可见）上传：标题、标签、简介、封面、`--tid-v2`（人工智能分区的编号要先查）；再 `biliup season add` 加进「原LAI如此」。
3. 创作声明、4:3 封面，用插件在编辑页（`/platform/upload/video/frame?type=edit&bvid=…`）补上。
4. 用户在创作中心检查后，自己改成公开。这一步就相当于「立即投稿」由用户点。
5. 《AI每日日报》可以不用再压到 9 MB，直接传原画质。它是全自动定时发布，用 `--dtime` 就行，但要先问用户。
- 风险要说清楚：非公开接口有账号风控风险；`cookies.json` 泄露等于账号被人登录；B 站今年一直在给这类项目发函。

## 这次用到的其他事实

- 投稿页底部除了「立即投稿」还有「存草稿」（网页自己的草稿功能，biliup 没有）。
- 插件 `javascript_tool` 返回网址、HTML 会被拦，只返回自己拼的短文本或布尔值。
