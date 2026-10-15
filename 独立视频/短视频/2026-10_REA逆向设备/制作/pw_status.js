async (page) => {
  return {url:page.url(),text:(await page.locator('body').innerText()).slice(-5500),links:await page.locator('a[href]').evaluateAll(ns=>ns.filter(x=>/BV|archive\//.test(x.href)).map(x=>({text:x.innerText,url:x.href})).slice(-12))};
}
