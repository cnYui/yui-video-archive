# -*- coding: utf-8 -*-
"""字幕台本：英文原话（whisper 识别后人工校对）+ 中文译文，一屏一条 → cues.json（唯一来源）+ 台本.md（给人读）。

  python build_cues.py

按项目的中英双语字幕标准写（用户 2026-10-02：“看一下其他分集的 skill 中的字幕要求……统一用那个双语标准”；标准见
`Way to AGI/skill/way-to-agi-episode/references/subtitles.md`「中英双语」和 `pipeline.md` §2）：
  - 一条字幕 1–2 句，**中文不超过约 28 字、英文不超过约 90 字符，括号注释算在内**，各一行、不换行；放不下就把长句拆成两条（各带自己的 s / e，来自逐词时间）。
  - 中文口语、简洁，按意思翻；专有名词保留英文原名；括号注释用全角“（）”、一般 12 字以内、只写有把握的、大约每分钟一条，英文对应一个简短的半角括号注释。
  - 字幕和成片里听到的一致：括号注释是没说出口的话。
术语表（全片统一）：Claude Slides（产品名，不翻）· Claude（不翻）· Anthropic（不翻）· Nate（讲话人，Nate Parrott）· Voice Memos → 语音备忘录（iOS 中文系统里的名字）· presentation → 演示文稿 · slide → 幻灯片 · transcript → 文字稿 · prompt → 提示词。
  （画面里的 Claude Design System 只在界面上出现、没念，不进字幕。）

校对过的识别错误：Cloud → Claude（2 处）、“Claude's slides” → Claude Slides（他念的是提示词里的产品名）、“Voice Memo's app” → Voice Memos app；
第 12 条识别出的结尾 “for three to read.” 是幻觉（词概率 0.27–0.39，换 medium / large-v3-turbo 重识别这一段都只有 “And I think it's a really good idea.”），删掉。
s / e 是这句话在原片里的起止秒（来自 en_asr.json 的逐词时间；拆句的地方取两个词之间的时刻；第 12 条的 e 截在 “idea” 说完）。显示时间由 make_subs.py 在这个基础上前 0.1 s、后 0.45 s。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

CUES = [
    # (id, s, e, 英文, 中文)
    ("C01", 4.70, 8.72, "So occasionally, at work, I'll have an idea, and I'll want to present it to the team.", "工作的时候，我偶尔会冒出一个想法，想讲给团队听。"),
    ("C02", 9.88, 12.80, "Now, I used to spend a ton of time in the Slides app,", "以前我会花大把时间泡在幻灯片软件里，"),
    ("C03", 12.96, 15.46, "just staring at a blank window, not sure what to write.", "盯着一片空白的窗口，不知道该写什么。"),
    ("C04", 17.62, 19.90, "Now, instead, I just go for a walk.", "现在呢，我就出去散步。"),
    ("C05", 20.62, 23.80, "Hi there. My name is Nate. I'm a designer at Anthropic,", "大家好，我叫 Nate，是 Anthropic 的设计师。"),
    ("C06", 23.86, 25.50, "and here's how I use Claude Slides (the slide-making feature)", "下面讲讲我怎么用 Claude Slides（做幻灯片的功能）"),
    ("C07", 25.52, 28.22, "to do work without staring at the computer the whole time.", "不用整天盯着电脑，也能把事做完。"),
    ("C08", 28.82, 31.64, "I take my phone, and I use the Voice Memos app.", "我拿出手机，打开“语音备忘录”。"),
    ("C09", 32.06, 35.10, "I'll yap into the mic and talk through everything I want to say.", "对着麦克风絮絮叨叨，把想说的全讲出来。"),
    ("C10", 35.62, 39.88, "It's usually a mess, but it's okay, because it's just for me and Claude.", "通常乱成一团，但没关系，反正只给我和 Claude 看。"),
    ("C11", 40.64, 42.16, "So here's the idea I want to present.", "这就是我想讲的点子。"),
    ("C12", 42.64, 44.62, "You should be able to email Claude.", "你应该能给 Claude 发邮件。"),
    ("C13", 44.76, 48.12, "You should be able to send it a task and it should be able to email you back a result.", "给它发一个任务，它就能把结果用邮件发回给你。"),
    ("C14", 48.54, 49.95, "And I think it's a really good idea.", "我觉得这是个特别好的主意。"),
    ("C15", 50.70, 53.94, "I come home and I copy out the transcript and send it to Claude.", "我回到家，把文字稿复制出来，发给 Claude。"),
    ("C16", 54.52, 56.20, "And I write a prompt like,", "然后我写一句提示词，大概是："),
    ("C17", 56.32, 59.88, "turn my exact words into a presentation using Claude Slides.", "把我的原话做成演示文稿，用 Claude Slides。"),
    ("C18", 60.72, 62.95, "Claude usually makes it look pretty nice.", "Claude 做出来通常挺好看。"),
    ("C19", 63.04, 64.68, "It knows what our brand looks like,", "它知道我们的品牌是什么风格，"),
    ("C20", 64.80, 67.60, "so I don't have to find the latest fonts or slide templates.", "所以我不用去找最新的字体或幻灯片模板。"),
    ("C21", 69.35, 72.67, "Typically, I'll have one or two little adjustments that I'll make myself.", "一般我自己再做一两处小调整。"),
    ("C22", 73.88, 77.16, "If there's anything bigger, I'll leave comments and send them to Claude.", "如果有更大的改动，我就留下评论，发给 Claude。"),
    ("C23", 80.80, 84.44, "After I'm done, I can share it with a team or export it and send it off.", "弄完之后，可以分享给团队，也可以导出发出去。"),
    ("C24", 87.33, 91.59, "I've really enjoyed spending less time on presentation and more time on substance", "我真的很喜欢这样：少花时间做演示，多花时间在内容上，"),
    ("C25", 91.59, 93.93, "and getting a little fresh air in the process.", "顺便还能呼吸点新鲜空气。"),
    ("C26", 95.28, 97.94, "So try it out next time you've got something to present.", "下次你有东西要讲的时候，也试试看吧。"),
]


def main():
    cues = [{"id": i, "s": s, "e": e, "en": en, "zh": zh} for i, s, e, en, zh in CUES]
    (HERE / "cues.json").write_text(json.dumps({"title": "How an Anthropic designer uses Claude Slides", "cues": cues}, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# 《How an Anthropic designer uses Claude Slides》中英字幕台本", "", "英文 = 原话（whisper 识别后校对），中文 = 译文；s / e = 原片里的起止秒。标准：中文 ≤ 约 28 字、英文 ≤ 约 90 字符，各一行。", ""]
    md += [f"- **{c['id']}** [{c['s']:.2f}–{c['e']:.2f}] {c['zh']}  \n  {c['en']}" for c in cues]
    (HERE / "台本.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(cues)} 条，中文共 {sum(len(c['zh']) for c in cues)} 字")


if __name__ == "__main__":
    main()
