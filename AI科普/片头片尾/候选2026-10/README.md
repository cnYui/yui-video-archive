# 片头 / 片尾候选（2026-10，三版）

用户 2026-10-02 的要求：“当前所有分集使用的片头和片尾都需要你重新设计一下，给我三种版本，我是一个科技账号，类似于参考视频的风格，最后要露出我的名称：AI鼓励师：悠一 然后结束片头。片尾的话也按照相同的风格设计，片尾会放一些使用到的参考文献和致谢，需要你提前留出文字编排的空间。”

参考视频：`SaveTwitter.Net_drY7Reou5Q9beWNz_(1080p).mp4`（Fable 5.5 的“Animator”片头，15 s）——米色纸纹背景、一颗带表情的红色小球在手绘小山上弹跳、发射成彗星、落下来用轨迹写出手写体标题、彩色纸屑、“— ANIMATOR —”字距拉开的小字。三版都沿用这套语言：**纸纹 + 藏青墨色 + 珊瑚橙 + 柔和的糖果色**，手写笔画逐笔写出（用白板引擎的笔画数据），每版一个不同的“小主角”。

**状态：三版都做完了，等用户挑一版。** 现行模板（`../intro`、`../outro`，终端小票风）没有动；挑定之后再换，换的时候要连流水线一起改（见最后一节）。

| 版本 | 小主角 | 片头（5.5 s） | 片尾（9.0 s） |
|---|---|---|---|
| **A 鼓励球** `A_鼓励球/` | 珊瑚色小球（有眼睛） | 小球掉进纸面弹三下、翻过小山从崖边飞出去，变成彗星落回纸上，**自己当笔尖一笔一笔写出“悠一”**，画下划线、落座、撒纸屑，打出“— AI鼓励师 —”，眨眼 | 小球跳进来写两个栏目标题，条目逐行铺开；跳到底部写感谢语、用珊瑚色写签名“悠一”，落座眨眼 |
| **B 纸飞机** `B_纸飞机/` | 纸飞机（航空信） | 飞机拖着虚线航迹翻一个跟头，掠过名字——飞过哪个字哪个字就**像盖章一样印出来**（马善政毛笔楷书），飞机从右边出画、从左边回来着陆，滑行痕迹就是下划线；最后盖一枚珊瑚色橡皮章“AI鼓励师” | 飞机丢下一封封好的信，信落到桌上弹一下，横向、纵向两次展开成一整页信纸（有折痕），信纸上写出两栏，末尾署名“—— 悠一”并盖方形朱印；飞机停在信纸右上角 |
| **C 铅笔与灯泡** `C_铅笔灯泡/` | 铅笔 + 会笑的灯泡 | 铅笔勾出一只灯泡，点一下，灯泡亮起来长出笑脸；两个**剪纸风大字**（藏青 + 珊瑚色衬层）从上面砸下来扬起纸屑，铅笔画下划线、用铅笔手写“AI鼓励师”后退场；灯泡悬在名字上方浮动、眨眼 | 一页横格笔记本纸（横线、红色页边线、装订孔）：铅笔写标题，条目按格子用手写体写出（Patrick Hand + 马善政），底部写感谢语、珊瑚色签名并划一道；灯泡亮在右上角 |

三版共同点：1920×1080 舞台居中、支持 2340×1080（`window.__CANVAS__` 或 `data.canvas`，和现行模板一样）；片头最后 0.3 s 淡到 `endColor`（默认白 `#FFFFFF`，正片现在都是白底；`"none"` 关掉）；片尾最后一帧是定格。字体全部 OFL（见 `fonts/`）。

## 看效果

- `out/A_片头_2340.mp4`、`out/A_片尾_2340.mp4`、`out/B_…`、`out/C_…`：2340×1080、60 fps、无声。
- `out/候选三版_连播.mp4`：六段按 A 片头 → A 片尾 → B → C 连起来，一次看完。
- `out/*_sheet.png`：16 格联系表；`out/stills_*`：制作时抽的单帧。

## 数据：每一版的 `intro/data.json`、`outro/data.json`

片头（三版相同）：

```json
{ "name": "悠一", "role": "AI鼓励师", "tagline": "", "endColor": "#FFFFFF" }
```

| 字段 | 说明 |
|---|---|
| `name` | 大字。A 版逐笔手写（没有笔画数据的字会用马善政字体补上）；B 版盖章；C 版剪纸。1–4 个字都排得下，2 个字最好看 |
| `role` | 小字“AI鼓励师”。A 版两侧珊瑚色短横；B 版橡皮章；C 版铅笔手写 |
| `tagline` | 可选，一行 ≤ 20 字的灰色小字，在 role 下面 |
| `endColor` | 片头收尾淡到的颜色，默认白；`"none"` 不淡 |

片尾（三版相同，**这是给参考文献和致谢留的版面**）：

