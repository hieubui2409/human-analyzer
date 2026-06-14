"""Thin deterministic composition wiring the EVL engine stages for the skill scripts.

The full scoring flow is gather → (LLM judges, done by the skill via the Agent tool) →
aggregate → write. These helpers own only the deterministic ends of that flow so the
skill `run_*.py` wrappers stay tiny and carry no judgment logic. The judge step is NOT
here — it happens in the skill between gather_payload and finalize_scorecard.
"""
from platform_lib.evl_aggregate import aggregate
from platform_lib.evl_evidence import gather_for_dyad, gather_for_rubric
from platform_lib.evl_schema import load_and_validate
from platform_lib.evl_scorecard import write_scorecard


def gather_payload(character: str, rubric_path) -> dict:
    """Evidence bundle for a single-subject rubric — the input the LLM judges score from."""
    rubric = load_and_validate(rubric_path)
    if rubric.get("subject") == "dyad":
        raise ValueError(f"{rubric['id']} is a dyad rubric — use gather_dyad_payload")
    return {
        "rubric_id": rubric["id"],
        "character": character,
        "scale": rubric["scale"],
        "min_judges": rubric.get("min_judges", 1),
        "evidence_by_criterion": gather_for_rubric(character, rubric),
    }


def gather_dyad_payload(pair, rubric_path) -> dict:
    """Evidence bundle for a dyad rubric, pooled from both characters in the pair."""
    rubric = load_and_validate(rubric_path)
    if rubric.get("subject") != "dyad":
        raise ValueError(f"{rubric['id']} is not a dyad rubric — use gather_payload")
    return {
        "rubric_id": rubric["id"],
        "pair": list(pair),
        "scale": rubric["scale"],
        "min_judges": rubric.get("min_judges", 1),
        "evidence_by_criterion": gather_for_dyad(tuple(pair), rubric),
    }


def finalize_scorecard(character: str, rubric_path, scores: list, *, asof: str,
                       judges=None, convergence=None, normalization=None,
                       updated_by: str = "evl:score"):
    """Aggregate collected judge scores and write the scorecard. Returns (path, result)."""
    rubric = load_and_validate(rubric_path)
    result = aggregate(rubric, scores)
    meta = {"character": character, "criteria": scores, "asof": asof,
            "updated_by": updated_by, "judges": judges, "convergence": convergence,
            "normalization": normalization}
    return write_scorecard(character, rubric, result, meta), result


def finalize_dyad_scorecard(pair, rubric_path, scores: list, *, asof: str,
                            judges=None, convergence=None, updated_by: str = "evl:compatibility"):
    """Aggregate a dyad rubric and write the scorecard under the FIRST character's eval/.

    The scorecard id is suffixed with the partner so one character can hold many dyad
    scorecards (one per relationship) without collision.
    """
    rubric = load_and_validate(rubric_path)
    if rubric.get("subject") != "dyad":
        raise ValueError(f"{rubric['id']} is not a dyad rubric")
    a, b = pair
    result = aggregate(rubric, scores)
    paired = {**rubric, "id": f"{rubric['id']}--{b}"}
    meta = {"character": a, "criteria": scores, "asof": asof, "updated_by": updated_by,
            "judges": judges, "convergence": convergence, "pair": [a, b]}
    return write_scorecard(a, paired, result, meta), result
