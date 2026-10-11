"""Generate common/handdata.js (window.__HAND__) for the 2026-10 intro / outro candidates.

Reuses the whiteboard engine's hand_glyphs.py (stroke medians from hanzi-writer-data, Latin from the EMS Tech
single-line font). The pages write the creator name, the role, the credit headings and the closing line stroke by
stroke; characters missing here fall back to a brush font inside the page (never an empty gap).

    python build_handdata.py            # -> common/handdata.js
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "skill" / "yuanlai-ruci-episode" / "assets" / "engine-template"))
import hand_glyphs  # noqa: E402

TEXTS = [
    "悠一", "AI鼓励师", "参考文献", "致谢", "本期制作清单", "资料来源", "特别致谢",
    "感谢观看，我们下期再见", "感谢大家看到最后", "下期见", "谢谢观看", "我们下期再会", "下次见", "再见",
    "拍摄 剪辑 配音 形象 画师 授权 模型 素材 字体 音乐 音效 评论区 观众 朋友 支持 关注 点赞 投币 收藏 转发 分享 订阅",
    "频道 合集 视频 封面 台本 文案 翻译 字幕 录屏 录音 混音 渲染 图片 截图 论文 文档 官方 博客 网站 新闻 发布 更新 数据",
    "公开 引用 以上 全部 排名 不分 先后 来自 出自 原型 作者 感谢 谢谢 再会 下次 下回 期待 欢迎 留言 交流 讨论 学习",
    "一起 进步 加油 继续 努力 日常 每天 每周 每日 日报 科普 原来如此 像素 讲解员 鲸鱼娘 山田凉 大肥鱼 悠一 的 了 和 与",
    "本 期 这 那 有 没 是 不 在 人 大 小 多 少 上 中 下 前 后 左 右 开 关 看 听 说 读 写 做 用 学 教 想 要 会 能 好 很 最 更",
    "你 我 他 她 它 们 家 们 位 个 条 篇 次 年 月 日 天 时 分 秒 第 零 两 三 四 五 六 七 八 九 十 百 千 万 亿",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "，。：；！？（）、—·…「」《》",
]
out = HERE / "common" / "handdata.js"
d = hand_glyphs.build_hand_js(TEXTS, out)
print(f"{out}: {len(d['cjk'])} 汉字, {len(d['punct'])} 标点, {len(d['lat']['g'])} 拉丁字符"
      + (f"；缺：{''.join(d['missing'])}" if d["missing"] else ""))
