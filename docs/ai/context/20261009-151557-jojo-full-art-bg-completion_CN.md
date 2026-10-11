# JoJo 全章角色、道具与背景补齐

## 范围与协作边界

依据 `游戏素材/JoJo/游戏/规划.md` 与 `docs/技术约定.md` v2.1，继续 Claude 中断后的资源工作。原 JoJo 源码、图集、分镜、烘焙脚本、音频和银魂工程均保持只读；Python 一律 `-B`，导入原工程前禁止写字节码。

本代理只维护 `tools/art/`、`tools/bg_new/`、`tools/bg_jojo.py`，不修改剧情、运行引擎和 registry；正式 `assets/` 由主代理统一构建。本记录是全章资源阶段的新记录，原 M1 交付与历史上下文不覆写。

## 结果

- 390 个新增精灵动作，烘入 83 个受影响图集，其中 51 个新角色。
- 71 个新增道具，与原 35 个合计 106 个；新增 Hol Horse 掉落牛仔帽 `hat`。
- 91 个角色的 666 条 AMAP 逻辑动作映射已从真实动画元数据读取并检查，均指向 `animations` 真名。
- 73 个背景，包括后续 55 个 key；逐层重建、循环、透明底等 1,252 项检查全部通过。

后续角色包含船长、安妮、恶魔使者/娃娃、黄色节制、女帝、ZZ、审判使者、阿努比斯宿主、肯尼G、尼禄萨库、幼年承太郎/波鲁纳雷夫、泥偶、亚空瘴气后段动作、奥西里斯神、荷鲁斯、旅途 NPC 等；既有角色增加攻击、受击、倒地、走路及五位同伴水面姿势。

道具补齐货轮眼睛、寄生物、镜片、焦油、梦境玩具、神灯、义手、12 种女教皇伪装、上下巨牙、列车、磁力杂物、六个可开合藏点、阿图姆灵魂人偶、终战道路标志/轿车/皮卡等。

## 发现并修复的资源问题

1. 后续美术模块的 `ONESHOT` / `STATIC_STATES` 使用裸动作名，原烘焙器只认 `cid.action`，使两帧攻击误烘为循环。`bake_art.py` 新增 `playback_names()`，只把本模块 `NEW` 中的动作扩成完整名，不串改其他角色。验证 `osiris.attack`、`horus.attack`、`devo.slash`、`death13.swing` 为 `oneshot`，`jotaro.float` 保持 `loop`，M1 `starplat.punch` 保持 `oneshot`。
2. 水面姿势曾沿用站立图的锚点，实际预览可见锚点离图像过远。改成新泳姿自身底部中心，再烘焙并重新看图。
3. 阿努比斯附身波鲁纳雷夫的 `slash` 被去重成为 alias，AMAP 改指真动作 `attack`；不接受 AMAP 指向 alias。
4. 豪宅楼梯恢复原 15 级坐标 `(34+i*12+6,166-(i+1)*6)`，前景栏杆直接只读调用原绘制；实际看过带锚点十字的合成图。
5. 卢克索住宅移除背景中不可开合的固定家具，六藏点由独立两状态道具表现。看过关闭/打开两版组合，内部确实露出，鱼缸有鱼和水草。
6. 列车近景按需求为 110 像素/秒，远景按视差比率 8.8/38.5；高速公路道路为 360。运行引擎的 `stage.state.speed` 作为倍率，资源没有另加状态接口。
7. 船甲板的水波遮罩避开甲板/舱体，卧室沿用原宅晨光底图，梦境摩天轮以八帧闭环，底层透明洞和地牢墙砖缝均已修复。

## 验证证据

独立输出在 `tools/art/_later_verified/`，不与主代理正式构建竞争。

```powershell
python -B -c "import sys; sys.dont_write_bytecode=True; sys.path.insert(0,'tools/art'); import bake_art; r=bake_art.run(out_dir='tools/art/_later_verified',force=True,previews=True); print('FINAL',len(r['chars']),len(r['props']))"
python -B tools/bg_jojo.py
python -B tools/art/audit_later_assets.py
```

最终美术报告：1,034 帧回读 0 错，1,838 次引擎绘制对照 0 差，AMAP 0 错。最终背景报告：73 key、1,252 checks、NG 0。重要预览均实际读取图片：Osiris/Horus、SPW/水果商、五人 float、薄被/摇篮/冰墙/双牙、六家具开合、带十字楼梯、机场。

`audit_later_assets.py` 生成 `tools/art/_preview/later_asset_inventory.json` 与 `后续资源真实清单.md`，包含真动作、帧数、播放方式、来源和全部道具。字面量扫描只证明静态角色/道具引用，不声称涵盖动态拼接、变量、scene 名称或所有动作；后者由主代理联调验收。

## 已交给剧情代理的真名问题

- 第七章 `magician` → `magred`，`lamp` → `genie_lamp`，`prosthetic_hand` → `joseph_hand`；扫描时仍有四处字面量错名，由主代理改剧情。
- 阿图姆人偶 `atum_doll_a` = 波鲁纳雷夫，`atum_doll_b` = 花京院，`atum_doll_c` = 乔瑟夫；后段剧情代理已收到花京院应选 b 的提示。
- `npc_cat.eat` 两帧、`npc_dealer.idle` 两帧均真实存在。
- `wheel.car`、`justice.skull`、`devo_doll.idle` 均真实存在。女帝 l0–l2 有专门真动作，l3 的 AMAP 映射到 `idle`/`bite`。

## 下一步

主代理收到资源可正式构建通知，继续 registry、字体、剧情和引擎联调；资源独立验证通过不代表全游戏已通关。AGENTS.md 的现行规则与记录链接由主代理统一维护。
