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


def window(width, height, title, body, extra_style=""):
    """Wrap SVG body markup in a dark terminal window with a title bar."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<style>
  text {{ font-family: {MONO}; }}
  {extra_style}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{VOID}" stroke="{BORDER}"/>
<path d="M0.5 {TITLE_H} H{width - 0.5}" stroke="{BORDER}"/>
<circle cx="18" cy="15" r="5" fill="{RUST}"/>
<circle cx="35" cy="15" r="5" fill="{SAGE}"/>
<circle cx="52" cy="15" r="5" fill="{MUTED}"/>
<text x="{width / 2}" y="19.5" text-anchor="middle" font-size="11.5" fill="{MUTED}">{escape(title)}</text>
{body}
</svg>
"""
