# 时间轴、混音、合成

配音切好之后（`配音\segments\`、`制作\voice\durations.json`、`alignment.json` 都在）按顺序跑。所有命令的 `<期目录>` 是 `SERIES\第NN期_<题目>`，脚本在 `SKILL\scripts\`。

```bash
python scripts/build_timeline.py <期目录>
python scripts/mix_audio.py <期目录>
python <期目录>/制作/engine/sync_assets.py
python scripts/assemble.py <期目录>          # 默认 4 路并行（2026-09-28 用户定：所有渲染统一 4 路并行）
```

## 1. 时间轴 `build_timeline.py`

- 输入：`episode.json`、`台本\script_data.py`、`制作\voice\durations.json`、`alignment.json`。
- 输出：`制作\timeline.json`（**不手改**）、`制作\chapters_bilibili.txt`。
- 每段时长用实测配音长度，段间隔 0.25 秒；`gap` 用台本里写的秒数。
- 字幕断行（`split_lines`）：
  - 先在句读处断（，。？！：；、，连同后面跟着的 ”）》 等一起留在这一行），再把短句拼满一行；
  - 单行显示宽度 ≤20（汉字和全角标点算 1，ASCII 算 0.55；只有一个不能拆的英文词 / 网址本身就超宽时例外）；
  - 英文词、数字、路径不拆，本期 `terms` 和引擎内置的橙色术语（API Key……）也不拆到两行（拆开就不标橙了）；
  - 避头尾：”’）》」』】〕〉、，。！？；：…% 等不放在行首（跟在上一行末尾），“‘（《「『【〔〈 等不放在行尾（挪到下一行开头）；
  - 一句超过 20 宽就按最好的断点拆成几行，每段各起一行：句读后 > 右引号 / 右括号后、中英文交界 > 「的 / 了……」后、英文词之间 > 汉字中间，尽量不在引号括号里面断，行宽尽量平均；
  - 碎行（不到 5 宽）并进邻行，并不进（会超 20）就把这两行重新平分；行尾的 ，、；： 去掉；
  - 引擎会把「≥18 个字符、以英文 / 数字结尾」的一行和「以英文 / 数字开头」的下一行粘成一行显示（给第 1 期旧时间轴用的，粘的时候不加空格），断行会避开这种断点（必要时把行尾的 ，留着）；
  - 最后按 `alignment.json` 的实际时间重新计时。改了规则只影响重跑 build_timeline 之后的时间轴（段的起止时间、口型不变，build_timeline 会说“保留原来的 mouth”）。
- 章节（进度条和 B 站分段章节）用整片时间：片头 3.8 秒 + 正片 + 片尾 4.8 秒。
- 画面说明里的 `【动作：…】` 解析成 `actions`；`episode` 字段嵌入 timeline（背景路径转成相对引擎目录的路径）。
- 画面尺寸：episode.json 的 `canvas`（新期 `[2340, 1080]`）检查后抄进 `timeline.episode.canvas`，打印 `canvas=2340x1080`；没写就是 1920×1080，时间轴和以前一模一样。它只影响出图，不影响口型和混音（改了 canvas 重跑 build_timeline 会说“保留原来的 mouth”）。

## 2. 混音 `mix_audio.py`

- 人声：每段峰值归一到 -3 dB，按时间轴位置摆放。
- BGM（`素材\音频\bgm.wav`，整片只用这一首）：正片 -17 dB，说话时再压 7 dB；片头片尾只有音乐，抬高 16 dB，进出正片各 1.2 秒渐变。
- 音效：场景切换处轻“嗒”（-20 dB），画面说明含“打勾”的停顿处放提示音（-18 dB）。
- 最后两遍线性 loudnorm 到 -16 LUFS、真峰值 -1.5 dB。
- 同时按人声音量算每帧口型（0 闭 / 1 半张 / 2 张），写回 `timeline.json` 的 `mouth`。所以**每次重跑 build_timeline.py 之后都要重跑 mix_audio.py**，否则口型数据丢失。
- 输出 `制作\build\mix.wav`。

## 3. 画面资源 `sync_assets.py`

在 `制作\engine\` 生成 `assets.js`：本期讲解员（`episode.json` 的 `presenter.frames`）的角色帧和 anims.json、背景图、字体的相对路径清单。素材有变动（加了背景图、新动作帧、讲解员的帧画完了）就重跑。缺帧时它会写明是哪个讲解员缺哪个 key，并以退出码 1 停下（assemble 也就停下）。

- 讲解员的帧还没画完、只出草稿：`python <期目录>/制作/engine/sync_assets.py --series D:/大疆/AI科普 --frames <已有的帧目录，相对 素材/> --allow-missing`，例如鲸鱼娘用 `--frames 角色/大肥鱼像素素材包/素材`（只有待机、口型、表情，缺帧的动作退回待机）。`--frames` 只管这一次，不改 episode.json，也不用做 episode.json 副本。然后 `assemble.py --no-sync`（assemble 自己跑的 sync_assets 不带 `--frames`，会因为缺帧停下）。
- 帧目录整个不存在、里面没有 anims.json、或者没有待机帧 `idle_m0..2`：直接报错退出，`--allow-missing` 也不放行（没有帧就只剩一个占位小人，不能当草稿交出去）；报错里写出同一个素材包里可以临时用的帧目录和完整命令。
- 临时文件别放会话临时目录：那里的路径超过 260 个字符，Windows 上 Python 打不开（`--episode` 读不到副本就是这个原因）。

## 4. 合成 `assemble.py`

- 全程按时间轴的 canvas 出片（第 2 期起 2340×1080；第 1 期 1920×1080），编码参数不变。
- 片头片尾从 `SERIES\片头片尾\` 的 HTML 以 30 fps 重新渲染，**按 canvas 原生渲染**（data 里写 `"canvas": [2340, 1080]`，`render.py` 按它开视口）：名字（悠一）/ 小票居中，底色、纹理、四角裁切标、片头收尾的整屏墨黑铺满全宽，不是把 1920 的画面补边或拉伸。片尾清单用 `episode.json` 的 `outro_items` / `outro_closing`，为空时脚本报错——**去问用户**，不要自己填。
- 正片：先自动跑一遍 `engine\sync_assets.py --series`（`--no-sync` 跳过），再 `render_parallel.py` 4 路并行（2026-09-28 用户定：所有渲染统一 4 路并行；JPEG q95 截图 → x264 CRF 16；视口 = canvas）。某一路浏览器卡住（截图 / 打开页面 30 s 超时）会自动重启并从卡住的那一帧接着渲染。各路相隔 0.7 s 启动（`--stagger`）；引擎预加载角色帧时偶发的加载失败由引擎自己重试，救回来的只打印一行 `image loads failed and were retried by the engine … all recovered`，不算报错。
- 三段统一编码后拼接，混入 `mix.wav`（AAC 192k），`+faststart`。
- 输出（期目录下）：`第NN期_<题目>_成片.mp4`、`_字幕.srt`（画面已烧录，这份给 B 站外挂字幕）、`_章节.txt`（B 站分段章节）。
- 脚本自带的检查（不通过就停下，不会留下一个短了的成片）：episode.json 的 canvas 和时间轴里的一致（不一致 = 改了 canvas 没重跑 build_timeline）；片头、正片、片尾和成片的尺寸都等于 canvas；正片帧数 = round(main_duration × 30)；拼接后和成片时长与 `total_duration` 相差 ≤0.1 s；页面报错（JS 异常、console.error、字体加载失败、引擎重试后仍没加载成功的文件——报错里写出文件地址）→ 停下并提示先修 scenes.js。`--skip-main` 时如果时间轴在上次渲染后变了（帧数或尺寸对不上），也会被拦下。

## 5. 交付前检查

- `ffprobe`：尺寸 = canvas（第 2 期起 2340×1080）、30 fps、H.264 + AAC，时长 = `timeline.json` 的 `total_duration`（±0.1 s）。
- 抽帧（片头、每章开头和中段、章节切换处、片尾）拼成联系表用 Read 看：
  - 画面是 canvas 的宽度（2340）：内容舞台居中，徽标、讲解员贴画布左边，目录贴画布右边，进度条全宽，背景铺满，两边没有空白或黑边；片头片尾也是全宽、构图居中；
  - 左上只有「原LAI如此 #NN」；右上目录状态对（补充章节期间不高亮，讲完打勾）；
  - 字幕按画布整体居中、不压角色、不压进度条；
  - 背景按章节切换，够淡，内容清楚；
  - 角色动作出现在该出现的地方，没有镜像、没有跳帧；
  - 进度条章节名和时间正确。
- 音画同步：抽 3 处配音开口时刻，对照口型和字幕出现时间。
- 响度：整片约 -16 LUFS，片头片尾音乐听得见但不吵。
- 成片交给用户时说明：时长、结构、需要用户确认的事实和发音。

## 局部返工（只重跑需要的部分）

| 改了什么 | 重跑 |
|---|---|
| 某句配音 | 重生成那一批 → `select_takes.py` → `segment_audio.py` → `build_timeline.py` → `mix_audio.py` → `assemble.py` |
| 字幕文字（配音不变） | 改 `script_data.py` 字幕原文 → `build_script.py` → `build_timeline.py` → `mix_audio.py` → `assemble.py` |
| 画面（scenes.js、背景、动作） | `build_timeline.py`（动作、背景在 timeline 里时）→ `mix_audio.py` → `sync_assets.py` → `assemble.py` |
| 讲解员的帧还没画完，先出草稿 | `sync_assets.py --frames <已有的帧目录> --allow-missing` → `assemble.py --no-sync`（帧画完后去掉这两个参数重跑 `assemble.py`） |
| 技能的引擎模板更新了（新规则、修复） | `new_episode.py --update-engine <期目录>`（scenes.js 不动）→ `build_timeline.py` → `mix_audio.py` → `sync_assets.py` → `check_layout.py` → `assemble.py` |
| 画面尺寸（episode.json 的 `canvas`，例如老目录改成 2340×1080） | 引擎是 2026-09-27 以前的就先 `new_episode.py --update-engine` → `build_timeline.py`（口型、混音不变）→ `sync_assets.py` → `check_layout.py` → `render.py --stills` 看版面 → `assemble.py`（不能 `--skip-main`，片头片尾也按新宽度重渲） |
| 卡片版的旧期换成白板版（第 3 期 2026-09-28 试过；已发布的期先在副本里做，见 lessons.md「文件操作」） | `new_episode.py --update-engine <期目录>` → episode.json 加 `"style": "board"`、`"layout": "center"`（配音照旧，不加 voice_source）→ `build_timeline.py`（口型、混音不变，它会提示 mix.wav 仍然有效）→ 按 visuals.md「白板版」**重写 scenes.js**（只参考卡片版的内容）→ `sync_assets.py`（生成 handdata.js）→ `check_layout.py` → 抽帧看章末、疑问 → 目录 → `assemble.py` → `make_cover.py`（白板期自动出白板版封面；旧 cover.json 的 subHTML 会当 sub 用，t1 / t2 照旧） |
| BGM 音量 | 改 `mix_audio.py` 参数 → `mix_audio.py` → `assemble.py --skip-main`（画面不重渲） |
| 片尾清单 | 改 `episode.json` 的 `outro_items` → `assemble.py --skip-main` |
