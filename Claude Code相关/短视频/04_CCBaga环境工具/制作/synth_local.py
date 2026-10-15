"""复用已有 Qwen 本地模型，逐句音频与字幕共用一份时序，避免拼接后错位。"""
import importlib.util
import hashlib
import json
import time
import wave
from pathlib import Path
from types import SimpleNamespace
import numpy as np

EP=Path(__file__).resolve().parents[1]
SOURCE=Path('D:/大疆/AI日报/skill/ai-daily-news/scripts/local_tts.py')
spec=importlib.util.spec_from_file_location('daily_local_tts',SOURCE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
lines=json.loads((EP/'台本/录制稿.json').read_text(encoding='utf-8'))['lines']
out=EP/'制作/02_配音/edit'; out.mkdir(exist_ok=True)
cache=EP/'制作/02_配音/tts/seg_raw'
a=SimpleNamespace(threads=6,bf16=False,speaker='Vivian',instruct=None,batch=8)
eng=m.Qwen(a)
def cache_path(line):
    return cache/(line['id']+'_'+hashlib.sha256(line['say'].encode()).hexdigest()[:10]+'.npy')
todo=[x for x in lines if not cache_path(x).exists()]
for start in range(0,len(todo),8):
    batch=todo[start:start+8]; t0=time.time()
    audio=eng.synth_batch([x['say'] for x in batch],1234+start)
    for line,x in zip(batch,audio):
        x=m.trim_edges(x,eng.sr); np.save(cache_path(line),x)
        print(line['id'],len(x)/eng.sr,'秒',flush=True)
    print('本批用时',round(time.time()-t0),'秒',flush=True)
pieces=[]; timing=[]; t=0
for line in lines:
    x=np.load(cache_path(line)); dur=len(x)/eng.sr
    gap=np.zeros(int(.18*eng.sr),np.float32)
    timing.append(dict(id=line['id'],s=t,e=t+dur,n0=t,n1=t+dur))
    pieces.extend([x,gap]); t+=dur+.18
y=np.concatenate(pieces); peak=max(float(abs(y).max()),.001)
if peak>.95:y*=.95/peak
with wave.open(str(out/'tts_narration.wav'),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(eng.sr);w.writeframes((y*32767).astype(np.int16).tobytes())
(out/'tts_edit.json').write_text(json.dumps(dict(total=t,lines=timing,engine='Qwen3-TTS-12Hz-0.6B-CustomVoice',speaker='Vivian',speed=1.0),ensure_ascii=False,indent=2),encoding='utf-8')
print('本地配音完成',round(t,2),'秒',flush=True)
