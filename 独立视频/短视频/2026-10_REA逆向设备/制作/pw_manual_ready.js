async (page) => {
  const unused=page.getByText('不用了',{exact:true});
  if(await unused.count() && await unused.isVisible()) await unused.click({force:true});
  await page.bringToFront();
  return {url:page.url(),text:(await page.locator('body').innerText()).slice(-3000)};
}
