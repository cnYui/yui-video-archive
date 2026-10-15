# -*- coding: utf-8 -*-
"""版式检查：逐页量「logo 列 + 文字列」整体的左右边距、文字列高度、最长一行的字数，超限就标出来。
用法：python check_layout.py
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_frames import ENGINE, load_data, W, H  # noqa: E402

MIN_MARGIN = 150      # 左右至少留这么多
MAX_TEXT_H = 780      # 文字列最高（底部要给节拍条留位置）
MAX_LINE_W = 1000     # 每行最大渲染宽度（px），再长手机上就太挤


def main():
    data = load_data()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--font-render-hinting=none"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.add_init_script("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";")
        pg.goto(ENGINE.as_uri())
        pg.evaluate("window.__ready")
        rows = pg.evaluate("""() => slides.filter(s => s.kind === 'camp').map(s => {
            s.el.style.display = 'block';
            const tc = s.textCol, lc = s.logoCol;
            const tl = tc.offsetLeft, tw = tc.offsetWidth, th = tc.offsetHeight;
            const r = { name: s.c.name, left: lc.offsetLeft, right: tl + tw, tcw: tw, th: th, top: tc.offsetTop,
                        lines: s.lines.map(x => x.getBoundingClientRect().width).concat(s.chip ? [s.chip.getBoundingClientRect().width] : []), title_w: s.title.getBoundingClientRect().width };
            s.el.style.display = 'none';
            return r; })""")
        b.close()
    bad = 0
    print(f"{'阵营':8s} {'左边距':>6s} {'右边距':>6s} {'文字宽':>6s} {'文字高':>6s} {'最宽一行':>8s}")
    for r in rows:
        lm, rm = r["left"], W - r["right"]
        mx = max(r["lines"])
        flags = []
        if min(lm, rm) < MIN_MARGIN:
            flags.append("边距不足")
        if abs(lm - rm) > 6:
            flags.append("没居中")
        if r["th"] > MAX_TEXT_H:
            flags.append("文字列太高")
        if mx > MAX_LINE_W:
            flags.append("行太长")
        bad += bool(flags)
        print(f"{r['name']:8s} {lm:6.0f} {rm:6.0f} {r['tcw']:6.0f} {r['th']:6.0f} {mx:8.0f}   {' '.join(flags)}")
    print("有问题的页：", bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
