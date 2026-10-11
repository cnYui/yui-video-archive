# JoJo 第4章重做 + 根仓库 PR #2 合并（2026-10-11 下午）

## 用户的话

- “接着做第四章”。
- 做的过程中又说“pr也合并”（根仓库 PR #2）。

## 根仓库 PR #2 合并

- https://github.com/cnYui/yui-video-archive/pull/2 用 merge commit 合并（6f2ee75），16 个提交的历史都保留；悠一声音的 modelId 在这条历史里是抹掉的。
- 本地 main 对齐 origin/main：`AGENTS.md` 有没提交的本地改动，直接 `git reset --keep` 会拒绝。dcg 钩子不让 `git checkout --` 丢改动，所以改成 `git stash push -- AGENTS.md` → `git reset --keep origin/main` → `git stash pop`（自动合并成功，本地改动都在，工作区里也不再有那个 ID）。合并过的本地分支 `claude/root-wrapup-20261011` 删掉了；远程分支还在，没删。
- **本地分支 `claude-projects-video-script`（没推过）是从没抹的旧提交上长出来的**：要推的话先把它自己的提交（5ef4808）挪到 origin/main 上，再扫一遍 ID。

## JoJo 第4章（印度）

做法照第2、3章：节拍表 → 背景 / 角色 / 音效派子代理并行 → 剧情重写 → 整章自动测试（正常 + 故意输）→ `ch4` 分支做完回 main。

- 节拍表：`游戏素材\JoJo\游戏\docs\章节素材调研\ch4_印度_节拍表.md`；剧情 `story\ch04.js`（87 行 → 约 700 行）。
- 流程：加尔各答街（一群小孩围住乔瑟夫要钱、圣牛舔波鲁纳雷夫、楼顶牛仔帽人影）→ 巷口荷尔·荷斯（分镜原句「比起当老大，我更适合当老二」）→ 雨中后巷：镜子里的倒吊人、阿布德尔推开波鲁纳雷夫倒下（剪影 + 枪声，不画血）→ 花京院：一起去 → 第 7 战 → 「为了雪莉」、雨停一道光 → 荷尔·荷斯拿奈娜挡剑逃走（掉了牛仔帽）→ 奈娜抓着乔瑟夫的手臂哭（一滴血）→ 街角没有葬礼、乔瑟夫看怀表 → 贝拿勒斯：乔瑟夫手臂上的女帝说话、偷吃水果、报纸通缉、女帝喊杀人犯、警哨 → 河坛第 8 战 → 奈娜的真面目剪影 → 恒河边会合。
- **按美术核对改的一处**：规划写“J·凯尔的死只看到帽子落地”，但 J·凯尔原图不戴帽子，原片 s09 落下的是荷尔·荷斯逃跑时掉的牛仔帽——改成 J·凯尔倒在雨水里（down 帧，不画血），荷尔·荷斯跑掉时掉帽子。
- 战斗机关沿用原来的，补演出：下雨、镜子 / 橱窗碎了切背景、开枪时荷尔·荷斯在画面边上露头 + 跳弹声、倒吊人换倒影的声音、念写指到的那只桶冒柏油、印度警察、警哨、女帝 3 级的帧。女帝贴在手臂上的缩放改成 l0–l2 原大、l3 ×0.8（原来小到看不见）。
- 修了两处：战斗结束后地图边界被还原成后巷（0–320）的，在 1280 宽的街上镜头卡在 x 0，过场里的人全在画面外；念写 / 波纹的藤蔓特效默认不会消失，一直留到结尾。
- 子代理做的：背景 `calcutta_street` / `india_alley` / `ganges_ghat` 重画、`varanasi_street` 新画；J·凯尔修 walk、补 kick / throw / down；女帝 l3；圣牛 `npc_cow`；印度警察皮肤 `npc_police.india_*`；道具 `tar_drum` / `wood_barrel` / `fruit_basket`；音效 10 个（`ricochet` / `mirror_flash` / `police_whistle` / `cow_moo` / `lick` / `empress_voice` / `temple_bell` / `rain_loop` / `bazaar_loop` / `ghat_loop`）。
- 新地点卡「印度·贝拿勒斯」（`tools\registry\ui_texts.json`）；`tools\dev\full\playtest_mid.py` 加了剧情台词截图。
- 验收：构建 0 错误 / 0 警告 / 0 兜底；正常路线 271 s 0 报错（`tools\_playtest\c4_v2`）；故意输路线 329 s 0 报错（`c4_lose1`，倒吊人输 2 次后有「放水再来」、女帝输 1 次后重来）。`dev_fight.py` 用的是通用测试器，不会打倒吊人的倒影机关（单独跑会一直输），只适合单独打女帝。
- 提交：JoJo 仓库 main `bf0d69b`（`ch4` 分支已合并删除）。

## 没人确认过的

- 新台词和新音效没人听过、玩过。
- 奈娜“指尖留下一滴血”是为了接上女帝的来历补的一句旁白；原著细节没核。
