async (page) => {
  return {
    text:await page.locator('body').innerText(),
    fields:await page.locator('input,textarea,[contenteditable=true]').evaluateAll(nodes=>nodes.map(x=>({tag:x.tagName,type:x.type,accept:x.accept,placeholder:x.placeholder,class:x.className,value:x.type==='file'?'':x.value,html:x.outerHTML.slice(0,500)}))),
    controls:await page.locator('.bcc-select,.select-controller,.cover-v2-container,.cover-container,.season-list,.season-input').evaluateAll(nodes=>nodes.map(x=>x.outerHTML.slice(0,1300)))
  };
}
