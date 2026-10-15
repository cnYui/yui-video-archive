"""录取仓库原始组件的隔离身份界面，虚构账号在画面和简介中标明。"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

EP=Path(__file__).resolve().parents[1]
MAT=EP.parents[1]/'素材/2026-10_CCBaga'
ENG=EP/'制作/00_整片'
with sync_playwright() as p:
    b=p.chromium.launch()
    page=b.new_page(viewport=dict(width=1500,height=1000),device_scale_factor=1)
    page.goto('http://127.0.0.1:5189/tests/identities.html')
    page.wait_for_function('window.identityFixture !== undefined')
    page.evaluate("window.identityFixture.language('zh')")
    page.get_by_text('fixture@example.invalid',exact=True).wait_for()
    page.wait_for_timeout(1500)
    panel=page.locator('#fixture > div').first
    panel.screenshot(path=str(MAT/'identity-preview.png'))
    page.goto((MAT/'CCBaga/docs/architecture.svg').as_uri())
    page.screenshot(path=str(MAT/'architecture.png'))
    b.close()
from PIL import Image
import shutil
dst=ENG/'media/pages/identity.png';dst.parent.mkdir(parents=True,exist_ok=True)
shutil.copy(MAT/'identity-preview.png',dst)
im=Image.open(dst)
path=ENG/'pages.json'
print('身份隔离预览',im.size)
# 页面素材共用同一套元信息，延续 capture_pages 的格式。
meta=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
meta['identity']=dict(src='pages/identity.png',w=im.width,h=im.height,url='github.com/liseami/CCBaga',bg='#faf9f5',marks={})
path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
(ENG/'pages.js').write_text('window.PG = '+json.dumps(meta,ensure_ascii=False)+';\n',encoding='utf-8')
