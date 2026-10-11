# -*- coding: utf-8 -*-
"""字幕版式自检（项目的中英双语标准）：用页面里真实的字体 / 样式，对每条字幕量中文行、英文行的实际宽度，
检查：各一行（行高没变）、不超出画面（左右各留 ≥ 100 px）、中文 ≤ 约 28 字 × 52 px、英文 ≤ 约 90 字符；再量演示区下沿（必须 ≤ 字幕带 y 922 − 10）。

  python check_subs.py [V1 V2 …]        不带参数 = 全部
"""
import sys

from render_all import open_page
from common import all_eps, out_dir  # noqa: F401
from playwright.sync_api import sync_playwright

JS = """
() => {
  const zh = document.getElementById('subZh'), en = document.getElementById('subEn');
  const width = el => { const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect().width; };
  const res = [];
  for (const c of TL.subs) {
    zh.textContent = ''; zh.style.opacity = 1; en.style.opacity = 1;
    if (c.who) { const w = document.createElement('span'); w.className = 'w'; w.textContent = c.who; zh.appendChild(w); }
    zh.appendChild(document.createTextNode(c.zh)); en.textContent = c.en;
    res.push({id: c.id + '.' + c.k, zw: Math.round(width(zh)), ew: Math.round(width(en)), zh: Math.round(zh.getBoundingClientRect().height), eh: Math.round(en.getBoundingClientRect().height), zl: c.zh.length, el: c.en.length});
  }
  const d = document.getElementById('demo').getBoundingClientRect(), t = document.getElementById('toc').getBoundingClientRect();
  return {subs: res, demo: [d.left, d.top, d.right, d.bottom].map(Math.round), toc: [t.left, t.top, t.right, t.bottom].map(Math.round)};
}
"""


def main():
    eps = sys.argv[1:] or all_eps()
    bad = 0
    with sync_playwright() as p:
        for ep in eps:
            browser, page, errors = open_page(p, ep)
            r = page.evaluate(JS)
            browser.close()
            subs = r["subs"]
            zmax = max(subs, key=lambda x: x["zw"])
            emax = max(subs, key=lambda x: x["ew"])
            probs = []
            for x in subs:
                if x["zh"] != 66 or x["eh"] != 40:
                    probs.append(f"{x['id']} 不是一行（中文行高 {x['zh']}、英文行高 {x['eh']}）")
                if (2340 - x["zw"]) / 2 < 100 or (2340 - x["ew"]) / 2 < 100:
                    probs.append(f"{x['id']} 太宽（中文 {x['zw']} px、英文 {x['ew']} px）")
                if x["el"] > 94:
                    probs.append(f"{x['id']} 英文 {x['el']} 字符 > 94")
            d = r["demo"]
            if d[3] > 922 - 10:
                probs.append(f"演示区下沿 {d[3]} 压到字幕带（≤ {922 - 10}）")
            print(f"{ep}: {len(subs)} 条字幕；中文最宽 {zmax['zw']} px（{zmax['id']}，{zmax['zl']} 字），英文最宽 {emax['ew']} px（{emax['id']}，{emax['el']} 字符）；"
                  f"演示区 {d}，左栏 {r['toc']}；{'没问题' if not probs else '；'.join(probs)}；页面报错 {errors or '无'}")
            bad += len(probs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
