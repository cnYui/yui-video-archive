# JoJo 美术：配角头身对位、二乔手臂 / 攻击帧 / 脸（状态记录，用户额度用完时停下）

游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（整个目录被根仓忽略，没有提交）。两次正式构建都通过，停下时**没有半装的资源**：
最后一次 `python -B tools\dev\full\locked_build.py art chars data check` → 错误 0、警告 0、兜底 0；art 回读 1135 帧 0 错、引擎比对 1984 次 0 不一致；`node --check engine/moves.js` 通过。

## 已完成

### 1. 头身对位审计（用户：“这些配角 NPC 还有没有这些情况？”）
- 新脚本 `tools\art\audit_heads.py`：读合并图集（`assets\chars` + `tools\_meta\chars.json`），逐帧量头部（最上 22%）左右中点 − 躯干中心（42–62% 高度里含枢轴那一段的中位数）、帧间跳动、漂浮部件（主块以外 ≥4 px 的连通块）；出 6 倍联系表、总览表、`--compare` 前后对比。91 个图集全量跑过，|头偏| ≥ 2 的 31 个逐个看过联系表，其余看总览抽查。
- 真缺陷 & 已修：
  - **借 h_frame2 的 6 个女性 NPC**（校医、女生 a / b（截图里棕发那个是 b）、空姐、卖粥阿婆、抬头的妇人）：头落在身体后面 4.5–6 px（同荷莉的原因）。`art_npc.h_frame2` 加 `head_dx`（头、帽子、发髻、马尾一起挪；默认 0 仍和原工程逐字相同，`art_holly_fix` 的断言照旧成立），NPC 统一 `NPC_HEAD_DX = 2`（同荷莉）。妇人的对话头像是从 idle 裁的，裁框跟着挪，说话帧的嘴原来画在衣领上，改到真嘴（`art_dialogue_heads.py`）。
  - **矮个子躯干塌掉**（三个小孩 npc_kid / polnareff_kid / jotaro_kid、安、ZZ）：`art_later_people.body()` 的 hip = h−14 落在肩线上，躯干被头盖住、手臂往上折成 V。改成躯干至少 6 行、手垂到大腿（只影响 h ≤ 37 的矮个子；连带 jotaro.kid / polnareff.kid 两行）。
  - 其余被标的是假阳性：武器 / 举手进了头部区（阿莱西斧头、审判、玛丽亚插头、银色战车剑）、非人形（伊奇、宠物店、车、鱼）、原设计（阿布德尔 / 承太郎 / 波鲁纳雷夫的发型在后、格雷·弗莱驼背、僵尸前倾），不改。
- 构建 1 后逐像素比快照：只有这 13 个图集变（承太郎、波鲁纳雷夫只变 kid 一行），荷莉、狱警、五人落水半头、承太郎原大头都不变。
- 前后对比：`tools\_playtest\art_heads_fix1\前后对比_女性NPC头身.png`、`前后对比_矮个子躯干.png`（及每个角色的 `compare_<cid>.png`）。

### 2. 二乔（手臂分段 + 普通攻击帧 + 脸）
- 新模块 `tools\art\art_joseph.py`（照原工程部件和 class G，`jo_frame2` = `SJ.jo_frame` 的副本，大头比例 / 帽子 / 灰白胡子 / 卡其衬衫 / 深裤 / 棕手套都不变；cell 82×57、pivot [30,54] 不变）：
  - 新动作：`vine_atk`（蓄力 → 甩出 → 命中 → 收势，4 帧 15 fps）、`vine_heavy`（举臂 → 猛抽（手臂缠藤）→ 定住 → 收势，4 帧 10 fps）、`vine_hold`（伸臂拽藤 2 帧循环）；`whip`、`guard` 重画（原来是通用拉线手臂、躯干右半边被挖掉；`art_later_existing` 不再生成这两个）。攻击用远侧棕手套那只手：肩缝描线、暗袖、卷起的袖口、3 px 前臂、大一圈的手套 / 拳。
  - 脸照对话框头像（用户后加的要求）：游戏里眼睛原来一行（像眯眼），改成“黑眼线 + 两行白蓝眼睛”（`JO_FACE2` / `JO_FACE2_SMUG` / 攻击咬牙 `JO_FACE2_GRIT`）；惊吓、受击、躺倒三张脸本来就对应头像，不改。
  - `apply()` 在 D12 审计之后（同 art_holly_fix）用新脸重画原图集 idle / walk / run / camera / point（point 顺带修指人手臂：手臂抬到口袋上、暗袖、细前臂），重算 float（水线同原来，只露帽子和眼睛）/ dodge；先断言副本按原参数原脸重画和原工程逐字一致。`bake_art.py` 已接（ART_MODULES 加 art_joseph、run() 调 apply）。
