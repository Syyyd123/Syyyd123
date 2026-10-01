"""Tidy the github-profile-3d-contrib output to fit the profile.

Removes the language pie (it only sees public repos, so it shows "Python")
and the activity radar (private work isn't counted as commits, so it sits
near zero), plus the star and fork counters, and puts the same stats line and
Less/More legend as the flat heatmap in their place. Swaps the font to the same
monospace as the other panels.

    python3 scripts/trim_3d.py profile-3d-contrib/profile-3d-sid.svg profile-3d.svg
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from theme import MONO, TITLE_H, window

NS = "http://www.w3.org/2000/svg"
CROP_TOP = 100  # the generator leaves empty space above the grid
ROOT = Path(__file__).resolve().parent.parent
SCALE = 1280 / 860  # drawn at 1280 wide, shown at 860, so enlarge the chrome to match
G = f"{{{NS}}}g"
ET.register_namespace("", NS)


def days_label(n):
    return f"{n} day" if n == 1 else f"{n} days"


def sub(parent, tag, text=None, **attrs):
    el = ET.SubElement(parent, f"{{{NS}}}{tag}", {k.replace("_", "-"): str(v) for k, v in attrs.items()})
    if text is not None:
        el.text = text
    return el


def add_stats(group, width):
    """Same numbers and legend as the flat heatmap, in the generator's coordinates."""
    st = json.loads((ROOT / "data/contributions.json").read_text())["stats"]
    colors = json.loads((ROOT / "profile-3d/settings.json").read_text())["contribColors"]
    x, y = 60, 796
    t = sub(group, "text", x=x, y=y, style="font-size: 26px")
    sub(t, "tspan", f"{st['total']:,}", **{"class": "fill-strong", "style": "font-weight: bold; font-size: 34px"})
    sub(t, "tspan", " contributions in the last year", **{"class": "fill-fg"})
    t2 = sub(group, "text", x=x, y=y + 34, style="font-size: 20px")
    sub(t2, "tspan", "longest streak ", **{"class": "fill-weak"})
    sub(t2, "tspan", days_label(st["longest_streak"]), **{"class": "fill-fg"})
    sub(t2, "tspan", "  ·  current streak ", **{"class": "fill-weak"})
    sub(t2, "tspan", days_label(st["current_streak"]), **{"class": "fill-fg"})
    # top row: provenance on the left, Less/More legend on the right
    ty = CROP_TOP + 40
    sub(group, "text", "updated daily · includes private work", x=x, y=ty, style="font-size: 17px", **{"class": "fill-weak"})
    lx = width - 60 - 5 * 26 - 110
    sub(group, "text", "Less", x=lx, y=ty, style="font-size: 17px", **{"class": "fill-weak"})
    for j, c in enumerate(colors):
        sub(group, "rect", x=lx + 52 + j * 26, y=ty - 17, width=20, height=20, rx=4, fill=c, stroke="#3A2C26")
    sub(group, "text", "More", x=lx + 58 + 5 * 26, y=ty, style="font-size: 17px", **{"class": "fill-weak"})


def trim(src, dst):
    tree = ET.parse(src)
    root = tree.getroot()
    removed = []
    for child in list(root):
        if child.tag == f"{{{NS}}}style":
            child.text = re.sub(r"font-family:[^;}]*", f"font-family: {MONO}", child.text)
        if child.tag != G:
            continue
        classes = {el.get("class") for el in child.iter()}
        if "radar" in classes or "axis" in classes:
            root.remove(child)
            removed.append("radar")
        elif re.match(r"translate\(40,", child.get("transform", "")):
            root.remove(child)
            removed.append("pie")
        else:
            # footer: keep the contributions number + label, drop star/fork icons and counts
            kids = list(child)
            if len(kids) >= 4 and all(k.tag == f"{{{NS}}}text" for k in kids[:2]) and any(k.tag == G for k in kids[2:]):
                for k in kids:
                    child.remove(k)
                removed.append("footer")
                add_stats(child, int(float(root.get("width"))))
    # Crop the empty sky above the grid and frame it like the other panels
    w = int(float(root.get("width")))
    top, h = CROP_TOP, int(float(root.get("height"))) - CROP_TOP
    root.set("viewBox", f"0 {top} {w} {h}")
    th = TITLE_H * SCALE
    root.set("x", "1"); root.set("y", str(th + 1))
    root.set("width", str(w - 2)); root.set("height", str(h))
    inner = ET.tostring(root, encoding="unicode")
    open(dst, "w").write(window(w, round(th + h + 8), "Contributions in 3D · last 12 months", inner, scale=SCALE))
    print("removed:", ", ".join(removed))


if __name__ == "__main__":
    trim(sys.argv[1], sys.argv[2])
