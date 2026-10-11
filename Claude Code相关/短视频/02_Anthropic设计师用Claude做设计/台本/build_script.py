# -*- coding: utf-8 -*-
"""plan.py → 录制稿.json（曼波 TTS 的每一块 = 一句同传）+ 台本.md（中英并排给人读），并用真实字体量每条字幕的宽度。

  python build_script.py

竖屏 1080 宽，字幕 52 px / 30 px（项目双语标准），左右各留 70 px → 每条最宽 940 px（中文约 17 个字宽、英文约 60 字符）。超了就报出来，回 plan.py 改。
TTS 时长这里只是粗估（中文每字 ≈ 0.16 s、英文词 ≈ 0.28 s、标点 ≈ 0.1 s），真实时长以导出后的 wav 为准（制作/02_配音/build_voice.py）。
"""
import json
import re
import sys
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parent
FONTS = EP / "制作" / "00_整片" / "fonts"
sys.path.insert(0, str(HERE))
import plan  # noqa: E402

ZH_PX, EN_PX = 52, 30
MAX_W = 940


def join_say(parts):
    """字幕各条拼成念的字：英文词和后面的汉字之间补一个空格（“Claude Design 做自己的项目”），免得 TTS 把 “Design做” 读连。"""
    out = parts[0]
    for p in parts[1:]:
        if re.search(r"[A-Za-z0-9]$", out) and re.match(r"[一-鿿]", p):
            out += " "
        out += p
    return out


def est_tts(s):
    cjk = len(re.findall(r"[一-鿿]", s))
    words = len(re.findall(r"[A-Za-z][A-Za-z\-']*", s))
    punct = len(re.findall(r"[，。！？；：、]", s))
    return cjk * 0.16 + words * 0.28 + punct * 0.10


def main():
    fz = ImageFont.truetype(str(FONTS / "NSC800.ttf"), ZH_PX)
    fe = ImageFont.truetype(str(FONTS / "NSC600.ttf"), EN_PX)
    lines, bad, md = [], [], ["# 台本（中英并排）", "",
                              f"标题：{plan.TITLE[0]} / {plan.TITLE[1]}；来源角标：{plan.BADGE}", "",
                              "| 块 | 段 | 原片 t0 | 同传（say） | 中文字幕 | 英文字幕 | 宽度 px（中 / 英） | 估时 s |", "|---|---|---|---|---|---|---|---|"]
    total_est = 0.0
    for p in plan.PASSAGES:
        for k, s in enumerate(p["sentences"]):
            assert len(s["zh"]) == len(s["en"]), f"{p['id']} 第 {k + 1} 句：中文 {len(s['zh'])} 条、英文 {len(s['en'])} 条，要一一对应"
            bid = f"{p['id']}{chr(ord('a') + k)}"
            say = join_say(s["zh"])
            est = est_tts(say)
            total_est += est
            lines.append({"id": bid, "passage": p["id"], "say": say, "zh": s["zh"], "en": s["en"], "own": bool(s.get("own"))})
            for j, (z, e) in enumerate(zip(s["zh"], s["en"])):
                wz, we = fz.getlength(z), fe.getlength(e)
                flag = " ⚠" if wz > MAX_W or we > MAX_W else ""
                if flag:
                    bad.append(f"{bid}.{j + 1}：中文 {wz:.0f} px、英文 {we:.0f} px（≤ {MAX_W}）  {z} | {e}")
                md.append(f"| {bid}.{j + 1} | {p['id']} | {s['t0']:.2f} | {say if j == 0 else ''} | {z} | {e} | {wz:.0f} / {we:.0f}{flag} | {format(est, '.1f') if j == 0 else ''} |")
    (HERE / "录制稿.json").write_text(json.dumps({"title": plan.TITLE, "lines": lines}, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "台本.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    nchar = sum(len(re.findall(r"[一-鿿]", l["say"])) for l in lines)
    print(f"{len(plan.PASSAGES)} 段，{len(lines)} 块同传，{sum(len(l['zh']) for l in lines)} 条字幕，汉字 {nchar} 个，TTS 粗估共 {total_est:.0f} s")
    print("超宽：" + ("\n  " + "\n  ".join(bad) if bad else "无"))


if __name__ == "__main__":
    main()
