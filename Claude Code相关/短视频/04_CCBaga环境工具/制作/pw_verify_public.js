async (page) => {
  return await page.evaluate(async () => {
    const results=await Promise.allSettled([
      fetch('/x/vupre/web/archive/view?bvid=BV1CxpC69ESE',{credentials:'include'}).then(r=>r.json()),
      fetch('https://api.bilibili.com/x/web-interface/view?bvid=BV1CxpC69ESE',{credentials:'include'}).then(r=>r.json())
    ]);
    return results.map((result,i)=>{
      if (result.status==='rejected') return {source:i,error:String(result.reason)};
      const reply=result.value;
      if (reply.code!==0) return {source:i,code:reply.code,message:reply.message};
      if (i===0) return {source:i,code:0,creation_statement:reply.data.archive.creation_statement,in_season:reply.data.in_season,add_season:reply.data.add_season,origin_state:reply.data.origin_state,had_passed:reply.data.archive.had_passed};
      const d=reply.data;
      return {source:i,code:0,aid:d.aid,bvid:d.bvid,title:d.title,state:d.state,duration:d.duration,tid:d.tid,season:{id:d.ugc_season?.id,title:d.ugc_season?.title},is_season_display:d.is_season_display,rights:d.rights,is_upower_exclusive:d.is_upower_exclusive};
    });
  });
}
