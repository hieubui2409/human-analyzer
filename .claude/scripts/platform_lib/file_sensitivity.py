"""File sensitivity classification for human-analyzer profile protection.

Reads sensitivity-config.json and classifies files by sensitivity level
(CRITICAL/HIGH/MEDIUM/LOW/NONE). Used by validation scripts and CLI.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from platform_lib.paths import ROOT, ALL_CHARS, PROFILE_FILES

CONFIG_PATH = Path(__file__).parent / "sensitivity-config.json"

_config_cache = None


def load_config():
    global _config_cache
    if _config_cache is None:
        _config_cache = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return _config_cache


def classify_file(file_path):
    """Classify a file path by sensitivity level.

    Returns dict with keys: level, zone, checks, pattern_matched.
    """
    config = load_config()
    rel = str(file_path).replace("\\", "/")
    if ROOT and str(ROOT) != ".":
        rel = rel.replace(str(ROOT).replace("\\", "/") + "/", "")
    rel = rel.lstrip("./")

    for zone in config["zones"]:
        if zone["pattern"] in rel:
            return {
                "level": zone["level"],
                "zone": zone["zone"],
                "checks": zone["checks"],
                "pattern_matched": zone["pattern"],
            }

    defaults = config.get("defaults", {})
    for prefix, level in defaults.items():
        if prefix == "fallback":
            continue
        if prefix in rel:
            return {
                "level": level,
                "zone": "default",
                "checks": [],
                "pattern_matched": prefix,
            }

    return {
        "level": defaults.get("fallback", "NONE"),
        "zone": "none",
        "checks": [],
        "pattern_matched": None,
    }


def classify_all_profiles():
    """Classify all 75 base profile files (25 per character)."""
    results = []
    for char in ALL_CHARS:
        for pf in PROFILE_FILES:
            fp = f"docs/profiles/{char}/{pf}"
            info = classify_file(fp)
            info["path"] = fp
            results.append(info)
    return results


LEVEL_COLORS = {
    "CRITICAL": "\033[91m",
    "HIGH": "\033[93m",
    "MEDIUM": "\033[33m",
    "LOW": "\033[32m",
    "NONE": "\033[90m",
}
RESET = "\033[0m"


def main():
    parser = argparse.ArgumentParser(description="File sensitivity classifier")
    parser.add_argument("--path", help="Classify a single file path")
    parser.add_argument("--all", action="store_true", help="Classify all profile files")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.path:
        result = classify_file(args.path)
        if args.json:
            result["path"] = args.path
            print(json.dumps(result, indent=2))
        else:
            use_color = sys.stdout.isatty()
            c = LEVEL_COLORS.get(result["level"], "") if use_color else ""
            r = RESET if use_color else ""
            print(f"{c}{result['level']:8s}{r}  {result['zone']:16s}  {args.path}")
    elif args.all:
        results = classify_all_profiles()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            use_color = sys.stdout.isatty()
            for item in sorted(results, key=lambda x: ("CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE").index(x["level"])):
                c = LEVEL_COLORS.get(item["level"], "") if use_color else ""
                r = RESET if use_color else ""
                print(f"{c}{item['level']:8s}{r}  {item['zone']:16s}  {item['path']}")
            counts = {}
            for item in results:
                counts[item["level"]] = counts.get(item["level"], 0) + 1
            print(f"\nTotal: {len(results)} files — " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
