# JoJo 战斗与美术收尾（combat-art 代理，2026-10-10 上午）

游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（整个目录被根仓忽略，没有提交）。接 combat 代理 `20261009-225125-jojo-hero-combat-review_CN.md` 和
美术代理 `20261009-225123-jojo-npc-heads-joseph-art_CN.md` 留下的事。中途协调员两次调整：先做序章 + 第1章 demo 看得到的；最后要求 15 分钟内收尾
（打斗测试用户自己做，不再跑整章路线）。

## 美术素材状态（逐项）

| 项 | 状态 | 证据（都在 `tools\_playtest\`） |
|---|---|---|
| 白金之星上勾拳 | **已画完并进游戏**：`starplat.upper` 1 → 3 帧（下蹲蓄力 / 上冲 / 拳过头顶收势），`SP_J3` 去掉 `standPre` 改 `standSeq` | `ca_evidence\01_上勾拳_重拳_新帧预览.png`、`02_上勾拳_重拳_游戏内J3.png`、`ca_heroes_capture\jotaro_J123.png` |
| 红色魔术师重拳 | **已画完并进游戏**：新 `magred.heavy` 2 帧（蓄火 / 直拳出火球）；`amap` `punch_heavy → heavy`；`AV_J3` 火球从拳头出（`shotAhead` 27、`range` 125，射程仍约 165 px）、`AV_FIN` 用重拳；地火柱 / 大招 / 剧情 Special 写明 `cast`（不变） | 同上 01 / 02、`ca_heroes_capture\avdol_J123.png` |
| 六人连打收招姿势 | **已完成并验证**：`combat.startRush` 播 `kit.rush.body`，乔瑟夫 `cmd_hold`（`vine_hold` 拽藤循环）；其余五人不写、照旧（承太郎 point、阿布德尔 / 花京院 cast、波鲁纳雷夫 fight、伊奇 bite 帧 0）——六人都抽帧看过 | `ca_evidence\03_六人连打姿势.png`、`04_乔瑟夫连打拽藤.png`、`ca_heroes_capture\*_rush.png` |
| 乔瑟夫攻击帧（正式入口抽帧） | **已核对**：J1 / J2 `vine_atk` 0→1→2、J3 `vine_heavy` 0→3、连打 `vine_hold`、格挡、U，0 错 0 缺图 | `ca_joseph_capture\joseph_J1 / J123 / rush / guard / U.png` |
| 乔瑟夫三张场景特写换新脸 | **已画完并进游戏**：`s05_joseph_kneel`、`s05_joseph_reach`（序章荷莉病床前）、`s20_joseph_wave`（终章，目前剧情没用到） | `ca_evidence\05_乔瑟夫场景图_旧脸左_新脸右.png`、`06_乔瑟夫场景图_游戏数据里.png` |
| 承太郎头像 / 对话头 / HUD 脸 | **已核对、一致**：承太郎图集所有原动作行、4 张头像文件、构建出的 normal / angry 头都和只读原图逐像素相同（原卡通大头，`JOTARO_ADULT = False` 没动）；HUD 和对话框用同一组头像 | `ca_evidence\07_承太郎乔瑟夫_精灵脸对头像.png`、`08_序1开战_HUD头像.png` |
| 愚者沙爪 / 拍地（slam） | **已画完并进游戏**：照原工程 `_fool_frame` 重画 `claw` 2 帧、`slam` 2 帧（人立举沙拳 → 砸地扬沙）；J3 / 连打终结改用 slam；大招巨像先人立升起再砸 | `ca_evidence\09_愚者沙爪砸地_新帧预览.png`、`ca_iggy_capture\iggy_J123.png`、`iggy_U.png` |
| 伊奇闪避 | **已画完并进游戏**：`iggy.dodge` 4 帧翻滚（缩成一团、像素格转 90° 逆时针一圈） | `ca_evidence\10_伊奇翻滚_新帧预览.png`、`ca_iggy_capture\iggy_dodge.png` |
| 替身随本体缩放（第5章脑内战） | **已完成并验证**：stand.js 站位 / 浮起 / 召唤上升 / 绘制 / 触须连线 / 藤蔓、combat.js 替身身前点 / 出手点都乘本体 `scale`；0.5 时偏移正好减半、替身画成一半大 | `ca_evidence\11_替身随本体缩放_左1右0.5.png`（`ca_stand_scale\`） |

**没画 / 没做**：无（清单内）。清单外看到没改的见 `tools\dev\p5\_out\sprite_issues.md` 末尾（通用走路腿、几个对话头像的嘴、片头视频 op.mp4 里二乔仍是旧脸）。

## 战斗代码

- `engine/combat.js`：①连打本体姿势 `kit.rush.body`；②擦身子弹时间色调：以前 `'ts_' + cid` 不被 post 认识（只记 `post_unknown ts_<cid>`），改按替身取 `ts_purple / ts_red / ts_green / ts_blue / ts_yellow`，淡入 6f，子弹时间结束或战斗结束淡出（新 `bulletTick`，在 cine 判断前）——六人各测一次：0 个 post_unknown、色调对、0.6 s 后 slow 回 1 且滤镜收掉；③替身相关偏移乘本体 scale。
- `engine/stand.js`：替身随本体缩放（scale = 1 逐像素不变）。
- `engine/fx.js`：`PALETTES.ts_red`、`TS_TINT.red`；`engine/post.js`（共享）`KNOWN` / case 加 `ts_red`。
- `engine/moves.js`（主角段 + 伊奇段）：见上表；`K.joseph.rush.body = 'cmd_hold'`。
- 文档：`docs\交付\收尾_共享改动.md` 补记 combat 代理昨晚的弹体出手点改动（第2章 ST_THROW、第5章 LV_SPORE、第10章 HH_LATE_BULLET、终章 TW_KNIFE 刀阵以前打不中、现在会掉血，给路线负责人），以及本次全部共享改动；`规划.md` §3.3 阿布德尔 J3 写明射程约 165 px（原写 200），上勾拳 / 爆炎的动作列同步。
- `tools\dev\p5\_out\sprite_issues.md`：审查里五条精灵问题 + 处理结果 + 证据路径。

## 美术管线

- `tools/art/art_stands.py`：上勾拳 3 帧、`magred.heavy`、愚者 `_fool_pose`（claw / slam）；`art_heroes.py`：`iggy.dodge`；`art_later_existing.py`：不再生成 fool.claw / fool.slam / iggy.dodge；`amap.py`：magred punch_heavy → heavy；`test_contract.py` 跟着改。
- `tools/art/art_joseph.py` 新 `scene_overrides()`：调用原场景脚本自己的生成函数（`s05_holly._mk_kneel / _mk_reach`、`s20_farewell._mk_joseph_wave`），**先用原 idle 复现、和 `角色图集\场景专用\` 原 PNG 逐像素比对（一致才继续）**，再按新脸 idle 重做 → `assets\props_new\scene\`；`bake_art.run` 在 `art_joseph.apply()` 之后调，缓存检查也算上这三张。
- `tools/build_assets.py`（共享，props 步 3 行）：拷场景专用图时 `assets\props_new\scene\<同名文件>` 存在就用它。原图目录只读、没动。

## 构建与核对

- 两次构建都是 `python -B tools\dev\full\locked_build.py art chars props data check`：错误 0、警告 0、兜底 0；art 回读 1139 → 1143 帧 0 错，引擎比对 1992 → 2000 次 0 不一致（日志 `tools\_playtest\ca_build_1.log`、`ca_build_2.log`）；`tools\art\test_contract.py` 通过。
- 重烘前快照 `tools\_playtest\ca_art_snap_20261010-092136`（开工）、`ca_art_snap_20261010-095631`（第二次前）；`diff_atlases.py` 和按 pivot 对齐逐动作比：全程只有 starplat（upper 行）、magred（新 heavy 行）、fool（claw / slam 行）、iggy（dodge 行）变了，其余 87 个图集逐像素不变（承太郎原大头、五人落水半头、荷莉 / 狱警 / NPC 头的修正、二乔新帧都在）；props 只有那三张二乔场景图变了（`ca_diff_after_build1.json`、`ca_diff_after_build2.json`、`ca_diff_session_total.json`）。

## 测试（最后一轮 = 全部改动之后）

- `test_combat.py` 14/14（`tools\dev\p5\_out\ca_after2\`）
- `test_specials.py` 79/79（`ca_after2\specials\`）
- `test_special_visuals.py` 12/12，页面错误 0（`ca_after2\visuals\`）
- 开工基线同样 14/14、79/79、12/12（`ca_baseline\`）；第一次构建后也全过（`ca_after1\`）。
- `test_jail_shots.py prologue --out tools\_playtest\ca_prologue`：ok、0 错误、297.7 s（第一次构建之后跑的，愚者 / 伊奇那次构建之后按协调员要求没再跑整章路线；序章不出伊奇）。
- 抽帧：`capture_moves.py` 六人 J123 + 连打伤害和昨晚一致（连打 90 / 86 / 62 / 94 / 74 / 84），乔瑟夫 / 伊奇全场景 0 错 0 缺图。

## 留给后面

- 片头视频 `assets\video\op.mp4`（原工程 s00 按原精灵渲染）里的乔瑟夫还是旧脸，要换得改渲片头的管线，没做。
- 沙之巨像（3 倍大）人立那 0.2 s 的大沙拳在画面上沿外，砸地那一下完整可见；要整只看见得缩小倍数（规划写 scale 3，没改）。
- 弹体出手点修好以后各章敌人的远程招式真的会掉血（见共享记录），难度要路线负责人 / 用户试玩后再调。
- `AGENTS.md` 没改（本代理不改）；主代理更新 JoJo 条目时可引用本记录。
