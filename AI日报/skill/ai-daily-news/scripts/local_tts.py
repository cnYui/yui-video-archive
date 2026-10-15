"""本地 TTS 配音（免费、离线、女声）：配音/chunks.json 的 C01 → 一个 wav。2026-10-14 起日报的配音用它，不再用 Fish Audio 网页版。

    python local_tts.py <期目录> --engine qwen|melo|sapi --out <wav> [--speaker Vivian] [--speed 1.0] [--seed 1234] [--limit N]

三个引擎（都在本机跑，不联网、不收费；模型放在 SERIES\\素材\\本地TTS\\）：
  qwen  阿里 Qwen3-TTS-12Hz-0.6B-CustomVoice（Apache-2.0）：中文女声 Vivian（明亮）/ Serena（温柔）。质量最好，CPU 上较慢。
        要用 SERIES\\素材\\本地TTS\\venv-qwen 里的 python 跑（torch + qwen-tts，和全局环境隔开）。
  melo  MeloTTS 中英混合（sherpa-onnx，MIT）：单一女声，CPU 上约 0.35× 实时，质量一般，是 qwen 太慢 / 出错时的备选。
  sapi  Windows 自带「Microsoft Huihui」女声（SAPI）：机械感重，只用来做“引导音轨”（无人声版定字幕时间，见 SKILL.md 第 5 步末尾）。

切句：按 。！？； 切成一句一句合成（每句 ≤ MAXLEN 字，太长在逗号处再切），句间补静音；每句落盘缓存在
配音/local_<引擎>/，中途断了再跑只补没做完的（缓存键 = 文字 + 说话人 + 语速 + 种子）。
"""
import argparse
import hashlib
import json
import re
import sys
import time
import wave
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
SERIES = Path(__file__).resolve().parent.parent.parent.parent       # D:/大疆/AI日报
MODELS = SERIES / "素材" / "本地TTS"
MAXLEN = 70                                                        # 一句最长字数（超了在逗号处再切）
GAP = {"。": 0.38, "！": 0.38, "？": 0.38, "；": 0.25, "，": 0.0, "": 0.30}   # 句末静音（秒）
QWEN_DIR = MODELS / "Qwen3-TTS-12Hz-0.6B-CustomVoice"
MELO_DIR = MODELS / "vits-melo-tts-zh_en"


