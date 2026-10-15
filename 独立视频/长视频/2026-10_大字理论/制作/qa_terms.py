"""用独立模型复核低置信度词，保留原始识别作为证据。"""
import json
from pathlib import Path
import soundfile as sf
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
audio, sr = sf.read(r"D:\大疆\独立视频\素材\2026-10_大字理论\audio16.wav", dtype="float32")
model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8)
out = []
for start, end in [(23.2, 27.6), (81.8, 94.0), (103.0, 111.0)]:
    segments, _ = model.transcribe(audio[int(start*sr):int(end*sr)], language="zh",
        beam_size=5, condition_on_previous_text=False)
    rows = [{"start": start+s.start, "end": start+s.end, "text": s.text} for s in segments]
    out.extend(rows)
    print(json.dumps(rows, ensure_ascii=False), flush=True)
(HERE / "qa_terms_original.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
