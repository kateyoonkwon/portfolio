# Phase 1 — Design inventory (Canva design `DAHYFWWaYeo`, "Kate Kwon")

Source: Canva connector, exact element data (positions in Canva px on a 1366px-wide canvas).
Not yet seen: the live published site (network blocked), full-resolution images.

## Global

| Token | Value | Where |
|---|---|---|
| Canvas width | 1366px | every page; scale to viewport width |
| Primary blue | `#2974ba` | "about me :)", project titles, links, card outlines, "omw!" |
| Text | `#252e34` | all body copy, image frame strokes |
| Skills card fill | `#edeced` | the "skills:" card on each project page |
| Signature blue | `#0970b8` | only inside `Name_web.svg` (slightly different from `#2974ba`) |
| Background | `#ffffff` | every page |
| Font | Canva font ref `YAD1aU3sLnI` (one family, regular + italic) | everything (**name unknown**) |
| Display size | 106.67px, line-height 0.83, letter-spacing 0.045em | "about me :)" |
| Body size | 26.67px, line-height 1.18 (free text) / 1.0 (inside cards) | everything else |
| Title size | 26.67px, centred, line-height 1.11, blue | project page titles |
| Card | 2px `#2974ba` outline, rounded corners (Canva corner value 36), 2px | response / impact / skills |
| Image frame | 2px `#252e34` stroke on some images, none on others | per element |

All text is lowercase by design (except "North American Bourbon and Whiskey" on minturn).

## Page / section order (Canva page titles = navigation labels)

1. **home** (1366 × 768 hero + 1366 × 1616 about)
   - Hero: `Name_web.svg` fills a 1367×752 frame, scaled to 1438×1025 and offset (-24.8, -20.8) → the signature spans the full width across the top ~200px.
   - 12-photo grid, 4 columns × 3 rows, each ~199.6×133px, columns at x = 264.8 / 475.3 / 685.9 / 896.5, rows at y = 215.2 / 358.0 / 501.0.
   - About: "about me :)" (x 49, y 13); intro paragraph (x 130, y 178, w 502); linkedin link + email; portrait photo (x 912, y 225, 276×310) with italic caption "omw!" centred under it (y 539).
   - Three columns at y 808: "what i can do:" (x 257), "what i can use:" (x 534), "who i got to work with:" + "who i'm working with:" (x 882).
2. **alpha kappa psi** (1366 × 1768) — 3 portrait images (276×342) at y 153; title "alpha kappa psi community relations"; background / role; 3 cards (response, impact, skills).
3. **bits of good** (1366 × 2657) — wide hero image 776×342; background/role; image (719×317, framed) + skills card; response + impact cards; framed 2-image strip (1087×179).
4. **good molecules** (1366 × 2260) — hero 776×342; background/role; 4×2 image grid in a rounded frame (997×302); 3 cards.
5. **matmerize** (1366 × 2678) — hero 772×342; background/role; 2 tall images (293×454) + response card; impact + skills cards.
6. **mengseats** (1366 × 2818) — hero 737×342; background/role; framed image 714×330 + skills card; response + impact cards; 2 framed images 541×183.
7. **minturn whisky** (1366 × 3087) — hero 718×342; background/role; 2 framed tall images + text card; response + impact cards; text card + framed image + skills card.
8. **scheller college of business** (1366 × 2668) — hero 655×342; background/role; 2×2 images inside a rounded outline (765×448); 3 cards.

Shared project template: hero at y 153 (h 342) · centred blue title at y 600 · "background:" at x 136.6 / "role:" at x 683, y 737 · visuals · cards.

## Links found in the design

| Text | Target |
|---|---|
| linkedin | https://www.linkedin.com/in/kate-y-kwon |
| alpha kappa psi (home list) | internal → alpha kappa psi page |
| akpsi instagram | https://www.instagram.com/gtakpsi/ |
| bits of good instagram / substack / website | https://www.instagram.com/gtbitsofgood/ · https://bitsofgood.substack.com/?utm_campaign=profile_chips · https://bitsofgood.org |
| good molecules website | https://www.goodmolecules.com |
| matmerize website | https://www.matmerize.com |
| mengseats full report / website | Google Doc (`10lZNeCi…`) · https://www.mengseats.com |
| minturn instagram / website | https://www.instagram.com/minturnwhiskyco/ · https://minturnwhisky.com |

## Assets

44 image elements + `Name_web.svg`. Canva originals are 1170–4032px wide; most are named "OLYMPUS DIGITAL CAMERA" or "Screenshot", so they will be identified by Canva media ID and page position, not filename.

## Open questions / not determinable yet (not guessed)

1. **Font name.** Only Canva's internal reference is exposed. Need the name shown in the Canva font menu (or the live site's CSS).
2. **Navigation bar** — style, position, sticky or not, mobile menu. Canva generates it from page titles; only visible as a tiny strip in thumbnails.
3. **Single scrolling page vs. separate pages.** The internal link uses a `#page-…` anchor, which suggests one long page with anchors; needs confirming on the live site.
4. **Full-resolution images** — connector returns 200px thumbnails only.
5. **Only "alpha kappa psi" is linked** in the "who i got to work with" list; the other six names are plain text. Kept as-is unless you want them linked.
6. **Email is plain text** (no `mailto:`). Kept as-is unless you want it clickable.
7. **Stray empty links**: matmerize (empty link to matmerize.com), mengseats (empty link to mengseats.com), scheller background (empty link to goodmolecules.com — looks accidental).
8. **Possible typos preserved verbatim**: "study body", "colarado", "obivous", double spaces in a few sentences.
9. Hover/animation effects and favicon/browser title — not visible in design data.
