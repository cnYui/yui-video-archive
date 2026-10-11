# -*- coding: utf-8 -*-
"""把 Tavus-Griffin 那条（第一条叠放 dual 真成片）验证出来的 pageShot 两处改动合进技能模板的 scenes.js：
  1. pageShot 的 {lower: true}：页面录屏放在 dual 的下框（ovPageB2，layer 'b2'）
  2. 页面录屏底部中文译文条：叠放后框里的字缩到 0.57，横屏的 40 px / 高 100 读不清 → dual 用 56 px / 高 124（单框保持 40 / 100）
"""
from pathlib import Path

P = Path(r"D:\大疆\短视频\skill\short-video\assets\engine-template\scenes.js")
s = P.read_text(encoding="utf-8")
if "ovPageB2" in s:
    print("已经合过，不动")
    raise SystemExit

a = "const ovPage = (t0, t1, build) => OV.push({ t0, t1, build, fast: true });"
assert a in s
s = s.replace(a, a + "\nconst ovPageB2 = (t0, t1, build) => OV.push({ t0, t1, build, fast: true, layer: 'b2' });   // 页面录屏放在 dual 的下框（pageShot 的 {lower: true}）", 1)

a = "{start: 起始滚动位置（图片像素）, pad: 比最后一句再多留的秒数})"
assert a in s
s = s.replace(a, "{start: 起始滚动位置（图片像素）, pad: 比最后一句再多留的秒数, lower: true = 放在 dual 的下框})", 1)

a = "  ovPage(t0, t1, p => {"
assert s.count(a) == 1
s = s.replace(a, "  (opt.lower ? ovPageB2 : ovPage)(t0, t1, p => {", 1)

old = "height: 100, background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: \"800 40px 'Noto Sans SC'\", padding: '0 36px',"
assert old in s
new = ("height: ZB[0], background: 'rgba(27,27,31,.93)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', font: `800 ${ZB[1]}px 'Noto Sans SC'`, padding: `0 ${ZB[2]}px`,")
s = s.replace(old, new, 1)

a = "    const VW = 1474, VH = 829 - PAGE_BAR, k = VW / m.w, IH = m.h * k, PADB = 200;"
assert a in s
s = s.replace(a, a + "\n    const ZB = TL.layout === 'dual' ? [124, 56, 30] : [100, 40, 36];     // 底部中文译文条：[高, 字号, 左右内边距]；dual 的框缩到 0.57，字要大一档才读得清", 1)
P.write_text(s, encoding="utf-8")
print("scenes.js 已合：ovPageB2 / lower / 译文条按版式取字号")
