async (page) => {
  return await page.getByText('双比例同步改动',{exact:true}).evaluateAll(ns=>ns.map(x=>({visible:!!x.getClientRects().length,html:x.parentElement.outerHTML.slice(0,2500)})));
}
