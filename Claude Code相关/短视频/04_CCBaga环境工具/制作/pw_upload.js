async (page) => {
  await page.goto('https://member.bilibili.com/platform/upload/video/frame');
  await page.locator('input[type="file"][accept*=".mp4"]').first().waitFor({state:'attached',timeout:30000});
  await page.locator('input[type="file"][accept*=".mp4"]').first().setInputFiles('D:/大疆/Claude Code相关/短视频/04_CCBaga环境工具/CCBaga_成片.mp4');
  await page.waitForTimeout(6000);
  return await page.locator('body').innerText();
}
