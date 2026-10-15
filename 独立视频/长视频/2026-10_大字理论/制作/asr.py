"""保留逐词转写，使剪辑和字幕能共同使用原片时间。"""
import json
import time
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"D:\大疆\独立视频\素材\2026-10_大字理论\audio16.wav")
PROMPT = "嗯，那个，就是，呃。薄肌理论，大水理论，大字理论，悠一，人工智能。"

def main():
    started = time.time()
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    segments, info = model.transcribe(str(SOURCE), language="zh", beam_size=5,
        word_timestamps=True, initial_prompt=PROMPT, condition_on_previous_text=False,
        vad_filter=False)
    rows = []
    for seg in segments:
        row = {"start": seg.start, "end": seg.end, "text": seg.text,
            "words": [{"w": w.word, "s": w.start, "e": w.end, "p": w.probability} for w in seg.words or []]}
        rows.append(row)
        print(f"{seg.start:.2f}-{seg.end:.2f}: {seg.text}", flush=True)
    (ROOT / "asr_original.json").write_text(json.dumps({"duration": info.duration,
        "segments": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成：{len(rows)} 段，耗时 {time.time()-started:.1f} 秒", flush=True)

if __name__ == "__main__":
    main()
