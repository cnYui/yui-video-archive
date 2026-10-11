"""Generate common/handdata.js (window.__HAND__) for the outro's handwriting (栏目标题、感谢语、签名).

The outro writes its headings / closing / signature stroke by stroke with the whiteboard engine's stroke data
(hanzi-writer-data medians, Arphic Public License; Latin from the EMS Tech single-line font, SIL OFL). To make any
closing line work without re-running this, the table holds all 3755 GB2312 level-1 characters + printable ASCII +
the CJK punctuation the engine draws by hand. A character that is still missing is drawn with Ma Shan Zheng
(the page never leaves a gap).

    python build_handdata.py            # -> common/handdata.js   (not in git: derived from the stroke data)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skill" / "yuanlai-ruci-episode" / "assets" / "engine-template"))
import hand_glyphs  # noqa: E402


def gb2312_level1():
    out = []
    for hi in range(0xB0, 0xD8):
        for lo in range(0xA1, 0xFF):
            try:
                out.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return "".join(out)


TEXTS = [gb2312_level1(), "".join(chr(c) for c in range(0x21, 0x7F)), "，。、：；！？（）“”《》—…·「」『』【】｜～",
         "悠鼓励谢献致"]
out = HERE / "common" / "handdata.js"
d = hand_glyphs.build_hand_js(TEXTS, out)
print(f"{out}: {len(d['cjk'])} 汉字, {len(d['punct'])} 标点, {len(d['lat']['g'])} 拉丁字符, {out.stat().st_size // 1024} KB"
      + (f"；缺 {len(d['missing'])} 个：{''.join(d['missing'][:40])}" if d["missing"] else ""))
