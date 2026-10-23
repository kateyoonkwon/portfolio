# Kate Kwon — portfolio

Static rebuild of the Canva site (`katekwon.my.canva.site`, design `DAHYFWWaYeo`). Plain HTML/CSS/JS, no build step.

```
index.html        home (hero + about me)
*.html            one page per project (alpha-kappa-psi.html, bits-of-good.html, …)
css/style.css     layout + design tokens
js/main.js        "projects" dropdown, mobile menu, missing-image fallback
vercel.json       clean URLs (/matmerize instead of /matmerize.html)
assets/           name-web.svg (home background) and img/
docs/             design inventory from Canva
```

## How the layout works

The nav (home + a "projects" dropdown) is repeated at the top of every page;
when adding a project, add its link to the dropdown on every page.

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

- **Font**: DM Sans (regular + italic), loaded from Google Fonts in `index.html`.
- Nav styling is approximated from Canva's page previews.
- Cockpit photo: on hold, not placed.
