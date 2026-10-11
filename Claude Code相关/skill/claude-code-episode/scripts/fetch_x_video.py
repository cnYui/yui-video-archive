# -*- coding: utf-8 -*-
r"""下载 X（推特）官方推文里的视频，不用 TwitterSaver。

  python fetch_x_video.py <推文链接或ID> [更多链接…] [--out <素材\X平台视频_ClaudeDevs>] [--quality best|1080|720|360]

做法（2026-10-03 第 3 期摸出来的）：X 的公开嵌入接口 cdn.syndication.twimg.com/tweet-result?id=<ID>&lang=en&token=a 返回 JSON：
text / created_at（UTC）/ entities.urls（t.co 展开）/ mediaDetails[].video_info.variants[]（各档 mp4 直链）/ parent（回复的上一条）。
mp4 直链本来就在官方 CDN video.twimg.com 上：脚本断言主机名是 video.twimg.com（不是就不下），下载后 ffprobe 核对时长 / 规格 / 有没有音轨，
文件名 <账号>_<推文ID>.mp4，并往 <out>\来源.md 追加一行（没有这个文件就新建带表头的）。
如果用户明说“用 TwitterSaver 下载”，照他说的做（OpenAI相关 第 1 期的流程，见 openai-episode 技能）；没明说就用这个。
推文里的链接、文字、时间也会打印出来（事实核对用）；时间是 UTC，旁边给出北京时间，旁白不写具体几号。
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"
API = "https://cdn.syndication.twimg.com/tweet-result?id={}&lang=en&token=a"


def tweet_id(s):
    m = re.search(r"status/(\d+)", s) or re.fullmatch(r"(\d{10,})", s.strip())
    if not m:
        sys.exit(f"认不出推文 ID：{s}")
    return m.group(1)


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def pick(variants, quality):
    mp4 = [v for v in variants if v.get("content_type") == "video/mp4" and v.get("url")]
    if not mp4:
        return None
    if quality != "best":
        want = [v for v in mp4 if f"/{quality}" in v["url"] or f"x{quality}/" in v["url"]]
        if want:
            mp4 = want
    return max(mp4, key=lambda v: v.get("bitrate") or 0)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    has_a = any(s["codec_type"] == "audio" for s in j["streams"])
    return v, has_a, float(j["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tweets", nargs="+")
    ap.add_argument("--out", default=".")
    ap.add_argument("--quality", default="best", choices=["best", "1080", "720", "360"])
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, bad = [], 0
    for t in a.tweets:
        tid = tweet_id(t)
        d = get_json(API.format(tid))
        user = (d.get("user") or {}).get("screen_name", "unknown")
        created = datetime.strptime(d["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc) if d.get("created_at") else None
        bj = created.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M") if created else "?"
        print(f"\n=== @{user} / {tid}  {created.strftime('%Y-%m-%d %H:%M') if created else '?'} UTC（北京 {bj}）")
        print(d.get("text", "").strip())
        for u in (d.get("entities") or {}).get("urls", []):
            print("  链接：", u.get("expanded_url"))
        if d.get("parent"):
            print("  回复的上一条：", (d["parent"].get("user") or {}).get("screen_name"), d["parent"].get("id_str"))
        media = [m for m in d.get("mediaDetails", []) if m.get("type") in ("video", "animated_gif")]
        if not media:
            print("  这条推文没有视频（图片 / 纯文字），不用下载（文字和链接已打印，事实核对用）")
            continue
        for k, m in enumerate(media):
            var = pick((m.get("video_info") or {}).get("variants", []), a.quality)
            if not var:
                print("  没有 mp4 直链，跳过")
                bad += 1
                continue
            u = urlparse(var["url"])
            if u.scheme != "https" or not (u.hostname or "").endswith("video.twimg.com"):
                print(f"  源站不是 video.twimg.com（{u.hostname}），不下载")
                bad += 1
                continue
            name = f"{user}_{tid}" + (f"_{k + 1}" if len(media) > 1 else "") + ".mp4"
            dst = out / name
            if dst.exists() and dst.stat().st_size > 0:
                print(f"  已有 {name}，不重下")
            else:
                req = urllib.request.Request(var["url"], headers={"User-Agent": UA})
                tmp = dst.with_suffix(".part")
                with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
                tmp.rename(dst)
            v, has_a, dur = probe(dst)
            spec = f"{dur:.2f} s，{v.get('width')}×{v.get('height')}，{v.get('r_frame_rate')} fps，{v.get('codec_name')}，{'有音轨' if has_a else '无音轨'}，{dst.stat().st_size:,} 字节"
            print(f"  -> {dst}  {spec}   （{var.get('bitrate')} bps 那档）")
            text = re.sub(r"\s+", " ", d.get("text", "")).strip()
            rows.append(f"| `{name}` | https://x.com/{user}/status/{tid} | {created.strftime('%Y-%m-%d %H:%M') if created else '?'} UTC（北京 {bj}） | {text[:90]}{'…' if len(text) > 90 else ''} | {spec} |")
    if rows:
        md = out / "来源.md"
        if not md.exists():
            md.write_text("# X 平台视频来源\n\n账号是官方账号的，片子里用到时标“画面：<账号> · X”，只作介绍和评论引用。下载方式：X 公开嵌入接口 + video.twimg.com 直链（fetch_x_video.py）。\n\n"
                          "| 文件 | 原帖 | 发帖时间 | 内容 | 规格 |\n|---|---|---|---|---|\n", encoding="utf-8")
        old = md.read_text(encoding="utf-8")
        new = [r for r in rows if r.split("|")[1] not in old]
        if new:
            md.write_text(old.rstrip("\n") + "\n" + "\n".join(new) + "\n", encoding="utf-8")
        print(f"\n来源表：{md}（新增 {len(new)} 行）")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
