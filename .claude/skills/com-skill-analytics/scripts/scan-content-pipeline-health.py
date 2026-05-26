"""M5 — Content pipeline health: posts per platform from assets/ (deterministic).

GOLDEN RULE #4: deterministic gather only. Scans assets/{platform}/{YYMMDD-slug}/
package dirs, counts posts per platform, derives last-post date, posting frequency
(posts ÷ months spanned) and days-since-last-post. Flags INACTIVE platforms (zero
posts). It surfaces cadence; the LLM decides what to publish next. READ-ONLY.

Usage:
  scan-content-pipeline-health.py [--platform NAME] [--since YYYY-MM-DD]
                                  [--json] [--format md|json]
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402

ASSETS_DIR = paths.ASSETS  # module-level, monkeypatchable in tests
# Known target platforms — show even at zero posts so gaps stay visible.
EXPECTED_PLATFORMS = ["facebook", "blog", "linkedin", "instagram", "tiktok", "youtube", "twitter"]
PKG_DATE = re.compile(r"^(\d{6})-")  # YYMMDD prefix of an asset package dir


def _parse_pkg_date(name: str) -> date | None:
    m = PKG_DATE.match(name)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%y%m%d").date()
    except ValueError:
        return None


def _months_span(first: date, last: date) -> float:
    months = (last.year - first.year) * 12 + (last.month - first.month) + 1
    return max(months, 1)


def gather(platform_filter: str | None, since: date | None) -> dict:
    assets = ASSETS_DIR
    discovered = set()
    if assets.exists():
        discovered = {d.name for d in assets.iterdir() if d.is_dir()}
    platforms = sorted(set(EXPECTED_PLATFORMS) | discovered)
    if platform_filter:
        platforms = [p for p in platforms if p == platform_filter]

    today = date.today()
    rows = []
    for p in platforms:
        pdir = assets / p
        dates = []
        if pdir.exists():
            for d in pdir.iterdir():
                if not d.is_dir():
                    continue
                dt = _parse_pkg_date(d.name)
                if dt and (since is None or dt >= since):
                    dates.append(dt)
        dates.sort()
        count = len(dates)
        last = dates[-1] if dates else None
        if count >= 2:
            freq = round(count / _months_span(dates[0], dates[-1]), 1)
            freq_label = f"~{freq}/month"
        elif count == 1:
            freq_label = "<1/month"
        else:
            freq_label = "INACTIVE"
        rows.append({
            "platform": p,
            "posts": count,
            "last_post": last.isoformat() if last else "never",
            "days_since": (today - last).days if last else None,
            "frequency": freq_label,
        })
    rows.sort(key=lambda r: -r["posts"])
    return {
        "total_posts": sum(r["posts"] for r in rows),
        "active_platforms": len([r for r in rows if r["posts"]]),
        "inactive": [r["platform"] for r in rows if r["posts"] == 0],
        "rows": rows,
    }


def render_md(data: dict) -> str:
    rows = [[r["platform"], str(r["posts"]), r["last_post"],
             "—" if r["days_since"] is None else str(r["days_since"]), r["frequency"]]
            for r in data["rows"]]
    return "\n".join([
        f"# Content Pipeline ({data['total_posts']} posts, "
        f"{data['active_platforms']} active platforms)\n",
        markdown_table(["Platform", "Posts", "Last Post", "Days Ago", "Frequency"], rows),
        f"\n**Inactive platforms:** {', '.join(data['inactive']) or '(none)'}",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description="Content pipeline health (M5)")
    ap.add_argument("--platform", help="restrict to one platform")
    ap.add_argument("--since", help="only count posts on/after YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    since = None
    if args.since:
        try:
            since = datetime.strptime(args.since, "%Y-%m-%d").date()
        except ValueError:
            print(f"error: --since must be YYYY-MM-DD, got {args.since!r}", file=sys.stderr)
            return 2
    data = gather(args.platform, since)
    if args.json or args.format == "json":
        print(json_output(data))
    else:
        print(render_md(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
