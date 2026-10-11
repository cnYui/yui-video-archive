# -*- coding: utf-8 -*-
"""短视频竖屏版式方案样图：用真引擎（image-blaster 那条的 index.html + 真帧 + 真字幕）按方案摆放，再套上边框和背景印花。
标题位置不动（y 280–570）；视频框、字幕往下移、拉开间距；双横屏另摆；GitHub 链接条 / 数字卡放在字幕下面。

  python make_layout_options.py
    → 版式A.png / 版式B.png / 版式C.png   每张：单框+链接条 | 单框+数字卡 | 双横屏（各带一种边框 + 一种背景印花）
    → 边框总览.png                         六种边框，同一画面
    → 背景总览.png                         四种背景（无 / 原色 / 墨色 / 橙色）
背景印花先跑 make_pattern.py。
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ENG = Path(r"D:\大疆\独立视频\短视频\2026-10_image-blaster推荐\制作\00_整片")
OUT = Path(__file__).resolve().parent
FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
T = 21.0                       # 取这一刻的字幕和画面（用户截图里的那一帧：Claude 会给每件物件各生成一张图）
HEAD_BOT = 570                 # 标题 280–570 不动

# 方案：g0 = 标题到视频框的间距，g1 = 视频框到字幕，g2 = 字幕到链接条 / 数字卡
OPTS = {
    "A": dict(name="方案 A · 适度下移", frame="win", pat="color",
              note="窗口式边框 + 原色淡印花；视频框下移 110、字幕下移 210，三段间距约 130；数字卡保持原来的大卡",
              single=dict(w=1000, g0=130, g1=130, g2=60, card="big"),
              dual=dict(kind="stack_sub_mid", w=800, g0=90, g1=70, g2=70)),
    "B": dict(name="方案 B · 宽松", frame="tape", pat="ink",
              note="胶带卡片边框 + 墨色单色印花；视频框下移 180、字幕下移 310，间距约 200 / 160；数字卡压成紧凑版",
              single=dict(w=1000, g0=200, g1=160, g2=50, card="compact"),
              dual=dict(kind="stack_pair", w=860, g0=110, gap=24, g1=80)),
    "C": dict(name="方案 C · 字幕靠下", frame="brut", pat="orange",
              note="粗描边硬阴影边框 + 橙色单色印花；视频框下移 230、字幕下移 405，间距约 230 / 190；数字卡压成一行细条",
              single=dict(w=1000, g0=230, g1=190, g2=60, card="slim"),
              dual=dict(kind="pip", w=1000, g0=200, pip_w=470, g1=70)),
}
FRAMES = [("plain", "原样（现在的白卡片）"), ("win", "窗口式"), ("tape", "胶带卡片"), ("ring", "渐变描边"), ("vf", "取景框 + REC"), ("brut", "粗描边硬阴影"), ("mon", "显示器")]

CSS = """
.linkpill{position:absolute;left:90px;width:900px;box-sizing:border-box;text-align:center;background:#16181D;color:#fff;border-radius:26px;padding:20px 24px 22px;
  font:700 42px/1.2 'JetBrains Mono','Noto Sans SC';box-shadow:0 14px 34px rgba(0,0,0,.28);white-space:nowrap;z-index:25}
