"""Isolated tests for psy:relation-intelligence (Batch 6 B9).

Covers the DETERMINISTIC layers (GR#4): graph-fact extraction, consent gating
(Rule-09 tag + crisis marker, fail-closed), trauma exclusion, primary_character
hint, and angle ranking arithmetic. LLM angle SYNTHESIS is validated separately.

Zero shared state: tmp graph/profile files; pure functions on dicts.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SK = PROJECT_ROOT / ".claude" / "skills" / "psy-relation-intelligence" / "scripts"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def extract_mod():
    return _load(SK / "extract-dyad-relationship-facts.py", "ri_extract")


@pytest.fixture
def rank_mod():
    return _load(SK / "rank-content-angles-by-evidence.py", "ri_rank")


GRAPH_MD = """---
domain: graph
characters: [test-alpha, test-beta]
references: []
---

# Alpha ↔ Beta

## Relationship Timeline

### Phase Transitions
- 09/2025 — Alpha và Beta trở thành bạn thân thiết với nhau
- 02/2026 — Beta nhắn "em chết cũng được" lúc khủng hoảng

## Growth Interface

### Bidirectional Growth Impact
Alpha giúp Beta xây dựng sự tự tin trong học tập mỗi ngày.
"""


# ---------- consent gating (fail-closed) ----------

class TestConsentGate:
    def test_crisis_marker_blocked(self, extract_mod):
        assert extract_mod._consent_for_line('Beta nhắn "em chết cũng được"') == "BLOCKED"

    def test_privacy_tag_blocked(self, extract_mod):
        assert extract_mod._consent_for_line("chuyện [CONFIDENTIAL: Beta] riêng") == "BLOCKED"

    def test_clean_line_ok(self, extract_mod):
        assert extract_mod._consent_for_line("Alpha giúp Beta tự tin hơn.") == "OK"

    def test_suicide_en_marker_blocked(self, extract_mod):
        assert extract_mod._consent_for_line("Beta showed self-harm signs") == "BLOCKED"


# ---------- graph fact extraction ----------

class TestExtractGraphFacts:
    def test_extracts_timeline_and_blocks_crisis(self, extract_mod, tmp_path):
        gf = tmp_path / "alpha-beta.md"
        gf.write_text(GRAPH_MD, encoding="utf-8")
        facts = extract_mod.extract_graph_facts(gf)
        assert facts, "should extract at least one fact"
        crisis = [f for f in facts if "chết" in f["text"]]
        assert crisis and crisis[0]["consent_status"] == "BLOCKED"

    def test_read_only_does_not_modify_file(self, extract_mod, tmp_path):
        gf = tmp_path / "alpha-beta.md"
        gf.write_text(GRAPH_MD, encoding="utf-8")
        before = gf.read_text(encoding="utf-8")
        extract_mod.extract_graph_facts(gf)
        assert gf.read_text(encoding="utf-8") == before

    def test_find_dyad_graph_by_frontmatter(self, extract_mod, tmp_path, monkeypatch):
        gdir = tmp_path / "graph"
        gdir.mkdir()
        (gdir / "weird-name.md").write_text(GRAPH_MD, encoding="utf-8")
        monkeypatch.setattr(extract_mod, "GRAPH", gdir)
        found = extract_mod.find_dyad_graph("test-beta", "test-alpha")  # order-independent
        assert found is not None and found.name == "weird-name.md"


# ---------- primary_character hint ----------

class TestPrimaryHint:
    def test_centrality_picks_most_mentioned(self, extract_mod, monkeypatch):
        monkeypatch.setattr(extract_mod, "CHAR_DISPLAY",
                            {"test-alpha": "Alpha", "test-beta": "Beta"})
        facts = [{"text": "Alpha làm điều này"}, {"text": "Alpha lại làm"},
                 {"text": "Beta xuất hiện"}]
        assert extract_mod.primary_character_hint(facts, ["test-alpha", "test-beta"]) == "test-alpha"


# ---------- angle ranking arithmetic ----------

class TestRanking:
    def test_blocked_fact_propagates_to_angle(self, rank_mod):
        facts = [{"fact_id": "F1", "evidence_tier": 1, "consent_status": "BLOCKED"}]
        angle = {"title": "x", "supporting_fact_ids": ["F1"], "coherence": 0.9, "publishability": 0.9}
        scored = rank_mod.score_angle(angle, {"F1": facts[0]})
        assert scored["consent_status"] == "BLOCKED" and scored["publishable"] is False

    def test_best_tier_wins(self, rank_mod):
        facts = {"F1": {"fact_id": "F1", "evidence_tier": 3, "consent_status": "OK"},
                 "F2": {"fact_id": "F2", "evidence_tier": 1, "consent_status": "OK"}}
        angle = {"supporting_fact_ids": ["F1", "F2"], "coherence": 1.0, "publishability": 1.0}
        scored = rank_mod.score_angle(angle, facts)
        assert scored["evidence_tier"] == "T1"

    def test_blocked_sinks_in_ranking(self, rank_mod):
        facts = [{"fact_id": "F1", "evidence_tier": 1, "consent_status": "OK"},
                 {"fact_id": "F2", "evidence_tier": 1, "consent_status": "BLOCKED"}]
        angles = [
            {"title": "blocked", "supporting_fact_ids": ["F2"], "coherence": 1.0, "publishability": 1.0},
            {"title": "clean", "supporting_fact_ids": ["F1"], "coherence": 0.5, "publishability": 0.5},
        ]
        ranked = rank_mod.rank(angles, facts)
        assert ranked[0]["title"] == "clean"
        assert ranked[-1]["title"] == "blocked"

    def test_no_evidence_still_scores_low_not_zero(self, rank_mod):
        angle = {"title": "y", "supporting_fact_ids": [], "coherence": 0.5, "publishability": 0.5}
        scored = rank_mod.score_angle(angle, {})
        assert 0 < scored["score"] < 0.15
