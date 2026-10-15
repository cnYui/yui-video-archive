async (page) => {
  await page.getByText('Claude Code相关',{exact:true}).first().click({force:true});
  const tagResults=[];
  for (const tag of ['Claude','Claude Code','开源工具','AI工具']) {
    const input=page.getByPlaceholder('按回车键Enter创建标签').first();
    await input.fill(tag);
    await page.waitForTimeout(1200);
    await input.press('Enter');
    await page.waitForTimeout(1500);
    tagResults.push({tag,tags:await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents()});
  }
  await page.locator('.cover-main .cover-img').click({force:true});
  return {
    tagResults,
    text:(await page.locator('body').innerText()).slice(-8000),
    files:await page.locator('input[type=file]').evaluateAll(ns=>ns.map(x=>({accept:x.accept,html:x.outerHTML,parent:x.parentElement.outerHTML.slice(0,650)})))
  };
}
