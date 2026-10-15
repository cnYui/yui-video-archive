async (page) => {
  return {text:(await page.locator('body').innerText()).slice(-6000),files:await page.locator('input[type=file]').evaluateAll(ns=>ns.map(x=>({accept:x.accept,parent:x.parentElement.outerHTML.slice(0,800)}))),cover:await page.locator('[class*=cover]').evaluateAll(ns=>ns.slice(0,14).map(x=>({class:x.className,html:x.outerHTML.slice(0,1100)})))};
}
