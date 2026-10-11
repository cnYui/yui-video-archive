# JoJo 第3章重做 + 根仓库 PR（2026-10-11 中午）

## 用户的话

- “一张一张来，第二章做完之后再做第三章”（语音输入：一张 = 一章）。第2章上午做完，接着做第3章。
- 中途要求“Create PR”（根仓库 cnYui/yui-video-archive → main）。

## 根仓库 PR

- PR：https://github.com/cnYui/yui-video-archive/pull/2 ，分支 `claude/root-wrapup-20261011`。内容是本地 main 攒下的 15 个提交（10-01 到 10-11）。
- 推之前扫了整段 diff：没有邮箱（只有 ffmpeg 日志里的 `ffmpeg-devel@ffmpeg.org`），没有 key / token / 电话。**悠一声音的 modelId（完整 32 位）在 `AGENTS.md` 里，订阅教程的 `tts/raw/web_usage.txt` 里有它的前 8 位**。问了用户，用户选“抹掉再开 PR”。
- 做法：脚本把 origin/main..main 的 15 个提交逐个重放（临时 index + `commit-tree`，不碰工作区），只替换这两处——`AGENTS.md` 换成「不公开：在 Fish 网页版「我的声音」里看」，`web_usage.txt` 换成「modelId 不公开」；作者、时间、提交说明都不变。核对：新分支和本地 main 只差这两行，整条新历史里搜不到这个 ID。
- **本地 main 还是原来没抹的提交**（哈希不同）。PR 合并以后用 `git reset --keep origin/main` 对齐，工作区没提交的改动会留着。合并之前别的会话在本地 main 上的新提交，要 rebase 到 origin/main 上再推。
- 没收进 PR 的：别的会话的未提交改动（AI日报 10-11、AI科普 第 05 / 06 期、B站互动、`Claude Code相关/04_ClaudeProjects` 等）；`AGENTS.md` 本地没提交的几行（含等用户定的个人信息）。

## JoJo 第3章（新加坡）

做法照第2章：先写节拍表，背景 / 角色 / 音效派子代理并行，剧情自己重写，整章自动测试（正常 + 故意输），`ch3` 分支做完回 main。

- 节拍表：`游戏素材\JoJo\游戏\docs\章节素材调研\ch3_新加坡_节拍表.md`；剧情 `story\ch03.js`（52 行 → 约 950 行）。
- 流程：骑楼街（警察问安妮护照、樱桃摊、鱼尾狮海报、三轮车）→ 分房（波鲁纳雷夫要单人间）→ 夜里单人间查房（妹妹的照片：两只右手的伏笔）→ 冰箱门自己开、迪波 → 第 5 战 → 房间狼藉 → 第 6 天早上：假花京院的破绽（连核嚼樱桃、垃圾桶被黏液吞掉、小贩的话、安妮说他踢猫、阿布德尔 / 承太郎 / 乔瑟夫用替身看他）→ 缆车外景 → 指认 → 第 6 战 → 海面求饶（荷尔·荷斯、J·凯尔两只右手）→ 火车：波鲁纳雷夫听到“两只右手”、安妮跟到印度、rerorero。
- 战斗：
  - 黑檀木恶魔：段 1 迪波故意挨打攒恨意；段 2 玩偶藏起来时三块镜子碎片照出它、它脚下冒灰 + 沙沙声、露出来会骂人。
  - 黄色节制：旧版测试器连输 4 次、黏液形态的动作名接不上（打起来就是普通拉巴索）。改成黏液吸收伤害但挡不住冲力，J3 把他推到端窗撞出去 / 贴近 U，掉海插一段缆车外景，水下限时 24 s；HP 600 → 500、黏液每层每秒 −1 → −0.5。规划 §6.2 同步改了。
- 子代理做的：背景 `singapore_street` / `singapore_hotel` / `cable_car` 重画、`cable_view` 新画；玩偶 `devo_doll` 重新设计（+ jump / peek），拉巴索黏液铠甲皮肤 `armor_*`，假花京院派生皮肤 `kakyoin.fake_*`（花京院原图逐像素没变），门童 `npc_bellhop`，道具 `slime_pool` / `trash_can` / `mirror_piece` / `doll_razor`；音效 `razor` / `doll_voice` / `doll_scurry` / `fridge` / `slime` / `slime_absorb` / `fan_loop` / `city_loop` / `cable_loop` / `train_loop`。
- 共享改动记在 `docs\交付\收尾_共享改动.md`：`story/common.js` 的 `drawBg` 多一个 state 参数（插入画面画碎窗）、`engine/moves_ch02_05.js` 第3章招式的音效和动作、`tools/playtest.py` 第3章两场的战术和覆盖检查、`tools/build_audio.py`、`tools/bg_jojo.py` 路由、`packs.json`。
- 验收：构建 0 错误 / 0 警告 / 0 兜底；正常路线 231 s 0 报错（`tools\_playtest\c3_final2`，迪波 52 s、黄色节制 23 s）；故意输路线 330 s 0 报错（`c3_lose1`，迪波输 2 次后有「放水再来」、黄色节制输 1 次后重来）。
- 提交：JoJo 仓库 `ch3` 分支 `bc4b1a9`。

## 没人确认过的

- 新台词和十个新音效都没人听过、玩过；测试器打黄色节制只要 23 s，真人大概要久一些。
- 安妮跟到印度的理由（SPW 联系上她爸爸，人在外地回不来）是按规划 §6.1 “跟到第5章送上飞机”补的。
