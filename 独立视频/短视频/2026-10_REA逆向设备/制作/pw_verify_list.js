async (page) => {
  return await page.evaluate(async () => {
    const response=await fetch('/x/web/archives?pn=1&ps=10&status=is_pubing,pubed,not_pubed',{credentials:'include'}).then(r=>r.json());
    return {code:response.code,message:response.message,found:response.data?.arc_audits?.filter(x=>x.Archive?.title.includes('逆向一切')).map(x=>({aid:x.Archive.aid,bvid:x.Archive.bvid,title:x.Archive.title,state:x.Archive.state,state_desc:x.Archive.state_desc})),resources:performance.getEntriesByType('resource').filter(x=>/archive|cover|upload/.test(x.name)).slice(-18).map(x=>({path:new URL(x.name).pathname,duration:x.duration,responseEnd:x.responseEnd}))};
  });
}
