# -*- coding: utf-8 -*-
"""image-blaster 推荐：四个平台的投稿文案 → 投稿信息.json，并按各平台的字数上限核对。"""
import json
from pathlib import Path

EP = Path(r"D:\大疆\独立视频\短视频\2026-10_image-blaster推荐")
ORIG = "https://x.com/neilsonks/status/2055013782771134479"
REPOST = "https://x.com/liambraus/status/2106383261089849825"
REPO = "https://github.com/neilsonnn/image-blaster"
SHOWCASE = "https://www.worldlabs.ai/labs/showcase/image-blaster"

bili_desc = f"""GitHub 项目推荐：neilsonnn/image-blaster —— 一套 Claude 技能。丢一张图，先让 Claude 看图列出画面里的物件，混元 3D（Hunyuan 3D）给每件物件出 3D 模型，World Labs 用擦掉物件的空场景生成可以走进去的 3D 场景，再用 ElevenLabs 配环境循环音和每件物体的碰撞音。

画面和英文讲解：作者 @neilsonks（Neilson Koerner-Safrata，World Labs 设计团队）2026-05-14 在 X 上发的演示视频 {ORIG} ，本片用的是 @liambraus 2026-10-03 转发的版本 {REPOST} 。中文为 AI 同传（曼波声线），字幕中英双语；片中的 GitHub 页面是我们自己截的图。

项目：{REPO} （MIT 协议；我们截页面时 5.2k 星；最后一次提交 2026-05-15）。World Labs 展示页：{SHOWCASE}

要说明的：
- “不到 5 分钟”是 README 里作者自己的说法，我们没有实测；
- 需要自备 World Labs 和 FAL 两个 API key，费用我们没有核实；
- 演示里作者说目前只管生成、不管搭场景；
- 仓库四月建的，五月中旬之后没再更新。

画面版权归原作者，仅作介绍和评论引用；配音为 AI 生成（曼波声线）。"""

short_body = (
    "GitHub 项目推荐：neilsonnn/image-blaster（MIT）。丢一张图，Claude 先列出画面里的物件，混元 3D 给每件物件出模型，"
    "World Labs 用擦掉物件的空场景生成能走进去的 3D 场景，ElevenLabs 配环境音和碰撞音。"
    "画面和英文讲解来自作者 @neilsonks 在 X 上发的演示视频，中文为 AI 同传，画面版权归原作者。"
    "“不到 5 分钟”是作者自述，我们没有实测；要自备 World Labs 和 FAL 两个 API key，费用没核实。"
)
dy_topics = ["GitHub", "开源项目", "3D", "AI工具", "Claude"]
xhs_topics = ["GitHub", "开源项目", "AI工具", "3D建模", "Claude"]
wx_topics = ["GitHub", "开源项目", "AI工具", "3D", "Claude"]

xhs_body = """GitHub 项目推荐：neilsonnn/image-blaster（MIT，5000+ 星）。一套 Claude 技能，丢一张图就能出：
1. Claude 先看图，列出画面里的物件
2. 混元 3D 给每件物件出 3D 模型
3. 把物件擦掉的空场景交给 World Labs，生成能走进去的 3D 场景
4. ElevenLabs 配环境循环音和每件物体的碰撞音
画面和英文讲解来自作者 @neilsonks 在 X 上发的演示视频，中文为 AI 同传，画面版权归原作者。
要说明的：“不到 5 分钟”是作者在 README 里的自述，我们没有实测；需要自备 World Labs 和 FAL 两个 API key，费用没有核实；作者自己说目前只管生成、不管搭场景。"""

info = {
    "_说明": "image-blaster 推荐 · 四个平台的投稿内容（2026-10-04 用户：去 B 站 / 抖音 / 小红书 / 视频号用浏览器插件发布）。成片由用户拖进各平台的上传区（插件传不了 10 MB 以上），我填表；用户明说“发布”才点最后一步。",
    "video": "image-blaster推荐_成片.mp4",
    "duration_s": 59.6,
    "covers": {"3x4": "制作/04_封面/封面_选定_3x4.png", "16x9": "制作/04_封面/封面_选定_16x9.png", "4x3": "制作/04_封面/封面_选定_4x3.png"},
    "source": {
        "original_post": ORIG,
        "original_author": "@neilsonks（Neilson Koerner-Safrata，World Labs），2026-05-14",
        "repost_used": REPOST + "（@liambraus 2026-10-03 转发，本片用这份 720p）",
        "project": REPO,
    },
    "bilibili": {
        "title": "一张图生成能走进去的3D世界！GitHub 5000+星 Claude 技能 image-blaster（作者演示·中文同传）",
        "desc": bili_desc,
        "declaration": ["含AI生成内容", "内容为转载"],
        "repost_source": f"转自 X @neilsonks 原帖 {ORIG} （2026-05-14）；画面用 @liambraus 转发版 {REPOST} ；中文为 AI 同传",
        "category": "人工智能（默认 tid 231）",
        "tags": ["claude", "GitHub", "开源项目", "3D", "AI工具", "人工智能", "AI编程", "三维建模", "Claude Code", "项目推荐"],
        "tags_spare": ["AI Agent", "大模型", "World Labs", "技能"],
        "collection": "不选（独立视频）",
        "cover": "两个位各传各的（双比例同步改动不勾）：16:9 → 个人空间封面，4:3 → 首页推荐封面",
    },
    "douyin": {
        "title": "一张图变3D世界！GitHub 5000+星的开源项目",
        "desc": short_body,
        "topics": dy_topics,
        "declaration": "内容由AI生成（以页面上的字为准）",
        "cover": "竖封面 3:4 = 封面_选定_3x4.png；横封面 4:3 = 封面_选定_4x3.png",
    },
    "xiaohongshu": {
        "title": "一张图变3D世界｜5000+星开源项目",
        "desc": xhs_body,
        "topics": xhs_topics,
        "declaration": "含AI合成内容 / 引用转载（以页面上的字为准）",
        "cover": "3:4 = 封面_选定_3x4.png",
    },
    "weixin_channels": {
        "short_title": "一张图变3D世界的开源项目",
        "desc": short_body,
        "topics": wx_topics,
        "declaration": "含AI生成内容；不勾原创（画面来自 @neilsonks 原帖）",
        "cover": "3:4 = 封面_选定_3x4.png",
    },
    "published": {},
}

(EP / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")


def n(s):
    return len(s)


def with_topics(body, topics):
    return body + "\n" + " ".join("#" + t for t in topics)


print("B站 标题", n(info["bilibili"]["title"]), "/ 80；简介", n(bili_desc), "/ 2000；转载来源", n(info["bilibili"]["repost_source"]), "/ 200；标签", len(info["bilibili"]["tags"]), "/ 10")
print("抖音 标题", n(info["douyin"]["title"]), "/ 30；简介(含话题)", n(with_topics(short_body, dy_topics)), "/ 1000")
print("小红书 标题", n(info["xiaohongshu"]["title"]), "/ 20；正文(含话题)", n(with_topics(xhs_body, xhs_topics)), "/ 1000")
print("视频号 短标题", n(info["weixin_channels"]["short_title"]), "(6–16)；描述(含话题)", n(with_topics(short_body, wx_topics)))
