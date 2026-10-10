# JoJo 片头视频换二乔新脸（op-face 代理，2026-10-10 下午）

用户：“片头动画里乔瑟夫还是旧脸”。游戏目录 `D:\大疆\游戏素材\JoJo\游戏\`（本地仓库，分支 `demo/prologue-ch1`，本代理没提交）。

## 原因

`tools\render_cutscene.py` 直接调原工程的 `common.render_frame`，精灵从原工程注册表 `engine.sprite._REG` 取。游戏里二乔的新脸 / 指人手臂分段（`tools\art\art_joseph.py`）只在 `bake_art` 烘图集时在内存里替换注册表，原工程文件没变，所以 op（s00）一直按旧精灵渲。

用到二乔的地方：s00 点名卡第 2 张 `joseph.point`（第 111–140 帧，4.62–5.85 s）、结尾金字塔合影 `joseph.idle` → `joseph.point`（第 261–335 帧，10.87 s 到结尾，前半段是黑剪影）。coffin（s01）只有 DIO、棺材、蝙蝠，没有任何游戏层重画过的角色。

## 改了什么

| 文件 | 改动 |
|---|---|
| `tools\cutscene_sprites.py`（新） | `apply_game_redraws()`：在内存里照 `bake_art.run` 的顺序做——`assets.load_all()` → 按 `bake_art.ART_MODULES` 顺序 import 全部 art_* 模块（`art_joseph.apply` 要用 `art_later_existing`，后者又要 `art_stands` 等先注册，单独调会 KeyError `starplat.reach`）→ 原名重画：`bake_art.JOTARO_ADULT` 为真才换承太郎（现在 False，承太郎保持原卡通大头，开关直接读 bake_art）→ `art_holly_fix.apply()` → `art_joseph.apply()`。sys.path 只在导入期间临时加 `tools\art`，结束恢复。`check_atlas(names)`：把被换掉的每个精灵每一帧按锚点放进格子，和 `assets\chars_new\<cid>\<cid>.png` 逐像素比。不写任何文件。 |
| `tools\render_cutscene.py` | 渲染前（import 场景模块之前）调上面两步；图集核对不一致 = 图集没重烘，打印哪帧不对、返回 5、不出视频。新参数 `--orig-sprites`（用原精灵，只给对照用）。docstring 写明。镜头、时间、混音代码一行没动。 |
| `assets\video\op.mp4 / op.webm` | 重渲（新脸）。 |
| `assets\video\_旧稿\` | 换之前的四个文件：`op_二乔旧脸_20261010.mp4/.webm`、`coffin_20261010.mp4/.webm`。`make_demo.py` 只拷 `assets\video\` 顶层的 mp4 / webm，不会打进发布包。 |
| `assets\video\coffin.*` | 构建时跟着重渲了一遍（render_cutscene.py 改了 = 缓存失效）：mp4 和原来**逐字节相同**；webm 视频包 / 解码后的声音都相同，只差 WebM 容器里随机的段 ID（第 284 字节），所以把 `_旧稿` 里的原文件拷回去了（新 mtime，video 步缓存仍有效），git 里 coffin 没有改动。 |

没改：`tools\build_assets.py`（共享）、原工程 / 角色图集 / 烘焙脚本 / 剧情分镜 / 音频、AGENTS.md。

## 核对

- **和游戏同一个二乔**：替换后的 `joseph.idle`（2 帧）、`joseph.point` 和游戏图集 `assets\chars_new\joseph\joseph.png` 的格子逐像素相同（render_cutscene 每次渲染都核对，这次 10 个被替换的精灵 0 不一致；替换的是 holly.idle / walk / wave、joseph.idle / walk / run / camera / point / float / dodge，片头只用到 joseph.idle / point）。
- **逐帧原始画面对比**（同一套代码，原精灵 vs 游戏层，640×360 合成帧，脚本 `排查\20261010_片头二乔新脸\脚本\dump_frames.py` + `compare.py`）：s00 共 336 帧，只有第 111–140、261–335 帧变了，变化区域都在二乔身上；音效事件 37 条完全相同。s01 240 帧 0 变化。
- **成片**：新旧 op.mp4 逐帧解码 md5，不同的正好是 [111–140]、[261–335]，其余 231 帧（含承太郎点名卡 84–110 帧）解码后完全相同。声音：mp4 的 AAC 包 md5 相同、解码 md5 相同；webm 的 Opus 解码 md5 相同（“Error parsing Opus packet header” 提示新旧文件都有，原来就有）。时长 mp4 14.000 s、webm 14.009 s、336 帧 1280×720 24 fps，和原来一样。
- **看过的对照图**（都在 `D:\大疆\游戏素材\JoJo\游戏\排查\20261010_片头二乔新脸\`）：
  - `01_点名卡_旧左新右.png`（第 115 / 126 / 136 帧，从新旧 op.mp4 抽的）
  - `02_结尾合影_旧左新右.png`（第 290 / 330 帧；旁边的承太郎仍是原卡通大头）
  - `00_整帧_旧左新右.png`（第 126 / 290 帧整帧）
  - 单帧原图 `before\op_f*.png`（旧片）、`after\op_f*.png`（新片）
- **正式构建**：`python -B tools\dev\full\locked_build.py video data check` → 完成 53.0 s；错误 0，警告 0，兜底 0（日志 `排查\20261010_片头二乔新脸\脚本\build_video.log`）。`data\data_meta.js` / `tools\_meta\video.json` 的 video 段不变：op 14.0 s、coffin 10.0 s。
- **游戏里**（Playwright，`index.html?autotest=1` → 真实键盘选「从序章开始」，脚本 `脚本\pw_video.py`；只在测试页里钩 `document.createElement` 拿到 video 元素，没改游戏文件）：场景 `video` 播的是 `op.webm`，5.21 s 暂停截图是新脸点名卡（`game\op_joseph_card_t5.21.png`），12.07 s 结尾合影（`game\op_finale_t12.07.png`），接着 `coffin.webm` 播放（`game\coffin_mid_t5.01.png`），放完进 `world` 出「序章 东京」篇章卡（`game\after_videos.png`）；控制台 0 错误 0 警告。

## 留下的问题

1. **video 步的缓存不看美术文件**：`build_assets.step_video` 只比 `render_cutscene.py` 和 `源码\{scenes,engine,assets}` 的时间。以后改 `tools\art\art_joseph.py`（或 `cutscene_sprites.py`）再重烘 art / chars，`video` 步会说“已是最新，跳过”，片头又和游戏不一致。要么那时用 `--force`（或手动跑 render_cutscene），要么在 step_video 的 `src_mt` 列表里加 `os.path.join(HERE, "art")` 和 `os.path.join(HERE, "cutscene_sprites.py")`（共享文件，一行，本代理没改）。反过来，图集没重烘就渲视频会被 `check_atlas` 拦住（返回 5），不会悄悄出一个和游戏不一样的二乔。
2. **点名卡的波纹火花位置**：原片 s00 里波纹 / 火花的坐标是写死的（`hx - 26, HY - 47` 一带），本来就在指尖下方约 10 px；游戏的新指人手臂抬高了 2 个精灵像素（片里 4 px），差距变成约 14 px。按“除了二乔其余都不动”没改特效坐标；看对照图读起来仍是“手边冒波纹”，用户要贴指尖得改场景代码（只能在内存里补丁，原工程只读）。
3. 结尾合影前半段（10.87–11.70 s）二乔是 93% 黑的剪影，新旧几乎看不出差别，正常。
4. `assets\video\_旧稿\` 和 `排查\20261010_片头二乔新脸\` 是新目录（未跟踪），提不提交由主代理定。`tools\dev\p5\_out\sprite_issues.md` 第 23 行“片头视频里二乔仍是旧脸”现在已解决，文件不归本代理，没改。
5. 终章 `ending`（s20）以后渲时同样会自动用游戏层形象（s20 里的二乔挥手是场景脚本拿 `joseph.idle` 现做的，apply 在 import 场景之前，所以也会是新脸）。
