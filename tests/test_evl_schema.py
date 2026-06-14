"""Tests for evl_schema — canonical EVL rubric loader + validator.

Locks the rubric contract: shape (via the shared Draft-7 engine) PLUS the cross-field
invariants JSON-Schema cannot express (weight sums, high-stakes judge floor, clinical
rails, threshold coverage, tier vocabulary). Every invalid rubric must produce a precise,
loud error string — never a silent pass.
"""
import copy
from pathlib import Path

import pytest

from platform_lib import evl_schema

FIXTURES = Path(__file__).resolve().parent / "golden" / "evl"


def _valid_minimal() -> dict:
    """A valid canonical rubric dict — single source mutated by the invariant tests."""
    return {
        "id": "minimal-test",
        "version": "1.0.0",
        "title": "Minimal Test Rubric",
        "kind": "psychometric",
        "subject": "single",
        "high_stakes": False,
        "verdict": "scalar",
        "cache": "allow",
        "normalization": "z_score",
        "min_judges": 1,
        "scale": {"min": 0, "max": 5},
        "aggregate": "weighted_mean",
        "domains": [
            {
                "id": "d1",
                "weight": 1.0,
                "criteria": [
                    {
                        "id": "c1",
                        "text": "Criterion one",
                        "weight": 1.0,
                        "anchors": {"0": "low", "2": "mid", "5": "high"},
                        "evidence_hint": ["behavioral-patterns.md"],
                        "min_tier": "T2",
                    }
                ],
            }
        ],
    }


def _domain(did: str, weight: float) -> dict:
    return {
        "id": did,
        "weight": weight,
        "criteria": [
            {
                "id": f"{did}-c1",
                "text": "c",
                "weight": 1.0,
                "anchors": {"0": "low", "2": "mid", "5": "high"},
                "evidence_hint": ["x.md"],
                "min_tier": "T3",
            }
        ],
    }


def _tri_state_thresholds() -> dict:
    return {
        "BLOCKED": {"min": 0, "max": 1.5},
        "PASS_WITH_RISK": {"min": 1.5, "max": 3.5},
        "PASS": {"min": 3.5, "max": 5},
    }


# --- happy path -------------------------------------------------------------

def test_valid_minimal_dict_has_no_errors():
    assert evl_schema.validate_rubric(_valid_minimal()) == []


def test_valid_minimal_yaml_loads_and_validates():
    r = evl_schema.load_and_validate(FIXTURES / "rubric-valid-minimal.yaml")
    assert r["id"] == "minimal-test"
    assert r["scale"]["max"] == 5


def test_load_rubric_returns_dict():
    r = evl_schema.load_rubric(FIXTURES / "rubric-valid-minimal.yaml")
    assert isinstance(r, dict) and r["kind"] == "psychometric"


# --- invariant 1: weight sums ----------------------------------------------

def test_domain_weights_must_sum_to_one():
    r = _valid_minimal()
    r["domains"].append(_domain("d2", 0.5))  # 1.0 + 0.5 = 1.5
    errs = evl_schema.validate_rubric(r)
    assert any("domain" in e.lower() and "weight" in e.lower() and "sum" in e.lower() for e in errs), errs


def test_criterion_weights_must_sum_to_one_within_domain():
    r = _valid_minimal()
    r["domains"][0]["criteria"] = [
        {"id": "c1", "text": "a", "weight": 0.5, "anchors": {"0": "l", "2": "m", "5": "h"},
         "evidence_hint": ["x.md"], "min_tier": "T2"},
        {"id": "c2", "text": "b", "weight": 0.3, "anchors": {"0": "l", "2": "m", "5": "h"},
         "evidence_hint": ["x.md"], "min_tier": "T2"},
    ]
    errs = evl_schema.validate_rubric(r)
    assert any("criteri" in e.lower() and "weight" in e.lower() and "sum" in e.lower() for e in errs), errs


# --- invariant 2: high_stakes ⇒ min_judges >= 2 ----------------------------

def test_high_stakes_requires_two_judges():
    r = _valid_minimal()
    r["high_stakes"] = True
    r["min_judges"] = 1
    errs = evl_schema.validate_rubric(r)
    assert any("high_stakes" in e and "judge" in e.lower() for e in errs), errs


