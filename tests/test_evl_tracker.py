"""Tests for evl_tracker — score-over-time diff + deterministic event attribution.

Diffs two scorecard snapshots (overall / per-domain / verdict / coverage) and joins
profile-change events by (character, timestamp) — a deterministic join only; narrative
causation is the LLM's job in the skill, never inferred by this script.
"""
import json

import pytest

from platform_lib import evl_tracker as T


def _card(overall, verdict, cov, d1):
    return {"overall": overall, "verdict": verdict, "verified_coverage": cov,
            "domains": [{"id": "d1", "score": d1}]}


def test_diff_overall_verdict_coverage_and_domain():
    d = T.diff_scorecards(_card(3.0, "PASS_WITH_RISK", 0.8, 3.0),
                          _card(4.0, "PASS", 1.0, 4.0))
    assert d["overall_delta"] == pytest.approx(1.0)
    assert d["verdict_change"] == ("PASS_WITH_RISK", "PASS")
    assert d["coverage_delta"] == pytest.approx(0.2)
    assert d["domains"][0]["delta"] == pytest.approx(1.0)


def test_diff_none_overall_is_uncomputable():
    d = T.diff_scorecards(_card(None, "PASS", 0.0, None), _card(3.0, "PASS", 1.0, 3.0))
    assert d["overall_delta"] is None       # cannot diff from a missing prior score


def test_diff_no_verdict_change_is_none():
    d = T.diff_scorecards(_card(3.0, "PASS", 1.0, 3.0), _card(3.0, "PASS", 1.0, 3.0))
    assert d["verdict_change"] is None


def test_attribute_changes_filters_character_and_since(tmp_path):
    log = tmp_path / "events.jsonl"
    log.write_text("\n".join(json.dumps(r) for r in [
        {"timestamp": "2026-05-01T10:00:00Z", "event": "PSY.refresh", "character": "test-alpha"},
        {"timestamp": "2026-05-03T10:00:00Z", "event": "GRO.assessed", "character": "test-alpha"},
        {"timestamp": "2026-05-03T10:00:00Z", "event": "PSY.refresh", "character": "test-beta"},
    ]), encoding="utf-8")
    out = T.attribute_changes("test-alpha", "2026-05-02T00:00:00Z", event_paths=[log])
    assert len(out) == 1
    assert out[0]["event"] == "GRO.assessed" and out[0]["character"] == "test-alpha"


def test_attribute_changes_surfaces_untagged_records(tmp_path):
    # Live telemetry records carry {timestamp, event, source, reason} — NO character.
    # These must be surfaced in the window, never silently dropped.
    log = tmp_path / "events.jsonl"
    log.write_text("\n".join(json.dumps(r) for r in [
        {"timestamp": "2026-05-01T10:00:00Z", "event": "PSY.refresh", "source": "psy:wave", "reason": "old"},
        {"timestamp": "2026-05-03T10:00:00Z", "event": "GRO.assessed", "source": "gro:assess", "reason": "new"},
    ]), encoding="utf-8")
    out = T.attribute_changes("test-alpha", "2026-05-02T00:00:00Z", event_paths=[log])
    assert len(out) == 1 and out[0]["event"] == "GRO.assessed"  # untagged but in window


def test_attribute_changes_missing_log_is_empty(tmp_path):
    assert T.attribute_changes("test-alpha", "2026-01-01T00:00:00Z",
                               event_paths=[tmp_path / "nope.jsonl"]) == []


def test_load_current_and_history(tmp_path, monkeypatch):
    import platform_lib.paths as paths_mod
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS", {"test-alpha": "test-alpha"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["test-alpha"])
    eval_dir = tmp_path / "test-alpha" / "eval"
    (eval_dir / "history").mkdir(parents=True)
    (eval_dir / "demo.json").write_text(json.dumps(_card(4.0, "PASS", 1.0, 4.0)), encoding="utf-8")
    (eval_dir / "history" / "demo-2026-05-01.json").write_text(
        json.dumps(_card(3.0, "PASS", 0.8, 3.0)), encoding="utf-8")
    (eval_dir / "history" / "demo-2026-06-01.json").write_text(
        json.dumps(_card(3.5, "PASS", 0.9, 3.5)), encoding="utf-8")

    assert T.load_current("test-alpha", "demo")["overall"] == 4.0
    hist = T.load_history("test-alpha", "demo")
    assert [h["overall"] for h in hist] == [3.0, 3.5]    # chronological by snapshot name
