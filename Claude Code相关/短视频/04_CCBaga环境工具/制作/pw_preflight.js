async (page) => {
  await page.getByText('制作中...',{exact:true}).waitFor({state:'hidden',timeout:30000});
  const tagsBefore=await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents();
  if (!tagsBefore.some(t=>t.toLowerCase()==='claude')) {
    await page.locator('.hot-tag-item').filter({hasText:/^claude$/}).click({force:true});
    await page.waitForTimeout(2000);
  }
  return {
    title:await page.getByPlaceholder('请输入稿件标题').inputValue(),
    declaration:await page.getByPlaceholder('请选择符合您视频内容的创作声明').inputValue(),
    tags:await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents(),
    category:await page.locator('.select-controller').innerText(),
    desc:await page.locator('.ql-editor').first().evaluate(x=>x.parentElement.__quill.getText().replace(/\n$/,'')),
    collection:await page.locator('.season-enter-text-default').allTextContents(),
    text:(await page.locator('body').innerText()).slice(-6000),
    links:await page.locator('.cover-main .cover-img').evaluateAll(ns=>ns.map(x=>x.style.backgroundImage.startsWith('url("data:')?'data image':x.style.backgroundImage))
  };
}
