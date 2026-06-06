"""Meta-test: assert zero forbidden real-name tokens in the shipped test tree.

Loads the forbidden token set from the same source (pii_tokens.tokens_only / characters.yaml)
that the masker and privacy scanner use — so scanner and test share the same definition of
"forbidden". Skips cleanly when the roster file is absent (toolkit-only consumer pack with no
characters.yaml), since there is nothing to forbid in that state.

Scope: tests/*.py except this file itself and tests/mock-data (mock-data is intentionally
synthetic and was already verified to contain no real names).
"""
import re
import sys
from pathlib import Path

import pytest

_TEST_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _TEST_DIR.parent


def _load_forbidden_tokens() -> list[str]:
    """Load forbidden tokens from the shared pii_tokens module.

    Returns [] when the roster is absent (toolkit-only pack) so the test skips cleanly.
    """
    anonymize_dir = _PROJECT_ROOT / "tools" / "anonymize"
    if str(anonymize_dir) not in sys.path:
        sys.path.insert(0, str(anonymize_dir))
    try:
        from pii_tokens import tokens_only
        return tokens_only()
    except ImportError:
        return []


def _collect_test_files() -> list[Path]:
    """All test files in scope: tests/*.py excluding this file and mock-data subtree."""
    this_file = Path(__file__).resolve()
    return [
        f for f in sorted(_TEST_DIR.glob("*.py"))
        if f.resolve() != this_file
    ]


@pytest.mark.parametrize("test_file", _collect_test_files(), ids=lambda p: p.name)
def test_no_real_names_in_test_file(test_file: Path) -> None:
    """Each test file must contain zero forbidden real-name tokens.

    Skips when the token list is absent (no characters.yaml → nothing to forbid).
    Fails when any forbidden token is found, reporting the file, line, and token.
    """
    tokens = _load_forbidden_tokens()
    if not tokens:
        pytest.skip("No forbidden token list available — roster absent, skipping name check")

    # Build a single alternation pattern for efficiency; word-boundary aware.
    pattern = re.compile(
        r"(?<!\w)(" + "|".join(re.escape(t) for t in tokens) + r")(?!\w)",
        re.IGNORECASE,
    )

    try:
        content = test_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        pytest.fail(f"Could not read {test_file.name}: {exc}")

    hits: list[str] = []
    for lineno, line in enumerate(content.splitlines(), 1):
        for m in pattern.finditer(line):
            hits.append(f"  line {lineno}: {m.group()!r} in: {line.strip()[:80]}")

    assert not hits, (
        f"Forbidden real-name token(s) found in {test_file.name}:\n"
        + "\n".join(hits)
        + "\n\nDe-name: replace with slug-based lookup or synthetic placeholder."
    )
