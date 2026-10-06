"""Tile same-sized RGBA frames into one PNG over white: contact_sheet.py OUT COLS FRAME..."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import png  # noqa: E402

out, cols, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
frames = [png.read(p) for p in paths]
w, h = frames[0][0], frames[0][1]
rows = (len(frames) + cols - 1) // cols
gap = 4
W, H = cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap
sheet = [[[205, 205, 210, 255] for _ in range(W)] for _ in range(H)]
for i, (_, _, px) in enumerate(frames):
    ox, oy = (i % cols) * (w + gap), (i // cols) * (h + gap)
    for y in range(h):
        row, srow = sheet[oy + y], px[y]
        for x in range(w):
            r, g, b, a = srow[x]
            row[ox + x] = [(r * a + 255 * (255 - a)) // 255, (g * a + 255 * (255 - a)) // 255,
                           (b * a + 255 * (255 - a)) // 255, 255]
png.write(out, W, H, sheet)
