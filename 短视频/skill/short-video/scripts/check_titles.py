# -*- coding: utf-8 -*-
r"""交付包的标题：3 个候选 × 3 个平台 = 9 个标题，按各平台的要求量字数、报超限；定稿后的各平台字段也一起核对。

用户 2026-10-04 要的是 3×4（第四个是视频号短标题 6–16）；2026-10-06 用户定“视频号之后不发”，视频号已从短视频发布流程移除，改成 3×3（旧做法存档在 references/_archive/视频号发布_已移除_20261006.md）。

  python check_titles.py <本条目录>      读 <本条>\投稿信息.json 的 titles（交付包阶段）和各平台字段（定稿后），有超限 / 缺项就退出码 1

各平台对标题的要求（实际发过的页面；字数按 Python len() 数，中英文都算 1）：
  B 站      标题 ≤ 80（页面计数 xx/80），可以放完整标题；标签 ≤ 10 个；简介 ≤ 2000；转载来源 ≤ 200
  抖音      作品标题 ≤ 30（页面计数 xx/30，放不下的完整标题放描述第一行）；话题 ≤ 5 个（平台上限）；描述（含话题）≤ 1000
  小红书    标题 ≤ 20（完整标题放正文第一行）；正文（含话题）≤ 1000；话题 8–10 个；“原创声明”开关选开

投稿信息.json 里 titles 这么写（三个候选，每个三个字段，三个角度要真有区别：事实陈述 / 数字悬念 / 泼冷水）：
  "titles": [{"id": 1, "angle": "事实陈述", "recommend": true,
              "bilibili": "…", "douyin": "…", "xiaohongshu": "…"}, {…}, {…}]
另外检查：标题不能和封面大字同一句（读 制作/04_封面/candidates.json 的 big）；三个候选的同一平台标题不能一样。
"""
import json
import re
import sys
from pathlib import Path

LIMITS = {"bilibili": (1, 80), "douyin": (1, 30), "xiaohongshu": (1, 20)}
NAMES = {"bilibili": "B 站", "douyin": "抖音", "xiaohongshu": "小红书"}
PUNCT = re.compile(r"[\s，。！？：；、“”‘’（）()《》【】,.!?:;\"'…—\-·|｜#]")


def n(s):
    return len(s or "")


def norm(s):
    return PUNCT.sub("", s or "")


def title_of(d, key):
    """候选里按平台取标题（老条目里的 weixin_channels 字段不再检查）。"""
    return d.get(key, "")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("用法：python check_titles.py <本条目录>     读 <本条>\\投稿信息.json 的 titles（3 候选 × 三个平台）和各平台字段，按各平台要求量字数；有超限退出码 1")
        sys.exit(0)
    ep = Path(sys.argv[1])
    info = json.loads((ep / "投稿信息.json").read_text(encoding="utf-8"))
    bad = 0
    hooks = []
    cj = ep / "制作" / "04_封面" / "candidates.json"
    if cj.is_file():
        for c in json.loads(cj.read_text(encoding="utf-8")).get("candidates", []):
            big = c.get("big", [])
            hooks.append(norm("".join(big if isinstance(big, list) else [big])))

    titles = info.get("titles") or []
    if titles:
        print(f"标题 {len(titles)} × 3（要求：3 个候选，每个 B 站 ≤ 80 / 抖音 ≤ 30 / 小红书 ≤ 20）")
        if len(titles) != 3:
            print(f"  ✗ 候选数 {len(titles)}，交付包要 3 个")
            bad += 1
        for t in titles:
            row = []
            for key, (lo, hi) in LIMITS.items():
                s = title_of(t, key)
                ok = lo <= n(s) <= hi
                bad += 0 if ok else 1
                row.append(f"{NAMES[key]} {n(s)}/{hi if lo == 1 else f'{lo}–{hi}'} {'✓' if ok else '✗'}")
                if s and any(h and h in norm(s) for h in hooks):
                    print(f"  ✗ 标题 {t.get('id')} 的{NAMES[key]}包含封面大字（封面协定：标题和封面不写同一句）：{s}")
                    bad += 1
            print(f"  标题 {t.get('id')}{'（推荐）' if t.get('recommend') else ''} · {t.get('angle', '')}：" + "；".join(row))
        for key in LIMITS:
            seen = [title_of(t, key) for t in titles]
            if len(set(seen)) < len(seen):
                print(f"  ✗ {NAMES[key]}：三个候选里有重复的标题")
                bad += 1
    else:
        print("（投稿信息.json 里还没有 titles：交付包阶段要写 3 个候选）")

    # 定稿后的各平台字段
    p = {k: info.get(k, {}) for k in ("bilibili", "douyin", "xiaohongshu")}
    rows = []

    def chk(label, val, lo, hi):
        nonlocal bad
        ok = lo <= val <= hi
        bad += 0 if ok else 1
        rows.append(f"  {'✓' if ok else '✗'} {label} {val}（要求 {lo if lo > 1 else '≤'}{'–' if lo > 1 else ''}{hi}）")

    b, d, x = p["bilibili"], p["douyin"], p["xiaohongshu"]
    if b.get("title"):
        chk("B 站标题", n(b["title"]), 1, 80)
        chk("B 站标签数", len(b.get("tags", [])), 0, 10)
        chk("B 站简介", n(b.get("desc", "")), 0, 2000)
        if b.get("repost_source"):
            chk("B 站转载来源", n(b["repost_source"]), 0, 200)
    if d.get("title"):
        chk("抖音标题", n(d["title"]), 1, 30)
        chk("抖音话题数", len(d.get("topics", [])), 0, 5)
        chk("抖音描述（含话题）", n(d.get("desc", "")) + sum(n(t) + 2 for t in d.get("topics", [])), 0, 1000)
    if x.get("title"):
        chk("小红书标题", n(x["title"]), 1, 20)
        chk("小红书正文（含话题）", n(x.get("desc") or x.get("body", "")) + sum(n(t) + 2 for t in x.get("topics", [])), 0, 1000)
        if not 8 <= len(x.get("topics", [])) <= 10:
            rows.append(f"  · 小红书话题 {len(x.get('topics', []))} 个（默认 8–10 个）")
    if rows:
        print("定稿字段：")
        print("\n".join(rows))
    print("全部在限内。" if not bad else f"有 {bad} 处要改。")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
