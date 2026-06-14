"""End-to-end regression for the 4 hand-authored reference rubrics.

These exemplars are the acceptance test for the whole engine: each must load + validate
clean, and a deterministic FakeLLMClient run (gather→judge→aggregate→render) must produce
the expected verdict + coverage. The clinical rubric exercises every honesty rail at once
(tri_state + min_judges:2 + cache:never + convergence); the dyad rubric scores a real pair.
"""
import json
import re

import pytest

from platform_lib import evl_aggregate as agg
from platform_lib import evl_convergence as conv
from platform_lib import evl_evidence as ev
from platform_lib import evl_schema
from platform_lib import evl_scorecard as sc
from platform_lib.evl_judge import FakeLLMClient, judge_rubric, judge_criterion
from platform_lib.paths import RUBRICS

REFERENCE_IDS = ["psychometric-big-five", "role-casting-fit",
                 "clinical-risk-safety", "relationship-compatibility"]


def _path(rubric_id):
    return RUBRICS / f"{rubric_id}.yaml"


def _fixed_responder(score, tier="T2"):
    """Returns the same verified score for every criterion (keyed off the prompt's id=)."""
    def fn(system, user):
        m = re.search(r"id=([\w-]+)", user)
        cid = m.group(1) if m else "x"
        return json.dumps({"score": score, "citation": f"{cid}.md:1", "tier": tier,
                           "justification": "deterministic fixture"})
    return fn


def _all_criteria(rubric):
    return [c for d in rubric["domains"] for c in d["criteria"]]


def _synthetic_evidence(rubric):
    return {c["id"]: [{"text": "e", "source": f"{c['id']}.md:1", "tier": "T2",
                       "section": "s", "character": "x"}] for c in _all_criteria(rubric)}


# --- every reference rubric loads + validates clean --------------------------

@pytest.mark.parametrize("rubric_id", REFERENCE_IDS)
def test_reference_rubric_validates(rubric_id):
    rubric = evl_schema.load_and_validate(_path(rubric_id))  # raises if invalid
    assert rubric["id"] == rubric_id


def test_exactly_four_reference_rubrics_present():
    ids = {evl_schema.load_rubric(p)["id"] for p in RUBRICS.glob("*.yaml")}
    assert set(REFERENCE_IDS) <= ids


# --- psychometric end-to-end (scalar) ---------------------------------------

def test_psychometric_full_coverage_scores_clean():
    rubric = evl_schema.load_and_validate(_path("psychometric-big-five"))
    scores = judge_rubric(rubric, _synthetic_evidence(rubric), FakeLLMClient(_fixed_responder(4, "T2")))
    result = agg.aggregate(rubric, scores)
    assert result["overall"] == pytest.approx(4.0)     # every criterion verified at 4
    assert result["unverified"] == [] and result["verified_coverage"] == pytest.approx(1.0)
    md, data = sc.render_scorecard(rubric, result, {"character": "x", "criteria": scores,
                                                    "asof": "2026-06-14"})
    assert "Psychometric" in md and data["verdict"] is None  # scalar → no verdict band


def test_uncited_judge_reply_lands_in_unverified():
    rubric = evl_schema.load_and_validate(_path("psychometric-big-five"))
    bad = FakeLLMClient('{"score": 4, "citation": null, "tier": null, "justification": "guess"}')
    scores = judge_rubric(rubric, _synthetic_evidence(rubric), bad)
    result = agg.aggregate(rubric, scores)
    assert result["overall"] is None                   # nothing verified → no score
    assert len(result["unverified"]) == len(_all_criteria(rubric))


# --- clinical end-to-end: exercises every honesty rail ----------------------

def test_clinical_severe_scores_blocked():
    rubric = evl_schema.load_and_validate(_path("clinical-risk-safety"))
    assert rubric["cache"] == "never" and rubric["verdict"] == "tri_state"
    assert conv.required_judges(rubric) == 2           # high_stakes floor
    scores = judge_rubric(rubric, _synthetic_evidence(rubric), FakeLLMClient(_fixed_responder(5, "T2")))
    result = agg.aggregate(rubric, scores)
    assert result["overall"] == pytest.approx(5.0)
    assert result["verdict"] == "BLOCKED"              # high severity → blocked
    _, data = sc.render_scorecard(rubric, result, {"character": "x", "criteria": scores,
                                                   "asof": "2026-06-14"})
    assert data["reassess_required"] is True


def test_clinical_low_scores_pass():
    rubric = evl_schema.load_and_validate(_path("clinical-risk-safety"))
    scores = judge_rubric(rubric, _synthetic_evidence(rubric), FakeLLMClient(_fixed_responder(0, "T2")))
    result = agg.aggregate(rubric, scores)
    assert result["verdict"] == "PASS"                 # no severity → safe


def test_clinical_two_judges_converge():
    rubric = evl_schema.load_and_validate(_path("clinical-risk-safety"))
    crit = _all_criteria(rubric)[0]
    evidence = [{"text": "e", "source": "x.md:1", "tier": "T2", "section": "s", "character": "x"}]
    judges = [judge_criterion(crit, evidence, FakeLLMClient(_fixed_responder(5, "T2")),
                              scale=rubric["scale"]) for _ in range(2)]
    res = conv.converge(judges, scale=rubric["scale"])
    assert res["converged"] is True and res["score"] == pytest.approx(5.0)


# --- dyad end-to-end on a real pair -----------------------------------------

@pytest.mark.usefixtures("patch_platform_paths")
def test_dyad_scores_a_real_pair():
    rubric = evl_schema.load_and_validate(_path("relationship-compatibility"))
    assert rubric["subject"] == "dyad"
    evidence = ev.gather_for_dyad(("test-alpha", "test-beta"), rubric)
    assert any(evidence[c["id"]] for c in _all_criteria(rubric)), "should gather from the pair"
    scores = judge_rubric(rubric, evidence, FakeLLMClient(_fixed_responder(4, "T3")))
    result = agg.aggregate(rubric, scores)
    assert result["verdict"] == "Highly-Compatible"    # overall 4.0 → top band
