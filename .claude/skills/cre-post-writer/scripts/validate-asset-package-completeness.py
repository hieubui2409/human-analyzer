#!/usr/bin/env python3
"""Check asset packages against the Rule-03 output manifest.

Rule 03 (docs/rules/03-content-creation-pipeline.md) defines the canonical package:
  1. post.md   — markdown source (source of truth)
  2. post.txt  — plain-text publish-ready version (must mirror post.md)
  3. prompt.txt — image-generation prompts (only when the package has visuals)
  4. images/   — generated images directory (only when visual)
  5. README.md — input parameters + clinical intent

Required = a post (post.md OR post.txt) + README.md. The post.md/post.txt pair is the
source-of-truth + publish form; a package with only one of them is reported as a sync gap
(deterministic gathering — not a hard verdict). Visual files stay optional.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.formatters import print_table, eprint

POST_FORMS = ["post.md", "post.txt"]          # at least one required; both = synced pair
RECOMMENDED = ["README.md"]                    # Rule-03 required metadata file
OPTIONAL = ["prompt.txt", "image-prompts.txt", "images"]  # visual-only
ASSETS = ROOT / "assets"


def check_package(pkg: Path) -> dict | None:
    files = {f.name for f in pkg.iterdir()}
    posts_present = [p for p in POST_FORMS if p in files]
    # Skip dirs that are clearly grouping folders (no post in any form, but hold sub-packages).
    has_subpackages = any(child.is_dir() and any(
        (child / pf).exists() for pf in POST_FORMS) for child in pkg.iterdir())
    if not posts_present and has_subpackages:
        return None
    missing_post = len(posts_present) == 0
    sync_gap = len(posts_present) == 1  # only one of post.md/post.txt → not a synced pair
    missing_recommended = [r for r in RECOMMENDED if r not in files]
    return {
        "package": pkg.name,
        "posts": posts_present,
        "missing_post": missing_post,
        "sync_gap": sync_gap,
        "missing_recommended": missing_recommended,
        "complete": not missing_post and not missing_recommended,
    }


def check_packages() -> list[dict]:
    results = []
    for platform_dir in sorted(ASSETS.iterdir()):
        if not platform_dir.is_dir():
            continue
        for pkg in sorted(platform_dir.iterdir()):
            if not pkg.is_dir():
                continue
            rec = check_package(pkg)
            if rec is None:
                # grouping folder → descend one level into sub-packages
                for sub in sorted(pkg.iterdir()):
                    if sub.is_dir():
                        sub_rec = check_package(sub)
                        if sub_rec:
                            sub_rec["package"] = f"{pkg.name}/{sub_rec['package']}"
                            sub_rec["platform"] = platform_dir.name
                            results.append(sub_rec)
                continue
            rec["platform"] = platform_dir.name
            results.append(rec)
    return results


def main():
    if not ASSETS.exists():
        eprint("[WARN] assets/ directory not found")
        return
    results = check_packages()
    complete = sum(1 for r in results if r["complete"])
    sync_gaps = sum(1 for r in results if r["sync_gap"])
    eprint(f"[OK] {len(results)} packages: {complete} complete, "
           f"{len(results)-complete} incomplete, {sync_gaps} post.md/post.txt sync gaps")
    rows = []
    for r in results:
        notes = []
        if r["missing_post"]:
            notes.append("NO POST")
        if r["sync_gap"]:
            notes.append(f"only {r['posts'][0]}")
        if r["missing_recommended"]:
            notes.append("missing " + ", ".join(r["missing_recommended"]))
        rows.append([r["platform"], r["package"], "Y" if r["complete"] else "N",
                     ", ".join(r["posts"]) or "-", "; ".join(notes) or "-"])
    print_table(["Platform", "Package", "Complete?", "Post(s)", "Notes"], rows)


if __name__ == "__main__":
    main()
