# How an Anthropic designer uses Claude Slides（中英字幕版）

Anthropic 官方 YouTube 视频（104 s，Nate Parrott 讲他怎么用 Claude Slides：散步、语音备忘录讲想法、把文字稿发给 Claude 做成幻灯片）。2026-10-02 用户给了两个文件，要求“拼在一个视频中，把封面修改为中文，其他不变”，后来补“给视频加上中文的字幕，这样就是双语字幕了”。**已发布**：[BV1Yham6gECf](https://www.bilibili.com/video/BV1Yham6gECf/)（2026-10-02 16:13 北京时间，105 s，标题“Anthropic设计师教你如何使用Claude”，转载，进了 B 站合集「Claude Code相关」，是第 2 集；没做配音）。原片 = Claude 官方 YouTube 频道（@claude）2026-10-01 发的《Make presentations with Claude Slides》（https://www.youtube.com/watch?v=NzcRprKWbD8，1:45；封面上写的 “How an Anthropic designer uses Claude Slides” 是它的缩略图文字，和 YouTube 标题不是一个）。投稿填法见 `docs/ai/context/20261002-153000-claude-slides-designer-video-zh-subs-cover_CN.md` 的“投稿”一节。

| 文件 | 说明 |
|---|---|
| `成片_中英字幕.mp4` | 成品：原片 + 烧进画面的中英双语字幕（按项目的中英双语字幕标准：中文 52 px 墨黑白边一行、英文 30 px 灰一行，居中，字幕带在 y 922 以下），1920×1080、24 fps，声音原样 |
| `成片_无字幕.mp4` | 只把下载的视频流和音频流合在一起（`ffmpeg -c copy`，没重编码） |
| `成片_双语字幕.srt` / `成片_中文字幕.srt` / `成片_英文字幕.srt` | 26 条字幕（中文一行 + 英文一行），时间和烧进去的一致，可单独上传；命名照 Way to AGI / 计算机研究生的“双语 / 中文 / 英文”三份 |
| `制作/04_封面/封面_选定_16x9.png`（1280×720）、`封面_选定_4x3.png`（1280×960） | 中文封面：只把标题换成“Anthropic 设计师 / 如何使用 Claude Slides”，其余像素不动 |
| `素材/` | 原片视频流（`videoplayback (3).mp4`）、音频流（`videoplayback (1).m4a`）的拷贝，用户给的英文封面原图 |
| `台本/` | `build_cues.py`（英文校对稿 + 中文译文，唯一来源）→ `cues.json`、`台本.md`；`en_asr.json` / `en_transcript.txt` 是 whisper 识别结果 |

## 重做

```bash
cd 制作/02_转写 && python asr_en.py ../../素材/原片_音频流.m4a      # 识别英文（large-v3-turbo，约 90 s）
cd ../../台本 && python build_cues.py                                  # 改译文只改这里（中文 ≤ 约 28 字、英文 ≤ 约 90 字符，各一行）
cd ../制作/00_整片 && python make_subs.py && python render.py          # 出 ASS / SRT（会量宽度，超长报出来），烧进画面（15 s）
cd ../04_封面 && python make_cover_zh.py --weight 500 --size 80 --name 封面   # 中文封面
```

## 说明

- **字幕标准**（用户 2026-10-02：“看一下其他分集的 skill 中的字幕要求……统一用那个双语标准”）：以 `Way to AGI/skill/way-to-agi-episode/references/subtitles.md`「中英双语」+ `pipeline.md` §2 为准，样式取自该技能模板的 `#subs`：中文 52 px / 行高 66（Noto Sans SC 800，墨黑 #1B1B1F，白边）、英文 30 px / 行高 40（600，灰 #4B5563，白边），居中，字幕带 y 922 起；一条 1–2 句、中文 ≤ 约 28 字、英文 ≤ 约 90 字符（括号注释算在内）；每条开始前 0.1 s 到结束后 0.45 s、不叠；括号注释全角、≤ 12 字、约每分钟一条（这条只有一处：Claude Slides（做幻灯片的功能））；术语表在 `台本/build_cues.py` 开头。字重用 `制作/00_整片/fonts/NSC800.ttf`、`NSC600.ttf`（从变量字体切出的静态字重）。
- 原片没有任何字幕（下载的是 YouTube 的视频流 + 音频流），所以英文字幕是识别后人工校对的：Cloud → Claude（2 处）、“Claude's slides” → Claude Slides、“Voice Memo's app” → Voice Memos app；第 11 句结尾识别出的 “for three to read.” 是幻觉（词概率 0.27–0.39，换 medium 和 large-v3-turbo 重识别这一段都只有 “And I think it's a really good idea.”），已删。
- 开头 4.7 s（片头动画）和结尾（Claude 标志）没有人声，不加字幕；画面上原片自带的设计字（名牌、界面、胶囊字幕）都没动。
- 封面做法见 `制作/04_封面/make_cover_zh.py` 开头的说明：英文词 “Anthropic”“Claude Slides”（粗体）直接从原图裁下来贴回去，保证字体一致；中文用 Noto Serif SC 500（Google Fonts），基线和原来两行对齐（y = 523、613）。
- 版权：画面、声音、封面设计都是 Anthropic 的；英文逐字稿、译文、字幕文件、封面衍生图已在 `.gitignore` 里排除，不进公开仓库。发 B 站时标明转载、注明出处（YouTube 官方视频）。
