"""Tests for instinct_store.py — instinct CRUD, confidence scoring, agent mapping (Batch 3 A5)."""
import json
import math
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from platform_lib import instinct_store


@pytest.fixture(autouse=True)
def temp_instinct_file(tmp_path, monkeypatch):
    """Redirect INSTINCT_FILE to temp path for all tests."""
    temp_file = tmp_path / "instincts.jsonl"
    monkeypatch.setattr(instinct_store, "INSTINCT_FILE", temp_file)
    return temp_file


class TestCreateInstinct:
    def test_creates_with_defaults(self):
        inst = instinct_store.create_instinct("test insight", "psychology")
        assert inst["id"].startswith("instinct-")
        assert inst["confidence"] == 0.5
        assert inst["status"] == "active"
        assert inst["evidence_count"] == 1
        assert inst["category"] == "psychology"
        assert inst["pinned"] is False

    def test_creates_with_custom_confidence(self):
        inst = instinct_store.create_instinct("test", "writing", confidence=0.75)
        assert inst["confidence"] == 0.75

    def test_id_uniqueness(self):
        ids = set()
        for _ in range(10):
            inst = instinct_store.create_instinct("test", "psychology")
            ids.add(inst["id"])
        assert len(ids) == 10

    def test_process_auto_pinned(self):
        inst = instinct_store.create_instinct("workflow tip", "process")
        assert inst["pinned"] is True

    def test_text_truncation(self):
        long_text = "x" * 200
        inst = instinct_store.create_instinct(long_text, "psychology")
        assert len(inst["text"]) == 140


class TestAppendAndLoad:
    def test_append_creates_file(self, temp_instinct_file):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        assert temp_instinct_file.exists()

    def test_append_preserves_existing(self):
        for i in range(3):
            inst = instinct_store.create_instinct(f"insight {i}", "psychology")
            instinct_store.append_instinct(inst)
        loaded = instinct_store.load_instincts()
        assert len(loaded) == 3

    def test_load_filters_by_status(self):
        active = instinct_store.create_instinct("active one", "psychology")
        instinct_store.append_instinct(active)
        archived = instinct_store.create_instinct("archived one", "psychology")
        archived["status"] = "archived"
        instinct_store.append_instinct(archived)
        assert len(instinct_store.load_instincts(status="active")) == 1
        assert len(instinct_store.load_instincts(status="archived")) == 1
        assert len(instinct_store.load_instincts()) == 2

    def test_load_empty_file(self, temp_instinct_file):
        assert instinct_store.load_instincts() == []

    def test_load_handles_malformed_lines(self, temp_instinct_file):
        inst = instinct_store.create_instinct("valid", "psychology")
        instinct_store.append_instinct(inst)
        with open(temp_instinct_file, "a") as f:
            f.write("this is not json\n")
        loaded = instinct_store.load_instincts()
        assert len(loaded) == 1


class TestReinforce:
    def test_reinforcement_formula(self):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.5)
        instinct_store.append_instinct(inst)
        result = instinct_store.reinforce(inst["id"], boost=0.15)
        assert result["confidence"] == pytest.approx(0.575, abs=0.001)

    def test_reinforcement_asymptotes(self):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.5)
        instinct_store.append_instinct(inst)
        for _ in range(8):
            result = instinct_store.reinforce(inst["id"], boost=0.15)
        assert result["confidence"] <= 0.95

    def test_reinforcement_increments_evidence(self):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        result = instinct_store.reinforce(inst["id"])
        assert result["evidence_count"] == 2
        result = instinct_store.reinforce(inst["id"])
        assert result["evidence_count"] == 3

    def test_reinforce_missing_id_raises(self):
        with pytest.raises(KeyError):
            instinct_store.reinforce("nonexistent-id")

    def test_reinforce_archived_raises(self):
        inst = instinct_store.create_instinct("test", "psychology")
        inst["status"] = "archived"
        instinct_store.append_instinct(inst)
        with pytest.raises(ValueError, match="non-active"):
            instinct_store.reinforce(inst["id"])


class TestDecay:
    def test_decay_formula_7days(self, monkeypatch):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.8)
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        inst["last_reinforced"] = seven_days_ago
        instinct_store.append_instinct(inst)
        decayed = instinct_store.apply_decay(lambda_=0.05)
        assert len(decayed) == 1
        expected = 0.8 * math.exp(-0.05 * 7)
        assert decayed[0]["confidence"] == pytest.approx(expected, abs=0.01)

    def test_decay_formula_14days(self, monkeypatch):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.8)
        fourteen_days_ago = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        inst["last_reinforced"] = fourteen_days_ago
        instinct_store.append_instinct(inst)
        decayed = instinct_store.apply_decay(lambda_=0.05)
        expected = 0.8 * math.exp(-0.05 * 14)
        assert decayed[0]["confidence"] == pytest.approx(expected, abs=0.01)

    def test_decay_handles_naive_datetime(self):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.8)
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
        inst["last_reinforced"] = seven_days_ago
        instinct_store.append_instinct(inst)
        decayed = instinct_store.apply_decay(lambda_=0.05)
        assert len(decayed) == 1
        expected = 0.8 * math.exp(-0.05 * 7)
        assert decayed[0]["confidence"] == pytest.approx(expected, abs=0.01)

    def test_no_decay_for_recent(self):
        inst = instinct_store.create_instinct("test", "psychology", confidence=0.8)
        instinct_store.append_instinct(inst)
        decayed = instinct_store.apply_decay()
        assert len(decayed) == 0

    def test_pinned_exempt_from_decay(self):
        inst = instinct_store.create_instinct("workflow tip", "process", confidence=0.5)
        old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        inst["last_reinforced"] = old_date
        instinct_store.append_instinct(inst)
        decayed = instinct_store.apply_decay()
        assert len(decayed) == 0


