# Kate Kwon — portfolio

Personal portfolio, rebuilt in code from the original Canva site
(`katekwon.my.canva.site`, design `DAHYFWWaYeo`) and since redesigned.
Plain HTML, CSS and JavaScript: no framework and no build step, so the repo root
is the website.

## Files

```
index.html           home: name hero, photo grid, about me
projects.html        all seven case studies on one page
css/style.css        all styles, in numbered sections (contents at the top)
js/main.js           navigation, scroll fade-in, project list, carousels
vercel.json          clean URLs and redirects from the old /<project> pages
assets/              backgrounds, signature, flower, icons, fonts
assets/img/          project and home-page images
tools/               scripts that generate parts of the pages (below)
docs/                snapshot of the original Canva design
```

## How the layout works

Each page section is an artboard 1366 units wide, the size of the Canva canvas.
Every placed element has class `el` and its position inline in Canva pixels:

```html
<div class="el card" style="--x:136.6;--y:854.5;--w:344.6;--h:215">…</div>
```

CSS scales those units to the window (`--u` = one Canva pixel), so the whole
page scales like the Canva site did. Images also carry Canva's crop
(`--ix --iy --iw --ih`). To move or resize something, change its numbers.

At 760px wide and below (phones) the artboard is switched off and elements flow
in the order they appear in the HTML. That section of `style.css` lists the
phone-only adjustments.

The navigation is written out in both HTML files. When adding a project, add it
to the dropdown in both files and to the side list in `projects.html`.

## Content patterns (projects page)

| Class | What it is |
|---|---|
| `.box` | the "background:" and "role:" boxes |
| `.card` | outlined text card; `.card.trio` three in a row, `.card.beside` text at the bottom next to tall images |
| `.arrow`, `.arrow.labeled` | thin down arrow; with a label in its stem ("the execution") |
| `.kicker` + `.pull` | small label over a very large statement |
| `.pull-note` | centred lead-in line |
| `.lede` + `.subline` | left-aligned heading with its subline |
| `.stat-line` | the key line in a card, a step larger |
| `.carousel` | slide strip with one slide shown large (arrows, click, keys, auto-advance) |
| `.glow` | soft-light highlight placed right before the element it highlights |
| `.img.cover` | square-cornered cover image; other images get rounded, outlined frames |

Type sizes on the projects page follow Somi Park's case studies
(somi.framer.website): 16 / 20 / 30 / 50px at a 1366px window.

## Tools

Run from the repo root. Serve the site locally first for `reflow.cjs`:
`python3 -m http.server 8080`.

| Command | What it does |
|---|---|
| `python3 tools/build_titles.py` | Rebuilds the cross-stitch project titles from each `<h2 class="title stitch" data-text="…">` (`a|b` = two lines) and moves the boxes below to fit. Uses `stitch_title.py` and the traced alphabet in `cursive_glyphs.json`. |
| `NODE_PATH=$(npm root -g) node tools/reflow.cjs http://localhost:8080/projects.html` | Re-spaces each project after copy edits: sizes boxes to their text (measured at five window widths) and re-stacks rows with even gaps. New elements can be added with `--y:0`. Needs the `playwright` package. |
| `python3 tools/build_stamp.py` | Rebuilds the cross-stitch flower (`flower.svg`), the stamp (`stamp.svg`) and the site icons from `flower_cells.json`. Needs Pillow. |

Typical copy edit: change the text in `projects.html`, run `reflow.cjs`, check
the page.

## Assets

- **Background** (`velvet.webp`): the velvet photo, enhanced and lightened, stacked
  with its mirror image so it repeats down the page without a seam.
- **Glows** (`glow.webp`): the soft-light photo. Each `.glow` picks a part of it
  (`--fx`/`--fy`) and a zoom (`--zoom`).
- **Signature** (`name-web.svg`): the home page hero.
- **Flower and icons** (`flower.svg`, `stamp.svg`, `favicon-64.png`,
  `apple-touch-icon.png`): built by `build_stamp.py`.
- **Fonts**: DM Sans comes from Google Fonts. Headings use Century Schoolbook Bold
  where installed, otherwise `fonts/C059-Bold.woff2`, a free metric-compatible
  clone (AGPL with font exception). Keep its license files next to it.

## Run locally

```
python3 -m http.server 8080
```

Then open http://localhost:8080.

## Deploy

The site is deployed on Vercel from this repo: every push to `main` goes live.
Settings: Framework Preset "Other", no build command, output directory = repo root.
