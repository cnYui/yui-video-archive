# JoJo 序章 + 第1章场景（scenes-early）：石阶、客舱坐姿、驾驶舱——收尾状态

2026-10-10 上午，并行分工里的 **scenes-early** 代理（序章 + 第1章场景与背景）。用户 2026-10-09 晚的三条反馈：

1. “对话里说是有楼梯，但这里并没有真正做一个下楼梯的场景……动漫里确实是在下楼梯的场景触发的”；医务室的门也没做；牢房里的物品、书和桌子要重画、提高精度。
2. 第1章客舱：“乘客并没有坐在椅子上，半个身子都在地下。”
3. 驾驶舱：“控制台、椅子的大小完全不对。”

中途协调方通知：用户要先把序章 + 第1章做成 demo 发布；之后又要求 20 分钟内收尾、没开始的不开。游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（整个目录被根仓忽略，没有提交）。

## 各项状态（用户问“美术素材是不是都画好了”）

| 项 | 状态 | 证据 |
|---|---|---|
| 序章石阶背景 `school_stairs`（新） | **已画完并接进游戏**（packs.json prologue、bg_jojo EXPORTERS、stages.js `stairs_pro`） | `tools\_playtest\scenes_bg\after_school_stairs.png`；游戏内 `tools\_playtest\scenes_prologue\23_goal_stairs_pro.png`、`24_stairs_descending.png` |
| 楼梯剧情（承太郎走下石阶 → 第 8 级被触须绊倒、滚下去 → 左膝裤子划开 → 花京院递纸巾） | **已接进游戏**，序章路线跑过这一段 0 报错 | `25_pro_stairs_tumble.png`、`26_pro_stairs_landed.png`、`27_pro_knee_slit.png`、`28_pro_stairs_tissue.png`、`29_goal_school_pro.png`（同目录） |
| 医务室门（门框、小窗、把手、保健室牌子 + 进出门演出） | **没做**（背景和演出都没动，门还是被画面右边切掉的那一条） | 现状：`tools\_playtest\scenes_bg\before_school_infirmary.png` |
| 牢房背景重画（物品、书、桌子、灯光、地面） | **没做**（还是原工程 `A.jail_cell` 导出，铁栏 6 张和 fgDepth 144 没动，调查点坐标不用改） | 现状：`tools\_playtest\scenes_bg\before_jail_cell.png` |
| 其他序章背景（空条家三张、卧室、校门、黄昏门口、榻榻米）加细节 | **没做** | 校门现状 `before_school_gate_wide.png` |
| 第1章客舱座椅 + 乘客坐姿 | **已画完并接进游戏** | 背景前后 `scenes_bg\before_plane_cabin_side.png` / `after_plane_cabin_side.png`，拼图 `mock_cabin_seated.png`；游戏内 `tools\_playtest\scenes_shots\cabin_x120.png`、`cabin_x250.png`、`cabin_x420.png`、`cabin_x560.png`、`cabin_slump.png` |
| 第1章驾驶舱 | **已画完并接进游戏** | 背景前后 `scenes_bg\before_cockpit.png` / `after_cockpit.png`，拼图 `mock_cockpit.png`；游戏内 `scenes_shots\cockpit_alarm.png`、`cockpit_alarm_b.png`、`cockpit_yoke_pulled.png` |
| `plane_cabin`（兜底透视客舱）、香港夜街、虎豹别墅加细节 | **没做** | — |

## 改了什么

### 1. 石阶（新背景 + 新地图 + 剧情接线）

