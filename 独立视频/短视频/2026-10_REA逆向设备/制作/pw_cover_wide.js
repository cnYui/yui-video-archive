async (page) => {
  await page.getByText('个人空间封面（16:9）',{exact:true}).click({force:true});
  return {
    text:(await page.locator('body').innerText()).slice(0,6500),
    checks:await page.locator('input[type=checkbox]').evaluateAll(ns=>ns.map(x=>({checked:x.checked,parent:x.parentElement.innerText}))),
    buttons:await page.locator('button').allTextContents()
  };
}
