# JoJo 序章背景加细节（bg-pro）

2026-10-10 下午，并行分工里的 **bg-pro** 代理。用户要求：“当前的剧情场景背景，需要你再着重优化一下精度……你要仔细地把背景图片重新画一下”，今天收尾项“其他序章背景加细节”。游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（自己的本地仓库，分支 `demo/prologue-ch1`；我没提交，由主代理提交）。

做法：每个 key 一个游戏层模块 `tools\bg_new\<模块>.py`（`export(ex, BJ)`，同 jail_cell / cockpit 的约定），把原工程画法搬过来、在对应的图层顺序里加东西（细节画在树 / 人物之前，夜景的月亮星星灯笼光在调色之后画）。**尺寸、ground、纵深带、锚点、图层名 / 类型 / 位置 / 视差、strip 帧数和 fps、花瓣和乌鸦参数全部和旧导出一致**（预览脚本逐项比对，打印“契约：一致”），剧情文件一个没动，不需要改几何。

## 各背景状态

| key | 状态 | 模块 | 改前 / 改后图（`游戏\tools\bg_new\_preview\bg_pro\`） |
|---|---|---|---|
| `kujo_house_day` | **已完成并接入**（EXPORTERS 已改） | `kujo_house.py` | `kujo_house_day_before_1x.png` / `kujo_house_day_after_1x.png`；三行对比 `kujo_house_day.png` |
| `kujo_house_night` | **已完成并接入** | `kujo_house.py` | `kujo_house_night_before_1x.png` / `_after_1x.png`，`kujo_house_night.png` |
| `kujo_house_morning` | **已完成并接入** | `kujo_house.py` | `kujo_house_morning_before_1x.png` / `_after_1x.png`，`kujo_house_morning.png` |
| `kujo_bedroom_dusk` | **已完成并接入** | `kujo_bedroom_dusk.py` | `kujo_bedroom_dusk_before_1x.png` / `_after_1x.png`，`kujo_bedroom_dusk.png` |
| `school_gate`（480 宽） | **已完成并接入** | `school_gate.py` | `school_gate_before_1x.png` / `_after_1x.png`，三个镜头位置 `school_gate.png` |
| `dusk_gate`（420 宽） | **已完成并接入** | `dusk_gate.py` | `dusk_gate_before_1x.png` / `_after_1x.png`，三个镜头位置 `dusk_gate.png` |
| `tatami_top` | **已完成并接入**（EXPORTERS 那行本来就指 `tatami_top.py`，模块重画；旧版移到 `tools\bg_new\_旧稿\tatami_top_20261010前.py`） | `tatami_top.py` | `tatami_top_before_1x.png` / `_after_1x.png`，`tatami_top.png` |

总对比 `sheet.png`（每个 key 三行：改前 / 改后 / 改后 + 纵深带青线 + 锚点红标）。

## 画了什么

- **空条家和室（三种光同一底图）**：竿缘天花板木纹；栏间格子压暗加高光；长押钉隐；壁龛砂墙、挂轴改成清楚的富士山（雪顶、红日、云带、山脚松林、落款红印、轴头、挂钩吊绳；对应调查点乔瑟夫“富士山”）；床板木纹、小香炉、花瓶薄板、床柱节疤；隔扇黑漆边、金云描边、淡墨远山 + 松枝、铜圈拉手；庭院两朵小云、远树两层、瓦当、粉墙柱子水渍、池塘石岸 + 三条锦鲤 + 睡莲叶（调查点“锦鲤”）、耙纹、苔斑、踏脚石、脱鞋石上的木屐、松树支柱、风铃后面一只壁虎（阿布德尔台词）、廊下板缝 + 蚊香猪、拉门樱花补丁；榻榻米织纹和镶边花纹；矮桌木纹、侧把茶壶、两杯绿茶、一碟仙贝、桌下阴影；坐垫线结和穗子。夜景另加月亮、星星（只落在天空像素上）、石灯笼点亮。
- **卧室（黄昏）**：天花板木纹、竖格栏间、土墙砂粒、左上小相框（荷莉和小时候的承太郎）；障子窗外框 + 窗台、纸面右上更亮、松枝影子带松针；金屏风金箔方格、黑漆框、铰链、两枝梅花 + 花苞；架子上小相框和首饰盒；托盘加水杯；榻榻米织纹；门口一双拖鞋；行灯腿和提手（灯纸、光晕仍是原 strip）。被褥位置周围的席面没加东西。
- **校门**：远层校舍屋顶栏杆、楼板线、窗中挺、几扇拉窗帘、竖幅、钟楼刻度 + 校徽、玄关雨棚 + 玻璃门里的鞋柜、旗杆、体育馆拱顶、远楼的窗；近层围墙分块 / 水渍 / 压顶高光、门柱花岗岩斑点 + 门灯、校名牌边框、铁门轮子和地轨、围墙边两辆自行车、告示板、井盖、排水篦子、树下落花更密。调查点 gate_plaque 200 / sakura 150 / gate 282 和进门触发区 x 212–258 对应的东西都在原位。
- **黄昏门口**：天顶几颗星；远处东京零星亮灯、航空灯、塔身横档和红灯；中景屋顶天线 / 烟囱 / 亮窗；第一根电线杆挂路灯（暖色光晕）、第二根变压器；院墙灰泥、瓦当、门柱「空条」门牌（逆光压暗）、信箱、门楣下门灯、门里踏脚石、排水沟盖板、路边线、井盖、松叶轮廓光。四人剪影走的那段路面只加了很淡的东西。
- **榻榻米俯视**：按原接缝位置重新排席：中间横放、左右竖放，织纹方向跟着席子走；长边深绿镶边带小花纹、短边压缝；草屑旧色、左上窗光；四档像素暗角照旧（中心脸和肉芽不受影响）。

## 验收

- 模块自检（每个都在 build 里跑）：导出层按 §3.6 公式重建 vs 直接绘制 0 px（空条家 3 个时刻 × 3 种光、卧室 3 个时刻、校门 5 个镜头位置、黄昏门口 4 个镜头位置、榻榻米），底图不透明；strip 闭合全部 0，接缝数和旧导出一样（风铃 12 / 落叶 4 / 晨光 10984 / 行灯 2584 / 路面反光 14）。
- 正式构建：`python -B tools\dev\full\locked_build.py bg data check` → **错误 0，警告 0，兜底 0**，背景 74 张自检全部通过（日志 `游戏\tools\_playtest\bgpro_build1.log`）。
- 游戏里的背景总览（`tools\dev\full\bg_sheet.py`，读构建好的数据）：`游戏\tools\bg_new\_preview\bg_pro\game_sheet\sheet.png`，7 张都画得出来。
- 真实页面（Playwright，`index.html?autotest=1`，`G.S.party` + `G.S.setStage` 摆队伍截图，脚本在会话 scratchpad `bgpro_shots.py`，只读）：空条家三种光、卧室、校门两个镜头、黄昏门口两个镜头共 8 张，人物站位正常、没有黑块，`missingImg` 空、页面 0 报错。图在 `游戏\tools\bg_new\_preview\bg_pro\ingame\`（拼图 `ingame_sheet.png`，结果 `result.json`）。
- 没跑序章整章路线（背景几何没变，剧情文件没动）；拔肉芽插入画面里的 `tatami_top` 没在剧情里截图，只在 bg_sheet 里看过。

## 文件

- 新：`游戏\tools\bg_new\kujo_house.py`、`kujo_bedroom_dusk.py`、`school_gate.py`、`dusk_gate.py`、`bgpro_preview.py`（改前 / 改后对比预览，只写 `_preview\bg_pro\`）。
- 改：`游戏\tools\bg_new\tatami_top.py`（重画；旧版 `_旧稿\tatami_top_20261010前.py`）。
- 共享：`游戏\tools\bg_jojo.py` EXPORTERS 6 行 + 注释（旧导出函数都留着）；已记进 `游戏\docs\交付\收尾_共享改动.md` 末条。没动 `_pv.py`、`test_contract.py`、`packs.json`、剧情和引擎。

## 遗留

1. `_pv.py` 的锚点预览名单 `NEW` 没加这几个 key（共享文件，不影响游戏）；共享预览 `tools\bg_new\_preview\_stages.json` 没重出（重出要跑全量 `bg_jojo.py`，会覆盖别人的预览）。
2. 卧室剧情里承太郎进场站在 (240,158)，正好踩在托盘上（原来就这样，不是这次改的）；要挪得改 `prologue.js`，归主代理。
3. 黄昏门口地图 `gate_pro` 的 `x1` 是 460，背景只有 420 宽（原来就这样；镜头 camX 最大 100 时右边还是满的）。
4. 细节都是“画在原布局上”，没改透视和房间结构；用户要更大的改动（比如空条家换角度、校门加纵深）得另做。
