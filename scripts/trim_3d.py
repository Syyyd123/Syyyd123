"""Tidy the github-profile-3d-contrib output to fit the profile.

Removes the language pie (it only sees public repos, so it shows "Python")
and the activity radar (private work isn't counted as commits, so it sits
near zero), plus the star and fork counters. Swaps the font to the same
monospace as the other panels.

    python3 scripts/trim_3d.py profile-3d-contrib/profile-3d-sid.svg profile-3d.svg
"""
import re
import sys
import xml.etree.ElementTree as ET

from theme import MONO, TITLE_H, window

NS = "http://www.w3.org/2000/svg"
CROP_TOP = 100  # the generator leaves empty space above the grid
G = f"{{{NS}}}g"
ET.register_namespace("", NS)


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
                for k in kids[2:]:
                    child.remove(k)
                removed.append("stars/forks")
    # Crop the empty sky above the grid and frame it like the other panels
    w = int(float(root.get("width")))
    top, h = CROP_TOP, int(float(root.get("height"))) - CROP_TOP
    root.set("viewBox", f"0 {top} {w} {h}")
    root.set("x", "1"); root.set("y", str(TITLE_H + 1))
    root.set("width", str(w - 2)); root.set("height", str(h))
    inner = ET.tostring(root, encoding="unicode")
    open(dst, "w").write(window(w, TITLE_H + h + 8, "Contributions in 3D · last 12 months", inner))
    print("removed:", ", ".join(removed))


if __name__ == "__main__":
    trim(sys.argv[1], sys.argv[2])
