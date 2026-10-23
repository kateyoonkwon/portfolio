# Kate Kwon — portfolio

Static rebuild of the Canva site (`katekwon.my.canva.site`, design `DAHYFWWaYeo`). Plain HTML/CSS/JS, no build step.

```
index.html        home (hero + about me)
projects.html     all 7 projects on one page, with a light-gray project list on the right
css/style.css     layout + design tokens
js/main.js        dropdown, mobile menu, scroll-in animation, project list highlight
vercel.json       clean URLs, plus redirects from the old /<project> pages
assets/           name-web.svg (home background), img/, fonts/
tools/            build_titles.py — regenerates the stitched project titles
docs/             design inventory from Canva
```

## How the layout works

The nav (home + a "projects" dropdown) is repeated at the top of both pages.
When adding a project, add its section to projects.html, its link to the
dropdown on both pages, and to the right-hand list in projects.html.

Each Canva page is a 1366px artboard. Every element carries its Canva geometry
inline (`--x --y --w --h`, in Canva px) and CSS scales it to the viewport width,
the same way Canva sites scale. Images also carry Canva's crop (`--ix --iy --iw --ih`).
To move something, change its numbers. Below 760px the artboard switches to a
single-column flow in source order.

## Stitched project titles

Project titles on projects.html are cross-stitch cursive squares, built from a
hand-made cross-stitch alphabet (tools/cursive_glyphs.json). They are generated:

```
python3 tools/build_titles.py
```

Edit a title by changing its `data-text` on the `<h2 class="title stitch">`
(one line starts at the left edge of the text boxes; `a|b` puts `b` at the
bottom-right, ending at the right edge of the text boxes), then rerun the
script; it also re-spaces the boxes below. Lowercase a–z and spaces only.

## Re-spacing a project after editing its content

```
python3 -m http.server 8080 &
NODE_PATH=$(npm root -g) node tools/reflow.cjs http://localhost:8080/projects.html
```

(needs the `playwright` package). It measures each row's text at five screen
widths, sizes boxes in a row to the tallest content, and re-stacks the rows
below the background/role boxes with even gaps. A new element can be added with
`--y:0`; it slots in after the element before it. Run build_titles.py first if
titles changed.

Case-study patterns (after somi.framer.website): `.card.trio` (three cards in a
row, centred label), `svg.arrow` (thin down arrow, used once: problem → insight),
`.kicker` + `.pull` (small label over a very large statement), `.pull-note`
(centred lead-in line), `.lede` + `.subline` (left heading and its subline),
`.stat-line` (key line in a card), `.card.beside` (text card next to tall images,
text at the bottom), `.carousel` (slide strip, one shown large; arrows, click,
keys, auto-advance until used), `.arrow.labeled` (arrow with a label in its stem),
video frames take the height of the card beside them. Project text sizes follow Somi's pages; borders are hairlines
(`--line`, 1 Canva px) in #252e34.

## Background

assets/velvet.webp is the velvet photo, enhanced (de-blocked, enlarged 3x,
sharpened, fine grain added), lightened to a pale aqua so the original blue
stays readable, and stacked with its own mirror image so it repeats down the
page without a seam.

## Glow highlights

assets/glow.webp (the soft-light photo, de-blocked and enlarged 2x) is faded in
radially behind key moments via `<div class="el glow">` placed right before the
element it highlights (`--fx`/`--fy` pick which part of the photo, `--zoom` how
close); tools/reflow.cjs moves each glow with that element. Glows
are hidden on phones.

## Stamp and site icon

assets/stamp.svg is the traced cross-stitch flower (tools/flower_cells.json) in a
perforated stamp border, on the same square grid as the titles. It sits in the
home page's bottom-left corner and is the site icon (with favicon-64.png and
apple-touch-icon.png). Rebuild all three with `python3 tools/build_stamp.py`.

## Run locally

```
python3 -m http.server 8080
```

## Deploy (Vercel)

1. Push this folder to a GitHub repo.
2. vercel.com → Add New → Project → import the repo.
3. Framework preset: **Other**. No build command, output directory = root.

## Adding or replacing images

Drop each file into `assets/img/` with that name. If it is a Canva SVG export
(already cropped and rounded), use `.svg`, add class `svg` to the frame and remove the crop vars.

## Open items

- **Fonts**: DM Sans (body, Google Fonts). Headings use Century Schoolbook Bold when installed, otherwise C059 Bold (free metric-compatible clone, AGPL with font exception) from `assets/fonts/` — keep its license files alongside it.
- Nav styling is approximated from Canva's page previews.
- Cockpit photo: on hold, not placed.
