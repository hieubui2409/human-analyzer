"""Deterministic weighted aggregation + verdict band mapping (no LLM, no IO).

The honesty boundary lives here. Each per-criterion score arrives from the LLM
judge as {criterion_id, score, citation, tier, justification}. A score counts
toward the roll-up ONLY when it is verified: a present citation AND a real
evidence tier (T1-T5) AND a tier at least as strong as the criterion's min_tier.
Everything else is excluded from the math and recorded in a loud list
(`unverified` or `below_min_tier`) — never silently zeroed, never a silent pass.

Roll-up re-normalizes over the verified subset so partial coverage degrades the
score's confidence (reported as coverage), not its scale.
"""
from platform_lib.materials_classifier import EVIDENCE_TIERS

# Tier identity is owned by materials_classifier; EVL cites the string form "T1".."T5".
VALID_TIERS = {f"T{k}" for k in EVIDENCE_TIERS}


def _tier_num(tier) -> int | None:
    """Numeric strength of a tier string ('T1'→1, strongest). None if not a real tier."""
    return int(tier[1:]) if tier in VALID_TIERS else None


def _classify(score: dict, min_tier: str) -> str:
    """verified | unverified | below_min_tier for one criterion score."""
    n = _tier_num(score.get("tier"))
    if not score.get("citation") or n is None:
        return "unverified"
    floor = _tier_num(min_tier)
    if floor is not None and n > floor:  # higher number = weaker than the required floor
        return "below_min_tier"
    return "verified"


def _roll_up(weighted_pairs, total_weight, mode) -> float:
    """weighted_pairs = [(weight, value)]. mean re-normalizes by covered weight;
    sum returns the raw weighted total (caller chose to forgo scale-normalization)."""
    num = sum(w * v for w, v in weighted_pairs)
    if mode == "weighted_sum":
        return num
    covered = sum(w for w, _ in weighted_pairs)
    return num / covered if covered else None


def aggregate(rubric: dict, scores: list[dict]) -> dict:
    """Roll per-criterion scores → domain → overall. Pure + idempotent."""
    mode = rubric.get("aggregate", "weighted_mean")
    by_id = {s["criterion_id"]: s for s in scores}
    unverified: list[str] = []
    below: list[str] = []
    verified_n = total_n = 0

    domain_results = []
    scored_domains = []  # (domain_weight, domain_score)
    for d in rubric["domains"]:
        pairs = []
        dom_total_w = sum(c["weight"] for c in d["criteria"])
        for c in d["criteria"]:
            total_n += 1
            s = by_id.get(c["id"])
            status = _classify(s, c.get("min_tier", "T5")) if s else "unverified"
            if status == "verified":
                verified_n += 1
                pairs.append((c["weight"], s["score"]))
            elif status == "below_min_tier":
                below.append(c["id"])
            else:
                unverified.append(c["id"])
        dom_score = _roll_up(pairs, dom_total_w, mode) if pairs else None
        covered_w = sum(w for w, _ in pairs)
        domain_results.append({
            "id": d["id"], "weight": d["weight"], "score": dom_score,
            "coverage": covered_w / dom_total_w if dom_total_w else 0.0,
        })
        if dom_score is not None:
            scored_domains.append((d["weight"], dom_score))

    overall = _roll_up(scored_domains, 1.0, mode) if scored_domains else None
    return {
        "rubric_id": rubric.get("id"),
        "overall": overall,
        "verdict": verdict_for_score(rubric, overall),
        "domains": domain_results,
        "unverified": unverified,
        "below_min_tier": below,
        "verified_coverage": verified_n / total_n if total_n else 0.0,
    }


def coverage(result: dict) -> float:
    """Fraction of criteria that were verified (the trustworthy share of the score)."""
    return result.get("verified_coverage", 0.0)


def verdict_for_score(rubric: dict, overall) -> str | None:
    """Map an overall score to its verdict band. None for scalar verdicts or a
    None score. Bands are lower-inclusive; the scale max falls in the top band."""
    if overall is None or rubric.get("verdict") == "scalar":
        return None
    bands = rubric.get("verdict_thresholds") or {}
    smax = rubric["scale"]["max"]
    ordered = sorted(bands.items(), key=lambda kv: kv[1]["min"])
    for label, band in ordered:
        if band["min"] <= overall < band["max"]:
            return label
    # max value lands on the closed upper edge of the top band
    if ordered and overall == smax:
        return ordered[-1][0]
    return None
