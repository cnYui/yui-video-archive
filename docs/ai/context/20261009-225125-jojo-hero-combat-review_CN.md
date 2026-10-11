# JoJo 六名主角战斗逐帧审查（combat 代理，2026-10-09 晚，额度到上限中途停）

游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（整个目录被根仓忽略，没有提交）。按协调者“立即停止”的要求收尾：停在最后一轮改动之后、回归测试之前。所有改过的 JS 都过了 `node --check`。

## 已完成

**1. 阿布德尔 J 火球（用户截图：火从替身拳头出来、火球却从地上冒出来）**
- 根因（`engine/combat.js`）：`moveTick` 把整个角色对象当出手点 `o` 并进弹体——z = 角色 z = 0（火球贴地飞，`|z − 20| > hitR[2]=18` 永远打不到站着的人）；角色的 `burn: null` 盖掉火球的燃烧；角色 `energy`（0–100）变成命中给的能量；`speed`（走速）变成追踪弹速度。
- 修法：新 `shotOrigin(a, m)` 只给 `{x, y, z, bx}`：from 'stand' = 替身身前 `shotAhead`、离替身脚底 `shotZ`；其他 = 本体胸口（≤ 30 px）。`hittableZ` 把高度夹在能打到站着的人的带子里；`bx`（本体 x）让弹体第一帧从本体扫到出手点，贴身敌人不会被跳过。
- `AV_J3`：from 'stand'、`shotAhead 22 / shotZ 34`、`range 130`（从手上飞 130 px = 从阿布德尔身前算约 165 px）、飞满 `fizzle: 'fire'`（烟 + 火星 + 闪光）、`sfxHit fire_burst / fxHit heavy`、燃烧现在真的生效。火球加了 3 团拖尾。
- 抽帧验证：木桩 40 px 命中（J123 伤害 38）、150 px 命中（18）、215 px 不命中并熄灭（0）。

**2. 其他弹体 / 特效出手点**
- 花京院：J1/J2/终结/连打/U 的宝石都从法皇手上出（以前 z 4 贴地、U 从花京院身上出）；射程 160 / 190 / 180、飞满碎成绿光点；宝石纵深判定 ±8；法皇浮在身后偏上出招（standZ 10、画在本体后面），不再把花京院挡住；U 追踪 1.5 → 3.2 rad/s（命中 12/24 → 18/24），剩下的 420 px 后碎掉。J3 触须网铺三排、网住人时触须缠身。
- 阿布德尔 U：安卡从红色魔术师手上聚起、飞出（以前从身上）。按住 L 身前火墙（`kit.guard.fx`）。地火柱预兆加地面火苗 + 火星、命中往上掀。
- 乔瑟夫：J1/J2/J3/终结以前 `stand: null`，隐者之紫一根藤都不出——现在藤蔓从伸出的手（身前 12、离地 30）长到判定远端、打完就缩；J3 带刺并缠住对手；连打每 6f 上下交替抽 + 波纹沿藤闪；终结波纹爆；U 藤蔓起点改到手上。
- 伊奇：愚者图集没有 punch/punch_heavy，以前全回退成待机——J2/J3/终结改用 claw（举爪 → 砸地）+ 落爪扬沙 / 地面冲击环；连打一下一下抓；L = 愚者 wall 沙盾；U 巨像用 slam。
- 波鲁纳雷夫：J1/J2 判定 8–56 → 8–60（剑尖实际到本体前 65 px）、命中剑尖 glint；J3 前冲残影 + 横向速度线（限在角色附近一条带）；U 卸甲真的换脱甲皮、残影用脱甲突刺帧，放完换回。
- 承太郎：J3/终结替身前冲 24（拳头和判定对齐）、J3 前 7f 先收拳（`standPre`）；拳影墙从替身胸口打出、伸 14 px（以前拳头碰到 70 px 外的人却打不到）；U 时本体指人。
- 通用：命中火花画在目标身体中段并用招式 accent（以前固定脚底上 24 px、accent 没传进去）；格挡/弹反火花画在替身前面；格挡时双份火花去掉；角色自己的 U 本体摆出招姿势（kit.special.pose）。

**3. 连打接不上（抽帧发现）**：J3 把人打退 24 px / 挑飞、倒地无敌，整段连打打空气、终结落空（各角色连打伤害 0–16）。改：进连打先冲到跟前（≤ 32 px，带残影），每一跳继续追身；连打命中清掉 J3 留下的倒地标记（锁受击）；浮空中挨打留在空中托高（以前 z 冻在半空、起身后一直悬着）；hurt 状态 z 自动落地。连打伤害现在：承太郎 90、阿布德尔 86、花京院 62、波鲁纳雷夫 94、乔瑟夫 74、伊奇 84。

