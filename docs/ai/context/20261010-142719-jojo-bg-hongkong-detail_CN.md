# JoJo 第1章：香港夜街 / 虎豹别墅加细节（bg-hk 代理）

2026-10-10 下午，并行分工里的 **bg-hk** 代理。用户原话：“当前的剧情场景背景，需要你再着重优化一下精度……你要仔细地把背景图片重新画一下”；今天要求做完剩下的“第1章的香港街和虎豹别墅加细节”。游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（自己的本地仓库，分支 `demo/prologue-ch1`，**没提交**，由主代理提交）。

## 各背景状态

| 背景 key | 状态 | 前 / 后对比 | 游戏内截图 |
|---|---|---|---|
| `hongkong_night`（香港夜街，960 宽） | **已画完并接进游戏**（`bg_jojo.py` EXPORTERS 改指 `tools\bg_new\hongkong_night.py`） | `tools\bg_new\_preview\bg_hk\hongkong_night_before_after.png`（5 个镜头位置、贴了剧情道具）；单张 `hongkong_night_before_cam*.png` / `hongkong_night_after_cam*.png`；3 倍放大 `_zoom_cam0/230/520.png` | `tools\_playtest\bg_hk\street_cam40_start.png`、`street_cam110_window.png`、`street_cam250_pawn.png`、`street_cam400_dinner.png`、`street_cam520_newsstand.png`、`street_cam640_kite.png` |
| `hk_garden_night`（虎豹别墅，320） | **已画完并接进游戏**（EXPORTERS 改指 `tools\bg_new\hk_garden_night.py`） | `tools\bg_new\_preview\bg_hk\hk_garden_night_before_after.png` | `tools\_playtest\bg_hk\garden_duel_positions.png`、`garden_walk_band_edges.png`、`garden_statue_visible_nopatch.png` |

两个原导出函数 `exp_hongkong_night` / `exp_hk_garden_night` 留在 `bg_jojo.py` 里不用。剧情文件（`story\stages.js`、`story\ch01.js`）一个字没动。

## 画了什么

### 香港夜街 `tools\bg_new\hongkong_night.py`

1987 年九龙夜市街（廟街一带）。契约照旧：960 宽、ground 154、纵深带 150–176、近景 640 循环；3 层 period 640 的 wrap（远 k .25 vx −.5 / 中 k .6 / 近 k 1）+ period 40 路面黄线 + neon + reflect（`test_contract.py` 的条件都满足）。

- 天空：渐变、星星、弯月。新加 `clouds` 层：一架启德降落的客机慢慢飞过楼顶。
- 远景：九龙群山山脊 + 高楼窗灯、天线红灯、楼顶灯箱。中景：唐楼窗灯、窗帘、冷气机、晾衫竹、天台水箱 / 天线 / 广告架。
- 近景（640 循环）：唐楼铁窗花、冷气机滴水印、晾衫竹和衣服、雨水管、天台铁皮屋；地铺分段和原片一样（橱窗那家还是 x 199–236，`anchors.shopwindow` 仍 [205,112,230,146]），每家店里有货：烧腊、飞发铺、凉茶铜壶、洋服橱窗（假人 + 玻璃斜反光）、上楼的红灯门口、药房货架、当铺遮羞板、电视墙、厨房瓷砖、面档、拉闸的铁闸；横巷留着能看见后面的楼，巷口灯笼、电线；人行道砖、垃圾桶、消防栓。
- 新加 `pano` 层（整条 960 不循环）：所有招牌的暗底和挂架、当铺“蝠鼠吊金钱”押字牌、大牌档（帆布棚、四只灯泡、绿铁皮档口、炉火、挂着的叉烧、红胶凳、发泡胶箱）、**菜单板**（叉燒飯 / 雲吞麵 / 炒蜆，真字）、**报摊**（「書報」牌、两排杂志、一叠叠报纸）、看相摊（八卦桌布、「睇相」布幡、灯笼）、三根路灯（都立在巷口，不穿招牌）、「廟街」路牌、地图右头的「碼頭→」指路牌。
- 霓虹：16 块真字招牌（simsun 12 / 16 px 点阵字，`fontmode '1'` 不糊）：酒家 飛髮 涼茶 洋服 夜總會 藥房 **當舖** 旅館 大牌檔 粥麵 茶餐廳 燒臘 理髮 藥材 **麻雀** 舞廳，6 块会闪（JS 的 flick，灭的时候露出 pano 里的暗底）；按世界坐标放，不再每 640 重复一遍。
- 会动的：大牌档炉上的蒸汽（strip 24 帧 @8 fps，k 1）、理发店旋转灯柱（6 帧 @6 fps，k 1），都严格闭合。
- 倒影：源图改成 960 整条（近景 + 街面 + 亮霓虹，period 960 = 世界坐标），湿路面上看得见招牌的颜色。

