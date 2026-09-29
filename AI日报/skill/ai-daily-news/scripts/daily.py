"""《AI每日日报》单次运行的各个阶段（routine 里 Claude 按 SKILL.md 依次调用；每步产物落盘，可以从断点续跑）。

    python daily.py init   [--date YYYY-MM-DD] [--hours N]   建本期目录；最后抓一次；导出候选 → candidates.md、aired_recent.md
        （Claude 选题、查原文、写 台本.json）
    python daily.py build  [--date ...]    台本.json → episode.json / script_data.py / 引擎 → 台本.md、配音分段.json → 配音分批
        （配音：用户 2026-09-29 定，之后都用 Fish Audio 网页版。Claude 用 Chrome 插件在网页版整期一次生成（用户 Plus、S1），
          页面一次出两个版本 → 插件 read_network_requests 拿两个任务编号 → webvoice 下载）
    python daily.py webvoice --task <编号> [--task <编号2>] [--date ...] [--probe]   网页版音频 → 配音/raw/C01_vN.mp3（登记文字、记用量）
    python daily.py tts    [--date ...] --api [--takes 1] [--model s1]   Fish Audio API 配音（停用：只在用户点名时加 --api 用）
    python daily.py voice  [--date ...] [--hist urls_hist.txt]   选版本 + 按句切开、对齐字幕
    python daily.py render [--date ...] [--skip-main]           时间轴 → 混音 → 成片 → 封面 → 上传版（≤9 MB）→ 核对 → 审稿单、投稿信息
        ✋ 用户看 审稿单.md 和成片，回复“发”；Claude 用 Chrome 插件填 B 站投稿页，收到“发”才点「立即投稿」
    python daily.py published --bv BV1xxxxxxxxx [--date ...]   记 BV 号，写进已播清单（下次选题去重用）
    python daily.py status [--date ...]

日期默认是北京时间今天。期目录 = D:/大疆/AI日报/<日期>/（必须直接放在系列根下）。
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from lxml import html as lhtml

sys.stdout.reconfigure(encoding="utf-8")
SK = Path(__file__).resolve().parent
SERIES = SK.parent.parent.parent                          # D:/大疆/AI日报
COLLECT = SERIES / "collector" / "collect.py"
AIRED = SERIES / "collector" / "aired.jsonl"
YL = Path(r"D:/大疆/AI科普/skill/yuanlai-ruci-episode/scripts")
CST = timezone(timedelta(hours=8))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
UPLOAD_LIMIT = 9_000_000                                   # the Chrome extension uploads ≤ 10 MB per file
BASE_TAGS = ["AI资讯", "人工智能", "大模型", "AI日报"]
# “Claude”在 B 站是话题专用词，普通标签加不上（2026-09-27）
ORG_TAGS = {"OpenAI": "OpenAI", "Anthropic": "Anthropic", "Google": "谷歌", "DeepSeek": "DeepSeek", "Qwen": "通义千问", "Kimi": "Kimi",
            "智谱": "智谱", "MiniMax": "MiniMax", "Meta": "Meta", "xAI": "Grok", "Mistral": "Mistral", "NVIDIA": "英伟达",
            "Microsoft": "微软", "Apple": "苹果", "字节 Seed": "豆包", "腾讯": "腾讯混元", "百度": "文心一言", "小米": "小米"}


def today_cst():
    return datetime.now(CST).strftime("%Y-%m-%d")


def run(cmd, cwd=None, check=True):
    cmd = [str(c) for c in cmd]
    print("$ " + " ".join(cmd)[:220], flush=True)
    r = subprocess.run(cmd, cwd=cwd)
    if check and r.returncode != 0:
        sys.exit(f"失败（退出码 {r.returncode}）：{' '.join(cmd)[:160]}")
    return r.returncode


def ep_dir(date):
    return SERIES / date


def load_state(ep):
    p = ep / "state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"stages": {}}


def save_state(ep, st, stage, **info):
    st.setdefault("stages", {})[stage] = {"at": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"), **info}
    st["last"] = stage
    (ep / "state.json").write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:12] if Path(path).exists() else None


def load_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


# ---------------------------------------------------------------- init
def cmd_init(a):
    ep = ep_dir(a.date)
    ep.mkdir(parents=True, exist_ok=True)
    st = load_state(ep)
    run([sys.executable, COLLECT, "collect"])
    if (ep / "candidates.json").exists() and st["stages"].get("init") and not a.force:
        print("候选已经导出过（重跑用 --force；--hours N 取最近 N 小时）")
    else:
        extra = ["--hours", str(a.hours)] if a.hours else []
        run([sys.executable, COLLECT, "export", ep, *extra])
    aired = [json.loads(l) for l in AIRED.read_text(encoding="utf-8").splitlines() if l.strip()] if AIRED.exists() else []
    cutoff = (datetime.fromisoformat(a.date) - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [x for x in aired if x.get("date", "") >= cutoff]
    L = ["# 最近 7 天已播（选题去重：同一件事没有新进展就不再报）", ""]
    L += [f"- {x['date']}｜{x['headline']}｜" + " ".join(r.get("url", "") for r in x.get("refs", [])[:2]) for x in recent] or ["（无）"]
    (ep / "aired_recent.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    save_state(ep, st, "init")
    meta = load_json(ep / "candidates.json", {}).get("meta", {})
    print(f"\n本期目录：{ep}\n候选：{meta.get('candidates')} 个（{meta.get('since_cst')} → {meta.get('exported_cst')}），看 candidates.md；已播：aired_recent.md")
    print("下一步：选 4–5 条、查原文、写 台本.json（格式见 SKILL.md），然后 daily.py build")


# ---------------------------------------------------------------- build
def cmd_build(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    if not (ep / "台本.json").exists():
        sys.exit(f"缺少 {ep / '台本.json'}")
    h = sha(ep / "台本.json")
    run([sys.executable, SK / "make_episode.py", ep])
    run([sys.executable, SK / "snap_sources.py", ep], check=False)     # 原文截图；失败的条目回到单栏版面，不挡流程
    run([sys.executable, YL / "build_script.py", ep, "--series", SERIES])
    changed = st["stages"].get("build", {}).get("script_sha") not in (None, h)
    vdir = ep / "配音"
    cur = load_json(vdir / "chunks.json", []) or []
    if len(cur) == 1 and cur[0].get("scene") == "ALL" and (vdir / "chunks_batches.json").exists():
        shutil.copy2(vdir / "chunks_batches.json", vdir / "chunks.json")   # chunk_voice 要和它自己的分批比较
    run([sys.executable, YL / "chunk_voice.py", ep, "--series", SERIES] + (["--force"] if changed or a.force else []))
    chunks = load_json(vdir / "chunks.json", [])
    # 整期一次生成（用户 2026-09-27：分批生成音色会有差别）：把分批合成一批 C01；
    # 分批结果留在 chunks_batches.json（--batches = 保留分批，只在网页版单次放不下整期时用）
    if chunks and not a.batches:
        (vdir / "chunks_batches.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
        text = "".join(c["text"] for c in chunks)
        chunks = [dict(chunk="C01", scene="ALL", ids=[i for c in chunks for i in c["ids"]], text=text, count=len(text.encode("utf-8")))]
        (vdir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    save_state(ep, st, "build", script_sha=h, chunks=len(chunks))
    if changed:
        print("! 台本.json 改过：daily.py tts 会整期重新生成（旧音频挪进 配音/raw/_旧稿_*，不删）")
    print(f"\n配音：{len(chunks)} 批，共 {sum(c['count'] for c in chunks)} 字节：{vdir / 'chunks.json'}")
    print("下一步：Fish Audio 网页版配音（SKILL.md 第 5 步）→ daily.py webvoice --task <编号> --task <编号2>，然后 daily.py voice")


# ---------------------------------------------------------------- tts (Fish Audio API：停用，用户点名才加 --api)
def cmd_tts(a):
    if not a.api:
        sys.exit("用户 2026-09-29 定：之后都用 Fish Audio 网页版配音（SKILL.md 第 5 步），生成后 daily.py webvoice --task <编号> 下载。\n"
                 "不调 API；用户点名要用 API 时才加 --api。")
    ep = ep_dir(a.date)
    st = load_state(ep)
    extra = ["--takes", str(a.takes), "--model", a.model, "--missing"]   # 只补文字对不上 / 还没有版本的批次
    run([sys.executable, SK / "tts_api.py", ep, *extra])
    save_state(ep, st, "tts", model=a.model, takes=a.takes)
    print("下一步：daily.py voice")


# ---------------------------------------------------------------- webvoice（Fish Audio 网页版的音频 → 配音/raw/）
R2 = "https://platform.r2.fish.audio/tasks/{d}/{t}.mp3"


def r2_exists(url):
    for method, headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        try:
            r = httpx.request(method, url, headers={"User-Agent": UA, **headers}, timeout=20, follow_redirects=True)
            if r.status_code in (200, 206):
                return True
        except httpx.HTTPError:
            pass
    return False


def cmd_webvoice(a):
    """网页版每次 Ctrl+Enter 出两个版本（两个任务编号）。地址 = R2/<日期>/<编号>.mp3，日期是哪个时区的没确认过，
    所以 UTC 今天、前一天、后一天都试。文字对不上的旧版本挪进 配音/raw/_旧稿_<时间>/（和 tts_api.py --missing 一样），
    新版本的文字记在 配音/raw/api_takes.json，select_takes 就只会在当前文字的版本里挑。"""
    ep = ep_dir(a.date)
    st = load_state(ep)
    raw = ep / "配音" / "raw"
    chunks = load_json(ep / "配音" / "chunks.json", []) or []
    if len(chunks) != 1:
        sys.exit("配音/chunks.json 不是整期一批 C01：先 daily.py build")
    c = chunks[0]
    now = datetime.now(timezone.utc)
    days = list(dict.fromkeys((now + timedelta(days=k)).strftime("%Y-%m-%d") for k in (0, -1, 1)))
    urls = []
    for t in a.task:
        t = t.strip().lower()
        if not re.fullmatch(r"[0-9a-f]{32}", t):
            sys.exit(f"任务编号应该是 32 位十六进制：{t}")
        hit = next((R2.format(d=d, t=t) for d in days if r2_exists(R2.format(d=d, t=t))), None)
        if not hit:
            sys.exit(f"找不到任务 {t} 的音频（日期试过 {'、'.join(days)}）：确认已经生成完、编号没抄错")
        urls.append(hit)
        print(f"{t} -> {hit}")
    if a.probe:
        return
    raw.mkdir(parents=True, exist_ok=True)
    db_path = raw / "api_takes.json"
    db = load_json(db_path, {}) or {}
    stale = [f for f in sorted(raw.glob(f"{c['chunk']}_v*.mp3")) if db.get(f.name) != c["text"]]
    if stale:
        stale_dir = raw / f"_旧稿_{datetime.now(CST):%Y%m%d-%H%M%S}"
        stale_dir.mkdir(parents=True, exist_ok=True)
        for f in stale:
            shutil.move(str(f), str(stale_dir / f.name))
        print(f"{len(stale)} 个旧版本和当前文字对不上，挪到 {stale_dir.name}/")
    n = 1
    for u in urls:
        while (raw / f"{c['chunk']}_v{n}.mp3").exists():
            n += 1
        dst = raw / f"{c['chunk']}_v{n}.mp3"
        r = httpx.get(u, headers={"User-Agent": UA}, timeout=120, follow_redirects=True)
        r.raise_for_status()
        tmp = dst.with_suffix(".part")
        tmp.write_bytes(r.content)
        tmp.replace(dst)
        dur = ffprobe_duration(dst)
        if dur < 60:
            sys.exit(f"{dst.name} 只有 {dur:.1f} 秒：网页上可能没生成完或只生成了一段，查一下再下")
        db[dst.name] = c["text"]
        print(f"{dst.name}: {dur:.1f} s，{len(r.content) / 1e6:.2f} MB")
    db_path.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(raw / "web_usage.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now(CST):%Y-%m-%d %H:%M} 北京｜网页版 S1｜{len(c['text'])} 字 / {c['count']} 字节｜任务 {' '.join(a.task)}\n")
    save_state(ep, st, "tts", source="web", tasks=a.task)
    print("下一步：daily.py voice")


# ---------------------------------------------------------------- voice
def cmd_voice(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    extra = ["--hist", a.hist] if a.hist else []
    run([sys.executable, YL / "select_takes.py", ep, "--series", SERIES, *extra])
    run([sys.executable, YL / "segment_audio.py", ep, "--series", SERIES])
    sel = load_json(ep / "配音" / "selection.json", {})
    save_state(ep, st, "voice", takes=len(sel) if isinstance(sel, (list, dict)) else None)
    print("下一步：daily.py render")


# ---------------------------------------------------------------- render
def ffprobe_duration(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)])
    return float(out.decode().strip())


def encode_upload(src, dst, logdir, codec="hevc"):
    """上传版 ≤ UPLOAD_LIMIT（插件单个文件上限 10 MB）。5–6 分钟、2340x1080 只能给视频约 150 kbps，
    所以默认用 H.265（同样大小画质比 H.264 好一截；B 站收 H.265）。codec="h264" 是退路（B 站不收时用）。
    两遍编码；x265 的 stats 路径里不能有盘符冒号，所以在 logdir 里用相对路径跑。"""
    dur = ffprobe_duration(src)
    v = max(100, int(UPLOAD_LIMIT * 8 / 1000 / dur * 0.96) - 64)
    logdir = Path(logdir)
    for _ in range(3):
        if codec == "hevc":
            xp = f"vbv-maxrate={int(v * 1.6)}:vbv-bufsize={v * 2}:log-level=error"
            common = ["-c:v", "libx265", "-preset", "medium", "-b:v", f"{v}k", "-pix_fmt", "yuv420p"]
            p1 = [*common, "-x265-params", f"pass=1:stats=x265_2pass.log:{xp}"]
            p2 = [*common, "-x265-params", f"pass=2:stats=x265_2pass.log:{xp}", "-tag:v", "hvc1"]
        else:
            common = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-b:v", f"{v}k", "-maxrate", f"{int(v * 1.6)}k",
                      "-bufsize", f"{v * 2}k", "-pix_fmt", "yuv420p", "-passlogfile", "x264_2pass"]
            p1, p2 = [*common, "-pass", "1"], [*common, "-pass", "2"]
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", Path(src).resolve(), *p1, "-an", "-f", "null", "NUL"], cwd=logdir)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", Path(src).resolve(), *p2, "-c:a", "aac", "-b:a", "64k", "-ac", "1",
             "-movflags", "+faststart", Path(dst).resolve()], cwd=logdir)
        size = Path(dst).stat().st_size
        if size <= UPLOAD_LIMIT:
            return size, v
        v = int(v * UPLOAD_LIMIT / size * 0.95)
    sys.exit(f"上传版压不到 {UPLOAD_LIMIT} 字节以内（最后 {size}）")


NUM = re.compile(r"\d+(?:\.\d+)?")
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9.\-]*\d[A-Za-z0-9.\-]*|[A-Z][A-Za-z]{2,}")
COMMON = {"AI", "CEO", "API", "The", "App", "OpenAI", "Anthropic", "Google"}


def page_text(url):
    if "news.google.com" in url:
        return False, "Google News 跳转链接，抓不到原文"
    try:
        r = httpx.get(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=25, follow_redirects=True)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        doc = lhtml.fromstring(r.content)
        for bad in doc.xpath("//script|//style|//noscript|//svg"):
            bad.drop_tree()
        return True, re.sub(r"\s+", " ", doc.text_content())
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:60]}"


def fact_check(sc):
    """For every line: numbers and latin names that do not appear in any of its item's source pages."""
    cache, out = {}, []
    for i, n in enumerate(sc["news"], 1):
        pages = []
        for r in n.get("refs") or []:
            u = r.get("url", "")
            if u and u not in cache:
                cache[u] = page_text(u)
            if u:
                pages.append(cache[u])
        corpus = " ".join(t for ok, t in pages if ok).lower()
        for ln in n["lines"]:
            txt = ln["text"]
            toks = [t for t in dict.fromkeys(NUM.findall(txt) + LATIN.findall(txt)) if t not in COMMON]
            # “116亿” = 11.6 billion, “18亿” = 1.8 billion, “3万” = 30,000 / 30K: accept the English forms too
            alt = {}
            for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(亿|万)", txt):
                v = float(num) / 10 if unit == "亿" else float(num) * 10
                s = f"{v:g}"
                alt[num] = [s, s + "k"] if unit == "万" else [s]
            def found(t):
                return t.lower() in corpus or any(a.lower() in corpus for a in alt.get(t, []))
            missing = [t for t in toks if not found(t)] if corpus else toks
            out.append({"item": i, "text": txt, "tokens": toks, "missing": missing, "no_source": not corpus})
    return out, cache


