---
name: psy:wave
description: "Orchestrate the 3-wave profile generation pipeline. Use when creating new character profiles, performing major profile updates (≥3 files affected), or integrating significant new source materials. Triggers: 'wave', 'profile pipeline', '3-wave', 'major update', 'new character', 'full profile update'. NOT for minor single-file edits."
argument-hint: "[--wave <1|2|3>|--character <name>|--all|--status|--plan <path>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "profile-pipeline"
  dependencies: ["orc:bootstrap", "psy:crossref", "psy:ref-audit", "mat:loader"]
---

# 3-Wave Profile Pipeline

Orchestrate profile generation/major updates following `docs/rules/05-wave-pipeline.md`.

## When to Use

- Creating a new character profile from scratch
- Major profile updates (≥3 files affected)
- Integrating significant new source materials (crisis events, relationship reveals, new transcripts)

**NOT for**: single-fact additions, minor corrections → edit directly with `[Source:]` tag.

## Flags

| Flag                 | Purpose                                                 |
| -------------------- | ------------------------------------------------------- |
| `--wave <1\|2\|3>`   | Execute specific wave only                              |
| `--character <name>` | Target character (resolve via orc:bootstrap name table) |
| `--all`              | Run all 3 waves sequentially with gates                 |
| `--status`           | Show current wave progress                              |
| `--plan <path>`      | Link to existing plan file for context                  |

## Character Name Resolution

| Input                                 | Directory           |
| ------------------------------------- | ------------------- |
| `hieu`, `hiếu`, `character-a`      | `character-a`    |
| `hoa`, `hòa`, `character-b`        | `character-b`    |
| `chien`, `chiến`, `character-c` | `character-c` |

## Wave Execution

### Wave 1: Foundation (Data Extraction)

**Purpose:** Extract objective facts → build character base.

**Steps:**

1. Load source materials via `mat:loader --character <name>`
2. Extract facts:
   - **Identity**: Name, DOB, Origins, Career, Education
   - **Timeline**: Chronological events (verify ages align with DOB)
   - **Relationships**: Family tree, key connections
3. Tag confidential info: `[PRIVATE]`, `[CONFIDENTIAL: {person}]`
4. Tag uncertain data: `[UNCERTAIN]`, `[DISPUTED: ...]`
5. Update files: `identity/core.md`, `timeline/overview.md`, `relationships/family.md`
6. For cross-character events → update OTHER character's files too (including `relationships/{other-character}.md` — discovered via `list_relationship_files()`)

**Gate check before Wave 2:**

- [ ] All source materials catalogued with P1-P4 priority
- [ ] Timeline has ≥N new events with dates
- [ ] Relationships updated with new connections
- [ ] Confidentiality tags applied

**Outputs:** Updated identity/core.md, timeline/overview.md, relationships/family.md

### Wave 2: Deep Dive (Psychological Analysis)

**Purpose:** Analyze behavioral patterns, trauma, and voice.

**Steps:**

1. Load `psychology/formulation.md` + `psychology/core-wounds.md` + `darkness/traumas.md` + `light/strengths-hope.md` for character
2. Analyze from Wave 1 facts:
   - **Soul & Wound**: Core wounds, triggers, dominant/hidden emotions
   - **Duality**: External Mask vs. Internal Reality
   - **Coping**: Healthy/unhealthy mechanisms, growth edges
3. Apply NGUYÊN TẮC TỐI THƯỢNG (mandatory clinical referencing):
   - Every psychological finding MUST link to `docs/references/`
   - If no theory exists → flag for `psy:ref-create` or create inline
