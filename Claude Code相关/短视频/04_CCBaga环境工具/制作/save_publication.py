"""从已完成的浏览器核验结果更新本期发布台账，避免凭页面跳转推断发布成功。"""
import json
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
QUEUE = Path('C:/Users/yui/AppData/Local/Temp/pw_ccbaga_20261014')
creator = public = listing = statement = None
for path in sorted(QUEUE.glob('*.out.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:15]:
    output=json.loads(path.read_text(encoding='utf-8')).get('text','')
    if '### Result' not in output:
        continue
    try:
        value,_=json.JSONDecoder().raw_decode(output.split('### Result',1)[1].lstrip())
    except ValueError:
        continue
    if isinstance(value,dict) and value.get('archive',{}).get('bvid')=='BV1CxpC69ESE':
        if 'covers' in value:
            creator=value
        if value.get('endpoint')=='/x/web/archives':
            listing=value
    if isinstance(value,list):
        for item in value:
            if item.get('source')==1 and item.get('bvid')=='BV1CxpC69ESE':
                public=item
            if item.get('source')==0 and item.get('creation_statement'):
                statement=item
if not creator or not public or not listing or not statement:
    raise SystemExit('缺少三个接口的核验结果，未更新台账。')
info_path=EP/'投稿信息.json'
info=json.loads(info_path.read_text(encoding='utf-8'))
assert creator['archive']['title']==info['bilibili']['title']
assert creator['archive']['desc']==info['bilibili']['desc']
assert public['state']==0 and listing['archive']['state']==0
assert public['season']['id']==9223239
assert statement['creation_statement']['content']=='含AI生成内容'
assert (creator['covers']['cover']['width'],creator['covers']['cover']['height'])==(1920,1080)
assert (creator['covers']['cover43']['width'],creator['covers']['cover43']['height'])==(1440,1080)
verified_at=datetime.now().astimezone().isoformat(timespec='seconds')
evidence=dict(verified_at=verified_at,archive_view=creator,public_view=public,archives=listing,declaration=statement)
(HERE/'B站发布核验.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
published=dict(url='https://www.bilibili.com/video/BV1CxpC69ESE/',bvid='BV1CxpC69ESE',aid=117438129702417,cid=42732094824,posted_at='2026-10-14T15:41:19+08:00',verified_at=verified_at,state=0,state_desc='开放浏览',title=public['title'],duration_s=public['duration'],category_tid=231,collection=public['season'],declaration=statement['creation_statement'],tags=creator['archive']['tag'].split(','),covers=creator['covers'],uploaded_file=str(EP/'CCBaga_成片.mp4'),uploaded_size_bytes=7156553,evidence='制作/B站发布核验.json')
info['bilibili']['published']=published
info['published']['bilibili']=published
info['publish_status']='published'
info.pop('publish_blocker',None)
info_path.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
media_args=HERE/'pw_media_args.json'
if media_args.exists():
    shutil.move(str(media_args),str(QUEUE/'media_args_已用.json'))
print(json.dumps(dict(bvid=published['bvid'],state=published['state_desc'],evidence=str(HERE/'B站发布核验.json')),ensure_ascii=False))
