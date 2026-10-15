# AI每日视频 routine 转换为 GPT 版本

时间：2026-10-15（+09，日本东京）

## 来源

- Claude routine：`C:\Users\yui\.claude\scheduled-tasks\ai-daily-news-produce\SKILL.md`
- 业务技能：`D:\大疆\AI日报\skill\ai-daily-news\SKILL.md`
- 工作目录：`D:\大疆`

本次迁移的是 Claude 侧的“AI日报-每日生成”主 routine，不包含另一个独立的“AI日报-分段章节” routine。原 routine 的执行时间为每天东京 04:30（北京时间 03:30）。

## GPT 版本

- 名称：`AI日报每日生成（GPT）`
- 类型：Codex 本地 cron 自动化
- 时间：每天 04:30，按当前 Codex 客户端的 Asia/Tokyo 时区解释
- 模型：`gpt-5.6-sol`
- 推理强度：`high`
- 项目：`D:\大疆`

GPT 版本沿用现有 AI日报技能和当前用户规则：先读状态并从断点继续；竖屏 1080×2340；本机免费开源 TTS；自动 gate 和 AI 复核；只发布 B 站；每天同步带配图的 note.com 日文文章；抖音、小红书、视频号保持暂停；登录、浏览器、人机验证、付费或连续重试失败时停止并如实记录；成功或失败都写运行记录和中文报告。

## 边界与风险

- 没有改动或删除 Claude 原 routine，便于回退和对照；因此迁移后的 GPT 自动化与 Claude 原 routine 同时存在，启用前应确认只保留一个实际执行者，避免同一天重复制作和发布。
- Codex 版本使用当前可用的浏览器 / Playwright 工具完成平台操作，不假设 Claude 专用工具存在。
- 本记录只描述迁移，不代表某一天的日报已经制作、审核或发布成功。
