"""Fish Audio API 配音：按 配音/chunks.json 逐批生成，存成 配音/raw/Cxx_vN.mp3（和网页版下载的命名一样），
之后照常 daily.py voice（select_takes 用语音识别打分挑版本 → segment_audio 切句）。

    python tts_api.py <期目录> [--takes 1] [--only C01,C05] [--missing] [--model s1] [--out DIR] [--score] [--dry-run]

- 默认（daily.py tts 就是这样调）= --missing：只给“还没有和当前文字一致的版本”的批次生成。每个版本生成时用的文字记在
  配音/raw/api_takes.json；台本改过、文字对不上的旧版本挪到 配音/raw/_旧稿_<时间>/（不删），select_takes 就不会挑到。
- --only C05：给这些批次再加版本（重配读得不好的批次），旧版本保留，select_takes 按识别分挑。

- daily.py build 默认把整期合成一批（C01），这里一次请求生成整期音频，避免分批调用音色不一致（用户 2026-09-27）。
- API key 读环境变量 FISH_API_KEY；当前进程里没有就读 Windows 用户环境变量（刚设好不用重启）。脚本不打印、不保存 key。
- 模型默认 s1（和首期网页版同一个模型）；--model s2.1-pro-free 是免费模型，只在用户点名时用（余额不足不要换它）。
- 音色「苏晓晓」；温度 0.9、top_p 0.9、语速 1，和网页版的设置一致。
- 计费按请求文本的 UTF-8 字节（s1 每百万字节 $15，2026-09-27 官方定价页）。跑完打印字节数和估算费用，
  并追加到 <输出目录>/api_usage.jsonl。
- 401（key 不对）、402（余额不足）直接停下，不重试；429、503、超时等 10 / 20 秒重试，最多 3 次。
  402 之后改用 Chrome 插件操作 Fish Audio 网页版（用户 2026-09-28：额度用完就用浏览器插件；Plus 账号、S1、整期一次），
  做法见 SKILL.md 第 5 步。
"""
import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

