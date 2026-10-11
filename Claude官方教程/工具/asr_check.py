# -*- coding: utf-8 -*-
r"""给一批 wav 做两遍识别（中文 + 英文），看专名读得对不对。机器识别只是警报，读没读对最后要耳朵听。

  python asr_check.py <wav 目录> [--model small|medium|base] [--en-only] [--lines <台词 txt，一行一句，和 wav 顺序对应>]

输出：每个 wav 的时长、中文识别、英文识别；台词给了就并排打印。
"""
import sys
import wave
from pathlib import Path

from faster_whisper import WhisperModel


def dur(p):
    w = wave.open(str(p))
    d = w.getnframes() / w.getframerate()
    w.close()
    return d


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = Path(args[0])
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small"
    lines = None
    if "--lines" in sys.argv:
        lines = Path(sys.argv[sys.argv.index("--lines") + 1]).read_text(encoding="utf-8").splitlines()
    m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4)
    wavs = sorted(d.glob("*.wav"))
    for i, p in enumerate(wavs):
        row = [f"{p.name} {dur(p):5.2f}s"]
        if lines and i < len(lines):
            row.append("稿：" + lines[i])
        if "--en-only" not in sys.argv:
            seg, _ = m.transcribe(str(p), language="zh", initial_prompt="以下是普通话的句子，使用简体中文。Claude Code、Anthropic、CLAUDE.md、SKILL.md、PreToolUse。", beam_size=3)
            row.append("中：" + "".join(s.text for s in seg).strip())
        seg, _ = m.transcribe(str(p), language="en", beam_size=3)
        row.append("英：" + "".join(s.text for s in seg).strip())
        print("\n  ".join(row), flush=True)


if __name__ == "__main__":
    main()
