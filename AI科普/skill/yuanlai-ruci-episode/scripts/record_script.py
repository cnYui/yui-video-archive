"""Write the recording script the user reads from: 配音/录音稿.md, plus 配音/录音稿.txt for a teleprompter.

  python record_script.py <期目录>

《原LAI如此》 is voiced by the user from 2026-09-28 on (references/voice.md「自己录音」). 录音稿.md: short
instructions, then chapter by chapter (scene titles from 台本/script_data.py) every sentence with its segment id and
its subtitle text, which is exactly what segment_audio.py later matches the recording against. Where the TTS
spelling differs in a way that matters when reading aloud (English names, numbers), a small「读作」hint follows
(e.g. Jev → 杰夫, 0.72 → 零点七二); TTS spacing tricks such as "A P I" are never shown as text to read.
录音稿.txt: only the sentences, one per line, a blank line between chapters, no ids.
Re-run after every script change (build_script.py). Next: the user records, then import_voice.py <期目录> <文件…>.
"""
import argparse
import difflib
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402
from fetch_check import norm  # noqa: E402

HOWTO = [
    "手机或麦克风都行，wav / m4a / mp3 都可以。",
    "找一个安静的房间（关掉风扇、空调）。",
    "按顺序读，句与句之间停 1 秒左右。",
    "读错了不用停：停一下，把这一句从头再读一遍（脚本保留最后读完整的那一遍）。",
    "可以整期录成一个文件，也可以按章节分几个文件。",
    "段号（S03-12 这种）不用读；「读作」是英文、数字的读法提示，也不用读。",
    "录好把文件路径发过来。",
]
TOKEN_JOIN = set("-._+/'")          # characters that keep an English / number token together (GPT-5.6, 0.72)


def collapse(s):
    """Undo TTS spacing tricks for display: 'A P I' -> 'API', 'Chat G P T' -> 'Chat GPT'; trim spaces next to CJK."""
    out, run = [], False
    for t in s.split():
        single = bool(re.fullmatch(r"[A-Za-z]", t))
        if single and run:
            out[-1] += t                 # G P T -> GPT
        else:
            out.append(t)
        run = single
    s = " ".join(out)
    keep = [c for i, c in enumerate(s)
            if not (c == " " and ((i > 0 and _cjk(s[i - 1])) or (i + 1 < len(s) and _cjk(s[i + 1]))))]
    return "".join(keep).strip(" ，,。、")


def _cjk(c):
    o = ord(c)
    return 0x3000 <= o <= 0x303F or 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF


def _chars(s):
    """[(normalised char, index in s)] (same normalisation as the ASR matching)."""
    out = []
    for i, c in enumerate(s):
        for x in norm(c):
            out.append((x, i))
    return out


def _is_word(c):
    return c.isascii() and c.isalnum()


def hints(text, tts):
    """[(as written, as read)] for the parts of the subtitle with English letters or digits that the TTS text
    spells differently (spacing / punctuation differences do not count)."""
    a, b = _chars(text), _chars(tts or text)
    sa, sb = [x for x, _ in a], [x for x, _ in b]
    if sa == sb:
        return []
    ops = difflib.SequenceMatcher(None, sa, sb, autojunk=False).get_opcodes()
    eq = {}
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            for k in range(i2 - i1):
                eq[i1 + k] = j1 + k
    found = []
    for tag, i1, i2, j1, j2 in ops:
        if tag not in ("replace", "delete") or not any(_is_word(text[a[k][1]]) for k in range(i1, i2)):
            continue

        def joined(k0, k1):              # are text chars k0 < k1 (normalised idx) in one token (no space / CJK)?
            between = text[a[k0][1] + 1:a[k1][1]]
            return _is_word(text[a[k0][1]]) and _is_word(text[a[k1][1]]) and all(c in TOKEN_JOIN for c in between)

        while i1 > 0 and (i1 - 1) in eq and joined(i1 - 1, i1):      # widen to the whole token (GPT-5.6)
            i1, j1 = i1 - 1, eq[i1 - 1]
        while i2 < len(a) and i2 in eq and joined(i2 - 1, i2):
            j2 = eq[i2] + 1
            i2 += 1
        shown = text[a[i1][1]:a[i2 - 1][1] + 1]
        said = collapse(tts[b[j1][1]:b[j2 - 1][1] + 1]) if j2 > j1 else "（不读）"
        if re.fullmatch(r"\d{1,2}", shown):                         # 4倍 -> 四倍: nothing to point out
            continue
        if found and found[-1][2] >= i1:                              # overlapping after widening: merge
            continue
        found.append((shown, said, i2))
    return [(x, y) for x, y, _ in found]


