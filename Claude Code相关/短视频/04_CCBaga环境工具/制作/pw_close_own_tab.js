async (page) => {
  if (!page.url().startsWith('https://member.bilibili.com/')) throw new Error('当前不是本期投稿工作页，保留标签');
  await page.close();
  return {closed:true};
}
