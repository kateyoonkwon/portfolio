"""Rebuild the stitched (pixel-square cursive) project titles in projects.html.

Each <h2 class="el title stitch" data-text="..."> gets two inline SVGs: a desktop
layout (lines as given, "|" = line break) and a narrower phone layout. Every
square carries --i, its position in pen order, so CSS can reveal them one by one.

Run from the repo root:  python3 tools/build_titles.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stitch_title import stitch  # noqa: E402

FONT = str(Path(__file__).parent / 'DancingScript.ttf')
CPE = 32          # grid squares per em
CELL = 3          # page units (Canva px) per square on desktop
LINE_GAP = 4      # empty rows between lines
PHONE_COLS = 150  # max squares per line in the phone layout
COVER_BOTTOM = 495  # covers sit at y 153, 342 tall; titles centre between this and the boxes


def layout(lines):
    parts = [stitch(FONT, t, CPE) for t in lines]
    w = max(p['w'] for p in parts)
    cells, y = [], 0
    for p in parts:
        x0 = (w - p['w']) // 2
        cells += [(c + x0, r + y) for c, r in p['cells']]
        y += p['h'] + LINE_GAP
    return w, y - LINE_GAP, cells


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


def svg(w, h, cells, cls):
    step = round(2400 / len(cells), 2)  # whole title writes itself in ~2.4s
    rects = ''.join(f'<rect x="{c * 4}" y="{r * 4}" width="4" height="4" style="--i:{i}"/>'
                    for i, (c, r) in enumerate(cells))
    return (f'<svg class="{cls}" viewBox="0 0 {w * 4} {h * 4}" style="--step:{step}ms" '
            f'aria-hidden="true" focusable="false">{rects}</svg>')


def build(match, box_top):
    attrs, text = match.group(1), match.group(2)
    w, h, cells = layout(text.split('|'))
    pw, ph, pcells = layout(wrap(text))
    width, height = w * CELL, h * CELL
    x = round(683 - width / 2, 1)
    y = round((COVER_BOTTOM + box_top) / 2 - height / 2, 1)
    attrs = re.sub(r'style="[^"]*"', f'style="--x:{x};--y:{y};--w:{width};--h:{height}"', attrs)
    label = text.replace('|', ' ')
    return (f'<h2{attrs} data-text="{text}"><span class="visually-hidden">{label}</span>'
            f'{svg(w, h, cells, "stitch-wide")}{svg(pw, ph, pcells, "stitch-narrow")}</h2>')


page = Path('projects.html')
html = page.read_text()
count = 0


def build_section(sec):
    global count
    box_top = float(re.search(r'class="el t box" style="--x:[\d.]+;--y:([\d.]+)', sec.group(0)).group(1))
    out, n = re.subn(r'<h2( class="el title stitch"[^>]*?) data-text="([^"]+)">.*?</h2>',
                     lambda m: build(m, box_top), sec.group(0), flags=re.S)
    count += n
    return out


html = re.sub(r'<section id="[^"]+".*?</section>', build_section, html, flags=re.S)
page.write_text(html)
print(f'rebuilt {count} titles')
