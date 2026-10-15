# -*- coding: utf-8 -*-
"""下载 logo 到 制作/assets/logos/，把来源、状态码、大小、sha256 记进 _manifest.json（增量更新）。

清单文件是 JSON 数组：[{"id": "kimi", "url": "https://…", "file": "kimi.svg"}, …]
用法：python fetch_logos.py <清单.json>
只用 curl 下载，单个文件 ≤ 2 MB，不执行任何下载来的东西。
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets" / "logos"
MANIFEST = OUT / "_manifest.json"
MAX = 2 * 1024 * 1024


def main():
    todo = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    for it in todo:
        dst = OUT / it["file"]
        r = subprocess.run(
            ["curl", "-sS", "-L", "-m", "40", "--max-filesize", str(MAX), "-A", "Mozilla/5.0 (video-prep)",
             "-o", str(dst), "-w", "%{http_code}", it["url"]],
            capture_output=True, text=True)
        code = r.stdout.strip()
        ok = code == "200" and dst.exists() and dst.stat().st_size > 0
        info = {"id": it["id"], "url": it["url"], "http": code, "ok": ok,
                "size": dst.stat().st_size if dst.exists() else 0,
                "sha256": hashlib.sha256(dst.read_bytes()).hexdigest() if ok else None,
                "when": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": it.get("note", "")}
        if not ok and dst.exists():
            dst.unlink()          # 失败的不留半截文件
        manifest[it["file"]] = info
        print(f"{'OK ' if ok else 'ERR'} {code} {info['size']:>7}B  {it['file']:34s} {it['url']}")
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
