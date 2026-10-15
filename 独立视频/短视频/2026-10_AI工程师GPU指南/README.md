# AI工程师GPU指南（竖屏短视频，2026-10-05）

X 长文《Everything an AI Engineer Needs to Know About GPUs》（@kmeanskaran / Karan，2026-10-01，https://x.com/kmeanskaran/status/2105635344385450151）的二次创作：87.3 s，1080×2340，single 版式 B + 边框 6，温柔男生第三人称配音 + 中英双语字幕 + BGM，画面是作者的手绘示意图（镜头推拉 + 高亮框）+ NVIDIA 官网 H200 页 + Hugging Face 价格表 + 5 张大数字卡。

**状态（2026-10-06 09:35）：已发布 B 站 BV1XyHd6KEJn（开放浏览）/ 抖音（09:33 回查已发布，aweme 7693342833876471040，链接已写进 `投稿信息.json`）/ 小红书（仍“审核中”，通过后补链接）；视频号用户说不发。封面 B、标题“推特长文《AI 工程师需要知道的 GPU 知识》精选”；视频顶上的标题 = 文章标题。小红书笔记是“原创声明关”发的，是否改成开等用户决定。**

## 文件
| 路径 | 内容 |
|---|---|
| `AI工程师GPU指南_成片.mp4` | 成片（第 0 帧还不是封面，用户选定封面后跑 `cover_frame0.py`） |
| `AI工程师GPU指南_手机预览.mp4` / `_双语字幕.srt` / `_中文字幕.srt` / `_英文字幕.srt` | 手机预览、三份 SRT（36 条，没有片头偏移） |
| `投稿信息.json` | 标题 3×4、四平台简介 / 话题 / 声明、来源、approval 状态 |
| `台本\录制稿.json` `plan.json` | 唯一台本来源（18 句，zh / say / en）和场景 / 镜头表 |
| `台本\台本.md` `事实核对.md` | 给人看的台本表；独立子代理的事实核对（13 条“要改口”都落实了） |
| `制作\00_整片\` | 引擎副本（`figShot` 配图镜头、`build_figs.py`、`capture_pages.py` 加了 `@tr` / `PRE_JS` / 截图左边和宽度）；`scenes.js` 末尾是本条场景 |
| `制作\02_配音\` | Fish 导出（`segments (24).zip`）、`tts/seg_raw/final/`、`edit/tts_edit.json` |
| `制作\04_封面\` | 框版封面 3×3：`候选A/B/C_{3x4,16x9,4x3}.png`、`候选总览.png`、`make_cover_src.py`（裁底图 + 画橙框）、`candidates_framed.json` |
| 素材 | `独立视频\素材\2026-10_AI工程师GPU指南\`（`文章\fxtwitter_tweet.json`、`图片\`） |

## 重做 / 接着做
```bash
cd 制作\00_整片
python capture_pages.py          # 页面截图（X 推文卡、NVIDIA H200、HF 价格表）
python build_figs.py             # 配图 → media/figs + figs.js
python build_timeline.py         # 真实配音时间轴（--est 是估时）
python check_subs.py && RENDER_WORKERS=3 python render_all.py && python finish.py
```
用户选定后：`python D:\大疆\短视频\skill\short-video\scripts\make_cover_framed.py <本条目录> --select X` → `cover_frame0.py <本条目录>` → 发布（`references/publish.md`）。

## 要耳朵听的句子
N02（GPT-OSS 怎么读）、N09（“更吃显存”）、N12（“B F 十六”）、N16（“GPU”）。机器识别（whisper medium + large-v3-turbo，带术语提示词）逐句都对得上，剩下的只能靠耳朵。

## 限定语（别在后续改稿时丢）
145 倍 / 0.01 ms / 1.5 ms / 670 token/s 是作者按规格表算的理论上限、作者自己说没实测；“约 5 GB / token”是作者估算；2.1 TB 是粗算（不含激活）；价格是 Hugging Face（AWS）10-05 的标价、会变；Kimi K3 的 1.56 TB 是 HF 仓库文件大小；没写 NVIDIA 的 32×H200 配方和 8×B300。
