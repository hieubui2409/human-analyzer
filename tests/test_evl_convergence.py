"""Tests for evl_convergence — multi-judge agreement math (deterministic, stateless).

High-stakes rubrics run >=2 input-isolated judges; this module decides whether they
converged. Divergence is NEVER silently averaged into a fake consensus — it returns
DIVERGED + manual_review_required so a human decides.
"""
import pytest

from platform_lib import evl_convergence as C
from platform_lib.evl_judge import PASS, UNVERIFIED

SCALE = {"min": 0, "max": 5}


def _v(score, verdict=PASS, citation="x.md:1", tier="T2"):
    return {"score": score, "citation": citation, "tier": tier,
            "justification": "j", "verdict": verdict}


def test_required_judges_high_stakes_floor():
    assert C.required_judges({"high_stakes": True, "min_judges": 1}) >= 2
    assert C.required_judges({"high_stakes": True, "min_judges": 3}) == 3
    assert C.required_judges({"min_judges": 1}) == 1


def test_two_close_judges_converge():
    res = C.converge([_v(4), _v(4)], scale=SCALE)
    assert res["converged"] is True
    assert res["score"] == pytest.approx(4.0)      # median consensus
    assert res["verdict"] == PASS
    assert "manual_review_required" not in res or not res["manual_review_required"]


def test_judges_within_tolerance_converge_median():
    res = C.converge([_v(4), _v(3), _v(4)], scale=SCALE)
    assert res["converged"] is True
    assert res["score"] == pytest.approx(4.0)      # median of [3,4,4]


def test_verdict_disagreement_diverges():
    res = C.converge([_v(4, PASS), _v(None, UNVERIFIED, citation=None, tier=None)], scale=SCALE)
    assert res["converged"] is False
    assert res["verdict"] == "DIVERGED"
    assert res["manual_review_required"] is True


def test_score_spread_too_wide_diverges():
    # both PASS but 1 vs 5 on a 0-5 scale → spread 4 > 20% tolerance (1.0)
    res = C.converge([_v(1), _v(5)], scale=SCALE)
    assert res["converged"] is False
    assert res["verdict"] == "DIVERGED"


def test_converge_merges_citations():
    res = C.converge([_v(4, citation="a.md:1"), _v(4, citation="b.md:2")], scale=SCALE)
    assert "a.md:1" in res["citation"] and "b.md:2" in res["citation"]


def test_agreement_reports_pct_and_spread():
    a = C.agreement([_v(4), _v(4), _v(2)])         # all PASS verdicts, scores 4/4/2
    assert a["n"] == 3
    assert a["pct"] == pytest.approx(1.0)          # all 3 share the modal verdict (PASS)
    assert a["spread"] == pytest.approx(2.0)       # 4-2


def test_agreement_pct_with_a_dissenter():
    a = C.agreement([_v(4, PASS), _v(4, PASS), _v(None, UNVERIFIED, citation=None, tier=None)])
    assert a["pct"] == pytest.approx(2 / 3)        # 2 of 3 agree on PASS


def test_cohen_kappa_perfect_agreement():
    a = ["PASS", "FAIL", "PASS", "FAIL"]
    assert C.cohen_kappa(a, list(a)) == pytest.approx(1.0)


def test_cohen_kappa_total_disagreement_is_negative():
    assert C.cohen_kappa(["PASS", "PASS"], ["FAIL", "FAIL"]) <= 0.0


def test_cohen_kappa_single_category_is_none():
    # no variance in either rater → kappa undefined
    assert C.cohen_kappa(["PASS", "PASS"], ["PASS", "PASS"]) is None


def test_single_judge_does_not_converge():
    res = C.converge([_v(4)], scale=SCALE)
    assert res["converged"] is False  # convergence needs >=2 judges


def test_consensus_needs_every_judge_to_score():
    # both say PASS, but one abstained (score None) — a consensus resting on one
    # verified judge defeats the multi-judge guarantee → must NOT converge
    abstained = {"score": None, "citation": "x.md:1", "tier": "T2",
                 "justification": "j", "verdict": PASS}
    res = C.converge([_v(4), abstained], scale=SCALE)
    assert res["converged"] is False
    assert res["verdict"] == "DIVERGED"
