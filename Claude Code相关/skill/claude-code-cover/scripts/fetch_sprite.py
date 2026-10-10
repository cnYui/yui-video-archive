# -*- coding: utf-8 -*-
"""从 claude.dev 官方教程页的前端代码里取出 Claude 像素宇航员的原始像素表，存成 assets/sprite_official.dat（JSON）。

  python fetch_sprite.py [--url URL]

背景（2026-10-02 查到的）：页面底部的宇航员不是图片，是前端代码里的一张 40×33 像素表（canvas 逐格画的）：
  n({w:40, h:33, fps:12, palette:["#141413","#bf684c","#d97757","#d1cfc4","#f5db9a","#faf9f4"], base:"…1320 个字符…", deltas:[130 帧补丁…]})
  调色板下标：0 深色（眼睛）  1 深橙 #bf684c（阴影）  2 品牌橙 #d97757（身体）  3 浅灰 #d1cfc4（头盔环、领口）  4 淡黄 #f5db9a（小星光）  5 白 #faf9f4（头盔高光）
  base = 没戴头盔的 Claude Code 小怪物：头 16×4（眼睛是 2×2 的深色格）、中间一条 24 宽的“手臂带”（rows 21–24）、躯干 16×4、四条腿（2 宽、4 高）；
  deltas = 130 帧，每帧是对上一帧的补丁（“格子序号(36 进制 2 位) + 新值”，逗号分隔；序号 = y*40+x，值 '.' = 透明）：
  头盔飞来扣上 → 漂浮摇摆、拖着腿、冒小星光 → 头盔飞走，又回到 base。
这个文件是 Anthropic 的美术数据，.dat 不在公开仓库的白名单里（不会被提交）；丢了就重跑本脚本。
找不到时（官方改版、变量名变了）：在页面加载的所有脚本里搜 `palette:["#141413","#bf684c","#d97757"`，改下面的正则。
"""
import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "assets" / "sprite_official.dat"
URL = "https://claude.dev/blog/getting-started-with-claude-code-mods/"
PAT = re.compile(r'n\(\{w:(\d+),h:(\d+),fps:(\d+),palette:\[((?:"#[0-9a-f]{6}",?)+)\],base:"([^"]*)",deltas:\[')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=URL)
    a = ap.parse_args()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        pg = ctx.new_page()
        urls = []
        pg.on("response", lambda r: urls.append(r.url) if r.request.resource_type == "script" else None)
        pg.goto(a.url, wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(1500)
        found = None
        for u in urls:
            try:
                body = ctx.request.get(u, timeout=30000).text()
            except Exception:
                continue
            for m in PAT.finditer(body):
                pal = re.findall(r'"(#[0-9a-f]{6})"', m.group(4))
                if "#d97757" in pal and int(m.group(1)) == 40:
                    # deltas 数组：从 "deltas:[" 往后配对方括号
                    start = m.end() - 1
                    depth = 0
                    for j in range(start, len(body)):
                        if body[j] == "[":
                            depth += 1
                        elif body[j] == "]":
                            depth -= 1
                            if depth == 0:
                                break
                    found = dict(w=int(m.group(1)), h=int(m.group(2)), fps=int(m.group(3)), palette=pal, base=m.group(5),
                                 deltas=json.loads(body[start:j + 1]), script=u.split("/")[-1], source="claude.dev 前端代码（2026-10-02 取）")
                    break
            if found:
                break
        b.close()
    if not found:
        raise SystemExit("没找到宇航员的像素表：官方改版了，见本文件开头的说明")
    OUT.write_text(json.dumps(found, ensure_ascii=False), encoding="utf-8")
    print(f"-> {OUT}  {found['w']}×{found['h']}，调色板 {found['palette']}，{len(found['deltas'])} 帧，来自 {found['script']}")


if __name__ == "__main__":
    main()
