---
name: claude-code-cover
description: 给「Claude Code相关」合集（Claude Code 产品信息 / 新功能 / 更新速递）的 B 站视频做封面：必须用 Claude 的官方像素宇航员（要大，动作可以自己画，但不能用自己造的别的角色顶替）和 Claude 品牌色（橙 #D97757、米白 #FAF9F5、淡黄 #F5DB9A、深色 #141413），背景也用品牌色（深色 / 米白 / 品牌橙 / 淡黄四种方案），16:9 和 4:3 各出一张，封面只放几个短而大的字、不和视频标题重复；一份候选清单一条命令出 3 个候选 + 验收 + 总览图，用户选定后一条命令定稿。用户提到 Claude Code 相关视频的封面、“封面太丑”、“这不是 claude 的形象”、Claude 像素形象 / 宇航员 / 吉祥物、品牌色封面、给封面换动作 / 换背景色时用这个技能。
---

# Claude Code相关 · 封面

用户 2026-10-02 的要求（原话）：“封面要求必须使用claude的像素形象，claude的品牌色”；“当前claude这个像素形象，你可以自己画不同的动作，自由发挥即可”；“背景也是，使用品牌色即可，橙色，米白，黄色等等”；另外“封面中出现的内容和标题不要重复”“claude的形象大一点”。第 1 期（《Claude mod(模组)发布》）封面 = 深色太空 + 放大的官方宇航员；第 3 期（《You should know 插件》）三个候选（night / orange / ivory），用户选了 night + `float2`。

## 硬性要求（每张封面都要满足，`check_cover.py` 会查前 5 条）

1. **必须有 Claude 的官方像素宇航员，而且大**：16:9 里身体宽 ≥ 画面宽的 17%（默认约 20–22.5%）。形象不重新上色（橙 #D97757、深色眼睛、浅灰头盔），**不用别的角色顶替**：用户 2026-10-03 退回过一版——“封面中你这个claude形象太丑了，换一个，而且你这个都不是claude的形象”（那版是我另写脚本画的原创机器人）。形象只来自 `mascot.py`（官方 40×33 像素表 + 官方动画帧）；动作可以在官方身体上改手臂 / 腿 / 眼睛、加道具，但**身体、头盔、眼睛的样子不能变**。出封面只用 `make_candidates.py` / `make_cover.py`，不要另写脚本去画角色；`check_cover.py` 第 5 条拿官方像素表重新渲染来逐像素对，非官方形象过不了。
2. **只用品牌色**：深色 #141413、米白 #FAF9F5、品牌橙 #D97757（深橙 #BF684C / #C15F3C）、淡黄 #F5DB9A，加宇航员自带的头盔灰 #D1CFC4。不要别的色相，不要渐变、暖色光晕。色值取自 claude.dev 官方页面的 CSS（深色主题 `--bg #141413`、正文 #FAF9F5、`--accent #d97757`、`--accent-deep #c15f3c`）。
3. **背景用品牌色**：night（深色 + 星空）/ ivory（米白）/ orange（品牌橙）/ yellow（淡黄）四选一；字色、头盔环颜色、描边随方案自动换（见 `references/design.md`）。
4. **封面字和视频标题不写同一句话**。用户 2026-10-03：「封面文字中最下面一行的小字可以删除，因为用户根本看不见……封面中的文字要简略要大，标题则需要详细，这个规则对我目前做的所有的视频skill都要生效」：封面上只放两行**简短的大字**（关键词 / 钩子，每行 ≤ 12 个汉字宽，第 2 行用强调色），**不放最下面那行小字**（副标题、说明、清单、来源署名之类，缩到信息流里根本看不见）；**标题写详细**，把封面放不下的信息（时间、数量、对象、结论……）写进标题，不和封面是同一句。例：封面「大模型 / 谁夯谁拉？」→ 标题「2026下半年大模型谁夯谁拉？18个模型锐评」；第 3 期封面「别漏看重点 / Claude 新插件」→ 标题「一个视频了解 Claude Code 新插件 You should know：…」。系列名、期号这类合集标识照旧。开工前先和用户定好各写什么，并先出 3 个候选（不同背景方案 × 不同动作 × 不同钩子字）让用户选。
5. 两个比例都出，4:3 单独排版；B 站首页会把 16:9 裁成 16:10（左右各切约 96 px），字和宇航员收在 96–1824 之间，底部约 12% 留给时长角标。
6. 官方插画（星空背景、宇航员）要在简介里注明：“封面里的像素宇航员 / 背景取自 claude.dev 官方页面，版权归 Anthropic”。
7. 出图后**一定要打开图看一眼**：先看 `候选总览.png` 的整体，再看用户可能选的那组 16:9 / 4:3 原图（字有没有被挤、星点有没有读成标点、道具有没有出画、宇航员有没有被裁）。验收脚本代替不了眼睛。

