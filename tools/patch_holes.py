"""Fill the holes other layers left in the body, paper and stand cutouts.

The Figma layers are cutouts of one 3D render, so wherever one layer sat in
front of another, the one behind is missing those pixels. The coins are
dropped, and the paper now slides out of the body, so those holes show.

Each hole sits on a straight outer edge, so the layer's true outline there is
its convex hull. Pixels inside the hull that are not solid
are filled by harmonic interpolation from the solid pixels around them, which
suits these smooth, matte surfaces.

    python3 tools/patch_holes.py

Reads reference/layers/<name>.png (untouched Figma exports) and writes
pos_printing/assets/<name>.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import png  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# name -> window (x0, y0, x1, y1) in source pixels that contains the hole.
# The hull is taken over the solid pixels in this window only, so the rest of
# the outline (the paper's curl, for one) keeps its concave shape.
HOLES = {
    'body': (0, 0, 418, 140),
    'paper': (140, 0, 300, 150),
    'stand': (0, 0, 173, 244),
}

SOLID = 250      # alpha at or above this counts as solid source colour
ERODE = 4        # px; drops the hole's rim, which carries the coins' gold bounce light
SUPERSAMPLE = 4  # per axis, for the hull edge's alpha
ITERATIONS = 1500


def hull(points):
    points = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def inside(poly, x, y):
    # Convex polygon, counter-clockwise in y-down space as built by hull().
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        if (bx - ax) * (y - ay) - (by - ay) * (x - ax) < 0:
            return False
    return True


def patch(name):
    w, h, px = png.read(os.path.join(ROOT, 'reference', 'layers', name + '.png'))
    x0, y0, x1, y1 = HOLES[name]
    alpha = [[p[3] for p in row] for row in px]

    # Pixel centres sit at +0.5; the hull runs through solid pixels' corners.
    solid = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if alpha[y][x] >= SOLID]
    poly = hull([(x + dx, y + dy) for x, y in solid for dx in (0, 1) for dy in (0, 1)])

    def is_source(x, y):
        for yy in range(y - ERODE, y + ERODE + 1):
            for xx in range(x - ERODE, x + ERODE + 1):
                if not (0 <= xx < w and 0 <= yy < h) or alpha[yy][xx] < SOLID:
                    return False
        return True

    unknown, coverage = [], {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = SUPERSAMPLE
            c = sum(inside(poly, x + (i + 0.5) / n, y + (j + 0.5) / n) for i in range(n) for j in range(n))
            if c and not is_source(x, y):
                unknown.append((x, y))
                coverage[(x, y)] = c / (n * n)

    # Start each unknown pixel from the mean of the sources around it, then
    # relax towards the harmonic solution.
    colour = {}
    known = lambda x, y: (x, y) not in coverage and alpha[y][x] >= SOLID  # noqa: E731
    for x, y in unknown:
        r = 1
        while True:
            near = [px[yy][xx] for yy in range(max(0, y - r), min(h, y + r + 1))
                    for xx in range(max(0, x - r), min(w, x + r + 1)) if known(xx, yy)]
            if near:
                colour[(x, y)] = [sum(p[k] for p in near) / len(near) for k in range(3)]
                break
            r *= 2
    for _ in range(ITERATIONS):
        nxt = {}
        for x, y in unknown:
            acc, cnt = [0.0, 0.0, 0.0], 0
            for xx, yy in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (xx, yy) in colour:
                    c = colour[(xx, yy)]
                elif 0 <= xx < w and 0 <= yy < h and known(xx, yy):
                    c = px[yy][xx]
                else:
                    continue
                acc = [acc[k] + c[k] for k in range(3)]
                cnt += 1
            nxt[(x, y)] = [a / cnt for a in acc] if cnt else colour[(x, y)]
        colour = nxt

    filled = 0
    for x, y in unknown:
        # Repaint solid rim pixels too: their colour is tinted by the coin.
        a = max(alpha[y][x], round(255 * coverage[(x, y)]))
        px[y][x] = [round(v) for v in colour[(x, y)]] + [a]
        filled += 1
    png.write(os.path.join(ROOT, 'pos_printing', 'assets', name + '.png'), w, h, px)
    print(f'{name}: hull {len(poly)} points, {filled} pixels filled')


if __name__ == '__main__':
    for name in sys.argv[1:] or HOLES:
        patch(name)
