"""Tests for the release tooling — Keep a Changelog lifecycle.

`release.py` manages the hand-maintained root CHANGELOG.md (extract / lock / bump / version), asserts a
release body is PII-clean before it can become a GitHub Release body, and the committed CHANGELOG.md is
itself gated PII-clean. The shipped README is the toolkit inventory — there is no generated per-version
catalog file.
"""
import sys
from pathlib import Path

import pytest

_SHARED_SCRIPTS = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "_framework-shared" / "scripts"
if str(_SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SHARED_SCRIPTS))

import release as rc  # noqa: E402


class TestPrivacy:
    def test_committed_changelog_is_pii_clean(self):
        if not rc.pii_tokens.scan_tokens():
            pytest.skip("roster absent — nothing to assert")
        # The hand/LLM-maintained CHANGELOG.md ships in docs prose; gate it like any other artifact.
        assert rc._assert_pii_clean(rc.CHANGELOG.read_text(encoding="utf-8")) is None


_SAMPLE = (
    "# Changelog\n\n## [Unreleased]\n\n- pending thing\n\n"
    "## [1.0.0] — 2026-06-07\n\n### Added\n- the toolkit\n"
)


class TestReleaseChangelog:
    def test_extract_returns_body_without_heading(self):
        body = rc.extract_section(_SAMPLE, "1.0.0")
        assert "### Added" in body and "the toolkit" in body
        assert "## [1.0.0]" not in body  # heading excluded

    def test_extract_unknown_version_raises(self):
        with pytest.raises(SystemExit):
            rc.extract_section(_SAMPLE, "9.9.9")

    def test_lock_moves_unreleased_to_version_and_opens_fresh(self):
        locked = rc.lock_unreleased(_SAMPLE, "1.1.0", "2026-07-01")
        assert "## [1.1.0] — 2026-07-01" in locked
        # the pending entry is now under the new version, and a fresh empty Unreleased remains on top
        assert rc.extract_section(locked, "1.1.0").strip().startswith("- pending thing")
        assert rc.extract_section(locked, "Unreleased").strip() == ""

    def test_lock_refuses_empty_unreleased(self):
        empty = "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] — 2026-06-07\n- x\n"
        with pytest.raises(SystemExit):
            rc.lock_unreleased(empty, "1.1.0", "2026-07-01")

    def test_lock_refuses_existing_version(self):
        with pytest.raises(SystemExit):
            rc.lock_unreleased(_SAMPLE, "1.0.0", "2026-07-01")

    @pytest.mark.parametrize("cur,level,expected", [
        ("1.0.0", "patch", "1.0.1"),
        ("1.0.0", "minor", "1.1.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.1.0-rc.1", "patch", "1.1.1"),
    ])
    def test_bump_version(self, cur, level, expected):
        assert rc.bump_version(cur, level) == expected

    def test_manifest_version_roundtrip(self):
        ver = rc.manifest_version()
        assert ver and all(part.isdigit() for part in ver.split("-")[0].split("."))
        bumped = rc.set_manifest_version(rc.MANIFEST.read_text(encoding="utf-8"), "9.9.9")
        assert 'version: "9.9.9"' in bumped