def chapters_lines(ep, ep_json):
    p = ep / f"{ep_json['dir_name']}_章节.txt"
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\d{1,2}:\d{2}", l.strip())]


DESC_LIMIT = 2000     # B 站简介上限；9/28 那期 8 条、19 个网址已经 1996 字


def desc_len(s):
    return len(s.encode("utf-16-le")) // 2      # 按网页里 JS 的字符串长度算（表情符号算 2）


def build_publish_info(ep, ep_json, sc, upload_path, dur):
    news = sc["news"]
    tags = list(BASE_TAGS)
    for n in news:
        for org in re.split(r"\s*/\s*", n.get("org") or ""):
            t = ORG_TAGS.get(org)
            if t and t not in tags and len(tags) < 8:
                tags.append(t)
    tags += [t for t in ("鲸鱼娘", "大肥鱼") if t not in tags][: 10 - len(tags)]
    chap = chapters_lines(ep, ep_json)
    # 投稿页的简介是 Quill 编辑器：行首打“1. ”会自动变成有序列表，编号重复成“2. 2.”，所以用圈号
    num = "①②③④⑤⑥⑦⑧⑨⑩"
    src_lines = []
    for i, n in enumerate(news):
        refs = " ；".join(f"{r.get('name', '')} {r.get('url', '')}".strip() for r in n.get("refs") or [])   # 空格隔开，网址后面不粘标点
        src_lines.append(f"{num[i]} {n['headline']}：{refs}")
    exported = load_json(ep / "candidates.json", {}).get("meta", {}).get("exported_cst", "")
    head = [f"AI每日日报 · {ep_json['date_label']}（{ep_json.get('weekday', '')}）", "鲸鱼娘带你看看 AI 圈发生了什么。", ""]
    toc = ["今日内容", *(chap or [f"{num[i]} {n['headline']}" for i, n in enumerate(news)]), ""]
    tail = ["来源", *src_lines, "",
            "说明",
            f"· 信息截至北京时间 {exported or ep_json['date']}，以各家官方发布为准。",
            "· 本期配音由 AI 合成（Fish Audio「苏晓晓」）；内容由 AI 整理，并自动核对来源，如有出入以原文为准。",   # 全自动：没有人工审核，不能写“经人工审核”
            "· 主播鲸鱼娘（像素素材包「大肥鱼」）是 DeepSeek 的网友拟人同人（原型：上善无形，CC BY-NC-SA 4.0；女仆造型：ZipZipPipe），与 DeepSeek 官方无关。"]
    desc = "\n".join(head + toc + tail)
    if desc_len(desc) > DESC_LIMIT:
        # 超出时先去掉时间表（过审后 B 站分段章节有同样的时间点）；来源和说明不能删，还超就由 gate 挡住
        desc = "\n".join(head + tail)
    return {
        "title": ep_json["title"],
        "video": str(upload_path), "video_seconds": round(dur, 2),
        "cover_16x9": str(ep / "封面" / "封面_16x9_1920x1080.png"), "cover_4x3": str(ep / "封面" / "封面_4x3_1440x1080.png"),
        "partition": "人工智能", "partition_fallback": "科技数码",
        "tags": tags[:10], "collection": "AI每日日报", "declaration": "含AI生成内容",
        "description": desc,
    }


