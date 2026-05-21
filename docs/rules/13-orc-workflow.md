---
title: ORC Workflow — End-to-End User Prompt to Published Content
version: "1.0"
created: "2026-05-17"
---

# Rule 13: ORC Workflow — End-to-End User Prompt to Published Content

## Overview

This rule defines the full journey from user prompt to published content, including skill prefix routing, quality gates between stages, and decision logic for when to use which framework.

## End-to-End Workflow

```
User Prompt
    │
    ▼
[Stage 0: CLASSIFY]  ← orc:intake + orc:classify
    │  Determine: work type + risk level + character
    │
    ├── Work type = materials ingestion?
    │       └──→ [MAT TRACK] (see below)
    │
    ├── Work type = profile update?
    │       └──→ [PSY TRACK] (see below)
    │
    ├── Work type = content creation?
    │       └──→ [CRE TRACK] (see below)
    │
    └── Work type = growth/career analysis?
            └──→ [GRO TRACK] (see below)
```

### MAT Track — Materials Ingestion

```
[MAT.1] orc:intake      → identify character + source type + confidentiality
[MAT.2] mat:loader      → normalize, frontmatter, tier assignment
[MAT.3] mat:indexer     → contradiction detection, cross-reference
[MAT.4] PSY gate        → MAT.integrated event → triggers PSY TRACK automatically
```

Quality gate between MAT.3 and MAT.4: if contradiction severity = high/critical → STOP → surface to user before proceeding.

### PSY Track — Profile Analysis & Update

```
[PSY.1] psy:bootstrap   → load character context (profiles + recent git + session state)
[PSY.2] psy:ref-scan    → map clinical theories to profile sections
[PSY.3] psy:crossref    → validate cross-character consistency (10 dimensions: 4 core + 6 extended)
[PSY.4] Profile edit    → write to psychology/, timeline/, darkness/, light/, etc.
[PSY.5] psy:propagate   → detect cross-character cascade needs, update affected profiles
[PSY.6] PSY.updated     → triggers CRE.recalibrate if voice-relevant sections changed
```

Quality gate between PSY.3 and PSY.4: crossref must pass >75% consistency threshold across all 10 dimensions or flag discrepancies for human review.

Quality gate between PSY.5 and PSY.6: psy:propagate cascade must complete — all affected characters updated symmetrically before emitting PSY.updated event.

### CRE Track — Content Creation

```
[CRE.1] orc:classify    → risk level (tiny / normal / high_risk)
[CRE.2] psy:profile-lite → compressed profile load (~95% token reduction)
[CRE.3] orc:voice-audit → verify 3-layer voice architecture is current
[CRE.4] cre:explore     → (normal+ risk only) lock content angle in CONTEXT.md
[CRE.5] orc:prompt-leverage → strengthen prompt through 5 layers
[CRE.6] cre:post-writer → generate draft in assets/{platform}/
[CRE.7] orc:privacy-guard → pre-publish privacy + clinical term scan
[CRE.8] Publish         → user manually copies to platform
```

Quality gate between CRE.3 and CRE.4: if voice architecture stale (last PSY refresh after last material integration) → force CRE.recalibrate before proceeding.

### GRO Track — Career & Growth Analysis

```
[GRO.1] orc:intake           → identify character + growth work type
[GRO.2] orc:bootstrap        → load character context + growth/ files
[GRO.3] gro:career-path      → career trajectory analysis (or gro:competency-map, gro:learning-profile)
[GRO.4] gro:validate         → cross-check growth data consistency
[GRO.5] GRO.assessed event   → triggers CRE.recalibrate if content angle affected
```

GRO→PSY cascade: `GRO.mentored` → `PSY.refresh` (mentoring reveals psychological insights)
GRO→CRE cascade: `GRO.assessed` / `GRO.profiled` → `CRE.recalibrate` (career data informs content)

## Skill Prefix Routing Table

