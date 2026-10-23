"""Turn a line of text into Name_web-style pixel "cross-stitch" squares.

Renders the text in a script font, traces the centre line of each stroke,
snaps it to a square grid (4-connected, like Name_web.svg), and numbers the
squares in pen order so they can be revealed as if written by hand.

Usage: python3 tools/stitch_title.py FONT.ttf "text" [cells_per_em]
Prints JSON: {"w": cols, "h": rows, "cells": [[col, row], ...in drawing order]}
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.morphology import skeletonize


def stitch(font_path, text, cells_per_em=22, size=440):
    font = ImageFont.truetype(font_path, size)
    l, t, r, b = font.getbbox(text)
    pad = size // 4
    img = Image.new('L', (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(img).text((pad - l, pad - t), text, font=font, fill=255)
    skel = skeletonize(np.array(img) > 128)

    s = size / cells_per_em
    ys, xs = np.nonzero(skel)
    cells = {(int(x // s), int(y // s)) for x, y in zip(xs, ys)}

    # Make diagonal steps 4-connected (a staircase), as in Name_web.svg.
    for (c, r_) in list(cells):
        for dc, dr in ((1, 1), (1, -1)):
            n = (c + dc, r_ + dr)
            if n in cells and (c + dc, r_) not in cells and (c, r_ + dr) not in cells:
                cells.add((c, r_ + dr) if dr > 0 else (c + dc, r_))

    # Pen order: start at the leftmost square, keep stepping to the nearest unvisited
    # square (neighbours first), which follows the strokes from left to right.
    left = set(cells)
    cur = min(left, key=lambda p: (p[0], p[1]))
    order = []
    while left:
        left.discard(cur)
        order.append(cur)
        if not left:
            break
        near = [p for p in ((cur[0] + dx, cur[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) if p in left]
        if near:
            # prefer orthogonal neighbours, then those further right
            cur = min(near, key=lambda p: (abs(p[0] - cur[0]) + abs(p[1] - cur[1]), -p[0]))
        else:
            cur = min(left, key=lambda p: (p[0] - cur[0]) ** 2 + (p[1] - cur[1]) ** 2)

    c0 = min(p[0] for p in order); r0 = min(p[1] for p in order)
    order = [(c - c0, r - r0) for c, r in order]
    return {'w': max(p[0] for p in order) + 1, 'h': max(p[1] for p in order) + 1, 'cells': order}


if __name__ == '__main__':
    cpe = int(sys.argv[3]) if len(sys.argv) > 3 else 22
    print(json.dumps(stitch(sys.argv[1], sys.argv[2], cpe)))
