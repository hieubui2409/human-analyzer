"""Evidence-tier publish permissions — single source of truth for gate verdicts.

Maps a MAT evidence tier (T1-T5) to a publish permission + a draft-gate verdict.
Imported by cre:evidence-scanner (standalone gate) and cre:post-writer (Phase 6).

Tier identity (names/descriptions) is owned by materials_classifier.EVIDENCE_TIERS.
This module only owns the permission/gate mapping for those tiers.

Tier → gate policy:
  T1 Primary / T2 Secondary  → yes      → PASS  (publishable)
  T3 Tertiary                → qualified → WARN  (publishable WITH qualification)
  T4 Contextual              → restricted → FAIL  (restricted: not publishable without
                                                   explicit editorial approval; distinct
                                                   from T5 in that restricted use is a
                                                   documented editorial decision, not a
                                                   blanket prohibition)
  T5 Auxiliary               → no        → FAIL  (not publishable — inference/metadata only)

Gate policy is FAIL-CLOSED: only T1/T2 PASS outright; T3 warns; T4/T5 fail.
A Rule-09 privacy leak in the claim text overrides tier and always FAILs.
"""
# LIB-07: Tier IDENTITY (T1-T5 names) lives in materials_classifier.EVIDENCE_TIERS.
# This module owns only the permission/verdict mapping for those tiers.
from platform_lib.materials_classifier import EVIDENCE_TIERS as _EVIDENCE_TIERS  # noqa: F401 (re-exported for callers)

# tier -> {permission, label}
TIER_PERMISSIONS = {
    1: {"permission": "yes", "label": "Publishable"},
    2: {"permission": "yes", "label": "Publishable"},
    3: {"permission": "qualified", "label": "With qualification"},
    4: {"permission": "restricted", "label": "Restricted use"},
    5: {"permission": "no", "label": "Not publishable"},
}

# permission -> default draft-gate verdict (non-strict mode)
PERMISSION_TO_VERDICT = {
    "yes": "PASS",
    "qualified": "WARN",
    "restricted": "FAIL",
    "no": "FAIL",
}

# In --strict mode, qualified (T3) is also rejected.
STRICT_OVERRIDES = {"qualified": "FAIL"}

# Verdict when a claim has NO candidate evidence at all.
# Never silent PASS (FAIL-CLOSED) — force a human/LLM look.
NO_EVIDENCE_VERDICT = "WARN"

VERDICT_ICON = {"PASS": "✓", "WARN": "~", "FAIL": "✗"}


def tier_permission(tier: int) -> dict:
    """Return {permission, label} for a tier; unknown tier → T5 (fail-closed)."""
    return TIER_PERMISSIONS.get(tier, TIER_PERMISSIONS[5])


def verdict_for_tier(tier: int, strict: bool = False) -> str:
    """Map a tier to a PASS/WARN/FAIL gate verdict. Fail-closed on unknown tier."""
    perm = tier_permission(tier)["permission"]
    if strict and perm in STRICT_OVERRIDES:
        return STRICT_OVERRIDES[perm]
    return PERMISSION_TO_VERDICT.get(perm, "FAIL")


def worst_verdict(verdicts) -> str:
    """Collapse many per-claim verdicts to one draft verdict (FAIL > WARN > PASS)."""
    order = {"FAIL": 2, "WARN": 1, "PASS": 0}
    if not verdicts:
        return "WARN"
    return max(verdicts, key=lambda v: order.get(v, 2))