# ---------------------------------------------------------------- 切句
def split_sentences(text):
    """[(句子, 句末标点)]。先按 。！？； 切；超过 MAXLEN 的在逗号 / 顿号处尽量对半再切。"""
    out = []
    for m in re.finditer(r"[^。！？；]+[。！？；]?", text.replace("\n", "")):
        s = m.group(0).strip()
        if not s:
            continue
        end = s[-1] if s[-1] in "。！？；" else ""
        out.append((s[:-1] if end else s, end))
    res = []
    for s, end in out:
        parts = [s]
        while any(len(p) > MAXLEN for p in parts):
            nxt = []
            for p in parts:
                if len(p) <= MAXLEN:
                    nxt.append(p)
                    continue
                cuts = [i for i, ch in enumerate(p) if ch in "，、：" and 8 <= i <= len(p) - 8]
                if not cuts:
                    nxt.append(p)
                    continue
                k = min(cuts, key=lambda i: abs(i - len(p) // 2))
                nxt += [p[:k + 1], p[k + 1:]]
            if nxt == parts:
                break
            parts = nxt
        for j, p in enumerate(parts):
            res.append((p, end if j == len(parts) - 1 else "，"))
    return [(s, e) for s, e in res if re.search(r"\w", s)]


# ---------------------------------------------------------------- 引擎
class Melo:
    name = "melo"

    def __init__(self, a):
        import sherpa_onnx as so
        d = str(MELO_DIR)
        vits = so.OfflineTtsVitsModelConfig(model=f"{d}/model.onnx", tokens=f"{d}/tokens.txt", lexicon=f"{d}/lexicon.txt", dict_dir=f"{d}/dict")
        mc = so.OfflineTtsModelConfig(vits=vits, num_threads=a.threads or 8, provider="cpu")
        cfg = so.OfflineTtsConfig(model=mc, rule_fsts=f"{d}/date.fst,{d}/phone.fst,{d}/number.fst", max_num_sentences=1)
        if not cfg.validate():
            sys.exit("MeloTTS 模型配置不对：检查 " + d)
        self.tts = so.OfflineTts(cfg)
        self.sr = self.tts.sample_rate
        self.speed = a.speed

    def synth(self, text, seed):
        r = self.tts.generate(text, sid=0, speed=self.speed)
        return np.asarray(r.samples, dtype=np.float32)


class Sapi:
    """Windows 自带 Huihui 中文女声，经 PowerShell + System.Speech 一次合成一批（pyttsx3 连续 runAndWait 第二句起会卡死，2026-10-14 实测，所以不用它）。"""
    name = "sapi"
    sr = 16000
    batch = 1000

    PS = r"""param([string]$In, [string]$OutDir, [int]$Rate)
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Name -like '*Huihui*' } | Select-Object -First 1
if (-not $v) { Write-Error 'no Huihui voice'; exit 2 }
$s.SelectVoice($v.VoiceInfo.Name)
$s.Rate = $Rate
$texts = Get-Content -LiteralPath $In -Raw -Encoding UTF8 | ConvertFrom-Json
for ($i = 0; $i -lt $texts.Count; $i++) {
  $s.SetOutputToWaveFile((Join-Path $OutDir ('t{0:D4}.wav' -f $i)))
  $s.Speak([string]$texts[$i])
  $s.SetOutputToNull()
}
"""

    def __init__(self, a):
        self.dir = Path(a.cache_dir) / "_sapi_tmp"
        self.rate = max(-10, min(10, round((a.speed - 1) * 10)))

    def synth_batch(self, texts, seed):
        import subprocess
        self.dir.mkdir(parents=True, exist_ok=True)
        for f in self.dir.glob("t*.wav"):
            f.unlink()
        (self.dir / "texts.json").write_text(json.dumps(list(texts), ensure_ascii=False), encoding="utf-8")
        (self.dir / "run.ps1").write_text("﻿" + self.PS, encoding="utf-8")
        r = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(self.dir / "run.ps1"),
                            "-In", str(self.dir / "texts.json"), "-OutDir", str(self.dir), "-Rate", str(self.rate)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("Huihui 合成失败：" + (r.stderr or r.stdout)[:300])
        out = []
        for i in range(len(texts)):
            with wave.open(str(self.dir / f"t{i:04d}.wav"), "rb") as w:
                self.sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            out.append(x)
        return out

    def synth(self, text, seed):
        return self.synth_batch([text], seed)[0]


class Qwen:
    name = "qwen"
    batch = 8                                              # 2026-10-14 实测（Core Ultra 5 225H、6 线程、fp32）：单句 3.5–5.4×实时，8 句一批 1.9×，16 句一批反而 2.2×

    def __init__(self, a):
        import torch
        from qwen_tts import Qwen3TTSModel
        self.torch = torch
        torch.set_num_threads(a.threads or 6)
        self.model = Qwen3TTSModel.from_pretrained(str(QWEN_DIR), device_map="cpu", dtype=torch.bfloat16 if a.bf16 else torch.float32,
                                                   attn_implementation="sdpa")
        self.speaker = a.speaker or "Vivian"
        self.instruct = a.instruct
        self.sr = 24000
        if a.batch:
            self.batch = a.batch

    def synth_batch(self, texts, seed):
        """一批句子一起合成（按长度排好序再分批，填充少）。max_new_tokens 按最长一句限一下：模型没吐出结束符时不会一直写下去。"""
        torch = self.torch
        torch.manual_seed(seed)
        n = len(texts)
        kw = {"instruct": [self.instruct] * n} if self.instruct else {}
        wavs, sr = self.model.generate_custom_voice(text=texts, language=["Chinese"] * n, speaker=[self.speaker] * n,
                                                    max_new_tokens=int(max(len(t) for t in texts) * 8) + 40, **kw)
        self.sr = sr
        return [np.asarray(w, dtype=np.float32).reshape(-1) for w in wavs]

    def synth(self, text, seed):
        return self.synth_batch([text], seed)[0]


ENGINES = {"qwen": Qwen, "melo": Melo, "sapi": Sapi}


# ---------------------------------------------------------------- 主流程
def trim_edges(x, sr, thr=0.004, keep=0.04):
    """去掉句子首尾的静音（保留 keep 秒），句间停顿由我们自己补。"""
    if len(x) == 0:
        return x
    idx = np.flatnonzero(np.abs(x) > thr)
    if len(idx) == 0:
        return x
    k = int(keep * sr)
    return x[max(0, idx[0] - k): idx[-1] + k + 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--engine", choices=list(ENGINES), default="qwen")
    ap.add_argument("--out", required=True, help="输出 wav")
    ap.add_argument("--speaker", help="qwen：Vivian（默认）/ Serena")
    ap.add_argument("--instruct", help="qwen：语气指令（0.6B 可能不支持，测过再用）")
    ap.add_argument("--speed", type=float, default=1.0, help="melo / sapi 的语速倍数")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--threads", type=int)
    ap.add_argument("--bf16", action="store_true", help="qwen：用 bfloat16（默认 float32，CPU 上通常更稳）")
    ap.add_argument("--batch", type=int, help="qwen：一批几句（默认 8）")
    ap.add_argument("--limit", type=int, help="只合成前 N 个字（试听 / 测速）")
    ap.add_argument("--text-file", help="不读 chunks.json，直接读这个文本文件（测试用）")
    a = ap.parse_args()

    ep = Path(a.episode_dir)
    if a.text_file:
        text = Path(a.text_file).read_text(encoding="utf-8")
    else:
        chunks = json.loads((ep / "配音" / "chunks.json").read_text(encoding="utf-8"))
        if len(chunks) != 1:
            sys.exit("配音/chunks.json 不是整期一批 C01：先 daily.py build")
        text = chunks[0]["text"]
    if a.limit:
        text = text[: a.limit]
    sents = split_sentences(text)
    a.cache_dir = str(ep / "配音" / f"local_{a.engine}")
    cache = Path(a.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    print(f"{a.engine}：{len(text)} 字 → {len(sents)} 句；缓存 {cache}", flush=True)

    t0 = time.time()
    eng = ENGINES[a.engine](a)
    print(f"模型载入 {time.time() - t0:.1f} s", flush=True)
    key0 = f"{a.engine}|{a.speaker or ''}|{a.instruct or ''}|{a.speed}|{a.seed}"
    files = [cache / f"s{i:04d}_{hashlib.md5((key0 + s).encode('utf-8')).hexdigest()[:10]}.npy" for i, (s, _) in enumerate(sents)]
    todo = [i for i, f in enumerate(files) if not f.exists()]
    print(f"  已缓存 {len(sents) - len(todo)} 句，要合成 {len(todo)} 句", flush=True)
    t_syn, done_audio, done_n = time.time(), 0.0, 0

    def sane(s, x):                                         # 每字 0.08–0.6 s 才算正常；太长多半是没吐出结束符、太短多半是漏读
        per = len(x) / eng.sr / max(len(s), 1)
        return 0.08 <= per <= 0.6

    def report(n_now):
        el = time.time() - t_syn
        print(f"  {done_n}/{len(todo)} 句，已合成 {done_audio:.0f} s 音频，用时 {el:.0f} s（{el / max(done_audio, 1e-9):.2f}× 实时）", flush=True)

    if hasattr(eng, "synth_batch"):
        order = sorted(todo, key=lambda i: len(sents[i][0]))
        for b in range(0, len(order), eng.batch):
            idx = order[b:b + eng.batch]
            xs = [trim_edges(x, eng.sr) for x in eng.synth_batch([sents[i][0] for i in idx], a.seed + b)]
            for i, x in zip(idx, xs):
                for retry in range(2):                      # 不正常的单句换个种子重来
                    if sane(sents[i][0], x):
                        break
                    print(f"  ! 第 {i + 1} 句时长不正常（{len(x) / eng.sr:.1f} s / {len(sents[i][0])} 字），换种子重做", flush=True)
                    x = trim_edges(eng.synth_batch([sents[i][0]], a.seed + 1000 * (retry + 1) + i)[0], eng.sr)
                np.save(files[i], x)
                done_audio += len(x) / eng.sr
                done_n += 1
            report(done_n)
    else:
        for k, i in enumerate(todo):
            s0 = sents[i][0]
            x = trim_edges(eng.synth(s0, a.seed + i), eng.sr)
            np.save(files[i], x)
            done_audio += len(x) / eng.sr
            done_n += 1
            if k % 5 == 4 or k == len(todo) - 1:
                report(done_n)
    pieces = []
    for f, (s0, end) in zip(files, sents):
        pieces += [np.load(f), np.zeros(int(GAP.get(end, 0.3) * eng.sr), dtype=np.float32)]
    y = np.concatenate(pieces)
    pk = float(np.abs(y).max()) or 1.0
    if pk > 0.95:
        y = y * (0.95 / pk)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(eng.sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"完成：{out}（{len(y) / eng.sr:.1f} s，总用时 {time.time() - t0:.0f} s）", flush=True)


if __name__ == "__main__":
    main()
