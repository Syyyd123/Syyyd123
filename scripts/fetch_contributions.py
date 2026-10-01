"""Fetch the public contribution calendar (no token) and write data/contributions.json.

GitHub serves the same calendar the profile page shows at
https://github.com/users/<user>/contributions. Private-repo work appears
there only when "Include private contributions on my profile" is turned on
in GitHub settings.
"""
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

USER = "Syyyd123"
ROOT = Path(__file__).resolve().parent.parent


def fetch():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "Mozilla/5.0 (profile-readme)"})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def parse(html):
    cells = {}
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        d = re.search(r'data-date="([\d-]+)"', td)
        cid = re.search(r'id="([^"]+)"', td)
        lvl = re.search(r'data-level="(\d)"', td)
        if d and cid:
            cells[cid.group(1)] = {"date": d.group(1), "level": int(lvl.group(1)) if lvl else 0, "count": 0}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*(\d[\d,]*) contribution", text)
        if cid in cells and m:
            cells[cid]["count"] = int(m.group(1).replace(",", ""))
    return sorted(cells.values(), key=lambda c: c["date"])


def stats(days):
    total = sum(d["count"] for d in days)
    longest = cur = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # current streak counts back from today (or yesterday, if today is still empty)
    for d in reversed(days):
        if d["count"]:
            cur += 1
        elif cur or d["date"] != date.today().isoformat():
            break
    best = max(days, key=lambda d: d["count"]) if days else None
    return {"total": total, "longest_streak": longest, "current_streak": cur,
            "best_day": best, "active_days": sum(1 for d in days if d["count"])}


def main():
    days = parse(fetch())
    if not days:
        raise SystemExit("No calendar cells found; GitHub may have changed the markup.")
    out = {"user": USER, "fetched": date.today().isoformat(), "days": days, "stats": stats(days)}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/contributions.json").write_text(json.dumps(out, indent=1))
    s = out["stats"]
    print(f"{len(days)} days, {s['total']} contributions, longest streak {s['longest_streak']}")


if __name__ == "__main__":
    main()
