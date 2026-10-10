"""用 iiilab 解析出的直链下载 YouTube 视频：1080p 画面 + 英文原声 → 本机 curl 下 → 校验字节数 → ffmpeg -c copy 合并。

输入文件每行一条：  <YouTube ID>|<视频直链（itag 137）>|<音频直链相对视频直链的差异参数>
  音频直链 = 视频直链去掉 aitags，再按差异参数替换 / 追加（和页面里 JS 的还原算法一致）。
用法：
  python dl_iiilab.py --out <输出目录> --names names.json links_a.txt [links_b.txt ...]
  names.json：{"<ID>": "文件名前缀"}，没写的用 ID。成片叫 <前缀>__<ID>.mp4。
合并后会删掉脚本自己下的分轨中间文件（<out>/_parts/ 里的 .v.mp4 / .a.m4a / .a.webm），不碰别的文件。
步骤和坑见同目录 README.md。
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
lock = threading.Lock()


def log(msg):
    with lock:
        print(time.strftime('%H:%M:%S ') + msg, flush=True)


def split_q(url):
    base, q = url.split('?', 1)
    return base, [tuple(s.split('=', 1)) for s in q.split('&')]


def build_audio(v, d):
    base, lv = split_q(v)
    rec = [(k, val) for (k, val) in lv if k != 'aitags']
    for s in d.split('&'):
        k, val = s.split('=', 1)
        for i, (k2, _) in enumerate(rec):
            if k2 == k:
                rec[i] = (k, val)
                break
        else:
            rec.append((k, val))
    return base + '?' + '&'.join(f'{k}={val}' for k, val in rec)


def qget(url, key):
    for k, val in split_q(url)[1]:
        if k == key:
            return val
    return None


def fetch(url, path, want):
    if os.path.exists(path) and os.path.getsize(path) == want:
        return True
    for _ in range(3):
        p = subprocess.run(['curl', '-sS', '-L', '--fail', '-m', '1500', '-A', UA, '-o', path, url],
                           capture_output=True, text=True)
        sz = os.path.getsize(path) if os.path.exists(path) else -1
        if p.returncode == 0 and sz == want:
            return True
        log(f'  retry {os.path.basename(path)} rc={p.returncode} size={sz}/{want} {p.stderr.strip()[:100]}')
        time.sleep(2)
    return False


def job(out, parts, names, vid, vurl, aurl):
    name = f'{names.get(vid, vid)}__{vid}'
    final = os.path.join(out, name + '.mp4')
    if os.path.exists(final) and os.path.getsize(final) > 100000:
        log(f'{vid} already done')
        return
    xt = qget(aurl, 'xtags') or ''
    if 'dubbed' in xt:
        log(f'{vid} REFUSED: audio link is a dubbed track ({xt}); use the original-language itag 251 instead')
        return
    vwant, awant, aitag = int(qget(vurl, 'clen')), int(qget(aurl, 'clen')), qget(aurl, 'itag')
    vpath = os.path.join(parts, f'{vid}.v.mp4')
    apath = os.path.join(parts, f'{vid}.a.' + ('m4a' if aitag == '140' else 'webm'))
    log(f'{vid} start  video {vwant/1e6:.1f} MB  audio itag {aitag} {awant/1e6:.1f} MB')
    res = {}
    t1 = threading.Thread(target=lambda: res.__setitem__('v', fetch(vurl, vpath, vwant)))
    t2 = threading.Thread(target=lambda: res.__setitem__('a', fetch(aurl, apath, awant)))
    t1.start(); t2.start(); t1.join(); t2.join()
    if not (res.get('v') and res.get('a')):
        log(f'{vid} DOWNLOAD FAILED v={res.get("v")} a={res.get("a")}  (链接可能过期，重新解析)')
        return
    tmp_out = final + '.part.mp4'
    acodec = ['-c:a', 'copy'] if aitag == '140' else ['-c:a', 'aac', '-b:a', '192k']
    p = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vpath, '-i', apath, '-map', '0:v:0', '-map', '1:a:0',
                        '-c:v', 'copy', *acodec, '-movflags', '+faststart', tmp_out], capture_output=True, text=True)
    if p.returncode != 0:
        log(f'{vid} MERGE FAILED {p.stderr.strip()[:200]}')
        return
    os.replace(tmp_out, final)
    pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_name,width,height',
                         '-of', 'default=nw=1', final], capture_output=True, text=True)
    log(f'{vid} OK -> {name}.mp4  {os.path.getsize(final)/1e6:.1f} MB  ' + ' '.join(pr.stdout.split()))
    os.remove(vpath)
    os.remove(apath)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--names', default=None)
    ap.add_argument('links', nargs='+')
    a = ap.parse_args()
    names = json.load(open(a.names, encoding='utf-8')) if a.names else {}
    parts = os.path.join(a.out, '_parts')
    os.makedirs(parts, exist_ok=True)
    jobs = []
    for fn in a.links:
        for line in open(fn, encoding='utf-8'):
            line = line.strip()
            if line:
                vid, vurl, d = line.split('|')
                jobs.append((a.out, parts, names, vid, vurl, build_audio(vurl, d)))
    ths = [threading.Thread(target=job, args=j) for j in jobs]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    log('ALL DONE')


if __name__ == '__main__':
    sys.exit(main())
