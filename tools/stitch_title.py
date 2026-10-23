"""Turn a line of lowercase text into cross-stitch cursive squares.

Letters come from a hand-made cross-stitch cursive alphabet (tools/cursive_glyphs.json:
for each letter, its filled squares as [column, row] with row 0 = the square just
above the baseline, negative = up). Letters are set left to right and pulled
together until they are GAP squares apart on any shared row, so slanted letters
tuck in the way handwriting does.

Usage: python3 tools/stitch_title.py "text"
Prints JSON: {"w": cols, "h": rows, "cells": [[col, row], ...]}
"""
import json
import sys
from pathlib import Path

GLYPHS = json.loads((Path(__file__).parent / 'cursive_glyphs.json').read_text())
GAP = 1          # empty squares between neighbouring letters
WORD_SPACE = 4   # empty squares between words


def stitch(text):
    cells = set()
    for wi, word in enumerate(text.lower().split()):
        for li, ch in enumerate(word):
            g = GLYPHS[ch]
            gap = WORD_SPACE if (wi and li == 0) else GAP
            if not cells:
                x = 0
            else:
                # Slide the letter left until it is `gap` squares from what's there on every row.
                right, left = {}, {}
                for c, r in cells:
                    right[r] = max(right.get(r, -10**6), c)
                for c, r in g:
                    left[r] = min(left.get(r, 10**6), c)
                rows = set(right) & set(left)
                x = (max(right[r] - left[r] for r in rows) + gap + 1 if rows
                     else max(c for c, _ in cells) + gap + 1)
            cells |= {(c + x, r) for c, r in g}
    c0 = min(c for c, _ in cells); r0 = min(r for _, r in cells)
    out = sorted([[c - c0, r - r0] for c, r in cells], key=lambda p: (p[0], p[1]))
    return {'w': max(p[0] for p in out) + 1, 'h': max(p[1] for p in out) + 1,
            'baseline': -r0, 'cells': out}


if __name__ == '__main__':
    print(json.dumps(stitch(sys.argv[1])))
