async (page) => {
  const title=await page.getByPlaceholder('请输入稿件标题').inputValue();
  const declaration=await page.getByPlaceholder('请选择符合您视频内容的创作声明').inputValue();
  const category=(await page.locator('.select-controller').innerText()).trim();
  const tags=await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents();
  const text=await page.locator('body').innerText();
  if (title!=='这个github开源项目防止你的Claude封号！ccbaga'||declaration!=='含AI生成内容'||category!=='人工智能'||tags.length!==6||!text.includes('Claude Code相关')||!text.includes('上传完成')) throw new Error('投稿前核对未通过');
  const network=[];
  const onResponse=async response=>{
    if (!/archive\/(add|submit)/.test(response.url())) return;
    try {
      const body=await response.json();
      network.push({path:new URL(response.url()).pathname,code:body.code,message:body.message,aid:body.data?.aid,bvid:body.data?.bvid});
    } catch {}
  };
  page.on('response',onResponse);
  await page.getByText('立即投稿',{exact:true}).click({force:true});
  let success=false;
  try {await page.getByText('稿件投递成功',{exact:false}).waitFor({timeout:30000});success=true;} catch {}
  page.off('response',onResponse);
  return {success,url:page.url(),network,text:(await page.locator('body').innerText()).slice(-6500),links:await page.locator('a[href]').evaluateAll(ns=>ns.filter(x=>/BV|archive\/|upload\//.test(x.href)).map(x=>({text:x.innerText,url:x.href})).slice(-15))};
}
