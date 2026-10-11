"""《AI每日日报》中英双语字幕（用户 2026-10-02：“改成双语，按统一标准来”）。

标准 = 项目统一的中英双语字幕标准：`D:/大疆/Way to AGI/skill/way-to-agi-episode/references/subtitles.md`「中英双语」。
检查、拆条、计时用《原LAI如此》的 `scripts/bilingual.py`（两档节目共用；它再 import Way to AGI 的 `bilingual_std.py`）：
  - 中文一行 52 px（Noto Sans SC 800，墨黑 #1B1B1F + 白边）在上，英文一行 30 px（600，灰 #4B5563 + 白边）在下，居中；
  - 一条中文 ≤ 约 28 字、英文 ≤ 约 90 字符，各一行不换行；放不下就拆条（split_pair_aligned：中英文一起找断点），
    拆得不顺的句子在台本里写 cuts 手动指定断点；
  - 每条开始前 0.1 s 显示到结束后 0.45 s，不和下一条重叠；
  - 导出三份 SRT：双语（中文在上）/ 中文 / 英文（assemble_wide.py 写）。
日报和标准唯一的差别：画面底部有全宽进度条（y 1000 起），字幕带从标准的 y 922 上移到 y 900，英文行才不压进度条的标签
（引擎 style.css 的 #subs.bi）。

    python bilingual_subs.py <期目录>            # build_timeline / mix_audio 之后：拆好的字幕条写进 制作/timeline.json 的 segments[].subs
    python bilingual_subs.py <期目录> --check    # 只读 台本.json，打印每句拆成的条，不写文件（写完台本自查用）

台本.json 每句（opening / news[].lines / closing）：text = 中文字幕，en = 英文字幕（整句意译，规则见 SKILL.md），
cuts = 可选，[[中文锚点, 英文锚点], …]（中文在这段文字之后断、英文在这段文字之后断，按出现的先后找）。
英文放在 台本.json 而不是 script_data.py：只改英文时从 daily.py render 重跑就行，不会被当成“台本改过”去重新配音。
时间：这一句在 timeline 里的 lines（build_timeline 按配音识别对齐过的短行）给出每个字的说话时刻，拆出来的每条取它首字和末字的时刻。
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
import bilingual as BL  # noqa: E402
from bilingual import B  # noqa: E402,F401  (assemble_wide.py 用 B.write_srts)

# 台本没写 closing 时 make_episode 用的结尾句（两边要一致）
DEFAULT_CLOSING = [{"text": "来源都在简介里。", "en": "Sources are in the description."}]


def script_lines(sc):
    """every spoken line of 台本.json in timeline order -> [(where, line)] (the same order make_episode writes the rows)"""
    out = [(f"opening 第 {k} 句", ln) for k, ln in enumerate(sc.get("opening") or [], 1)]
    for i, n in enumerate(sc.get("news") or [], 1):
        out += [(f"第 {i} 条第 {k} 句", ln) for k, ln in enumerate(n.get("lines") or [], 1)]
    out += [(f"closing 第 {k} 句", ln) for k, ln in enumerate(sc.get("closing") or DEFAULT_CLOSING, 1)]
    return out


def check(sc):
    """(errs, warns) for the English subtitles of 台本.json (make_episode.validate calls this)"""
    errs, warns = [], []
    for where, ln in script_lines(sc):
        e, w = BL.check_pair(where, ln.get("text"), ln.get("en"), ln.get("cuts"))
        errs += e
        warns += w
    return errs, warns


def attach(ep):
    sc = json.loads((ep / "台本.json").read_text(encoding="utf-8"))
    tl_path = ep / "制作" / "timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    pairs, segs = script_lines(sc), tl["segments"]
    if len(pairs) != len(segs):
        sys.exit(f"台本 {len(pairs)} 句、时间轴 {len(segs)} 段，对不上：台本改过，先重跑 daily.py build 之后的步骤")
    errs, warns = check(sc)
    if errs:
        sys.exit("英文字幕要改：\n" + "\n".join("  ✗ " + e for e in errs))
    subs, fallback = [], []
    for (where, ln), seg in zip(pairs, segs):
        if BL.norm(ln.get("text", "")) != BL.norm(seg["text"]):
            sys.exit(f"{where}「{ln.get('text', '')[:16]}」和时间轴 {seg['id']}「{seg['text'][:16]}」对不上：台本改过，先重跑 build 之后的步骤")
        seg["subs"], aligned = BL.seg_subs(seg, ln["en"], ln.get("cuts"))
        if not aligned:
            fallback.append(seg["id"])
        subs += seg["subs"]
    BL.set_windows(subs)
    tl["bilingual"] = True
    tl_path.write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    for w in warns:
        print("[提醒] " + w)
    if fallback:
        print(f"[提醒] 这几段的逐字时间对不上，按字数比例分时间：{' '.join(fallback)}")
    print(f"双语字幕 {len(subs)} 条（{len(segs)} 句）-> {tl_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ep = Path(a.episode_dir).resolve()
    if not a.check:
        attach(ep)
        return
    sc = json.loads((ep / "台本.json").read_text(encoding="utf-8"))
    errs, warns = check(sc)
    for where, ln in script_lines(sc):
        if not (ln.get("en") or "").strip():
            continue
        try:
            chunks = BL.split(ln.get("text", ""), ln["en"], ln.get("cuts"))
        except ValueError:
            continue
        print(where)
        for z, e, w in chunks:
            print(f"  {w:4.1f}｜{z}\n  {len(e):4d}｜{e}")
    for w in warns:
        print("  ! " + w)
    for e in errs:
        print("  ✗ " + e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
