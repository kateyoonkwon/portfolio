# Kate Kwon — portfolio

Static rebuild of the Canva site (`katekwon.my.canva.site`, design `DAHYFWWaYeo`). Plain HTML/CSS/JS, no build step.

```
index.html        home (hero + about me)
projects.html     all 7 projects on one page, with a light-gray project list on the right
css/style.css     layout + design tokens
js/main.js        dropdown, mobile menu, scroll-in animation, project list highlight
vercel.json       clean URLs, plus redirects from the old /<project> pages
assets/           name-web.svg (home background) and img/
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