.linkpill i{font-style:normal;color:#9CA3AF}.linkpill b{color:#FFD84D;font-weight:800}
.bigcard.compact{padding:14px 30px 18px}.bigcard.compact .n{font-size:92px}.bigcard.compact .n small{font-size:42px}.bigcard.compact .d{font-size:34px;margin-top:4px}
.bigcard.slim{padding:12px 28px 14px;display:flex;align-items:baseline;justify-content:center;gap:22px}
.bigcard.slim .n{font-size:68px}.bigcard.slim .n small{font-size:34px}.bigcard.slim .d{margin:0;font-size:34px}
body.pat::before{display:none}
#pat{position:absolute;left:0;top:0;width:1080px;height:2340px;z-index:0;background-repeat:no-repeat;background-size:1080px 2340px}

/* ── 边框 ── */
.frame.f-win{border:1px solid #D4D8DF;border-radius:20px;background:#F1F2F5;box-shadow:0 22px 50px rgba(0,0,0,.18)}
.frame.f-win::before{content:'';position:absolute;left:20px;top:21px;width:16px;height:16px;border-radius:50%;background:#FF5F57;box-shadow:26px 0 0 #FEBC2E,52px 0 0 #28C840}
.frame.f-win::after{content:attr(data-title);position:absolute;left:100px;right:100px;top:11px;text-align:center;font:700 25px/36px 'Noto Sans SC';color:#6B7280;white-space:nowrap;overflow:hidden}
.frame.f-win .inner{border-radius:6px;background:#111}
.frame.f-tape{border:0;border-radius:6px;background:#fff;transform:rotate(-1.1deg);box-shadow:0 20px 44px rgba(0,0,0,.2)}
.frame.f-tape::before,.frame.f-tape::after{content:'';position:absolute;top:-22px;width:150px;height:44px;background:rgba(255,216,77,.78);box-shadow:0 2px 6px rgba(0,0,0,.12)}
.frame.f-tape::before{left:56px;transform:rotate(-6deg)}.frame.f-tape::after{right:56px;transform:rotate(5deg)}
.frame.f-tape .inner{border-radius:2px}
.frame.f-ring{border:0;border-radius:28px;background:linear-gradient(135deg,#FF4F1A,#FFD84D 52%,#FF6183);box-shadow:0 0 0 7px rgba(255,79,26,.12),0 24px 50px rgba(255,79,26,.3)}
.frame.f-ring .inner{border-radius:17px;background:#111}
.frame.f-vf{border:0;background:transparent;box-shadow:none}
.frame.f-vf::before{content:'';position:absolute;inset:-16px;pointer-events:none;background:
  linear-gradient(#FF4F1A,#FF4F1A) 0 0/64px 8px no-repeat,linear-gradient(#FF4F1A,#FF4F1A) 0 0/8px 64px no-repeat,
  linear-gradient(#FF4F1A,#FF4F1A) 100% 0/64px 8px no-repeat,linear-gradient(#FF4F1A,#FF4F1A) 100% 0/8px 64px no-repeat,
  linear-gradient(#FF4F1A,#FF4F1A) 0 100%/64px 8px no-repeat,linear-gradient(#FF4F1A,#FF4F1A) 0 100%/8px 64px no-repeat,
  linear-gradient(#FF4F1A,#FF4F1A) 100% 100%/64px 8px no-repeat,linear-gradient(#FF4F1A,#FF4F1A) 100% 100%/8px 64px no-repeat}
.frame.f-vf::after{content:'● REC';position:absolute;left:4px;top:-62px;font:800 28px 'JetBrains Mono';color:#E11D48;letter-spacing:.08em}
.frame.f-vf .inner{border-radius:2px;box-shadow:0 18px 40px rgba(0,0,0,.28)}
.frame.f-brut{border:7px solid #141413;border-radius:14px;background:#141413;box-shadow:14px 14px 0 #FF4F1A}
.frame.f-brut::after{content:attr(data-tag);position:absolute;right:-8px;top:-38px;background:#FFD84D;color:#141413;border:5px solid #141413;border-radius:10px;padding:0 16px;font:900 26px/38px 'Noto Sans SC';transform:rotate(3deg)}
.frame.f-brut .inner{border-radius:4px}
.frame.f-mon{border:0;border-radius:22px;background:#1B1B1F;box-shadow:0 26px 50px rgba(0,0,0,.3)}
.frame.f-mon::before{content:'';position:absolute;left:50%;top:100%;width:170px;height:44px;margin-left:-85px;background:linear-gradient(#34343B,#1B1B1F);clip-path:polygon(16% 0,84% 0,100% 100%,0 100%)}
.frame.f-mon::after{content:'';position:absolute;left:50%;top:calc(100% + 42px);width:320px;height:12px;margin-left:-160px;background:#2A2A30;border-radius:8px}
.frame.f-mon .inner{border-radius:4px}
"""

APPLY = r"""
(cfg) => {
  const FR = {
    plain: {pad: [14, 14, 14, 14], bw: 1, cls: ''},
    win:   {pad: [58, 14, 14, 14], bw: 1, cls: 'f-win'},
    tape:  {pad: [22, 22, 22, 22], bw: 0, cls: 'f-tape'},
    ring:  {pad: [12, 12, 12, 12], bw: 0, cls: 'f-ring'},
    vf:    {pad: [10, 10, 10, 10], bw: 0, cls: 'f-vf'},
    brut:  {pad: [0, 0, 0, 0], bw: 7, cls: 'f-brut'},
    mon:   {pad: [18, 18, 24, 18], bw: 0, cls: 'f-mon'},
  };
  const box = (id, x, y, w, style, title, tag) => {
    const f = FR[style], el = document.getElementById(id);
    el.className = 'frame ' + f.cls;
    el.dataset.title = title || ''; el.dataset.tag = tag || '';
    const iw = w - f.pad[1] - f.pad[3] - 2 * f.bw, sc = iw / 1474, H = Math.round(829 * sc + f.pad[0] + f.pad[2] + 2 * f.bw);
    Object.assign(el.style, {left: x + 'px', top: y + 'px', width: w + 'px', height: H + 'px', padding: f.pad.map(v => v + 'px').join(' ')});
    el.querySelector('.demoin').style.transform = `scale(${sc})`;
    return H;
  };
  const src = (id, f) => { const i = document.getElementById(id); i.src = 'file:///' + f.replace(/\\/g, '/'); i.style.visibility = 'visible'; };
  const cx = w => Math.round((1080 - w) / 2);
  // 背景印花
  document.querySelectorAll('#pat').forEach(e => e.remove());
  document.body.classList.remove('pat');
  if (cfg.pat && cfg.pat !== 'none') {
    const pat = document.createElement('div'); pat.id = 'pat';
    pat.style.backgroundImage = `url('file:///${cfg.pat_dir.replace(/\\/g, '/')}/pattern_${cfg.pat}.png')`;
    document.body.insertBefore(pat, document.body.firstChild);
    document.body.classList.add('pat');
  }
  const P = document.getElementById('ovP'); P.innerHTML = '';
  const out = {};
  const credit = document.querySelector('.credit'); if (credit) credit.textContent = '画面：@neilsonks · X（原帖）';
  const title = '演示视频 · X @neilsonks', tag = '作者演示';
  const sub = y => { document.getElementById('subs').style.top = y + 'px'; return y; };
  if (cfg.layout === 'single') {
    document.body.classList.remove('dual'); document.getElementById('ovB').style.display = '';
    const y1 = 570 + cfg.g0, H = box('demo', cx(cfg.w), y1, cfg.w, cfg.frame, title, tag);
    const sy = sub(y1 + H + cfg.g1), iy = sy + 110 + cfg.g2;
    const el = document.createElement('div');
    if (cfg.info === 'pill') { el.className = 'linkpill'; el.innerHTML = '<i>github.com/</i>neilsonnn/<b>image-blaster</b>'; out.info_h = 96; }
    else { el.className = 'bigcard ' + (cfg.card === 'big' ? '' : cfg.card); el.innerHTML = '<div class="n">5000+<small>星标</small></div><div class="d">GitHub · MIT 协议</div>'; out.info_h = {big: 260, compact: 205, slim: 110}[cfg.card]; }
    el.style.top = iy + 'px'; P.appendChild(el);
    Object.assign(out, {y1, H, sub: sy, info: iy});
  } else {
    document.body.classList.add('dual'); document.getElementById('ovB').style.display = 'none';
    src('scrimg', cfg.f1); src('scrimg2', cfg.f2);
    const y1 = 570 + cfg.g0;
    if (cfg.kind === 'pip') {
      const H = box('demo', cx(cfg.w), y1, cfg.w, cfg.frame, title, tag);
      const hp = Math.round(829 * ((cfg.pip_w - 30) / 1474) + 30), py = y1 + H - 150;
      box('demo2', cfg.w + cx(cfg.w) - cfg.pip_w + 10, py, cfg.pip_w, cfg.frame, '', '');
      Object.assign(out, {y1, H, sub: sub(py + hp + cfg.g1), y2: py, H2: hp});
    } else if (cfg.kind === 'stack_pair') {
      const H = box('demo', cx(cfg.w), y1, cfg.w, cfg.frame, title, tag), y2 = y1 + H + cfg.gap;
      const H2 = box('demo2', cx(cfg.w), y2, cfg.w, cfg.frame, '', '');
      Object.assign(out, {y1, H, y2, H2, sub: sub(y2 + H2 + cfg.g1)});
    } else {
      const H = box('demo', cx(cfg.w), y1, cfg.w, cfg.frame, title, tag), sy = sub(y1 + H + cfg.g1), y2 = sy + 110 + cfg.g2;
      const H2 = box('demo2', cx(cfg.w), y2, cfg.w, cfg.frame, '', '');
      Object.assign(out, {y1, H, y2, H2, sub: sy});
    }
  }
  return out;
}
"""


def shot(page, cfg, path):
    page.evaluate("t => renderAt(t)", T)
    cfg = dict(cfg, pat_dir=str(OUT))
    info = page.evaluate(APPLY, cfg)
    page.wait_for_timeout(500)
    page.evaluate("Promise.all([...document.images].map(i => i.decode().catch(() => 0)))")
    page.screenshot(path=str(path))
    return info


def guides(im):
    """平台遮挡区（很淡）：顶栏 0–250、底部文案区 1950–2340、右侧按钮 x≥940（y 1170–1990）"""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, 1080, 250], fill=(110, 120, 140, 38))
    d.rectangle([0, 1950, 1080, 2340], fill=(110, 120, 140, 38))
    d.rectangle([940, 1170, 1080, 1990], fill=(110, 120, 140, 26))
    f = ImageFont.truetype(FONT, 26)
    d.text((24, 12), "平台顶栏", fill=(80, 90, 110, 170), font=f)
    d.text((24, 1962), "平台账号名 / 文案 / 音乐条", fill=(80, 90, 110, 170), font=f)
    d.text((948, 1180), "按钮", fill=(80, 90, 110, 170), font=f)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def phone(im, scale=0.5, radius=44):
    w, h = int(im.width * scale), int(im.height * scale)
    im = im.resize((w, h), Image.LANCZOS)
    pad = 10
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w + 2 * pad - 1, h + 2 * pad - 1], radius=radius, fill=(26, 26, 30, 255))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius - 8, fill=255)
    out.paste(im, (pad, pad), mask)
    return out


def main():
    scr = ENG / "media" / "scr"
    h1, m1 = sorted(scr.glob("H1_0_000*.jpg")), sorted(scr.glob("M1_1_001*.jpg"))
    f1, f2 = str(h1[len(h1) // 2]), str(m1[min(20, len(m1) - 1)])
    raw = OUT / "_raw"
    raw.mkdir(exist_ok=True)
    infos = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1080, "height": 2340})
        page.goto((ENG / "index.html").as_uri())
        page.evaluate("document.fonts.ready.then(() => true)")
        page.add_style_tag(content=CSS)
        for k, o in OPTS.items():
            base = dict(frame=o["frame"], pat=o["pat"])
            s, d = o["single"], o["dual"]
            infos[k] = shot(page, dict(layout="single", info="pill", **base, **s), raw / f"{k}_single_pill.png")
            shot(page, dict(layout="single", info="card", **base, **s), raw / f"{k}_single_card.png")
            infos[k + "_dual"] = shot(page, dict(layout="dual", f1=f1, f2=f2, **base, **d), raw / f"{k}_dual.png")
        for name, _ in FRAMES:                               # 边框总览：版式 A 的单框，只换边框
            shot(page, dict(layout="single", info="card", frame=name, pat="none", **OPTS["A"]["single"]), raw / f"frame_{name}.png")
        for pat in ("none", "color", "ink", "orange"):         # 背景总览：版式 A 的单框，只换背景
            shot(page, dict(layout="single", info="card", frame="plain", pat=pat, **OPTS["A"]["single"]), raw / f"pat_{pat}.png")
        b.close()
    json.dump(infos, open(OUT / "_positions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    big, small, tiny = ImageFont.truetype(FONT, 46), ImageFont.truetype(FONT, 28), ImageFont.truetype(FONT, 23)
    for k, o in OPTS.items():
        s, d = o["single"], o["dual"]
        ph = [phone(guides(Image.open(raw / f"{k}_{n}.png").convert("RGB"))) for n in ("single_pill", "single_card", "dual")]
        W, H = 3 * ph[0].width + 4 * 40, 170 + ph[0].height + 210
        sheet = Image.new("RGB", (W, H), "#F1F2F5")
        dr = ImageDraw.Draw(sheet)
        dr.text((40, 28), o["name"], fill="#141413", font=big)
        dr.text((40, 100), o["note"], fill="#4B5563", font=small)
        caps = ["单框 · GitHub 链接条", "单框 · 数字卡", {"stack_sub_mid": "双横屏 · 上下两框，字幕夹在中间", "stack_pair": "双横屏 · 两框叠在一起，字幕在下", "pip": "双横屏 · 主画面 + 小窗"}[d["kind"]]]
        for i, im in enumerate(ph):
            x = 40 + i * (ph[0].width + 40)
            sheet.paste(im, (x, 170), im)
            dr.text((x + 10, 170 + ph[0].height + 14), caps[i], fill="#141413", font=small)
        a = infos[k]
        line = (f"单框：标题 280–570（不动）→ 视频框 {a['y1']}–{a['y1'] + a['H']}（间距 {s['g0']}）→ 字幕 {a['sub']}–{a['sub'] + 110}（间距 {s['g1']}）"
                f"→ 链接条 / 数字卡 {a['info']}–{a['info'] + a['info_h']}（间距 {s['g2']}）")
        dr.text((40, 170 + ph[0].height + 62), line, fill="#4B5563", font=tiny)
        dr.text((40, 170 + ph[0].height + 100), "浅灰块 = 平台遮挡区（顶栏 / 底部文案区 / 右侧按钮），重要的字别放进去；框里的画面是 image-blaster 那条的真帧", fill="#6B7280", font=tiny)
        sheet.save(OUT / f"版式{k}.png")
        print("->", f"版式{k}.png", sheet.size)

    def grid(names, labels, out, title, cols, crop=None, scale=0.4):
        ims = []
        for n in names:
            im = Image.open(raw / f"{n}.png").convert("RGB")
            if crop:
                im = im.crop(crop)
            ims.append(im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS))
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (w + 30) + 30, 110 + rows * (h + 70)), "#F1F2F5")
        dr = ImageDraw.Draw(sheet)
        dr.text((30, 30), title, fill="#141413", font=big)
        for i, (im, lab) in enumerate(zip(ims, labels)):
            x, y = 30 + (i % cols) * (w + 30), 110 + (i // cols) * (h + 70)
            sheet.paste(im, (x, y))
            dr.text((x, y + h + 14), lab, fill="#141413", font=small)
        sheet.save(OUT / out)
        print("->", out, sheet.size)

    grid([f"frame_{n}" for n, _ in FRAMES], [f"{i + 1}. {lab}" for i, (_, lab) in enumerate(FRAMES)], "边框总览.png", "横屏视频的边框（同一画面，版式 A 的位置）", 4, crop=(0, 600, 1080, 1700), scale=0.43)
    grid([f"pat_{n}" for n in ("none", "color", "ink", "orange")], ["1. 无（只有原来的点阵）", "2. 原色淡印花", "3. 墨色单色印花", "4. 橙色单色印花"], "背景总览.png", "背景：AI 工具图标低透明度印花", 4, crop=(0, 0, 1080, 1950), scale=0.34)


if __name__ == "__main__":
    main()
