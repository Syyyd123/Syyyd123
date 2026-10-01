"""Stamp each SVG link in README.md with ?v=<content hash>.

Browsers and GitHub cache README images, so a new heatmap can look stale.
Changing the URL whenever the file changes forces a fresh download.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
readme = ROOT / "README.md"
text = readme.read_text()


def stamp(m):
    name = m.group(1)
    digest = hashlib.sha1((ROOT / name).read_bytes()).hexdigest()[:8]
    return f'src="./{name}?v={digest}"'


new = re.sub(r'src="\./([\w.-]+\.svg)(?:\?v=\w+)?"', stamp, text)
if new != text:
    readme.write_text(new)
    print("README image versions updated")
else:
    print("README already current")