```json
{
  "references_title": "参考文献",
  "references": ["Anthropic，Claude Fable 5.1 模型卡与发布说明，2026-09", "…"],
  "thanks_title": "致谢",
  "thanks": [ { "label": "配音", "value": "悠一" }, { "label": "形象", "value": "鲸鱼娘 · 原型画师 上善无形（CC BY-NC-SA 4.0）" } ],
  "closing": "感谢观看，我们下期再见",
  "signature": "悠一"
}
```

| 字段 | 说明 |
|---|---|
| `references` | 参考文献，字符串数组，**建议 ≤ 6 条，最多 8 条**；每条自动折行、最多 3 行；超长会整体缩字号（42 → 20 px） |
| `thanks` | 致谢 / 制作清单，`{label, value}` 数组，最多 8 条；`label` 珊瑚色、≤ 4 字最好看；旧字段名 `items` 同义（所以现有 episode.json 的 `outro_items` 不用改） |
| `references_title` / `thanks_title` | 两栏标题，默认“参考文献”“致谢”；写成“本期制作清单”“资料来源”也行 |
| `closing` | 感谢语，逐笔手写，≤ 14 字 |
| `signature` | 签名，默认“悠一”（B 版朱印取前两个字） |

没有 `references` 就只有致谢一栏（占满整宽），反过来也一样；两个都没有就只剩感谢语和签名。两栏字号由内容决定，所有条目在 4.5 s 前全部可见，之后定格到 9.0 s。

## 重新出片

```bash
cd D:\大疆\AI科普\片头片尾\候选2026-10
python render_preview.py A_鼓励球/intro/index.html --data A_鼓励球/intro/data.json --sheet out/A_片头_sheet.png            # 联系表
python render_preview.py A_鼓励球/intro/index.html --data A_鼓励球/intro/data.json --width 2340 -o out/A_片头_2340.mp4     # 成片
python render_preview.py A_鼓励球/outro/index.html --data A_鼓励球/outro/data.json --stills 2.5,8.9 --stills-dir out/stills   # 单帧
```

`render_preview.py` 和 `../render.py` 的约定一样（`window.DURATION`、`renderAt(t)`、`__DATA__`、`__READY__`），多一个 `--width`。真正接进流水线时不用它：`add_to_video.py` / `assemble.py` 直接打开 `intro|outro/index.html`。

## 文件

```
候选2026-10/
├─ common/pack.js        三版共用：纸纹、缓动、固定种子随机、笔刷、逐笔手写（Hand）、纸屑、两栏排版、小球 / 云 / 太阳 / 纸飞机 / 铅笔 / 灯泡
├─ common/handdata.js    手写笔画数据（build_handdata.py 生成：225 个汉字 + 标点 + 拉丁；缺的字页面用马善政字体补）
├─ build_handdata.py     要让别的字也逐笔写，把字加进 TEXTS 重跑
├─ fonts/fonts2.css      新增的手写字体：Ma Shan Zheng（马善政楷书）、Caveat、Patrick Hand、Kalam，都是 OFL；Noto Sans SC 等仍用 ../fonts/
├─ A_鼓励球/ B_纸飞机/ C_铅笔灯泡/   各 intro/index.html + data.json、outro/index.html + data.json
├─ render_preview.py
└─ out/                  成片、联系表、单帧
```

## 挑定之后要做的事（接进流水线）

1. 把选中那版的 `intro/`、`outro/` 换到 `../intro`、`../outro`（旧的终端小票版连 data.json 一起挪到 `AI科普/_旧稿/片头片尾_终端小票_2026-09/`），`common/`、`fonts/fonts2.css` 跟着放到 `../`，页面里的相对路径改一下。
2. **时长变了：片头 3.8 s → 5.5 s，片尾 4.8 s → 9.0 s。** 写死 3.8 的地方都要改：Way to AGI 的 `export_srt.py`（`INTRO = 3.8`）、CS 研究生技能、`Claude Code相关/…/make_submission.py`、`OpenAI相关/skill/openai-episode/assets/engine-template/common.py`（`INTRO_SEC`）、`AI实操/…/export_srt.py`、`独立视频/…/make_ass_std.py --intro`、各技能 SKILL.md / pipeline.md / publish.md 里的“章节时间加 3.8 s”。`epcommon.pack_durations` 是从 index.html 里正则读 `window.DURATION = 5.5`，自动对；`add_to_video.py` 用 `page_duration()` 实际取，也自动对。
3. 片尾数据多了 `references`：`assemble.py` / `assemble_wide.py` 现在只传 `items + closing + signature`，要加一行把 `episode.json` 的 `outro_references`（新字段）传进去；`add_to_video.py --outro-data` 直接吃新 JSON。
4. 技能文档里“片头 3.8 s 打出悠一、片尾 4.8 s 印章”的自查项改成新的描述；AGENTS.md「片头片尾所有合集共用」那段同步改。
5. 片头片尾下面垫的 BGM（`add_to_video.py`）不用改；想加音效（小球落地“啪”、盖章“咚”、纸飞机“嗖”）另做。
