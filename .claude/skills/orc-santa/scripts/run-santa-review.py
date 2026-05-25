#!/usr/bin/env python3
"""Deterministic pre-check report for Santa Method dual-review gate."""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.markdown_parser import extract_frontmatter
from platform_lib.formatters import print_json


FRAMEWORKS = ("psy", "cre", "gro", "mat")
SCOPES = ("full", "changes", "ref")


def get_target_files(target: Path, scope: str, framework: str) -> list[dict]:
    """Collect files based on scope mode."""
    if scope == "full":
        return _inventory_dir(target)
    elif scope == "changes":
        return _git_changed_files(target)
    elif scope == "ref":
        changed = _git_changed_files(target)
        changed_paths = {f["path"] for f in changed}
        cross_refs = _find_cross_refs(target, changed_paths)
        for ref in cross_refs:
            if ref["path"] not in changed_paths:
                ref["source"] = "cross-ref"
                changed.append(ref)
        return changed
    return []


def _inventory_dir(target: Path) -> list[dict]:
    """List all .md files in target directory."""
    if target.is_file():
        return [_file_info(target)]
    if not target.is_dir():
        return []
    results = []
    for f in sorted(target.rglob("*.md")):
        results.append(_file_info(f))
    return results


def _file_info(f: Path) -> dict:
    """Build file info dict."""
    try:
        content = f.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        content = ""
    lines = content.splitlines()
    words = len(content.split())
    return {
        "path": str(f.relative_to(ROOT)),
        "name": f.name,
        "lines": len(lines),
        "words": words,
        "source": "inventory",
    }


def _git_changed_files(target: Path) -> list[dict]:
    """Get git-changed files filtered to target path."""
    rel_target = str(target.relative_to(ROOT))
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", rel_target],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10,
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--", rel_target],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10,
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", rel_target],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10,
        )
        paths = set()
        for r in (result, staged, untracked):
            if r.returncode == 0:
                paths.update(p.strip() for p in r.stdout.strip().splitlines() if p.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return _inventory_dir(target)

    results = []
    for p in sorted(paths):
        fp = ROOT / p
        if fp.exists() and fp.suffix == ".md":
            info = _file_info(fp)
            info["source"] = "git-changed"
            results.append(info)
    return results


def _find_cross_refs(target: Path, changed_paths: set[str]) -> list[dict]:
    """Find files that reference any of the changed files."""
    refs = []
    seen = set()
    for changed in changed_paths:
        name = Path(changed).stem
        try:
            result = subprocess.run(
                ["grep", "-rl", "--include=*.md", name, str(ROOT / "docs")],
                capture_output=True, text=True, cwd=str(ROOT), timeout=15,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().splitlines():
                    fp = Path(line.strip())
                    rel = str(fp.relative_to(ROOT))
                    if rel not in changed_paths and rel not in seen and fp.exists():
                        seen.add(rel)
                        refs.append(_file_info(fp))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return refs


def validate_schema(files: list[dict]) -> dict:
    """Check frontmatter presence in each file."""
    valid = 0
    invalid = []
    for f in files:
        fp = ROOT / f["path"]
        if not fp.exists():
            continue
        fm = extract_frontmatter(fp)
        if fm:
            valid += 1
        else:
            invalid.append(f["path"])
    return {"valid_count": valid, "invalid_files": invalid, "total": len(files)}


def validate_dates(files: list[dict]) -> list[dict]:
    """Check ISO date format in timeline files."""
    import re
    iso_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    issues = []
    for f in files:
        if "timeline" not in f["path"]:
            continue
        fp = ROOT / f["path"]
        if not fp.exists():
            continue
        try:
            content = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        date_like = re.findall(r"\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}", content)
        non_iso = [d for d in date_like if not iso_pattern.fullmatch(d)]
        if non_iso:
            issues.append({"path": f["path"], "non_iso_dates": non_iso[:5]})
    return issues


def build_report(target: Path, framework: str, scope: str, round_num: int) -> dict:
    """Build complete pre-check report."""
    files = get_target_files(target, scope, framework)
    schema = validate_schema(files)
    date_issues = validate_dates(files)
    word_counts = {f["path"]: f["words"] for f in files}

    return {
        "target": str(target.relative_to(ROOT)),
        "framework": framework,
        "scope": scope,
        "round": round_num,
        "file_count": len(files),
        "files": files,
        "schema_validation": schema,
        "word_counts": word_counts,
        "date_issues": date_issues,
        "total_words": sum(word_counts.values()),
        "total_lines": sum(f["lines"] for f in files),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Santa Method pre-check: deterministic file analysis for dual-review gate"
    )
    parser.add_argument("--target", required=True, help="Target file or directory to review")
    parser.add_argument("--framework", required=True, choices=FRAMEWORKS, help="Domain framework")
    parser.add_argument("--scope", default="ref", choices=SCOPES,
                        help="Scope mode: full (all files), changes (git diff), ref (changes + cross-refs, default)")
    parser.add_argument("--round", type=int, default=1, choices=[1, 2],
                        help="Review round (1 or 2). Max 2 rounds. Escalate to user after round 2.")
    parser.add_argument("--json", action="store_true", default=True, help="Output as JSON (default)")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_absolute():
        target = ROOT / target

    if not target.exists():
        print(json.dumps({"error": f"Target not found: {args.target}"}), file=sys.stderr)
        sys.exit(1)

    report = build_report(target, args.framework, args.scope, args.round)
    print_json(report)


if __name__ == "__main__":
    main()
