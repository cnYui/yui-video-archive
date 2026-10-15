# -*- coding: utf-8 -*-
"""封面：16:9（1920×1080）和 4:3（1440×1080），白底，不用人像：大字“300字 / 管得住AI吗？” + 右边一张“四层要求”的文件卡。

  python make_cover.py            → 封面_A_16x9.png、封面_A_4x3.png、封面_B_16x9.png、封面_B_4x3.png
A = 300字 + 文件卡；B = 六位签字人的名字条 + “300字协议”。
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent

CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
:root { --ink:#1B1B1F; --gray:#6B7280; --orange:#FF4F1A; --marker:#FFD84D; }
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:%(W)spx; height:1080px; background:#fff; overflow:hidden; font-family:'Noto Sans SC', sans-serif; color:var(--ink); }
.abs { position:absolute; }
.kick { font:800 34px 'Noto Sans SC'; letter-spacing:.22em; color:var(--orange); }
.big { font-family:'Space Grotesk','Noto Sans SC'; font-weight:800; line-height:1; letter-spacing:-.02em; }
.mark { background:linear-gradient(transparent 62%%, var(--marker) 62%%, var(--marker) 94%%, transparent 94%%); }
.banner { background:var(--ink); color:#fff; border-radius:28px; font:900 %(BQ)spx/1.2 'Noto Sans SC'; padding:.22em .6em; white-space:nowrap; box-shadow:0 18px 40px rgba(0,0,0,.22); display:inline-block; }
.banner em { font-style:normal; color:var(--marker); }
.doc { background:#fff; border:3px solid #E5E7EB; border-radius:26px; box-shadow:0 30px 70px rgba(0,0,0,.2); padding:34px 38px; transform:rotate(-3.5deg); }
.doc .ti { font:800 34px 'Noto Sans SC'; color:var(--gray); margin-bottom:22px; white-space:nowrap; }
.layer { display:flex; align-items:center; gap:22px; height:118px; border-radius:18px; border:4px solid; margin-top:16px; padding:0 26px; background:#fff; font:800 46px 'Noto Sans SC'; white-space:nowrap; }
.layer i { flex:none; width:68px; height:68px; border-radius:14px; color:#fff; display:flex; align-items:center; justify-content:center; font:800 40px 'Space Grotesk'; font-style:normal; }
.l1 { border-color:#E11D48; } .l1 i { background:#E11D48; }
.l2 { border-color:#F59E0B; } .l2 i { background:#F59E0B; }
.l3 { border-color:#2563EB; } .l3 i { background:#2563EB; }
.l4 { border-color:#16A34A; } .l4 i { background:#16A34A; }
.stamp { border:9px solid #E11D48; color:#E11D48; border-radius:18px; font:900 74px 'Noto Sans SC'; letter-spacing:.08em; padding:6px 30px; background:rgba(255,255,255,.7); transform:rotate(-9deg); white-space:nowrap; }
.chip { display:inline-block; padding:8px 24px; border:4px solid var(--ink); border-radius:999px; font:800 38px 'Noto Sans SC'; margin:0 12px 14px 0; background:#fff; white-space:nowrap; }
.chip small { font:600 .66em 'Noto Sans SC'; color:var(--gray); margin-left:10px; }
</style>
"""

DOC = """
<div class="doc abs" style="left:%(DX)spx; top:%(DY)spx; width:%(DW)spx;">
  <div class="ti" style="font-size:%(TI)spx">《白宫超级智能协议》· 一页正文</div>
  <div class="layer l1"><i>1</i>内部控制</div>
  <div class="layer l2"><i>2</i>内部团队</div>
  <div class="layer l3"><i>3</i>外部审计</div>
  <div class="layer l4"><i>4</i>董事会委员会</div>
</div>
<div class="stamp abs" style="left:%(SX)spx; top:%(SY)spx;">没写处罚</div>
"""


