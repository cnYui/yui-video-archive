async (page) => {
  await page.getByText('封面设置',{exact:true}).evaluate(x=>x.click());
  await page.getByText('个人空间封面（16:9）',{exact:true}).waitFor({timeout:15000});
  return {text:(await page.locator('body').innerText()).slice(-6500),files:await page.locator('input[type=file]').evaluateAll(ns=>ns.map(x=>({accept:x.accept,parent:x.parentElement.outerHTML.slice(0,600)})))};
}
