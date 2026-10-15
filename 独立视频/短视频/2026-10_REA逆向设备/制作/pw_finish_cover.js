async (page) => {
  await page.getByText('完成',{exact:true}).click({force:true});
  return {
    text:(await page.locator('body').innerText()).slice(-7500),
    claude:await page.getByText('claude',{exact:true}).evaluateAll(ns=>ns.map(x=>({html:x.outerHTML,parent:x.parentElement.outerHTML.slice(0,700)}))),
    covers:await page.locator('.cover-main .cover-img').evaluateAll(ns=>ns.map(x=>({class:x.className,hasImage:!!x.style.backgroundImage}))),
    statement:await page.getByPlaceholder('请选择符合您视频内容的创作声明').inputValue()
  };
}
