"""Tests for evl_pipeline — thin deterministic composition used by the skill scripts.

gather_payload / gather_dyad_payload assemble the evidence bundle the LLM judges work
from; finalize_scorecard turns collected judge scores into an aggregated, written
scorecard. No judgment here — it only wires the deterministic engine stages together.
"""
import json

import pytest

from platform_lib import evl_pipeline as P
from platform_lib.evl_judge import PASS
from platform_lib.paths import RUBRICS


@pytest.mark.usefixtures("patch_platform_paths")
def test_gather_payload_shapes_bundle():
    payload = P.gather_payload("test-alpha", RUBRICS / "psychometric-big-five.yaml")
    assert payload["rubric_id"] == "psychometric-big-five"
    assert payload["character"] == "test-alpha"
    assert payload["scale"] == {"min": 0, "max": 5}
    assert isinstance(payload["evidence_by_criterion"], dict)


@pytest.mark.usefixtures("patch_platform_paths")
def test_gather_dyad_payload_uses_both():
    payload = P.gather_dyad_payload(("test-alpha", "test-beta"),
                                    RUBRICS / "relationship-compatibility.yaml")
    assert payload["pair"] == ["test-alpha", "test-beta"]
    assert isinstance(payload["evidence_by_criterion"], dict)


def test_gather_payload_rejects_dyad_rubric():
    with pytest.raises(ValueError):
        P.gather_payload("x", RUBRICS / "relationship-compatibility.yaml")


def test_finalize_writes_scorecard(monkeypatch, tmp_path):
    import platform_lib.paths as paths_mod
    import platform_lib.fs_guard as fsg
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS", {"test-alpha": "test-alpha"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["test-alpha"])
    monkeypatch.setitem(fsg.FRAMEWORK_WRITE_ROOTS, "EVL", [tmp_path])

    scores = [{"criterion_id": "openness", "score": 4, "citation": "x.md:1", "tier": "T2",
               "justification": "j", "verdict": PASS}]
    path, result = P.finalize_scorecard(
        "test-alpha", RUBRICS / "psychometric-big-five.yaml", scores, asof="2026-06-14")
    assert path.exists()
    data = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert data["rubric_id"] == "psychometric-big-five"
    # only 1 of many criteria scored → most are unverified, but it must not crash
    assert "openness" not in data["unverified"]


def test_finalize_dyad_scorecard_suffixes_partner(monkeypatch, tmp_path):
    import platform_lib.paths as paths_mod
    import platform_lib.fs_guard as fsg
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS", {"a": "a", "b": "b"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["a", "b"])
    monkeypatch.setitem(fsg.FRAMEWORK_WRITE_ROOTS, "EVL", [tmp_path])

    scores = [{"criterion_id": "horsemen-absence", "score": 4, "citation": "x.md:1",
               "tier": "T3", "justification": "j", "verdict": PASS}]
    path, _ = P.finalize_dyad_scorecard(
        ("a", "b"), RUBRICS / "relationship-compatibility.yaml", scores, asof="2026-06-14")
    assert path.parent.parent.name == "a"        # written under the first character
    assert path.name == "relationship-compatibility--b.md"  # partner-suffixed
