"""Evidence-tier publish permissions — single source of truth.

Maps a MAT evidence tier (T1-T5) to a publish permission + a draft-gate verdict.
Imported by cre:evidence-scanner (standalone gate) and cre:post-writer (Phase 6).

Tier semantics (from materials_classifier.EVIDENCE_TIERS):
  T1 Primary / T2 Secondary  → publishable
  T3 Tertiary                → publishable WITH qualification
  T4 Contextual / T5 Auxiliary → not publishable (hearsay / inference)

Gate policy is FAIL-CLOSED: only T1/T2 PASS outright; T3 warns; T4/T5 fail
(red-team R3: "only T4/T5 hard-fail"). A Rule-09 privacy leak in the claim text
overrides tier and always FAILs, regardless of backing evidence.
"""

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
# Never silent PASS (red-team R1 / FAIL-CLOSED) — force a human/LLM look.
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
