"""Isolated tests for cre:angle-discovery (Batch 7 B7).

Covers the DETERMINISTIC layers (GR#4): freshness decay, cross-framework signal
gather (event streams + PSY/GRO/MAT files), and the freshness×evidence×fit ranking
arithmetic (BLOCKED sink, speculative flag, consent factor). LLM angle SYNTHESIS is
validated separately. Zero shared state: tmp streams/files + monkeypatched paths.
"""
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SK = PROJECT_ROOT / ".claude" / "skills" / "cre-angle-discovery" / "scripts"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def agg_mod():
    return _load(SK / "aggregate-angle-signals-across-frameworks.py", "b7_agg")


@pytest.fixture
def rank_mod():
    return _load(SK / "rank-angles-by-freshness-and-evidence.py", "b7_rank")


NOW = datetime(2026, 5, 26, tzinfo=timezone.utc)


# ── Freshness decay ───────────────────────────────────────────────────────────
class TestFreshness:
    def test_today_is_full(self, agg_mod):
        assert agg_mod.freshness(NOW, 30, NOW) == 1.0

    def test_beyond_window_is_zero(self, agg_mod):
        old = NOW - timedelta(days=40)
        assert agg_mod.freshness(old, 30, NOW) == 0.0

    def test_midwindow_decays_linearly(self, agg_mod):
        mid = NOW - timedelta(days=15)
        assert agg_mod.freshness(mid, 30, NOW) == pytest.approx(0.5, abs=0.01)

    def test_future_clamps_to_one(self, agg_mod):
        fut = NOW + timedelta(days=5)
        assert agg_mod.freshness(fut, 30, NOW) == 1.0


# ── Event signal gather (deterministic) ───────────────────────────────────────
class TestEventSignals:
    @pytest.fixture
    def streams(self, tmp_path, agg_mod, monkeypatch):
        cre = tmp_path / "content-events.jsonl"
        orc = tmp_path / "cascade-events.jsonl"
        fresh = (NOW - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        stale = (NOW - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
        cre.write_text(
            json.dumps({"timestamp": fresh, "event": "CRE.published",
                        "character": "test-alpha", "reason": "linkedin post shipped"}) + "\n"
            + json.dumps({"timestamp": stale, "event": "CRE.recalibrate",
                          "character": "test-alpha", "reason": "old recalibration"}) + "\n",
            encoding="utf-8")
        orc.write_text(
            json.dumps({"timestamp": fresh, "event": "ORC.bootstrap",
                        "character": None, "reason": "session boot"}) + "\n",
            encoding="utf-8")
        evl = tmp_path / "evl-events.jsonl"
        evl.write_text(
            json.dumps({"timestamp": fresh, "event": "EVL.scored",
                        "character": "test-alpha", "reason": "big-five battery rescored"}) + "\n",
            encoding="utf-8")
        monkeypatch.setattr(agg_mod.paths, "EVENT_STREAMS",
                            {"CRE": cre, "ORC": orc, "EVL": evl, "PSY": tmp_path / "x.jsonl",
                             "MAT": tmp_path / "y.jsonl", "GRO": tmp_path / "z.jsonl"})
        return agg_mod

    def test_fresh_event_kept_stale_dropped(self, streams):
        sigs = streams.event_signals(["CRE"], "test-alpha", 30, NOW)
        summaries = [s["summary"] for s in sigs]
        assert "linkedin post shipped" in summaries
        assert "old recalibration" not in summaries  # 90d > 30d window

    def test_framework_maps_to_angle_lens(self, streams):
        sigs = streams.event_signals(["CRE"], "test-alpha", 30, NOW)
        assert sigs[0]["signal_type"] == "distribution"
        assert sigs[0]["source_framework"] == "CRE"

    def test_global_event_passes_character_filter(self, streams):
        # ORC.bootstrap has character=None → must not be filtered out
        sigs = streams.event_signals(["ORC"], "test-alpha", 30, NOW)
        assert any(s["origin"] == "ORC.bootstrap" for s in sigs)

    def test_evl_event_maps_to_evaluative_lens(self, streams):
        # EVL.scored is a content-angle source (eval verdict → evaluative lens).
        sigs = streams.event_signals(["EVL"], "test-alpha", 30, NOW)
        assert sigs[0]["source_framework"] == "EVL"
        assert sigs[0]["signal_type"] == "evaluative"
        assert "big-five battery rescored" in [s["summary"] for s in sigs]

    def test_all_frameworks_includes_evl(self, agg_mod):
        assert "EVL" in agg_mod._frameworks("all")

    def test_read_only_no_stream_mutation(self, streams, tmp_path):
        before = (tmp_path / "content-events.jsonl").read_text(encoding="utf-8")
        streams.event_signals(["CRE"], "test-alpha", 30, NOW)
        after = (tmp_path / "content-events.jsonl").read_text(encoding="utf-8")
        assert before == after


# ── Ranking arithmetic (deterministic) ────────────────────────────────────────
class TestRanking:
    def test_blocked_sinks_to_bottom(self, rank_mod):
        angles = [
            {"title": "blocked", "evidence_tier": 1, "freshness": 1.0, "consent_status": "BLOCKED"},
            {"title": "clean", "evidence_tier": 2, "freshness": 0.5, "consent_status": "OK"},
        ]
        ranked = rank_mod.rank(angles)
        assert ranked[-1]["title"] == "blocked"
        assert ranked[0]["title"] == "clean"

    def test_blocked_never_dropped(self, rank_mod):
        angles = [{"title": "b", "evidence_tier": 1, "freshness": 1.0, "consent_status": "BLOCKED"}]
        ranked = rank_mod.rank(angles)
        assert len(ranked) == 1
        assert ranked[0]["publishable"] is False

    def test_t5_flagged_speculative(self, rank_mod):
        angles = [{"title": "weak", "evidence_tier": 5, "freshness": 0.9, "consent_status": "OK"}]
        ranked = rank_mod.rank(angles)
        assert ranked[0]["speculative"] is True

    def test_t1_not_speculative(self, rank_mod):
        angles = [{"title": "strong", "evidence_tier": 1, "freshness": 0.9, "consent_status": "OK"}]
        ranked = rank_mod.rank(angles)
        assert ranked[0]["speculative"] is False

    def test_freshness_outranks_when_evidence_equal(self, rank_mod):
        angles = [
            {"title": "stale", "evidence_tier": 2, "freshness": 0.1, "consent_status": "OK"},
            {"title": "fresh", "evidence_tier": 2, "freshness": 0.9, "consent_status": "OK"},
        ]
        ranked = rank_mod.rank(angles)
        assert ranked[0]["title"] == "fresh"

    def test_platform_fit_raises_score(self, rank_mod):
        narrow = rank_mod.score_angle(
            {"title": "n", "evidence_tier": 2, "freshness": 0.5, "platform_fit": ["linkedin"],
             "consent_status": "OK"})
        broad = rank_mod.score_angle(
            {"title": "b", "evidence_tier": 2, "freshness": 0.5,
             "platform_fit": ["linkedin", "facebook", "blog"], "consent_status": "OK"})
        assert broad["score"] > narrow["score"]

    def test_evidence_tier_rendered_as_label(self, rank_mod):
        scored = rank_mod.score_angle(
            {"title": "x", "evidence_tier": 3, "freshness": 0.5, "consent_status": "OK"})
        assert scored["evidence_tier"] == "T3"
