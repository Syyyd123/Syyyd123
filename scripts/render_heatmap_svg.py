"""Render data/contributions.json as an animated contribution heatmap.

    python3 scripts/render_heatmap_svg.py          # animated -> contrib-heatmap.svg
    STATIC=1 python3 scripts/render_heatmap_svg.py # preview  -> contrib-heatmap.static.svg
"""
import json
import os
from datetime import date
from pathlib import Path

from theme import BORDER, MUTED, PAPER, RUST_LIGHT, TITLE_H, window

ROOT = Path(__file__).resolve().parent.parent
# empty -> busiest, in the site's rust
PALETTE = ["#2A201C", "#5C2A1E", "#83321F", "#B4452C", "#E0785E"]
CELL, GAP = 13, 3
STEP = CELL + GAP
LEFT, TOP, PAD = 52, TITLE_H + 34, 22
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def build():
    static = bool(os.environ.get("STATIC"))
    data = json.loads((ROOT / "data/contributions.json").read_text())
    days, st = data["days"], data["stats"]
    start = date.fromisoformat(days[0]["date"])
    start_row = (start.weekday() + 1) % 7  # GitHub rows start on Sunday
    weeks = (len(days) + start_row + 6) // 7
    width = LEFT + weeks * STEP + PAD
    height = TOP + 7 * STEP + 62
    parts = []
    # month labels where a new month starts in the first row of a column
    last = None
    for i, d in enumerate(days):
        dt = date.fromisoformat(d["date"])
        col = (i + start_row) // 7
        if dt.month != last and dt.day <= 7 and col < weeks - 1:
            parts.append(f'<text x="{LEFT + col * STEP}" y="{TOP - 10}" font-size="11" fill="{MUTED}">{MONTHS[dt.month - 1]}</text>')
            last = dt.month
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{PAD}" y="{TOP + r * STEP + 10}" font-size="11" fill="{MUTED}">{name}</text>')
    for i, d in enumerate(days):
        col, row = divmod(i + start_row, 7)
        delay = (col + row) * 0.018
        tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
        parts.append(f'<rect class="c" x="{LEFT + col * STEP}" y="{TOP + row * STEP}" width="{CELL}" height="{CELL}" rx="3" '
                     f'fill="{PALETTE[min(d["level"], 4)]}" style="animation-delay:{delay:.3f}s"><title>{tip}</title></rect>')
    fy = TOP + 7 * STEP + 30
    total = f'{st["total"]:,}'
    parts.append(f'<text x="{LEFT}" y="{fy}" font-size="12.5" fill="{PAPER}"><tspan fill="{RUST_LIGHT}" font-weight="700">{total}</tspan>'
                 f' contributions in the last year<tspan fill="{MUTED}">  ·  longest streak </tspan>{st["longest_streak"]} days'
                 f'<tspan fill="{MUTED}">  ·  current streak </tspan>{st["current_streak"]} days</text>')
    lx = width - PAD - 5 * STEP - 70
    parts.append(f'<text x="{lx}" y="{fy}" font-size="11" fill="{MUTED}">Less</text>')
    for j, c in enumerate(PALETTE):
        parts.append(f'<rect x="{lx + 34 + j * STEP}" y="{fy - 11}" width="{CELL}" height="{CELL}" rx="3" fill="{c}" stroke="{BORDER}"/>')
    parts.append(f'<text x="{lx + 40 + 5 * STEP}" y="{fy}" font-size="11" fill="{MUTED}">More</text>')
    parts.append(f'<text x="{LEFT}" y="{fy + 20}" font-size="10.5" fill="{MUTED}">updated {data["fetched"]} · includes private work</text>')
    style = """
  .c { transform-box: fill-box; transform-origin: center; opacity: 0; transform: scale(.3);
       animation: pop .35s cubic-bezier(.2,.8,.2,1) forwards; }
  @keyframes pop { to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) { .c { animation: none; opacity: 1; transform: none; } }"""
    if static:
        style += "\n  .c { animation: none !important; opacity: 1; transform: none; }"
    svg = window(width, height, "sid@sydney: ~ $ ./contributions.sh", "\n".join(parts), style)
    out = ROOT / ("contrib-heatmap.static.svg" if static else "contrib-heatmap.svg")
    out.write_text(svg)
    print(f"{out.name}  {width}x{height}  {weeks} weeks, {st['total']} contributions")


if __name__ == "__main__":
    build()
