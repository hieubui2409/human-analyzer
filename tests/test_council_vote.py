"""Tests for run-council-vote.py — prepare questions + format verdict docs (Batch 4 A4).

Scope: script I/O correctness only. Anti-anchoring enforcement is an LLM workflow
concern in SKILL.md. Tally does NO stance counting (GOLDEN RULE: scripts=deterministic).
"""
import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

COUNCIL_SCRIPT = PROJECT_ROOT / ".claude" / "skills" / "orc-council" / "scripts" / "run-council-vote.py"


def _load_council():
    spec = importlib.util.spec_from_file_location("council_mod", COUNCIL_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def council(tmp_path, monkeypatch):
    """Load council script with DECISIONS redirected to tmp_path/decisions."""
    mod = _load_council()
    decisions = tmp_path / "decisions"
    monkeypatch.setattr(mod, "DECISIONS", decisions)
    return mod


def _valid_payload():
    return {
        "question": "Should the council verdict live in formulation or decisions",
        "category": "psy",
        "character": "test-alpha",  # synthetic slug — format_verdict only round-trips this field
        "advocate": "Yes, decisions dir keeps clinical files clean.",
        "skeptic": "But formulation is where clinicians look first.",
        "pragmatist": "decisions dir is searchable and append-only — ship it.",
        "wildcard": "What if both, with a backlink?",
        "synthesis": "Store in .claude/decisions/ with a pointer note in formulation.",
    }


class TestPrepare:
    def test_prepare_valid_question(self, council):
        result = council.prepare("Which voice dominates multi-character content", "cre")
        assert result["slug"]
        assert result["output_path"].endswith(".md")
        assert "council" in result["output_path"]

    def test_prepare_empty_question(self, council):
        with pytest.raises(SystemExit):
            council.prepare("   ", "cre")

    def test_prepare_long_question(self, council):
        with pytest.raises(SystemExit):
            council.prepare("x " * 300, "cre")  # >500 chars

    def test_prepare_output_path_format(self, council):
        result = council.prepare("Pick the career path for Alex", "gro")
        date_str = datetime.now().strftime("%Y%m%d")
        fname = Path(result["output_path"]).name
        assert re.fullmatch(rf"{date_str}-council-[\w-]+\.md", fname)

    def test_slugify(self, council):
        assert council.slugify("Hello World Foo Bar Baz Qux") == "hello-world-foo-bar-baz"


class TestTally:
    def test_tally_valid_json(self, council, tmp_path):
        import json
        inp = tmp_path / "input.json"
        inp.write_text(json.dumps(_valid_payload()), encoding="utf-8")
        out_path = council.tally(str(inp))
        assert Path(out_path).exists()
        content = Path(out_path).read_text(encoding="utf-8")
        assert "Council Verdict" in content

    def test_tally_missing_voice_field(self, council, tmp_path):
        import json
        payload = _valid_payload()
        del payload["wildcard"]
        inp = tmp_path / "input.json"
        inp.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SystemExit):
            council.tally(str(inp))

    def test_tally_no_stance_counting(self, council):
        """Verdict embeds voice text verbatim — no vote tally / stance counting (GOLDEN RULE)."""
        md = council.format_verdict(_valid_payload())
        # Voice responses appear verbatim
        assert "decisions dir keeps clinical files clean" in md
        # No heuristic counting artifacts
        assert "votes:" not in md.lower()
        assert "majority" not in md.lower()
        assert "tally:" not in md.lower()
        assert "winner" not in md.lower()


class TestVerdictFormat:
    def test_verdict_frontmatter(self, council):
        md = council.format_verdict(_valid_payload())
        date_str = datetime.now().strftime("%Y-%m-%d")
        assert f"date: {date_str}" in md
        assert "category: council" in md
        assert "character: test-alpha" in md
        assert "status: active" in md
        assert "title:" in md

    def test_verdict_sections(self, council):
        md = council.format_verdict(_valid_payload())
        assert "## Advocate" in md
        assert "## Skeptic" in md
        assert "## Pragmatist" in md
        assert "## Wildcard" in md
        assert "## Synthesized Verdict" in md


class TestDecisionStorage:
    def test_verdict_writes_to_decisions_dir(self, council, tmp_path):
        import json
        inp = tmp_path / "input.json"
        inp.write_text(json.dumps(_valid_payload()), encoding="utf-8")
        out_path = council.tally(str(inp))
        assert str(out_path).startswith(str(tmp_path / "decisions"))

    def test_existing_verdict_not_overwritten(self, council, tmp_path):
        import json
        inp = tmp_path / "input.json"
        inp.write_text(json.dumps(_valid_payload()), encoding="utf-8")
        first = council.tally(str(inp))
        second = council.tally(str(inp))
        assert first != second
        assert Path(first).exists() and Path(second).exists()
        assert re.search(r"-2\.md$", second)


class TestDecisionMigration:
    def test_decisions_path_constant(self):
        from platform_lib.paths import DECISIONS, ROOT
        assert DECISIONS == ROOT / ".claude" / "decisions"

    def test_index_script_uses_decisions_constant(self):
        idx = PROJECT_ROOT / ".claude" / "skills" / "orc-decisions" / "scripts" / "index-decisions-with-search.py"
        content = idx.read_text(encoding="utf-8")
        assert "DECISIONS" in content
        assert "plans/decisions" not in content
