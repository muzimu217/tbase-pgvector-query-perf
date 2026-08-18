from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

W, H = 1100, 560
LEFT, RIGHT, TOP, BOTTOM = 120, 70, 70, 100
PLOT_W, PLOT_H = W - LEFT - RIGHT, H - TOP - BOTTOM
BG, GRID, TEXT = "#FFFFFF", "#D8D1C7", "#27302C"

def font(size):
    for path in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def sy(value, ymax):
    return TOP + PLOT_H - PLOT_H * value / ymax

def canvas(title, ylabel, ymax, ticks=5):
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.text((LEFT, 20), title, fill=TEXT, font=font(26))
    for i in range(ticks + 1):
        value = ymax * i / ticks
        y = sy(value, ymax)
        draw.line((LEFT, y, LEFT + PLOT_W, y), fill=GRID, width=1)
        draw.text((LEFT - 78, y - 9), f"{value:,.0f}", fill=TEXT, font=font(15))
    draw.line((LEFT, TOP, LEFT, TOP + PLOT_H), fill=TEXT, width=2)
    draw.line((LEFT, TOP + PLOT_H, LEFT + PLOT_W, TOP + PLOT_H), fill=TEXT, width=2)
    draw.text((25, TOP + PLOT_H // 2), ylabel, fill=TEXT, font=font(18))
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="#FFFFFF"/>', f'<text x="{LEFT}" y="42" font-family="Arial,sans-serif" font-size="26" fill="{TEXT}">{escape(title)}</text>', f'<text x="25" y="{TOP + PLOT_H // 2}" transform="rotate(-90 25 {TOP + PLOT_H // 2})" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" fill="{TEXT}">{escape(ylabel)}</text>']
    for i in range(ticks + 1):
        value = ymax * i / ticks
        y = sy(value, ymax)
        body += [f'<line x1="{LEFT}" y1="{y:.1f}" x2="{LEFT + PLOT_W}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>', f'<text x="{LEFT - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="Arial,sans-serif" font-size="15" fill="{TEXT}">{value:,.0f}</text>']
    body += [f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{TOP + PLOT_H}" stroke="{TEXT}" stroke-width="2"/>', f'<line x1="{LEFT}" y1="{TOP + PLOT_H}" x2="{LEFT + PLOT_W}" y2="{TOP + PLOT_H}" stroke="{TEXT}" stroke-width="2"/>']
    return image, draw, body

def label(draw, x, y, text, color=TEXT, size=15):
    f = font(size)
    box = draw.textbbox((0, 0), text, font=f)
    draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, fill=color, font=f)

def finish(image, body, output_stem):
    out = Path(output_stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out.with_suffix(".png"), dpi=(180, 180))
    body.append("</svg>")
    out.with_suffix(".svg").write_text("\n".join(body), encoding="utf-8")

def legend(draw, body, items):
    for i, (name, color) in enumerate(items):
        x = LEFT + i * 220
        draw.rectangle((x, H - 45, x + 18, H - 27), fill=color)
        label(draw, x + 90, H - 36, name, size=15)
        body.append(f'<rect x="{x}" y="{H - 45}" width="18" height="18" fill="{color}"/><text x="{x + 28}" y="{H - 30}" font-family="Arial,sans-serif" font-size="15" fill="{TEXT}">{escape(name)}</text>')
