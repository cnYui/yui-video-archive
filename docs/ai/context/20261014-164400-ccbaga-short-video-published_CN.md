# CCBaga 短视频完成发布

## 本轮授权

用户明确要求只发 B站，封面为「Claude永不封号？！」，标题为「这个github开源项目防止你的Claude封号！ccbaga」，使用 Chrome 的 Playwright 插件；小于 10 MB 的原片用 JS 上传，填表后直接点击发布。此次授权覆盖本期上传与发布，不再要求手动拖入或二次确认。

## 成片与制作

- 目录：`Claude Code相关/短视频/04_CCBaga环境工具/`。
- `CCBaga_成片.mp4`：7,156,553 字节，1080×2340，30 fps，86.53 秒；本机 Qwen3-TTS 配音、中英双语字幕，不出镜、不加片头片尾。
- 用户指定的封面 A：16:9 与 4:3 分别上传，关闭双比例同步。
- 内容包括本地身份归档、独立浏览器配置、语言时区地区对齐、网络出口与浏览器读数核验。明确全绿不保证免封、本地归档不清除平台服务端记录、选择地区不改变公网 IP；没有运行真实清理、系统修改或网络部署。

## 上传与发布证据

- 使用已有本期独立桥接队列 `C:/Users/yui/AppData/Local/Temp/pw_ccbaga_20261014` 连接 Chrome Playwright MCP Bridge，沿用登录态。
- 标准文件上传此前报 `DOM.setFileInputFiles: Not allowed`。按本轮明确授权，以 `File` / `DataTransfer` 给投稿页已存在的文件输入框传入完整原片并触发 change。没有压缩、分块或启动上传服务器。
- 页面显示 `CCBaga_成片`、`上传完成`，投稿前读回标题、简介、标签、人工智能分区、合集、AI 声明。
- 「Claude」标签被页面丢弃；选择推荐标签「claude」后读回 6 个标签。
- 点击「立即投稿」一次，页面显示「稿件投递成功」和「上传成功，已加入合集」。
- 投稿时间：2026-10-14 15:41:19 北京时间，16:41:19 东京时间。
- aid：117438129702417；bvid：BV1CxpC69ESE；cid：42732094824。
- 公共链接：https://www.bilibili.com/video/BV1CxpC69ESE/
- 创作中心 `/x/vupre/web/archive/view`：state 0，state_desc「开放浏览」，had_passed true，creation_statement id 1「含AI生成内容」，视频 duration 87 秒。
- 公开 `/x/web-interface/view`：code 0、state 0，标题一致；tid 231；ugc_season id 9223239、title「Claude Code相关」。
- 稿件列表 `/x/web/archives`：code 0，找到同一 BV 号、aid 与标题，state 0「开放浏览」、duration 87 秒。
- 两张线上封面为不同 URL：个人空间 cover 1920×1080，首页推荐 cover43 1440×1080。
- 标签：CCBaga、人工智能、Claude Code、开源工具、AI工具、claude；简介与本期投稿信息一致。

## 交付与保留

本期投稿信息、README、合集及短视频台账更新为已公开。原片、素材、配音、字幕与封面均保留，不做文件清理或 Git 提交。历史 context 文件保持原样。操作脚本位于本期 `制作/pw_*.py` 与 `pw_*.js`，核验证据位于 `制作/B站发布核验.json`；媒体编码参数只放私有临时队列，不纳入公开仓库。

后续边界：本轮 JS 上传授权针对本期小于 10 MB 的原片；未改写其他视频的默认发布规定。
