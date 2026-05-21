"""Detect domain state changes from git diff for mpc:session-state event routing."""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ROOT

DOMAIN_RULES = {
    "docs/materials/": {"event": "MAT.integrated", "domain": "MAT"},
    "docs/profiles/": {"event": "PSY.refresh", "domain": "PSY"},
    "docs/references/": {"event": "PSY.refresh", "domain": "PSY"},
    "docs/graph/": {"event": "PSY.refresh", "domain": "PSY"},
    "assets/": {"event": "CRE.recalibrate", "domain": "CRE"},
    "docs/rules/": {"event": "COM.rules_updated", "domain": "COM"},
    ".claude/skills/": {"event": "MPC.skill_updated", "domain": "MPC"},
    ".claude/scripts/": {"event": "MPC.script_updated", "domain": "MPC"},
}

IGNORE_PATTERNS = [
    "plans/", ".claude/session-state/", ".claude/profile-cache/",
    ".claude/teams/", ".claude/tasks/", "node_modules/",
]


def get_changed_files(ref: str = "HEAD~1", staged: bool = False) -> list[str]:
    """Get list of changed files from git diff."""
    try:
        if staged:
            cmd = ["git", "diff", "--cached", "--name-only"]
        else:
            cmd = ["git", "diff", "--name-only", ref]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().splitlines() if f]
    except (OSError, subprocess.SubprocessError):
        return []


def classify_changes(files: list[str]) -> list[dict]:
    """Classify changed files into domain events."""
    events = []
    seen_events = set()

    for filepath in files:
        if any(filepath.startswith(ignore) for ignore in IGNORE_PATTERNS):
            continue

        for prefix, info in DOMAIN_RULES.items():
            if filepath.startswith(prefix):
                event_key = f"{info['event']}:{prefix}"
                if event_key not in seen_events:
                    seen_events.add(event_key)
                    events.append({
                        "event": info["event"],
                        "domain": info["domain"],
                        "trigger_prefix": prefix,
                        "trigger_files": [],
                        "timestamp": datetime.now().isoformat(timespec="seconds"),
                    })

                for evt in events:
                    if evt["event"] == info["event"] and evt["trigger_prefix"] == prefix:
                        evt["trigger_files"].append(filepath)
                break

    return events


def main():
    parser = argparse.ArgumentParser(description="Detect domain state changes from git diff")
    parser.add_argument("--ref", default="HEAD~1", help="Git ref to diff against (default: HEAD~1)")
    parser.add_argument("--staged", action="store_true", help="Check staged changes instead")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    files = get_changed_files(args.ref, args.staged)
    events = classify_changes(files)

    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return

    print(f"\n  Git diff: {'--cached' if args.staged else args.ref}")
    print(f"  Changed files: {len(files)}")
    print(f"  Domain events detected: {len(events)}")

    if not events:
        print("  (no framework-relevant changes)")
        return

    print(f"\n  {'Event':<22s} {'Domain':<6s} {'Files':<6s} {'Trigger':<30s}")
    print(f"  {'-'*22} {'-'*6} {'-'*6} {'-'*30}")

    for evt in events:
        print(f"  {evt['event']:<22s} {evt['domain']:<6s} {len(evt['trigger_files']):<6d} {evt['trigger_prefix']:<30s}")
        for f in evt["trigger_files"][:3]:
            print(f"      → {f}")
        if len(evt["trigger_files"]) > 3:
            print(f"      ... and {len(evt['trigger_files']) - 3} more")


if __name__ == "__main__":
    main()
