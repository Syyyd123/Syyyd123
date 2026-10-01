"""Turn the portrait into an animated ASCII SVG in a halftone style.

Run locally only when the photo changes:
    python3 scripts/make_ascii_svg.py

Inputs:  assets/portrait-source.png  (cropped photo)
         assets/portrait-mask.png    (subject mask, from scripts/mask.swift)
Output:  ascii-portrait.svg

Style: the subject prints in bright Paper glyphs, with highlights solid and
shadows left empty; the background becomes a faint dot halftone, so the
subject stands forward. Rows print top to bottom once, then hold.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

from theme import MUTED, PAPER, RUST_LIGHT, TITLE_H, window

ROOT = Path(__file__).resolve().parent.parent
# Head-and-shoulders crop of the source; rows follow from the glyph aspect
CROP = (60, 0, 760, 640)
COLS = 110
CHAR_W, LINE_H, FONT = 4.7, 8.7, 8.0
PAD_X, PAD_Y = 18, 16
ROWS = round(COLS * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0]) * CHAR_W / LINE_H)

# dark -> bright; leading spaces keep the deepest shadows empty
FG_RAMP = " .:-=+*#%@"
# background halftone: only a sparse dot grid, by brightness
BG_RAMP = "  ..::"


def load():
    img = Image.open(ROOT / "assets/portrait-source.png").convert("L")
    mask = Image.open(ROOT / "assets/portrait-mask.png").convert("L").resize(img.size)
    img, mask = img.crop(CROP), mask.crop(CROP)
    # Spread the subject's tones evenly so mid-tones (skin, suit) still get glyphs
    subject = ImageOps.equalize(img, mask=mask)
    size = (COLS, ROWS)
    return (subject.resize(size, Image.LANCZOS), img.resize(size, Image.LANCZOS),
            mask.resize(size, Image.LANCZOS))


def glyph_rows():
    subject, raw, mask = load()
    s, r, m = subject.load(), raw.load(), mask.load()
    rows = []
    for y in range(ROWS):
        fg, bg = [], []
        for x in range(COLS):
            if m[x, y] > 110:
                v = s[x, y] / 255
                fg.append(FG_RAMP[min(int(v * len(FG_RAMP)), len(FG_RAMP) - 1)])
                bg.append(" ")
            else:
                fg.append(" ")
                # halftone: dots only on a checker grid, denser where the photo is brighter
                v = r[x, y] / 255
                on_grid = (x + y) % 2 == 0
                bg.append(BG_RAMP[min(int(v * len(BG_RAMP)), len(BG_RAMP) - 1)] if on_grid else " ")
        rows.append(("".join(fg), "".join(bg)))
    return rows


def build():
    rows = glyph_rows()
    width = round(PAD_X * 2 + COLS * CHAR_W)
    height = round(TITLE_H + PAD_Y * 2 + ROWS * LINE_H)
    line_len = COLS * CHAR_W
    fg_lines, bg_lines = [], []
    for i, (fg, bg) in enumerate(rows):
        y = TITLE_H + PAD_Y + (i + 1) * LINE_H - 2.5
        delay = 0.25 + i * 0.035
        common = f'x="{PAD_X}" y="{y:.1f}" textLength="{line_len}" lengthAdjust="spacing" xml:space="preserve"'
        if bg.strip():
            bg_lines.append(f'<text class="bg" {common} style="animation-delay:{delay + 0.9:.2f}s">{escape(bg)}</text>')
        if fg.strip():
            fg_lines.append(f'<text class="fg" {common} style="animation-delay:{delay:.2f}s">{escape(fg)}</text>')
    # A block cursor that rides down the rows as they print, then blinks at the end
    total = 0.25 + ROWS * 0.035
    cursor_y0 = TITLE_H + PAD_Y
    cursor = (f'<rect class="cursor" x="{PAD_X}" y="{cursor_y0}" width="7" height="{LINE_H:.1f}" fill="{RUST_LIGHT}">'
              f'<animate attributeName="y" from="{cursor_y0}" to="{cursor_y0 + ROWS * LINE_H - LINE_H:.1f}" '
              f'begin="0.25s" dur="{total - 0.25:.2f}s" fill="freeze"/></rect>')
    style = f"""
  .fg {{ fill: {PAPER}; font-size: {FONT}px; opacity: 0; animation: print .35s ease-out forwards; }}
  .bg {{ fill: {MUTED}; font-size: {FONT}px; opacity: 0; animation: dim .8s ease-out forwards; }}
  .cursor {{ animation: blink 1s steps(1) {total:.2f}s infinite; }}
  @keyframes print {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes dim {{ from {{ opacity: 0; }} to {{ opacity: .38; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .fg, .bg {{ animation: none; opacity: 1; }} .bg {{ opacity: .38; }} }}"""
    if os.environ.get("STATIC"):  # frozen final frame, for local previews
        style += "\n  .fg, .bg, .cursor { animation: none !important; } .fg { opacity: 1; } .bg { opacity: .38; }"
        cursor = ""
    body = "\n".join(bg_lines + fg_lines + [cursor])
    svg = window(width, height, "Sid Prithvi", body, style)
    out = ROOT / ("ascii-portrait.static.svg" if os.environ.get("STATIC") else "ascii-portrait.svg")
    out.write_text(svg)
    print(f"ascii-portrait.svg  {width}x{height}  {COLS}x{ROWS} chars")


if __name__ == "__main__":
    build()
