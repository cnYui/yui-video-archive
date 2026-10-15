async (page) => {
  await page.goto('https://member.bilibili.com/platform/upload/video/frame');
  await page.locator('input[type="file"][accept*=".mp4"]').first().waitFor({state:'attached',timeout:30000});
  return {url:page.url(),text:(await page.locator('body').innerText()).slice(-7000),inputs:await page.locator('input').evaluateAll(ns=>ns.map(x=>({type:x.type,accept:x.accept,placeholder:x.placeholder})))};
}
