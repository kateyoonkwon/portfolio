"""Build the cross-stitch flower graphics.

  assets/flower.svg             the bare flower, shown on the home page
  assets/stamp.svg              the flower in a postage-stamp frame (site icon)
  assets/favicon-64.png         the stamp as a PNG icon
  assets/apple-touch-icon.png   the stamp for iPhone home screens

The flower is the traced cross-stitch chart in tools/flower_cells.json ([col, row]
per stitch). The stamp adds, on the same grid: 2 empty squares, a 1-square frame
line, 2 more empty squares, and a perforated edge of alternating squares.

Run from the repo root:  python3 tools/build_stamp.py   (needs Pillow)
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

BLUE = '#0970b8'
ROOT = Path(__file__).parent.parent
GAP_IN, FRAME, GAP_OUT, PERF = 2, 1, 2, 1     # squares, from the flower outwards


def size(cells):
    return max(c for c, _ in cells) + 1, max(r for _, r in cells) + 1


def svg(cells):
    """One path of row runs (1 unit = 1 square), drawn with crisp edges."""
    w, h = size(cells)
    runs, filled = [], set(cells)
    for r in range(h):
        c = 0
        while c < w:
            if (c, r) in filled:
                end = c
                while (end, r) in filled:
                    end += 1
                runs.append(f'M{c} {r}h{end - c}v1h-{end - c}z')
                c = end
            else:
                c += 1
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 8}" height="{h * 8}" '
            f'shape-rendering="crispEdges"><path fill="{BLUE}" d="{"".join(runs)}"/></svg>\n')


def stamp(flower):
    fw, fh = size(flower)
    m = GAP_IN + FRAME + GAP_OUT + PERF            # squares from the edge to the flower
    w, h = fw + 2 * m, fh + 2 * m
    cells = {(c + m, r + m) for c, r in flower}
    for r in range(h):                             # perforated edge
        for c in range(w):
            on_edge = r in (0, h - 1) or c in (0, w - 1)
            k = c if r in (0, h - 1) else r
            if on_edge and k % 2 == 1:
                cells.add((c, r))
    f = PERF + GAP_OUT                             # frame line
    for r in range(f, h - f):
        for c in range(f, w - f):
            if r in (f, h - f - 1) or c in (f, w - f - 1):
                cells.add((c, r))
    return cells


def png(cells, side, path):
    """Square, transparent PNG with the cells scaled to fit and centred."""
    w, h = size(cells)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for c, r in cells:
        draw.point((c, r), fill=BLUE)
    scale = side / max(w, h)
    img = img.resize((round(w * scale), round(h * scale)), Image.NEAREST)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    canvas.save(path)


flower = [tuple(p) for p in json.loads((ROOT / 'tools/flower_cells.json').read_text())]
framed = stamp(flower)
(ROOT / 'assets/flower.svg').write_text(svg(flower))
(ROOT / 'assets/stamp.svg').write_text(svg(framed))
png(framed, 180, ROOT / 'assets/apple-touch-icon.png')
png(framed, 64, ROOT / 'assets/favicon-64.png')
print(f'flower {size(flower)}, stamp {size(framed)}, {len(flower)} stitches')
