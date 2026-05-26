# MODULES — Skill Grouping & Cross-Framework Dependency Map

Navigation map for the **55 project-owned skills** across 6 frameworks. Semi-derived from each
`SKILL.md` `metadata.dependencies` frontmatter + the CLAUDE.md catalog — **regenerate after skill
changes** (`orc:skill-stocktake --quick` catches count drift; `--conformance` checks structure).

Count reconciles with CLAUDE.md: **ORC 15 · PSY 16 · CRE 9 · GRO 8 · MAT 4 · COM 3 = 55**.
ck-origin skills (`cook`, `plan`, `scout`, `skill-creator`, `/ck:*`, `/ckm:*`) are **excluded** — they
are dev tools used read-only, not part of the framework catalog.

## MAT — Materials (4)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `mat:loader` | Stage 1-2 ingest, classify, CRAAP, frontmatter | — |
| `mat:indexer` | Stage 3-4 contradiction/gap/integration gate | `mat:loader` |
| `mat:archive` | Soft-delete/archival with audit trail | — |
| `mat:rescore` | Flag materials needing CRAAP re-eval | — |

## PSY — Psychology (16)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `psy:wave` | 3-wave orchestration | `orc:bootstrap`, `psy:crossref`, `psy:ref-audit`, `mat:loader` |
| `psy:crossref` | Cross-character 10-dimension validation | — |
| `psy:ref-audit` | Profile → reference accuracy | — |
| `psy:ref-scan` | Reference → profile coverage | `psy:ref-audit` |
| `psy:ref-create` | Create reference files (schema) | `psy:ref-audit`, `psy:ref-scan` |
| `psy:ref-maintain` | Reference library cleanup | — |
| `psy:crisis-assess` | DSM-5/ICD-11 crisis + risk levels | `orc:bootstrap`, `psy:ref-audit` |
| `psy:hypothesis` | Predict behavior given hypotheticals | `orc:bootstrap`, `psy:ref-audit` |
| `psy:arc-tracker` | Growth trajectories, hypothesis vs reality | `orc:bootstrap`, `psy:hypothesis` |
| `psy:narrative-twist` | Handle revealed falsehoods + cascade | `psy:crossref` |
| `psy:propagate` | Cross-character event cascade | — |
| `psy:timeline-sync` | Cross-character timeline validation | — |
| `psy:profile-lite` | Compress profiles (~95%) | `orc:bootstrap` |
| `psy:profile-compare` | Side-by-side dimension comparison | — |
| `psy:health-check` | Profile completeness scoring | — |
| `psy:relation-intelligence` | Mine dyad graph for content angles | — |

## CRE — Content Creation (9)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `cre:post-writer` | End-to-end content pipeline | (delegates `cre:evidence-scanner`) |
| `cre:exploring` | 7-question exploration → CONTEXT.md | — |
| `cre:angle-discovery` | Mine 6 frameworks → ranked angles | — |
| `cre:multiplatform` | 1→N platform-native variants | `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` |
| `cre:repurpose` | Adapt content 1→1 across platforms | — |
| `cre:prompt-leverage` | 5-layer prompt strengthening | `cre:exploring` |
| `cre:evidence-scanner` | Per-claim evidence-tier + Rule-09 gate | — |
| `cre:voice-audit` | Voice/tone consistency check | `orc:bootstrap` |
| `cre:privacy-guard` | Pre-publish privacy/confidentiality scan | — |

## GRO — Growth (8)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `gro:career-path` | Career trajectory + stage mapping | — |
| `gro:competency-map` | Skills/competency + gap analysis | — |
| `gro:learning-profile` | Learning style + acquisition patterns | — |
| `gro:mentoring-track` | Mentoring relationship documentation | — |
| `gro:career-forecast` | LLM career projection [FORECAST] | — |
| `gro:compare` | Side-by-side career comparison | — |
| `gro:milestone-tracker` | Career milestones actual vs planned | — |
| `gro:validate` | Cross-check growth data consistency | — |

## ORC — Orchestration (15)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `orc:bootstrap` | Load project context | `orc:session-state` |
| `orc:session-state` | Track session state + event queue | — |
| `orc:classify` | Risk classification + MAT gates | — |
| `orc:intake` | Route work type → skill chain | `orc:classify` |
| `orc:compounding` | Extract session learnings → memory | `orc:session-state` |
| `orc:dream` | Periodic memory consolidation | `orc:compounding` |
| `orc:agent-memory` | Per-agent calibration memory | `orc:compounding` |
| `orc:decisions` | Append-only decision records | — |
| `orc:event-log` | Persistent event audit (JSONL) | — |
| `orc:domain-router` | Route domain events downstream | — |
| `orc:cascade` | Resolve multi-step event cascades | — |
| `orc:audit` | Cross-domain event consistency | — |
| `orc:santa` | Dual-reviewer quality gate | `orc:classify` |
| `orc:council` | 4-voice decision framework | `orc:decisions` |
| `orc:skill-stocktake` | Skill catalog + CE-02 conformance audit | — |

## COM — Common (3)

| Skill | Purpose | Depends on |
| ----- | ------- | ---------- |
| `com:git` | Project-aware git operations | — |
| `com:health-check` | Session health monitoring | — |
| `com:rules` | Modular rules management | `orc:classify` |

## Cross-framework dependency edges

The notable couplings that cross a framework boundary (intra-framework deps omitted):

```
psy:wave            → orc:bootstrap, mat:loader        (PSY → ORC, MAT)
psy:crisis-assess   → orc:bootstrap                    (PSY → ORC)
psy:hypothesis      → orc:bootstrap                    (PSY → ORC)
psy:arc-tracker     → orc:bootstrap                    (PSY → ORC)
psy:profile-lite    → orc:bootstrap                    (PSY → ORC)
cre:voice-audit     → orc:bootstrap                    (CRE → ORC)
com:rules           → orc:classify                     (COM → ORC)
```

**Hub:** `orc:bootstrap` (5 inbound cross-framework edges) — the context-loading entry every
deep-analysis skill leans on. `mat:loader` is the MAT-side hub (`psy:wave`, `mat:indexer`).
Pure intra-framework chains (`psy:ref-*`, `orc:session-state → compounding → dream`) stay within
their domain, respecting the event-bus boundary (Rule 12).

## Maintenance

Regenerate when skills are added/renamed/retired. Source of truth = `SKILL.md` frontmatter; this
file is a derived view. `orc:skill-stocktake` reconciles the count and flags drift vs CLAUDE.md.
