"""Rebuild the cross-stitch project titles in projects.html.

Each <h2 class="title stitch" data-text="..."> is rebuilt from its data-text
(lowercase a-z and spaces; "|" splits it into two lines):
  - the first line overlaps the cover's top-left corner, starting at the left
    edge of the background box;
  - a second line overlaps the cover's bottom-right corner, ending at the right
    edge of the role box.
The middle of each line's lowercase letters sits on the image edge it crosses.
On phones the same SVGs are re-positioned by CSS (see .cover-group).

The background/role boxes and everything below them are then moved so they start
GAP_BELOW under the cover or the lowest title line.

Run from the repo root:  python3 tools/build_titles.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stitch_title import stitch  # noqa: E402

CELL = 7         # page units (Canva px) per square
GAP_BELOW = 80   # space between the cover/title and the background/role boxes

NUM = r'(-?[\d.]+)'


def rects(cells):
    return ''.join(f'<rect x="{c * 4}" y="{r * 4}" width="4" height="4"/>' for c, r in cells)


def build_section(match):
    sec = match.group(0)
    covers = [tuple(map(float, m)) for m in re.findall(
        rf'class="el img cover" style="--x:{NUM};--y:{NUM};--w:{NUM};--h:{NUM}"', sec)]
    left, top = min(c[0] for c in covers), min(c[1] for c in covers)
    right, bottom = max(c[0] + c[2] for c in covers), max(c[1] + c[3] for c in covers)
    boxes = [tuple(map(float, m)) for m in re.findall(
        rf'class="el t box" style="--x:{NUM};--y:{NUM};--w:{NUM}', sec)]
    box_left = min(b[0] for b in boxes)
    box_right = max(b[0] + b[2] for b in boxes)
    box_top = min(b[1] for b in boxes)

    h2 = re.search(r'<h2 class="title stitch" data-text="([^"]+)">.*?</h2>', sec, re.S)
    text = h2.group(1)
    svgs, lowest = [], bottom
    for i, (line, edge_y) in enumerate(zip((stitch(t) for t in text.split('|')), (top, bottom))):
        w, h = line['w'] * CELL, line['h'] * CELL
        x = box_left if i == 0 else box_right - w
        y = edge_y - (line['baseline'] - 3) * CELL   # middle of the x-height on the image edge
        lowest = max(lowest, y + h)
        svgs.append(f'<svg class="el stitch-line" style="--x:{x:.1f};--y:{y:.1f};--w:{w};--h:{h}" '
                    f'viewBox="0 0 {line["w"] * 4} {line["h"] * 4}" aria-hidden="true" focusable="false">'
                    f'{rects(line["cells"])}</svg>')
    sec = (sec[:h2.start()]
           + f'<h2 class="title stitch" data-text="{text}"><span class="visually-hidden">{text.replace("|", " ")}</span>'
           + ''.join(svgs) + '</h2>' + sec[h2.end():])

    # Move the boxes, and everything from them down, to sit GAP_BELOW under the title.
    shift = round(lowest + GAP_BELOW - box_top, 1)

    def move(m):
        style = m.group(2)
        y = float(re.search(r'--y:' + NUM, style).group(1))
        if y >= box_top - 1 and 'stitch-line' not in m.group(1):
            style = re.sub(r'--y:' + NUM, f'--y:{round(y + shift, 1):g}', style, count=1)
        return m.group(1) + style + '"'

    sec = re.sub(r'(class="el(?: [^"]*)?" style=")([^"]*)"', move, sec)
    sec = re.sub(r'(<div class="board" style="--h:)([\d.]+)',
                 lambda m: m.group(1) + f'{round(float(m.group(2)) + shift, 1):g}', sec, count=1)
    print(f'{text!r:40} boxes shifted {shift:+}')
    return sec


page = Path('projects.html')
page.write_text(re.sub(r'<section id="[^"]+".*?</section>', build_section, page.read_text(), flags=re.S))