| User intent                              | First skill            | Full chain                                               |
| ---------------------------------------- | ---------------------- | -------------------------------------------------------- |
| "Add new material / chat log / letter"   | `orc:intake`           | orc:intake → mat:loader → mat:indexer → (PSY auto)       |
| "Update profile with new info"           | `orc:intake`           | orc:intake → psy:bootstrap → profile edit → psy:crossref |
| "Write a post for [platform]"            | `orc:classify`         | orc:classify → psy:profile-lite → cre:post-writer        |
| "Repurpose this content for [platform]"  | `cre:repurpose`        | cre:repurpose → orc:privacy-guard                        |
| "Validate profile consistency"           | `psy:crossref`         | psy:bootstrap → psy:crossref → psy:ref-audit             |
| "Check clinical theory coverage"         | `psy:ref-scan`         | psy:ref-scan → psy:ref-audit                             |
| "Assess crisis risk in this material"    | `psy:crisis-assess`    | psy:bootstrap → psy:crisis-assess → (06-crisis-protocol) |
| "Track character growth trajectory"      | `psy:arc-tracker`      | psy:bootstrap → psy:arc-tracker                          |
| "Predict behavior in scenario X"         | `psy:hypothesis`       | psy:bootstrap → psy:hypothesis                           |
| "Start new session / catch me up"        | `psy:bootstrap`        | psy:bootstrap → orc:session-state                        |
| "Compress profiles for token efficiency" | `psy:profile-lite`     | psy:profile-lite (standalone)                            |
| "Record this decision"                   | `orc:decisions`        | orc:decisions (standalone, append-only)                  |
| "Consolidate session learnings"          | `orc:compounding`      | orc:compounding → orc:dream (if full consolidation)      |
| "Archive old materials"                  | `mat:archive`          | mat:archive (standalone, dry-run default)                |
| "Re-score CRAAP on materials"            | `mat:rescore`          | mat:rescore → mat:loader (for each flagged file)         |
| "Propagate changes to other characters"  | `psy:propagate`        | psy:propagate → psy:crossref (verify after cascade)      |
| "Sync timelines across characters"       | `psy:timeline-sync`    | psy:timeline-sync (standalone fix suggestions)           |
| "Check profile completeness"             | `psy:health-check`     | psy:health-check (standalone scoring)                    |
| "Compare characters side-by-side"        | `psy:profile-compare`  | psy:profile-compare --dimension <dim>                    |
| "Clean up reference library"             | `psy:ref-maintain`     | psy:ref-maintain (standalone audit)                      |
| "Show event history / audit trail"       | `orc:event-log`        | orc:event-log --query (standalone)                       |
| "Audit voice/tone consistency"           | `orc:voice-audit`      | orc:voice-audit (reads identity/writing-voice.md)        |
| "Handle revealed falsehood / new truth"  | `orc:narrative-twist`  | orc:narrative-twist → psy:crossref → (cascade updates)   |
| "Privacy scan before publishing"         | `orc:privacy-guard`    | orc:privacy-guard (standalone gate)                      |
| "Analyze career path / trajectory"       | `gro:career-path`      | orc:bootstrap → gro:career-path → gro:validate           |
| "Map competencies / skills gap"          | `gro:competency-map`   | orc:bootstrap → gro:competency-map → gro:validate        |
| "Build learning profile"                 | `gro:learning-profile` | orc:bootstrap → gro:learning-profile                     |
| "Document mentoring session"             | `gro:mentoring-track`  | orc:bootstrap → gro:mentoring-track → (PSY auto)         |
| "Forecast career trajectory"             | `gro:career-forecast`  | orc:bootstrap → gro:career-forecast [FORECAST]           |
| "Compare careers across characters"      | `gro:compare`          | gro:compare (standalone comparison)                      |
| "Route domain events / what runs next"   | `orc:domain-router`    | orc:domain-router --from-diff or --event                 |
| "Resolve event cascade chain"            | `orc:cascade`          | orc:cascade --trigger <event>                            |
| "Audit event consistency"                | `orc:audit`            | orc:audit --domain all                                   |

## Quality Gates Between Stages

### Gate 1: MAT → PSY (Integration Gate)

- Material processing_status must = "validated" before PSY refresh
- Contradiction severity high/critical → human review required
- Source tier must be documented (1-5)

### Gate 2: PSY → CRE (Profile Freshness Gate)

- `psy:profile-lite` must load files modified after last CRE session
- crossref consistency score must be ≥75% across all 10 dimensions
- `psychology/defense-mechanisms.md` must exist (CRE blocks without it)
- `timeline/state-timeline.md` current phase must be checked (phase-appropriate content routing)
- **Stale voice check**: if `last_material_integration` > `last_psy_refresh` → force `cre:voice-audit` before content creation

### Gate 3: CRE → Publish (Privacy + Voice Gate)

- `orc:privacy-guard` must pass: no `[PRIVATE]`/`[CONFIDENTIAL]` leaks
- Clinical terms must be translated to accessible language
- Platform format constraints verified (length, hook, hashtags)
- `post.md` ↔ `post.txt` sync confirmed

## Framework Selection Guide

### Use MAT when

- New raw material arrives (chat log, letter, interview, news article, screenshot)
- Source needs tier classification or CRAAP assessment
- Contradiction between existing profile and new information detected

### Use PSY when

- Profile files need updating from analyzed materials
- Cross-character consistency validation required
- Clinical theory mapping or reference audit needed
- Crisis assessment triggered by materials
- Character behavior hypothesis needed for content planning

### Use CRE when

- Generating any content that will be published or shared
- Repurposing existing content across platforms
- Voice/tone audit of draft content
- Image prompt generation for visual content

### Use ORC when

- Session start (always: orc:intake first)
- Risk classification needed before content creation
- Decision recording (append-only log)
- Session state tracking across multi-step workflows
- Privacy scan before any external publication
- Memory consolidation at session end

## Framework Integration Points

```
MAT ──[MAT.integrated]──→ PSY ──[PSY.updated]──→ CRE
 │                          │                      │
 │◄── reads materials        │◄── reads profiles    │◄── reads profiles (lite)
 │    (own domain)           │    from MAT output   │    from PSY output
 │                          │                      │
 └── NEVER writes to ────→  └── NEVER writes to ──→└── NEVER writes to
     profiles or assets          assets                  profiles or materials
```

ORC orchestrates all three — it owns `.claude/` config and session state only.

## Shortcuts for Common Scenarios

### Scenario A: New chat log arrives

```
orc:intake → mat:loader → mat:indexer → [gate 1] → psy:bootstrap → profile updates → psy:crossref → [gate 2] → (CRE if content needed)
```

### Scenario B: Write LinkedIn post about recent event

```
orc:classify → psy:profile-lite → orc:voice-audit → [gate 2] → cre:explore → orc:prompt-leverage → cre:post-writer → orc:privacy-guard → [gate 3]
```

### Scenario C: New material contradicts existing profile

```
mat:indexer detects contradiction → MAT.contradiction event → psy:crossref → orc:narrative-twist → profile corrections → psy:crossref rerun → CRE.recalibrate
```

### Scenario D: Session start after long break

```
psy:bootstrap --full → orc:session-state → psy:arc-tracker (optional) → proceed with task
```
