"""Multi-judge convergence math for high-stakes rubrics (deterministic, stateless).

>=2 input-isolated judges score the same criterion; this decides whether they
agree well enough to form a consensus. Convergence requires BOTH verdict agreement
(>= threshold share on the modal verdict) AND bounded score spread (within a
fraction of the scale). Anything less returns DIVERGED + manual_review_required —
the engine never silently averages a real disagreement into a fabricated number.

The skill spawns the judges input-isolated (no judge sees another's verdict); this
layer only does the arithmetic on the collected verdicts.
"""
import statistics
from collections import Counter

from platform_lib.evl_aggregate import VALID_TIERS

DIVERGED = "DIVERGED"
_DEFAULT_THRESHOLD = 0.8       # share of judges that must share the modal verdict
_SPREAD_FRACTION = 0.2         # max score spread as a fraction of the scale range


def required_judges(rubric: dict) -> int:
    """Judges this rubric requires: its min_judges, floored at 2 when high_stakes."""
    n = rubric.get("min_judges", 1)
    return max(n, 2) if rubric.get("high_stakes") else n


def _scores(verdicts: list) -> list:
    return [v["score"] for v in verdicts
            if isinstance(v.get("score"), (int, float)) and not isinstance(v.get("score"), bool)]


def agreement(verdicts: list) -> dict:
    """{n, modal_verdict, pct, spread} across N judges of one criterion."""
    n = len(verdicts)
    tokens = [v.get("verdict") for v in verdicts]
    modal, count = Counter(tokens).most_common(1)[0] if tokens else (None, 0)
    scores = _scores(verdicts)
    spread = (max(scores) - min(scores)) if scores else None
    return {"n": n, "modal_verdict": modal, "pct": (count / n) if n else 0.0, "spread": spread}


def converge(verdicts: list, scale: dict = None, threshold: float = _DEFAULT_THRESHOLD) -> dict:
    """Consensus CriterionScore when judges agree; else DIVERGED + manual_review_required."""
    a = agreement(verdicts)
    scores = _scores(verdicts)
    max_spread = _SPREAD_FRACTION * (scale["max"] - scale["min"]) if scale else None
    spread_ok = a["spread"] is None or max_spread is None or a["spread"] <= max_spread + 1e-9
    # Every judge must have contributed a numeric score — a consensus resting on one
    # verified judge while another abstained defeats the multi-judge guarantee.
    all_scored = len(scores) == a["n"]
    if a["n"] >= 2 and all_scored and a["pct"] >= threshold and spread_ok:
        citations = [v["citation"] for v in verdicts if v.get("citation")]
        tiers = [v["tier"] for v in verdicts if v.get("tier") in VALID_TIERS]
        return {
            "converged": True,
            "verdict": a["modal_verdict"],
            "score": statistics.median(scores) if scores else None,
            "citation": "; ".join(dict.fromkeys(citations)),       # merged, de-duped, ordered
            "tier": min(tiers, key=lambda t: int(t[1:])) if tiers else None,  # strongest
            "justification": f"consensus of {a['n']} judges",
            "judges": a["n"],
            "agreement": a,
        }
    return {
        "converged": False,
        "verdict": DIVERGED,
        "manual_review_required": True,
        "agreement": a,
        "candidates": verdicts,
    }


def cohen_kappa(labels_a: list, labels_b: list) -> float | None:
    """Two-rater agreement on paired categorical labels, chance-corrected.

    Returns None when undefined (mismatched/empty input, or no spread in either
    rater so chance agreement is total) — never a misleading 0.0 or 1.0.
    """
    n = len(labels_a)
    if n == 0 or n != len(labels_b):
        return None
    po = sum(1 for x, y in zip(labels_a, labels_b) if x == y) / n
    cats = set(labels_a) | set(labels_b)
    ca, cb = Counter(labels_a), Counter(labels_b)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe >= 1.0:
        return None
    return (po - pe) / (1 - pe)
