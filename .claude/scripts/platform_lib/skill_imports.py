"""Shared AST introspection of framework-skill scripts → platform_lib import edges.

com:skill-analytics had two copies of "parse every framework script, extract which
platform_lib submodules it imports" (health-check's importer_counts + dependency-graph's
_imports/_framework_scripts) that could drift. This is the single implementation.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator

from .paths import SKILLS, PLATFORM_LIB
from .skill_ids import FRAMEWORKS, framework_of


def framework_script_dirs() -> Iterator[tuple[str, Path]]:
    """Yield (framework, skill_dir) for every project framework-skill directory."""
    for d in sorted(SKILLS.iterdir()):
        if d.is_dir() and framework_of(d.name) in FRAMEWORKS:
            yield framework_of(d.name), d


def framework_scripts() -> Iterator[Path]:
    """Yield every .py under a framework skill's scripts/ directory."""
    for _, d in framework_script_dirs():
        yield from sorted((d / "scripts").glob("*.py")) if (d / "scripts").is_dir() \
            else sorted(d.glob("scripts/*.py"))


def platform_lib_imports_of(path: Path) -> set[str]:
    """Set of platform_lib submodule names a script imports (e.g. {'paths','formatters'})."""
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return set()
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("platform_lib"):
            parts = node.module.split(".")
            if len(parts) > 1:
                # from platform_lib.foo import bar
                mods.add(parts[1])
            else:
                # from platform_lib import foo, bar  → each name is a submodule
                for n in node.names:
                    mods.add(n.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                if n.name.startswith("platform_lib."):
                    mods.add(n.name.split(".")[1])
    return mods


def platform_lib_importer_counts() -> dict[str, int]:
    """For each platform_lib module, how many framework scripts import it (fan-in)."""
    counts: dict[str, int] = {m.stem: 0 for m in PLATFORM_LIB.glob("*.py") if m.stem != "__init__"}
    for script in framework_scripts():
        for name in platform_lib_imports_of(script):
            if name in counts:
                counts[name] += 1
    return counts
