#!/usr/bin/env python3
"""Scan .claude/agent-memory/ and show stats per agent: entry count, last updated."""
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ROOT
from platform_lib.formatters import print_table, print_json

AGENT_MEMORY_DIR = ROOT / ".claude" / "agent-memory"


def main():
    if not AGENT_MEMORY_DIR.exists():
        print_json({
            "agent_memory_dir": str(AGENT_MEMORY_DIR),
            "exists": False,
            "note": "No agent-memory directory found.",
        })
        sys.exit(0)

    agent_stats: dict[str, dict] = {}

    for f in AGENT_MEMORY_DIR.rglob("*.md"):
        # Agent name from parent dir or filename prefix
        if f.parent != AGENT_MEMORY_DIR:
            agent_name = f.parent.name
        else:
            # Try to infer agent name from filename (agent-name-memory.md)
            parts = f.stem.split("-")
            agent_name = "-".join(parts[:-1]) if len(parts) > 1 else f.stem

        if agent_name not in agent_stats:
            agent_stats[agent_name] = {"files": [], "total_lines": 0, "last_updated": 0.0}

        content = f.read_text(encoding="utf-8", errors="replace")
        lines = len(content.splitlines())
        mtime = f.stat().st_mtime
        agent_stats[agent_name]["files"].append(f.name)
        agent_stats[agent_name]["total_lines"] += lines
        if mtime > agent_stats[agent_name]["last_updated"]:
            agent_stats[agent_name]["last_updated"] = mtime

    if not agent_stats:
        print(f"No agent memory files found in {AGENT_MEMORY_DIR}")
        return

    rows = []
    for agent, stats in sorted(agent_stats.items()):
        last_dt = datetime.datetime.fromtimestamp(stats["last_updated"]).strftime("%Y-%m-%d %H:%M")
        rows.append([
            agent,
            str(len(stats["files"])),
            str(stats["total_lines"]),
            last_dt,
            ", ".join(stats["files"])[:60],
        ])

    print(f"## Agent Memory Stats — {AGENT_MEMORY_DIR}\n")
    print_table(["Agent", "Files", "Lines", "Last Updated", "File(s)"], rows)


if __name__ == "__main__":
    main()
