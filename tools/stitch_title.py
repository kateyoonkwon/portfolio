"""Turn a line of text into Name_web-style pixel "cross-stitch" squares, in pen order.

Follows how cursive is written by hand:
  - each word is one continuous stroke, written left to right; at crossings the pen
    keeps going in the direction it was already travelling (loops cross themselves),
    and short retraces (down the stem of a d, back up an a) are covered without a lift;
  - i/j dots and t crossbars (small separate marks) are added after the word is done;
  - the pen pauses briefly at each lift and a little longer between words.

The glyphs come from a script font: each word is rendered large, thinned to its
centre line, traced as pen paths, then laid onto a coarse grid as a one-square-wide,
4-connected line (diagonals become staircases, as in Name_web.svg).

Usage: python3 tools/stitch_title.py FONT.ttf "text" [cells_per_em]
Prints JSON: {"w": cols, "h": rows, "cells": [[col, row, ms], ...in drawing order]}
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import label
from skimage.morphology import skeletonize

SIZE = 440            # render size (px per em) for tracing
STEP_MS = 9           # time per square while the pen is moving
LIFT_MS = 140         # pause when the pen lifts within a word
WORD_MS = 260         # pause between words
DOT_FRACTION = 0.12   # marks shorter than this (x em) are dots/crossbars, drawn last
SPUR_FRACTION = 0.03  # skeleton branches shorter than this (x em) are noise
RETRACE_FRACTION = 0.08  # hops shorter than this (x em) are retraces, not pen lifts
STRETCH = 1.3         # horizontal stretch; >1 opens up loops on a coarse grid

N8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def neighbours(p, pts):
    x, y = p
    return [(x + dx, y + dy) for dx, dy in N8 if (x + dx, y + dy) in pts]


def prune_spurs(pts, max_len):
    """Remove short dead-end branches left by thinning."""
    pts = set(pts)
    for _ in range(3):
        ends = [p for p in pts if len(neighbours(p, pts)) == 1]
        removed = False
        for e in ends:
            branch, cur, prev = [e], e, None
            while True:
                nb = [q for q in neighbours(cur, pts) if q != prev and q not in branch]
                if len(nb) != 1 or len(neighbours(nb[0], pts)) > 2:
                    break
                prev, cur = cur, nb[0]
                branch.append(cur)
                if len(branch) > max_len:
                    break
            junction = [q for q in neighbours(branch[-1], pts) if q not in branch]
            if len(branch) <= max_len and len(junction) >= 2:
                pts.difference_update(branch)
                removed = True
        if not removed:
            break
    return pts


def trace(pts):
    """Order a connected set of skeleton pixels as pen paths. Returns a list of strokes."""
    left = set(pts)
    ends = [p for p in left if len(neighbours(p, left)) == 1]
    cur = min(ends or left, key=lambda p: (p[0], -p[1]))  # leftmost entry stroke
    strokes, path = [], [cur]
    left.discard(cur)
    while left:
        nb = neighbours(cur, left)
        if nb:
            if len(path) >= 2:
                k = path[max(0, len(path) - 6)]
                hx, hy = cur[0] - k[0], cur[1] - k[1]
                h = math.atan2(hy, hx)
                nb.sort(key=lambda q: abs((math.atan2(q[1] - cur[1], q[0] - cur[0]) - h + math.pi) % (2 * math.pi) - math.pi))
            else:
                nb.sort(key=lambda q: (-(q[0] - cur[0]), q[1] - cur[1]))
            cur = nb[0]
        else:
            # Dead end. Go back for the leftmost branch the pen skipped (it grows out of
            # what is already drawn); if a branch starts right here, it is just a retrace.
            done = pts - left
            frontier = [q for q in left if any(n in done for n in neighbours(q, pts))]
            if frontier:
                near = min(frontier, key=lambda q: (q[0] - cur[0]) ** 2 + (q[1] - cur[1]) ** 2)
                nxt = near if math.dist(near, cur) <= RETRACE_FRACTION * SIZE else min(frontier)
            else:
                nxt = min(left, key=lambda q: (q[0] - cur[0]) ** 2 + (q[1] - cur[1]) ** 2)
            if math.dist(nxt, cur) > RETRACE_FRACTION * SIZE:
                strokes.append(path)
                path = []
            cur = nxt
        path.append(cur)
        left.discard(cur)
    strokes.append(path)
    return strokes


def word_strokes(font, word):
    """Pen strokes for one word, in writing order; dots/crossbars last. Each stroke is
    (points, is_mark)."""
    l, t, r, b = font.getbbox(word)
    pad = SIZE // 4
    img = Image.new('L', (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(img).text((pad - l, pad - t), word, font=font, fill=255)
    if STRETCH != 1:
        img = img.resize((round(img.width * STRETCH), img.height), Image.BICUBIC)
    skel = skeletonize(np.array(img) > 128)
    labels = label(skel, connectivity=2)
    bodies, marks = [], []
    for k in range(1, labels.max() + 1):
        ys, xs = np.nonzero(labels == k)
        pts = set(zip((xs - round((pad - l) * STRETCH)).tolist(), (ys - pad + t).tolist()))
        if len(pts) < 4:  # stray pixels
            continue
        pts = prune_spurs(pts, int(SPUR_FRACTION * SIZE))
        (marks if len(pts) < DOT_FRACTION * SIZE else bodies).append(pts)
    bodies.sort(key=lambda p: min(q[0] for q in p))
    marks.sort(key=lambda p: min(q[0] for q in p))
    out = []
    for p in bodies:
        out += [(s, False) for s in trace(p)]
    for p in marks:
        out += [(s, True) for s in trace(p)]
    return out


def stitch(font_path, text, cells_per_em=24):
    font = ImageFont.truetype(font_path, SIZE)
    s = SIZE / cells_per_em
    space = font.getlength(' ')
    x_off, t_ms, cells, seen = 0.0, 0, [], set()
    for wi, word in enumerate(text.split()):
        if wi:
            t_ms += WORD_MS
        for si, (stroke, _mark) in enumerate(word_strokes(font, word)):
            if si:
                t_ms += LIFT_MS
            prev = None
            for x, y in stroke:
                c = (int((x + x_off) // s), int(y // s))
                if c == prev:
                    continue
                path = [c]
                if prev and abs(c[0] - prev[0]) == 1 and abs(c[1] - prev[1]) == 1:
                    path = [(c[0], prev[1]), c]          # diagonal step -> staircase
                elif prev and max(abs(c[0] - prev[0]), abs(c[1] - prev[1])) > 1:
                    path = [c]                           # tiny jump: no filler
                for q in path:
                    if q not in seen:
                        seen.add(q)
                        cells.append([q[0], q[1], t_ms])
                        t_ms += STEP_MS
                prev = c
        x_off += (font.getlength(word) + space) * STRETCH
    c0 = min(c[0] for c in cells); r0 = min(c[1] for c in cells)
    cells = [[c - c0, r - r0, ms] for c, r, ms in cells]
    return {'w': max(c[0] for c in cells) + 1, 'h': max(c[1] for c in cells) + 1, 'cells': cells}


if __name__ == '__main__':
    cpe = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    print(json.dumps(stitch(sys.argv[1], sys.argv[2], cpe)))
