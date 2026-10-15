# -*- coding: utf-8 -*-
"""一次性补丁：capture_series_pages.py 的 MARK_JS 换成“拼接全部文字节点再映射回 Range”的版本（<em> / <strong> 把一句话切成几个节点也找得到），
并限制第 36 条那张图的高度。跑完可以删。"""
from pathlib import Path

p = Path(__file__).resolve().parent / "capture_series_pages.py"
s = p.read_text(encoding="utf-8")
a = s.index('MARK_JS = r"""')
b = s.index("H1_JS = ")
new_js = r'''MARK_JS = r"""
([needle, y0, y1]) => {
  // 把页面里所有文字节点按文档顺序拼成一个长串（1:1 替换撇号 / 引号 / 不换行空格，不改长度），在长串里找 needle，再映射回 Range。
  // 这样 <em> / <strong> / 链接把一句话切成几个节点也找得到。
  const f1 = s => s.replace(/[’‘]/g, "'").replace(/[“”]/g, '"').replace(/ /g, ' ').toLowerCase();
  const nl = f1(needle);
  const nodes = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n, full = '';
  while ((n = w.nextNode())) { nodes.push({n, s: full.length}); full += f1(n.textContent); }
  let from = 0;
  while (true) {
    const i = full.indexOf(nl, from);
    if (i < 0) break;
    from = i + 1;
    const e = i + nl.length;
    const a = nodes.findLast(x => x.s <= i), z = nodes.findLast(x => x.s < e);
    if (!a || !z) continue;
    const r = document.createRange();
    r.setStart(a.n, i - a.s); r.setEnd(z.n, e - z.s);
    const rects = [...r.getClientRects()].map(q => [q.left + window.scrollX, q.top + window.scrollY, q.width, q.height]).filter(q => q[2] > 2 && q[3] > 2);
    if (rects.length && rects[0][1] >= y0 - 2 && rects[0][1] <= y1) return {kind: 'range', rects};
  }
  // 回退：区域里最小的、文字包含 needle 的块元素
  const norm2 = s => f1(s.replace(/​/g, '').replace(/\s+/g, ' '));
  let best = null;
  for (const el of document.querySelectorAll('p,li,td,th,pre,code,h1,h2,h3,h4,div,a,span,blockquote,time')) {
    const t = norm2(el.textContent || '');
    if (!t.includes(nl)) continue;
    const r = el.getBoundingClientRect();
    const top = r.top + window.scrollY;
    if (r.width < 4 || r.height < 4 || top < y0 - 2 || top > y1) continue;
    if (!best || t.length < best.len) best = {len: t.length, rect: [r.left + window.scrollX, top, r.width, r.height]};
  }
  return best ? {kind: 'block', rects: [best.rect]} : null;
}
"""

'''
s = s[:a] + new_js + s[b:]
old = '''                    if n == 20:                                              # 20 条后面接 “Shorter lessons”
                        y1 = short_y - 8'''
assert old in s
s = s.replace(old, old + '''
                    if n == 36:                                              # 最后一条：只要这条本身（后面是订阅页脚 / 评论）
                        y1 = y0 + 760''')
p.write_text(s, encoding="utf-8")
print("patched", p)
