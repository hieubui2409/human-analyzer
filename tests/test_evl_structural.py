"""Tests for evl_structural — deterministic scorecard validation (no LLM).

The structural runner re-proves a finished scorecard: schema valid, every scored
criterion cited, weights unity, aggregate math reproducible, scores in bounds. A
criterion id the rubric doesn't know is UNMAPPED (loud, non-fatal unless --strict);
an unknown checker name is FAIL (misconfiguration is never silent).
"""
import copy

from platform_lib import evl_aggregate as agg
from platform_lib import evl_structural as S
from platform_lib.evl_judge import PASS


def _rubric():
    return {
        "id": "struct-test", "version": "1.0.0", "title": "S", "kind": "psychometric",
        "subject": "single", "high_stakes": False, "verdict": "scalar", "cache": "allow",
        "normalization": "none", "min_judges": 1, "scale": {"min": 0, "max": 5},
        "aggregate": "weighted_mean",
        "domains": [{"id": "d1", "weight": 1.0, "criteria": [
            {"id": "c1", "text": "t", "weight": 0.5, "anchors": {"0": "l", "2": "m", "5": "h"},
             "evidence_hint": ["x.md"], "min_tier": "T3"},
            {"id": "c2", "text": "t", "weight": 0.5, "anchors": {"0": "l", "2": "m", "5": "h"},
             "evidence_hint": ["y.md"], "min_tier": "T3"}]}],
    }


def _criteria():
    return [
        {"criterion_id": "c1", "score": 4, "citation": "x.md:1", "tier": "T1",
         "justification": "j", "verdict": PASS},
        {"criterion_id": "c2", "score": 2, "citation": "y.md:2", "tier": "T2",
         "justification": "j", "verdict": PASS},
    ]


def _scorecard(rubric=None, criteria=None):
    rubric = rubric or _rubric()
    criteria = criteria if criteria is not None else _criteria()
    return {**agg.aggregate(rubric, criteria), "criteria": criteria}


def _status(rows, check):
    return next(r["status"] for r in rows if r["check"] == check)


def test_valid_scorecard_passes_all():
    verdict, rows = S.run_structural(_scorecard(), _rubric())
    assert verdict == "PASS"
    assert all(r["status"] in ("PASS", "SKIP") for r in rows), rows


def test_uncited_scored_criterion_fails():
    crits = _criteria()
    crits[0] = {**crits[0], "citation": None, "tier": None}
    verdict, rows = S.run_structural(_scorecard(criteria=crits), _rubric())
    assert verdict == "FAIL"
    assert _status(rows, "every_criterion_cited") == "FAIL"


def test_score_out_of_bounds_fails():
    crits = _criteria()
    crits[0] = {**crits[0], "score": 9}  # 9 > scale max 5
    verdict, rows = S.run_structural(_scorecard(criteria=crits), _rubric())
    assert verdict == "FAIL"
    assert _status(rows, "score_in_bounds") == "FAIL"


def test_tampered_overall_fails_math():
    sc = _scorecard()
    sc["overall"] = 4.9  # real aggregate is 3.0
    verdict, rows = S.run_structural(sc, _rubric())
    assert verdict == "FAIL"
    assert _status(rows, "aggregate_math_correct") == "FAIL"


def test_broken_rubric_weights_fail_schema():
    r = _rubric()
    r["domains"][0]["criteria"][0]["weight"] = 0.9  # 0.9 + 0.5 ≠ 1.0
    verdict, rows = S.run_structural(_scorecard(rubric=_rubric()), r)
    assert verdict == "FAIL"
    assert _status(rows, "rubric_schema_valid") == "FAIL"


def test_unmapped_criterion_is_loud_nonfatal_then_fatal_strict():
    crits = _criteria() + [{"criterion_id": "ghost", "score": 3, "citation": "z.md:1",
                            "tier": "T2", "justification": "j", "verdict": PASS}]
    sc = _scorecard(criteria=crits)
    verdict, rows = S.run_structural(sc, _rubric())
    assert _status(rows, "criteria_mapped") == "UNMAPPED"
    assert verdict == "PASS"  # loud but non-fatal
    sverdict, _ = S.run_structural(sc, _rubric(), strict=True)
    assert sverdict == "FAIL"  # strict promotes UNMAPPED to fatal


def test_unknown_checker_is_fail():
    verdict, rows = S.run_structural(_scorecard(), _rubric(), checks=["bogus_check"])
    assert verdict == "FAIL"
    assert _status(rows, "bogus_check") == "FAIL"


def test_scalar_verdict_skips_threshold_check():
    _, rows = S.run_structural(_scorecard(), _rubric())
    assert _status(rows, "verdict_thresholds_cover_range") == "SKIP"
    assert _status(rows, "verdict_matches_band") == "SKIP"  # scalar has no band


# --- H1: a tampered/stale verdict must not pass the structural gate ----------

def _tri_rubric():
    r = _rubric()
    r["verdict"] = "tri_state"
    r["verdict_thresholds"] = {"BLOCKED": {"min": 0, "max": 1.5},
                               "PASS_WITH_RISK": {"min": 1.5, "max": 3.5},
                               "PASS": {"min": 3.5, "max": 5}}
    return r


def test_correct_verdict_band_passes():
    r = _tri_rubric()
    sc = _scorecard(rubric=r)          # overall 3.0 → PASS_WITH_RISK (aggregate sets it)
    verdict, rows = S.run_structural(sc, r)
    assert _status(rows, "verdict_matches_band") == "PASS"
    assert verdict == "PASS"


def test_tampered_verdict_fails_band_check():
    r = _tri_rubric()
    sc = _scorecard(rubric=r)
    sc["verdict"] = "PASS"             # real band for overall 3.0 is PASS_WITH_RISK
    verdict, rows = S.run_structural(sc, r)
    assert _status(rows, "verdict_matches_band") == "FAIL"
    assert verdict == "FAIL"


# --- H2: a safety red_flag can only clear on evidence -----------------------

def _flagged_rubric():
    r = _rubric()
    r["red_flags"] = ["c1"]
    return r


def test_red_flag_with_evidence_passes():
    r = _flagged_rubric()
    verdict, rows = S.run_structural(_scorecard(rubric=r), r)
    assert _status(rows, "red_flags_assessed") == "PASS"


def test_unverified_red_flag_fails_closed():
    r = _flagged_rubric()
    crits = _criteria()
    crits[0] = {**crits[0], "citation": None, "tier": None}  # c1 (a red_flag) now unverified
    verdict, rows = S.run_structural(_scorecard(rubric=r, criteria=crits), r)
    assert _status(rows, "red_flags_assessed") == "FAIL"
    assert verdict == "FAIL"


def test_no_red_flags_skips():
    _, rows = S.run_structural(_scorecard(), _rubric())
    assert _status(rows, "red_flags_assessed") == "SKIP"