**4. Codex 交接**
- (a) 正式入口 `loop_error: reading 'draw'` 根因：验收脚本 `specials.js` 注入的 `W.fight` 没有 `data`，正式入口加载的 `moves_ch02_05.js` 的 `J.drawPixel` 每帧读 `G.world.fight.data.draw`（调用栈：moves_ch02_05.js:65 ← combat.js drawPixel ← world.js ← core.js pixelPass）。改验收脚本（`data: {}`、`on()`），生产代码没问题；`demo.js` 同改。`test_special_visuals.py` 现在存 pageerror 完整调用栈、终端只打摘要。
- (b) `tools/registry/ui_texts.json` `specials` 加 `joseph`「波纹疾走！」、`iggy`「汪！」（照规划 §3.3 切入写法：伊奇不会说话，切入喊“汪！”），`K.joseph/K.iggy.special.title` 改成键名；`locked_build.py ui data check`：错误 0、警告 0、兜底 0（日志 `tools/dev/p5/_out/build_ui_data_check.log`）。
- (c) 阿布德尔放大安卡：飞行、爆炸截图看过（`tools/dev/p5/_out/visuals_20261009-223841/desktop_avdol_active.png`、`desktop_avdol_explosion.png`、mobile 同名）。

## 测试结果（注意时间）

在第 3 项（追身 / 浮空 / 锁受击）和最后几处小改**之前**跑的：
- `test_combat.py` 14/14（`tools/dev/p5/_out/test_combat.json`）
- `test_specials.py` 79/79（`tools/dev/p5/_out/specials_20261009-223719/`）
- `test_special_visuals.py` 12/12、页面错误 0（电脑 + 手机模拟，`tools/dev/p5/_out/visuals_20261009-223841/`；修之前是 0/12：`visuals_20261009-220535_before`）

之后的改动（combat.js 追身 / 浮空 / 锁受击 / standPre / 网 / frontX / 速度线带、fx_mid.js 多排触须、moves.js 伊奇沙盾 dx）**还没重跑回归**，序章路线 `test_jail_shots.py prologue` 也**没跑**。

抽帧证据：`tools/dev/p5/_out/review_before/`（改前）、`review_after2/`（全套）、`review_after3/`（连打 + 三连，追身之后）；工具 `tools/dev/p5/capture_moves.py` + `capture_moves.js`（正式入口、真实按键时钟，联系表叠判定框 / 弹体 / 替身身前点）；精灵帧放大 `tools/dev/p5/_out/sprites/`。

## 半成品 / 没做

- 伊奇闪避“沙翻滚”的旋转（规划：run 帧 0 + 转一圈）没做——刚确认 world.js 画角色支持 `a.rot`，下一步可在 combat 的 dodge 里按 `kit.dodge.spin` 写 rot。
- `docs/交付/收尾_共享改动.md` 没追加：combat.js 的改动会影响所有敌人的弹体（出手点改到胸口 / 替身手上、能打到站着的人：第2章 ST_THROW、第5章 LV_SPORE、第10章 HH_LATE_BULLET、终章刀阵以前永远打不中，现在会打中；追踪弹速度不再被走速盖掉）以及所有命中火花位置，需要写进去通知各路线。
- `规划.md` 阿布德尔 J3 射程（约 165 px）没写进 §3.3。
- `tools/dev/p5/_out/sprite_issues.md` 没写。要写的：① 乔瑟夫 point / whip 手臂没分段、whip 是一根很长的卡其色条（已有重画待办）；② 白金之星 upper 只有 1 帧（代码用 punch 帧 0 垫了蓄力）；③ 愚者 slam 和 claw 帧 0 一模一样，没有真正的砸地帧；④ 伊奇 dodge 只有 1 帧静止图；⑤ 红色魔术师没有专门的重拳帧（J3 / 终结借 cast）。
- 自由走动 U（G.LOOK，story/common.js 归 main）只抽了帧，没细看。

## 下一步（照顺序）

1. `python -B tools\dev\p5\test_combat.py`、`test_specials.py --out tools\dev\p5\_out\specials_<时间>`、`test_special_visuals.py --out tools\dev\p5\_out\visuals_<时间>`，全部要过；不过就看是哪条新改动（追身最可能影响 test_specials 的贴墙 / 射程外项）。
2. `python -B tools\dev\full\test_jail_shots.py prologue --out tools\_playtest\combat_prologue_check`（序1 教学战、序2 法皇宝石——宝石出手点变了要确认还能打中、还能格挡）。
3. 追加 `收尾_共享改动.md`、规划 §3.3 阿布德尔射程、写 `sprite_issues.md`。
4. 再跑一次 `capture_moves.py --out tools\dev\p5\_out\review_after4` 看格挡火花位置、波鲁纳雷夫速度线、伊奇沙盾。

## 改过的文件

`engine/combat.js`、`engine/moves.js`（只动主角段）、`engine/stand.js`、`engine/fx_mid.js`、`tools/registry/ui_texts.json`（只动 specials）、`tools/dev/p5/specials.js`、`demo.js`、`test_special_visuals.py`，新增 `tools/dev/p5/capture_moves.py`、`capture_moves.js`。没有动共享文件（fight / ui / hud / party / core / audio / input / playtest）、美术、原素材、AGENTS.md。
