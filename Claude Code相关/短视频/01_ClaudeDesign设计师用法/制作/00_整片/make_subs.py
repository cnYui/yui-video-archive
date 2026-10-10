# -*- coding: utf-8 -*-
"""timeline.json 的字幕 → build/bilingual.ass（烧进画面）+ 成片_双语字幕.srt / 成片_中文字幕.srt / 成片_英文字幕.srt（放在本条目录根）。

  python make_subs.py

项目中英双语字幕标准（Way to AGI/skill/way-to-agi-episode/references/subtitles.md「中英双语」，代码实现 bilingual_std.py）：
  中文一行 52 px（Noto Sans SC 800，墨黑 + 米白描边向外 5 px）+ 英文一行 30 px（600，灰 #4B5563，描边 3 px），居中，各一行不换行；
  每条开始前 0.1 s 显示、结束后 0.45 s 收掉，不和下一条重叠（display_windows）。
竖屏（1080 宽）：每条中文 ≤ 约 17 个字宽、英文 ≤ 约 60 字符，左右各留 ≥ 70 px——这里用真实字体量宽度，超了报出来（要回 台本/build_script.py 改字幕）。
位置：中文行中心 y = BAND_TOP + 33，英文行中心 y = BAND_TOP + 90（版式见 config.py，照技能 short-video 的 layout.md：字幕带 1195–1305）。
SRT 时间 = 显示窗口，没有片头偏移（短视频不加悠一片头片尾）。字重用 fonts/NSC800.ttf、NSC600.ttf（族名 NSC800 / NSC600，libass 按族名取）。
"""
import json
import sys

from PIL import ImageFont

import config as C

sys.path.insert(0, str(C.WAY_SCRIPTS))
from bilingual_std import display_windows, esc_ass, ts_ass, write_srts  # noqa: E402

BUILD = C.HERE / "build"
MAX_W = C.W - 140


def bgr(rgb):
    return "&H00%02X%02X%02X" % (rgb[2], rgb[1], rgb[0])


def main():
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    subs = tl["subs"]
    fz = ImageFont.truetype(str(C.FONTS / "NSC800.ttf"), C.ZH_PX)
    fe = ImageFont.truetype(str(C.FONTS / "NSC600.ttf"), C.EN_PX)
    wins = display_windows([(s["a"], s["b"]) for s in subs])
    wins[-1] = (wins[-1][0], min(wins[-1][1], tl["total"]))          # 最后一条别越过片尾
    bad, ev, rows = [], [], []
    for s, (a, b) in zip(subs, wins):
        wz, we = fz.getlength(s["zh"]), fe.getlength(s["en"])
        if wz > MAX_W or we > MAX_W or not s["zh"].strip() or not s["en"].strip():
            bad.append(f"{s['id']}：中文 {wz:.0f} px、英文 {we:.0f} px（≤ {MAX_W}）")
        ev.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},ZH,,0,0,0,,{{\\an5\\pos({C.CX},{C.ZH_CY})}}{esc_ass(s['zh'])}")
        ev.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},EN,,0,0,0,,{{\\an5\\pos({C.CX},{C.EN_CY})}}{esc_ass(s['en'])}")
        rows.append((a, b, s["zh"], s["en"]))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {C.W}
PlayResY: {C.H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,NSC800,{C.ZH_PX},{bgr(C.INK)},&H000000FF,{bgr(C.BG)},&H00000000,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1
Style: EN,NSC600,{C.EN_PX},{bgr(C.EN_GREY)},&H000000FF,{bgr(C.BG)},&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (BUILD / "bilingual.ass").write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    write_srts(str(C.EP / "成片"), rows)
    print(f"bilingual.ass：{len(subs)} 条；SRT 三份已写到 {C.EP}（成片_双语字幕.srt 等）")
    print("超宽 / 空条：" + ("；".join(bad) if bad else "无"))
    for s, (a, b) in zip(subs, wins):
        print(f"  {a:6.2f}–{b:6.2f}  {s['zh']}  |  {s['en']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
