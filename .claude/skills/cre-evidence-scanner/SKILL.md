---
name: cre:evidence-scanner
description: "Standalone, re-runnable evidence-tier safety gate for any content draft. Extracts atomic claims, maps each to its MAT evidence tier (T1-T5), detects Rule-09 privacy/clinical leaks, and adjudicates a per-claim PASS/WARN/FAIL verdict. Invoked by cre:post-writer Phase 6 and runnable on any published asset. Triggers: 'evidence check', 'evidence scan', 'tier compliance', 'check claims', 'evidence gate', 'verify claims'."
argument-hint: "--asset <dir> [--character <slug>] [--json] [--strict]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "cre-framework"
  position: "validation"
  dependencies: []
---

# cre:evidence-scanner — Per-Claim Evidence-Tier Gate

Turn the manual `cre:post-writer` Phase 6 "Evidence alignment" step into a
first-class, re-runnable gate that can audit **any** `assets/{platform}/{slug}/`
draft — not just freshly generated ones. Composable into `cre:repurpose`,
`cre:multiplatform` (Batch 7), and `orc:santa` CRE review.

## Determinism Split (GOLDEN RULE #4)

| Layer      | Owner                             | Does                                                                                                                                                                      |
| ---------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Extract    | `extract-claims-from-draft.py`    | Segment draft → atomic claims (VN-aware) + line/span. Deterministic.                                                                                                      |
| Gather     | `map-claims-to-evidence-tiers.py` | OVER-GATHER candidate materials per claim by keyword/entity overlap; attach tier + confidentiality; detect Rule-09 leaks; FAIL-CLOSED preliminary verdict. Deterministic. |
| Adjudicate | **LLM**                           | Decide whether a candidate material _actually supports_ the claim (CiteAudit Reasoner+Judge). Finalize PASS/WARN/FAIL. Heuristic.                                         |

Scripts may over-flag (false positives expected) — better to over-gather than
miss an unsupported claim. The LLM prunes candidates that don't support the claim.

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
SK=.claude/skills/cre-evidence-scanner/scripts

# 1. (optional) inspect extracted claims
$PY $SK/extract-claims-from-draft.py assets/facebook/260413-slug --json

# 2. run the gate (extracts internally) — exit 1 on any FAIL
$PY $SK/map-claims-to-evidence-tiers.py assets/facebook/260413-slug --json
$PY $SK/map-claims-to-evidence-tiers.py assets/facebook/260413-slug --strict   # T3→FAIL
```

## Verdict Policy (FAIL-CLOSED)

| Condition                                                                                    | Verdict                                            |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Backing material T1 / T2 (Primary / Secondary)                                               | PASS                                               |
| Backing material T3 (Tertiary)                                                               | WARN (needs qualification) — FAIL under `--strict` |
| Backing material T4 / T5 (Contextual / Auxiliary)                                            | FAIL (not publishable)                             |
| Candidate material is `private` / `restricted` confidentiality                               | WARN (downgraded from PASS)                        |
| No candidate evidence detected for claim                                                     | WARN — **never silent PASS** (red-team R1)         |
| Rule-09 leak in claim: `[PRIVATE]` / `[CONFIDENTIAL: x]` / `[ANONYMIZE]` / raw clinical term | FAIL                                               |
| Unknown / missing `source_category`                                                          | T5 → FAIL (fail-closed)                            |

Overall draft verdict = worst per-claim verdict (FAIL > WARN > PASS). Any FAIL → exit 1.

## Rule-09 Leak Detection

Scans each claim for privacy tags (`platform_lib.markdown_parser.extract_tags`)
and raw clinical terms (`platform_lib.clinical_terms.COMPILED_PATTERNS`). A leak
is a hard FAIL regardless of evidence tier — public content must not reference
`[CONFIDENTIAL: {person}]` material or expose raw DSM/ICD/clinical vocabulary
(Rule 02 show-don't-tell, Rule 09 confidentiality).

## Events

On completion emits **`CRE.evidence-checked`** → `content-events.jsonl`
(via `orc:event-log`). On a FAIL caused by a Rule-09 leak, ALSO emit
**`COM.governance`** → `governance-audit.jsonl` (red-team Phase-3 add):

```bash
$PY .claude/skills/orc-event-log/scripts/append-event-to-log.py \
  --event-type CRE.evidence-checked --source cre:evidence-scanner \
  --character <slug> --reason "verdict=<overall> claims=<n>"
# if FAIL-by-leak:
$PY .../append-event-to-log.py --event-type COM.governance \
  --source cre:evidence-scanner --reason "rule09 leak blocked publish"
```

## Single Source of Truth

`TIER_PERMISSIONS` + verdict mapping live in
`.claude/scripts/platform_lib/evidence_tier_permissions.py` — imported by both
this skill and `cre:post-writer`. There is **no** duplicate tier logic
(the old `cre-post-writer/scripts/check-evidence-tier-compliance-in-draft.py`
was relocated here and deleted — red-team R4).

## See Also

- `cre:post-writer` — Phase 6 delegates to this scanner (no duplicate logic).
- `cre:privacy-guard` — asset-wide PII/tag scan (complementary; this is per-claim tier).
- `cre:repurpose` / `cre:multiplatform` (Batch 7) — re-run the gate per variant.
- `orc:santa` — CRE dual-review can invoke this as a pre-check.
- Rule 14 (`cre-evidence-and-events`) — evidence-tier permissions + CRE events.
