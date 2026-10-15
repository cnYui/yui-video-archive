"""复用已验证的页面操作结构，将本期文案和封面传给独立队列。"""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EP=HERE.parent
OLD=Path('D:/大疆/Claude Code相关/短视频/04_CCBaga环境工具/制作')
data=json.loads((EP/'投稿信息.json').read_text(encoding='utf-8'))
core='''async (page) => {
  await page.getByPlaceholder('请输入稿件标题').fill(TITLE);
  await page.locator('.bcc-select').click({force:true});
  await page.locator('.bcc-option').filter({hasText:'含AI生成内容'}).click({force:true});
  await page.locator('.ql-editor').first().evaluate((x, text)=> {
    const q=x.parentElement.__quill;
    if (!q) throw new Error('未找到简介编辑器');
    q.setText(text,'user');
  }, DESCRIPTION);
  await page.locator('.select-controller').click({force:true});
  return {text:(await page.locator('body').innerText()).slice(-5500),categories:await page.locator('.drop-list-v2-item').evaluateAll(ns=>ns.map(x=>({text:x.innerText,title:x.title})))};
}'''.replace('TITLE',json.dumps(data['bilibili']['title'],ensure_ascii=False)).replace('DESCRIPTION',json.dumps(data['bilibili']['desc'],ensure_ascii=False))
(HERE/'pw_fill.js').write_text(core,encoding='utf-8')
for name in ['pw_media.py','pw_cover_unsync.js','pw_cover_wide.js','pw_finish_cover.js']:
    content=(OLD/name).read_text(encoding='utf-8').replace('pw_ccbaga_20261014','pw_rea_20261014')
    (HERE/name).write_text(content,encoding='utf-8')
print('本期填表与封面操作脚本已准备。')