# --- invariant 3: clinical ⇒ cache never AND verdict tri_state -------------

def test_clinical_requires_cache_never():
    r = _valid_minimal()
    r["kind"] = "clinical"
    r["high_stakes"] = True
    r["min_judges"] = 2
    r["verdict"] = "tri_state"
    r["verdict_thresholds"] = _tri_state_thresholds()
    r["cache"] = "allow"  # the violation in isolation
    errs = evl_schema.validate_rubric(r)
    assert any("clinical" in e.lower() and "cache" in e.lower() for e in errs), errs


def test_clinical_requires_tri_state_verdict():
    r = _valid_minimal()
    r["kind"] = "clinical"
    r["high_stakes"] = True
    r["min_judges"] = 2
    r["cache"] = "never"
    r["verdict"] = "scalar"  # the violation in isolation
    errs = evl_schema.validate_rubric(r)
    assert any("clinical" in e.lower() and "tri_state" in e.lower() for e in errs), errs


# --- invariant 4: non-scalar verdict ⇒ thresholds present + cover range -----

def test_tri_state_requires_thresholds():
    r = _valid_minimal()
    r["verdict"] = "tri_state"  # no verdict_thresholds
    errs = evl_schema.validate_rubric(r)
    assert any("threshold" in e.lower() for e in errs), errs


def test_thresholds_must_cover_scale_with_no_gaps():
    r = _valid_minimal()
    r["verdict"] = "tri_state"
    r["verdict_thresholds"] = {
        "BLOCKED": {"min": 0, "max": 1.5},
        "PASS": {"min": 2.0, "max": 5},  # gap 1.5..2.0
    }
    errs = evl_schema.validate_rubric(r)
    assert any("threshold" in e.lower() and ("gap" in e.lower() or "cover" in e.lower()) for e in errs), errs


# --- invariant 5: decision ⇒ target_profile --------------------------------

def test_decision_requires_target_profile():
    r = _valid_minimal()
    r["kind"] = "decision"
    r["verdict"] = "decision"
    r["verdict_thresholds"] = {"NO": {"min": 0, "max": 2.5}, "YES": {"min": 2.5, "max": 5}}
    # no target_profile
    errs = evl_schema.validate_rubric(r)
    assert any("target_profile" in e and "decision" in e.lower() for e in errs), errs


# --- invariant 6: min_tier ∈ {T1..T5} --------------------------------------

def test_bad_tier_is_rejected():
    r = _valid_minimal()
    r["domains"][0]["criteria"][0]["min_tier"] = "T9"
    errs = evl_schema.validate_rubric(r)
    assert any("tier" in e.lower() for e in errs), errs


# --- invariant 7: anchors include scale endpoints + a mid ------------------

def test_anchors_must_include_min_mid_max():
    r = _valid_minimal()
    r["domains"][0]["criteria"][0]["anchors"] = {"0": "low", "5": "high"}  # no mid
    errs = evl_schema.validate_rubric(r)
    assert any("anchor" in e.lower() for e in errs), errs


# --- schema-shape failure (missing required field) -------------------------

def test_missing_required_field_is_schema_error():
    r = _valid_minimal()
    del r["scale"]
    errs = evl_schema.validate_rubric(r)
    assert errs, "missing scale must error"


# --- load_and_validate raises loudly ---------------------------------------

def test_load_and_validate_raises_on_invalid(tmp_path):
    import yaml
    bad = copy.deepcopy(_valid_minimal())
    bad["min_judges"] = 1
    bad["high_stakes"] = True
    p = tmp_path / "bad.yaml"
    p.write_text(yaml.safe_dump(bad), encoding="utf-8")
    with pytest.raises(evl_schema.EvlSchemaError) as exc:
        evl_schema.load_and_validate(p)
    assert "judge" in str(exc.value).lower()


# --- list_rubrics ----------------------------------------------------------

def test_list_rubrics_finds_yaml(tmp_path):
    (tmp_path / "a.yaml").write_text("id: a", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("id: b", encoding="utf-8")
    (tmp_path / "note.md").write_text("x", encoding="utf-8")
    found = evl_schema.list_rubrics(tmp_path)
    names = sorted(p.name for p in found)
    assert names == ["a.yaml", "b.yaml"]
