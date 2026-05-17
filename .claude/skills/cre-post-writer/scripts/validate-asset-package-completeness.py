#!/usr/bin/env python3
"""Check asset packages for required files (post.txt, image-prompts.txt, README.txt)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.formatters import print_table, eprint

REQUIRED = ["post.txt"]
OPTIONAL = ["image-prompts.txt", "README.txt", "images"]
ASSETS = ROOT / "assets"


def check_packages() -> list[dict]:
    results = []
    for platform_dir in sorted(ASSETS.iterdir()):
        if not platform_dir.is_dir():
            continue
        for pkg in sorted(platform_dir.iterdir()):
            if not pkg.is_dir():
                continue
            files = [f.name for f in pkg.iterdir()]
            missing_req = [r for r in REQUIRED if r not in files]
            missing_opt = [o for o in OPTIONAL if o not in files]
            results.append({
                "platform": platform_dir.name,
                "package": pkg.name,
                "files": files,
                "missing_required": missing_req,
                "missing_optional": missing_opt,
                "complete": len(missing_req) == 0,
            })
    return results


def main():
    if not ASSETS.exists():
        eprint("[WARN] assets/ directory not found")
        return
    results = check_packages()
    complete = sum(1 for r in results if r["complete"])
    eprint(f"[OK] {len(results)} packages: {complete} complete, {len(results)-complete} incomplete")
    rows = [[r["platform"], r["package"], "Y" if r["complete"] else "N",
             ", ".join(r["missing_required"]) or "-",
             ", ".join(r["missing_optional"]) or "-"]
            for r in results]
    print_table(["Platform", "Package", "Complete?", "Missing Req", "Missing Opt"], rows)


if __name__ == "__main__":
    main()
