"""只传入用户已授权的本期小文件；避免把媒体编码和浏览器连接令牌写到输出。"""
import base64
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parent
media = Path(sys.argv[1]).resolve()
media.relative_to(EP)
raw = media.read_bytes()
if len(raw) >= 10_000_000:
    raise SystemExit('文件达到 10 MB，停止上传。')
selector = sys.argv[2]
mime = 'video/mp4' if media.suffix == '.mp4' else 'image/png'
payload = dict(base64=base64.b64encode(raw).decode('ascii'), name=media.name, mime=mime, selector=selector)
code = '''async (page) => {
  if (!page.url().startsWith('https://member.bilibili.com/')) throw new Error('页面不是 B站创作中心');
  const result = await page.evaluate((data) => {
    const input = document.querySelector(data.selector);
    if (!input || input.type !== 'file') throw new Error('未找到目标文件输入框');
    const bytes = Uint8Array.from(atob(data.base64), c=>c.charCodeAt(0));
    const file = new File([bytes], data.name, {type:data.mime});
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    input.dispatchEvent(new Event('change', {bubbles:true}));
    return {name:file.name,size:file.size,selected:input.files.length};
  }, PAYLOAD);
  return {file:result,text:(await page.locator('body').innerText()).slice(-10000)};
}'''.replace('PAYLOAD',json.dumps(payload,ensure_ascii=False))
arg = Path('C:/Users/yui/AppData/Local/Temp/pw_rea_20261014/media_args.json')
arg.write_text(json.dumps(dict(code=code),ensure_ascii=False),encoding='utf-8')
command = [sys.executable,'-W','ignore','D:/大疆/docs/pw/pw_do.py','--queue','C:/Users/yui/AppData/Local/Temp/pw_rea_20261014','browser_run_code_unsafe','@'+str(arg)]
r = subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace')
out = re.sub(r'### Ran Playwright code[\s\S]*?(?=### Page|### Events|\Z)','',r.stdout+r.stderr)
out = re.sub(r'(token=)[^\s&\)\]]+',r'\1[已脱敏]',out)
print(out)
sys.exit(r.returncode)
