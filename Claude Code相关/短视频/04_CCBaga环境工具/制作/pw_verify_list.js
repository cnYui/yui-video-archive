async (page) => {
  return await page.evaluate(async () => {
    const observed=performance.getEntriesByType('resource').find(x=>x.name.includes('/x/web/archives'));
    const endpoint=observed?.name||new URL('/x/web/archives?status=pubed&pn=1&ps=10',location.origin).href;
    const reply=await fetch(endpoint,{credentials:'include'}).then(r=>r.json());
    const item=reply.data?.arc_audits?.find(x=>x.Archive?.bvid==='BV1CxpC69ESE'||x.archive?.bvid==='BV1CxpC69ESE');
    const a=item?.Archive||item?.archive;
    return {endpoint:new URL(endpoint).pathname,code:reply.code,found:!!a,archive:a?{aid:a.aid,bvid:a.bvid,title:a.title,state:a.state,state_desc:a.state_desc,tid:a.tid,duration:a.duration}:null,dataKeys:Object.keys(reply.data||{})};
  });
}
