async (page) => {
  await page.locator('.drop-list-v2-item[title="人工智能"]').click({force:true});
  while(await page.locator('.tag-pre-wrp .close').count()) await page.locator('.tag-pre-wrp .close').first().click({force:true});
  const results=[];
  for(const tag of ['REA','开源','逆向工程','人工智能','Codex','Claude Code','智能家居','设备协议']) {
    const input=page.getByPlaceholder('按回车键Enter创建标签').first();
    await input.fill(tag);
    await page.waitForTimeout(800);
    await input.press('Enter');
    await page.waitForTimeout(900);
    results.push({tag,tags:await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents()});
  }
  await page.locator('.cover-main .cover-img').click({force:true});
  return {results,text:(await page.locator('body').innerText()).slice(-6000),files:await page.locator('input[type=file]').evaluateAll(ns=>ns.map(x=>({accept:x.accept,parent:x.parentElement.outerHTML.slice(0,700)})))};
}
