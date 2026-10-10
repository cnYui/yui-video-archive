# -*- coding: utf-8 -*-
"""短视频台本（唯一来源）→ 台本/录制稿.json + 台本/台本.md，并用真实字体量每条字幕的宽度。

  python build_script.py

一句 = 一个配音区块（`say` 是给曼波念的字，`zh` / `en` 是烧进画面的双语字幕）；一句可以拆成 1–2 条字幕（`cues`）。
竖屏 1080 宽，字幕标准里的 52 px / 30 px 不变，所以每条中文 ≤ 约 17.5 个字宽、英文 ≤ 约 60 个字符；这里量真实宽度，超了就报出来。

文风：照 docs/台本风格_AI大圆镜.md（2026-10-04 起所有台本）+ 技能 short-video 的 references/script.md——30 秒以内只要 钩子 → 背书 → 拆机制 → 收尾金句 四拍；
  配音是中文讲解（不是逐句翻译），挑最硬的点重排，原话只引最关键的一句（N06 “Bigger bird.”）；不靠加速凑时长（配音 1.0×），超了就删句。
  N01 钩子 = 最反常识的具体事实 + 数字（两杯咖啡：视频里喝了两次咖啡，不夸大成“两杯咖啡的工夫做完”）；N02 答案 + 产品名；N03–N07 拆机制（每句一个新信息：一句话 / 四版）；
  N08 官方原话（视频简介最后一句）；N09 官方金句（片尾卡）。背书（官方演示）放在标题上面的小字 kicker 里，不占配音时间。
译文规则（项目双语标准）：口语、简洁，按意思翻；专名保留官方英文；官方原句（片尾 “Claude makes it. You steer it.”）英文用原话；
不用第三人称代词称呼 Nate（旁白里省掉主语）；日期不写几号（美西 10-02、北京 10-03，差一天）。

事实出处：
  官方视频 = Claude 官方 YouTube 频道（@claude）2026-10-02 12:44（美西）发的《Build an App With Claude Design》（1:43，视频 ID COJAZQM1aeQ；画面上的缩略图文字是 “How an Anthropic designer uses Claude Design”）。
  官方简介：“Nate, a designer at Anthropic, uses Claude design in Claude Code to take his side project's onboarding from rough idea to working prototype. He connects his repo, opens the Artifacts tab,
  and asks Claude for design options. Then leaves comments on what's working, fixes details himself in the editor, and asks for a click-through prototype before telling Claude to build it.
  A quick design process like this fits anywhere you'd normally skip straight to code.”
  原话（制作/02_转写/asr_en.json）：“I go get a coffee, I come back, and I see what we've got.”（N01 / N02）；“Get another coffee, come back, and see what we got.”（第二杯，做原型时）；
  “I open up Claude code, connect my repo, head over to the artifacts tab and make a new design.”（N03）；“Design a silly onboarding for this app.”（N04，屏幕上的提示词是 design a silly onboarding for this silly app. start from what we have currently, and do a series of designs for new ideas）；
  聊天里 Claude 说 “I'll look at what the first run does today, then sketch some new directions next to it.” / “The canvas has five artboards: Current + A–D”（N05：四版新方案 + 一块现状对照）；
  评论框里打的是 “@Claude Bigger bird. Much bigger. It should be uncomfortable.”（N06）；“I don't like some of the details. So I go into the editor, and I fix them myself.”（N06）；
  “Then I ask Claude to make a click-through prototype … I play around with it, not bad … So I say, okay Claude, build it.”（N07）；片尾卡 “Claude makes it. You steer it.”（N09）。
"""
import json
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parent
FONTS = EP / "制作" / "00_整片" / "fonts"
ZH_PX, EN_PX = 52, 30
MAX_W = 940                                   # 1080 宽，左右各留 70 px

# 顶上标题（整条一直在）：第一行 ≤ 12 字（黑 76 px），第二行 ≤ 15 字（橙 60 px），kicker ≤ 18 字（<b> 里的词用强调橙）
HOOK = ["设计师喝了两杯咖啡", "Claude 一次出四版"]
KICKER = "悠一 · <b>Claude</b> 官方演示"

