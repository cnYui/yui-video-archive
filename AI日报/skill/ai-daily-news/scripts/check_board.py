"""白板版自查：打开 制作/engine/index.html（带 timeline.json），列出场景淡出时还没写完的手写字（ENG.handLate）和页面报错。

    python check_board.py <期目录>

退出码：0 = 干净；1 = 有没写完的字或页面报错（清单印在下面）。没写完一般是这句的时间窗太短：
把那条的标题 / 要点改短一点，或者看 scenes.board.js 里那一处的 until / vmax。深色卡片版（style = news）直接跳过。
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ep = Path(sys.argv[1]).resolve()
    tl = json.loads((ep / "制作" / "timeline.json").read_text(encoding="utf-8"))
    if (tl.get("episode") or {}).get("style") != "board":
        print("深色卡片版，不用查")
        return
    html = ep / "制作" / "engine" / "index.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 2340, "height": 1080})
        msgs = []
        pg.on("console", lambda m: m.type == "error" and msgs.append(m.text))
        pg.on("pageerror", lambda e: msgs.append(str(e)))
        pg.add_init_script("window.__CAPTURE__ = true; window.__DATA__ = " + json.dumps(tl, ensure_ascii=False) + ";")
        pg.goto(html.as_uri())
        pg.wait_for_function("window.__READY__ === true", timeout=30000)
        late = pg.evaluate("ENG.handLate || []")
        b.close()
    for x in late:
        print(f"没写完：{x['scene']}「{x['text']}」写到 {x['end']} s，场景 {x['sceneEnd']} s 就淡出了")
    for m in msgs:
        print("页面报错：" + m)
    print("白板自查：" + ("干净" if not late and not msgs else f"{len(late)} 处没写完，{len(msgs)} 条报错"))
    sys.exit(1 if late or msgs else 0)


if __name__ == "__main__":
    main()
