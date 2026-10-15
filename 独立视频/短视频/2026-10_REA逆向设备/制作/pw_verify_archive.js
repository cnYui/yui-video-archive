async (page) => {
  return await page.evaluate(async () => {
    const r=await fetch('/x/vupre/web/archive/view?bvid=BV1JepC6EEk8',{credentials:'include'}).then(r=>r.json());
    if(r.code!==0) return {code:r.code,message:r.message};
    const a=r.data.archive;
    const covers={};
    for(const key of ['cover','cover43']) {
      covers[key]=await new Promise(resolve=>{const img=new Image();img.onload=()=>resolve({url:a[key],width:img.naturalWidth,height:img.naturalHeight});img.onerror=()=>resolve({url:a[key],error:true});img.src=a[key];});
    }
    return {code:r.code,archive:{aid:a.aid,bvid:a.bvid,title:a.title,desc:a.desc,tid:a.tid,tag:a.tag,state:a.state,state_desc:a.state_desc,season_id:a.season_id,creation_statement:a.creation_statement},covers,videos:r.data.videos?.map(v=>({duration:v.duration,cid:v.cid,title:v.title})),statement:r.data.creation_statement,dataKeys:Object.keys(r.data),statementFields:Object.fromEntries(Object.entries(a).filter(([k])=>/statement|ai|copyright|source/.test(k)))};
  });
}
