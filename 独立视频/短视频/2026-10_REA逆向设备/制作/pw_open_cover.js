async (page) => {
  await page.locator('.cover-main').hover();
  return {text:await page.locator('.cover-main').innerText(),controls:await page.locator('.cover-main').evaluate(x=>x.outerHTML.replace(/data:image[^"&]+/g,'[图片]').slice(-5500)),dialogs:await page.locator('[role=dialog]').count()};
}