- `tools\art\amap.py`：二乔 `cmd → vine_atk`（J1 / J2 / 收尾 / 连打）、`cmd2 → vine_heavy`、`cmd_hold → vine_hold`、`special` 照规划仍是 `point`。
- `engine\moves.js` 只改一个字段：`JS_J3 body 'cmd' → 'cmd2'`（`stand / vineLen / vineHold` 是战斗负责人 22:45 加的，没动），已记 `docs\交付\收尾_共享改动.md`。
- 构建 2 后比快照：只有 joseph 图集变；其中 shock / hurt / lie / portrait / portrait_shock 逐像素不变。预览（草稿区）：`C:\Users\yui\AppData\Local\Temp\claude\D----\dd592801-8a86-495b-83a0-71d863169d18\scratchpad\art\jo_new_a.png`、`jo_new_b.png`、`jo_atk_zoom_a.png / _b.png`。

### 3. 脸 vs 对话框头像（协调员转达的用户新要求）
- 新脚本 `tools\art\audit_faces.py`：66 个有头像的角色，游戏头部 ×8 | 头像 ×6 | 头像缩到精灵头宽 ×8；结果 `tools\_playtest\art_faces_before\faces_01..09.png`。
- 结论：**明显对不上的只有二乔**（已改，见上）。很多配角的头像本来就是从精灵裁 / 同一个画头函数缩放的，天然一致；五主角、荷莉、DIO、狱警、校医、女生等结构对应。瓦尼拉·艾斯的头像是 DIO 暴怒脸改色（表情不同，五官位置不算拼错），没改。

## 没做完 / 下一步（按顺序）
1. **还没做游戏内抽帧验收**：二乔攻击帧没在正式入口截图。下一步：`python -B tools\dev\p5\capture_moves.py --out tools\_playtest\joseph_capture_<时间> --only joseph --scen J1,J123,rush,guard`（战斗负责人的脚本，只读用），看甩藤四段、J3 猛抽、连打、格挡和 stand.js 藤蔓（起点已改到 pivot+12、−30）是否对得上。
2. **二乔场景专用图还是旧脸**：`角色图集\场景专用\s05_joseph_kneel.png`、`s05_joseph_reach.png`（序章荷莉病床）、`s20_joseph_wave.png`（终章）。原图集只读、build_assets 的 props 步没有覆盖机制；做法：在 `tools\art\` 写一个按像素把旧眼睛换成新眼睛的补丁脚本 → 输出到 `assets\props_new\scene\`，再请 build_assets 负责人在 `step_props` 加“props_new\scene\<file> 存在就用它”（约 3 行），构建要带 `props`。
3. 给战斗负责人的建议（已写进共享记录，没改）：`combat.startRush` 写死 `play(a,'cmd')`，二乔连打停在“收势 / 拽藤”帧；改成 `play(a, r.body || 'cmd')` + `K.joseph.rush.body = 'cmd_hold'` 就会用 `vine_hold`。
4. `tools\dev\p5\_out\sprite_issues.md` 停下时还不存在（任务 4 没开始）；之后再看。
5. 承太郎复核（任务 3）：两次构建里 jotaro 图集只有 kid 一行变（矮个子修复带的），idle / float 等逐像素不变、仍是原大头；头像 / HUD 脸没单独截图核对。
6. 其他发现没修：art_later_existing 通用“走路”重画的腿和 idle 不一致（玛丽亚光腿变黑粗腿、J·凯尔 / 阿莱西没鞋）；几个对话头像（香港路人 A、乘客 a）的说话嘴画在下巴上；女帝 idle 第 1 帧左角离开身体 1 px。
7. 本记录之后还要补：`AGENTS.md` 的 JoJo 条目由主代理更新（本代理不改 AGENTS.md）。

## 快照与证据
- 重烘前快照：`tools\_playtest\art_snap_20261009-220516`（开工基线）、`art_snap_20261009-221953`（构建 1 前）、`art_snap_20261009-225006`（构建 2 前）；对比结果 `diff_after_build1.json`、`diff_after_build2.json`（`tools\art\diff_atlases.py <快照> --expect ...` 生成）。
- 构建日志：`tools\_playtest\art_build_1.log`、`art_build_2.log`。
- 审计：`tools\_playtest\art_heads_before\`（改前全量）、`art_heads_after1\report.md`（改后）、`art_faces_before\`。
