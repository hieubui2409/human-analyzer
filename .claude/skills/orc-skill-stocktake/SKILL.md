---
name: orc:skill-stocktake
description: "Audit the project skill catalog — Quick Scan (counts per framework vs CLAUDE.md, frontmatter-metadata gaps, catalog drift) + Full Stocktake (pairwise description/trigger overlap candidates, usage signal, gap detection) in the proven 260523 KEEP/ENHANCE/CONSOLIDATE/RETIRE verdict format. Distinct from orc:audit (which audits events, not the skill catalog). READ-ONLY. Use when skills are added/renamed, periodically to catch catalog drift + bloat, or before a release. Triggers: 'skill stocktake', 'skill audit', 'catalog audit', 'skill overlap', 'are skills duplicated', 'skill necessity', 'count skills'."
argument-hint: "[--quick | --full] [--framework orc|psy|cre|gro|mat|com] [--report] [--min-overlap N]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "orc-framework"
  position: "maintenance"
  dependencies: []
---

# orc:skill-stocktake — Skill Catalog Audit

Automates the once-manual skill necessity audit (the hand-written `audit-260523-…` report).
Two modes: **Quick Scan** (fast count + metadata + CLAUDE.md reconciliation) and **Full
Stocktake** (overlap/gap/usage gather → LLM verdict). Its first run audits its own arrival
plus the Batch 6-7 growth (angle trio, content pair).

## When to Use

- After adding, renaming, or retiring a skill (catch count drift vs CLAUDE.md early).
- Periodically (quarterly) to detect overlap/bloat before it compounds.
- Before a release or a stocktake-style review.
- NOT for event-consistency auditing — that is `orc:audit` (different concern).

## Determinism Split (GOLDEN RULE #4)

| Layer    | Owner                                   | Does                                                                                                                  |
| -------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Gather   | `scan-skill-catalog-metadata.py`        | Count project skills per framework, parse frontmatter completeness, reconcile vs CLAUDE.md tables + total. Deterministic. |
| Gather   | `analyze-skill-overlap-and-gaps.py`     | Pairwise description/trigger Jaccard (over-gather candidates) + usage signal (event mentions, git recency, NEW-guard). Deterministic. |
| Adjudicate | **LLM**                               | Decide duplicate (CONSOLIDATE) vs complementary (KEEP), gap severity, keep/enhance/retire. Heuristic.                 |

Scripts OVER-GATHER overlap candidates — high token overlap ≠ duplication. The LLM applies
the **"complementary ≠ duplicate"** rule (the trap the 260523 audit avoided: e.g.
`psy:ref-audit`/`psy:ref-scan` are reverse directions, NOT duplicates).

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
SK=.claude/skills/orc-skill-stocktake/scripts

# Quick Scan — counts, metadata gaps, CLAUDE.md drift
$PY $SK/scan-skill-catalog-metadata.py --json

# Full Stocktake — overlap candidates + usage signal (feed to LLM for verdicts)
$PY $SK/analyze-skill-overlap-and-gaps.py --min-overlap 0.30 --json
```

## Verdict Format (260523 report)

LLM assigns each skill / pair one verdict, in the proven distribution format:

| Verdict         | Meaning                                                       |
| --------------- | ------------------------------------------------------------- |
| **KEEP**        | Distinct purpose, no action needed                            |
| **ENHANCE**     | Useful but metadata/description gaps to fix (additive)        |
| **CONSOLIDATE** | Genuine duplicate of another skill → merge (recommendation)   |
| **RETIRE**      | No distinct purpose AND not new → remove (recommendation)     |

RETIRE/CONSOLIDATE are **recommendations only — never auto-executed**.

## Red-Team R-cross — New-Skill Guard

A freshly-created skill has no event history yet. **"No usage" ≠ "unused."** Skills with
< 3 commits touching them are tagged `NEW` and their usage signal is marked not-meaningful
— they are never recommended for RETIRE. Overlap is the only signal that applies to new skills.

## First-Run Checklist (Batches 6-7-9 growth)

Adjudicate the overlaps Batches 6-7 introduced:

- `cre:exploring` (interactive) vs `cre:angle-discovery` (autonomous) vs `psy:relation-intelligence` (relationship source) → KEEP all (complementary; documented boundaries).
- `cre:repurpose` (1→1 adapt) vs `cre:multiplatform` (1→N native) → KEEP both (distinct ops, shared lib).
- `psy:crossref` (validation) / `psy:propagate` (cascade) / `psy:relation-intelligence` (angle mining) → KEEP all.

## See Also

- `orc:audit` — event-consistency audit (the catalog↔event split).
- `score-skill-description.py` — description format compliance (Tier 2 of `--conformance`).
- `validate-skill-frontmatter.py` / `validate-skill-crossrefs.py` — frontmatter + cross-ref gates.
- `audit-260523-…skill-necessity-report.md` — the output-format template.
