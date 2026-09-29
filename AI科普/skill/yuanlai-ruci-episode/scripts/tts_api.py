"""Generate the voice with the Fish Audio API, in this episode's presenter's voice: 配音/chunks.json -> 配音/raw/Cxx_vN.mp3.

  python tts_api.py <episode_dir> [--takes 1] [--only C01] [--model s1] [--dry-run] [--series ...]

Normal use (since 2026-09-27 the user wants the API, not the web page / browser plugin): chunk_voice.py --whole first,
so chunks.json is one chunk C01 = the whole episode, generated in ONE request (the voice does not drift between
batches). Then select_takes.py (ASR score -> selection.json) and segment_audio.py as before; takes are named like the
old web downloads (Cxx_v1.mp3 …), so nothing downstream changes.

- Voice = episode.json "presenter" (epcommon.PRESENTERS: 山田凉 -> 「山田凉」, 鲸鱼娘 -> 「苏晓晓」; voice_id, or the id in
  voice_app / voice_page); --voice <model id> overrides it.
- Default: only chunks without a take of their CURRENT text get one (the text of every take is recorded in
  配音/raw/api_takes.json). Takes whose text no longer matches (台本 changed) are moved to 配音/raw/_旧稿_<time>/, never
  deleted, so select_takes cannot pick them. --only C01: add another take of these chunks (a retake), old ones kept.
- API key: environment variable FISH_API_KEY, else the Windows user variable of that name (set in
  「编辑账户的环境变量」; no restart needed). The script never prints or saves the key.
- Model s1 (the model every episode so far was voiced with); temperature 0.9, top_p 0.9, speed 1.0 (the web defaults).
- Billing is per UTF-8 byte of the request text (s1: USD 15 per million bytes, Fish Audio pricing page 2026-09-27;
  a 6-minute episode is about 6000 bytes = about USD 0.09 per take). The run prints bytes and the estimate and appends
  them to 配音/raw/api_usage.jsonl. --dry-run only prints the plan and the estimate.
- 401 (wrong key) and 403 stop at once: tell the user. 402 (balance too low) also stops; never top up or pay: the
  user's rule (2026-09-28) is to fall back to the Fish Audio web page with their Plus account, model S1, whole
  episode in one go (references/voice.md「备用：网页版」). 429 / 5xx / timeouts are retried twice (10 s, 20 s).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import httpx

sys.stdout.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

API = "https://api.fish.audio/v1/tts"
PRICE = {"s1": 15.0}              # USD per million UTF-8 bytes of request text (pricing page, 2026-09-27)
FATAL = {401: "API key 不对或已失效（401）：请用户到 Fish Audio 后台核对，重新设置用户环境变量 FISH_API_KEY",
         402: "余额不足（402）：不要替用户充值；按 references/voice.md「备用：网页版」改用网页版（用户的 Plus 账号，模型 S1，整期一次）",
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
        sys.exit("没有 FISH_API_KEY：请用户在 Windows「编辑账户的环境变量」（rundll32 sysdm.cpl,EditEnvironmentVariables）"
                 "的“用户变量”里新建 FISH_API_KEY，值填 Fish Audio 后台的 API key（不要把 key 发在对话里或写进文件）")
    return k.strip()


def synth(client, key, model, voice, text):
    body = {"text": text, "reference_id": voice, "format": "mp3", "mp3_bitrate": 128, "latency": "normal",
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
                raise Stop(f"{FATAL[r.status_code]}  {r.text[:200]}")
            err = f"HTTP {r.status_code} {r.text[:200]}"
        if attempt < 3:
            time.sleep(10 * attempt)
    raise Stop(f"重试 3 次仍失败：{err}")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]).decode().strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    ap.add_argument("--takes", type=int, default=1, help="每批生成几个版本（默认 1；select_takes 按识别分挑）")
    ap.add_argument("--only", help="只给这些批次再生成版本（重配），逗号分隔，如 C01")
    ap.add_argument("--model", default="s1", choices=sorted(PRICE))
    ap.add_argument("--voice", help="Fish Audio 音色模型 id（默认本期讲解员的音色）")
    ap.add_argument("--workers", type=int, default=3, help="同时发几个请求（最多 5）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划和估算费用，不调用 API")
    a = ap.parse_args()
    p = C.Paths(a.episode_dir, a.series)
    chunks = C.load_json(p.chunks)
    if not chunks:
        sys.exit(f"缺少 {p.chunks}：先运行 chunk_voice.py --whole")
    pr = C.presenter_of(C.load_episode(p, required=False) or {})
    voice = a.voice or C.voice_id_of(pr)
    if not voice:
        sys.exit(f"讲解员 {pr.get('name')} 没有音色 id：在 episode.json presenter.voice_id（或 epcommon.PRESENTERS）写上")
    if len(chunks) > 1 and not a.only:
        print(f"[提醒] chunks.json 有 {len(chunks)} 批：API 配音通常整期一批（chunk_voice.py --whole --force），"
              "分批生成时各批之间音色可能有差别")

    out = p.raw
    want = set(a.only.split(",")) if a.only else None
    unknown = sorted(want - {c["chunk"] for c in chunks}) if want else []
    if unknown:
        sys.exit(f"chunks.json 里没有 {'、'.join(unknown)}")
    db_path = out / "api_takes.json"
    db = C.load_json(db_path, {}) or {}
    stale_dir = out / f"_旧稿_{datetime.now():%Y%m%d-%H%M%S}"
    plan, taken, stale = [], set(), []
    for c in chunks:
        cid = c["chunk"]
        if want is not None:
            if cid not in want:
                continue
        else:
            have = sorted(out.glob(f"{cid}_v*.mp3")) if out.exists() else []
            if any(db.get(f.name) == c["text"] for f in have):
                continue
            stale += [f for f in have if f.name in db]     # API takes of an older text: move them away
            if any(f.name not in db for f in have):         # takes from the old web workflow: keep, text unknown
                print(f"[提醒] {cid} 已有网页版录音（{'、'.join(f.name for f in have if f.name not in db)}），"
                      "保留不动；新版本编号接在后面，select_takes 会一起打分")
        n = 1
        for _ in range(a.takes):
            while (out / f"{cid}_v{n}.mp3").exists() or (cid, n) in taken:
                n += 1
            taken.add((cid, n))
            plan.append((c, out / f"{cid}_v{n}.mp3"))
    nbytes = sum(len(c["text"].encode("utf-8")) for c, _ in plan)
    print(f"音色 {pr.get('voice_name') or voice}（{pr.get('name')}，{voice}），模型 {a.model}")
    print(f"{len({c['chunk'] for c, _ in plan})} 批 × {a.takes} 个版本 = {len(plan)} 次请求，{nbytes} 字节，"
          f"估算 ${nbytes / 1e6 * PRICE[a.model]:.4f}")
    if stale:
        print(f"{len(stale)} 个旧版本和当前文字对不上" + ("（dry-run 不挪）" if a.dry_run else f"，挪到 {stale_dir.name}/"))
    if a.dry_run or not plan:
        if not plan:
            print("没有要生成的：每批都已有和当前文字一致的版本（要重配加 --only C01）")
        return
    key = api_key()                              # make sure there is a key before moving anything
    out.mkdir(parents=True, exist_ok=True)
    if stale:
        stale_dir.mkdir(parents=True, exist_ok=True)
        for f in stale:
            shutil.move(str(f), str(stale_dir / f.name))
    done = []

    def work(item):
        c, dst = item
        t0 = time.time()
        audio = synth(client, key, a.model, voice, c["text"])
        tmp = dst.with_suffix(".part")
        tmp.write_bytes(audio)
        tmp.replace(dst)
        db[dst.name] = c["text"]
        return c, dst, time.time() - t0

    try:
        with httpx.Client(timeout=httpx.Timeout(900, connect=15)) as client, \
                ThreadPoolExecutor(max_workers=max(1, min(a.workers, 5))) as ex:
            for c, dst, secs in ex.map(work, plan):
                dur = duration(dst)
                done.append(dict(chunk=c["chunk"], file=dst.name, bytes=len(c["text"].encode("utf-8")),
                                 duration=round(dur, 2)))
                print(f"{dst.name}: {dur:.1f}s 音频（请求 {secs:.0f}s，{done[-1]['bytes']} 字节）", flush=True)
    except Stop as e:
        print(f"停下：{e}")
    finally:
        C.write_json(db_path, db)
        used = sum(d["bytes"] for d in done)
        if done:
            with open(out / "api_usage.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "episode": p.ep.name,
                                    "voice": voice, "model": a.model, "requests": len(done), "bytes": used,
                                    "usd": round(used / 1e6 * PRICE[a.model], 5), "files": [d["file"] for d in done]},
                                   ensure_ascii=False) + "\n")
        print(f"完成 {len(done)}/{len(plan)} 次请求，{used} 字节，约 ${used / 1e6 * PRICE[a.model]:.4f}")
    if len(done) < len(plan):
        sys.exit(1)
    print(f"下一步：python select_takes.py {p.ep}（语音识别打分挑版本）→ segment_audio.py → 请用户试听")


if __name__ == "__main__":
    main()
