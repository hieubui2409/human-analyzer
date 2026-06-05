"""Rank LLM-synthesized content angles by freshness × evidence × platform fit.

GOLDEN RULE #4 split:
  - LLM (upstream): reads raw signals (aggregate-angle-signals-across-frameworks.py)
    and SYNTHESIZES candidate angles — title, hook, source_framework, which
    signal feeds it, evidence_tier, platform_fit, freshness carried from the signal.
    Heuristic framing.
  - SCRIPT (here): combine those numeric attributes into a weighted score + ranking.
    Pure arithmetic + consent propagation. Deterministic.

Score = w_fresh·freshness + w_evid·evidence_strength + w_fit·platform_fit,
        then × consent_factor (BLOCKED sinks to the bottom, never dropped — B9 rule).

Angle input schema (JSON list), each:
  {title, hook, source_framework, primary_character, evidence_tier?(1-5),
   freshness?(0-1), platform_fit?[...], consent_status?(OK|REVIEW|BLOCKED)}

Usage:
  rank-angles-by-freshness-and-evidence.py --angles angles.json [--top N] [--json]
READ-ONLY.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.angle_scoring import (
    TIER_STRENGTH, evidence_strength as _evidence_strength, consent_factor as _consent_factor,
)

# weights (sum 1.0) — freshness leads (proactive/timely), evidence second
W_FRESH, W_EVID, W_FIT = 0.45, 0.40, 0.15


def _platform_fit(angle: dict) -> float:
    """More native platforms an angle fits → higher reach potential (capped)."""
    fit = angle.get("platform_fit") or []
    if not isinstance(fit, list):
        return 0.5
    return min(1.0, len(fit) / 3.0) if fit else 0.4


def score_angle(angle: dict) -> dict:
    fresh = float(angle.get("freshness", 0.5))
    evid = _evidence_strength(angle.get("evidence_tier"))
    fit = _platform_fit(angle)
    consent = angle.get("consent_status", "OK")
    base = W_FRESH * fresh + W_EVID * evid + W_FIT * fit
    score = round(base * _consent_factor(consent), 4)
    tier = angle.get("evidence_tier")
    return {
        **angle,
        "evidence_tier": f"T{int(tier)}" if str(tier).strip().isdigit() else "—",
        "consent_status": consent,
        "score": score,
        "speculative": evid <= TIER_STRENGTH[4],  # T4/T5-only → flagged
        "publishable": consent != "BLOCKED" and score >= 0.15,
    }


def rank(angles: list[dict]) -> list[dict]:
    scored = [score_angle(a) for a in angles]
    return sorted(scored, key=lambda a: (a["consent_status"] == "BLOCKED", -a["score"]))


def main():
    ap = argparse.ArgumentParser(description="Rank angles by freshness × evidence × fit.")
    ap.add_argument("--angles", required=True, help="JSON file of LLM-synthesized angles")
    ap.add_argument("--top", type=int, default=0, help="Keep only top N (0 = all)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = json.loads(Path(args.angles).read_text(encoding="utf-8"))
    angles = data.get("angles", data) if isinstance(data, dict) else data
    ranked = rank(angles)
    if args.top > 0:
        ranked = ranked[: args.top]

    out = {"angle_count": len(ranked), "ranked_angles": ranked}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for i, a in enumerate(ranked, 1):
            flag = " ⛔BLOCKED" if a["consent_status"] == "BLOCKED" else (
                " ~spec" if a["speculative"] else "  ✓")
            print(f"{i:>2}. [{a['score']:.3f}] {a['evidence_tier']:>3}{flag}  "
                  f"{a.get('source_framework','?'):>3}  {a.get('title','(untitled)')[:54]}")


if __name__ == "__main__":
    main()
