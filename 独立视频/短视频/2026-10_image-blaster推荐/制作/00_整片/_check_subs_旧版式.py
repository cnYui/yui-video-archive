# -*- coding: utf-8 -*-
"""竖屏版式自检：用页面里真实的字体 / 样式，量每条字幕和标题的实际宽度。检查：
- 字幕：中文、英文各一行（行高 66 / 40 没变），左右各留 ≥ 70 px（1080 宽），英文 ≤ 64 字符；
- 标题：kicker / 第一行 / 第二行各一行、不超出 1000 px；
- 上框下沿在字幕上面（≤ 1195 − 20）；双分镜时下框上沿在字幕下面（≥ 1195 + 110）。
渲染前跑一遍（build_timeline.py 之后、prep_frames.py 之前就可以跑）：

  python check_subs.py
"""
import sys

from playwright.sync_api import sync_playwright

from render_all import open_page

W, MARGIN, SUB_TOP = 1080, 70, 1195
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
  const head = ['kicker', 't1', 't2'].map(id => { const e = document.getElementById(id); return {id, w: Math.round(width(e)), h: Math.round(e.getBoundingClientRect().height), text: e.textContent}; });
  const d = document.getElementById('demo').getBoundingClientRect(), d2 = document.getElementById('demo2').getBoundingClientRect();
  return {subs: res, head, demo: [d.left, d.top, d.right, d.bottom].map(Math.round), demo2: TL.layout === 'dual' ? [d2.left, d2.top, d2.right, d2.bottom].map(Math.round) : null};
}
"""
LINE_H = {"kicker": 44, "t1": 93, "t2": 75}     # 一行时的高度（字号 × 行高，取整后的大约值，多一行就会翻倍）


def main():
    with sync_playwright() as p:
        browser, page, errors = open_page(p)
        r = page.evaluate(JS)
        errors = errors + page.evaluate("window.__ERR")
        browser.close()
    errors = [e for e in errors if "ERR_FILE_NOT_FOUND" not in e]      # 抽帧（prep_frames.py）之前帧文件还不存在，不算报错
    subs = r["subs"]
    zmax = max(subs, key=lambda x: x["zw"])
    emax = max(subs, key=lambda x: x["ew"])
    probs = []
    for x in subs:
        if x["zh"] != 66 or x["eh"] != 40:
            probs.append(f"{x['id']} 不是一行（中文行高 {x['zh']}、英文行高 {x['eh']}）")
        if (W - x["zw"]) / 2 < MARGIN or (W - x["ew"]) / 2 < MARGIN:
            probs.append(f"{x['id']} 太宽（中文 {x['zw']} px、英文 {x['ew']} px，左右要各留 {MARGIN} px）")
        if x["el"] > 64:
            probs.append(f"{x['id']} 英文 {x['el']} 字符 > 64")
    for h in r["head"]:
        if h["text"] and (h["w"] > 1000 or h["h"] > LINE_H[h["id"]] * 1.5):
            probs.append(f"标题 {h['id']}「{h['text']}」不是一行或太宽（{h['w']} px，高 {h['h']}）")
    if not r["head"][1]["text"]:
        probs.append("没有标题第一行（录制稿.json 的 hook）")
    d = r["demo"]
    if d[3] > SUB_TOP - 20:
        probs.append(f"上框下沿 {d[3]} 压到字幕（≤ {SUB_TOP - 20}）")
    d2 = r["demo2"]
    if d2 and d2[1] < SUB_TOP + 110:
        probs.append(f"下框上沿 {d2[1]} 压到字幕（≥ {SUB_TOP + 110}）")
    print(f"{len(subs)} 条字幕；中文最宽 {zmax['zw']} px（{zmax['id']}，{zmax['zl']} 字），英文最宽 {emax['ew']} px（{emax['id']}，{emax['el']} 字符）；"
          f"标题 {' / '.join(str(h['w']) + ' px' for h in r['head'])}；上框 {d}，下框 {d2 or '无（单框）'}；{'没问题' if not probs else '；'.join(probs)}；页面报错 {errors or '无'}")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
