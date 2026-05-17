---
name: mat:indexer
description: "MAT framework indexer — contradiction detection, cross-reference validation, evidence tier verification, and material-to-profile linking. Runs after mat:loader. Triggers: 'index materials', 'cross-reference', 'contradiction check', 'mat index', 'validate materials'."
argument-hint: "[--character <name>|--all|--contradictions|--coverage|--stale]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "mat-framework"
  position: "pipeline-stage-3-4"
  dependencies: ["mat:loader"]
---

# mat:indexer — Material Cross-Reference & Validation (MAT Framework)

Cross-reference materials against profiles, detect contradictions, verify evidence tiers, and track coverage gaps.

## MAT Pipeline Position

```
Stage 1 → Stage 2 → [Stage 3: Validation] → [Stage 4: Integration Gate] → Stage 5
mat:loader            mat:indexer               mat:indexer              (auto)
```

mat:indexer owns Stages 3-4: validation and integration readiness assessment.

## Default (No Arguments)

`--all` — run full cross-reference across all characters.

## Flags

| Flag                 | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `--all`              | Full cross-reference for all characters (default)    |
| `--character <name>` | Cross-reference one character's materials vs profile |
| `--contradictions`   | Show only contradictions (skip coverage/stale)       |
| `--coverage`         | Show evidence coverage gaps per profile section      |
| `--stale`            | Find materials stuck at raw/extracted for >7 days    |

## Workflow: --all / --character `<name>`

### Stage 3: Cross-Reference Validation

For each material file with `processing_status` in [raw, extracted, analyzed]:

1. **Extract claims** — parse material for factual claims about:
   - Events (dates, places, actions)
   - Relationships (who did what to whom)
   - Psychological states (emotions, behaviors, symptoms)
   - Financial/practical details

2. **Match against profiles** — for each claim:
   - Search corresponding profile files (psychology/, timeline/, identity/, etc.)
   - Classify match:

     | Match Type  | Meaning                                            |
     | ----------- | -------------------------------------------------- |
     | CONFIRMS    | Material supports existing profile data            |
     | EXTENDS     | Material adds new detail not in profile            |
     | CONTRADICTS | Material conflicts with profile data               |
     | NOVEL       | Material contains info with no profile counterpart |

3. **Contradiction severity assessment:**

   | Severity | Definition                                         | Action                  |
   | -------- | -------------------------------------------------- | ----------------------- |
   | LOW      | Minor detail difference (dates off by days)        | Log, auto-resolve later |
   | MEDIUM   | Factual disagreement (different event description) | Flag for review         |
   | HIGH     | Core narrative conflict (contradicts key profile)  | STOP — surface to user  |
   | CRITICAL | Safety-relevant (SI risk, crisis level mismatch)   | IMMEDIATE — alert user  |

4. **Evidence tier validation:**
   - Check if material's evidence_tier is appropriate for its source_category
   - Flag over-rated materials (e.g., T1 assigned to hearsay)
   - Suggest tier adjustments

### Stage 4: Integration Gate

For each material ready for integration:

1. **Pre-integration checklist:**
   - [ ] No HIGH/CRITICAL contradictions unresolved
   - [ ] Evidence tier verified
   - [ ] CRAAP score ≥ 15/25
   - [ ] Confidentiality tags applied
   - [ ] Cross-character references identified

2. **If PASS:** Set `processing_status: validated` → emit `MAT.integrated` event
3. **If FAIL:** Set `processing_status: analyzed` with failure reason → flag for review

### Output

```
## MAT Index Report: {character or "all"}

### Contradiction Summary
| # | Material | Claims | Profile Says | Severity | File |
|---|----------|--------|-------------|----------|------|

### Coverage Analysis
| Profile Section | Materials Supporting | Evidence Tier | Gap? |
|----------------|---------------------|---------------|------|
| psychology/formulation.md | 5 files (T1×2, T2×3) | Strong | No |
| timeline/state-timeline.md | 2 files (T2×1, T3×1) | Moderate | Minor |
| darkness/traumas.md | 1 file (T1) | Adequate | No |
| light/strengths-hope.md | 0 files | None | YES |

### Integration Ready
| Material | Status | Blocker |
|----------|--------|---------|
| transcript-crisis-09-2025.md | ✓ READY | — |
| letter-huyện-undated.md | ✗ BLOCKED | CRAAP < 15 |

### Stale Materials (>7 days at raw/extracted)
| File | Status | Days Stuck |
|------|--------|-----------|

### Events Emitted
- MAT.integrated × {N} files
- MAT.contradiction × {M} (severity: {breakdown})
```

## Workflow: --contradictions

Focused mode — only run contradiction detection:

1. For each material file, extract factual claims
2. Compare against all profile files
3. Output contradiction table sorted by severity (CRITICAL first)
4. Skip coverage analysis and stale check

## Workflow: --coverage

Evidence coverage gap analysis:

1. For each profile section (21 files per character):
   - Count how many materials reference/support this section
   - Assess evidence tier distribution
   - Flag sections with no material backing (T5-only or gap)
2. Output coverage matrix

## Workflow: --stale

Find materials stuck in pipeline:

1. Read all materials with `processing_status` in [raw, extracted]
2. Check `last_updated` or git log for age
3. Flag files >7 days without progress
4. Suggest: re-run mat:loader or manual review

## Scripts

| Script                                                   | Purpose                                                |
| -------------------------------------------------------- | ------------------------------------------------------ |
| `scripts/detect-contradictions-materials-vs-profiles.py` | Scan materials for claims and compare against profiles |
| `scripts/evidence-coverage-gap-analysis.py`              | Map which profile sections lack material backing       |

## Event Emissions

| Event               | Condition                       | Downstream                      |
| ------------------- | ------------------------------- | ------------------------------- |
| `MAT.integrated`    | Material passes Stage 4 gate    | → PSY.refresh + CRE.recalibrate |
| `MAT.contradiction` | Contradiction severity ≥ MEDIUM | → PSY.flag → user review        |

## Safety

- READ-ONLY for all modes except status updates
- Writes only to material frontmatter (`processing_status` field)
- Never modifies profile files — only flags what needs updating
- Domain boundary: reads `docs/materials/` + `docs/profiles/`, writes only to `docs/materials/`

## Examples

```bash
/mat:indexer                                  # full cross-reference all
/mat:indexer --character hoa                  # Nhân vật B's materials vs profile
/mat:indexer --contradictions                 # show conflicts only
/mat:indexer --coverage                       # evidence gaps
/mat:indexer --stale                          # stuck materials
```

## See Also

- `mat:loader` — Stage 1-2: ingestion and classification (run before indexer)
- `psy:crossref` — profile-level cross-character consistency (runs after MAT integration)
- `docs/rules/11-mat-pipeline.md` — full pipeline documentation
- `.claude/schemas/material-schema.yaml` — frontmatter schema
- `docs/rules/12-mpc-orchestration.md` — event system documentation
