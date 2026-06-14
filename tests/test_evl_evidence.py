"""Tests for evl_evidence — deterministic candidate retrieval (gather, never judge).

The script only SURFACES candidate snippets + a best-effort tier tag for the LLM
judge to pick and cite; it makes no scoring decision. Runs against tests/mock-data.
"""
import pytest

from platform_lib import evl_evidence as ev

pytestmark = pytest.mark.usefixtures("patch_platform_paths")


def _crit(cid="c1", hints=("psychology/*.md",), min_tier="T3"):
    return {"id": cid, "evidence_hint": list(hints), "min_tier": min_tier}


def _tier_num(t):
    return int(t[1:]) if t else 99


def test_gather_for_criterion_returns_evidence():
    out = ev.gather_for_criterion("test-alpha", _crit())
    assert out, "psychology/*.md should surface candidates"
    e = out[0]
    assert set(e) >= {"text", "source", "tier", "section", "character"}
    assert e["source"].startswith("psychology/") and ":" in e["source"]  # file:line
    assert e["character"] == "test-alpha"


def test_gather_caps_candidates():
    out = ev.gather_for_criterion(
        "test-alpha", _crit(hints=("psychology/*.md", "identity/*.md", "*.md")))
    assert len(out) <= ev.MAX_CANDIDATES


def test_unmatched_hint_is_empty():
    assert ev.gather_for_criterion("test-alpha", _crit(hints=("nonexistent/*.md",))) == []


def test_gather_for_rubric_keys_by_criterion():
    rubric = {"subject": "single", "domains": [{"id": "d", "weight": 1.0, "criteria": [
        _crit("c1", ("psychology/*.md",)), _crit("c2", ("identity/*.md",))]}]}
    out = ev.gather_for_rubric("test-alpha", rubric)
    assert set(out) == {"c1", "c2"}
    assert isinstance(out["c1"], list)


def test_tier_tag_explicit_and_confidence_fallback():
    assert ev._tier_tag({"evidence_tier": "T1"}) == "T1"
    assert ev._tier_tag({"tier": 2}) == "T2"
    assert ev._tier_tag({"confidence": "high"}) == "T2"
    assert ev._tier_tag({"confidence": "medium"}) == "T3"
    assert ev._tier_tag({"confidence": "low"}) == "T4"
    assert ev._tier_tag({"tier": "T9"}) is None  # not a real tier
    assert ev._tier_tag({}) is None


def test_candidates_ranked_strongest_tier_first():
    out = ev.gather_for_criterion(
        "test-alpha", _crit(hints=("*.md", "psychology/*.md", "identity/*.md")))
    nums = [_tier_num(e["tier"]) for e in out]
    assert nums == sorted(nums), "strongest tier (lowest number) must come first"


def test_gather_for_dyad_pulls_both_characters():
    rubric = {"subject": "dyad", "domains": [{"id": "d", "weight": 1.0, "criteria": [
        _crit("c1", ("relationships/*.md",))]}]}
    out = ev.gather_for_dyad(("test-alpha", "test-beta"), rubric)
    chars = {e["character"] for e in out["c1"]}
    assert chars == {"test-alpha", "test-beta"}
