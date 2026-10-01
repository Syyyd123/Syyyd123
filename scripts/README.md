# Profile art scripts

| Script | When to run | Output |
| --- | --- | --- |
| `mask.swift` | New photo: `swiftc -O mask.swift -o mask && ./mask photo.png mask.png 0.5 0.4` (macOS 14+) | subject mask |
| `make_ascii_svg.py` | New photo (needs `assets/portrait-source.png` + `assets/portrait-mask.png`, kept local) | `ascii-portrait.svg` |
| `make_info_card.py` | Details change (edit `LINES`) | `info-card.svg` |
| `fetch_contributions.py` + `render_heatmap_svg.py` + `bump_readme_versions.py` | Daily, via GitHub Actions (run the last one after any SVG change) | `contrib-heatmap.svg`, cache-busted README links |

Add `STATIC=1` to any `make_`/`render_` script for a frozen preview frame (`*.static.svg`, git-ignored).
Requires Python 3 with Pillow for the portrait only; the daily job is stdlib-only.