def write_review(ep, ep_json, sc, checks, cache, info, final_mp4, upload_size, dur):
    L = [f"# 审稿单 · {ep_json['title']}", "",
         f"- 成片：`{final_mp4}`（{int(dur // 60)}:{int(dur % 60):02d}）",
         f"- 上传版：`{info['video']}`（{upload_size / 1e6:.2f} MB，给浏览器插件上传）",
         f"- 封面预览：`{ep / '封面' / '封面_预览.png'}`",
         "", "全自动模式：`daily.py gate`（自动检查 + AI 复核）通过后定时发布；这份审稿单是本期记录。", ""]
    by_item = {}
    for c in checks:
        by_item.setdefault(c["item"], []).append(c)
    for i, n in enumerate(sc["news"], 1):
        L += [f"## {i}. {n['headline']}", f"- 来源：{n.get('source', '')}　日期：{n.get('date', '')}",
              "- 要点：" + "；".join(f"{j + 1}. {p}" for j, p in enumerate(n.get("points") or []))]
        for k, c in enumerate(by_item.get(i, []), 1):
            mark = "✓" if not c["missing"] else ("⚠ 来源页抓不到，无法自动核对" if c["no_source"] else "⚠ 原文里没找到：" + "、".join(c["missing"]))
            L.append(f"  {k}. {c['text']}　〔{mark if c['tokens'] or c['no_source'] else '—'}〕")
        for r in n.get("refs") or []:
            ok = cache.get(r.get("url", ""), (None, ""))
            L.append(f"  - {r.get('name', '')}：{r.get('url', '')}" + ("" if ok[0] else f"（抓取：{ok[1]}）"))
        L.append("")
    L += ["核对只查“句子里的数字和英文名在来源页里有没有出现”：✓ = 都找到了；⚠ = 没找到（意译、换算或来源页抓不到）——全自动模式下 ⚠ 会挡住发布，要改台本。", ""]
    cands = load_json(ep / "candidates.json", {}).get("candidates", [])
    used = {r.get("url") for n in sc["news"] for r in n.get("refs") or []}
    rest = [c for c in cands if c["url"] not in used][:10]
    if rest:
        L += ["## 没选的候选（前 10）"] + [f"- {c['cid']}（{c['score']}）{c['title'][:70]}｜{c['source']}" for c in rest] + [""]
    L += ["## B 站投稿信息", f"- 标题：{info['title']}",
          f"- 分区：{info['partition']}（投稿页只有一级分区；没有就用 {info['partition_fallback']}）",
          f"- 标签：{'、'.join(info['tags'])}", f"- 合集：{info['collection']}（已建好，在“加入合集”下拉里选）", f"- 创作声明：{info['declaration']}",
          "- 简介：", "```text", info["description"], "```", ""]
    (ep / "审稿单.md").write_text("\n".join(L), encoding="utf-8")


