#!/usr/bin/env python3
import csv
from pathlib import Path
from common import *

ROOT = Path(__file__).resolve().parents[1]
records = list(csv.DictReader((ROOT / "data/simd_matrix.csv").open()))
by_rep = {}
for row in records:
    by_rep.setdefault(int(row["rep"]), {})[row["variant"]] = float(row["execution_time_ms"])
image, draw, body = canvas("Every paired run is faster after restoring auto-vectorization", "200-query workload (ms)", 24000)
for rep in sorted(by_rep):
    scalar, vectorized = by_rep[rep]["scalar"], by_rep[rep]["vectorized"]
    x1, x2 = LEFT + 160, LEFT + PLOT_W - 160; y1, y2 = sy(scalar, 24000), sy(vectorized, 24000)
    gain = (scalar - vectorized) / scalar * 100
    label_y = y2 + (rep - 3) * 18
    draw.line((x1, y1, x2, y2), fill="#8A9199", width=4); draw.ellipse((x1 - 7, y1 - 7, x1 + 7, y1 + 7), fill="#8A9199"); draw.ellipse((x2 - 7, y2 - 7, x2 + 7, y2 + 7), fill="#7F8F84"); label(draw, x2 + 55, label_y, f"-{gain:.1f}%", color="#5F6D62", size=14)
    body.append(f'<line x1="{x1}" y1="{y1:.1f}" x2="{x2}" y2="{y2:.1f}" stroke="#8A9199" stroke-width="4"/><circle cx="{x1}" cy="{y1:.1f}" r="7" fill="#8A9199"/><circle cx="{x2}" cy="{y2:.1f}" r="7" fill="#7F8F84"/><text x="{x2 + 28}" y="{label_y + 5:.1f}" font-family="Arial,sans-serif" font-size="14" fill="#5F6D62">-{gain:.1f}%</text>')
label(draw, LEFT + 160, TOP + PLOT_H + 30, "Scalar", size=17); label(draw, LEFT + PLOT_W - 160, TOP + PLOT_H + 30, "Compiler-vectorized", size=17)
body += [f'<text x="{LEFT + 160}" y="{TOP + PLOT_H + 36}" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" fill="{TEXT}">Scalar</text>', f'<text x="{LEFT + PLOT_W - 160}" y="{TOP + PLOT_H + 36}" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" fill="{TEXT}">Compiler-vectorized</text>']
finish(image, body, ROOT / "output/02_simd_pairs")
