// Re-space the projects page after editing its content.
//
//   python3 -m http.server 8080 &
//   NODE_PATH=$(npm root -g) node tools/reflow.cjs http://localhost:8080/projects.html
//
// (needs the `playwright` package.) For every project it re-stacks the rows from
// the background/role boxes down, with even gaps, and rewrites --y / --h in
// projects.html:
//  - a row is the elements whose top (--y) is within 8 of each other;
//  - cards and boxes in a row share one height: their tallest content measured at
//    five window widths (+2), or the images beside them if those are taller;
//  - a video takes the row's height (it crops itself to fit);
//  - arrows, small labels (.kicker) and sublines sit closer to their neighbours;
//  - a glow keeps its offset from the element right after it (the one it lights);
//  - a new element can be written with --y:0; it slots in after the one before it.
// The cover and the stitched title are left alone (see tools/build_titles.py).
const { chromium } = require('playwright');
const fs = require('node:fs');

const WIDTHS = [1024, 1280, 1366, 1536, 1920];
const GAP = 64;        // between rows
const LINK_GAP = 24;   // around an arrow, under a .kicker, above a .subline
const BOTTOM = 90;     // below a project's last row

// Measure every .el of every project at one window width.
async function measure(browser, url, width) {
  const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const sections = await page.evaluate(() => [...document.querySelectorAll('section.project')].map((sec) => {
    const u = sec.querySelector('.board').offsetWidth / 1366;
    return {
      id: sec.id,
      els: [...sec.querySelectorAll('.el')].map((e) => {
        const num = (n) => parseFloat(e.style.getPropertyValue(n));
        const text = e.matches('.card, .box, .t');
        let need = null;                              // content height, in Canva units
        if (text) {
          const old = e.style.height;
          e.style.height = 'auto';
          need = e.offsetHeight / u;
          e.style.height = old;
        }
        return {
          y: num('--y'),
          h: Number.isNaN(num('--h')) ? null : num('--h'),
          need,
          text,
          boxy: e.matches('.card, .box'),
          video: e.matches('.video'),
          glow: e.matches('.glow'),
          skip: e.matches('.stitch-line, .cover, .glow'),
          tightAfter: e.matches('.arrow, .kicker'),
          tightBefore: e.matches('.arrow, .subline'),
        };
      }),
    };
  }));
  await page.close();
  return sections;
}

// New --y / --h for one project's elements, and the project's new height.
function layout(els) {
  els.forEach((e, k) => { if (e.y === 0 && k) e.y = els[k - 1].y + 10; });
  const body = els.filter((e) => !e.skip);
  const start = Math.min(...body.filter((e) => e.boxy).map((e) => e.y));

  const rows = [];
  for (const e of body.filter((e) => e.y >= start - 1).sort((a, b) => a.y - b.y)) {
    const row = rows.find((r) => Math.abs(r.y - e.y) < 8);
    if (row) row.els.push(e); else rows.push({ y: e.y, els: [e] });
  }

  const out = {};
  let y = start;
  rows.forEach((row, k) => {
    const top = Math.min(...row.els.map((e) => e.y));
    const images = row.els.filter((e) => !e.text && e.h != null && !e.video);
    const height = Math.max(
      images.length ? Math.max(...images.map((e) => e.y - top + e.h)) : 0,
      ...row.els.filter((e) => e.boxy).map((e) => Math.ceil(e.need) + 2),
      ...row.els.filter((e) => e.text && !e.boxy).map((e) => Math.ceil(e.need)),
      0,
    );
    for (const e of row.els) {
      out[e.i] = { y: +(y + (e.text ? 0 : e.y - top)).toFixed(1) };
      if (e.boxy || e.video) out[e.i].h = height;
    }
    const next = rows[k + 1];
    const tight = next && (row.els.some((e) => e.tightAfter) || next.els.some((e) => e.tightBefore));
    y += height + (tight ? LINK_GAP : GAP);
  });

  els.forEach((e, k) => {
    const next = els[k + 1];
    if (e.glow && next && out[next.i]) out[e.i] = { y: +(out[next.i].y + e.y - next.y).toFixed(1) };
  });
  return { out, board: Math.round(y - GAP + BOTTOM) };
}

// Write the new values into projects.html (elements are matched in document order).
function write(layouts) {
  let html = fs.readFileSync('projects.html', 'utf8');
  html = html.replace(/<section id="([^"]+)" class="page project">[\s\S]*?<\/section>/g, (sec, id) => {
    const L = layouts[id];
    let i = -1;
    sec = sec.replace(/(class="el(?: [^"]*)?" style=")([^"]*)"/g, (m, start, style) => {
      i++;
      const o = L.out[i];
      if (!o) return m;
      style = style.replace(/--y:-?[\d.]+/, `--y:${o.y}`);
      if (o.h != null) style = /--h:/.test(style) ? style.replace(/--h:[\d.]+/, `--h:${o.h}`) : `${style};--h:${o.h}`;
      return start + style + '"';
    });
    console.log(id.padEnd(30), 'height', L.board);
    return sec.replace(/(<div class="board" style="--h:)[\d.]+/, `$1${L.board}`);
  });
  fs.writeFileSync('projects.html', html);
}

(async () => {
  const url = process.argv[2];
  const browser = await chromium.launch();
  const runs = [];
  for (const w of WIDTHS) runs.push(await measure(browser, url, w));
  await browser.close();

  const layouts = {};
  runs[0].forEach((sec, s) => {
    const els = sec.els.map((e, i) => ({
      ...e, i, need: e.text ? Math.max(...runs.map((r) => r[s].els[i].need)) : null,
    }));
    layouts[sec.id] = layout(els);
  });
  write(layouts);
})();
