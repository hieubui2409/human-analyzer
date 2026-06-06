"""Tests for tools/release/generate_changelog.py — deterministic, PII-clean catalog generator.

Asserts the generated release notes enumerate the full live catalog (every framework + skill + domain
agent + framework hook), are byte-deterministic across runs, and contain zero real-name tokens.
"""
import sys
from pathlib import Path

import pytest

_TOOLS_RELEASE = Path(__file__).resolve().parents[1] / "tools" / "release"
if str(_TOOLS_RELEASE) not in sys.path:
    sys.path.insert(0, str(_TOOLS_RELEASE))

import generate_changelog as gen  # noqa: E402

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
    # Re-collect from the tree each time (NOT the shared `data` fixture) so nondeterminism inside
    # collect() — git-log ordering, glob/dict/set iteration order — is actually exercised, not masked
    # by rendering the same cached dict twice.
    def test_release_notes_byte_identical(self):
        assert (gen.render_release_notes(gen.collect(), _VER, _DATE)
                == gen.render_release_notes(gen.collect(), _VER, _DATE))

    def test_changelog_byte_identical(self):
        assert (gen.render_changelog(gen.collect(), _VER, _DATE)
                == gen.render_changelog(gen.collect(), _VER, _DATE))


class TestPrivacy:
    def test_output_has_zero_pii_tokens(self, data):
        if not gen.pii_tokens.scan_tokens():
            pytest.skip("roster absent — nothing to assert")
        notes = gen.render_release_notes(data, _VER, _DATE)
        changelog = gen.render_changelog(data, _VER, _DATE)
        # _assert_pii_clean raises (SystemExit) on any leak; success = returns None.
        assert gen._assert_pii_clean(notes, changelog) is None
