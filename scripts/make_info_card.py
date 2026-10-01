"""Neofetch-style info card that prints line by line.

Edit LINES when your details change, then:
    python3 scripts/make_info_card.py          # animated  -> info-card.svg
    STATIC=1 python3 scripts/make_info_card.py # preview   -> info-card.static.svg
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

from theme import BORDER, MUTED, PAPER, RUST, RUST_LIGHT, SAGE, TITLE_H, window

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 553, 532  # same box as the portrait so the two sit level
PAD_X, TOP = 22, TITLE_H + 30
LINE_H, FONT, KEY_W = 28.5, 13, 88

HEADER = ("sid", "sydney")
# (key, value); an empty key continues the line above
LINES = [
    ("Role", "Business Analyst · Product Owner"),
    ("Base", "Sydney, Australia · full working rights"),
    ("Now", "Cognisian · Caresa eye-care clinical system"),
    ("Shipped", "Caresa in under 1 year (legacy took 10)"),
    ("Scale", "77,000 patients on Caresa"),
    ("Built", "Caresa patient app · iOS + Android"),
    ("Founder", "Ringa · AI voice receptionist"),
    ("", "UpBand · IELTS writing app"),
    ("Prev", "Lollypop Design Studio · edvin.ai"),
    ("Growth", "edvin.ai: 0 → 100K+ users in 9 months"),
    ("AI", "Claude Code · Codex · ChatGPT · Muse Spark"),
    ("Tools", "Figma · Power BI · GitHub"),
    ("Web", "sidprithvi.com"),
]
SWATCHES = ["#1A1310", RUST, RUST_LIGHT, SAGE, MUTED, "#D8CFC2", PAPER]


def build():
    static = bool(os.environ.get("STATIC"))
    rows = []
    user, host = HEADER
    y = TOP
    rows.append(f'<text class="ln" x="{PAD_X}" y="{y}" font-size="{FONT + 1}" style="animation-delay:.2s">'
                f'<tspan fill="{RUST_LIGHT}" font-weight="700">{user}</tspan><tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{RUST_LIGHT}" font-weight="700">{host}</tspan></text>')
    y += 10
    rows.append(f'<path class="ln" d="M{PAD_X} {y} H{PAD_X + 112}" stroke="{BORDER}" stroke-width="1.5" style="animation-delay:.3s"/>')
    y += LINE_H + 2
    for i, (k, v) in enumerate(LINES):
        delay = 0.45 + i * 0.12
        key = f'<tspan fill="{RUST_LIGHT}" font-weight="700">{escape(k)}</tspan>' if k else ""
        rows.append(f'<text class="ln" x="{PAD_X}" y="{y:.1f}" font-size="{FONT}" style="animation-delay:{delay:.2f}s">{key}'
                    f'<tspan x="{PAD_X + KEY_W}" fill="{PAPER}">{escape(v)}</tspan></text>')
        y += LINE_H
    y += 8
    delay = 0.45 + len(LINES) * 0.12
    for j, c in enumerate(SWATCHES):
        rows.append(f'<rect class="ln" x="{PAD_X + j * 30}" y="{y:.1f}" width="26" height="14" rx="2" fill="{c}" '
                    f'stroke="{BORDER}" style="animation-delay:{delay + j * 0.05:.2f}s"/>')
    style = """
  .ln { opacity: 0; transform: translateX(-6px); animation: in .45s ease-out forwards; }
  @keyframes in { to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) { .ln { animation: none; opacity: 1; transform: none; } }"""
    if static:
        style += "\n  .ln { animation: none !important; opacity: 1; transform: none; }"
    svg = window(WIDTH, HEIGHT, "sid@sydney: ~ $ neofetch", "\n".join(rows), style)
    out = ROOT / ("info-card.static.svg" if static else "info-card.svg")
    out.write_text(svg)
    print(f"{out.name}  {WIDTH}x{HEIGHT}, last line at y={y:.0f}")


if __name__ == "__main__":
    build()
