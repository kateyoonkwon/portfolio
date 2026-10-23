"""Turn a line of lowercase text into cross-stitch cursive squares.

Letters come from a hand-made cross-stitch cursive alphabet (tools/cursive_glyphs.json:
for each letter, its filled squares as [column, row] with row 0 = the square just
above the baseline, negative = up). Letters are set left to right and pulled
together until they are GAP squares apart on any shared row, so slanted letters
tuck in the way handwriting does. Within a word, each letter is joined to the
next along the baseline: from the previous letter's rightmost square in the bottom
two rows to the new letter's leftmost square in the bottom two rows (cursive
joins run along the bottom, so letter shapes stay open). Short gaps only, and
only between letters that join that way in handwriting (see JOIN_INTO/JOIN_FROM).

Usage: python3 tools/stitch_title.py "text"
Prints JSON: {"w": cols, "h": rows, "cells": [[col, row], ...]}
"""
import json
import sys
from pathlib import Path

GLYPHS = json.loads((Path(__file__).parent / 'cursive_glyphs.json').read_text())
GAP = 1          # empty squares between neighbouring letters
WORD_SPACE = 4   # empty squares between words
# Baseline joins go only into letters that start with an upstroke from the baseline,
# and only out of letters that end on the baseline (o, b, v, w end at the top; joining
# into round letters like a, c, e, o, s along the bottom would close them up).
JOIN_INTO = set('fhijklmnprtuy')
JOIN_FROM = set('acdefhiklmnpqrtuxyz')  # not s: a tail off its curve reads as an e


def join(a, b):
    """4-connected staircase of squares from a to b (exclusive of both ends)."""
    (c1, r1), (c2, r2) = a, b
    out, c, r = [], c1, r1
    while (c, r) != (c2, r2):
        dc, dr = c2 - c, r2 - r
        # step in the direction that keeps us closest to the straight line
        if dc and (not dr or abs(dc) * 1.0 / (abs(c2 - c1) or 1) >= abs(dr) * 1.0 / (abs(r2 - r1) or 1)):
            c += 1 if dc > 0 else -1
        else:
            r += 1 if dr > 0 else -1
        out.append((c, r))
    return out[:-1]


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
            placed = {(c + x, r) for c, r in g}
            if li:
                low = [p for p in prev if -2 <= p[1] <= -1]
                ent = [p for p in placed if -2 <= p[1] <= -1]
                if low and ent and word[li - 1] in JOIN_FROM and ch in JOIN_INTO:
                    ex = max(low, key=lambda p: (p[0], p[1]))
                    en = min(ent, key=lambda p: (p[0], -p[1]))
                    if 1 < en[0] - ex[0] <= 4:
                        cells |= set(join(ex, en))
            cells |= placed
            prev = placed
    c0 = min(c for c, _ in cells); r0 = min(r for _, r in cells)
    out = sorted([[c - c0, r - r0] for c, r in cells], key=lambda p: (p[0], p[1]))
    return {'w': max(p[0] for p in out) + 1, 'h': max(p[1] for p in out) + 1,
            'baseline': -r0, 'cells': out}


if __name__ == '__main__':
    print(json.dumps(stitch(sys.argv[1])))
