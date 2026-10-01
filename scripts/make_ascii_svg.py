"""Turn the portrait into an animated ASCII SVG in a halftone style.

Run locally only when the photo changes:
    python3 scripts/make_ascii_svg.py

Inputs:  assets/portrait-source.png  (cropped photo)
         assets/portrait-mask.png    (subject mask, from scripts/mask.swift)
Output:  ascii-portrait.svg

Style: the subject prints in bright Paper glyphs, with highlights solid and
shadows left empty; the background becomes a faint dot halftone, so the
subject stands forward. Rows print top to bottom, then it keeps moving:
the halftone breathes, a rust light sweeps across, and a few rows glitch.
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


# Rows that glitch sideways now and then, with their loop length (s)
GLITCH_ROWS = {12: 7.3, 21: 9.1, 29: 6.7, 37: 11.3, 46: 8.2}


def build():
    """Print in once, then keep moving: breathing halftone, a rust light sweep, row glitches."""
    rows = glyph_rows()
    width = round(PAD_X * 2 + COLS * CHAR_W)
    height = round(TITLE_H + PAD_Y * 2 + ROWS * LINE_H)
    line_len = COLS * CHAR_W
    total = 0.25 + ROWS * 0.035  # when the last row has printed
    fg_lines, bg_lines = [], []
    for i, (fg, bg) in enumerate(rows):
        y = TITLE_H + PAD_Y + (i + 1) * LINE_H - 2.5
        delay = 0.25 + i * 0.035
        common = f'x="{PAD_X}" y="{y:.1f}" textLength="{line_len}" lengthAdjust="spacing" xml:space="preserve"'
        if bg.strip():
            # fade in, then breathe forever in a top-to-bottom wave
            bg_lines.append(f'<text class="bg" {common} style="animation-delay:{delay + 0.9:.2f}s,{total + 1 + i * 0.09:.2f}s">'
                            f'{escape(bg)}</text>')
        if fg.strip():
            if i in GLITCH_ROWS:
                fg_lines.append(f'<text class="fg gl" {common} style="animation-delay:{delay:.2f}s,{total + 2 + i * 0.05:.2f}s;'
                                f'animation-duration:.35s,{GLITCH_ROWS[i]}s">{escape(fg)}</text>')
            else:
                fg_lines.append(f'<text class="fg" {common} style="animation-delay:{delay:.2f}s">{escape(fg)}</text>')
    # A block cursor that rides down the rows as they print, then blinks at the end
    cursor_y0 = TITLE_H + PAD_Y
    cursor = (f'<rect class="cursor" x="{PAD_X}" y="{cursor_y0}" width="7" height="{LINE_H:.1f}" fill="{RUST_LIGHT}">'
              f'<animate attributeName="y" from="{cursor_y0}" to="{cursor_y0 + ROWS * LINE_H - LINE_H:.1f}" '
              f'begin="0.25s" dur="{total - 0.25:.2f}s" fill="freeze"/></rect>')
    # Diagonal rust light band that sweeps across the subject, then rests
    sweep = f'''<defs><linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{width}" y2="{height * 0.55:.0f}" gradientTransform="translate(-{width * 1.3:.0f} 0)">
  <stop offset="0" stop-color="{PAPER}"/><stop offset=".44" stop-color="{PAPER}"/>
  <stop offset=".5" stop-color="{RUST_LIGHT}"/><stop offset=".56" stop-color="{PAPER}"/><stop offset="1" stop-color="{PAPER}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-{width * 1.3:.0f} 0; {width * 1.3:.0f} 0; {width * 1.3:.0f} 0"
    keyTimes="0;.4;1" dur="7s" begin="{total + 0.6:.2f}s" repeatCount="indefinite"/>
</linearGradient></defs>'''
    style = f"""
  .fg {{ fill: url(#sheen); font-size: {FONT}px; opacity: 0; animation: print .35s ease-out forwards; }}
  .gl {{ animation-name: print, glitch; animation-timing-function: ease-out, steps(1); animation-iteration-count: 1, infinite; }}
  .bg {{ fill: {MUTED}; font-size: {FONT}px; opacity: 0;
         animation: dim .8s ease-out forwards, breathe 4.5s ease-in-out infinite alternate; }}
  .cursor {{ animation: blink 1s steps(1) {total:.2f}s infinite; }}
  @keyframes print {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes dim {{ from {{ opacity: 0; }} to {{ opacity: .38; }} }}
  @keyframes breathe {{ from {{ opacity: .38; }} to {{ opacity: .1; }} }}
  @keyframes glitch {{ 0%, 90% {{ transform: none; opacity: 1; }} 91% {{ transform: translateX(5px); opacity: .55; }}
                      92% {{ transform: translateX(-3px); opacity: 1; }} 93%, 100% {{ transform: none; opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .fg, .bg, .gl {{ animation: none; opacity: 1; }} .bg {{ opacity: .38; }} }}"""
    if os.environ.get("STATIC"):  # frozen final frame, for local previews
        style += "\n  .fg, .bg, .gl, .cursor { animation: none !important; } .fg { opacity: 1; fill: " + PAPER + "; } .bg { opacity: .38; }"
        cursor = sweep = ""
    body = "\n".join([sweep] + bg_lines + fg_lines + [cursor])
    svg = window(width, height, "Sid Prithvi", body, style)
    out = ROOT / ("ascii-portrait.static.svg" if os.environ.get("STATIC") else "ascii-portrait.svg")
    out.write_text(svg)
    print(f"{out.name}  {width}x{height}  {COLS}x{ROWS} chars")


if __name__ == "__main__":
    build()
