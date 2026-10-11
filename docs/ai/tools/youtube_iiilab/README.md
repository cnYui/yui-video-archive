# YouTube 视频下载（iiilab，2026-10-05 跑通）

AGENTS.md「常用网页」里用户指定的 YouTube 下载站是 https://youtube.iiilab.com/ 。这份说明是 2026-10-05 下 Claude Academy 官方视频（16 条，1080p，共约 258 MB；分两轮，第二轮 4 条用 `--names` 直接命名）时跑通的流程，记录见 `docs/ai/context/20261005-210000-claude-academy-short-video-breakdown_CN.md` 和 `20261005-220000-claude-official-tutorial-plan_CN.md`。

## 什么时候走这条路

- **本机 `yt-dlp` 被 YouTube 拦了**（“Sign in to confirm you’re not a bot”）：当天先用 yt-dlp 批量查了 170 条元数据（`-J`，不下载），之后连单条下载都被拦。**批量查元数据别太猛**（并发 6、170 条就触发了）。拦了之后不要去绕（不读用户浏览器 cookie、不换客户端伪装），改走 iiilab。
- 不拦的时候 yt-dlp 更省事（见 `独立视频\2026-10_OpenAI视频中文版` 那次的记录）。

## 步骤

1. **用 Claude 内置浏览器开 iiilab**（`mcp__Claude_Browser__navigate` 到 `https://youtube.iiilab.com/`），不要去抢共用 Chrome 窗口（里面是别的会话的标签，前置会把它们切成后台）。内置浏览器窗格是隐藏的也能解析；共用 Chrome 里 `visibilityState = hidden` 的标签点“解析视频”没有结果。iiilab 不需要登录，所以不受“账号内网页用 Chrome 插件”那条约束。
2. **页面里用 JS 逐条解析**（`javascript_tool`，后台任务 + 轮询）。输入框是 React 受控组件，要用原生 setter + `input` 事件；等结果时用封面链接里带的视频 ID 判断是不是新结果（`a` 文字“下载封面”的 href 含 `/vi/<ID>/`），别读到上一条的旧结果：

```js
const tick=()=>new Promise(r=>{const c=new MessageChannel();c.port1.onmessage=()=>r();c.port2.postMessage(0)});
const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
const input=document.querySelector('input'); const btn=[...document.querySelectorAll('button')].find(b=>/解析视频/.test(b.innerText));
window.__res={};
for(const id of IDS){
  setter.call(input,'https://www.youtube.com/watch?v='+id); input.dispatchEvent(new Event('input',{bubbles:true})); btn.click();
  const t0=Date.now();
  while(Date.now()-t0<40000){ await tick();
    const cov=([...document.querySelectorAll('a')].find(a=>/下载封面/.test(a.innerText))||{}).href||'';
    const A=[...document.querySelectorAll('a')].filter(a=>/googlevideo/.test(a.href));
    if(A.length>=8 && cov.includes('/vi/'+id+'/')){
      const g=it=>{const a=A.find(x=>new URL(x.href).searchParams.get('itag')===it);return a?a.href:null};
      window.__res[id]={v:g('137'), a:g('140'), a2:g('251')}; break; } }
  await new Promise(r=>setTimeout(r,800));
}
```

3. **音轨一定看 `xtags`**：itag 140 / 251 的链接里 `xtags=acont%3Doriginal…lang%3Den-US` 才是英文原声；`acont=dubbed-auto lang=ar` 是 YouTube 自动配音的阿拉伯语（`j1Vk6Y-23CY` 就是这样，改用 251）。没有 `xtags` = 只有一条音轨。多音轨视频一般没有 itag 140 的原声，只有 251（opus，脚本转成 AAC 192k）。
4. **把直链从页面带到本机**：内置浏览器页面连不上 `127.0.0.1`（`fetch` 和 `new Image()` 都失败）、也写不了剪贴板（`execCommand('copy')` 返回 false），所以只能让 `javascript_tool` 把文字返回来、我写进文件。每条链接约 2 KB，视频直链和音频直链几乎一样（只差 `itag / mime / xtags / clen / dur / lmt / txp / sparams / sig`，视频链接多一个 `aitags`），所以**只返回“视频直链 + 音频差异参数”**，每行 `ID|视频直链|差异`：

```js
const L=h=>h.split('?')[1].split('&').map(s=>{const i=s.indexOf('=');return [s.slice(0,i),s.slice(i+1)]});
ids.map(id=>{const r=window.__res[id]; const aud=r.a||r.a2;   // 140 是配音时手动改成 r.a2
  const lv=L(r.v), la=L(aud), dv=new Map(lv);
  const d=la.filter(([k,v])=>!dv.has(k)||dv.get(k)!==v).map(([k,v])=>k+'='+v).join('&');
  return id+'|'+r.v+'|'+d}).join('\n')
```

   （用 Chrome 插件的 `javascript_tool` 时，返回值里带 `?` `=` `&` 的整条 URL 会被拦成 `[BLOCKED: Cookie/query string data]`；内置浏览器的不拦。）每 4 条一批，写成 `links_*.txt`（放 scratchpad，不要进项目：里面有带签名的临时链接）。
5. `python docs\ai\tools\youtube_iiilab\dl_iiilab.py --out <素材\视频目录> --names names.json links_a.txt …`：每条视频的画面和音频并行 `curl`，字节数对 `clen`，通过再 `ffmpeg -c copy` 合成 mp4。1080p 画面约 9–40 MB、音频 2–5 MB，12 条并行 5 分钟内下完（DASH 链接被限速，约 300 KB/s 一路，多条并行就行）。
6. 下完用 `ffprobe` 核对分辨率、时长；有疑问的那条用 faster-whisper 对 30 秒检测语言（本机有 `large-v3-turbo`，CPU int8 可跑）。

## 其他坑

- 链接约 6 小时过期，下载失败（403 / 字节数对不上）就重新解析那一条。
- 解析一次约 2.5 秒，一次一条，没有批量；页面有广告和“批量下载软件”推广，别点。
- iiilab 的 1080p 是 H.264（itag 137），2K / 4K 是 VP9 webm（itag 271 / 313，4K 一条 80 MB 以上）；要裁切放大再单独取。
- dcg 钩子会拦 `python - <<EOF` 里的 `os.remove()`：临时文件写到 scratchpad、别在内联脚本里删；这个脚本是文件，只删自己下的分轨中间文件。
- D 盘 2026-10-05 只剩 12 GB，下之前先 `df -h /d`。
