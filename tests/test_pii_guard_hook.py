"""Tests for the born-time PII write-guard: pii_guard_check.py (judgment) + pii-guard-on-write.cjs (shim).

NAME-FREE: every fixture uses a SYNTHETIC roster (slug `zeta`, full name "Zeta Quux Synthetic") written
to a tmp dir and fed via --profiles-dir / PII_GUARD_PROFILES_DIR — no real name is hardcoded here, and
the tests do not depend on the live characters.yaml.

The guard blocks a real-name token the moment it would be written into a SHIPPED-CLASS file (one the pack
distributes); writes into the pack-excluded corpus (docs/profiles, …) pass. Collision-free scanner token
set parity with scan_pack_pii: slugs + multi-word full names match; bare display names do not gate.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
HOOK = PROJECT_DIR / ".claude" / "hooks" / "pii-guard-on-write.cjs"
_SHARED = PROJECT_DIR / ".claude" / "skills" / "_framework-shared" / "scripts"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

import pii_guard_check  # noqa: E402

_SYNTH_ROSTER = (
    "characters:\n"
    "  zeta:\n"
    "    display: Zeta\n"
    "    aliases:\n"
    '      - "Zeta Quux Synthetic"\n'
)
_HAVE_NODE = shutil.which("node") is not None


@pytest.fixture
def roster(tmp_path):
    d = tmp_path / "roster"
    d.mkdir()
    (d / "characters.yaml").write_text(_SYNTH_ROSTER, encoding="utf-8")
    return d


class TestShippedClassClassification:
    @pytest.mark.parametrize("rel", [
        ".claude/skills/orc-bootstrap/SKILL.md",
        ".claude/scripts/platform_lib/paths.py",
        "docs/rules/01-profile-structure.md",
        "tests/test_x.py",
        "README.md",
        "CLAUDE.md",
        ".claude/hooks/pii-guard-on-write.cjs",
    ])
    def test_shipped_paths(self, rel):
        assert pii_guard_check.is_shipped_class(rel) is True

    @pytest.mark.parametrize("rel", [
        "docs/profiles/zeta/INDEX.md",   # corpus — where real names belong (safety_filter drop)
        "docs/materials/zeta/x.md",
        "docs/graph/dyads.md",
        "docs/references/theory.md",
        "plans/some-plan/phase-01.md",   # not an include glob
        "BACKLOG.md",
    ])
    def test_non_shipped_paths(self, rel):
        assert pii_guard_check.is_shipped_class(rel) is False


class TestGlobMatcher:
    def test_double_star_spans_segments(self):
        assert pii_guard_check._glob_to_re(".claude/scripts/**/*").match(
            ".claude/scripts/platform_lib/paths.py")

    def test_single_star_within_segment_only(self):
        # `orc-*` must not leak past its segment boundary.
        assert pii_guard_check._glob_to_re(".claude/skills/orc-*/SKILL.md").match(
            ".claude/skills/orc-bootstrap/SKILL.md")
        assert not pii_guard_check._glob_to_re(".claude/skills/orc-*").match(
            ".claude/skills/orc-bootstrap/SKILL.md")


class TestCheck:
    def test_blocks_slug_on_shipped(self, roster):
        v = pii_guard_check.check(".claude/skills/orc-bootstrap/SKILL.md",
                                  "intro character-zeta — zeta outro", roster)
        assert v["block"] is True and "zeta" in v["tokens"]

    def test_blocks_full_name_on_shipped(self, roster):
        v = pii_guard_check.check("docs/rules/01-x.md", "see Zeta Quux Synthetic", roster)
        assert v["block"] is True and "Zeta Quux Synthetic" in v["tokens"]

    def test_corpus_write_allowed(self, roster):
        v = pii_guard_check.check("docs/profiles/zeta/INDEX.md", "zeta everywhere", roster)
        assert v["block"] is False and v["reason"] == "not-shipped-class"

    def test_non_shipped_path_allowed(self, roster):
        v = pii_guard_check.check("plans/foo.md", "zeta", roster)
        assert v["block"] is False and v["reason"] == "not-shipped-class"

    def test_clean_text_on_shipped_passes(self, roster):
        v = pii_guard_check.check("tests/test_x.py", "nothing forbidden here", roster)
        assert v["block"] is False and v["reason"] == "clean"

    def test_word_boundary_no_partial_match(self, roster):
        # 'zeta' inside 'zetamorphic' must NOT trip — word-boundary anchored.
        v = pii_guard_check.check("README.md", "zetamorphic compound", roster)
        assert v["block"] is False

    def test_roster_absent_no_op(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        v = pii_guard_check.check(".claude/skills/orc-bootstrap/SKILL.md", "zeta", empty)
        assert v["block"] is False and v["reason"] == "roster-absent"

    def test_outside_repo_path_ignored(self, roster):
        v = pii_guard_check.check("/etc/passwd", "zeta", roster)
        assert v["block"] is False and v["reason"] == "outside-repo"


def _run_hook(payload: dict, roster_dir: Path, project_dir: Path | None = None):
    env = {**os.environ,
           "CLAUDE_PROJECT_DIR": str(project_dir or PROJECT_DIR),
           "PII_GUARD_PROFILES_DIR": str(roster_dir)}
    return subprocess.run(["node", str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, env=env)


@pytest.mark.skipif(not _HAVE_NODE, reason="node not available")
class TestHookIntegration:
    def test_blocks_write_with_token(self, roster):
        r = _run_hook({"tool_name": "Write",
                       "tool_input": {"file_path": ".claude/skills/orc-bootstrap/SKILL.md",
                                      "content": "hi character-zeta bye"}}, roster)
        assert r.returncode == 2 and "PII WRITE-GUARD" in r.stderr

    def test_blocks_edit_with_token(self, roster):
        r = _run_hook({"tool_name": "Edit",
                       "tool_input": {"file_path": "docs/rules/01-x.md",
                                      "new_string": "Zeta Quux Synthetic"}}, roster)
        assert r.returncode == 2

    def test_blocks_multiedit_token_in_later_edit(self, roster):
        r = _run_hook({"tool_name": "MultiEdit",
                       "tool_input": {"file_path": "tests/test_y.py",
                                      "edits": [{"new_string": "clean"},
                                                {"new_string": "zeta"}]}}, roster)
        assert r.returncode == 2

    def test_corpus_write_passes(self, roster):
        r = _run_hook({"tool_name": "Edit",
                       "tool_input": {"file_path": "docs/profiles/zeta/INDEX.md",
                                      "new_string": "zeta"}}, roster)
        assert r.returncode == 0

    def test_ignores_read_tool(self, roster):
        r = _run_hook({"tool_name": "Read",
                       "tool_input": {"file_path": ".claude/skills/orc-bootstrap/SKILL.md"}}, roster)
        assert r.returncode == 0

    def test_unparseable_stdin_fails_open(self, roster):
        env = {**os.environ, "PII_GUARD_PROFILES_DIR": str(roster)}
        r = subprocess.run(["node", str(HOOK)], input="not json",
                           capture_output=True, text=True, env=env)
        assert r.returncode == 0

    def test_disabled_via_framework_config(self, roster, tmp_path):
        # Isolated project dir: disabled config + a symlink to the real skills tree so the helper
        # script + venv resolve. Disabled ⇒ run() returns early ⇒ exit 0 even on a shipped-class token.
        proj = tmp_path / "proj"
        (proj / ".claude").mkdir(parents=True)
        (proj / ".claude" / "skills").symlink_to(PROJECT_DIR / ".claude" / "skills")
        (proj / ".claude" / "framework-config.json").write_text(
            json.dumps({"hooks": {"pii-guard-on-write": False}}), encoding="utf-8")
        r = _run_hook({"tool_name": "Write",
                       "tool_input": {"file_path": ".claude/skills/orc-bootstrap/SKILL.md",
                                      "content": "character-zeta"}}, roster, project_dir=proj)
        assert r.returncode == 0
