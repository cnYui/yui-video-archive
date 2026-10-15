# 《不再 Review》短视频（独立视频 · 短视频，2026-10-05）

长视频《一个月合并 2000 多个 PR，却不逐个 Review》（`独立视频/长视频/2026-10_不再Review/`）的二次剪辑：54 s，1080×2340，没有悠一片头片尾；dual 版式——上框 Lauren / Matt 的访谈人像格（静音），下框她演讲里的幻灯片和 pstack 官方页面录屏；温柔男生第三人称重新讲、BGM 床 −9 dB。素材和事实核对都沿用长视频（`独立视频/素材/2026-10_不再Review/`、长视频 `台本/事实核对.md`）。记录 `docs/ai/context/20261005-113000-no-more-review-short-video_CN.md`。

## 文件

```text
台本/make_script.py       台本唯一来源（12 句；镜头表 plan 也在这里）→ 录制稿.json / plan.json
制作/00_整片/             竖屏引擎副本：build_timeline → check_subs → prep_frames → render_all → mix_audio → qa_mix → finish
                          （prep_frames / build_timeline 加了 range 的 bg 纯色补边；mix_audio 的 BGM_BED = −9 dB）
制作/02_配音/             Fish 故事工作室配音：tts_input.txt（整稿）、import_segments.py、build_voice.py
制作/04_封面/             candidates.json → make_candidates.py（3 候选 × 3:4 / 16:9 / 4:3 + 候选总览.png）
投稿信息.json             标题 3×4、四个平台的简介 / 话题 / 声明、来源（approval = pending）
不再Review短视频_成片.mp4 / _手机预览.mp4 / 三份 SRT（26 条，无片头偏移）
```

## 重做

```bash
cd 台本 && python make_script.py                          # 改台本 / 镜头表后重生成 录制稿.json、plan.json，再把 say 同步到 制作/02_配音/tts_input.txt
cd ../制作/00_整片
python build_timeline.py [--est]                          # --est 按字数估时（配音没出之前）
python check_subs.py && python prep_frames.py && python render_all.py --stills-segs
python mix_audio.py && python render_all.py               # 渲染前 ListAgents + 看空闲内存（≥ 6 GB 用 4 路，否则 RENDER_WORKERS=3）
python qa_mix.py && python finish.py                      # 逐句识别 + 成片 / 手机预览 / SRT
python "D:\大疆\短视频\skill\short-video\scripts\make_candidates.py" "<本条目录>"        # 封面 3×3
python "D:\大疆\短视频\skill\short-video\scripts\check_titles.py" "<本条目录>"            # 标题 3×4 限长
```

## 现状（2026-10-05 15:35）

用户 11:57 同意（封面 A、标题 1、并行发布）：**B 站 15:08 发布（BV1pcHp64ECz）、抖音 15:11（审核中）、小红书 15:24 都已发，视频号不发（用户 2026-10-06 定）**。15:15 用户要求封面统一成框版（白字 + 橙字）：封面 A 和成片第 0 帧已重做，B 站 / 抖音的封面已替换（B 站线上 cover / cover43 核对过，抖音“修改审核中”）；详情 `投稿信息.json` 的 `published`、记录 `docs/ai/context/20261005-153500-no-more-review-cover-unify-and-publish_CN.md`。

### 11:35 时的状态

成片、手机预览、SRT、封面 3×3、标题 3×4 都做好了，**交付包已发用户，等“封面 X 标题 Y 同意”**；之后：`make_candidates.py --select X` → `cover_frame0.py <本条>`（成片第 0 帧 = 选定封面）→ 定稿 `投稿信息.json` → 排队（四个创作页：日报 RSS 源扩展 → 短视频制作 → 长视频制作与素材下载 → 我）→ 用户拖原片、我填四个平台（B 站不选合集、声明含 AI 生成内容、视频号不选位置）→ 点发布 → 逐个核对线上。**没发布。**

要用耳朵听的句子：N02（Lauren Tan / SpaceXAI / Grok Bot）、N08（pstack）、N07（lint）。
