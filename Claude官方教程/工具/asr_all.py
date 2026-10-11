# -*- coding: utf-8 -*-
r"""给 10 期的逐句配音做识别核对（中文 + 英文各一遍，faster-whisper small / int8），把“读歪”的嫌疑句列出来，写 台本\配音核对.md。
机器识别只是警报：专名、sh/x、数字都有假低分；真正读没读对要耳朵听（记忆 fish-tts-english-names-check-first）。

  python asr_all.py [期号 …] [--model small|medium]
"""
import difflib
import re
import sys
import time
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES, EP_ROOT  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402


def norm(s):
    s = re.sub(r"[\s，。！？、；：“”‘’（）()\[\]{}《》\-—…,.!?;:'\"/\\]", "", s).lower()
    return s


def main():
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(EPISODES)
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small"
    m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
    t0 = time.time()
    for n in want:
        d = EPISODES[n]
        final = EP_ROOT / d["folder"] / "制作" / "02_配音" / "tts" / "seg_raw" / "final"
        rows = []
        only_new = "--new" in sys.argv
        redo = set()
        if only_new and (HERE / "redo.txt").exists():
            for ln in (HERE / "redo.txt").read_text(encoding="utf-8").splitlines():
                ln = ln.split("#")[0].strip()
                if ln:
                    a, b = ln.split(":")
                    redo.add((int(a), b.strip()))
        for i, l in enumerate(d["lines"]):
            if only_new and not (int(l["id"][1:]) >= 13 or (n, l["id"]) in redo):
                continue
            p = final / f"{i:06d}.wav"
            w = wave.open(str(p))
            dur = w.getnframes() / w.getframerate()
            w.close()
            seg, _ = m.transcribe(str(p), language="zh", initial_prompt="以下是普通话的句子，使用简体中文。Claude Code、Anthropic、PreToolUse、PostToolUse、SessionStart、MCP、Linear、Context7。", beam_size=3)
            zh = "".join(s.text for s in seg).strip()
            seg, _ = m.transcribe(str(p), language="en", beam_size=3)
            en = "".join(s.text for s in seg).strip()
            sim = difflib.SequenceMatcher(None, norm(zh), norm(l["say"])).ratio()
            toks = re.findall(r"[A-Za-z][A-Za-z0-9]{2,}", l["say"])
            miss = [t for t in toks if t.lower() not in norm(zh) and t.lower() not in norm(en)]
            rows.append((l["id"], dur, sim, l["say"], zh, en, miss))
        out = EP_ROOT / d["folder"] / "台本" / ("配音核对_补录.md" if only_new else "配音核对.md")
        low = [r for r in rows if r[2] < 0.80 or r[6]]
        txt = [f"# 第 {n} 期 配音识别核对（faster-whisper {model}，中文 + 英文各一遍；只是警报，读没读对要耳朵听）\n",
               f"- 句数 {len(rows)}，有声 {sum(r[1] for r in rows):.1f} s；嫌疑句 {len(low)} 条（中文相似度 < 0.80，或稿里的英文词两遍识别都没出现）\n",
               "| 句 | 时长 | 相似度 | 稿（say） | 中文识别 | 英文识别 | 没听到的英文词 |", "| - | - | - | - | - | - | - |"]
        for r in rows:
            flag = " ⚠" if (r[2] < 0.80 or r[6]) else ""
            txt.append(f"| {r[0]}{flag} | {r[1]:.1f} | {r[2]:.2f} | {r[3]} | {r[4]} | {r[5]} | {'、'.join(r[6])} |")
        out.write_text("\n".join(txt) + "\n", encoding="utf-8")
        print(f"第 {n} 期：{len(rows)} 句，嫌疑 {len(low)} 条 → {out.name}（累计 {time.time() - t0:.0f}s）", flush=True)
        for r in low:
            print(f"   ⚠ {r[0]} 相似度 {r[2]:.2f} 缺词 {r[6]}\n      稿：{r[3]}\n      中：{r[4]}\n      英：{r[5]}", flush=True)


if __name__ == "__main__":
    main()
