# -*- coding: utf-8 -*-
"""整期配音前的试读：只念几个容易念错的词（夯、Mimo、Jev、Artificial Analysis、L M Arena），
用本期讲解员的音色和 s1 模型，花费约 0.002 美元；再用本机的 faster-whisper 听写一遍核对。
key 只从环境变量 / 用户变量 FISH_API_KEY 读（复用 tts_api.api_key），不打印、不保存。"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
EP = HERE.parent.parent
sys.path.insert(0, r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
import tts_api as T  # noqa: E402

TEXT = ("从夯到拉。夯，又强又值。给到，夯。"
        "九月新出的小米 Mimo，阶跃 Step 五，还有 Jev。"
        "独立评测机构 Artificial Analysis。L M Arena 是用户盲投。")

ep = json.loads((EP / "episode.json").read_text(encoding="utf-8"))
voice = ep["presenter"]["voice_id"]
nbytes = len(TEXT.encode("utf-8"))
print(f"音色 {ep['presenter']['voice_name']}（{voice}），模型 s1，{nbytes} 字节，估算 ${nbytes / 1e6 * T.PRICE['s1']:.4f}")
key = T.api_key()
t0 = time.time()
with httpx.Client(timeout=120) as client:
    audio = T.synth(client, key, "s1", voice, TEXT)
out = HERE / "try_v1.mp3"
out.write_bytes(audio)
with open(EP / "配音" / "raw" / "api_usage.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"time": datetime.now().isoformat(timespec="seconds"), "what": "试读（夯、Mimo、Jev 等）",
                        "voice": voice, "model": "s1", "requests": 1, "bytes": nbytes,
                        "usd": round(nbytes / 1e6 * T.PRICE["s1"], 5), "files": [str(out.relative_to(EP))]},
                       ensure_ascii=False) + "\n")
print(f"-> {out}（{len(audio)} 字节，{time.time() - t0:.1f} s）")

from faster_whisper import WhisperModel  # noqa: E402
m = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8",
                 local_files_only=True)
segs, _ = m.transcribe(str(out), language="zh", word_timestamps=False, beam_size=5)
print("听写：", "".join(s.text for s in segs))
