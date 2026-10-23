// Re-stack the rows of every project on projects.html below the background/role
// boxes, sized to their real content.
//
//   node tools/reflow.cjs http://localhost:8080/projects.html
//   (needs the `playwright` package; serve the repo root first:
//    python3 -m http.server 8080)
//
// Rows: elements whose top (--y) is within 8 of each other, merged with any row
// they overlap vertically (e.g. an outline drawn around a grid of images). New
// elements can be given --y:0 to slot in right after the element before them.
// Boxes and cards in a row get one height: the tallest content measured at
// several screen widths, or the height of images in the same row if larger.
const { chromium } = require('playwright');
const fs = require('node:fs');

(async () => {

const url = process.argv[2];
const WIDTHS = [1024, 1280, 1366, 1536, 1920];
const GAP = 64;          // between rows
const LINK_GAP = 24;     // above/below an arrow, and under a small label (.kicker)
const BOTTOM = 90;       // below the last row of a project

const browser = await chromium.launch();
const need = {};         // `${section}:${index}` -> max content height (Canva units)
let geo = null;
for (const w of WIDTHS) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 }, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const r = await page.evaluate(() => [...document.querySelectorAll('section.project')].map((sec) => {
    const u = sec.querySelector('.board').offsetWidth / 1366;
    return {
      id: sec.id,
      els: [...sec.querySelectorAll('.el')].map((e) => {
        const v = (n) => parseFloat(e.style.getPropertyValue(n));
        const text = e.matches('.card, .box, .t');
        let h = null;
        if (text) {
          const old = e.style.height; e.style.height = 'auto';
          h = e.offsetHeight / u; e.style.height = old;
        }
        return { y: v('--y'), h: Number.isNaN(v('--h')) ? null : v('--h'), text, boxy: e.matches('.card, .box'),
          outline: e.matches('.outline'), link: e.matches('.arrow, .kicker'), arrow: e.matches('.arrow'), skip: e.matches('.stitch-line, .cover'), need: h };
      }),
    };
  }));
  geo = geo || r;
  r.forEach((s) => s.els.forEach((e, i) => {
    if (e.need != null) need[`${s.id}:${i}`] = Math.max(need[`${s.id}:${i}`] || 0, e.need);
  }));
  await page.close();
}
await browser.close();

const layout = {};
for (const s of geo) {
  const els = s.els.map((e, i) => ({ ...e, i, need: need[`${s.id}:${i}`] }));
  // placeholders: right after the previous element
  els.forEach((e, k) => { if (e.y === 0 && k) e.y = els[k - 1].y + 10; });
  const body = els.filter((e) => !e.skip);
  const start = Math.min(...body.filter((e) => e.boxy).map((e) => e.y));
  const rows = [];
  for (const e of body.filter((e) => e.y >= start - 1).sort((a, b) => a.y - b.y)) {
    const row = rows.find((r) => Math.abs(r.y - e.y) < 8);
    if (row) row.els.push(e); else rows.push({ y: e.y, els: [e] });
  }
  // merge rows that overlap vertically (outline + grid inside it)
  for (let k = 1; k < rows.length; k++) {
    const prev = rows[k - 1];
    const bottom = Math.max(...prev.els.map((e) => e.y + (e.h ?? 0)));
    if (rows[k].y < bottom - 1 && prev.els.some((e) => e.outline)) {
      prev.els.push(...rows[k].els); rows.splice(k, 1); k--;
    }
  }
  let y = start; const out = {};
  rows.forEach((r, k) => {
    const imgs = r.els.filter((e) => !e.text && e.h != null);
    const top = Math.min(...r.els.map((e) => e.y));
    const imgH = imgs.length ? Math.max(...imgs.map((e) => e.y - top + e.h)) : 0;
    const boxH = Math.max(0, ...r.els.filter((e) => e.boxy).map((e) => Math.ceil(e.need) + 2));
    const textH = Math.max(0, ...r.els.filter((e) => e.text && !e.boxy).map((e) => Math.ceil(e.need)));
    const H = Math.max(imgH, boxH, textH);
    for (const e of r.els) {
      out[e.i] = { y: +(y + (e.text ? 0 : e.y - top)).toFixed(1) };
      if (e.boxy) out[e.i].h = H;
    }
    const next = rows[k + 1];
    const tight = next && (r.els.some((e) => e.link) || next.els.some((e) => e.arrow));
    y += H + (tight ? LINK_GAP : GAP);
  });
  layout[s.id] = { out, board: Math.round(y - GAP + BOTTOM) };
}

let html = fs.readFileSync('projects.html', 'utf8');
html = html.replace(/<section id="([^"]+)" class="page project">[\s\S]*?<\/section>/g, (sec, id) => {
  const L = layout[id]; let i = -1;
  sec = sec.replace(/(class="el(?: [^"]*)?" style=")([^"]*)"/g, (m, a, st) => {
    i++; const o = L.out[i]; if (!o) return m;
    st = st.replace(/--y:-?[\d.]+/, `--y:${o.y}`);
    if (o.h != null) st = /--h:/.test(st) ? st.replace(/--h:[\d.]+/, `--h:${o.h}`) : `${st};--h:${o.h}`;
    return a + st + '"';
  });
  sec = sec.replace(/(<div class="board" style="--h:)[\d.]+/, `$1${L.board}`);
  console.log(id.padEnd(30), 'height', L.board);
  return sec;
});
fs.writeFileSync('projects.html', html);
})();
