"""Regression test: zero stale profile filename references across project."""
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OLD_FILENAMES = [
    "SOUL.md", "DARKNESS.md", "LIGHT.md", "CHARACTERISTIC.md",
    "WRITING-VOICE.md", "IDENTITY.md", "RELATIONSHIPS.md",
]

EXCLUDE_PATTERNS = [
    "__pycache__", "LEGACY_", "PROFILE_FILE_MAP", "LEGACY_TO_NEW_MAP",
    "LEGACY_SPLIT_MAP", "OLD_FILENAMES", "# Old", "# Legacy",
    "→", "->", "plans/", ".pyc", "mock-data",
]


def test_zero_stale_refs_in_skills():
    pattern = "|".join(rf"{f}" for f in OLD_FILENAMES)
    result = subprocess.run(
        ["grep", "-rn", "--include=*.py", "--include=*.md", pattern,
         str(PROJECT_ROOT / ".claude" / "skills"),
         str(PROJECT_ROOT / ".claude" / "agents")],
        capture_output=True, text=True,
    )
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
    stale = [
        ln for ln in lines
        if not any(exc in ln for exc in EXCLUDE_PATTERNS)
    ]
    assert stale == [], f"Found {len(stale)} stale refs:\n" + "\n".join(stale[:20])


def test_no_stale_refs_in_platform_lib():
    """platform_lib may have old names in mapping dicts — those are OK.
    But any USAGE outside of mapping dicts is stale."""
    paths_py = PROJECT_ROOT / ".claude" / "scripts" / "platform_lib" / "paths.py"
    content = paths_py.read_text()
    for old in OLD_FILENAMES:
        occurrences = content.count(f'"{old}"')
        mapping_contexts = sum(1 for ln in content.split("\n")
                               if f'"{old}"' in ln and ("LEGACY" in ln or "MAP" in ln or ":" in ln))
        assert occurrences == mapping_contexts, (
            f'{old} appears {occurrences} times but only {mapping_contexts} in mapping dicts'
        )