sys.stdout.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True
API = "https://api.fish.audio/v1/tts"
VOICE = "e7219cb8cfab46bebba2ee570932b0a6"                 # 苏晓晓（作者 yc Z）
PRICE = {"s1": 15.0, "s2-pro": 15.0, "s2.1-pro": 15.0, "s2.1-pro-free": 0.0}   # USD / 百万 UTF-8 字节
CST = timezone(timedelta(hours=8))
YL = Path(r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
FATAL = {401: "API key 不对或已失效（401）",
         402: "余额不足（402）：不要替用户充值，也不要换免费模型；按 SKILL.md 第 5 步改用 Chrome 插件操作 Fish Audio 网页版"
              "（用户的 Plus 账号，模型 S1，整期一次生成）",
         403: "没有权限（403）"}


class Stop(Exception):
    pass


def api_key():
    k = os.environ.get("FISH_API_KEY")
    if not k and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
                k = winreg.QueryValueEx(h, "FISH_API_KEY")[0]
        except OSError:
            k = None
    if not k:
        sys.exit("没有 FISH_API_KEY：运行 rundll32 sysdm.cpl,EditEnvironmentVariables，"
                 "在“用户变量”里新建 FISH_API_KEY，值填 Fish Audio 后台的 API key")
    return k.strip()


def synth(client, key, model, text):
    body = {"text": text, "reference_id": VOICE, "format": "mp3", "mp3_bitrate": 128, "latency": "normal",
            "temperature": 0.9, "top_p": 0.9, "prosody": {"speed": 1.0}}
    headers = {"Authorization": f"Bearer {key}", "model": model}
    err = ""
    for attempt in range(1, 4):
        try:
            r = client.post(API, json=body, headers=headers)
        except httpx.HTTPError as e:
            err = type(e).__name__
        else:
            if r.status_code == 200 and r.content:
                return r.content
            if r.status_code in FATAL:
                raise Stop(f"{FATAL[r.status_code]}：{r.text[:200]}")
            err = f"HTTP {r.status_code} {r.text[:200]}"
        if attempt < 3:
            time.sleep(10 * attempt)
    raise Stop(f"重试 3 次仍失败：{err}")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]).decode().strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--takes", type=int, default=1, help="每批生成几个版本（默认 1；select_takes 会挑分数最高的）")
    ap.add_argument("--only", help="只生成这些批次，逗号分隔，如 C01,C05")
    ap.add_argument("--missing", action="store_true", help="只生成还没有和当前文字一致的版本的批次（文字对不上的旧版本挪进 _旧稿）")
    ap.add_argument("--model", default="s1", choices=sorted(PRICE))
    ap.add_argument("--out", help="输出目录（默认 <期目录>/配音/raw；试音时指到别处）")
    ap.add_argument("--score", action="store_true", help="生成后用 faster-whisper 打分（和 select_takes 同一个算法）")
    ap.add_argument("--workers", type=int, default=3, help="同时发几个请求（预充值不到 $100 的账号上限 5）")
    ap.add_argument("--dry-run", action="store_true", help="只算字节和费用，不调用 API")
    a = ap.parse_args()

    ep = Path(a.episode_dir)
    chunks = json.loads((ep / "配音" / "chunks.json").read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else ep / "配音" / "raw"
    want = set(a.only.split(",")) if a.only else None
    db_path = out / "api_takes.json"
    db = json.loads(db_path.read_text(encoding="utf-8")) if db_path.exists() else {}
    stale_dir = out / f"_旧稿_{datetime.now(CST):%Y%m%d-%H%M%S}"
    plan, taken, stale = [], set(), []
    for c in chunks:
        cid = c["chunk"]
        if want and cid not in want:
            continue
        if a.missing:
            have = sorted(out.glob(f"{cid}_v*.mp3"))
            if any(db.get(f.name) == c["text"] for f in have):
                continue
            stale += have                       # 文字对不上（或来源不明）的旧版本：挪走，免得被选中
        n = 1
        for _ in range(a.takes):
            while (out / f"{cid}_v{n}.mp3").exists() or (cid, n) in taken:
                n += 1
            taken.add((cid, n))
            plan.append((c, out / f"{cid}_v{n}.mp3"))
    nbytes = sum(len(c["text"].encode("utf-8")) for c, _ in plan)
    print(f"{len({c['chunk'] for c, _ in plan})} 批 × {a.takes} 个版本 = {len(plan)} 次请求，{nbytes} 字节，"
          f"模型 {a.model}，估算 ${nbytes / 1e6 * PRICE[a.model]:.4f}")
    if stale:
        print(f"{len(stale)} 个旧版本和当前文字对不上" + ("（dry-run 不挪）" if a.dry_run else f"，挪到 {stale_dir.name}/"))
    if a.dry_run or not plan:
        return
    key = api_key()                              # 先确认有 key，再挪旧版本
    if stale:
        stale_dir.mkdir(parents=True, exist_ok=True)
        for f in stale:
            shutil.move(str(f), str(stale_dir / f.name))
    out.mkdir(parents=True, exist_ok=True)
    done = []

    def work(item):
        c, dst = item
        t0 = time.time()
        audio = synth(client, key, a.model, c["text"])
        tmp = dst.with_suffix(".part")
        tmp.write_bytes(audio)
        tmp.replace(dst)
        db[dst.name] = c["text"]
        return c, dst, time.time() - t0

    try:
        with httpx.Client(timeout=httpx.Timeout(600, connect=15)) as client, \
                ThreadPoolExecutor(max_workers=max(1, min(a.workers, 5))) as ex:
            for c, dst, secs in ex.map(work, plan):
                dur = duration(dst)
                done.append(dict(chunk=c["chunk"], file=dst.name, bytes=len(c["text"].encode("utf-8")),
                                 duration=round(dur, 2), text=c["text"]))
                print(f"{dst.name}: {dur:.2f}s（请求 {secs:.1f}s，{done[-1]['bytes']} 字节）", flush=True)
    except Stop as e:
        print(f"停下：{e}")
    finally:
        db_path.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
        used = sum(d["bytes"] for d in done)
        if done:
            with open(out / "api_usage.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"at": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"), "episode": ep.name,
                                    "model": a.model, "requests": len(done), "bytes": used,
                                    "usd": round(used / 1e6 * PRICE[a.model], 5)}, ensure_ascii=False) + "\n")
        print(f"完成 {len(done)}/{len(plan)} 次请求，{used} 字节，约 ${used / 1e6 * PRICE[a.model]:.4f}")
    if len(done) < len(plan):
        sys.exit(1)

    if a.score:
        sys.path.insert(0, str(YL))
        from fetch_check import ASR_PROMPT, load_model, norm   # 和 select_takes 同一套归一化
        model = load_model("small")
        with open(out / "scores.jsonl", "a", encoding="utf-8") as f:
            for d in done:
                segs, _ = model.transcribe(str(out / d["file"]), language="zh", initial_prompt=ASR_PROMPT)
                hyp = "".join(s.text for s in segs)
                s = difflib.SequenceMatcher(None, norm(d["text"].replace(" ", "")), norm(hyp)).ratio()
                print(f"{d['file']}: score={s:.3f}\n   ASR: {hyp}")
                f.write(json.dumps(dict(chunk=d["chunk"], variant=int(Path(d["file"]).stem.split("_v")[-1]),
                                        file=d["file"], url=f"api:{a.model}", duration=d["duration"],
                                        score=round(s, 3), asr=hyp), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
