"""Rebuild the stitched (pixel-square cursive) project titles in projects.html.

Each <h2 class="title stitch" data-text="..."> is rebuilt from its data-text:
  - one line            -> straddles the cover image's top-left corner
  - two lines ("a|b")   -> "a" straddles the top-left corner, "b" the bottom-right
Lines are centred on the corner (half over the image, half outside), nudged in
so they stay on the page. A separate wrapped SVG is used on phones. Every square
carries --i, its place in pen order, so CSS can reveal them one by one.

It then moves the background/role boxes (and everything below) so they start a
fixed gap under the cover or the lowest title line.

Run from the repo root:  python3 tools/build_titles.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stitch_title import stitch  # noqa: E402

FONT = str(Path(__file__).parent / 'DancingScript.ttf')
CPE = 32           # grid squares per em
CELL = 3           # page units (Canva px) per square on desktop
LINE_GAP = 4       # empty rows between lines in the phone layout
PHONE_COLS = 150   # max squares per line in the phone layout
PAGE = (24, 1342)  # keep titles inside these x bounds
GAP_BELOW = 80     # space between cover/title and the background/role boxes
TOTAL_MS = 2400    # a whole title writes itself in about this long


def rects(cells, start, step):
    return ''.join(f'<rect x="{c * 4}" y="{r * 4}" width="4" height="4" style="--i:{start + i}"/>'
                   for i, (c, r) in enumerate(cells))


def wrap(text):
    lines, cur = [], ''
    for word in text.replace('|', ' ').split():
        trial = (cur + ' ' + word).strip()
        if cur and stitch(FONT, trial, CPE)['w'] > PHONE_COLS:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def stack(lines):
    parts = [stitch(FONT, t, CPE) for t in lines]
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
    lines = [stitch(FONT, t, CPE) for t in text.split('|')]
    total = sum(len(l['cells']) for l in lines)
    step = round(TOTAL_MS / total, 2)

    svgs, start, lowest = [], 0, bottom
    for line, (cx, cy) in zip(lines, corners):
        w, h = line['w'] * CELL, line['h'] * CELL
        x = min(max(cx - w / 2, PAGE[0]), PAGE[1] - w)
        y = cy - h / 2
        lowest = max(lowest, y + h)
        svgs.append(f'<svg class="el stitch-line stitch-wide" style="--x:{x:.1f};--y:{y:.1f};--w:{w};--h:{h};--step:{step}ms" '
                    f'viewBox="0 0 {line["w"] * 4} {line["h"] * 4}" aria-hidden="true" focusable="false">'
                    f'{rects(line["cells"], start, step)}</svg>')
        start += len(line['cells'])

    pw, ph, pcells = stack(wrap(text))
    pstep = round(TOTAL_MS / len(pcells), 2)
    svgs.append(f'<svg class="el stitch-line stitch-narrow" style="--x:0;--y:0;--w:{pw * CELL};--h:{ph * CELL};--step:{pstep}ms" '
                f'viewBox="0 0 {pw * 4} {ph * 4}" aria-hidden="true" focusable="false">{rects(pcells, 0, pstep)}</svg>')

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
