async (page) => {
  await page.locator('.drop-list-v2-item[title="人工智能"]').click({force:true});
  for (let i=0;i<3;i++) await page.locator('.tag-pre-wrp .close').first().click({force:true});
  for (const tag of ['Claude','Claude Code','CCBaga','开源工具','AI工具','人工智能']) {
    const input=page.getByPlaceholder('按回车键Enter创建标签').first();
    await input.fill(tag);
    await input.press('Enter');
  }
  await page.getByText('请选择合集',{exact:true}).click({force:true});
  return {
    text:(await page.locator('body').innerText()).slice(-7500),
    tags:await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents(),
    desc:await page.locator('.ql-editor').first().evaluate(x=>({text:x.innerText,quill:!!x.parentElement.__quill,quillText:x.parentElement.__quill?.getText()})),
    cover:await page.locator('[class*=cover]').evaluateAll(nodes=>nodes.filter(x=>x.className.includes('cover')).slice(0,12).map(x=>({class:x.className,html:x.outerHTML.slice(0,1000)})))
  };
}
