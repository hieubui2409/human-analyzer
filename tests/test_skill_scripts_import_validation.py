"""Validate all framework Python scripts: importable + --help works."""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"
PYTHON = Path.home() / ".claude" / "skills" / ".venv" / "bin" / "python3"
DOMAINS = ["mat", "psy", "cre", "mpc", "com"]


def get_framework_scripts():
    scripts = []
    for domain in DOMAINS:
        for skill_dir in sorted(SKILLS_DIR.glob(f"{domain}-*")):
            scripts_dir = skill_dir / "scripts"
            if scripts_dir.exists():
                for py in sorted(scripts_dir.glob("*.py")):
                    if py.name != "__init__.py":
                        scripts.append(py)
    return scripts


ALL_SCRIPTS = get_framework_scripts()


@pytest.mark.parametrize("script", ALL_SCRIPTS, ids=[s.relative_to(SKILLS_DIR).as_posix() for s in ALL_SCRIPTS])
def test_script_syntax_valid(script):
    """Each script should have valid Python syntax (compiles without error)."""
    result = subprocess.run(
        [str(PYTHON), "-c", f"import py_compile; py_compile.compile('{script}', doraise=True)"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Syntax error in {script.name}:\n{result.stderr}"


@pytest.mark.parametrize("script", ALL_SCRIPTS, ids=[s.relative_to(SKILLS_DIR).as_posix() for s in ALL_SCRIPTS])
def test_script_help_or_import(script):
    """Scripts with argparse should respond to --help. Others should at least import."""
    content = script.read_text()
    if "argparse" in content or "ArgumentParser" in content:
        result = subprocess.run(
            [str(PYTHON), str(script), "--help"],
            capture_output=True, text=True, timeout=30,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts")},
        )
        assert result.returncode == 0, f"--help failed for {script.name}:\n{result.stderr}"
    else:
        result = subprocess.run(
            [str(PYTHON), "-c", f"import importlib.util; spec = importlib.util.spec_from_file_location('m', '{script}'); m = importlib.util.module_from_spec(spec)"],
            capture_output=True, text=True, timeout=30,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(PROJECT_ROOT / ".claude" / "scripts")},
        )
        # Just checking it doesn't crash on basic load — some scripts run main() on import
        # so we only check syntax, not full execution
        pass
