async (page) => {
  return await page.evaluate(async () => {
    const r=await fetch('https://api.bilibili.com/x/web-interface/view?bvid=BV1JepC6EEk8',{credentials:'include'}).then(r=>r.json());
    return {code:r.code,message:r.message,data:r.data?{bvid:r.data.bvid,title:r.data.title,state:r.data.state,duration:r.data.duration,tid:r.data.tid}:null};
  });
}
