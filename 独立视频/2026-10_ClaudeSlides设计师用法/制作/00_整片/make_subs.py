# -*- coding: utf-8 -*-
"""台本/cues.json → bilingual.ass（烧进画面）+ 成片_双语字幕.srt / 成片_中文字幕.srt / 成片_英文字幕.srt（和成片放一起）。

  python make_subs.py

按项目的中英双语字幕标准（用户 2026-10-02：“统一用那个双语标准”；标准在 `Way to AGI/skill/way-to-agi-episode/references/subtitles.md`「中英双语」、
`pipeline.md` §2，样式取自该技能模板 `assets/template/制作/03_成片/index.html` 的 `#subs` / `#subZh` / `#subEn`）：
  - 版式：居中，字幕带在 y 922 以下（带高 130）：中文 52 px / 行高 66（Noto Sans SC ExtraBold 800，墨黑 #1B1B1F，白边 10 px 描边，里面一半被字盖住 → 向外 5 px）、
    英文 30 px / 行高 40，从带顶往下 70 px（Noto Sans SC SemiBold 600，灰 #4B5563，白边 6 px → 向外 3 px），各一行、不换行。
  - 长度：中文 ≤ 约 28 字、英文 ≤ 约 90 字符（括号注释算在内）；本脚本会量实际宽度，超了就报出来（要回 build_cues.py 拆条）。
  - 时间：每条从开始前 0.1 s 显示到结束后 0.45 s，不和下一条重叠（下一条开始前 0.1 s 收掉）。
  - SRT 三份：双语（中文一行 + 英文一行）、中文、英文；时间和烧进去的一致。
字重用 fonts/NSC800.ttf、NSC600.ttf（从变量字体 NotoSansSC.ttf 切出的静态字重，族名 NSC800 / NSC600），libass 按族名取，不靠 \\b 猜字重。
"""
import json
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
ZH_FONT, EN_FONT = "NSC800", "NSC600"
ZH_PX, EN_PX = 52, 30
ZH_Y, EN_Y = 922 + 33, 922 + 70 + 20          # 字幕带里两行的垂直中心：带顶 922 + 行高的一半
CX = 960
LEAD, LAG = 0.1, 0.45
ZH_MAX_CHARS, EN_MAX_CHARS = 28.5, 90          # 中文按“字”算（52 px 的宽度 / 52），英文按字符数
INK, GREY = "&H001F1B1B", "&H00635B4B"        # #1B1B1F、#4B5563（ASS 是 BGR）


def ts_ass(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ts_srt(t):
    ms = round(max(0.0, t) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def esc(s):
    return s.replace("{", "(").replace("}", ")")


def main():
    cues = sorted(json.loads((EP / "台本" / "cues.json").read_text(encoding="utf-8"))["cues"], key=lambda c: c["s"])
    fz = ImageFont.truetype(str(HERE / "fonts" / "NSC800.ttf"), ZH_PX)
    fe = ImageFont.truetype(str(HERE / "fonts" / "NSC600.ttf"), EN_PX)
    events, srt, bad = [], {"zh": [], "en": [], "both": []}, []
    for i, c in enumerate(cues):
        zh_chars = fz.getlength(c["zh"]) / ZH_PX
        if zh_chars > ZH_MAX_CHARS or len(c["en"]) > EN_MAX_CHARS or not c["zh"].strip() or not c["en"].strip():
            bad.append(f"{c['id']}：中文 {zh_chars:.1f} 字（≤ {ZH_MAX_CHARS}）、英文 {len(c['en'])} 字符（≤ {EN_MAX_CHARS}）")
        a = c["s"] - LEAD
        b = c["e"] + LAG
        if i + 1 < len(cues):
            b = min(b, cues[i + 1]["s"] - LEAD - 0.02)
        b = max(b, a + 0.3)
        events.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},ZH,,0,0,0,,{{\\an5\\pos({CX},{ZH_Y})}}{esc(c['zh'])}")
        events.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},EN,,0,0,0,,{{\\an5\\pos({CX},{EN_Y})}}{esc(c['en'])}")
        for key, text in (("zh", c["zh"]), ("en", c["en"]), ("both", c["zh"] + "\n" + c["en"])):
            srt[key].append(f"{i + 1}\n{ts_srt(a)} --> {ts_srt(b)}\n{text}\n")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,{ZH_FONT},{ZH_PX},{INK},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1
Style: EN,{EN_FONT},{EN_PX},{GREY},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (HERE / "bilingual.ass").write_text(head + "\n".join(events) + "\n", encoding="utf-8")
    for key, name in (("both", "成片_双语字幕.srt"), ("zh", "成片_中文字幕.srt"), ("en", "成片_英文字幕.srt")):
        (EP / name).write_text("\n".join(srt[key]), encoding="utf-8")
    print(f"bilingual.ass：{len(cues)} 条；成片_双语字幕.srt / 成片_中文字幕.srt / 成片_英文字幕.srt 已写到 {EP}")
    print("超长（要回 build_cues.py 拆条）：" + ("；".join(bad) if bad else "无"))


if __name__ == "__main__":
    main()
