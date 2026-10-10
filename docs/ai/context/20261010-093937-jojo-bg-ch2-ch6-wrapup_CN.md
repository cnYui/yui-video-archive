# JoJo：第2–6章背景重画（bg-mid）收尾——用户叫停，主代理代写

时间：2026-10-10 上午。游戏目录 `游戏素材/JoJo/游戏/`（被根仓忽略，不提交）。
用户 2026-10-10 决定先把**序章 + 第1章**做成 demo 发布，这条线 09:32 左右被用户停掉、不能再唤醒，收尾由主代理按它的工作记录整理。用户以后有空再接着做。

## 当时的任务

把第2–6章 24 张背景按动画场景重画、精度大幅提高（建筑 / 道具 / 招牌 / 质感 / 光影 / 多层视差，人物在可走带上清楚），每张做成独立模块 `tools\bg_new\<key>.py`，在 `tools\bg_jojo.py` 里改路由；保持剧情依赖的尺寸、可走带、`anchors`、命名图层、`hide_*` / 座位 / 门等位置；每张出改前 / 改后对照图并在游戏里截图核对。

24 张：
- 第2章：`yacht_deck`、`freighter_deck`、`freighter_corridor`、`underwater`（common 包）
- 第3章：`singapore_street`、`singapore_hotel`、`cable_car`、`train_interior`
- 第4章：`calcutta_street`、`india_alley`、`ganges_ghat`、`varanasi_street`
- 第5章：`desert_highway`、`mountain_road`、`fog_town`、`enya_inn`、`inn`、`karachi_street`、`brain_inside`
- 第6章：`desert_noon`、`yaprin_village`、`cessna_cabin`、`dream_carnival`、`desert_night`

## 做了什么

- 读完了要求的资料、构建流程（`build_assets.py` 的 bg 步骤、`bg_jojo.py` 路由、`later_stages.py` 现有画法）、原版 `源码\engine\bg_asia.py` / `bg_egypt.py` / `core.py` 的画法（渐变、拜耳抖动、噪声纹理），以及角色尺寸（`tools\_meta\chars.json`）。
- 拍了 24 张的“改前”图：`tools\bg_new\_preview\bg_mid\before\<key>.png`（用当前正式构建的数据渲染）。
- 正准备写共用绘图工具（kit：画图元 + 导出 / 自检）时被停。

**没有改任何游戏文件**：没有新模块、没改 `bg_jojo.py` / `later_stages.py` / `packs.json`，游戏里还是旧背景，构建不受影响。

## 没做什么（以后接着做）

24 张一张都没重画；共用 kit 没写；没有改后对照图、没有游戏内核对。

## 下次接着做的入口

- 先读：`D:\大疆\AGENTS.md`（JoJo 段）、游戏根目录 `README.md`、`规划.md` §5.3 起的各章地图表和场景描述、`docs\技术约定.md`、`docs\交付\收尾_共享改动.md`；参考分镜 `游戏素材\JoJo\剧情分镜\`（只读）。
- 现有画法在 `tools\bg_new\later_stages.py`（`make(key)` / `export()`），路由在 `tools\bg_jojo.py` 的 `_LATER_PACKS` → `EXPORTERS`；预览 `tools\bg_new\_pv.py`；契约测试 `tools\bg_new\test_contract.py`。
- 改前图已经在 `tools\bg_new\_preview\bg_mid\before\`。序章 / 第1章场景代理这次画的 `tools\bg_new\school_stairs.py` 等可以当单张模块的写法参考；第7章–终章那条线留了 `tools\bg_new\late_preview.py`（改前 / 改后 / 对照一条命令），可以照着做一个第2–6章的版本。
- 动之前每个 key 先 grep `story\stages_ch02_05.js`、`stages_ch06_09.js`、`chNN.js` 里用到的锚点 / 图层名。
- 正式构建：`python -B tools\dev\full\locked_build.py bg data check`（会重导所有背景，较慢；平时用自己的预览迭代）。
