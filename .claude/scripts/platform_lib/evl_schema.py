"""Canonical EVL rubric loader + validator.

A rubric is a shared, versioned, character-agnostic scoring contract (YAML).
Validation runs in two layers:

  1. Shape — delegated to the one shared Draft-7 engine (schema_validator) against
     evl-rubric.schema.json. Enums, required keys, types, ranges.
  2. Cross-field invariants JSON-Schema cannot express — weight sums, the
     high-stakes judge floor, clinical rails, decision target, verdict-band
     coverage, anchor endpoints. Each yields a precise, loud error string.

Every invalid rubric returns a non-empty error list (or raises from the
load_and_validate convenience). Nothing fails silently: an uncited score is the
caller's concern, but a malformed rubric never scores at all.
"""
from pathlib import Path

import yaml

from platform_lib import schema_validator
from platform_lib.paths import RUBRICS

SCHEMA_NAME = "evl-rubric.schema.json"


class EvlSchemaError(ValueError):
    """Raised by load_and_validate when a rubric fails shape or invariant checks."""


def load_rubric(path) -> dict:
    """Parse a rubric YAML file into a dict. Raises if the body is not a mapping."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise EvlSchemaError(f"{path}: rubric must be a YAML mapping")
    return data


def validate_rubric(rubric: dict) -> list[str]:
    """Return a list of human-readable error strings; [] means valid.

    Shape errors short-circuit the invariant pass: invariants index into the
    rubric structure and assume the shape already holds.
    """
    shape = [
        f"{v['field']}: {v['message']}"
        for v in schema_validator.validate_instance(
            rubric, SCHEMA_NAME, label=str(rubric.get("id", "<rubric>"))
        )
    ]
    if shape:
        return shape
    return _invariants(rubric)


def load_and_validate(path) -> dict:
    """Load + validate in one step. Raises EvlSchemaError with all findings."""
    rubric = load_rubric(path)
    errs = validate_rubric(rubric)
    if errs:
        joined = "\n  - ".join(errs)
        raise EvlSchemaError(f"invalid rubric {Path(path).name}:\n  - {joined}")
    return rubric


def list_rubrics(rubrics_dir=RUBRICS) -> list[Path]:
    """Top-level *.yaml rubrics in the library (non-recursive; drafts/imports nest)."""
    return sorted(Path(rubrics_dir).glob("*.yaml"))


# --- cross-field invariants -------------------------------------------------

def _invariants(r: dict) -> list[str]:
    errs: list[str] = []
    smin, smax = r["scale"]["min"], r["scale"]["max"]
    domains = r["domains"]

    dsum = sum(d["weight"] for d in domains)
    if abs(dsum - 1.0) > 1e-6:
        errs.append(f"domain weights must sum to 1.0 (got {dsum:g})")

    for d in domains:
        csum = sum(c["weight"] for c in d["criteria"])
        if abs(csum - 1.0) > 1e-6:
            errs.append(
                f"criterion weights in domain '{d['id']}' must sum to 1.0 (got {csum:g})"
            )
        for c in d["criteria"]:
            errs += _anchor_errors(c, smin, smax)

    if r.get("high_stakes") and r.get("min_judges", 1) < 2:
        errs.append("high_stakes rubric requires min_judges >= 2 (independent judges)")

    if r["kind"] == "clinical":
        if r.get("cache") != "never":
            errs.append("clinical rubric must set cache: never (no stale risk verdicts)")
        if r.get("verdict") != "tri_state":
            errs.append(
                "clinical rubric must use verdict: tri_state (PASS/PASS_WITH_RISK/BLOCKED)"
            )

    if r["kind"] == "decision" and not r.get("target_profile"):
        errs.append("decision rubric requires a target_profile to score fit against")

    if r["verdict"] != "scalar":
        errs += _threshold_errors(r, smin, smax)

    return errs


def _anchor_errors(c: dict, smin, smax) -> list[str]:
    """Anchors must pin both scale endpoints plus at least one interior point so a
    judge is never extrapolating past the rubric's own examples."""
    keys = []
    for k in c.get("anchors", {}):
        try:
            keys.append(float(k))
        except (TypeError, ValueError):
            pass
    if smin not in keys or smax not in keys or not any(smin < v < smax for v in keys):
        return [
            f"criterion '{c['id']}' anchors must include the scale min ({smin}), "
            f"max ({smax}), and at least one mid point"
        ]
    return []


def _threshold_errors(r: dict, smin, smax) -> list[str]:
    """A non-scalar verdict maps a score to a band; the bands must tile the whole
    scale contiguously — no gap (a score with no verdict) and no overlap (two)."""
    bands_raw = r.get("verdict_thresholds")
    if not bands_raw:
        return [f"verdict '{r['verdict']}' requires verdict_thresholds bands"]
    try:
        bands = sorted(
            ((b["min"], b["max"]) for b in bands_raw.values()), key=lambda x: x[0]
        )
    except (KeyError, TypeError, AttributeError):
        return ["verdict_thresholds bands must each have a numeric min and max"]
    if bands[0][0] != smin or bands[-1][1] != smax:
        return [f"verdict_thresholds must cover the full scale [{smin}, {smax}] with no gap"]
    for (_, hi), (lo_next, _) in zip(bands, bands[1:]):
        if hi != lo_next:
            return [
                f"verdict_thresholds have a gap/overlap at {hi:g} "
                "(bands must be contiguous to cover the scale)"
            ]
    return []
