"""已发布作品的本地视频清理清单（只读，不删任何东西）。

    python build_manifest.py [--registry published_works.json] [--out manifest.csv]

只扫 published_works.json 里登记的作品目录，只列视频文件；路径里有 protected_components（素材 / 参考分析 / proxy /
共用片头片尾 / 测试目录…）的一律跳过。登记的作品如果 `投稿信息.json` 里 approval.status 还是 pending，直接报错退出。
输出的 CSV 交给 recycle.ps1 去移进回收站。规则和踩过的坑见同目录 README.md。
"""
import argparse
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO_EXT = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v', '.flv', '.wmv'}


def kind_of(parts, name):
    """只用来在汇总里分类，不影响删不删。"""
    j = '\\'.join(parts)
    if '_旧稿' in j or '\\_旧\\' in ('\\' + j + '\\') or '旧字幕版' in j:
        return 'old-version'
    if '02_出镜\\edit' in j:
        return 'facecam-edit'
    if '01_录屏剪辑' in j:
        return 'screen-cut'
    if '03_成片' in j:
        return 'final/preview'
    if re.search(r'(成片|上传版|手机预览|手机版)', name) and '制作' not in parts:
        return 'final/preview'
    if 'parts' in parts or 'build' in parts or '00_整片' in j or 'scenes' in parts or 'clips' in parts:
        return 'render-intermediate'
    if '制作' in parts:
        return 'production-other'
    return 'final/preview'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default=os.path.join(HERE, 'published_works.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'manifest.csv'))
    a = ap.parse_args()

    reg = json.load(open(a.registry, encoding='utf-8'))
    root = os.path.normpath(reg['root'])
    protected = set(reg['protected_components'])

    rows, missing, pending = [], [], []
    for w in reg['works']:
        base = os.path.normpath(os.path.join(root, w['dir']))
        if not os.path.isdir(base):
            missing.append(w['dir'])
            continue
        # 守卫：还没发布的不许清
        info = os.path.join(base, '投稿信息.json')
        if os.path.isfile(info):
            try:
                st = (json.load(open(info, encoding='utf-8')).get('approval') or {}).get('status')
            except Exception:
                st = None
            if st == 'pending':
                pending.append(w['label'])
        inc = re.compile(w['include'], re.I) if w.get('include') else None
        exc = re.compile(w['exclude'], re.I) if w.get('exclude') else None
        for dp, dn, fn in os.walk(base):
            rel_dir = os.path.relpath(dp, base)
            parts = [] if rel_dir == '.' else rel_dir.split('\\')
            dn[:] = [d for d in dn if d not in protected]
            for f in fn:
                if os.path.splitext(f)[1].lower() not in VIDEO_EXT:
                    continue
                rel = '\\'.join(parts + [f])
                if inc and not inc.search(rel):
                    continue
                if exc and exc.search(rel):
                    continue
                p = os.path.join(dp, f)
                rows.append(dict(work=w['label'], kind=kind_of(parts, f), size=os.path.getsize(p),
                                 mtime=os.path.getmtime(p), path=p))

    if pending:
        sys.exit('登记表里有 approval.status = pending 的作品（还没发布），先从 published_works.json 里拿掉：' + '、'.join(pending))
    with open(a.out, 'w', encoding='utf-8-sig', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=['work', 'kind', 'size', 'mtime', 'path'])
        wr.writeheader()
        wr.writerows(rows)

    print('目录不存在（已搬走 / 改名？）:', missing or '无')
    print(f'文件 {len(rows)} 个，共 {sum(r["size"] for r in rows)/1024**3:.2f} GiB  → {a.out}')
    by = {}
    for r in rows:
        d = by.setdefault(r['kind'], [0, 0])
        d[0] += 1
        d[1] += r['size']
    for k, (n, s) in sorted(by.items(), key=lambda x: -x[1][1]):
        print(f'  {k:20s} {n:5d} 个 {s/1048576:9.1f} MB')


if __name__ == '__main__':
    main()
