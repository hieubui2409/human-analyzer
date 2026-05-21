---
title: GRO Framework — Career + Intelligence Growth
version: "1.0"
created: "2026-05-21"
---

# Rule 15: GRO Framework — Career + Intelligence Growth

## Overview

GRO (Growth) covers career development, professional skills, cognitive/learning profiles, and mentoring dynamics. Factual career data only — psychological interpretation stays in PSY domain.

## Domain Boundaries

| Domain | Writes to                      | Reads from                                                             |
| ------ | ------------------------------ | ---------------------------------------------------------------------- |
| GRO    | `docs/profiles/{char}/growth/` | `docs/profiles/` identity/, psychology/ (read-only), `docs/materials/` |

**Hard rule**: GRO never writes to psychology/, identity/, relationships/, or any non-growth profile directory. Cross-reference allowed, cross-write forbidden.

## Profile Files (4 per character)

| File                | Framework                          | Content                                              |
| ------------------- | ---------------------------------- | ---------------------------------------------------- |
| career-path.md      | Super's Life-Career Rainbow + SCCT | Career history, trajectory, decisions, self-efficacy |
| competencies.md     | Dreyfus + SFIA hybrid              | Skill inventory: technical, soft, domain (7-level)   |
| learning-profile.md | Kolb's Experiential Learning       | Cognitive style, learning patterns, problem-solving  |
| mentoring-map.md    | Kram's Developmental Networks      | Mentor/mentee relationships, dual functions          |

### File Schema

Each growth file uses standard frontmatter:

```yaml
---
character: { char-slug }
domain: growth
type: data
tags: [career|competency|learning|mentoring]
references: []
cross_characters: []
last_updated: "YYYY-MM-DD"
updated_by: gro:{skill}
confidence: high|medium|low|unverified
---
```

## GRO ↔ PSY Boundary

| GRO owns (factual)                  | PSY owns (interpretive)                           |
| ----------------------------------- | ------------------------------------------------- |
| Career history, job titles, dates   | Why career choices were made (defense mechanisms) |
| Skill levels (Dreyfus 1-7)          | Growth-edges, therapeutic windows                 |
| Learning style preference           | Cognitive patterns as personality indicators      |
| Mentoring relationships (who, when) | Attachment dynamics in mentoring                  |
| Career trajectory milestones        | Life Architecture meaning-making                  |

Cross-reference between GRO↔PSY is allowed and encouraged. Cross-write is forbidden.

## Evidence Requirements

Career/learning observations must be grounded in MAT source materials (evidence tiers T1-T5):

| Evidence Tier | GRO Usage                                        |
| ------------- | ------------------------------------------------ |
| T1 (Primary)  | Direct career data from character (dates, roles) |
| T2 (Observed) | Corroborated skill assessments                   |
| T3 (Single)   | Single-observer competency ratings               |
| T4 (Indirect) | Reported career information                      |
| T5 (Theory)   | Framework-only inferences, marked [UNVERIFIED]   |

Ungrounded claims must be marked `[UNVERIFIED]`.

## GRO Events

| Event          | Trigger                               | Downstream                                                   |
| -------------- | ------------------------------------- | ------------------------------------------------------------ |
| `GRO.assessed` | Competency/skill assessment completed | → `CRE.recalibrate` (career data informs content angle)      |
| `GRO.forecast` | Career forecast generated             | Log only (informational, no cascade)                         |
| `GRO.mentored` | Mentoring interaction documented      | → `PSY.refresh` (mentoring reveals psychological insights)   |
| `GRO.profiled` | Learning profile updated              | → `CRE.recalibrate` (learning profile changes content style) |

## GRO → Other Domain Cascades

```
GRO.assessed ──→ CRE.recalibrate (career content angles change)
GRO.mentored ──→ PSY.refresh (mentoring reveals psychological dynamics)
GRO.profiled ──→ CRE.recalibrate (learning style affects content framing)
GRO.forecast ──→ (log only — no cascade)
```

## Life Stage Adaptation

Characters are at different career stages. GRO templates adapt:

| Character | Stage           | career-path.md focus        | competencies.md focus      |
| --------- | --------------- | --------------------------- | -------------------------- |
| Nhân vật A      | Professional    | Full career trajectory      | Professional skill matrix  |
| Nhân vật B       | Student (Gr.12) | Academic path + aspirations | Academic + emerging skills |
| Nhân vật C     | Freshman (Uni)  | Academic → early career     | Student + volunteer skills |

Thin data sections marked `[LIMITED DATA]` — never fabricated.

## Skills

| Skill                 | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| gro:career-path       | Analyze career trajectory, decisions, inflection points |
| gro:competency-map    | Inventory + assess skills (Dreyfus 7-level)             |
| gro:learning-profile  | Map cognitive style, learning patterns                  |
| gro:validate          | Cross-check growth data consistency                     |
| gro:mentoring-track   | Map mentor/mentee relationships                         |
| gro:career-forecast   | LLM-powered career trajectory projection [FORECAST]     |
| gro:compare           | Cross-character career/growth comparison                |
| gro:milestone-tracker | Track career milestones and progression                 |

## See Also

- `docs/rules/12-orc-orchestration.md` — event system and domain boundaries
- `docs/rules/13-orc-workflow.md` — GRO Track workflow
- `docs/rules/14-cre-evidence-and-events.md` — GRO→CRE recalibrate triggers
- `docs/rules/01-profile-structure.md` — universal profile schema
