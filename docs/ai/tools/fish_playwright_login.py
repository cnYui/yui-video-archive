from pathlib import Path
from playwright.sync_api import sync_playwright


PROFILE = Path(r"C:\Users\yui\AppData\Local\fish-audio-playwright")
URL = "https://fish.audio/app/text-to-speech/"


with sync_playwright() as p:
    PROFILE.mkdir(parents=True, exist_ok=True)
    context = p.chromium.launch_persistent_context(
        str(PROFILE),
        headless=False,
        channel="chrome",
        viewport={"width": 1440, "height": 960},
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    print("Fish Audio 登录窗口已打开。请在窗口中完成登录；完成后回到终端按 Enter。", flush=True)
    input()
    print(f"当前页面：{page.url}", flush=True)
    print(f"持久化配置目录：{PROFILE}", flush=True)
    context.close()
