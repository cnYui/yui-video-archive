async (page) => {
  return {
    runtime:{require:typeof require,Buffer:typeof Buffer,process:typeof process},
    inputs:await page.locator('input[type=file]').evaluateAll(nodes=>nodes.map(x=>({html:x.outerHTML,parent:x.parentElement.outerHTML.slice(0,2200)}))),
    upload:await page.locator('.upload-area').count()
  };
}
