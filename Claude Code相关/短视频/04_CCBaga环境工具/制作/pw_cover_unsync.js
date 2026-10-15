async (page) => {
  const checked=await page.locator('.sync.ratio_16_9 input[type=checkbox]').isChecked();
  if (checked) await page.locator('.sync.ratio_16_9 .sync-checkbox').click({force:true});
  return {sync:await page.locator('.sync.ratio_16_9 input[type=checkbox]').isChecked()};
}
