# 《一个月合并 2000 多个 PR，却不逐个 Review》（独立视频 · 长视频，2026-10-05）

围绕“不再 Review”：为什么 AI 时代有人不再逐个 Review PR。素材 = Matt Pocock 的 YouTube 直播（Lauren Tan / poteto 访谈）+ Lauren 自己在 X 上发的演讲视频（幻灯片）+ 宝玉的长推文总结 + pstack 官方文档。用户原话、事实核对结论、做法和坑见 `docs/ai/context/20261005-075000-no-more-review-long-video_CN.md`（末尾“状态”一节是接着做的步骤）。

## 目录

```text
独立视频/长视频/2026-10_不再Review/
  台本/        make_script.py（台本唯一来源，改它再重跑）→ 录制稿.json / plan.json；事实核对.md
  制作/
    00_整片/   引擎：build_timeline → check_subs → prep_frames → render_all → mix_audio → qa_mix → finish；capture_pages.py（页面录屏）、scenes.js（叠加层）、outro.json（片尾草稿）
    02_配音/   Fish 故事工作室配音：tts_input.txt（整稿，一行一句）、import_segments.py、build_voice.py、qa_names.py（专名读音）
    02_转写/   transcribe_live.py / transcribe_talk.py / merge_transcripts.py / words.py（词级转写和查词）
    04_封面/   make_cover.py（A / B / C 三个候选，16:9 + 4:3）
  make_submission.py → 投稿信息.json（标题 3 个候选、简介、标签、章节时间）
独立视频/素材/2026-10_不再Review/   直播视频、转写、X 推文全文 / 嵌入页、Lauren 的演讲视频（整个目录不进 git）
```

## 重做 / 接着做

```bash
cd 台本 && python make_script.py                       # 改完台本重生成 录制稿.json / plan.json，再重生成 制作/02_配音/tts_input.txt
cd ../制作/00_整片
python build_timeline.py [--est]                       # --est 按字数估时间（配音没出之前用）
python check_subs.py && python prep_frames.py          # 字幕版式自检、抽帧（增量）
python render_all.py --stills-segs                     # 每个场景 3 张静帧，逐张看
python mix_audio.py && python render_all.py            # 混音（同传段原声 −29 LUFS）→ 4 路渲染（先 ListAgents，同一时间只一个渲染）
python qa_mix.py                                       # 用 voice_only.wav 逐句核对配音位置和内容
python finish.py                                       # 片头片尾 + 手机预览 + 三份 SRT
cd ../.. && python make_submission.py                  # 投稿信息（章节时间 = 正片 + 片头）
python "D:\大疆\Claude Code相关\skill\claude-code-episode\scripts\predeliver_check.py" "<本期目录>"
```

## 现状（2026-10-05 15:35）

**更新**：用户 11:57 要求“并行，封面用 A，短视频发完后长视频也发四个平台”；15:15 要求封面统一成框版（白字 + 橙字黑描边、边框 6、黄贴纸、印花底），封面 A 和成片第 0 帧已按新样式重做（16:9 居中 + 左右模糊补边，`cover_frame0.py --pts-tol 0.03`）；`投稿信息.json` 已扩成四平台。**四个平台都发了（2026-10-05）：B 站 16:22 BV1jEHs6XEne（开放浏览，封面两个比例核对过）、视频号 16:33、抖音 16:37（审核中）、小红书 16:42**；记录 `docs/ai/context/20261005-153500-no-more-review-cover-unify-and-publish_CN.md`。

### 11:30 时的状态

**成片做完了，等用户选封面 / 标题、听配音、确认片尾清单**；还没投稿（用户拖 mp4、说“发布”才点）。

- 成片 `不再Review_成片.mp4`：451.4 s = 片头 4.8 + 正片 437.6 + 片尾 9.0，2340×1080 30 fps，191 MB，−16.2 LUFS、真峰值 −0.9 dBFS；`不再Review_手机预览.mp4`（23.6 MB）、三份 SRT（104 条，时间含片头）都在本目录。
- 配音：Fish 故事工作室空白项目，「温柔男生」+ S2 Pro，90 句一次生成、一次导出（SHA-256 逐句核对）；`qa_mix.py` 逐句识别 90 条，只有 2 条低于 0.8：K03（数字写法 2500 / 两千五百，识别结果对）、**N19“她靠两样东西”被听成“他考了两样东西”（靠 / 考，要用耳朵听）**；其余 0.83–1.00。
- 渲染：第一次 4 路渲完（13128 帧）后，抽帧发现 288 秒“8 × 1万+”数字框盖住右上角来源角标和幻灯片标题、访谈左下角直播自带的“Matt”名牌被说明条盖掉一半，改了 `scenes.js`（数字框挪到幻灯片左下角不带说明行；访谈上的说明条上移到 y 650、数字框 bottom 80，下沿停在名牌之上；连着几条同位置的条用 `fast` 快淡、前一条在后一条开始前 0.1 s 收掉），再整片重渲（3 路 834 s，0 报错）。
- 封面：`封面_选定_*` 目前是**暂按推荐的 A 复制的**（`make_cover.py --select A`，为了让 predeliver_check 全过）；用户选了别的就 `make_cover.py --select B|C`。`投稿信息.json` 的标题 3 个候选、简介 1988 字、章节时间（含片头）都已生成；`predeliver_check.py` 全部通过。
- 同题**短视频**在 `独立视频/短视频/2026-10_不再Review/`（54 s，dual 版式，二次剪辑）。
