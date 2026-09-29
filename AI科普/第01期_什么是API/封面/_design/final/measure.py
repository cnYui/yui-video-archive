"""Print the on-screen bounds of the cover's key elements (after rotation), plus text overflow.

usage: python measure.py <cover.html> [data.json]
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

JS = r"""
() => {
  const out = {};
  const box = (el) => { const r = el.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  // ink-ish bounds of text: use a Range over the element's contents
  const tbox = (el) => { const rg = document.createRange(); rg.selectNodeContents(el); const r = rg.getBoundingClientRect();
                         return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  for (const id of ['receipt', 'content', 'ryo', 'qmark', 'sub', 't1', 't2', 'dash']) {
    const el = document.getElementById(id); if (!el) continue; out[id] = box(el);
  }
  for (const id of ['t1', 't2', 'sub']) out[id + '_text'] = tbox(document.getElementById(id));
  const c = document.getElementById('content');
  out.content_inner_w = c.clientWidth;
  for (const id of ['t1', 't2', 'sub']) { const el = document.getElementById(id); out[id + '_scrollW'] = el.scrollWidth; }
  out.fonts = [...document.fonts].map(f => f.family + ':' + f.status);
  return out;
}
"""


def main():
    html = Path(sys.argv[1]).resolve()
    data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv) > 2 else None
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text", "--font-render-hinting=none"])
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        if data is not None:
            pg.add_init_script(f"window.__DATA__ = {json.dumps(data, ensure_ascii=False)};")
        pg.goto(html.as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready.then(() => true)")
        for k, v in pg.evaluate(JS).items():
            print(f"{k:16s} {v}")
        b.close()


if __name__ == "__main__":
    main()
