"""Tests for evl_aggregate — the deterministic honesty-contract core.

Locks: uncited / invalid-tier / too-weak-tier criteria are NEVER silently scored —
they are excluded from the weighted roll-up AND counted in a loud list. Weighted
math is exact against a hand-computed fixture. No LLM, no IO — pure arithmetic.
"""
import pytest

from platform_lib import evl_aggregate as agg


def _rubric(aggregate="weighted_mean", verdict="scalar", thresholds=None,
            c1_min="T3", c2_min="T3", c3_min="T3"):
    r = {
        "id": "t", "scale": {"min": 0, "max": 5},
        "aggregate": aggregate, "verdict": verdict,
        "domains": [
            {"id": "D1", "weight": 0.6, "criteria": [
                {"id": "c1", "weight": 0.5, "min_tier": c1_min},
                {"id": "c2", "weight": 0.5, "min_tier": c2_min}]},
            {"id": "D2", "weight": 0.4, "criteria": [
                {"id": "c3", "weight": 1.0, "min_tier": c3_min}]},
        ],
    }
    if thresholds:
        r["verdict_thresholds"] = thresholds
    return r


def _score(cid, score, tier=None, citation=None):
    return {"criterion_id": cid, "score": score, "citation": citation,
            "tier": tier, "justification": "j"}


def _all_verified():
    return [
        _score("c1", 4, "T1", "behavioral-patterns.md:12"),
        _score("c2", 2, "T2", "interview.md:3"),
        _score("c3", 5, "T1", "diary.md:1"),
    ]


# --- exact weighted math ----------------------------------------------------

def test_all_verified_weighted_mean_is_exact():
    res = agg.aggregate(_rubric(), _all_verified())
    # D1 = (0.5*4 + 0.5*2)/1.0 = 3.0 ; D2 = 5.0 ; overall = 0.6*3 + 0.4*5 = 3.8
    assert res["overall"] == pytest.approx(3.8)
    doms = {d["id"]: d for d in res["domains"]}
    assert doms["D1"]["score"] == pytest.approx(3.0)
    assert doms["D2"]["score"] == pytest.approx(5.0)
    assert res["unverified"] == []
    assert res["verified_coverage"] == pytest.approx(1.0)


def test_weighted_sum_mode_branch():
    res = agg.aggregate(_rubric(aggregate="weighted_sum"), _all_verified())
    # full coverage, weights sum to 1 → same numeric result as mean here
    assert res["overall"] == pytest.approx(3.8)


# --- honesty contract: uncited never silently scored ------------------------

def test_uncited_criterion_excluded_and_listed():
    scores = [
        _score("c1", 4, "T1", "x.md:1"),
        _score("c2", 2, "T2", "y.md:2"),
        _score("c3", 5, tier=None, citation=None),  # no citation
    ]
    res = agg.aggregate(_rubric(), scores)
    assert "c3" in res["unverified"]
    doms = {d["id"]: d for d in res["domains"]}
    assert doms["D2"]["score"] is None          # whole domain unscored
    assert doms["D2"]["coverage"] == pytest.approx(0.0)
    # overall re-normalizes over scored domains → just D1 = 3.0
    assert res["overall"] == pytest.approx(3.0)
    assert res["verified_coverage"] == pytest.approx(2 / 3)


def test_invalid_tier_string_is_unverified():
    scores = _all_verified()
    scores[0] = _score("c1", 4, "T9", "x.md:1")  # T9 not a real tier
    res = agg.aggregate(_rubric(), scores)
    assert "c1" in res["unverified"]


def test_citation_without_tier_is_unverified():
    scores = _all_verified()
    scores[0] = _score("c1", 4, tier=None, citation="x.md:1")
    res = agg.aggregate(_rubric(), scores)
    assert "c1" in res["unverified"]


# --- too-weak evidence is excluded, not silently accepted --------------------

def test_tier_weaker_than_min_is_below_min_tier():
    # c1 requires T2; judge cites T4 (weaker) → excluded + flagged, not scored
    scores = _all_verified()
    scores[0] = _score("c1", 4, "T4", "x.md:1")
    res = agg.aggregate(_rubric(c1_min="T2"), scores)
    assert "c1" in res["below_min_tier"]
    assert "c1" not in res["unverified"]
    # D1 now scored on c2 alone: (0.5*2)/0.5 = 2.0
    doms = {d["id"]: d for d in res["domains"]}
    assert doms["D1"]["score"] == pytest.approx(2.0)
    assert doms["D1"]["coverage"] == pytest.approx(0.5)


def test_tier_meeting_min_exactly_is_verified():
    scores = _all_verified()
    scores[0] = _score("c1", 4, "T2", "x.md:1")  # min T2, cites T2 → ok
    res = agg.aggregate(_rubric(c1_min="T2"), scores)
    assert "c1" not in res["below_min_tier"] and "c1" not in res["unverified"]


# --- verdict band mapping (deterministic) -----------------------------------

_TRI = {"BLOCKED": {"min": 0, "max": 1.5},
        "PASS_WITH_RISK": {"min": 1.5, "max": 3.5},
        "PASS": {"min": 3.5, "max": 5}}


def test_verdict_for_score_bands():
    r = _rubric(verdict="tri_state", thresholds=_TRI)
    assert agg.verdict_for_score(r, 3.8) == "PASS"
    assert agg.verdict_for_score(r, 1.0) == "BLOCKED"
    assert agg.verdict_for_score(r, 2.0) == "PASS_WITH_RISK"
    assert agg.verdict_for_score(r, 1.5) == "PASS_WITH_RISK"  # lower bound inclusive
    assert agg.verdict_for_score(r, 5.0) == "PASS"            # max inclusive


def test_verdict_for_scalar_is_none():
    assert agg.verdict_for_score(_rubric(), 3.8) is None


def test_verdict_for_none_overall_is_none():
    r = _rubric(verdict="tri_state", thresholds=_TRI)
    assert agg.verdict_for_score(r, None) is None


# --- coverage helper + empty input ------------------------------------------

def test_coverage_helper():
    res = agg.aggregate(_rubric(), _all_verified())
    assert agg.coverage(res) == pytest.approx(1.0)


def test_no_scores_yields_none_overall_zero_coverage():
    res = agg.aggregate(_rubric(), [])
    assert res["overall"] is None
    assert res["verified_coverage"] == pytest.approx(0.0)
    assert sorted(res["unverified"]) == ["c1", "c2", "c3"]
