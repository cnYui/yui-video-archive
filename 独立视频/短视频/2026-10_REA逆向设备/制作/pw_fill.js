async (page) => {
  await page.getByPlaceholder('请输入稿件标题').fill("一个视频拆解最近爆火的“逆向一切”的 RAE 开源项目 从厂商 App 查到设备协议，自己的控制端能自己写吗？");
  await page.locator('.bcc-select').click({force:true});
  await page.locator('.bcc-option').filter({hasText:'含AI生成内容'}).click({force:true});
  await page.locator('.ql-editor').first().evaluate((x, text)=> {
    const q=x.parentElement.__quill;
    if (!q) throw new Error('未找到简介编辑器');
    q.setText(text,'user');
  }, "REA（Reverse Engineer Anything）把程序分析工具接给 Claude Code / Codex。本期直接在线阅读官方代码，拆解 ADB 获取 APK、HAR/mitmproxy 抓包分析、Binwalk/Unblob 固件解包和 Ghidra 分析的证据链。Star 为 2026-10-14 查询快照，约 21.8 万。\n\n源码：https://github.com/morluto/rea\nX 教程与原图：蓝哥AI @0xlangeai（https://x.com/0xlangeai/status/2109544824135467312）；@ResearchWang（https://x.com/ResearchWang/status/2109812002076143824）。\n菜单栏空调画面来自独立开源项目 MideaBar：https://github.com/Binaryify/MideaBar，仅作控制端示例，未声称由 REA 完成。固件链路需 Linux 与已有外部工具；是否能还原某台设备取决于协议、权限等。\n本地 Qwen3-TTS 合成配音，中英双语字幕。图片版权归原作者，本期作介绍与评论引用。");
  await page.locator('.select-controller').click({force:true});
  return {text:(await page.locator('body').innerText()).slice(-5500),categories:await page.locator('.drop-list-v2-item').evaluateAll(ns=>ns.map(x=>({text:x.innerText,title:x.title})))};
}