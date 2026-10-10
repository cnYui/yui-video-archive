# JoJo 后段（第10章、第11章、终章）+ 界面登记：做到哪了（因额度用完中途停）

记录时间：2026-10-09 22:52（日本时间）。我是并行分工里的 **late** 代理。协调者通知用户额度用完、立即停：两条在跑的真实键盘路线（第10章、终章）已手动中断，没有在跑的构建 / 测试。停时所有改过的 JS 都过了 `node --check`，`ui_texts.json`、`stands.json` 是合法 JSON。

游戏目录：`D:\大疆\游戏素材\JoJo\游戏\`（下面路径都相对它）。没有提交 Git，没有碰 `源码 / 角色图集 / 烘焙脚本 / 剧情分镜 / 音频` 原件和银魂工程。共享改动已逐条记在 `docs\交付\收尾_共享改动.md` 末尾。

## 已完成（有证据）

1. **终章两个真问题（交接 §4.4）**，`story/final.js`：
   - 首次觉醒：不再在 `W.ticks` 回调里再 push tick（world.update 把 ticks 过滤成新数组会丢）；改成 fight 自己的 tick 里 `growthTick` 每帧查，QTE 成功那一帧放行时停并收掉结果牌；失败照常 0.7 秒结果牌后由 Promise 收尾；重来 / 打完 / 回标题都会收掉残留 QTE（`dropGrowth`）。
   - 装死：`G.ui.insertUI` 按对象身份放回，try/finally 里在取消 / 重来时也放回、关插入画面、收路牌。`this.insertUI.draw is not a function` 消失。
   - 顺带修：布网倒计时减完停在小负数，`!s.warn` 为假，之后再也不出飞刀 / 切丝（归零）；第二段 DIO 只会被打到 1 HP，玩家一直没掉到 35% 以下时也能装死（否则卡关），并提示；第一段 DIO 先被打到 1 HP 时把下一次时停提前，保证“手指动了”觉醒一定出现；第三段剧情 U 的窗口 = 能量满（以前整场 HUD 都写「按 U！」）。
2. **`engine/debug.js` 观测字段（交接 §4.5）**：`teleLeft = dur − t`（t 是已过秒数）；`hitIn = 预警剩余 + (active[0] − tele.elapsed)`（以前多加一整段前摇）；hazard 读真实的 `t / delay / warn / phase`。只改观测，不改判定。**副作用（主代理提醒，已照做）**：`playtest.Tester.defend()` 现在会在远程招式“出手”那一刻闪避，弹体还在 100–160 px 外——各路线 Tester 对远程招式要按弹体距离反应（序章已由主代理改，后段在 `test_late_routes.py` 里改了）。
3. **`engine/timestop.js`**：时停台词大字的 Promise 没人接，回标题时报 `Uncaught (in promise) RunCancelled`，加了 catch。
4. **界面登记（任务 3）**：第2–5章缺的 23 个 key 全部补上（名牌 / 地点 / VS 文字照规划 §4.1、各章名牌原文；替身卡进 `stands.json`）；另补后段名牌 / 地点 / VS、时停台词 4 条、チク… タク…、以及别人文件里在用却没登记的 5 个拟声字；`tools/ui_jojo.py` 内置 specials 加 `jotaro_ts`、`阳光飞踢`、`正义 · 吸雾`（登记表 specials 节归战斗负责人，没碰）。新卡全部出过预览并目视检查（`C:\Users\yui\AppData\Local\Temp\claude\...\scratchpad\late\new_ui_sheet.png`，scratch 里，会话删了就没）。
   - 构建：`python -B tools\dev\full\locked_build.py ui font data check` 两次，**错误 0、警告 0、兜底 0**。
   - `tools/dev/full/test_asset_contract.py` 扩到运行时动态取的界面图（时停 lines、切入 title、special 的 title||name、拟声字、`S.vs({key})`、explore 的 location）。最后一次报告 **错误 2**，都在 `engine/moves.js`（二乔 / 伊奇 `special: { name, title: null }` → 查 `ui/special/波纹疾走`、`ui/special/愚者·沙之巨像`），归战斗负责人；他已在登记表加了 `joseph`、`iggy` 两条 specials，可能正在改 moves.js 的 title。
5. **后段夹具（任务 4）** `tools/dev/p1/test_late.py`：**45/45 通过**（`tools/dev/p1/_out/test_late.json`）。夹具修正：每 10 帧让出一次宏任务（以前只 await 一次微任务，剧情多跳 await 链比真实游戏晚）；预言失败菜单等 0.15 秒再按 Enter（菜单 0.08 秒内忽略确认）；D3 在真正冻结的 stopped 段用真实 J 验证排队；背景包用 `loadPack`；记录 pageerror 堆栈。回归：`test_cancel` 18/18、`test_core` 85/85、`timestop_test.js` 通过。
6. **后段剧情补齐（规划 §4.1/4.2/4.5）**：第10/11章、终章加篇章卡、地点卡、名牌（达比 / 泰伦斯 / 瓦尼拉）、VS 卡（奥西里斯神、皇帝&托特神、荷鲁斯神、阿图姆神、次中音萨克斯、奶油、世界）、奶油 / 白金之星·世界替身卡；战斗里的机关说明从顶栏改到右上（`L.hud`，同中段 `M.hud`，不压队长血条和 VS 标签）；第10章结尾先 `loadPack('bg_ch11')` 再进馆外（选章直进第10章时背景缺图）；三个预言共用一个荷尔·荷斯（以前每场留一个，第3个预言三人同时开枪）；奶油隐身段结束移走那个瓦尼拉；追车段左右 / 上下都能换道；机场 U 调查改成告别台词。

## 做了一半（停在这里）

- **真实键盘路线（任务 5）**：新建 `tools/dev/full/test_late_routes.py`（继承 `playtest.Tester`，只读快照 / `G.lateGame` / 战斗公开状态，动作全走键盘；含扑克选项、抓出千、布网、钟面瞄准、迷宫、棒球、两种车道小游戏、预言三解法、荷鲁斯神俯冲精准格挡、奶油虚空闪避、阳光飞踢、DIO 时停防御 / 装死 / 弹刀、远程招式按弹体距离防御、`--lose` 主动输、连输两次选「放水再来」、截图、FPS 采样、动作回退检查）。
  - 第10章第一轮在第3个预言反复失败 → 查出“三个荷尔·荷斯”并已修（证据 `tools/_playtest/late_ch10_run1_triple_holhorse/`）。修后第二轮跑到第1个预言（121 s，errors 0）时被叫停：`tools/_playtest/late_ch10/`。
  - 终章跑到屋顶布网（101 s，errors 0）时被叫停：`tools/_playtest/late_final/`（楼梯、追车截图已看过，正常）。
  - 第11章还没跑。**没有任何一章到章尾，不能写成通过；FPS 也没有完整采样。**

## 接着做（按顺序）

1. 在游戏目录依次跑（不要并行太多，免得 FPS 掉到 55 以下）：
   `python -B tools\dev\full\test_late_routes.py ch10 --out tools\_playtest\late_ch10`
   `python -B tools\dev\full\test_late_routes.py ch11 --out tools\_playtest\late_ch11`
   `python -B tools\dev\full\test_late_routes.py final --out tools\_playtest\late_final`
   再各加 `--lose` 跑一遍（输出目录 `late_*_lose`）。看 `result.json` 的 `errors`、`fps_summary`、`fallbacks`，逐张看截图。
2. 预计的难点：荷鲁斯神俯冲的精准格挡（8 帧窗口，`tight_parry` 按接触时间 ≤0.095 s 按 L）、奶油隐身段（HP 1200、只在探头 0.67 秒能打）、DIO 三段。卡住先看是 Tester 时序还是游戏问题，**不要为测试改判定**。
3. 跑完再跑一次 `python -B tools\dev\full\test_asset_contract.py` 和 `tools\dev\p1\test_late.py`；`prologue.js` 22:22 被主代理改过（加了 ポロッ），字库需要别人或下次构建 `ui font data check` 时带上。
4. 可选打磨：追车 / F-MEGA / 抓出千小游戏还是色块画（车用了矩形），可以改用现成 `prop:truck`、`prop:senator_car` 等道具图。
5. 写最终验收记录（新时间戳文件），不要改 AGENTS.md。
