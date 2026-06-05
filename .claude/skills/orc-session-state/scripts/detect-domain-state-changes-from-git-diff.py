"""Detect domain state changes from git diff for orc:session-state event routing."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import ROOT
# Path→event routing is owned by the canonical routing registry so the diff
# detector and the domain-router cannot drift apart. detect_events is the shared
# canonical implementation (IGNORE_PATTERNS applied, dedup by event:prefix).
from platform_lib.event_routing import detect_events


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
    """Classify changed files into domain events (delegates to shared canonical impl)."""
    return detect_events(files)


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