class TestArchive:
    def test_archives_stale(self):
        inst = instinct_store.create_instinct("stale insight", "psychology", confidence=0.3)
        old_date = (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        inst["last_reinforced"] = old_date
        instinct_store.append_instinct(inst)
        archived = instinct_store.archive_stale(conf_threshold=0.4, days_threshold=30)
        assert len(archived) == 1
        assert archived[0]["status"] == "archived"

    def test_keeps_healthy(self):
        inst = instinct_store.create_instinct("healthy", "psychology", confidence=0.8)
        instinct_store.append_instinct(inst)
        archived = instinct_store.archive_stale()
        assert len(archived) == 0

    def test_pinned_exempt(self):
        inst = instinct_store.create_instinct("process tip", "process", confidence=0.2)
        old_date = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        inst["last_reinforced"] = old_date
        instinct_store.append_instinct(inst)
        archived = instinct_store.archive_stale(conf_threshold=0.4, days_threshold=30)
        assert len(archived) == 0
        active = instinct_store.load_instincts(status="active")
        assert len(active) == 1


class TestFindSimilar:
    def test_exact_match(self):
        inst = instinct_store.create_instinct("Nhân vật B avoidance under stress", "psychology")
        instinct_store.append_instinct(inst)
        results = instinct_store.find_similar("Nhân vật B avoidance under stress")
        assert len(results) >= 1
        assert results[0][1] == pytest.approx(1.0, abs=0.01)

    def test_similar_text(self):
        inst = instinct_store.create_instinct("Nhân vật B avoidance intensifies under academic pressure", "psychology")
        instinct_store.append_instinct(inst)
        results = instinct_store.find_similar("Nhân vật B avoidance intensifies under academic pressure and stress", threshold=0.7)
        assert len(results) >= 1

    def test_dissimilar_text(self):
        inst = instinct_store.create_instinct("Nhân vật B avoidance under stress", "psychology")
        instinct_store.append_instinct(inst)
        results = instinct_store.find_similar("LinkedIn post structure works well")
        assert len(results) == 0


class TestPromotionCandidates:
    def test_meets_criteria(self):
        inst = instinct_store.create_instinct("strong insight", "psychology", confidence=0.85)
        inst["evidence_count"] = 4
        instinct_store.append_instinct(inst)
        candidates = instinct_store.get_promotion_candidates()
        assert len(candidates) == 1

    def test_below_threshold(self):
        inst = instinct_store.create_instinct("weak insight", "psychology", confidence=0.75)
        inst["evidence_count"] = 2
        instinct_store.append_instinct(inst)
        candidates = instinct_store.get_promotion_candidates()
        assert len(candidates) == 0


class TestUpdateInstinct:
    def test_update_fields(self):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        result = instinct_store.update_instinct(inst["id"], confidence=0.9, tags=["updated"])
        assert result["confidence"] == 0.9
        assert result["tags"] == ["updated"]
        reloaded = instinct_store.load_instincts()
        assert reloaded[0]["confidence"] == 0.9

    def test_update_missing_id_raises(self):
        with pytest.raises(KeyError):
            instinct_store.update_instinct("nonexistent-id", confidence=0.5)

    def test_update_immutable_field_raises(self):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        with pytest.raises(ValueError, match="immutable"):
            instinct_store.update_instinct(inst["id"], id="new-id")
        with pytest.raises(ValueError, match="immutable"):
            instinct_store.update_instinct(inst["id"], created_at="2020-01-01")

    def test_reinforce_missing_id_raises(self):
        with pytest.raises(KeyError):
            instinct_store.reinforce("nonexistent-id")


class TestAgentCategoryMapping:
    def test_mapping_psychologist(self):
        cats = instinct_store.get_agent_categories("psychologist")
        assert cats == ["psychology", "clinical"]

    def test_mapping_content_strategist(self):
        cats = instinct_store.get_agent_categories("content-strategist")
        assert cats == ["writing", "audience"]

    def test_mapping_growth_analyst(self):
        cats = instinct_store.get_agent_categories("growth-analyst")
        assert cats == ["growth"]

    def test_unmapped_category(self):
        cats = instinct_store.get_agent_categories("unknown-agent")
        assert cats == []


class TestAtomicRewrite:
    def test_atomic_rewrite_persists(self):
        for i in range(3):
            inst = instinct_store.create_instinct(f"insight {i}", "psychology")
            instinct_store.append_instinct(inst)
        loaded = instinct_store.load_instincts()
        assert len(loaded) == 3
        instinct_store.reinforce(loaded[0]["id"])
        reloaded = instinct_store.load_instincts()
        assert len(reloaded) == 3
        assert reloaded[0]["evidence_count"] == 2

    def test_load_valid_during_normal_ops(self):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        before = instinct_store.load_instincts()
        instinct_store.reinforce(inst["id"])
        after = instinct_store.load_instincts()
        assert len(before) == 1
        assert len(after) == 1


class TestCLI:
    def test_cli_stats(self, temp_instinct_file, monkeypatch, capsys):
        inst = instinct_store.create_instinct("test", "psychology")
        instinct_store.append_instinct(inst)
        monkeypatch.setattr(sys, "argv", ["instinct_store.py", "--stats"])
        instinct_store.main()
        captured = capsys.readouterr()
        assert '"total_active": 1' in captured.out

    def test_cli_list(self, temp_instinct_file, monkeypatch, capsys):
        inst = instinct_store.create_instinct("visible insight", "psychology")
        instinct_store.append_instinct(inst)
        monkeypatch.setattr(sys, "argv", ["instinct_store.py", "--list"])
        instinct_store.main()
        captured = capsys.readouterr()
        assert "visible insight" in captured.out
        assert "psychology" in captured.out
