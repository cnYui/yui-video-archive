async (page) => {
  await page.getByText('封面制作',{exact:true}).waitFor({state:'hidden',timeout:30000});
  const title=await page.getByPlaceholder('请输入稿件标题').inputValue();
  const expected='一个视频拆解最近爆火的“逆向一切”的 RAE 开源项目 从厂商 App 查到设备协议，自己的控制端能自己写吗？';
  const declaration=await page.getByPlaceholder('请选择符合您视频内容的创作声明').inputValue();
  const category=(await page.locator('.select-controller').innerText()).trim();
  const tags=await page.locator('.tag-pre-wrp .label-item-v2-content').allTextContents();
  const text=await page.locator('body').innerText();
  if(title!==expected||declaration!=='含AI生成内容'||category!=='人工智能'||tags.length!==8||!text.includes('上传完成')) throw new Error('投稿前核对失败');
  const network=[];
  const handler=async response=>{
    if(!/archive\/(add|submit)/.test(response.url())) return;
    try { const r=await response.json(); network.push({path:new URL(response.url()).pathname,code:r.code,message:r.message,aid:r.data?.aid,bvid:r.data?.bvid}); } catch {}
  };
  page.on('response',handler);
  await page.getByText('立即投稿',{exact:true}).click({force:true});
  let success=false;
  try {await page.getByText('稿件投递成功',{exact:false}).waitFor({timeout:30000});success=true;} catch {}
  page.off('response',handler);
  return {success,url:page.url(),network,text:(await page.locator('body').innerText()).slice(-4500)};
}
