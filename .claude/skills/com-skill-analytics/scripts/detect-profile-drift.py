"""M4 — Profile drift detector (deterministic, fast post-edit gate).

GOLDEN RULE #4: deterministic gather only. A fast (<10s) regex/path gate over
profile markdown — NOT a semantic audit. Catches what static analysis can prove:
broken internal links (a `[x](./other.md)` whose target is missing), and timeline
date sanity (malformed or implausibly-future dates). It surfaces drift; psy:crossref
(LLM) does the deep semantic consistency pass. M4 = fast gate, crossref = thorough.

Two modes:
  --file <path>   targeted check on one just-edited file (used by the PostToolUse hook)
  --all           full scan across every profile file (manual)

Usage:
  detect-profile-drift.py [--file PATH | --all] [--character SLUG]
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
from platform_lib.markdown_parser import extract_links, extract_dates  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402
from platform_lib.paths import resolve_character  # noqa: E402

# Module-level, monkeypatchable in tests.
PROFILES = paths.PROFILES
# Future beyond this many days = likely a typo (profiles are retrospective).
FUTURE_DAYS_TOLERANCE = 365
_MD_LINK = re.compile(r".*\.md(#.*)?$")


def _is_internal_md(url: str) -> bool:
    url = url.strip()
    if url.startswith(("http://", "https://", "mailto:", "#")):
        return False
    return bool(_MD_LINK.match(url))


def broken_links(md_file: Path) -> list[dict]:
    """Relative .md links in md_file whose target file does not exist."""
    try:
        text = md_file.read_text(encoding="utf-8")
    except OSError:
        return []
    out = []
    for link in extract_links(text):
        url = link["url"].strip()
        if not _is_internal_md(url):
            continue
        target = (md_file.parent / url.split("#", 1)[0]).resolve()
        if not target.exists():
            out.append({"file": str(md_file), "link_text": link["text"], "url": url})
    return out


def _parse_date(raw: str) -> date | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%Y", "%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def implausible_dates(md_file: Path) -> list[dict]:
    """Dates parsed from a (timeline) file that fall implausibly in the future."""
    try:
        text = md_file.read_text(encoding="utf-8")
    except OSError:
        return []
    today = date.today()
    out = []
    for raw in extract_dates(text):
        d = _parse_date(raw)
        if d and (d - today).days > FUTURE_DAYS_TOLERANCE:
            out.append({"file": str(md_file), "date": raw,
                        "days_future": (d - today).days})
    return out


def _profile_md_files(character: str | None):
    root = PROFILES
    if not root.exists():
        return []
    # Resolve aliases (e.g. "hieu" → "character-a") so --character doesn't silently
    # point at a non-existent dir and scan nothing.
    chars = [root / resolve_character(character)] if character else [d for d in root.iterdir() if d.is_dir()]
    files = []
    for c in chars:
        if c.is_dir():
            files.extend(sorted(c.rglob("*.md")))
    return files


def check_file(md_file: Path) -> dict:
    md_file = Path(md_file)
    links = broken_links(md_file)
    dates = implausible_dates(md_file) if "/timeline/" in str(md_file).replace("\\", "/") else []
    return {"broken_links": links, "implausible_dates": dates}


def gather(file: str | None, character: str | None) -> dict:
    if file:
        files = [Path(file)]
    else:
        files = _profile_md_files(character)
    all_broken, all_dates = [], []
    for f in files:
        res = check_file(f)
        all_broken += res["broken_links"]
        all_dates += res["implausible_dates"]
    issues = len(all_broken) + len(all_dates)
    return {
        "files_checked": len(files),
        "broken_links": all_broken,
        "implausible_dates": all_dates,
        "issue_count": issues,
        "status": "GREEN" if issues == 0 else ("YELLOW" if issues <= 2 else "RED"),
    }


def render_md(data: dict) -> str:
    out = [f"# Profile Drift — {data['status']} "
           f"({data['files_checked']} file(s), {data['issue_count']} issue(s))\n"]
    if data["broken_links"]:
        rows = [[Path(b["file"]).name, b["link_text"][:30], b["url"]] for b in data["broken_links"]]
        out += ["## Broken internal links\n", markdown_table(["File", "Link text", "Target"], rows)]
    if data["implausible_dates"]:
        rows = [[Path(d["file"]).name, d["date"], f"+{d['days_future']}d"] for d in data["implausible_dates"]]
        out += ["\n## Implausible future dates\n", markdown_table(["File", "Date", "Future"], rows)]
    if data["issue_count"] == 0:
        out.append("_No deterministic drift detected._")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Profile drift detector (M4)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--file", help="check one file (post-edit)")
    g.add_argument("--all", action="store_true", help="scan all profile files")
    ap.add_argument("--character", help="restrict --all to one character slug")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    if not args.file and not args.all:
        args.all = True
    data = gather(args.file, args.character)
    print(json_output(data) if (args.json or args.format == "json") else render_md(data))
    return 1 if data["status"] == "RED" else 0


if __name__ == "__main__":
    sys.exit(main())