剧情位置对照（模块自检里逐条断言，0 条不满足）：霓虹招牌 (400,60) = 「當舖」竖招牌 x 390–412、y 40–79；橱窗倒影 (230,120) = 洋服橱窗；菜单板 (520,120) = 板 x 500–540、y 104–146；报摊电视：道具 tv (660,152) 立在报摊（x 624–702）前面；招牌上的风筝：道具 kite (860,150) z 80 画在 y 62–70，正好挂在「麻雀」招牌上沿（y 68）；两张桌（476–572）在帆布棚下；老板 590 / 626 在档口前；看相佬 760 在看相摊前。游戏里拍过，全部对上。

### 虎豹别墅 `tools\bg_new\hk_garden_night.py`

契约照旧：320、ground 150、纵深带 140–176；static + 飞鸟 clouds（同原片），新加一条 strip（栏杆上三只红灯笼的光，6 帧 @6 fps）。

- 夜空 + 满月月晕 + 薄云；山后面一线港岛楼灯；两层树冠。
- 白塔（cx 250、底 104、七层）：拱窗、瓦垄、翘角、绿边、金顶，几扇窗亮着；地上有白塔的月影。
- 彩绘假山伸到 x 196：赭石 / 橙褐 / 灰蓝石块 + 石纹；两边小龛里是彩塑小人，**中间 x 160 的大龛供神像（光环、供桌、烛光）= 调查点「彩绘假山洞」(160,110)**。
- 虎像：橙黄 + 黑纹 + 白肚 + 张嘴露牙 + 翘尾，比原片细；**整只在剧情的 tigerPatch（x 15–70、y 83–117）里面**（自检：有虎 / 没虎两张图在 y<117 的差异落在补丁外的像素 = 0），底座石 y 116–132 露着，红色魔术师石像（mr_statue (44,133) z 17）照旧立在上面。
- **金狮一对挪到 x 80 / 100（调查点「金狮」(90,128)，原来那里什么都没有）**，左边那只镀金掉了一块块、露出灰石头（对应台词“镀金掉了一半”）；石阶两边原来的金狮改成一对石狮（212 / 288）。`anchors.lions` 改成 [[80,118],[100,118]]，另加 `stone_lions`（剧情不读这些锚点）。
- 红栏杆加柱子和金柱头、青花瓷缸两只、棕榈树干分节。

## 验收

- 模块自检（`python -B tools\bg_new\bg_hk_preview.py`）：香港 12 项、虎豹别墅 7 项全过（导出层 vs 整幅直接拼 0 px、帧条闭合 0、剧情位置 0 条不满足、虎像出补丁 0 px）。
- 正式构建：`python -B tools\dev\full\locked_build.py bg data check` → **错误 0、警告 0、兜底 0**，背景 74 张自检全部通过（`游戏\tools\_playtest\bghk_build1.log`）。
- 共享预览重出（`python -B tools\bg_jojo.py`，日志 `tools\_playtest\bg_hk\bg_jojo_preview.log`）+ `python -B tools\bg_new\test_contract.py` 通过（19 张）。
- 游戏内（Playwright、`index.html?autotest=1`，替换 `G.CHAPTERS[1].run` 只为了摆人拍图；脚本在会话 scratchpad `bghk_shots.py`，只读）：两张图 `missingImg` 空、`bg_type_missing` 0、页面错误 0（`tools\_playtest\bg_hk\result.json`）。

## 改了哪些共享文件

- `tools\bg_jojo.py`：只动 EXPORTERS 里 `hongkong_night` / `hk_garden_night` 两行 + 两行注释（已记进 `docs\交付\收尾_共享改动.md`）。
- 没动 `_pv.py`、`test_contract.py`、`packs.json`、剧情文件。

## 新文件

- `tools\bg_new\hongkong_night.py`、`tools\bg_new\hk_garden_night.py`（游戏层模块，`export(ex, BJ)`）
- `tools\bg_new\bg_hk_preview.py`（前 / 后对比预览工具）
- 预览输出 `tools\bg_new\_preview\bg_hk\`（含 `layers_before\ layers_after\ layers_dbg\` 中间图层、`_font_test.png` 字体测试），游戏内截图 `tools\_playtest\bg_hk\`

## 没做 / 留意

1. 虎豹别墅的彩绘假山还是几何石块 + 石纹，彩塑场景只有小龛里几个小人；要更像真的虎豹别墅（大面积彩绘浮雕、十八层地狱那种场景）还能再画。
2. 雕成石像以后（`garden.carved`）的样子没在游戏里拍到（要打到战斗阶段 2），靠自检保证虎像全在补丁里；`garden_statue_visible_nopatch.png` 是没盖补丁直接显示石像的样子，只看位置。
3. 菜单板在大排档那段对话时会被坐着的四个人挡住大半（板在 y 104–146，人头在 y 110 上下），调查点照样能用。
4. 霓虹 flick 的招牌，倒影里一直是亮的（倒影源图是静态的，和原片一样的限制）。
5. 金狮从石阶旁挪到 x 80–100 是为了对上剧情调查点 (90,128)；如果剧情那边本意是石阶旁的狮子，要改的是 `ch01.js` 的调查点坐标（我没动）。
