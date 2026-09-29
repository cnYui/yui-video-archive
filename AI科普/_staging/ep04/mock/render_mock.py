# -*- coding: utf-8 -*-
"""把 tier_mock.html 按 mock_data.json 里的几组数据截成 2340×1080 静帧（样张，只看版面）。"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / (sys.argv[1] if len(sys.argv) > 1 else "mock_data.json")).read_text(encoding="utf-8"))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 2340, "height": 1080})
    for name, mock in data.items():
        pg.add_init_script(f"window.MOCK = {json.dumps(mock, ensure_ascii=False)};")
        pg.goto((HERE / "tier_mock.html").as_uri())
        pg.wait_for_timeout(600)
        pg.evaluate("document.fonts.ready")
        out = HERE / f"{name}.png"
        pg.screenshot(path=str(out))
        print(out)
        pg.close(); pg = b.new_page(viewport={"width": 2340, "height": 1080})
    b.close()
