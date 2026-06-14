"""Cross-character calibration for comparable rubric scores (pure math, no IO).

The same rubric run over different characters yields raw overalls that only become
comparable once placed in a cohort. This emits, per character: raw (always),
z-score (peer-relative — suppressed with a loud note when the cohort is too small
or has no spread, since a z from N<3 or zero variance is noise), and a rank-based
percentile (always defined). Which one a scorecard features is the rubric's
`normalization` choice; the engine never silently fabricates a statistic.
"""
import statistics

MIN_COHORT = 3  # below this, peer-relative z is statistically meaningless


def normalize_method(rubric: dict) -> str:
    """The rubric's chosen primary normalization; defaults to z_score."""
    return rubric.get("normalization") or "z_score"


def normalize_cohort(rubric_id: str, overall_by_char: dict) -> dict:
    """Map {char: raw_overall|None} → {char: {raw, z, percentile, note}}.

    z is None (with a note) when the comparable cohort has <3 members or zero
    variance. Characters with no score (None) pass through inert.
    """
    comparable = {c: v for c, v in overall_by_char.items() if v is not None}
    values = list(comparable.values())

    z_ok, cohort_note = _z_eligibility(values)
    mean = statistics.fmean(values) if values else 0.0
    sd = statistics.pstdev(values) if z_ok else 0.0

    out = {}
    for char, raw in overall_by_char.items():
        if raw is None:
            out[char] = {"raw": None, "z": None, "percentile": None, "note": "no_score"}
            continue
        out[char] = {
            "raw": raw,
            "z": (raw - mean) / sd if z_ok else None,
            "percentile": _percentile(raw, values),
            "note": None if z_ok else cohort_note,
        }
    return out


def _z_eligibility(values: list) -> tuple[bool, str | None]:
    if len(values) < MIN_COHORT:
        return False, f"insufficient_cohort (N={len(values)} < {MIN_COHORT})"
    if statistics.pstdev(values) == 0:
        return False, "zero_variance (all scores identical)"
    return True, None


def _percentile(raw: float, values: list) -> float:
    """Mid-rank percentile: fraction below + half the ties, scaled to 0-100."""
    n = len(values)
    if n == 0:
        return 50.0
    below = sum(1 for v in values if v < raw)
    equal = sum(1 for v in values if v == raw)
    return 100.0 * (below + 0.5 * equal) / n
