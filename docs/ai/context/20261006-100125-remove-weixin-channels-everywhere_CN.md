# 去掉视频号（全局，2026-10-06）

用户 2026-10-06：先说“同步到短视频skill中，原创声明 就是小红书应该选择的，视频号之后不发，把视频号这个平台移除短视频发布skill，然后标题修改为入门，你来修改”（只动了短视频技能 + RL 那条的标题）；我问“日报 routine、OpenAI相关 / Claude Code相关整期流程、AGENTS.md 里还写着视频号，要一并去掉吗？”，用户答：**“去掉视频号”**。时间 10:01（Asia/Tokyo）。

## 改了什么
- **短视频技能**（上一步已做）：三平台、标题 3×3、旧做法存档 `短视频/skill/short-video/references/_archive/视频号发布_已移除_20261006.md`。
- **日报技能 `AI日报/skill/ai-daily-news/`**：`SKILL.md`（描述 / 发布平台 / 标题 / 合集 / 第 6、8 步 / 第 9 步推送；第 8d 节视频号整段原样搬进上面的存档，原位留墓碑）、`scripts/daily.py`（`TITLE_LIMITS` 去掉视频号短标题、`auto_titles` 不再生成视频号标题、`build_publish_info` 不再写 `weixin_channels` 块、gate 的“标题 / H.264 上传版”文字、`--also` 帮助、`NEXT` 提示）、`scripts/make_episode.py`（`titles` 检查去掉视频号）、`scripts/make_vertical.py`（只改注释 / 打印）、`assets/vertical-engine/index.html`（一句注释）。冒烟测过：三个脚本 py_compile 通过；`make_episode.py 2026-10-06 --check` 通过；`platform_titles` 返回三个标题；`build_publish_info` 不再有 `weixin_channels`、小红书块 `original: True`。
- **日报 routine（`ai-daily-news-produce`）的提示词**：用 `update_scheduled_task` 改了（三个平台、去掉“视频号不发并推送提醒”、推送 / 报告里不再写视频号结果）；cron 不变（东京 04:32）。
- **小红书“原创声明”开**（用户同一天定的平台规则）：日报技能第 8c 步和 `build_publish_info` 的 `original` 也跟着改成开——这是我按“小红书应该选原创声明”推广到日报的，**不是用户单独对日报说的**，不对就改回（SKILL.md 第 49 行 / 第 8c 第 4 步、`daily.py` 的 `"original": True`）。
- **AGENTS.md**：发布平台 3 个（视频号网址标“已不发，仅备查”）、日报 / Claude官方教程 / 日报竖屏 / 标题等条目、“视频号待发”的两个作品改“不发”。
- **README / 作品状态**：`短视频/README.md`、`独立视频/README.md`、不再Review 短视频和 Claude封号潮 的 README / `投稿信息.json` 里“视频号待发”改“不发（用户 2026-10-06 定）”。
- **Claude官方教程**：`计划.md`（标题规则表去掉视频号行、十期标题表去掉视频号列、发布 / 合集 / 待办 / 简介模板 / 封面都改三平台）、`README.md`。
- **清理工具**：`docs/ai/tools/published_cleanup/README.md` 判据改成只看三个平台（没有执行任何清理）。
- **记忆**：publish-platforms-four 等条目范围从“短视频”扩到“全部”。

## 没动
- 历史记录（`docs/ai/context/` 里以前的、各作品已发布的 `投稿信息.json` / README 里写着“视频号已发表”的）：那是当时的事实。
- Tim Denning 系列（`独立视频/短视频/_TimDenning系列/`）的脚本 / 交付包：[93e3d5] 在用，已发消息请他们自己去掉视频号。
- `docs/ai/tools/chrome_group_recover/*.ps1` 里的视频号字样（只是例子 / 标签名）。
- 视频号上已发的作品、合集、登录态：没碰。

## 要用户知道的
- 以前“视频号待发”的两个作品（不再Review 短视频、Claude封号潮）现在算已发布，进了“可清理本地视频”的范围；**没有清理**，要不要清问用户。

## 补：小红书“原创声明”要用户本人同意须知（10:2x）

> **已作废（2026-10-06 晚）**：用户说“《原创声明须知》之后都是你来勾选，我已同意”，以后由我来勾，不用问、routine 也直接勾；下面是 10:2x 当时的情况。
[93e3d5]（Tim Denning 会话）发现：点开小红书“原创声明”开关会弹《原创声明须知》，要勾选“我已阅读并同意”，**这个同意得用户本人给**（接受条款 / 协议不能替用户做），它没勾、在聊天里问了用户“开 / 关”。所以我上面“日报也改成开”要加保护：日报技能第 49 行 / 第 8c 步第 4 条、routine 提示词（`update_scheduled_task`）、短视频技能 `SKILL.md` / `publish.md`、记忆 `short-video-declare-ai-everywhere` 都补了“弹出须知就不勾、保持关闭、推送写明；用户在场就在聊天里问”。`daily.py` 的 `"original": True` 只是期望状态，实际由技能第 8c 步的保护决定。用户是否已经同意过须知、同意后还会不会再弹，没验证。