- `tools\bg_new\school_stairs.py`（新）：侧视 640 宽，从马路对面看：左边高台（石垣墙面、天端石、排水孔水渍、常春藤），台上是坡顶小路（民宅、板塀 + 树篱、路灯、樱花、石柱路标）；小路尽头 20 级石阶往右下走到人行道（每级宽 11、低 4，踏面 + 侧面 + 落花）；人行道后面砖墙、电线杆、转角镜、自动售货机、院子里的樱花；远景天空 + 远山 + 街景 + 远处的学校（pano k 0.35）；前景是坡顶栏杆 + 顺着石阶的钢管扶手（挡住小腿）；樱花瓣 petals 层。锚点 `stairs {x0 184, run 11, rise 4, n 20, top 80}`、`trip_x`、`bottom`、`kakyoin`、`exit_x`。
- `story\stages.js`：新地图 `stairs_pro`（640 宽，纵深带 y 150–160，墙 x 12–628）。
- `story\prologue.js`：
  - 人站在台阶上的高度用 z：`stairZ(x)` 和背景的 `height()` 同一算法（读 anchors.stairs）；`stairsTick()` 每帧给台阶上的人设 z、关掉引擎影子，`stairShadows`（custom 道具，depth −1）把影子画在脚下那一级台阶上；滚下台阶时用 `mem.stairManual` 自己摆高度。
  - 序-8 改成：`stairs_pro` 坡顶（两个女生跟着走、爱心按台阶高度冒）→ 往右走下石阶 → 走到第 8 级触发 `stairsFall`：再迈一级、脚边绿线闪 4 帧、一路磕下去（空中受击 + 落地趴一下 + 咚 + 扬灰，四下）→ 摔在人行道上 → 台阶上的女生尖叫「JoJo——！」→ 推镜，膝盖上画一道浅色口子（只在这一段，不画血）→ 花京院从学校那边走来、递纸巾、报名字、走掉 → 「……刚才那一下，不是我自己绊倒的。」→ 往右走到头 → `school_pro`（校门，只剩男生 + 三个调查点；铁门调查点挪到真正的铁门 x 282）→ 走到校门口往上走进去（触发区 x 212–258、y ≤ 145）→ 序-9 保健室（原来“走到地图右头 = 进校舍”不合理）。台词照规划 5.1 的序-8b 表；女生 B 第二句改成「他一直站在石阶下面往这边看」（伏笔对得上）；新加一句女生 A 的「JoJo——！」。
  - 加了 4 个截图标记：`pro_stairs_tumble / pro_stairs_landed / pro_knee_slit / pro_stairs_tissue`。
- `tools\dev\full\test_prologue.py`：石阶地图先和两个女生搭话再往右走；校门先和男生搭话再走到门口往上走；校验“女生搭得上话”“目标箭头”改看 `stairs_pro`；走到石阶一半拍 `stairs_descending`。

### 2. 第1章客舱：乘客真的坐在座椅里

- `tools\bg_new\plane_cabin_side.py` 按人（约 46 px）的比例重画：远侧座椅每 32 px 一排（3/4 后视、朝机头），椅脚 y 150、椅背顶 y 131（白头巾套）、小桌板 / 口袋 / 扶手；舷窗一排 y 92–119（透明洞，窗外云自己卷）、行李架 y 50–84、服务面板 y 84–89（阅读灯、面罩舱口）、弧形天花板 + 灯带 + 安全带灯 + 出风口；紧急出口门、洗手间门、驾驶舱门；前景近侧椅背。另导出 `bg/plane_cabin_side/seats`（和背景里的座椅逐像素一致，自检里比过）。
- `story\ch01.js`（`setupPlane`）：乘客 / 格雷·弗莱脚底 y 156 → 150、`z 15`、`shadow false`，全部朝右（原来后四个朝左 = 倒着坐）；地图 props 加 `seatsFront`（`type 'image'`、depth 150.5）= 椅背画在坐着的人前面、过道上的人后面；毛毯 y 141 / depth 150.7 / z 76（落在妈妈肩上、搭在椅背顶）；四个调查点 y 改到过道 158 + `ly`（原来行李架 ly 落在画面外）。
- `tower()`：格雷·弗莱被打倒时先从座位挪到过道、晃两下再倒（规划 1-7）；氧气面罩改成从镜头里那几排座椅头顶的服务面板掉下来。

### 3. 第1章驾驶舱：按人的比例重画

