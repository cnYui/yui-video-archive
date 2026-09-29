"""Download the two Fish Audio variants of a chunk and score them against the script with ASR.

usage: python fetch_check.py C02 <url_variant1> <url_variant2>
Writes raw/C02_v1.mp3, raw/C02_v2.mp3 and appends a line to raw/scores.jsonl.
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
sys.stdout.reconfigure(encoding="utf-8")

T2S = str.maketrans("給紹說麼個們這為會後開發請應們來時對現裡體與種據邊語調問題點數條讀錯費帳號範戶權綫線處寫處檔傳碼記過還讓設計還將從並們會實際擇選項頁輸認證錢單額償將聯網絡資訊務雲廠夠應處轉換類標標準貝雜舊專聽廣氣電腦畫寫實結構參數響應欄態",
                    "给绍说么个们这为会后开发请应们来时对现里体与种据边语调问题点数条读错费账号范户权线线处写处档传码记过还让设计还将从并们会实际择选项页输认证钱单额偿将联网络资讯务云厂够应处转换类标标准贝杂旧专听广气电脑画写实结构参数响应栏态")


def norm(s):
    s = s.translate(T2S).lower()
    return re.sub(r"[^\w]|_", "", s)


def main():
    chunk, urls = sys.argv[1], sys.argv[2:]
    ref = next(c for c in json.loads((HERE / "chunks.json").read_text(encoding="utf-8")) if c["chunk"] == chunk)
    ref_text = norm(ref["text"].replace(" ", ""))
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    results = []
    for i, url in enumerate(urls, 1):
        out = RAW / f"{chunk}_v{i}.mp3"
        subprocess.run(["curl", "-sS", "-L", "--max-time", "60", "-o", str(out), url.replace("?cors", "")], check=True)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                             "-of", "csv=p=0", str(out)]).decode().strip())
        segs, _ = model.transcribe(str(out), language="zh", initial_prompt="以下是普通话的句子。")
        hyp = "".join(s.text for s in segs)
        ratio = difflib.SequenceMatcher(None, ref_text, norm(hyp)).ratio()
        results.append(dict(chunk=chunk, variant=i, file=out.name, url=url, duration=round(dur, 2),
                            score=round(ratio, 3), asr=hyp))
        print(f"{chunk} v{i}: {dur:.2f}s score={ratio:.3f}\n   ASR: {hyp}")
    with open(RAW / "scores.jsonl", "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
