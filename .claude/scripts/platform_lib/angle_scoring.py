"""Shared scoring primitives for content-angle rankers (cre + psy).

Both cre:angle-discovery and psy:relation-intelligence turn LLM-synthesized angles into a
ranked list using the same evidence-tier strength, no-evidence fallback, and consent
propagation. Centralising them here keeps the two rankers from drifting (they previously
held divergent copies) and gives one robust evidence_strength() that never crashes on
empty/garbage tier values.
"""
from __future__ import annotations

# Evidence tier (1-5) → strength weight; unknown/empty → weak-but-not-zero (never silent drop).
TIER_STRENGTH = {1: 1.0, 2: 0.85, 3: 0.55, 4: 0.25, 5: 0.15}
NO_EVIDENCE_STRENGTH = 0.3
UNKNOWN_TIER_STRENGTH = 0.15

# Consent status → score multiplier. BLOCKED is kept (transparency) but sunk to the bottom.
CONSENT_FACTOR = {"OK": 1.0, "REVIEW": 0.5, "BLOCKED": 0.05}
DEFAULT_CONSENT_FACTOR = 0.05


def evidence_strength(tier) -> float:
    """Map a tier (int, numeric str, None, or '') to a strength weight. Never raises."""
    if tier is None or (isinstance(tier, str) and not tier.strip()):
        return NO_EVIDENCE_STRENGTH
    try:
        return TIER_STRENGTH.get(int(tier), UNKNOWN_TIER_STRENGTH)
    except (ValueError, TypeError):
        return NO_EVIDENCE_STRENGTH


def consent_factor(status: str | None) -> float:
    """Score multiplier for a consent status; unknown → most conservative (treat as blocked)."""
    return CONSENT_FACTOR.get(status or "OK", DEFAULT_CONSENT_FACTOR)
