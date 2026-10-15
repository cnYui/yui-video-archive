async (page) => {
  return {url:page.url(),text:await page.locator('body').innerText(),inputs:await page.locator('input').evaluateAll(nodes=>nodes.map(x=>({type:x.type,accept:x.accept,placeholder:x.placeholder,class:x.className,value:x.type==='file'?'':x.value}))) };
}
