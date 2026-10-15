# -*- coding: utf-8 -*-
"""交付包：把 6 期的成片路径 / 时长 / 封面候选 / 标题 3×4 / 默认项 / 要耳朵听的句子汇总成 系列目录下的 交付包.md（聊天里发摘要，完整内容看这个文件）。

  python make_delivery.py
读：各期 投稿信息.json、成片 / 手机预览（ffprobe）、制作/_run_qa.log（qa_mix 低分句）、制作/04_封面/候选总览.png。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402


def probe(p):
    if not p.exists():
        return None
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=width,height", "-of", "default=nw=1", str(p)], capture_output=True, text=True).stdout
    kv = dict(l.split("=", 1) for l in o.split() if "=" in l)
    return float(kv["duration"]), int(kv["size"]) / 1e6, kv.get("width"), kv.get("height")


def low_lines(ep):
    f = ep_dir(ep) / "制作" / "_run_qa.log"
    if not f.exists():
        return None
    out = []
    for l in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(N\d+)\s+([\d.]+)\s+(.*?)\s+<<<", l)
        if m:
            out.append((m.group(1), m.group(2), m.group(3)))
    return out


def main():
    L = ["# 《Tim Denning 的 36 条忠告》交付包（6 期）", "",
         "回复格式：“第 N 期：封面 X 标题 Y 同意”（或“全部按推荐同意”）；同意前不会发布任何平台。", ""]
    for ep in D.EPISODES:
        n = ep["num"]
        d = ep_dir(ep)
        info = json.loads((d / "投稿信息.json").read_text(encoding="utf-8"))
        v = probe(d / f"{ep['slug']}_成片.mp4")
        pv = probe(d / f"{ep['slug']}_手机预览.mp4")
        L += [f"## 第 {n} 期 · {ep['name'].split('_', 1)[1]}", "",
              f"- 标题（画面顶上）：{ep['hook'][0]} / {ep['hook'][1]}",
              f"- 成片：`{d / (ep['slug'] + '_成片.mp4')}`" + (f"（{v[0]:.1f} s，{v[1]:.1f} MB，{v[2]}×{v[3]}）" if v else "（还没出）"),
              f"- 手机预览：`{d / (ep['slug'] + '_手机预览.mp4')}`" + (f"（{pv[1]:.1f} MB）" if pv else ""),
              f"- 字幕：`{d / (ep['slug'] + '_双语字幕.srt')}`（另有中文 / 英文两份）",
              f"- 封面 3×3 总览：`{d / '制作' / '04_封面' / '候选总览.png'}`（A 整张配图铺满 / B 紧裁到中间那位的脸；字样都是“2800万浏览 / 推特万字长文 / 解读(N)”，各 3:4、16:9、4:3）", "",
              "| 候选 | 角度 | B 站（≤80） | 抖音（≤30） | 小红书（≤20） |", "|---|---|---|---|---|"]
        for t in info["titles"]:
            L.append(f"| {t['id']}{'（推荐）' if t.get('recommend') else ''} | {t['angle'].split('（')[0]} | {t['bilibili']} | {t['douyin']} | {t['xiaohongshu']} |")
        ll = low_lines(ep)
        L += ["", "要耳朵听的句子（机器识别低于 0.8，多半是同音 / 数字写法 / 专名）：" + ("还没跑 qa_mix" if ll is None else ("无" if not ll else "；".join(f"{a}（{b}）{c}" for a, b, c in ll))), ""]
    L += ["## 其余默认项（不用回，要改再说）", "",
          "- 三个平台（B 站 / 抖音 / 小红书；视频号 2026-10-06 起不发），合集随 B 站（没有就不选；这个系列还没建合集，要建先说名字：抖音 ≤ 20 字）；",
          "- 声明统一选“含 AI 生成内容”；话题抖音 5 / 小红书 10、B 站标签 10；",
          "- 简介前两行写转载来源（Tim Denning 文章 X 长文 / Substack 链接），自称的数字都挂名；BGM 默认配（系列 BGM，−9 dB 床）；",
          "- 成片第 0 帧 = 选定封面（`cover_frame0.py`，用户选定封面后再做；抖音竖封面直接用它）；视频由用户拖进各平台上传区，不压缩。", ""]
    (HERE / "交付包.md").write_text("\n".join(L), encoding="utf-8")
    print("->", HERE / "交付包.md")


if __name__ == "__main__":
    main()
