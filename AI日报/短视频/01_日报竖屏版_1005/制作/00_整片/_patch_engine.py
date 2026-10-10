p = "engine.js"
s = open(p, encoding="utf-8").read()
a = s.index("  // ---------------------------------------------------------------- 一次性的字宽适配")
b = s.index("  const imgs = Array.from(document.images);")
new = '''  // ---------------------------------------------------------------- 一次性的字宽适配（字体加载后）；用文字范围量真实宽度（块级元素的 scrollWidth 至少是容器宽）
  function textW(node) { const r = document.createRange(); r.selectNodeContents(node); return r.getBoundingClientRect().width; }
  function shrinkFont(node, maxW, min, what) {                 // 改 font-size（标题：里面没有别的字号）
    let k = 1; const base = parseFloat(getComputedStyle(node).fontSize);
    while (textW(node) > maxW && k > min) { k -= 0.03; node.style.fontSize = (base * k).toFixed(2) + 'px'; }
    if (k < 1) window.__WARN.push(`${what} 缩到 ${(k * 100).toFixed(0)}%`);
  }
  function shrinkZoom(node, maxW, min, what) {                 // 改 zoom（数字卡：数字里还套着单位小字）
    let k = 1;
    while (textW(node) > maxW && k > min) { k -= 0.03; node.style.zoom = k.toFixed(2); }
    if (k < 1) window.__WARN.push(`${what} 缩到 ${(k * 100).toFixed(0)}%`);
  }
  function fitAll() {
    S.forEach(o => {
      shrinkFont(o.head.querySelector('.t1'), 960, 0.6, `${o.sc.id} t1`);
      shrinkFont(o.head.querySelector('.t2'), 960, 0.6, `${o.sc.id} t2`);
      o.chips.forEach((c, i) => { let k = 1, base = parseFloat(getComputedStyle(c).fontSize); while (c.scrollWidth > c.clientWidth + 1 && k > 0.7) { k -= 0.03; c.style.fontSize = (base * k).toFixed(2) + 'px'; } if (k < 1) window.__WARN.push(`${o.sc.id} 要点${i + 1} 缩到 ${(k * 100).toFixed(0)}%`); });
      o.bigs.forEach(({ b, e }) => { shrinkZoom(e.querySelector('.n'), 680, 0.5, `${o.sc.id} 数字 ${b.n}`); shrinkZoom(e.querySelector('.d'), 680, 0.55, `${o.sc.id} 说明 ${b.d}`); });
    });
  }
'''
s = s[:a] + new + s[b:]
s = s.replace("日报的待宿呼吸", "日报的待机呼吸")
open(p, "w", encoding="utf-8").write(s)
print("ok")
