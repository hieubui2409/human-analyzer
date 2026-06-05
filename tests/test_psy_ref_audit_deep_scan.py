"""psy:ref-audit behavioral deep-scan script — exit codes, output shape, --json contract."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".claude" / "skills" / "psy-ref-audit" / "scripts" / "build-behavioral-deep-scan-prompt.py"
_VENV = ROOT / ".claude" / "skills" / ".venv" / "bin" / "python3"
PY = str(_VENV) if _VENV.exists() else sys.executable
ENV = {**__import__("os").environ, "PYTHONPATH": str(ROOT / ".claude" / "scripts")}


def _run(*args):
    return subprocess.run(
        [PY, str(SCRIPT)] + list(args),
        capture_output=True, text=True, env=ENV, timeout=60,
    )


def test_help_exits_0():
    """--help must succeed (passes test_skill_scripts_import_validation.py's contract)."""
    r = _run("--help")
    assert r.returncode == 0, r.stderr
    assert "character" in r.stdout.lower()


def test_hieu_plain_exits_0():
    """Running on a real character must exit 0 (deterministic, read-only)."""
    r = _run("--character", "hieu")
    assert r.returncode == 0, r.stderr


def test_hieu_output_contains_instructions_block():
    """stdout must include the '## Instructions' block from build_llm_prompt_for_deep_scan."""
    r = _run("--character", "hieu")
    assert r.returncode == 0, r.stderr
    assert "## Instructions" in r.stdout, "Expected '## Instructions' block in prompt output"


def test_hieu_output_contains_profile_section():
    """stdout must contain at least one profile section marker (file:line-line format)."""
    r = _run("--character", "hieu")
    assert r.returncode == 0, r.stderr
    # extract_sections_for_llm_review emits blocks like [formulation.md:1-5]
    import re
    assert re.search(r"\[\S+\.md:\d+-\d+\]", r.stdout), (
        "Expected at least one [filename.md:N-N] section block in output"
    )


def test_json_shape_has_required_keys():
    """--json output must be valid JSON with keys: character, files, prompt."""
    r = _run("--character", "hieu", "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert {"character", "files", "prompt"} <= set(data.keys()), (
        f"Missing keys. Got: {sorted(data.keys())}"
    )


def test_json_character_field_is_full_slug():
    """character field must be the canonical slug, not the alias."""
    r = _run("--character", "hieu", "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["character"] == "character-a", (
        f"Expected 'character-a', got '{data['character']}'"
    )


def test_json_prompt_contains_instructions():
    """The prompt string inside JSON must contain the Instructions block."""
    r = _run("--character", "hieu", "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert "## Instructions" in data["prompt"]


def test_slug_filter_reduces_catalog():
    """--slugs limits the Behavioral Theory Catalog to only listed theories."""
    r_full = _run("--character", "hieu")
    r_filtered = _run("--character", "hieu", "--slugs", "savior-complex")
    assert r_full.returncode == 0 and r_filtered.returncode == 0
    # Filtered output must be shorter (fewer catalog entries)
    assert len(r_filtered.stdout) < len(r_full.stdout), (
        "Filtered prompt should be shorter than full prompt"
    )
    assert "savior-complex" in r_filtered.stdout
    # Another slug (not in filter) should not appear in the catalog section
    # It may appear in the profile text itself, so only check the catalog header area
    catalog_section = r_filtered.stdout.split("## Profile Sections")[0]
    assert "hypervigilance" not in catalog_section, (
        "hypervigilance should not appear in catalog when filtered to savior-complex only"
    )


def test_single_file_mode():
    """--file restricts scan to one profile file; output still has Instructions block."""
    r = _run("--character", "hieu", "--file", "psychology/formulation.md")
    assert r.returncode == 0, r.stderr
    assert "## Instructions" in r.stdout


def test_invalid_character_exits_nonzero():
    """Unknown character slug must not exit 0."""
    r = _run("--character", "nonexistent-character-xyz")
    assert r.returncode != 0, "Expected non-zero exit for unknown character"


def test_invalid_file_exits_nonzero():
    """Unknown --file path must exit non-zero."""
    r = _run("--character", "hieu", "--file", "psychology/does-not-exist.md")
    assert r.returncode != 0, "Expected non-zero exit for missing file"
