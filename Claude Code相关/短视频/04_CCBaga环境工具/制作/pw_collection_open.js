async (page) => {
  await page.getByText('请选择合集',{exact:true}).first().click({force:true});
  return {
    text:(await page.locator('body').innerText()).slice(-7500),
    tags:await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents(),
    desc:await page.locator('.ql-editor').first().evaluate(x=>({text:x.innerText,quill:!!x.parentElement.__quill,quillText:x.parentElement.__quill?.getText()})),
    cover:await page.locator('[class*=cover]').evaluateAll(nodes=>nodes.slice(0,12).map(x=>({class:x.className,html:x.outerHTML.slice(0,1000)})))
  };
}
