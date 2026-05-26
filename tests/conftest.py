"""Shared pytest fixtures for ck-marketing test suite.

Monkeypatches platform_lib.paths to point at tests/mock-data/
so scripts under test never touch real docs/profiles, docs/materials, docs/references.
"""
import os
import sys
from pathlib import Path

import pytest

# Disable telemetry side-effects (atexit script metrics + sink writes) for the
# whole session BEFORE any platform_lib import triggers the auto-import.
os.environ["CK_TELEMETRY_DISABLED"] = "1"

# Ensure platform_lib is importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

MOCK_DATA_DIR = Path(__file__).resolve().parent / "mock-data"


@pytest.fixture(scope="session")
def mock_data_dir() -> Path:
    """Absolute path to tests/mock-data/."""
    return MOCK_DATA_DIR


@pytest.fixture(autouse=False)
def patch_platform_paths(monkeypatch):
    """Redirect platform_lib.paths globals to mock-data for the duration of a test."""
    import platform_lib.paths as paths_mod
    import platform_lib.materials_classifier as mat_mod
    import platform_lib.profile_validator as val_mod

    mock_profiles = MOCK_DATA_DIR / "profiles"
    mock_materials = MOCK_DATA_DIR / "materials"
    mock_references = MOCK_DATA_DIR / "references"

    # Patch paths module globals
    monkeypatch.setattr(paths_mod, "PROFILES", mock_profiles)
    monkeypatch.setattr(paths_mod, "MATERIALS", mock_materials)
    monkeypatch.setattr(paths_mod, "REFERENCES", mock_references)
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["test-alpha", "test-beta"])
    monkeypatch.setattr(
        paths_mod,
        "CHAR_DISPLAY",
        {"test-alpha": "Alpha", "test-beta": "Beta"},
    )
    monkeypatch.setattr(
        paths_mod,
        "CHARACTERS",
        {
            "test-alpha": "test-alpha",
            "alpha": "test-alpha",
            "test-beta": "test-beta",
            "beta": "test-beta",
        },
    )

    # Patch materials_classifier which imports from paths at module level
    monkeypatch.setattr(mat_mod, "MATERIALS", mock_materials)
    monkeypatch.setattr(mat_mod, "ALL_CHARS", ["test-alpha", "test-beta"])
    monkeypatch.setattr(mat_mod, "CHAR_DISPLAY", {"test-alpha": "Alpha", "test-beta": "Beta"})

    # Patch profile_validator
    monkeypatch.setattr(val_mod, "PROFILES", mock_profiles)
    monkeypatch.setattr(val_mod, "ALL_CHARS", ["test-alpha", "test-beta"])
    monkeypatch.setattr(val_mod, "CHAR_DISPLAY", {"test-alpha": "Alpha", "test-beta": "Beta"})

    return {
        "profiles": mock_profiles,
        "materials": mock_materials,
        "references": mock_references,
    }


@pytest.fixture(scope="session")
def python_bin() -> Path:
    """Path to the project venv Python interpreter."""
    return Path.home() / ".claude" / "skills" / ".venv" / "bin" / "python3"


@pytest.fixture(scope="session")
def skills_dir() -> Path:
    """Root of .claude/skills/."""
    return Path(__file__).resolve().parents[1] / ".claude" / "skills"


@pytest.fixture(scope="session")
def scripts_root() -> Path:
    """Root of .claude/scripts/ (platform_lib lives here)."""
    return Path(__file__).resolve().parents[1] / ".claude" / "scripts"