def scene_titles(p):
    """{scene id: title} from 台本/script_data.py, else episode.json chapters."""
    titles = {}
    try:
        ns = C.load_script(p)
        for sc in ns["SCENES"]:
            if isinstance(sc, dict) and sc.get("id") and not C.is_bookend(sc):
                titles[sc["id"]] = str(sc.get("title") or sc["id"])
    except SystemExit:
        pass
    ep = C.load_episode(p, required=False) or {}
    for k, v in (ep.get("chapters") or {}).items():
        titles.setdefault(k, v)
    return titles


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    plan = C.load_json(p.voice_plan)
    if not plan:
        sys.exit(f"缺少 {p.voice_plan}：先写好台本，运行 build_script.py")
    ep = C.load_episode(p, required=False) or {}
    titles = scene_titles(p)
    est = sum(float(s.get("est_seconds") or C.est_seconds(s.get("tts_text") or s["text"])) for s in plan)
    minutes = (est * 1.15 + len(plan) * 1.0) / 60          # a person reads a bit slower than the TTS, + 1 s pauses
    num = ep.get("number")
    head = f"《原LAI如此》第 {num} 期「{ep.get('title', p.ep.name)}」录音稿" if num else f"{p.ep.name} 录音稿"
    per = {s["id"]: hints(s["text"], s.get("tts_text") or s["text"]) for s in plan}
    glossary = []
    for s in plan:
        for h in per[s["id"]]:
            if h not in glossary:
                glossary.append(h)
    md = [f"# {head}", "",
          f"共 {len(plan)} 句，照正常语速连停顿大约 {minutes:.0f} 分钟。"
          f"{time.strftime('%Y-%m-%d %H:%M')} 由 `record_script.py` 从 `台本/配音分段.json` 生成：台本改了要重新生成，按最新的读。",
          "", "## 怎么录", ""]
    md += [f"{i}. {x}" for i, x in enumerate(HOWTO, 1)]
    if glossary:
        md += ["", "## 读法", "", "英文、数字这样读（下面每章第一次出现时也会提示）：", ""]
        md += [f"- {x} → {y}" for x, y in glossary]
    txt, cur, n_hints, seen = [], None, 0, set()
    for s in plan:
        if s["scene"] != cur:
            cur, seen = s["scene"], set()
            md += ["", f"## {cur}　{titles.get(cur, '')}".rstrip(), ""]
            if txt:
                txt.append("")
        md.append(f"- **{s['id']}**　{s['text']}")
        hs = []
        for h in per[s["id"]]:                   # each reading once per chapter (people record chapter by chapter)
            if h not in seen and h not in hs:
                hs.append(h)
        seen.update(hs)
        if hs:
            n_hints += 1
            md.append("  - *读作：" + "；".join(f"{x} → {y}" for x, y in hs) + "*")
        txt.append(s["text"])
    p.voice.mkdir(exist_ok=True)
    out_md, out_txt = p.voice / "录音稿.md", p.voice / "录音稿.txt"
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    out_txt.write_text("\n".join(txt) + "\n", encoding="utf-8")
    print(f"-> {out_md}（{len(plan)} 句，{n_hints} 句带读法提示）")
    print(f"-> {out_txt}（提词用：一句一行，章节之间空一行）")
    print(f"把录音稿发给用户录音（约 {minutes:.0f} 分钟）；录好后：python {Path(__file__).resolve().parent / 'import_voice.py'} "
          f"{p.ep} <文件1> [文件2 …]")


if __name__ == "__main__":
    main()
