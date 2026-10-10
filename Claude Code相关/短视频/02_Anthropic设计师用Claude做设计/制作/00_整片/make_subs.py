# -*- coding: utf-8 -*-
"""timeline.json 的字幕 → build/bilingual.ass（烧进画面）+ 本条目录根的 成片_双语字幕.srt / 成片_中文字幕.srt / 成片_英文字幕.srt。

  python make_subs.py

项目中英双语字幕标准（Way to AGI/skill/way-to-agi-episode/references/subtitles.md「中英双语」，代码实现 bilingual_std.py）：
  中文一行 52 px（Noto Sans SC 800，墨黑 + 米白描边向外 5 px）+ 英文一行 30 px（600，灰 #4B5563，描边 3 px），居中，各一行不换行；
  每条开始前 0.1 s 显示、结束后 0.45 s 收掉，不和下一条重叠（build_timeline.py 里已按 display_windows 排好，并裁在各段之内）。
竖屏（1080 宽）：每条中文 ≤ 约 17 个字宽、英文 ≤ 约 60 字符，左右各留 ≥ 70 px——这里用真实字体量宽度，超了报出来。
位置：**底部偏上**——中文行中心 y = BAND_TOP + 33，英文行中心 y = BAND_TOP + 90（config.py：BAND_TOP = 1764；用户：“字幕放在屏幕底部偏上的位置，现在的字幕太高了”）。
SRT 时间 = 显示窗口，没有片头偏移（短视频不加悠一片头片尾）。字重用 fonts/NSC800.ttf、NSC600.ttf（族名 NSC800 / NSC600，libass 按族名取）。

**字号（用户 2026-10-04：“你看一下当前 /short-video 里面规定的字幕的字号，你同步修改一下当前视频的字幕”）**：技能规定中文 52 px + 英文 30 px 是 **CSS 的 font-size（em 大小）**，
但 ASS 的 Fontsize 不是 em——libass 按“行高”（字体的 winAscent + winDescent = Noto Sans SC 的 1.448 em）来缩放，写 Fontsize 52 实际只画出 52 / 1.458 ≈ 36 px 的字
（实测：同一串字 CSS 52 px 宽 1077 px，ASS Fontsize 52 画出来 739 px，比值 0.686；Fontsize 76 才是 1079 px）。所以 ASS 里要写 Fontsize = 标准字号 / 0.686（中文 76、英文 44），
画出来才和技能 HTML 引擎里的 52 / 30 px 一样大。第一版成片（写的是 52 / 30）实际只有标准的 68.6 %，已按这里改正。
（宽度检查仍然按 em 52 / 30 px 量——现在画出来的就是这个宽度，所以每条 ≤ 940 px 的检查才是真的。）
"""
import json
import sys

from PIL import ImageFont

import config as C

sys.path.insert(0, str(C.WAY_SCRIPTS))
from bilingual_std import esc_ass, ts_ass, write_srts  # noqa: E402

MAX_W = C.W - 140
LIBASS_EM = 0.686                                    # 实测：ASS Fontsize 画出来的字宽 / 同数值 CSS px 的字宽（Noto Sans SC 静态字重 NSC800 / NSC600，见上面）
ZH_ASS, EN_ASS = round(C.ZH_PX / LIBASS_EM), round(C.EN_PX / LIBASS_EM)       # 76、44


def bgr(rgb):
    return "&H00%02X%02X%02X" % (rgb[2], rgb[1], rgb[0])


def main():
    tl = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))
    cues = [c for p in tl["passages"] for c in p["cues"]]
    cues.sort(key=lambda c: c["a"])
    fz = ImageFont.truetype(str(C.FONTS / "NSC800.ttf"), C.ZH_PX)
    fe = ImageFont.truetype(str(C.FONTS / "NSC600.ttf"), C.EN_PX)
    bad, ev, rows = [], [], []
    for i, c in enumerate(cues):
        a, b = c["a"], c["b"]
        if i + 1 < len(cues):
            b = min(b, cues[i + 1]["a"] - 0.02)                  # 不叠（段与段交界处两边的窗口已经各自裁过）
        wz, we = fz.getlength(c["zh"]), fe.getlength(c["en"])
        if wz > MAX_W or we > MAX_W or not c["zh"].strip() or not c["en"].strip():
            bad.append(f"{c['id']}：中文 {wz:.0f} px、英文 {we:.0f} px（≤ {MAX_W}）")
        ev.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},ZH,,0,0,0,,{{\\an5\\pos({C.CX},{C.ZH_CY})}}{esc_ass(c['zh'])}")
        ev.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},EN,,0,0,0,,{{\\an5\\pos({C.CX},{C.EN_CY})}}{esc_ass(c['en'])}")
        rows.append((a, b, c["zh"], c["en"]))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {C.W}
PlayResY: {C.H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,NSC800,{ZH_ASS},{bgr(C.INK)},&H000000FF,{bgr(C.BG)},&H00000000,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1
Style: EN,NSC600,{EN_ASS},{bgr(C.EN_GREY)},&H000000FF,{bgr(C.BG)},&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (C.BUILD / "bilingual.ass").write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
    write_srts(str(C.EP / "成片"), rows)
    print(f"bilingual.ass：{len(cues)} 条；三份 SRT 已写到 {C.EP}（成片_双语字幕.srt 等）")
    print("超宽 / 空条：" + ("；".join(bad) if bad else "无"))
    for a, b, z, e in rows[:6]:
        print(f"  {a:7.2f}–{b:7.2f}  {z}  |  {e}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
