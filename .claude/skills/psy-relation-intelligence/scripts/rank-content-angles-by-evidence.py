"""Rank LLM-synthesized content angles by evidence + consent (deterministic scoring).

GOLDEN RULE #4 split:
  - LLM (upstream): reads dyad facts (extract-dyad-relationship-facts.py) and
    SYNTHESIZES candidate angles — title, hook, primary_character, which fact_ids
    back it, narrative coherence + publishability judgments. Heuristic.
  - SCRIPT (here): combine the LLM's numeric judgments with deterministic
    evidence-tier strength + consent propagation into a final score + ranking.
    No reasoning, just arithmetic. Deterministic.

Consent propagation (OQ#6 A): an angle inherits BLOCKED if it cites ANY fact
whose consent_status is BLOCKED (crisis/self-harm or Rule-09 tag). BLOCKED angles
are kept (transparency) but sink to the bottom and flagged — never silently dropped.

Score = evidence_strength × coherence × publishability × consent_factor.

Angle input schema (JSON list), each:
  {title, hook, primary_character, supporting_fact_ids:[...], evidence_tier?,
   consent_status?, coherence:0-1, publishability:0-1, emotional_register?, platform_fit?[]}

Usage:
  rank-content-angles-by-evidence.py --angles angles.json [--facts facts.json] [--json]
READ-ONLY.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

# evidence tier (1-5) → strength weight; None/unknown → weak-but-not-zero
_TIER_STRENGTH = {1: 1.0, 2: 0.85, 3: 0.55, 4: 0.25, 5: 0.15}
_NO_EVIDENCE_STRENGTH = 0.3
_CONSENT_FACTOR = {"OK": 1.0, "REVIEW": 0.5, "BLOCKED": 0.05}


def _evidence_strength(tier) -> float:
    if tier is None:
        return _NO_EVIDENCE_STRENGTH
    return _TIER_STRENGTH.get(int(tier), 0.15)


def resolve_from_facts(angle: dict, facts_by_id: dict) -> tuple:
    """Derive best evidence tier + worst consent from the angle's cited facts."""
    ids = angle.get("supporting_fact_ids") or []
    cited = [facts_by_id[i] for i in ids if i in facts_by_id]
    if not cited:
        return angle.get("evidence_tier"), angle.get("consent_status", "OK")
    tiers = [f["evidence_tier"] for f in cited if f.get("evidence_tier") is not None]
    best_tier = min(tiers) if tiers else angle.get("evidence_tier")
    # worst consent wins (BLOCKED > REVIEW > OK)
    order = {"BLOCKED": 2, "REVIEW": 1, "OK": 0}
    worst = max((f.get("consent_status", "OK") for f in cited), key=lambda c: order.get(c, 0))
    return best_tier, worst


def score_angle(angle: dict, facts_by_id: dict) -> dict:
    tier, consent = resolve_from_facts(angle, facts_by_id)
    coherence = float(angle.get("coherence", 0.5))
    publishability = float(angle.get("publishability", 0.5))
    strength = _evidence_strength(tier)
    consent_factor = _CONSENT_FACTOR.get(consent, 0.05)
    score = round(strength * coherence * publishability * consent_factor, 4)
    return {
        **angle,
        "evidence_tier": f"T{tier}" if tier else "—",
        "consent_status": consent,
        "score": score,
        "publishable": consent != "BLOCKED" and score >= 0.15,
    }


def rank(angles: list[dict], facts: list[dict]) -> list[dict]:
    facts_by_id = {f["fact_id"]: f for f in facts if "fact_id" in f}
    scored = [score_angle(a, facts_by_id) for a in angles]
    # BLOCKED sink to bottom regardless of score; then by score desc
    return sorted(scored, key=lambda a: (a["consent_status"] == "BLOCKED", -a["score"]))


def main():
    ap = argparse.ArgumentParser(description="Rank content angles by evidence + consent.")
    ap.add_argument("--angles", required=True, help="JSON file of LLM-synthesized angles")
    ap.add_argument("--facts", help="JSON file from extract-dyad-relationship-facts.py")
    ap.add_argument("--json", action="store_true", help="JSON output")
    args = ap.parse_args()

    angles = json.loads(Path(args.angles).read_text(encoding="utf-8"))
    if isinstance(angles, dict):
        angles = angles.get("angles", [])
    facts = []
    if args.facts:
        fdata = json.loads(Path(args.facts).read_text(encoding="utf-8"))
        facts = fdata.get("facts", fdata) if isinstance(fdata, dict) else fdata

    ranked = rank(angles, facts)
    out = {"angle_count": len(ranked), "ranked_angles": ranked}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for i, a in enumerate(ranked, 1):
            flag = " ⛔BLOCKED" if a["consent_status"] == "BLOCKED" else (
                "  ✓" if a["publishable"] else "  ~")
            print(f"{i:>2}. [{a['score']:.3f}] {a['evidence_tier']:>3} {flag}  "
                  f"{a.get('title','(untitled)')[:60]}  →{a.get('primary_character','?')}")


if __name__ == "__main__":
    main()