- `tools\bg_new\cockpit.py`（新，`bg_jojo` 的 `EXPORTERS['cockpit']` 改指它，原 `exp_cockpit` 留着不用）：320 单屏、地板 y 172。左：开着的驾驶舱门（看得见客舱暖光）、断路器面板、随机工程师面板、折叠观察员座椅、挂着的外套、灭火瓶；中：两张人那么大的驾驶座（羊皮椅套、头枕、扶手、底座滑轨），远侧副驾驶歪倒在座位上（戴耳机、闭眼，没有血），近侧机长座空着；两根羊角盘操纵杆（近侧那根是 pick 层 `yoke` 0 / 1），中央操纵台四根油门杆；右：遮光板 + 自动驾驶面板、主仪表板（姿态仪等）、方向舵踏板；上：往机头压低的天花板 + 头顶开关面板；挡风玻璃 + 侧窗外是往下冲的海和天（strip 24 帧 @12 fps，2 s 严格闭合）；`alarm`：主警告灯 2 Hz 闪 + 天花板红色警灯光晕。
- `story\ch01.js`（`crash()`）：机长倒在座椅后面地板 (132,174)、帽子 (166,175)；三人站在门口 (52,172)(72,168)(92,175)；乔瑟夫从 (176,172) 冲到 (228,172) 抓住近侧羊角盘；进场 `S.state('alarm', true)`，连按成功后 `S.state('yoke', 1)`、每次重来先放回 0。`stages.js` 的 `cockpit_ch1` 墙改成 x 44–240、默认 state `alarm/yoke`。

## 验收

- 构建：`python -B tools\dev\full\locked_build.py bg data check` 两次，**错误 0、警告 0、兜底 0**（`tools\_playtest\scenes_build1.log`、`scenes_build2.log`）；背景 74 张全部自检通过。共享预览重出过（`python -B tools\bg_jojo.py`），`python -B tools\bg_new\test_contract.py` 通过（19 张）。
- 游戏内截图（`C:\Users\yui\AppData\Local\Temp\claude\...\scratchpad\scenes\shots.py`，真实页面，只读）：客舱 / 驾驶舱 0 报错、`missingImg` 空。
- 序章路线：`python -B tools\dev\full\test_jail_shots.py prologue --out tools\_playtest\scenes_prologue`（结果见下方“序章路线结果”）。
- 第1章整章由主代理跑（`tools\_playtest\main_ch1_r1`、`main_ch1_lose_r1`），test_ch1.py 归主代理。
- **序章路线结果**：从标题打到序章章末，`{"ok": true, "errors": 0, "sec": 336.97}`（`tools\_playtest\scenes_prologue.log`、`scenes_prologue\result.json`）；地图顺序 jail_pro → kujo_pro → **stairs_pro → school_pro**（走进校门）→ infirmary_pro → school_pro（序2）→ kujo_pro → bedroom_pro → gate_pro；石阶段约 25 s。牢房的铁栏前后景 / 走出牢房 / 火柱 / 拳影墙截图也在同目录（02、04、08–14）。没跑 `test_jail_explore.py`（牢房这次没改）。

## 没做 / 下一步

1. 医务室：门（门框、小窗、把手、「保健室」牌子，门在画面里完整露出来）+ 承太郎进门 / 花京院出现在门口的开门演出；书架、文件、桌上的台灯和纸、药柜、床、布帘提高精度。保健室背景是 `tools\bg_new\school_infirmary.py`，锚点 door (300,156) 和剧情坐标要一起挪。
2. 牢房重画（游戏层新模块 `tools\bg_new\jail_cell.py`，保持原布局：调查点 `police_talk / pipe_look / tally / magazines / bunk / bulb / poster / bars / window / radio / cans` 和 `standTouch` 的伸手坐标都按现在的位置；铁栏 6 张 pick + fgDepth 144 不动）：杂志 / 书堆、小桌子和桌上的东西、床铺毯子枕头、收音机、海报（角上的拳印）、罐子、墙面裂缝水渍、地面、灯光。
3. 其他序章背景加细节；第1章 plane_cabin / 香港夜街 / 虎豹别墅。
4. 驾驶舱的“拉杆”差别不大（近侧操纵杆被乔瑟夫挡住大半），以后可以把 pull 画得更明显。
5. 飞机上灰塔扑向乘客时，俯冲终点在乘客脚底 y 150（引擎按目标 y 算），最后几帧会从椅背后面穿过去，打中时火花在乘客头上，问题不大，没改引擎。
