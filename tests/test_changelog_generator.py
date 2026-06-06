"""Tests for the release tooling — deterministic RELEASE-NOTES catalog + Keep a Changelog lifecycle.

`generate_changelog.py` asserts the generated release notes enumerate the full live catalog (every
framework + skill + domain agent + framework hook), are byte-deterministic across runs, and contain
zero real-name tokens. `release_changelog.py` manages the hand-maintained root CHANGELOG.md
(extract / lock / bump), and the committed CHANGELOG.md is gated PII-clean.
"""
import sys
from pathlib import Path

import pytest

_TOOLS_RELEASE = Path(__file__).resolve().parents[1] / "tools" / "release"
if str(_TOOLS_RELEASE) not in sys.path:
    sys.path.insert(0, str(_TOOLS_RELEASE))

import generate_changelog as gen  # noqa: E402
import release_changelog as rc  # noqa: E402

_VER, _DATE = "1.0.0", "2026-06-06"


@pytest.fixture(scope="module")
def data():
    return gen.collect()


class TestCatalogCompleteness:
    def test_lists_all_skills_from_tree(self, data):
        skill_dirs = sum(
            len(list((gen.REPO / ".claude" / "skills").glob(f"{fw}-*")))
            for fw, _ in gen.FRAMEWORKS
        )
        notes = gen.render_release_notes(data, _VER, _DATE)
        for f in data["frameworks"]:
            for s in f["skills"]:
                assert f"`{s['name']}`" in notes
        assert gen._counts(data)["skills"] == skill_dirs

    def test_lists_six_frameworks_and_agents(self, data):
        assert gen._counts(data)["frameworks"] == 6
        notes = gen.render_release_notes(data, _VER, _DATE)
        for a in data["agents"]:
            assert a["name"] in notes
        assert len(data["agents"]) == len(gen.scan_pack_pii._FRAMEWORK_AGENTS)

    def test_lists_framework_hooks(self, data):
        notes = gen.render_release_notes(data, _VER, _DATE)
        for h in data["hooks"]:
            assert h["name"] in notes
        assert len(data["hooks"]) == 6


class TestDeterminism:
    # Re-collect from the tree each time (NOT a shared fixture) so nondeterminism inside collect() —
    # glob/dict/set iteration order — is actually exercised, not masked by rendering one cached dict
    # twice. The notes carry NO git-derived block, so identical tree ⇒ identical output, forever.
    def test_release_notes_byte_identical(self):
        assert (gen.render_release_notes(gen.collect(), _VER, _DATE)
                == gen.render_release_notes(gen.collect(), _VER, _DATE))


class TestPrivacy:
    def test_release_notes_have_zero_pii_tokens(self, data):
        if not gen.pii_tokens.scan_tokens():
            pytest.skip("roster absent — nothing to assert")
        notes = gen.render_release_notes(data, _VER, _DATE)
        # _assert_pii_clean raises (SystemExit) on any leak; success = returns None.
        assert gen._assert_pii_clean(notes) is None

    def test_committed_changelog_is_pii_clean(self):
        if not gen.pii_tokens.scan_tokens():
            pytest.skip("roster absent — nothing to assert")
        # The hand/LLM-maintained CHANGELOG.md ships in docs prose; gate it like any other artifact.
        assert gen._assert_pii_clean(rc.CHANGELOG.read_text(encoding="utf-8")) is None


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
