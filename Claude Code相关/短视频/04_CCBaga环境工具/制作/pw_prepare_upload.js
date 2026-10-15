async (page) => {
  await page.goto('https://member.bilibili.com/platform/upload/video/frame');
  await page.locator('.upload-area').waitFor({timeout:30000});
  return {
    url:page.url(),
    text:await page.locator('body').innerText(),
    runtime:{require:typeof require,Buffer:typeof Buffer,process:typeof process},
    inputs:await page.locator('input').evaluateAll(nodes=>nodes.map(x=>({type:x.type,accept:x.accept,placeholder:x.placeholder,class:x.className})))
  };
}
