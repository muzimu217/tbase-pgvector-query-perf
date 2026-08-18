#!/usr/bin/env python3
import csv
from pathlib import Path
from common import *

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/rescan_memory.csv").open()))
rescans = sorted({int(r["rescans"]) for r in rows})
variants = ["no_value_cleanup", "full_patch"]
colors = {"no_value_cleanup": "#8A9199", "full_patch": "#7F8F84"}
values = {v: [float(next(r["mean_peak_growth_kb"] for r in rows if int(r["rescans"]) == n and r["variant"] == v)) for n in rescans] for v in variants}
image, draw, body = canvas("Rescan lifecycle cleanup reduces peak RSS growth", "Mean peak RSS growth (KB)", 90000)
bar_w = 70
for i, variant in enumerate(variants):
    for j, value in enumerate(values[variant]):
        x = LEFT + (j + 0.5) * PLOT_W / len(rescans) + (i - 0.5) * bar_w
        y = sy(value, 90000)
        draw.rectangle((x - bar_w / 2, y, x + bar_w / 2, TOP + PLOT_H), fill=colors[variant]); label(draw, x, y - 18, f"{value:,.0f}", size=13)
        body.append(f'<rect x="{x - bar_w / 2:.1f}" y="{y:.1f}" width="{bar_w}" height="{TOP + PLOT_H - y:.1f}" fill="{colors[variant]}"/><text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="{TEXT}">{value:,.0f}</text>')
for j, n in enumerate(rescans):
    x = LEFT + (j + 0.5) * PLOT_W / len(rescans); label(draw, x, TOP + PLOT_H + 28, f"{n:,}")
    body.append(f'<text x="{x:.1f}" y="{TOP + PLOT_H + 34}" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" fill="{TEXT}">{n:,}</text>')
legend(draw, body, [("Without cleanup", colors["no_value_cleanup"]), ("Full patch", colors["full_patch"])])
finish(image, body, ROOT / "output/01_rescan_memory")