LINES = [
    dict(id="N01", say="做个引导页，Anthropic 的设计师喝了两杯咖啡。",
         cues=[("做个引导页，", "Designing an onboarding,"), ("Anthropic 的设计师喝了两杯咖啡。", "an Anthropic designer had two coffees.")]),
    dict(id="N02", say="这两杯咖啡的工夫，Claude Design 在干活。",
         cues=[("这两杯咖啡的工夫，", "During those two coffees,"), ("Claude Design 在干活。", "Claude Design does the work.")]),
    dict(id="N03", say="在 Claude Code 里连上仓库，进 Artifacts 新建设计。",
         cues=[("在 Claude Code 里连上仓库，", "In Claude Code, connect your repo,"), ("进 Artifacts 新建设计。", "go to Artifacts, start a new design.")]),
    dict(id="N04", say="一句话：设计个搞笑的新手引导。",
         cues=[("一句话：设计个搞笑的新手引导。", "One line: design a silly onboarding.")]),
    dict(id="N05", say="Claude 先看现有页面，再摆出四版方案。",
         cues=[("Claude 先看现有页面，", "Claude checks the current screens,"), ("再摆出四版方案。", "then lays out four options.")]),
    dict(id="N06", say="评论里说：鸟再大点。细节自己进编辑器改。",
         cues=[("评论里说：鸟再大点。", "In a comment: “Bigger bird.”"), ("细节自己进编辑器改。", "Fix details in the editor yourself.")]),
    dict(id="N07", say="再要个可点击的原型，满意就说：开工。",
         cues=[("再要个可点击的原型，", "Ask for a click-through prototype,"), ("满意就说：开工。", "then say: build it.")]),
    dict(id="N08", say="官方说：本来直接写代码的地方，也能先设计一遍。",
         cues=[("官方说：本来直接写代码的地方，", "Anthropic says: where you'd normally skip to code,"), ("也能先设计一遍。", "you can design a quick version first.")]),
    dict(id="N09", say="Claude 做出来，你来掌舵。",
         cues=[("Claude 做出来，你来掌舵。", "Claude makes it. You steer it.")]),
]


def main():
    fz = ImageFont.truetype(str(FONTS / "NSC800.ttf"), ZH_PX)
    fe = ImageFont.truetype(str(FONTS / "NSC600.ttf"), EN_PX)
    out, bad, md = [], [], ["# 台本（中英并排）", "", f"标题：{HOOK[0]} / {HOOK[1]}；kicker：{KICKER}", "",
                            "| 句 | 念的字（say） | 中文字幕 | 英文字幕 | 宽度 px（中 / 英） |", "|---|---|---|---|---|"]
    for l in LINES:
        zh = "".join(c[0] for c in l["cues"])
        en = " ".join(c[1] for c in l["cues"])
        out.append({"id": l["id"], "zh": zh, "say": l["say"], "en": en, "cues": [{"zh": a, "en": b} for a, b in l["cues"]]})
        for k, (a, b) in enumerate(l["cues"]):
            wz, we = fz.getlength(a), fe.getlength(b)
            flag = " ⚠" if wz > MAX_W or we > MAX_W else ""
            if flag:
                bad.append(f"{l['id']}.{k + 1}：中文 {wz:.0f} px、英文 {we:.0f} px（≤ {MAX_W}）")
            md.append(f"| {l['id']}.{k + 1} | {l['say'] if k == 0 else ''} | {a} | {b} | {wz:.0f} / {we:.0f}{flag} |")
    (HERE / "录制稿.json").write_text(json.dumps({"hook": HOOK, "kicker": KICKER, "lines": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "台本.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    nchar = sum(len(l["say"]) for l in LINES)
    print(f"{len(LINES)} 句，{sum(len(l['cues']) for l in LINES)} 条字幕，念的字共 {nchar} 个字符（含标点、英文字母）")
    print("超宽：" + ("；".join(bad) if bad else "无"))


if __name__ == "__main__":
    main()
