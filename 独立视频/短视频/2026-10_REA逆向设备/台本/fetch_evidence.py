"""保存在线阅读的引用证据和 X 图片，保留来源；不克隆或安装 REA。"""
import concurrent.futures
import json
import re
import subprocess
import urllib.request
from pathlib import Path

MAT = Path(r'D:\大疆\独立视频\素材\2026-10_REA逆向设备')
MAT.mkdir(parents=True, exist_ok=True)
EVID = MAT / '证据'
EVID.mkdir(exist_ok=True)

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=60).read()

def save_repo(path, sha):
    u = f'https://raw.githubusercontent.com/morluto/rea/{sha}/{path}'
    b = get(u)
    (EVID / path.replace('/', '__')).write_bytes(b)
    s = b.decode('utf-8')
    relevant = [(i, l) for i,l in enumerate(s.splitlines(), 1) if re.search(r'binwalk|unblob|ghidra|mitmproxy|HAR|correlat|source.*locat|pull.*[Pp]ackage|apk|air condition|glasses',l,re.I)]
    return {'path':path,'url':u,'sha':sha}, relevant[:35]

def fetch_tweet(user, tid):
    d = json.loads(get(f'https://api.fxtwitter.com/{user}/status/{tid}'))
    (EVID / f'X_{user}_{tid}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    t = d['tweet']
    print('X',t['url'],t['text'])
    urls = []
    def visit(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k == 'original_img_url' and isinstance(v,str): urls.append(v)
                elif k == 'url' and isinstance(v,str) and v.startswith('https://pbs.twimg.com/media/'): urls.append(v)
                else: visit(v)
        elif isinstance(x,list):
            for v in x: visit(v)
    visit(t)
    rows = []
    for i,u in enumerate(dict.fromkeys(urls),1):
        ext = '.png' if '.png' in u else '.jpg'
        dst = MAT / f'X_{user}_{tid}_{i:02d}{ext}'
        dst.write_bytes(get(u))
        rows.append({'file':dst.name,'url':u,'post':t['url'],'author':user,'time':t.get('created_at')})
    (EVID / f'X_{tid}_图片来源.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    if t.get('article'):
        a=t['article']
        blocks=a.get('content',{}).get('blocks',[])
        (EVID/f'X_{tid}_文章.txt').write_text('\n'.join(b['text'] for b in blocks),encoding='utf-8')
    print('下载图片', len(rows))
    return rows

if __name__=='__main__':
    sha=subprocess.check_output(['gh','api','repos/morluto/rea/commits/main','--jq','.sha'],text=True).strip()
    meta=json.loads(subprocess.check_output(['gh','api','repos/morluto/rea'],text=True))
    (EVID/'github_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    paths=['README.md','LICENSE','docs/adb-device-analysis.md','docs/firmware-analysis.md','docs/web-network-captures.md','docs/web-source-location.md','src/adb/AdbProvider.ts','src/firmware/FirmwareProvider.ts']
    manifest=[]
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        for m,lines in ex.map(lambda p:save_repo(p,sha),paths):
            manifest.append(m)
            print(m['path'], '\n'+'\n'.join(f'{i}: {l}' for i,l in lines))
    (EVID/'在线代码来源.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    fetch_tweet('0xlangeai','2109544824135467312')
