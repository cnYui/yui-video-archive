async (page) => {
  await page.getByPlaceholder('请输入稿件标题').fill('这个github开源项目防止你的Claude封号！ccbaga');
  await page.locator('.bcc-select').click({force:true});
  await page.locator('.bcc-option').filter({hasText:'含AI生成内容'}).click({force:true});
  await page.locator('.ql-editor').first().fill('CCBaga 把 Claude 本地身份归档、配套浏览器和环境核验放到一个桌面工作流中。\n\n标题围绕防封话题；项目明确：选择地区不改变公网 IP，绿色结果只说明本次已测项目匹配，不保证匿名、解封或账号获准。仅管理自己的身份，遵守 Anthropic 条款与支持地区，账号受限走官方申诉。\n\n项目与画面来源：https://github.com/liseami/CCBaga\n版本：2026年10月14日核对 v0.2.43；第三方开源项目，与 Anthropic 无隶属或背书关系。身份页面为项目原始组件的隔离预览，使用虚构身份；没有执行真实清理或网络修改。\n\n配音：本机 Qwen3-TTS 开源模型合成；中英双语字幕。背景音乐来自本项目既有系列素材。');
  await page.locator('.select-controller').click({force:true});
  return {
    text:(await page.locator('body').innerText()).slice(-10000),
    tagParent:await page.getByPlaceholder('按回车键Enter创建标签').first().evaluate(x=>x.parentElement.parentElement.outerHTML.slice(0,7000)),
    category:await page.locator('.drop-list-v2-item').evaluateAll(ns=>ns.map(x=>({text:x.innerText,html:x.outerHTML.slice(0,550)})))
  };
}
