"""Canonical interpreter for tests that spawn framework scripts as subprocesses.

The skills venv is PROJECT-local (`.claude/skills/.venv/`), NOT under `$HOME` — the old
`Path.home() / ".claude" / ...` assumption broke in any container whose home != repo parent. Prefer the
project venv; fall back to the running interpreter (CI installs deps into the runner Python, no project venv).
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_VENV = _ROOT / ".claude" / "skills" / ".venv" / "bin" / "python3"
VENV_PYTHON = _PROJECT_VENV if _PROJECT_VENV.exists() else Path(sys.executable)