def cover_a(w):
    if w == 1920:
        p = dict(W=1920, BQ=104, DX=1130, DY=150, DW=720, SX=1290, SY=770, TI=34)
        left = f"""
<div class="kick abs" style="left:96px; top:92px;">白宫 · 2026.9.29</div>
<div class="big abs" style="left:84px; top:170px; font-size:370px;"><span class="mark">300</span><span style="font-size:250px">字</span></div>
<div class="abs" style="left:96px; top:600px; font:900 96px/1.15 'Noto Sans SC';">《超级智能协议》</div>
<div class="abs" style="left:96px; top:790px;"><span class="banner">管得住 <em>AI</em> 吗？</span></div>"""
    else:
        # 4:3：左列是大字 + 标题 + 横幅，右列是缩小的文件卡，互相不压
        p = dict(W=1440, BQ=92, DX=860, DY=110, DW=520, SX=870, SY=800, TI=25)
        left = f"""
<div class="kick abs" style="left:90px; top:70px;">白宫 · 2026.9.29</div>
<div class="big abs" style="left:70px; top:130px; font-size:270px;"><span class="mark">300</span><span style="font-size:190px">字</span></div>
<div class="abs" style="left:90px; top:470px; font:900 78px/1.15 'Noto Sans SC';">《超级智能协议》</div>
<div class="abs" style="left:90px; top:760px;"><span class="banner" style="font-size:88px">管得住 <em>AI</em> 吗？</span></div>"""
    return CSS % p + left + DOC % p


def cover_b(w):
    names = [("皮查伊", "谷歌"), ("阿莫迪", "Anthropic"), ("扎克伯格", "Meta"), ("布罗克曼", "OpenAI"), ("马斯克", "xAI"), ("黄仁勋", "英伟达")]
    chips = "".join(f'<span class="chip">{n}<small>{c}</small></span>' for n, c in names)
    if w == 1920:
        p = dict(W=1920, BQ=96, DX=0, DY=0, DW=0, SX=0, SY=0, TI=34)
        body = f"""
<div class="kick abs" style="left:96px; top:92px;">六位大佬 · 一页纸</div>
<div class="big abs" style="left:84px; top:130px; font-size:400px;"><span class="mark">300</span><span style="font-size:280px">字</span></div>
<div class="stamp abs" style="left:1260px; top:230px; font-size:84px; transform:rotate(-8deg);">6 位签字</div>
<div class="abs" style="left:96px; top:520px; font:900 128px/1.1 'Noto Sans SC';">白宫联署协议</div>
<div class="abs" style="left:96px; top:700px; width:1700px;">{chips}</div>
<div class="abs" style="left:96px; top:870px;"><span class="banner">管得住 <em>AI</em> 吗？</span></div>"""
    else:
        p = dict(W=1440, BQ=88, DX=0, DY=0, DW=0, SX=0, SY=0, TI=34)
        body = f"""
<div class="kick abs" style="left:90px; top:80px;">六位大佬 · 一页纸</div>
<div class="big abs" style="left:70px; top:130px; font-size:330px;"><span class="mark">300</span><span style="font-size:230px">字</span></div>
<div class="abs" style="left:90px; top:500px; font:900 118px/1.1 'Noto Sans SC';">白宫联署协议</div>
<div class="abs" style="left:90px; top:670px; width:1300px;">{chips}</div>
<div class="abs" style="left:90px; top:900px;"><span class="banner">管得住 <em>AI</em> 吗？</span></div>"""
    return CSS % p + body


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for tag, fn in (("A", cover_a), ("B", cover_b)):
            for w, name in ((1920, "16x9"), (1440, "4x3")):
                pg = b.new_page(viewport={"width": w, "height": 1080})
                pg.set_content("<!doctype html><html><head><meta charset='utf-8'></head><body>" + fn(w) + "</body></html>")
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(600)
                out = HERE / f"封面_{tag}_{name}.png"
                pg.screenshot(path=str(out))
                print("->", out.name)
                pg.close()
        b.close()


if __name__ == "__main__":
    main()
