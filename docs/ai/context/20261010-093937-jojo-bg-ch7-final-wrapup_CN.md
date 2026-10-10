# JoJo：第7章–终章背景重画（bg-late）收尾——用户叫停，主代理代写

时间：2026-10-10 上午。游戏目录 `游戏素材/JoJo/游戏/`（被根仓忽略，不提交）。
用户 2026-10-10 决定先把**序章 + 第1章**做成 demo 发布，这条线 09:32 左右被用户停掉、不能再唤醒，收尾由主代理按它的工作记录整理。用户以后有空再接着做。

## 当时的任务

把第7章–终章 31 张背景按动画场景重画、精度大幅提高，每张做成独立模块 `tools\bg_new\<key>.py`，在 `tools\bg_jojo.py` 里改路由；保持剧情依赖的尺寸、可走带、`anchors`、命名图层（宅邸的 `hide_*`、潜艇的牙齿 / 潜望镜 / 屏幕 / 钟、幻觉循环等）；每张出改前 / 改后对照图并在游戏里截图核对。

31 张：
- 第7章：`redsea_island`、`submarine`、`seabed_mouth`、`egypt_coast`
- 第8章：`desert_day`、`aswan_town`
- 第9章：`egypt_temple`、`nile_bank`、`egypt_rail`、`luxor_town`、`luxor_house`
- 第10章：`cafe_interior`、`cairo_day`、`cairo_sewer`
- 第11章：`mansion_exterior`、`mansion_corridor`、`game_room`、`mansion_illusion`、`illusion_corridor`、`mansion_hall`、`coffin_tower`、`mansion_tower`
- 终章：`mansion_stairs`、`cairo_night`、`cairo_street_night`、`cairo_rooftops`、`cairo_dawn`、`cairo_street_dawn`、`cairo_sunrise`、`kujo_bedroom_morning`、`airport`

## 做了什么

- 读完了要求的资料、原版 `源码\engine\bg_egypt.py` / `bg_asia.py` 的画法（噪声纹理、`_fbm_wrap` 等）、`docs\美术精度对比\`、`docs\调研\06_JoJo背景库.md`、角色锚点（`atlas.js` pivot）。
- 新增预览工具 `tools\bg_new\late_preview.py`（只写 `tools\bg_new\_preview\late\`，不碰 `assets\` / `data\`）：
  - `python -B tools\bg_new\late_preview.py before`：用当前正式构建拍“改前”（2 倍最近邻，宽地图按镜头 0 / 中间 / 最右横拼）
  - `after [key ...]`：跑 `tools\bg_new\<key>.py` 出图层 + 预览，另出一张在可走带上下沿摆承太郎 / 波鲁纳雷夫 / 伊奇的“带人”图
  - `compare [key ...]`：改前 / 改后上下对照 + 总览
- 跑过一次 `before`（输出在 `tools\bg_new\_preview\late\before\`）。

**没有改任何游戏文件**：没有新背景模块、没改 `bg_jojo.py` / `later_stages.py` / `packs.json`，游戏里还是旧背景，构建不受影响。

## 没做什么（以后接着做）

31 张一张都没重画；没有改后对照图、没有游戏内核对。

## 下次接着做的入口

- 先读：`D:\大疆\AGENTS.md`（JoJo 段）、游戏根目录 `README.md`、`规划.md` 第7章–终章的地图表和场景描述、`docs\技术约定.md`、`docs\交付\收尾_共享改动.md`；参考分镜 `游戏素材\JoJo\剧情分镜\`（只读）。
- 预览工具已经有了：`tools\bg_new\late_preview.py`（`before` / `after` / `compare`），`KEYS` 和各图可走带都写在文件开头。
- 现有画法在 `tools\bg_new\later_stages.py`；路由 `tools\bg_jojo.py` 的 `_LATER_PACKS` → `EXPORTERS`；契约测试 `tools\bg_new\test_contract.py`。
- 动之前每个 key 先 grep `story\stages_ch06_09.js`、`stages_late.js`、`chNN.js`、`final.js` 里用到的锚点 / 图层名（宅邸 `hide_*`、潜艇牙齿 / 潜望镜 / 屏幕 / 钟、幻觉循环）。
- 正式构建：`python -B tools\dev\full\locked_build.py bg data check`（会重导所有背景，较慢；平时用预览迭代）。
