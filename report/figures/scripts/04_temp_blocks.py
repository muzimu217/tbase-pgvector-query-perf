#!/usr/bin/env python3
import csv
from pathlib import Path
from common import *

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/query_work_mem.csv").open()))
variants = ["inherit_work_mem", "query_work_mem_64mb"]; labels = ["Inherited work_mem", "query_work_mem = 64 MB"]
read_vals = [int(next(r["temp_read_blocks"] for r in rows if r["variant"] == v)) for v in variants]; write_vals = [int(next(r["temp_written_blocks"] for r in rows if r["variant"] == v)) for v in variants]
image, draw, body = canvas("Query-specific memory removes temporary I/O", "Temporary blocks per workload", 80000)
bar_w = 62
for i, values in enumerate([read_vals, write_vals]):
    color = ["#8A9199", "#B7A99A"][i]
    for j, value in enumerate(values):
        x = LEFT + (j + 0.5) * PLOT_W / len(variants) + (i - 0.5) * bar_w; y = sy(value, 80000)
        draw.rectangle((x - bar_w / 2, y, x + bar_w / 2, TOP + PLOT_H), fill=color); label(draw, x, y - 18, f"{value:,}", size=14)
        body.append(f'<rect x="{x - bar_w / 2:.1f}" y="{y:.1f}" width="{bar_w}" height="{TOP + PLOT_H - y:.1f}" fill="{color}"/><text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{TEXT}">{value:,}</text>')
for j, text in enumerate(labels):
    x = LEFT + (j + 0.5) * PLOT_W / len(variants); label(draw, x, TOP + PLOT_H + 28, text, size=14); body.append(f'<text x="{x:.1f}" y="{TOP + PLOT_H + 34}" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="{TEXT}">{text}</text>')
legend(draw, body, [("Read blocks", "#8A9199"), ("Written blocks", "#B7A99A")])
finish(image, body, ROOT / "output/04_temp_blocks")
