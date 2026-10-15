# -*- coding: utf-8 -*-
"""做“原帖节选卡”：推文嵌入页会把长推文截断（Show more），关键句露不出来，x.com 又要登录——所以用接口取到的完整原文自己排一张引用卡，
卡上写明账号、北京时间、“原帖节选”，节选处用 …… 标出，原文一个字不改。再由 capture_pages.py 截成长图、算高亮位置（SPECS 里的 Q_ 开头）。

  python make_quotes.py        生成 quotes/Q_ayi.html、quotes/Q_lw.html
"""
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import MAT

HERE = Path(__file__).resolve().parent
OUT = HERE / "quotes"
RAW = MAT / "2026-10_Claude封号潮"
BJ = timezone(timedelta(hours=8))

CSS = """
html,body{margin:0;padding:0;width:800px;background:#EEF1F5;font-family:'Noto Sans SC',sans-serif;color:#141413}
.wrap{padding:26px 24px 30px}
.card{background:#fff;border-radius:22px;border:2px solid #D5DBE3;padding:26px 30px 24px}
.hd{display:flex;align-items:center;gap:14px}
.av{flex:none;width:54px;height:54px;border-radius:50%;background:#141413;color:#FFD84D;font:900 28px/54px 'Noto Sans SC';text-align:center}
.nm b{font:800 23px 'Noto Sans SC'}
.nm span{display:block;font:500 16px 'Noto Sans SC';color:#6B7280;margin-top:2px}
.tag{margin-left:auto;font:800 15px 'Noto Sans SC';color:#374151;background:#FFD84D;border-radius:999px;padding:4px 14px;white-space:nowrap}
.body p{font:500 23px/1.68 'Noto Sans SC';margin:18px 0 0}
.body p.ell{color:#9AA1AC;font-size:22px;margin-top:6px}
.ft{margin-top:22px;padding-top:14px;border-top:2px solid #E5E7EB;font:600 15px 'JetBrains Mono','Noto Sans SC';color:#6B7280;word-break:break-all}
"""


def card(initial, name, sub, tag, paras, footer):
    body = "".join(f'<p class="ell">……</p>' if p == "…" else f"<p>{html.escape(p)}</p>" for p in paras)
    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css"><style>{CSS}</style></head><body><div class="wrap"><div class="card">
<div class="hd"><div class="av">{initial}</div><div class="nm"><b>{html.escape(name)}</b><span>{html.escape(sub)}</span></div><div class="tag">{html.escape(tag)}</div></div>
<div class="body">{body}</div>
<div class="ft">{html.escape(footer)}</div></div></div></body></html>"""


def tw(path):
    t = json.loads(path.read_text(encoding="utf-8"))["tweet"]
    when = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y").astimezone(BJ).strftime("%Y-%m-%d %H:%M")
    return t["text"], when


def main():
    OUT.mkdir(exist_ok=True)
    # AYi 的长推文（10-04）
    text, when = tw(RAW / "longtweet_fxtwitter.json")
    flat = "".join(ch for ch in text.replace("\n", "")).replace("， ", "，")
    e1 = "国庆这几天 Claude 的封号潮来得极其凶猛，群里不少用了两年的老号、刚充了 Max 的开发者账号全被一锅端，哀鸿遍野。"
    e2 = "官方风控本质上是一套多维交叉打分系统， 上半年官方封禁了整整 1140 万个账号，申诉推翻率只有可怜的十分之一，真正要命的根本不是说中文或者 IP 纯不纯，而是时区撕裂、WebRTC 泄漏以及终端命令行里残留的系统代理。"
    for e in (e1, e2):
        assert " ".join(e.split()).replace("， ", "，") in " ".join(flat.split()).replace("， ", "，").replace("\n", ""), f"原文里找不到：{e[:20]}…"
    (OUT / "Q_ayi.html").write_text(card("A", "AYi", f"@AYi_AInotes · {when}（北京时间）", "原帖节选", [e1, "…", e2.replace("， ", "，"), "…"], "原帖：x.com/AYi_AInotes/status/2106649320179032146"), encoding="utf-8")
    # 劳伦斯的推文（10-04 08:39 UTC）
    text, when = tw(RAW / "lawrence_2106665574067761626_fxtwitter.json")
    f1 = "时效性跟有效性自行判断（我是在opus4.8发布后那短时间以及fable5发布后的那段时间一直在购买服务使用）！"
    f2 = "先说结论：授权登录的环境以及避免多端（移动端、桌面端）使用才是最重要！！！IP、时区无所谓。"
    for e in (f1, f2):
        assert e in text, f"原文里找不到：{e[:20]}…"
    (OUT / "Q_lw.html").write_text(card("劳", "劳伦斯", f"@LawrenceW_Zen · {when}（北京时间）", "原帖节选", ["…", f1, "…", f2, "…"], "原帖：x.com/LawrenceW_Zen/status/2106665574067761626"), encoding="utf-8")
    (OUT / "Q_scmp.html").write_text(card("南", "南华早报 SCMP", "Tech War · Chong Ming Lee · 2026-10-02（香港时间）", "报道标题",
        ["Hong Kong users caught off guard as Anthropic tightens VPN access to Claude"],
        "scmp.com/tech/tech-war/article/3369526/hong-kong-users-caught-offguard-anthropic-tightens-vpn-access-claude"), encoding="utf-8")
    print("已生成", [p.name for p in OUT.glob("*.html")])


if __name__ == "__main__":
    main()
