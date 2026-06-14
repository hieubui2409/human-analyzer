"""Tests for evl_normalize — cross-character calibration (pure math, no IO).

Locks: raw is always present; z-score is suppressed with a loud note when the
cohort is too small (N<3) or has zero variance — never a silently-garbage z.
Percentile is rank-based and always defined.
"""
import math

import pytest

from platform_lib import evl_normalize as norm


def test_three_char_cohort_z_and_percentile():
    out = norm.normalize_cohort("r", {"a": 4.0, "b": 3.0, "c": 2.0})
    assert out["a"]["raw"] == 4.0
    # mean 3.0, pstdev sqrt(2/3) ≈ 0.8165 → z_a ≈ +1.2247, z_c ≈ -1.2247, z_b 0
    assert out["a"]["z"] == pytest.approx(1.224745, abs=1e-5)
    assert out["b"]["z"] == pytest.approx(0.0, abs=1e-9)
    assert out["c"]["z"] == pytest.approx(-1.224745, abs=1e-5)
    assert out["a"]["percentile"] == pytest.approx(100 * 2.5 / 3)
    assert out["b"]["percentile"] == pytest.approx(50.0)
    assert out["a"]["note"] in (None, "")


def test_small_cohort_suppresses_z_with_note():
    out = norm.normalize_cohort("r", {"a": 4.0, "b": 3.0})
    assert out["a"]["z"] is None and out["b"]["z"] is None
    assert "cohort" in out["a"]["note"].lower()
    assert out["a"]["raw"] == 4.0                      # raw still emitted
    assert out["a"]["percentile"] == pytest.approx(75.0)


def test_zero_variance_suppresses_z_with_note():
    out = norm.normalize_cohort("r", {"a": 3.0, "b": 3.0, "c": 3.0})
    assert out["a"]["z"] is None
    assert "variance" in out["a"]["note"].lower()
    assert out["a"]["percentile"] == pytest.approx(50.0)


def test_single_char_cohort_is_degenerate_but_safe():
    out = norm.normalize_cohort("r", {"a": 4.0})
    assert out["a"]["raw"] == 4.0 and out["a"]["z"] is None
    assert out["a"]["percentile"] == pytest.approx(50.0)


def test_none_raw_passes_through():
    out = norm.normalize_cohort("r", {"a": 4.0, "b": None, "c": 2.0})
    assert out["b"]["raw"] is None and out["b"]["z"] is None
    # cohort of comparable (non-None) values is a,c → N=2 → z suppressed
    assert out["a"]["z"] is None


def test_normalize_method_default_and_override():
    assert norm.normalize_method({}) == "z_score"
    assert norm.normalize_method({"normalization": "percentile"}) == "percentile"


def test_z_scores_are_finite():
    out = norm.normalize_cohort("r", {"a": 10.0, "b": 5.0, "c": 0.0})
    assert all(math.isfinite(out[c]["z"]) for c in out)
