"""Rebuild the stitched (pixel-square cursive) project titles in projects.html.

Each <h2 class="title stitch" data-text="..."> is rebuilt from its data-text:
  - one line            -> overlaps the cover image's top-left corner
  - two lines ("a|b")   -> "a" overlaps the top-left corner, "b" the bottom-right
A first line starts at the left edge of the background box; a second line ends
at the right edge of the role box. The middle of each line's lowercase letters sits on
the image edge it crosses. A separate wrapped SVG is used on phones.

It then moves the background/role boxes (and everything below) so they start a
fixed gap under the cover or the lowest title line.

Run from the repo root:  python3 tools/build_titles.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stitch_title import stitch  # noqa: E402

CELL = 7           # page units (Canva px) per square on desktop
LINE_GAP = 3       # empty rows between lines in the phone layout
PHONE_COLS = 72    # max squares per line in the phone layout
GAP_BELOW = 80     # space between cover/title and the background/role boxes


def rects(cells):
    return ''.join(f'<rect x="{c * 4}" y="{r * 4}" width="4" height="4"/>' for c, r in cells)


def wrap(text):
    lines, cur = [], ''
    for word in text.replace('|', ' ').split():
        trial = (cur + ' ' + word).strip()
        if cur and stitch(trial)['w'] > PHONE_COLS:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def stack(lines):
    parts = [stitch(t) for t in lines]
    w = max(p['w'] for p in parts)
    cells, y = [], 0
    for p in parts:
        x0 = (w - p['w']) // 2
        cells += [(c + x0, r + y) for c, r in p['cells']]
        y += p['h'] + LINE_GAP
    return w, y - LINE_GAP, cells


def build_section(sec_match):
    sec = sec_match.group(0)
    covers = [tuple(map(float, m)) for m in re.findall(
        r'class="el img cover" style="--x:([\d.]+);--y:([\d.]+);--w:([\d.]+);--h:([\d.]+)"', sec)]
    left = min(c[0] for c in covers); top = min(c[1] for c in covers)
    right = max(c[0] + c[2] for c in covers); bottom = max(c[1] + c[3] for c in covers)
    corners = [(left, top), (right, bottom)]

    m = re.search(r'<h2 class="(?:el )?title stitch"[^>]*?data-text="([^"]+)">.*?</h2>', sec, re.S)
    text = m.group(1)
    lines = [stitch(t) for t in text.split('|')]
    boxes = [tuple(map(float, m)) for m in re.findall(
        r'class="el t box" style="--x:([\d.]+);--y:[\d.]+;--w:([\d.]+)', sec)]
    box_left = min(b[0] for b in boxes); box_right = max(b[0] + b[1] for b in boxes)

    svgs, lowest = [], bottom
    for i, (line, (_, cy)) in enumerate(zip(lines, corners)):
        w, h = line['w'] * CELL, line['h'] * CELL
        x = box_left if i == 0 else box_right - w
        y = cy - (line['baseline'] - 3) * CELL   # middle of the x-height on the image edge
        lowest = max(lowest, y + h)
        svgs.append(f'<svg class="el stitch-line stitch-wide" style="--x:{x:.1f};--y:{y:.1f};--w:{w};--h:{h}" '
                    f'viewBox="0 0 {line["w"] * 4} {line["h"] * 4}" aria-hidden="true" focusable="false">'
                    f'{rects(line["cells"])}</svg>')

    pw, ph, pcells = stack(wrap(text))
    svgs.append(f'<svg class="el stitch-line stitch-narrow" style="--x:0;--y:0;--w:{pw * CELL};--h:{ph * CELL}" '
                f'viewBox="0 0 {pw * 4} {ph * 4}" aria-hidden="true" focusable="false">{rects(pcells)}</svg>')

    h2 = (f'<h2 class="title stitch" data-text="{text}"><span class="visually-hidden">{text.replace("|", " ")}</span>'
          + ''.join(svgs) + '</h2>')
    sec = sec[:m.start()] + h2 + sec[m.end():]

    # Move the background/role boxes, and everything from them down, to sit GAP_BELOW under the title.
    box_top = float(re.search(r'class="el t box" style="--x:[\d.]+;--y:([\d.]+)', sec).group(1))
    shift = round(lowest + GAP_BELOW - box_top, 1)

    def move(mm):
        st = mm.group(2)
        y = float(re.search(r'--y:(-?[\d.]+)', st).group(1))
        if y >= box_top - 1 and 'stitch-line' not in mm.group(1):
            st = re.sub(r'--y:-?[\d.]+', f'--y:{round(y + shift, 1):g}', st)
        return mm.group(1) + st + '"'

    sec = re.sub(r'(class="el(?: [^"]*)?" style=")([^"]*)"', move, sec)
    sec = re.sub(r'(<div class="board" style="--h:)([\d.]+)',
                 lambda mm: mm.group(1) + f'{round(float(mm.group(2)) + shift, 1):g}', sec, count=1)
    print(f'{text!r:40} lines={len(lines)} boxes shifted {shift:+}')
    return sec


page = Path('projects.html')
html = re.sub(r'<section id="[^"]+".*?</section>', build_section, page.read_text(), flags=re.S)
page.write_text(html)
