// 原图和原文摘录保持来源可见；缓慢推近只帮助阅读。
for (const sg of TL.segs) {
  const c = TL.clips[sg.id];
  const image = c.ui.image;
  ovB(sg.s - 0.11, sg.e - 0.08, root => {
    const win = at(root, 0, 0, 1474, 829, '', {background:'#FAF9F5',overflow:'hidden'});
    const img = mk(win, '', {position:'absolute',inset:0,width:1474,height:829,objectFit:'contain'}, '', 'img');
    setSrc(img, 'media/' + image + '.png');
    if (!['S03','S05','S06'].includes(sg.id)) at(win, 28, 15, null, 58, '', {background:'rgba(20,20,19,.90)',color:'#fff',borderRadius:10,padding:'8px 18px',font:"700 29px 'Noto Sans SC'"}, {
      S01:'独立示例：MideaBar · 非 REA 实测',S02:'@0xlangeai · X 原图',S03:'GitHub API · 2026-10-14',S04:'morluto/rea · 官方 Hopper 截图',S05:'REA 文档 · ADB / 抓包',S06:'REA 固件文档 · 原文摘录',S07:'@0xlangeai · X 原图',S08:'独立示例：MideaBar · 非 REA 实测',S09:'@0xlangeai · X 原图'
    }[sg.id]);
    return lt => { img.style.transform = `scale(${1 + .015*clamp(lt/(sg.e-sg.s))})`; };
  });
}
// 需要两类抓包来源时切到网络捕获文档，不让画面只停在 ADB。
const mid5 = P('L05', '网络请求');
ovB(mid5, E('L05')+.4, root => {
  const img = mk(root,'',{position:'absolute',inset:0,width:1474,height:829,objectFit:'contain',background:'#101b2c'},'','img');
  setSrc(img,'media/captures.png');
  return () => {};
});
// 新补充原帖的工具分工图只用于说明分工，避免沿用它的绝对化封面。
const m7 = S('L07') + (E('L07')-S('L07'))*.56;
ovB(m7,E('L07')+.4,root=>{
  const img=mk(root,'',{position:'absolute',inset:0,width:1474,height:829,objectFit:'contain'},'','img');
  setSrc(img,'media/workflow.png');
  at(root,28,15,null,58,'',{background:'rgba(20,20,19,.9)',color:'#fff',borderRadius:10,padding:'8px 18px',font:"700 29px 'Noto Sans SC'"},'@ResearchWang · X 原图');
  return ()=>{};
});
big(S('L03'),E('L03')+.3,'21.8','万 Star','2026-10-14 · GitHub 查询快照');
linkPill(S('L02'),E('L02')+.3,'github.com/','morluto/<b>rea</b>');
linkPill(S('L04'),E('L07')+.3,'github.com/','morluto/<b>rea</b>');
linkPill(S('L08'),TL.total,'github.com/','morluto/<b>rea</b>');
ovP(S('L06'),E('L06')+.3,root=>{
  at(root,70,1405,940,50,'',{textAlign:'center',font:"700 34px 'Noto Sans SC'",color:'#535762'},'固件链路：Linux · 需自备外部工具');
  return ()=>{};
});
