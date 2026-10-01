"""Shared palette and terminal-window chrome for every SVG on the profile.

Colours come from sidprithvi.com: Void background, Paper text, Rust accent,
Sage secondary, Muted for labels.
"""
from xml.sax.saxutils import escape

VOID = "#1A1310"
PANEL = "#211813"
BORDER = "#3A2C26"
PAPER = "#F5F2EC"
MUTED = "#8A8378"
RUST = "#A63D28"
RUST_LIGHT = "#E0785E"
SAGE = "#9AA685"

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

TITLE_H = 30


def window(width, height, title, body, extra_style="", scale=1.0):
    """Wrap SVG body markup in a dark terminal window with a title bar.

    scale enlarges the chrome for SVGs that are drawn big and shown scaled down.
    """
    th, r, fs = TITLE_H * scale, 5 * scale, 11.5 * scale
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<style>
  text {{ font-family: {MONO}; }}
  {extra_style}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{VOID}" stroke="{BORDER}"/>
<path d="M0.5 {th} H{width - 0.5}" stroke="{BORDER}"/>
<circle cx="{18 * scale}" cy="{th / 2}" r="{r}" fill="{RUST}"/>
<circle cx="{35 * scale}" cy="{th / 2}" r="{r}" fill="{SAGE}"/>
<circle cx="{52 * scale}" cy="{th / 2}" r="{r}" fill="{MUTED}"/>
<text x="{width / 2}" y="{th / 2 + fs * 0.39:.1f}" text-anchor="middle" font-size="{fs}" fill="{MUTED}">{escape(title)}</text>
{body}
</svg>
"""