## 流程（第 3 期实测）

1. 和用户（或按本期内容）定封面字（钩子）和标题，标题另写；挑 3 个差别大的组合：背景 night / orange / ivory（或 yellow）各一个，动作按内容选（下面）。
2. 在 `制作\04_封面\` 写 `封面候选.json`（格式在 `make_candidates.py` 开头；写上 `title` 就会查封面字有没有和标题重复），然后：

```bash
cd "D:\大疆\Claude Code相关\skill\claude-code-cover\scripts"
python make_candidates.py "<…>\制作\04_封面\封面候选.json" --out "<…>\制作\04_封面"     # 3 个候选 × 2 个比例 + 逐张验收 + 候选总览.png
python make_candidates.py … --only B                                                    # 只重出 B（改了字 / 动作后）
python make_candidates.py --out "<…>\制作\04_封面" --select A [--force]                  # 用户选了 A → 封面_选定_16x9.png / 封面_选定_4x3.png
```

3. 打开 `候选总览.png`（和要选的原图）看过，再把三个候选发给用户选（发 `候选总览.png` 一张就够，用户要看大图再发单张）。**用户选定前不要往下做投稿相关的事。**
4. 选定后 `--select`；上传 B 站见下面“上传”。

只改一张时直接用 `make_cover.py`：

```bash
python make_cover.py --line1 "别漏看重点" --line2 "Claude 新插件" --out "<…>\制作\04_封面" --name A --scheme night --pose float2
python check_cover.py "<…>\封面_A_16x9.png" "<…>\封面_A_4x3.png"      # 可一次给多张；同目录有同名 .meta.json
python mascot.py list                                  # 动作名 + 适合的内容
python mascot.py gallery --scheme night --out gallery.png   # 所有动作的总览图
```

## 参数和选动作

- `--scheme night|ivory|orange|yellow`（背景方案，默认 night）；`--pose`：官方帧 `float`（默认）`float2` `float3` `stand`，自画 `wave`（打招呼 / 新功能上线）`cheer`（重大发布）`gear`（设置 / 模组）`terminal`（Claude Code 命令行 / 教程）`megaphone`（公告）`flag`（新版本 / 里程碑）`shield`（安全 / 权限）`plug`（插件 / 技能 / 模组）`gift`（礼包 / 福利）`point`（指向左边的字）`think`（原理解释）`bolt`（提速 / 新模型）；`--flip` 镜像（道具朝左）；`--eyes happy|wink`。
- 选动作看内容：新功能 → wave / gift；设置、模组 → gear / plug；命令行教程 → terminal；安全 → shield；新版本 → flag；性能 → bolt；解释原理 → think；没有合适的道具 → 官方帧 float / float2 / float3 / stand（第 3 期三个候选就是 float2 / float3 / stand，最“像 Claude”）。
- **字号和宇航员大小自动适配**：从大到小逐档试字号，字框外扩后不碰宇航员的任何一格、不超出右边界；字和宇航员（连道具）抢横向空间、字号低于 `fs_fit` 时，**自动把宇航员每格缩小 1 px 再试，但不会缩到保底以下**（16:9 每格 16 = 身体宽 20%，4:3 每格 12 = 20%；`--min-cell-16x9 / --min-cell-4x3` 可改，`--no-fit` 关掉自动缩小）。字号还低（< 130 会报警）就换动作、`--flip` 或缩短封面字，别再靠缩小宇航员——身体宽低于 17% 验收判不合格。
- 其他参数：`--cell-16x9 18 --cell-4x3 14`（每格像素上限）、`--mpos-16x9 0.75,0.81`（宇航员外框中心 x、底边 y 比例，所有动作站在同一条地平线上）、`--bg scene|pixel`（night 默认官方星空截图，其他方案是程序画的像素星点）、`--seed`（换一批星点；小星光已避开 16:10 会被裁掉的两侧，不用再为过安全区验收换 seed）、`--bg-shift dx,dy`（换一块官方星空）。
- 想画新动作：在 `scripts/mascot.py` 的 `POSES` 里加一个函数——在官方的 40×33 格子上改手臂 / 腿 / 眼睛，再用 `PROPS` 风格的字符画贴道具（`0` 深色 `1` 深橙 `2` 品牌橙 `3` 头盔环 `4` 小星光 `5` 高光 `I` 米白 `Y` 淡黄 `P/S` 随方案换色的主 / 副色 `Z` 装饰小星光），`python mascot.py gallery` 看效果。格子坐标和身体各部分的位置写在 `mascot.py` 开头的说明里。

## 文件

- `scripts/make_candidates.py`（按候选清单批量出图 + 验收 + 总览图 + 选定）、`make_cover.py`（出单个封面）、`check_cover.py`（验收，可多张）、`mascot.py`（像素宇航员：官方帧 + 自画动作 + 配色方案 + 渲染）、`fetch_sprite.py`（从 claude.dev 前端代码取官方像素表）、`capture_scene.py` + `build_assets.py`（截官方星空、擦掉宇航员得到 `scene_clean.png`、记下品牌色）。
- `assets/`：`sprite_official.dat`（官方 40×33 像素表 + 130 帧动画，Anthropic 的美术数据）、`scene_clean.png`、`scene_src/s6_*.png`、`brand.json`、`sprite.json`、`astronaut_f*.png`（截图抠的旧版宇航员，现在只剩参考用）、`样图_16x9.png`、`动作总览_*.png`。**png 和 .dat 不进 git**（第三方素材，本期的封面 png 也加了 .gitignore 规则）；丢了按顺序跑 `fetch_sprite.py`、`capture_scene.py`、`build_assets.py`。
- `references/design.md`：版式数字、配色表、被否掉的做法。依赖：Playwright、共用字体 `D:\大疆\AI科普\素材\字体\fonts.css`（Noto Sans SC 900）。

## 上传到 B 站（2026-10-03 第 3 期定下的做法）

封面弹窗（点表单里的“添加封面”）里 **“双比例同步改动”保持不勾**（勾上会把一张图同时用到两个位）：点“个人空间封面（16:9）”，`find` 出文件输入框，`file_upload` 传 `封面_选定_16x9.png` → 点“首页推荐封面（4:3）”，用同一个文件框传 `封面_选定_4x3.png` → 截图确认两个位各是对应排版（4:3 位两边留灰 = 装的是 4:3 图）→ “完成”（`div.button.submit`，用 JS 点文字是“完成”的可见元素）。只换了一个位点“完成”会弹“检测到个人空间封面（16:9）未修改…是否同步”：点“不同步，手动编辑”，别点“确认同步”。投稿后用接口核对 `cover`（16:9）和 `cover43`（4:3）是**两张不同的图**，且和本地一致（下载后算平均像素差，JPEG 压缩后 < 1）。步骤全文见 `Claude Code相关/skill/claude-code-episode/references/publish.md`，细节和别的合集通用的坑见 `AI科普/skill/yuanlai-ruci-episode/references/bilibili.md` §5 和 AGENTS.md。「立即投稿」不点，等用户说；用户会在页面里手改标题，他开始打字时我只读不写。

## 视频本身：片头片尾必加

本技能只做封面。这个合集的视频按项目规则**必须加统一的片头片尾**（用户 2026-10-03：“所有生成的视频都需要使用片头和片尾”）：模板 `D:\大疆\AI科普\片头片尾\`（片头 4.8 s、片尾 9.0 s，`pack_info.py` 读时长），加法 `python D:\大疆\AI科普\skill\yuanlai-ruci-episode\scripts\add_to_video.py <正片.mp4> --outro-data <片尾.json> -o <成片.mp4>`，说明见 `D:\大疆\AI科普\skill\yuanlai-ruci-episode\references\add-intro-outro.md`。整条视频的制作流程用 `claude-code-episode` 技能（它会调用本技能出封面）。
