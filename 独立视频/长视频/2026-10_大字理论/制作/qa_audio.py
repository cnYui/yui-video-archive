"""识别剪后音轨并核对字幕，暴露切断、漏词和时间偏移。"""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
model = WhisperModel("large-v3-turbo",device="cpu",compute_type="int8",cpu_threads=8)
segments,info = model.transcribe(str(HERE/"qa_audio.wav"),language="zh",beam_size=5,
    word_timestamps=True,condition_on_previous_text=False,
    initial_prompt="薄肌理论，大水理论，大字理论，消费主义焦虑，幸福者退让原则。")
rows=[]
for s in segments:
    rows.append(dict(s=s.start,e=s.end,text=s.text,words=[dict(w=w.word,s=w.start,e=w.end) for w in s.words or []]))
    print(f"{s.start:.2f}-{s.end:.2f}: {s.text}",flush=True)
(HERE/"qa_asr_original.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
edit=json.loads((HERE/"edit.json").read_text(encoding="utf-8"))
normalize=lambda x: re.sub(r"[^\u4e00-\u9fff0-9a-zA-Z]","",x)
checks=[]
for c in edit["cues"]:
    text="".join(w["w"] for r in rows for w in r["words"] if c["start"]-.12<=(w["s"]+w["e"])/2<=c["end"]+.12)
    ratio=SequenceMatcher(None,normalize(c["zh"]),normalize(text)).ratio()
    checks.append(dict(start=c["start"],expected=c["zh"],recognized=text,ratio=round(ratio,3)))
(HERE/"qa_subtitles.json").write_text(json.dumps(dict(duration=info.duration,checks=checks),ensure_ascii=False,indent=2),encoding="utf-8")
print("需复核",json.dumps([x for x in checks if x["ratio"]<.70],ensure_ascii=False),flush=True)