def cmd_render(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    run([sys.executable, YL / "build_timeline.py", ep, "--series", SERIES])
    run([sys.executable, YL / "mix_audio.py", ep, "--series", SERIES])
    # 2340x1080（iPhone 全面屏 19.5:9）：本技能自己的宽屏拼接脚本（《原LAI如此》的 assemble.py 是 1920x1080，不动它）
    run([sys.executable, SK / "assemble_wide.py", ep, "--series", SERIES, "--workers", str(a.workers)] + (["--skip-main"] if a.skip_main else []))
    run([sys.executable, SK / "make_cover_white.py", ep, "--from-script"])   # 2026-09-28 起：白底两行大字 + 鲸鱼娘右下 + 其余新闻小字（旧版 make_cover.py 留着不用）
    ep_json = load_json(ep / "episode.json")
    final = ep / f"{ep_json['dir_name']}_成片.mp4"
    upload = ep / f"{ep_json['dir_name']}_上传版.mp4"
    size, kbps = encode_upload(final, upload, ep / "制作" / "build", "h264" if a.x264 else "hevc")
    print(f"上传版 {size / 1e6:.2f} MB（{'H.264' if a.x264 else 'H.265'}，视频 {kbps} kbps）")
    cmd_review(a, st)


def cmd_review(a, st=None):
    """Fact check + 审稿单.md + 投稿信息.json only (the video, cover and upload version must exist)."""
    ep = ep_dir(a.date)
    st = st or load_state(ep)
    ep_json = load_json(ep / "episode.json")
    sc = load_json(ep / "台本.json")
    final = ep / f"{ep_json['dir_name']}_成片.mp4"
    upload = ep / f"{ep_json['dir_name']}_上传版.mp4"
    dur = ffprobe_duration(final)
    size = upload.stat().st_size
    checks, cache = fact_check(sc)
    (ep / "制作" / "source_pages.json").write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")   # gate 复用，不再重新抓
    info = build_publish_info(ep, ep_json, sc, upload, dur)
    (ep / "投稿信息.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    write_review(ep, ep_json, sc, checks, cache, info, final, size, dur)
    n_warn = sum(1 for c in checks if c["missing"])
    save_state(ep, st, "render", seconds=round(dur, 2), upload_bytes=size, check_warnings=n_warn)
    print(f"\n审稿单：{ep / '审稿单.md'}（核对提示 {n_warn} 处）、成片 {final}\n下一步：daily.py gate（自动检查）→ AI 复核 → 再跑一次 gate")


# ---------------------------------------------------------------- gate（全自动发布前的闸门）
REVIEW_FILE = "审核_复核.json"     # AI 复核（独立的子代理）写：{"verdict": "pass"|"fail", "script_sha", "issues": [...], "checked": [...]}


def cmd_gate(a):
    """所有 block 级检查都通过、而且 AI 复核通过（针对当前 台本.json），才算 PASS（退出码 0）；否则 FAIL（退出码 1）。
    结果写到 审核记录.json。review 级命中（新闻里可能正常出现的词）交给 AI 复核逐条确认。"""
    sys.path.insert(0, str(SK))
    import safety
    from make_episode import validate
    ep = ep_dir(a.date)
    st = load_state(ep)
    ep_json = load_json(ep / "episode.json") or {}
    sc = load_json(ep / "台本.json") or {}
    info = load_json(ep / "投稿信息.json") or {}
    name = ep_json.get("dir_name", "")
    final, upload, srt = ep / f"{name}_成片.mp4", ep / f"{name}_上传版.mp4", ep / f"{name}_字幕.srt"
    checks = []

    def add(check, ok, detail="", level="block"):
        checks.append(dict(check=check, ok=bool(ok), level="ok" if ok else level, detail=detail))

    errs, warns, total = validate(sc)
    add("台本检查", not errs, "；".join(errs) or f"{len(sc.get('news', []))} 条，约 {total} 字")
    if warns:
        add("台本提示", False, "；".join(warns), level="warn")
    add("成片", final.exists(), str(final))
    add("上传版 ≤ 9 MB", upload.exists() and upload.stat().st_size <= UPLOAD_LIMIT,
        f"{upload.stat().st_size / 1e6:.2f} MB" if upload.exists() else "没有上传版")
    add("封面", all((ep / "封面" / f).exists() for f in ("封面_16x9_1920x1080.png", "封面_4x3_1440x1080.png")), "16:9 + 4:3")
    d = datetime.fromisoformat(sc.get("date") or "2000-01-01")
    want_title = f"{d.month}月{d.day}日，鲸鱼娘带你看看AI圈发生了什么？"
    add("标题格式", info.get("title") == want_title, info.get("title", "没有 投稿信息.json"))
    refs = [r.get("url", "") for n in sc.get("news", []) for r in n.get("refs") or [] if r.get("url")]
    desc = info.get("description", "")
    miss = [u for u in refs if u not in desc]
    add("简介里有全部来源", "来源" in desc and not miss, ("缺：" + " ".join(miss)) if miss else f"{len(refs)} 个网址")
    extra = [u for u in re.findall(r"https?://[^\s；]+", desc) if u not in refs]
    add("简介里没有别的网址", not extra, " ".join(extra))
    add(f"简介 ≤ {DESC_LIMIT} 字", desc_len(desc) <= DESC_LIMIT,
        f"{desc_len(desc)} 字" + ("" if desc_len(desc) <= DESC_LIMIT else "：每条新闻的 refs 减到 2 个以内，或换短网址的来源"))
    dur = ffprobe_duration(final) if final.exists() else 0
    add("总时长超过 5 分钟（B 站分段章节要求）", dur > 302, f"{dur:.1f} 秒", level="warn")

    sel = load_json(ep / "配音" / "selection.json", {}) or {}
    low = {k: v.get("score") for k, v in sel.items() if isinstance(v, dict) and (v.get("score") or 0) < 0.75}
    add("配音识别分 ≥ 0.75", bool(sel) and not low, ("低：" + json.dumps(low, ensure_ascii=False)) if low else f"{len(sel)} 批")
    soft = {k: v.get("score") for k, v in sel.items() if isinstance(v, dict) and 0.75 <= (v.get("score") or 0) < 0.85}
    if soft:
        add("配音识别分 < 0.85（多半是英文名）", False, json.dumps(soft, ensure_ascii=False), level="warn")

    # 事实核对：复用 render 时抓的来源页
    pages = load_json(ep / "制作" / "source_pages.json", {}) or {}
    for u in refs:
        if u not in pages:
            pages[u] = page_text(u)
    fc = []
    for i, n in enumerate(sc.get("news", []), 1):
        corpus = " ".join(t for ok, t in (pages.get(r.get("url", ""), (False, "")) for r in n.get("refs") or []) if ok).lower()
        if not corpus:
            fc.append(f"第 {i} 条：来源页都抓不到，没法核对")
            continue
        for ln in n.get("lines") or []:
            txt = ln["text"]
            toks = [t for t in dict.fromkeys(NUM.findall(txt) + LATIN.findall(txt)) if t not in COMMON]
            alt = {num: [f"{float(num) / 10 if unit == '亿' else float(num) * 10:g}"]
                   for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(亿|万)", txt)}
            bad = [t for t in toks if t.lower() not in corpus and not any(x.lower() in corpus for x in alt.get(t, []))]
            if bad:
                fc.append(f"第 {i} 条「{txt[:24]}」原文里没找到：{'、'.join(bad)}")
    add("事实核对（数字、英文名都在原文里）", not fc, "；".join(fc) or "全部找到")

    # 内容安全：成品 + 来源页
    srt_text = srt.read_text(encoding="utf-8") if srt.exists() else ""
    hits = safety.scan_episode(sc, info, srt_text)
    for u in refs:
        ok, text = pages.get(u, (False, ""))
        if ok:
            hits += safety.scan_source(text, u)
    blocks = [h for h in hits if h["level"] == "block"]
    reviews = [h for h in hits if h["level"] == "review"]
    add("内容安全（色情、暴力、时政、广告、提示词注入、隐藏字符）", not blocks,
        "；".join(f"[{h['cat']}] {h['where']}：{h['word']}（…{h['context']}…）" for h in blocks[:12]) or "没有命中")
    if reviews:
        add("要 AI 复核确认的词", False, "；".join(f"[{h['cat']}] {h['where']}：{h['word']}" for h in reviews[:20]), level="warn")

    # 已播去重：最近 7 天播过的原文网址不再用
    aired = [json.loads(l) for l in AIRED.read_text(encoding="utf-8").splitlines() if l.strip()] if AIRED.exists() else []
    cutoff = (d - timedelta(days=7)).strftime("%Y-%m-%d")
    old = {r.get("url") for x in aired if cutoff <= x.get("date", "") < sc.get("date", "") for r in x.get("refs", [])}
    dup = [u for u in refs if u in old]
    add("没有重复最近 7 天播过的原文", not dup, " ".join(dup))

    rv = load_json(ep / REVIEW_FILE, {}) or {}
    cur = sha(ep / "台本.json")
    rv_ok = rv.get("verdict") == "pass" and rv.get("script_sha") == cur
    add("AI 复核（独立子代理，看成品和原文）", rv_ok,
        ("通过" if rv_ok else f"没有针对当前台本（sha {cur}）的通过结论")
        + (("：" + "；".join(map(str, rv.get("issues", []))))[:400] if rv.get("issues") else ""))

    passed = all(c["ok"] or c["level"] != "block" for c in checks)
    (ep / "审核记录.json").write_text(json.dumps({"date": sc.get("date"), "script_sha": cur, "passed": passed,
                                                 "checked_at": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
                                                 "checks": checks, "hits": hits}, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in checks:
        mark = "✓" if c["ok"] else ("✗" if c["level"] == "block" else "!")
        print(f"{mark} {c['check']}：{str(c['detail'])[:300]}")
    save_state(ep, st, "gate", passed=passed, script_sha=cur)
    print("\nGATE PASS：可以定时发布" if passed else "\nGATE FAIL：有 ✗ 项，改好再跑（详见 审核记录.json）")
    sys.exit(0 if passed else 1)


# ---------------------------------------------------------------- chapters（B 站分段章节：稿件过审公开后才能加）
def cmd_chapters(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    bv = st["stages"].get("published", {}).get("bv")
    if a.done:
        save_state(ep, st, "chapters", bv=bv)
        print("已记录：分段章节加好了")
        return
    ep_json = load_json(ep / "episode.json") or {}
    rows = []
    for l in chapters_lines(ep, ep_json):
        m = re.match(r"^(\d{1,2}):(\d{2})\s+(.*)$", l)
        if m:
            rows.append({"time": f"{m.group(1)}:{m.group(2)}", "sec": int(m.group(1)) * 60 + int(m.group(2)), "title": m.group(3)[:20]})
    while len(rows) > 10:                   # B 站最多 10 段：去掉离前一段最近的那个切点
        gaps = [rows[i + 1]["sec"] - rows[i]["sec"] for i in range(len(rows) - 1)]
        rows.pop(gaps.index(min(gaps)) + 1)
    print(json.dumps({"bv": bv, "chapters": rows}, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- published / status
def cmd_published(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    sc = load_json(ep / "台本.json", {})
    with open(AIRED, "a", encoding="utf-8") as f:
        for n in sc.get("news", []):
            f.write(json.dumps({"date": a.date, "headline": n["headline"], "refs": n.get("refs", []), "bv": a.bv}, ensure_ascii=False) + "\n")
    save_state(ep, st, "published", bv=a.bv)
    print(f"已记录 {a.bv}，{len(sc.get('news', []))} 条写进 {AIRED}")


NEXT = {None: "daily.py init", "init": "选 6–8 条、查原文、写 台本.json，然后 daily.py build",
        "build": "Fish Audio 网页版配音（SKILL.md 第 5 步）→ daily.py webvoice --task …",
        "tts": "daily.py voice", "voice": "daily.py render", "render": "daily.py gate → AI 复核 → daily.py gate",
        "gate": "gate 通过：插件填 B 站投稿页、定时北京 06:00 投稿，然后 daily.py published --bv …（没通过：改台本重做）",
        "published": "公开后加 B 站分段章节（daily.py chapters），加好后 daily.py chapters --done", "chapters": "本期完成"}


def cmd_status(a):
    ep = ep_dir(a.date)
    st = load_state(ep)
    for k, v in st.get("stages", {}).items():
        print(f"  {k:<10} {v}")
    print(f"下一步：{NEXT.get(st.get('last'))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "build", "webvoice", "tts", "voice", "render", "review", "gate", "published", "chapters", "status"):
        s = sub.add_parser(name)
        s.add_argument("--date", default=today_cst())
        if name == "init":
            s.add_argument("--hours", type=float)
            s.add_argument("--force", action="store_true")
        if name == "build":
            s.add_argument("--force", action="store_true", help="重新分批（台本改过时会自动加）")
            s.add_argument("--batches", action="store_true", help="保留按场景分批（只在网页版单次放不下整期时用）；默认整期一批，一次生成")
        if name == "webvoice":
            s.add_argument("--task", action="append", required=True, help="网页版的任务编号（32 位十六进制；一次出两个版本就写两次 --task）")
            s.add_argument("--probe", action="store_true", help="只找音频地址、打印出来，不下载、不改文件")
        if name == "tts":
            s.add_argument("--api", action="store_true", help="用户点名要用 API 时才加（2026-09-29 起默认用网页版）")
            s.add_argument("--takes", type=int, default=1, help="每批几个版本（默认 1）")
            s.add_argument("--model", default="s1", help="s1（默认，和首期同一个模型）；s2.1-pro-free（免费）只在用户点名时用，"
                                                          "余额不足（402）改用网页版，见 SKILL.md 第 5 步")
        if name == "voice":
            s.add_argument("--hist", help="配音/raw/ 下的 urls_hist.txt（从 Fish Audio 历史记录抓到的 CDN 地址）")
        if name == "render":
            s.add_argument("--workers", type=int, default=4)   # 2026-09-28 用户定：所有渲染统一 4 路并行
            s.add_argument("--skip-main", action="store_true")
            s.add_argument("--x264", action="store_true", help="上传版用 H.264（B 站不收 H.265 时的退路）")
        if name == "published":
            s.add_argument("--bv", required=True)
        if name == "chapters":
            s.add_argument("--done", action="store_true", help="B 站分段章节已加好，记进 state.json")
    a = ap.parse_args()
    {"init": cmd_init, "build": cmd_build, "webvoice": cmd_webvoice, "tts": cmd_tts, "voice": cmd_voice, "render": cmd_render, "review": cmd_review,
     "gate": cmd_gate, "published": cmd_published, "chapters": cmd_chapters, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
