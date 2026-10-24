"""Build the cross-stitch flower (assets/flower.svg, used on the page), the flower
stamp (assets/stamp.svg) and the site icons (made from the stamp).

The flower is the traced cross-stitch chart (tools/flower_cells.json, [col, row]).
Around it, on the same grid: 2 squares of paper, a 1-square frame line, 2 more
squares of paper, and a perforated edge (alternating squares), all in blue; the paper is left transparent.

Run from the repo root:  python3 tools/build_stamp.py
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

BLUE = '#0970b8'
ROOT = Path(__file__).parent.parent

flower = json.loads((ROOT / 'tools/flower_cells.json').read_text())
fw = max(c for c, _ in flower) + 1
fh = max(r for _, r in flower) + 1
PAD_IN, FRAME, PAD_OUT, PERF = 2, 1, 2, 1
m = PAD_IN + FRAME + PAD_OUT + PERF          # squares from the edge to the flower
W, H = fw + 2 * m, fh + 2 * m

ink = set()
for r in range(H):
    for c in range(W):
        edge = r in (0, H - 1) or c in (0, W - 1)
        if edge:
            k = c if r in (0, H - 1) else r
            if k % 2 == 1:                       # perforation: every other square
                ink.add((c, r))
f0 = PERF + PAD_OUT                              # frame line position
for r in range(f0, H - f0):
    for c in range(f0, W - f0):
        if r in (f0, H - f0 - 1) or c in (f0, W - f0 - 1):
            ink.add((c, r))
ink |= {(c + m, r + m) for c, r in flower}


def runs(cells):
    out = []
    for r in range(H):
        c = 0
        while c < W:
            if (c, r) in cells:
                e = c
                while (e, r) in cells:
                    e += 1
                out.append(f'M{c} {r}h{e - c}v1h-{e - c}z')
                c = e
            else:
                c += 1
    return ''.join(out)


svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 8}" height="{H * 8}" '
       f'shape-rendering="crispEdges"><path fill="{BLUE}" d="{runs(ink)}"/></svg>\n')
(ROOT / 'assets/stamp.svg').write_text(svg)

fl = set(map(tuple, flower))
W0, H0, W, H = W, H, fw, fh          # runs() reads W/H: reuse it for the bare flower
(ROOT / 'assets/flower.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fw} {fh}" width="{fw * 8}" height="{fh * 8}" '
    f'shape-rendering="crispEdges"><path fill="{BLUE}" d="{runs(fl)}"/></svg>\n')
W, H = W0, H0


def png(size, path):
    s = max(1, size // max(W, H))
    img = Image.new('RGBA', (W * s, H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for cells, col in ((ink, BLUE),):
        for c, r in cells:
            d.rectangle([c * s, r * s, c * s + s - 1, r * s + s - 1], fill=col)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    img = img.resize((round(W * size / max(W, H)), round(H * size / max(W, H))), Image.NEAREST)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    canvas.save(path)


png(180, ROOT / 'assets/apple-touch-icon.png')
png(64, ROOT / 'assets/favicon-64.png')
print(f'stamp {W}x{H} squares, flower {fw}x{fh}, {len(flower)} stitches')
