"""保存发布后的公开核验与封面比对，更新本期台账。"""
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
EP=HERE.parent
ROOT=Path('D:/大疆')
QUEUE=Path('C:/Users/yui/AppData/Local/Temp/pw_rea_20261014')
results=[]
for path in sorted(QUEUE.glob('*.out.json')):
    payload=json.loads(path.read_text(encoding='utf-8'))
    text=payload.get('text','')
    match=re.search(r'### Result\s*\n(\{.*?\})\s*\n###',text,re.S)
    if match:
        try: results.append(json.loads(match.group(1)))
        except json.JSONDecodeError: pass
archive=next(x for x in reversed(results) if x.get('archive',{}).get('bvid')=='BV1JepC6EEk8' and 'covers' in x)
public=next(x for x in reversed(results) if x.get('data',{}).get('bvid')=='BV1JepC6EEk8')
assert archive['archive']['state']==0 and public['code']==0
info_path=EP/'投稿信息.json'
info=json.loads(info_path.read_text(encoding='utf-8'))
assert archive['archive']['title']==info['bilibili']['title']
assert archive['archive']['desc']==info['bilibili']['desc']
assert archive['archive']['creation_statement']['id']==1
cover_scores={}
for key,ratio in [('cover','16x9'),('cover43','4x3')]:
    target=HERE/f'B站线上封面_{ratio}.jpg'
    urllib.request.urlretrieve(archive['covers'][key]['url'],target)
    online=np.array(Image.open(target).convert('RGB'),dtype=float)
    local=np.array(Image.open(HERE/f'04_封面/封面_选定_{ratio}.png').convert('RGB'),dtype=float)
    assert online.shape==local.shape
    score=float(10*np.log10(255**2/np.mean((online-local)**2)))
    assert score>30,score
    cover_scores[ratio]=score
now=datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds')
report=dict(verified_at=now,archive=archive,public=public,cover_psnr_db=cover_scores,upload_method='用户手动上传14.5MB完整原片，未压缩；Playwright JS上传两张小封面并点击发布')
(HERE/'B站发布核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
info['bilibili']['published']=dict(bvid='BV1JepC6EEk8',url='https://www.bilibili.com/video/BV1JepC6EEk8/',state='开放浏览',verified_at=now)
info['published']['bilibili']=info['bilibili']['published']
info['approval']['status']='published'
info_path.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(EP/'README.md').write_text('# REA 逆向设备短视频\n\n已发布 B 站：[BV1JepC6EEk8](https://www.bilibili.com/video/BV1JepC6EEk8/)，开放浏览。仅 B 站。\n\n封面：A 的 MideaBar 图片 + B 的“逆向一切 / 看见证据”文字。标题按用户原文，RAE 拼写保留。58.73 秒，1080×2340、30 fps，本地 Qwen3-TTS 配音、中英双语字幕。\n\n14.5 MB 原片由用户手动上传，未压缩；Playwright 完成文案、双比例封面、AI 声明、标签和发布。来源及交付说明见台本/交付说明.md，核验见制作/B站发布核验.json。\n',encoding='utf-8')
with (ROOT/'独立视频/README.md').open('a',encoding='utf-8') as f:
    f.write('\n- REA 逆向设备短视频（2026-10-14）：短视频/2026-10_REA逆向设备，58.73秒、本地Qwen配音；仅B站 [BV1JepC6EEk8](https://www.bilibili.com/video/BV1JepC6EEk8/)，开放浏览，封面B文字+A图片。\n')
with (ROOT/'短视频/README.md').open('a',encoding='utf-8') as f:
    f.write('\n- 2026-10-14 REA：独立视频/短视频/2026-10_REA逆向设备，仅B站 [BV1JepC6EEk8](https://www.bilibili.com/video/BV1JepC6EEk8/)，开放浏览；用户手动上传14.5MB原片，代理Playwright填表并发布。\n')
print(json.dumps(dict(bvid='BV1JepC6EEk8',state='开放浏览',cover_psnr_db=cover_scores,verified_at=now),ensure_ascii=False))
