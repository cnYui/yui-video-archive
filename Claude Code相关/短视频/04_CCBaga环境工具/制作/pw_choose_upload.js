async (page) => {
  if(!page.url().startsWith('https://member.bilibili.com/')) await page.goto('https://member.bilibili.com/platform/upload/video/frame');
  await page.locator('.upload-area').click();
}
