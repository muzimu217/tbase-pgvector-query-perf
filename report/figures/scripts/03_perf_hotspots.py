#!/usr/bin/env python3
import csv
from pathlib import Path
from common import *

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/perf_hotspots.csv").open()))
groups = ["inner_product_total", "btfloat8fastcmp"]; names = ["Inner product total", "btfloat8fastcmp"]
colors = {"scalar": "#8A9199", "vectorized": "#7F8F84"}
image, draw, body = canvas("The inner-product hotspot shrinks after vectorization", "perf self-time share (%)", 40)
bar_w = 70
for i, build in enumerate(["scalar", "vectorized"]):
    for j, group in enumerate(groups):
        value = float(next(r["share_pct"] for r in rows if r["symbol_group"] == group and r["build"] == build)); x = LEFT + (j + 0.5) * PLOT_W / len(groups) + (i - 0.5) * bar_w; y = sy(value, 40)
        draw.rectangle((x - bar_w / 2, y, x + bar_w / 2, TOP + PLOT_H), fill=colors[build]); label(draw, x, y - 18, f"{value:.2f}%", size=14)
        body.append(f'<rect x="{x - bar_w / 2:.1f}" y="{y:.1f}" width="{bar_w}" height="{TOP + PLOT_H - y:.1f}" fill="{colors[build]}"/><text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{TEXT}">{value:.2f}%</text>')
for j, name in enumerate(names):
    x = LEFT + (j + 0.5) * PLOT_W / len(groups); label(draw, x, TOP + PLOT_H + 28, name, size=15); body.append(f'<text x="{x:.1f}" y="{TOP + PLOT_H + 34}" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" fill="{TEXT}">{name}</text>')
legend(draw, body, [("Scalar", colors["scalar"]), ("Vectorized", colors["vectorized"])])
finish(image, body, ROOT / "output/03_perf_hotspots")
