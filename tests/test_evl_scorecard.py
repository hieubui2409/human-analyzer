"""Tests for evl_scorecard — standardized scorecard emitter (md + json).

Locks the honesty surface: the UNVERIFIED list and the coverage headline are
prominent in the markdown (never buried), JSON is the source of truth and
round-trips, clinical (cache:never) scorecards are stamped reassess_required,
and writes are fenced under docs/profiles/{char}/eval/ only.
"""
import json

import pytest

from platform_lib import evl_aggregate as agg
from platform_lib import evl_scorecard as SC
from platform_lib.evl_judge import PASS, UNVERIFIED


def _rubric(kind="psychometric", cache="allow", verdict="scalar"):
    return {
        "id": "demo-rubric", "version": "1.2.0", "title": "Demo Rubric", "kind": kind,
        "subject": "single", "high_stakes": False, "verdict": verdict, "cache": cache,
        "normalization": "z_score", "min_judges": 1, "scale": {"min": 0, "max": 5},
        "aggregate": "weighted_mean",
        "domains": [{"id": "d1", "weight": 1.0, "criteria": [
            {"id": "c1", "text": "Conscientiousness", "weight": 0.5,
             "anchors": {"0": "l", "2": "m", "5": "h"}, "evidence_hint": ["x.md"], "min_tier": "T3"},
            {"id": "c2", "text": "Openness", "weight": 0.5,
             "anchors": {"0": "l", "2": "m", "5": "h"}, "evidence_hint": ["y.md"], "min_tier": "T3"}]}],
    }


def _criteria_with_one_unverified():
    return [
        {"criterion_id": "c1", "score": 4, "citation": "behavioral.md:4", "tier": "T2",
         "justification": "meets deadlines", "verdict": PASS},
        {"criterion_id": "c2", "score": None, "citation": None, "tier": None,
         "justification": "no evidence found", "verdict": UNVERIFIED},
    ]


def _meta(criteria, **kw):
    base = {"character": "test-alpha", "criteria": criteria, "asof": "2026-06-14",
            "updated_by": "evl:score"}
    base.update(kw)
    return base


def _render(kind="psychometric", cache="allow"):
    rubric = _rubric(kind=kind, cache=cache)
    crits = _criteria_with_one_unverified()
    result = agg.aggregate(rubric, crits)
    return SC.render_scorecard(rubric, result, _meta(crits))


def test_render_returns_md_and_json():
    md, data = _render()
    assert isinstance(md, str) and isinstance(data, dict)
    assert data["rubric_id"] == "demo-rubric" and data["rubric_version"] == "1.2.0"
    assert data["overall"] == pytest.approx(4.0)  # only c1 verified → domain & overall = 4.0


def test_unverified_is_loud_in_markdown():
    md, _ = _render()
    assert "UNVERIFIED" in md
    assert "c2" in md                      # the uncited criterion is named
    assert "coverage" in md.lower()        # coverage headline present


def test_coverage_headline_reflects_partial():
    md, data = _render()
    assert data["verified_coverage"] == pytest.approx(0.5)
    assert "50" in md                       # 50% coverage shown


def test_json_round_trips():
    _, data = _render()
    assert json.loads(json.dumps(data)) == data


def test_clinical_scorecard_stamps_reassess():
    md, data = _render(kind="clinical", cache="never")
    assert data["cache"] == "never" and data["reassess_required"] is True
    assert "never" in md.lower()


def test_render_is_deterministic():
    a, _ = _render()
    b, _ = _render()
    assert a == b                            # same inputs → byte-identical md


def test_scorecard_path_is_under_eval(monkeypatch, tmp_path):
    import platform_lib.paths as paths_mod
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS", {"test-alpha": "test-alpha"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["test-alpha"])
    p = SC.scorecard_path("test-alpha", "demo-rubric")
    assert p.parent.name == "eval" and p.name == "demo-rubric.md"


def test_write_scorecard_emits_md_and_json(monkeypatch, tmp_path):
    import platform_lib.paths as paths_mod
    import platform_lib.fs_guard as fsg
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS", {"test-alpha": "test-alpha"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["test-alpha"])
    monkeypatch.setitem(fsg.FRAMEWORK_WRITE_ROOTS, "EVL", [tmp_path])

    rubric = _rubric()
    crits = _criteria_with_one_unverified()
    result = agg.aggregate(rubric, crits)
    out = SC.write_scorecard("test-alpha", rubric, result, _meta(crits))

    assert out.exists() and out.suffix == ".md"
    json_path = out.with_suffix(".json")
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["rubric_id"] == "demo-rubric"
    assert "eval" in out.parts                 # fenced under eval/
