#!/usr/bin/env python3
"""Read .claude/session-state/state.json and format as human-readable summary."""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import SESSION_STATE
from platform_lib.formatters import print_json, summary_block
from platform_lib.errors import emit_error

STATE_FILE = SESSION_STATE / "state.json"


def format_value(v) -> str:
    if isinstance(v, list):
        return ", ".join(str(x) for x in v) if v else "_(none)_"
    if isinstance(v, dict):
        return str(v)
    if v is None or v == "":
        return "_(not set)_"
    return str(v)


def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def main():
    parser = argparse.ArgumentParser(description="Read and display current session state")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--field", help="Output specific field value only")
    args = parser.parse_args()

    if not STATE_FILE.exists():
        print("No session state found.")
        print(f"Expected: {STATE_FILE}")
        sys.exit(0)

    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        emit_error("parse", str(e), {"file": str(STATE_FILE)})
        print(f"Error: state.json is malformed — {e}", file=sys.stderr)
        sys.exit(1)

    if args.field:
        val = state.get(args.field)
        print(format_value(val))
        return

    if args.json:
        print_json(state)
        return

    print("\n## Session State Summary\n")

    # Phase and mode
    phase = state.get("phase") or state.get("current_phase", "")
    mode = state.get("mode") or state.get("session_mode", "")
    if phase or mode:
        print(f"**Phase:** {phase or '_(not set)_'}  |  **Mode:** {mode or '_(not set)_'}\n")

    # Profiles touched
    profiles = state.get("profiles_touched") or state.get("characters") or []
    print(f"**Profiles Touched:** {format_value(profiles)}\n")

    # Content created
    content = state.get("content_created") or state.get("assets_created") or []
    print(f"**Content Created:** {format_value(content)}\n")

    # Last activity
    last = state.get("last_activity") or state.get("updated_at") or state.get("timestamp") or ""
    if last:
        print(f"**Last Activity:** {format_timestamp(last)}\n")

    # All other fields
    known = {"phase", "current_phase", "mode", "session_mode", "profiles_touched",
             "characters", "content_created", "assets_created", "last_activity",
             "updated_at", "timestamp"}
    extra = {k: v for k, v in state.items() if k not in known}
    if extra:
        print("### Additional Fields\n")
        for k, v in extra.items():
            print(f"- **{k}**: {format_value(v)}")

    print(f"\n---\n_State file: {STATE_FILE}_")


if __name__ == "__main__":
    main()
