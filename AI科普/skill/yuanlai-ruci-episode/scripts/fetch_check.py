"""Download the Fish Audio takes of a chunk and score each against the script with ASR (faster-whisper).

  python fetch_check.py <episode_dir> C02 <url_take1> <url_take2>      # one chunk
  python fetch_check.py <episode_dir> --urls 配音/urls.txt              # many: lines "C05 <url1> <url2>"

Takes are saved as 配音/raw/C02_v1.mp3, C02_v2.mp3 … (numbering continues after existing takes),
and each score is appended to 配音/raw/scores.jsonl (score = similarity of the recognised text to the
chunk's tts_text, 0–1; ≥0.95 is normally clean, lower means a skipped / misread word: listen to it).
Next: select_takes.py <episode_dir>
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

T2S = str.maketrans("給紹說麼個們這為會後開發請應們來時對現裡體與種據邊語調問題點數條讀錯費帳號範戶權綫線處寫處檔傳碼記過還讓設計還將從並們會實際擇選項頁輸認證錢單額償將聯網絡資訊務雲廠夠應處轉換類標標準貝雜舊專聽廣氣電腦畫寫實結構參數響應欄態",
                    "给绍说么个们这为会后开发请应们来时对现里体与种据边语调问题点数条读错费账号范户权线线处写处档传码记过还让设计还将从并们会实际择选项页输认证钱单额偿将联网络资讯务云厂够应处转换类标标准贝杂旧专听广气电脑画写实结构参数响应栏态")
ASR_PROMPT = "以下是普通话的句子。"


def norm(s):
    """Normalise text for comparison: traditional->simplified (common chars), lower case, drop punctuation."""
    s = s.translate(T2S).lower()
    return re.sub(r"[^\w]|_", "", s)


def load_model(name="small"):
    from faster_whisper import WhisperModel
    return WhisperModel(name, device="cpu", compute_type="int8")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]).decode().strip())


def check_chunk(p, model, chunk, urls):
    ref = next((c for c in C.load_json(p.chunks, []) if c["chunk"] == chunk), None)
    if ref is None:
        sys.exit(f"chunks.json 里没有 {chunk}")
    ref_text = norm(ref["text"].replace(" ", ""))
    p.raw.mkdir(parents=True, exist_ok=True)
    n = 1
    while (p.raw / f"{chunk}_v{n}.mp3").exists():
        n += 1
    results = []
    for url in urls:
        out = p.raw / f"{chunk}_v{n}.mp3"
        n += 1
        subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", str(out), url.replace("?cors", "")], check=True)
        dur = duration(out)
        segs, _ = model.transcribe(str(out), language="zh", initial_prompt=ASR_PROMPT)
        hyp = "".join(s.text for s in segs)
        ratio = difflib.SequenceMatcher(None, ref_text, norm(hyp)).ratio()
        results.append(dict(chunk=chunk, variant=int(out.stem.split("_v")[-1]), file=out.name, url=url,
                            duration=round(dur, 2), score=round(ratio, 3), asr=hyp))
        print(f"{chunk} {out.stem}: {dur:.2f}s score={ratio:.3f}\n   ASR: {hyp}")
    with open(p.raw / "scores.jsonl", "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("chunk", nargs="?", help="批次号，如 C02")
    ap.add_argument("urls", nargs="*", help="这一批的录音地址（通常两个）")
    ap.add_argument("--urls", dest="url_file", help="批量：文本文件，每行「C05 <url1> <url2>」")
    ap.add_argument("--model", default="small", help="faster-whisper 模型（默认 small）")
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    jobs = []
    if args.url_file:
        f = Path(args.url_file)
        f = f if f.is_absolute() or f.exists() else p.ep / f
        for line in f.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 2 and re.fullmatch(r"C\d+", parts[0]):
                jobs.append((parts[0], parts[1:]))
    if args.chunk:
        if not args.urls:
            ap.error("给了批次号就要给录音地址")
        jobs.append((args.chunk, args.urls))
    if not jobs:
        ap.error("需要 <chunk> <url…> 或 --urls 文件")
    known = {c["chunk"] for c in C.load_json(p.chunks, [])}
    bad = [c for c, _ in jobs if c not in known]
    if bad:
        sys.exit(f"chunks.json 里没有 {'、'.join(bad)}（先运行 chunk_voice.py）")
    model = load_model(args.model)
    for chunk, urls in jobs:
        check_chunk(p, model, chunk, urls)


if __name__ == "__main__":
    main()
