async (page) => {
  return await page.evaluate(async () => {
    const reply=await fetch('/x/vupre/web/archive/view?bvid=BV1CxpC69ESE',{credentials:'include'}).then(r=>r.json());
    if (reply.code!==0) return {code:reply.code,message:reply.message};
    const data=reply.data, a=data.archive;
    const covers={};
    for (const key of ['cover','cover43']) {
      const url=a[key];
      covers[key]=await new Promise(resolve=>{
        const img=new Image();
        img.onload=()=>resolve({url,width:img.naturalWidth,height:img.naturalHeight});
        img.onerror=()=>resolve({url,error:true});
        img.src=url;
      });
    }
    return {code:reply.code,dataKeys:Object.keys(data),archiveKeys:Object.keys(a),archive:{aid:a.aid,bvid:a.bvid,title:a.title,desc:a.desc,tid:a.tid,tag:a.tag,season_id:a.season_id,state:a.state,state_desc:a.state_desc,attribute:a.attribute,dtime:a.dtime},covers,videos:data.videos?.map(v=>({filename:v.filename,title:v.title,duration:v.duration,cid:v.cid,status:v.status})),addit:data.addit};
  });
}
