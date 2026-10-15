async (page) => {
  await page.getByText('查看进度',{exact:true}).click({force:true});
  await page.waitForTimeout(1800);
  return {url:page.url(),text:(await page.locator('body').innerText()).slice(0,10000),links:await page.locator('a[href]').evaluateAll(ns=>ns.filter(x=>/BV|aid=|type=edit/.test(x.href)).map(x=>({text:x.innerText,url:x.href})).slice(0,20))};
}
