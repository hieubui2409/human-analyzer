"""Deterministic scorecard validation runner (no LLM) — the structural honesty gate.

A checker registry re-proves a finished scorecard against its rubric: schema valid,
every id mapped, every scored criterion cited, weights unity, aggregate math
reproducible, scores in bounds, verdict bands cover the scale. Statuses are
PASS | FAIL | SKIP | UNMAPPED. UNMAPPED (a criterion id the rubric doesn't define)
is loud but non-fatal unless strict; an unknown checker name is FAIL — a
misconfigured gate is never a silent pass.
"""
from platform_lib import evl_aggregate as agg
from platform_lib import evl_schema
from platform_lib.evl_aggregate import VALID_TIERS


def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _close(a, b, tol=1e-6) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol


def _rubric_schema_valid(sc, rubric):
    errs = evl_schema.validate_rubric(rubric)
    return ("FAIL", "; ".join(errs)) if errs else ("PASS", "")


def _criteria_mapped(sc, rubric):
    rubric_ids = {c["id"] for d in rubric["domains"] for c in d["criteria"]}
    sc_ids = {c.get("criterion_id") for c in sc.get("criteria", [])}
    extra, missing = sc_ids - rubric_ids, rubric_ids - sc_ids
    if extra or missing:
        return ("UNMAPPED", f"extra={sorted(extra)} missing={sorted(missing)}")
    return ("PASS", "")


def _every_criterion_cited(sc, rubric):
    bad = [c.get("criterion_id") for c in sc.get("criteria", [])
           if _num(c.get("score")) is not None
           and not (c.get("citation") and c.get("tier") in VALID_TIERS)]
    return ("FAIL", f"scored but uncited: {bad}") if bad else ("PASS", "")


def _weight_sum_unity(sc, rubric):
    errs = []
    dsum = sum(d["weight"] for d in rubric["domains"])
    if abs(dsum - 1.0) > 1e-6:
        errs.append(f"domains sum {dsum:g}")
    for d in rubric["domains"]:
        csum = sum(c["weight"] for c in d["criteria"])
        if abs(csum - 1.0) > 1e-6:
            errs.append(f"domain {d['id']} sum {csum:g}")
    return ("FAIL", "; ".join(errs)) if errs else ("PASS", "")


def _aggregate_math_correct(sc, rubric):
    rec = agg.aggregate(rubric, sc.get("criteria", []))
    bad = [] if _close(rec["overall"], sc.get("overall")) else ["overall"]
    sc_doms = {d["id"]: d.get("score") for d in sc.get("domains", [])}
    bad += [f"domain {d['id']}" for d in rec["domains"] if not _close(d["score"], sc_doms.get(d["id"]))]
    return ("FAIL", f"mismatch: {bad}") if bad else ("PASS", "")


def _score_in_bounds(sc, rubric):
    lo, hi = rubric["scale"]["min"], rubric["scale"]["max"]
    bad = [c.get("criterion_id") for c in sc.get("criteria", [])
           if _num(c.get("score")) is not None and not (lo <= c["score"] <= hi)]
    ov = _num(sc.get("overall"))
    if ov is not None and not (lo <= ov <= hi):
        bad.append("overall")
    return ("FAIL", f"out of [{lo},{hi}]: {bad}") if bad else ("PASS", "")


def _verdict_thresholds_cover_range(sc, rubric):
    if rubric.get("verdict") == "scalar":
        return ("SKIP", "scalar verdict has no bands")
    errs = evl_schema._threshold_errors(rubric, rubric["scale"]["min"], rubric["scale"]["max"])
    return ("FAIL", "; ".join(errs)) if errs else ("PASS", "")


def _verdict_matches_band(sc, rubric):
    """The stored verdict must equal the band the (recomputed) overall maps to — a
    tampered or stale verdict (e.g. a clinical BLOCKED downgraded to PASS) is a FAIL,
    not a silent pass. Re-derives from the rubric, never trusts the stored label."""
    if rubric.get("verdict") == "scalar":
        return ("SKIP", "scalar verdict has no band")
    expected = agg.verdict_for_score(rubric, sc.get("overall"))
    actual = sc.get("verdict")
    if expected == actual:
        return ("PASS", "")
    return ("FAIL", f"stored verdict {actual!r} != band {expected!r} for overall {sc.get('overall')}")


def _red_flags_assessed(sc, rubric):
    """A safety red_flag can only clear on evidence. If any red_flags criterion is
    UNVERIFIED or below its min_tier, the veto could not be evaluated → fail closed.
    This DETECTS the gap deterministically; the veto judgment itself stays with the LLM."""
    flags = rubric.get("red_flags") or []
    if not flags:
        return ("SKIP", "no red_flags declared")
    unresolved = [f for f in flags
                  if f in sc.get("unverified", []) or f in sc.get("below_min_tier", [])]
    if unresolved:
        return ("FAIL", f"safety red_flags not assessed on evidence: {unresolved}")
    return ("PASS", "")


# Registry order is the report order.
CHECKERS = {
    "rubric_schema_valid": _rubric_schema_valid,
    "criteria_mapped": _criteria_mapped,
    "every_criterion_cited": _every_criterion_cited,
    "weight_sum_unity": _weight_sum_unity,
    "aggregate_math_correct": _aggregate_math_correct,
    "score_in_bounds": _score_in_bounds,
    "verdict_thresholds_cover_range": _verdict_thresholds_cover_range,
    "verdict_matches_band": _verdict_matches_band,
    "red_flags_assessed": _red_flags_assessed,
}


def run_structural(scorecard: dict, rubric: dict, strict: bool = False, checks=None):
    """Run the checker registry over a scorecard. Returns (verdict, rows).

    rows = [{check, status, detail}]; verdict is FAIL on any FAIL (or any UNMAPPED
    under strict), else PASS. An unknown checker name is itself a FAIL row.
    """
    names = checks if checks is not None else list(CHECKERS)
    rows = []
    for name in names:
        fn = CHECKERS.get(name)
        if fn is None:
            rows.append({"check": name, "status": "FAIL", "detail": "unknown checker"})
            continue
        status, detail = fn(scorecard, rubric)
        rows.append({"check": name, "status": status, "detail": detail})
    statuses = {r["status"] for r in rows}
    verdict = "FAIL" if ("FAIL" in statuses or (strict and "UNMAPPED" in statuses)) else "PASS"
    return verdict, rows
