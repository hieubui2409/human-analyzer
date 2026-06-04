"""P3 — Static import dependency graph for framework skill scripts.

GOLDEN RULE #4: deterministic gather. Walks every framework skill script with
ast and records which platform_lib modules it imports, then reports module
fan-in (single points of failure), unused modules, and any circular platform_lib
imports. It does NOT prescribe refactors. READ-ONLY.

Usage:
  build-dependency-graph.py [--json] [--dot] [--critical]
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths  # noqa: E402
from platform_lib.formatters import markdown_table, json_output  # noqa: E402
from platform_lib.skill_imports import (  # noqa: E402
    platform_lib_imports_of as _imports, framework_scripts as _framework_scripts,
)

PLATFORM_LIB = paths.PLATFORM_LIB
CRITICAL_FANIN = 20


def _lib_internal_edges() -> dict[str, set[str]]:
    """platform_lib module → platform_lib modules it imports (for cycle detect)."""
    edges: dict[str, set[str]] = {}
    for m in PLATFORM_LIB.glob("*.py"):
        if m.stem == "__init__":
            continue
        edges[m.stem] = {x for x in _imports(m) if x != m.stem}
    return edges


def _find_cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    WHITE, GREY, BLACK = 0, 1, 2
    color = defaultdict(int)
    stack: list[str] = []

    def dfs(u: str):
        color[u] = GREY
        stack.append(u)
        for v in edges.get(u, ()):
            if color[v] == GREY:
                i = stack.index(v)
                cycles.append(stack[i:] + [v])
            elif color[v] == WHITE:
                dfs(v)
        stack.pop()
        color[u] = BLACK

    for n in edges:
        if color[n] == WHITE:
            dfs(n)
    return cycles


def gather() -> dict:
    adjacency: dict[str, list[str]] = {}
    fanin: dict[str, int] = defaultdict(int)
    all_modules = {m.stem for m in PLATFORM_LIB.glob("*.py") if m.stem != "__init__"}
    for s in _framework_scripts():
        try:
            rel = str(s.relative_to(paths.ROOT))
        except ValueError:
            rel = str(s)  # script outside ROOT (e.g. test fixture) — use full path
        mods = sorted(_imports(s))
        adjacency[rel] = mods
        for m in mods:
            fanin[m] += 1
    unused = sorted(all_modules - set(fanin))
    critical = sorted([m for m, c in fanin.items() if c >= CRITICAL_FANIN])
    cycles = _find_cycles(_lib_internal_edges())
    return {
        "adjacency": adjacency,
        "fanin": dict(sorted(fanin.items(), key=lambda kv: -kv[1])),
        "critical_modules": critical,
        "unused_modules": unused,
        "cycles": cycles,
        "script_count": len(adjacency),
    }


def render_dot(data: dict) -> str:
    lines = ["digraph deps {", "  rankdir=LR;", "  node [shape=box];"]
    for script, mods in data["adjacency"].items():
        short = Path(script).name
        for m in mods:
            lines.append(f'  "{short}" -> "{m}";')
    lines.append("}")
    return "\n".join(lines)


def render_md(data: dict) -> str:
    rows = [[m, str(c), "CRITICAL" if c >= CRITICAL_FANIN else "ok"]
            for m, c in data["fanin"].items()]
    out = [f"# Script Dependency Graph ({data['script_count']} scripts)\n",
           markdown_table(["platform_lib module", "Fan-in", "Status"], rows)]
    if data["unused_modules"]:
        out.append("\n**Unused modules:** " + ", ".join(data["unused_modules"]))
    if data["cycles"]:
        out.append("\n**Circular imports:** " + "; ".join(" → ".join(c) for c in data["cycles"]))
    else:
        out.append("\n**Circular imports:** none")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Static import dependency graph (P3)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dot", action="store_true", help="emit graphviz DOT")
    ap.add_argument("--critical", action="store_true", help="only high fan-in modules")
    args = ap.parse_args()
    data = gather()
    if args.critical:
        data["fanin"] = {m: c for m, c in data["fanin"].items() if c >= CRITICAL_FANIN}
    if args.dot:
        print(render_dot(data))
    elif args.json:
        print(json_output(data))
    else:
        print(render_md(data))
    return 1 if data["cycles"] else 0


if __name__ == "__main__":
    sys.exit(main())
