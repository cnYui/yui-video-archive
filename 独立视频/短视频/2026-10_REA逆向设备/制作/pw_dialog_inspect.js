async (page) => {
  return {url:page.url(),frames:page.frames().map(f=>({name:f.name(),path:(()=>{try{return new URL(f.url()).origin+new URL(f.url()).pathname;}catch{return f.url();}})()})),dialogs:await page.locator('[role=dialog],[class*=geetest],[class*=captcha],[class*=verify],[class*=risk]').evaluateAll(ns=>ns.map(x=>({class:x.className,text:x.innerText,visible:!!x.getBoundingClientRect().width})).slice(-20)),text:(await page.locator('body').innerText()).slice(-1800)};
}
