# -*- coding: utf-8 -*-
"""临时测试：双横屏版式（两框叠在一起、字幕在下）用真引擎 CSS 摆出来对不对。"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
scr = HERE / "media" / "scr"
f1 = sorted(scr.glob("H1_0_000*.jpg"))[60]
f2 = sorted(scr.glob("M1_1_001*.jpg"))[20]
JS = r"""
([a, b]) => {
  document.body.classList.add('dual');
  document.getElementById('ovB').style.display = 'none';
  const i1 = document.getElementById('scrimg'), i2 = document.getElementById('scrimg2');
  i1.src = 'file:///' + a.replace(/\\/g, '/'); i2.src = 'file:///' + b.replace(/\\/g, '/');
  i1.style.visibility = 'visible'; i2.style.visibility = 'visible';
  document.getElementById('demo').dataset.tag = '@neilsonks · X（原帖）';
}
"""
POS = r"""() => ['demo', 'demo2', 'subs'].map(id => { const e = document.getElementById(id).getBoundingClientRect(); return [id, Math.round(e.left), Math.round(e.top), Math.round(e.right), Math.round(e.bottom)]; })"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 2340})
    pg.goto((HERE / "index.html").as_uri())
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.evaluate("t => renderAt(t)", 21.0)
    pg.evaluate(JS, [str(f1), str(f2)])
    pg.wait_for_timeout(700)
    print(pg.evaluate(POS))
    pg.screenshot(path=r"C:\Users\yui\AppData\Local\Temp\claude\D----\93a5cccf-5549-4abd-bafd-dfe7d18e128f\scratchpad\fr\dual_test.png")
    b.close()