4. If crisis indicators detected → run `psy:crisis-assess`
5. If narrative twist detected → run `psy:narrative-twist`
6. Update files: `psychology/formulation.md`, `psychology/core-wounds.md`, `darkness/traumas.md`, `light/strengths-hope.md`, `psychology/defense-mechanisms.md`, `milestones.md`
7. Also check/update these additional psychology files if applicable:
   - `psychology/attachment-style.md` — attachment patterns + relationship dynamics
   - `psychology/growth-edges.md` — active growth areas + therapeutic windows
   - `psychology/diagnostics.md` — Big Five + ICD-11 dimensional scores
   - `psychology/cultural-formulation.md` — cultural context factors
   - `psychology/archetype.md` — Jungian + Pia Melody mapping
   - `identity/achievements.md` — academic, scholarships, awards
   - `identity/media-coverage.md` — press timeline
   - `identity/writing-voice.md` — tone, themes (if voice evolution observed)
   - `evidence/conversations.md` — key conversation evidence
   - `timeline/state-timeline.md` — longitudinal ICD-11 phases with severity

**Gate check before Wave 3:**

- [ ] ≥5 triggers documented
- [ ] ≥3 coping mechanisms identified
- [ ] Inner conflict duality described
- [ ] All clinical terms linked to docs/references/
- [ ] Crisis protocol applied if needed (risk level documented)

**Outputs:** Updated `psychology/formulation.md`, `psychology/core-wounds.md`, `darkness/traumas.md`, `light/strengths-hope.md`, `psychology/defense-mechanisms.md`, `milestones.md` (+ applicable files from step 7)

### Wave 3: Synthesis & Validation

**Purpose:** Cross-reference all files, ensure consistency.

**Steps:**

1. Run `psy:crossref --character <name> --extended` → check 10 dimensions:
   - Core (automated): Temporal, Relational, Psychological, Factual
   - Extended (LLM): Evidential, Developmental, Cultural, Systemic, Narrative, Linguistic
2. Run `psy:ref-audit --character <name>` → verify clinical accuracy
3. Fix all CRITICAL and MAJOR issues found
4. Run `psy:propagate --character <name>` → detect cross-character cascade needs
   - If other characters affected → update their files symmetrically
5. Update `INDEX.md` with current status
6. Generate validation report → `plans/reports/wave3-{date}-{slug}.md`

**Gate check (final):**

- [ ] All 10 dimensions validated (4 core + 6 extended)
- [ ] No CRITICAL inconsistencies remaining
- [ ] Cross-character cascade applied (psy:propagate)
- [ ] INDEX.md reflects current state
- [ ] Validation report generated

**Outputs:** Updated INDEX.md, validation report

### Post-Wave Actions (MANDATORY)

After Wave 3 completes:

1. `orc:compounding --character <name>` — extract psychological insights + patterns learned
2. `orc:session-state --record-profile <name>` — record profiles touched for session recovery
3. Review existing `psy:hypothesis` reports — if any predictions exist for this character, check if wave findings confirm/deny them via `psy:arc-tracker --compare`

## --status

Show current progress:

```
## Wave Pipeline Status: {character}
Wave 1 (Foundation):  ✅ Complete / 🔄 In Progress / ⬜ Not Started
Wave 2 (Deep Dive):   ✅ Complete / 🔄 In Progress / ⬜ Not Started
Wave 3 (Validation):  ✅ Complete / 🔄 In Progress / ⬜ Not Started
Blockers: {list or "none"}
```

## --all (Full Pipeline)

Execute Wave 1 → Gate → Wave 2 → Gate → Wave 3 sequentially.
If a gate fails → stop and report what's missing before proceeding.

## Plan Integration

If `--plan <path>` provided:

1. Read plan file for context (objectives, deliverables)
2. Create wave1.md, wave2.md, wave3.md in plan directory
3. Update plan.md with wave progress

If no plan → create lightweight tracking in session state.

## Safety

- This skill MODIFIES profile files — always commit or checkpoint before running
- Wave 3 validation is NON-OPTIONAL — never skip
- Cross-character updates MUST be symmetric (update both sides)
- Scope: profile pipeline orchestration. Does NOT handle content creation or publishing.

## See Also

psy:crossref, psy:ref-audit, orc:classify
