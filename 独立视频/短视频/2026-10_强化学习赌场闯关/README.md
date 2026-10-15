# 强化学习赌场闯关（竖屏短视频，single 版式）

《Reinforcement Learning from scratch #1》——X 用户 @goyal__pramod（Pramod Goyal）2026-10-03 的长文，作者说是 Sutton & Barto 教科书第 2–4 章的“赌场闯关版”。本条用文章里的手绘配图 + 作者推文截图，温柔男生第三人称重新讲，约 60 秒。

- 做法：技能 `short-video`（竖屏 1080×2340，版式 B + 边框 6，随机背景印花 `pattern_ink`）；全部是 `card` 场景，画面是文章配图（`制作\00_整片\media\img\`）+ 推文截图（`capture_pages.py` 的 `X_t1`），镜头由 `scenes.js` 里的 `imgShot()`（缓推 / 平移 + 橙框 / 荧光笔 / 白色遮罩）和 `pageShot()`（`fixed: true` 不滚动）做，时间全按字幕条算。
- 素材：`D:\大疆\独立视频\素材\2026-10_强化学习赌场闯关\`（`文章\fxtwitter_tweet.json` 全文 JSON、`文章\article_blocks.txt`、`图片\` 18 张配图 + 封面）。全文取法：`https://api.fxtwitter.com/goyal__pramod/status/2106244243727507733`（不用登录）。
- 台本：`台本\录制稿.json`（18 句：zh / say / en）+ `台本\plan.json`（12 个场景）+ `台本\事实核对.md`（每个说法的依据；文章说“价值迭代 5 轮”，照他的代码是 4 轮停，台词不念 5）。
- 配音：Fish 故事工作室、声线「温柔男生」+ S2 Pro（`制作\02_配音\say_lines.txt` 是键入的稿子，SHA-256 `b5bbad58…`）。
- 封面：`制作\04_封面\candidates_framed.json` → `make_cover_framed.py`（3 候选 × 3 比例 + 总览）；标题 3×3（当时 3×4，视频号去掉）在 `投稿信息.json`。
- 同一条推文另一个代理（Codex？）也在做，建了 `独立视频\短视频\2026-10_强化学习从零开始\`（只有 README），互不覆盖；见 `docs\ai\context\20261005-204800-rl-casino-short-video-claude_CN.md`。

## 重跑
```bash
cd 制作/00_整片
python build_timeline.py            # 配音后用真实时间轴（--est 是按字数估的）
python prep_frames.py && python check_subs.py
python render_all.py --stills-segs  # 逐张看静帧
python mix_audio.py && python render_all.py && python qa_mix.py && python finish.py
```

## 发布状态（2026-10-06 09:5x）
- B 站 BV1rGH46vEwT（开放浏览，简介 10-06 补上）、抖音（已发布）、小红书（已发布）：用户 10-05 21:41–21:42 自己点的发布。
- **标题已改成“入门”版**（用户 10-06：“标题修改为入门，你来修改”）：B 站 / 抖音 `推特长文《强化学习从零开始》，一个视频带你入门强化学习`、小红书 `《强化学习从零开始》一个视频入门`（正文第一行同步改）；三个平台都读回核对过（抖音先“修改审核中”、几分钟后通过）。
- **小红书“原创声明”选开**（用户：“原创声明 就是小红书应该选择的”）：线上笔记本来就是开的，不用改。
- **视频号不发**（用户：“视频号之后不发”，已从 short-video 技能移除）；`投稿信息.json` 里的视频号字段已删。
- 详细和教训：`投稿信息.json` 的 `published`、`docs/ai/context/20261005-204800-rl-casino-short-video-claude_CN.md`、`D:\大疆\短视频\流程复盘.md` 第 8 部分。
