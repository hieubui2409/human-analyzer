# CLAUDE.md

Guidance for Claude Code in this repository. Loaded every session — kept lean: **architecture, rules, workflow only**. No examples, no character specifics (those live in `docs/profiles/`).

---

## Project Purpose

A clinical-grade **character profile intelligence system** for storytelling and content creation. Each character is documented as a deep, evidence-backed psychological profile; profiles feed platform-native content.

Built to **scale to many characters** (currently 3). Never hardcode character specifics into shared logic — resolve characters dynamically via `paths.py`.

---

## Architecture

Four domain frameworks + one orchestrator + one common toolkit, wired by an event bus:

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                  ↑ ORC (Orchestration) ↑
            GRO (Growth) ↗ PSY + CRE
```

| Framework | Type         | Domain       | Data location                                         | Purpose                            |
| --------- | ------------ | ------------ | ----------------------------------------------------- | ---------------------------------- |
| **MAT**   | Domain       | Materials    | `docs/materials/`                                     | Evidence ingestion, tiers, CRAAP   |
| **PSY**   | Domain       | Psychology   | `docs/profiles/` + `docs/references/` + `docs/graph/` | Clinical profiling, 5P formulation |
| **CRE**   | Domain       | Content      | `assets/`                                             | Platform content creation          |
| **GRO**   | Domain       | Growth       | `docs/profiles/*/growth/`                             | Career + competency intelligence   |
| **ORC**   | Orchestrator | Coordination | `.claude/`                                            | Event routing, domain boundaries   |
| **COM**   | Common       | Utilities    | `.claude/`                                            | Git, health-check, rules           |

Domain boundaries are enforced: each framework owns its data location and communicates through events, not direct cross-domain writes (Rule 12).

---

## Directory Structure

```
docs/
├── profiles/{character}/   ← 25-file universal nested profile (schema below)
├── materials/{character}/  ← MAT source materials w/ evidence tiers T1–T5 + CRAAP scores
├── references/             ← Clinical theory library (60+ theories), show-don't-tell
├── graph/                  ← Cross-character relational dynamics
└── rules/                  ← 15 modular rule files
plans/{reports,templates}/  ← Validation reports + plan templates
assets/{platform}/          ← CRE output, per platform
```

Asset package convention: `assets/{platform}/{YYMMDD}-{slug}/` → `post.txt`, `image-prompts.txt`, `images/`, `README.txt`.

**Navigation docs:** `docs/knowledge-architecture.md` (6-layer knowledge map), `docs/MODULES.md` (55-skill grouping + cross-framework dependency edges), `docs/distilled-principles.md` (5 cross-domain invariants from rules 01–15).

---

## Profile Structure — Universal Nested Schema

Every character has the **same 25 universal files** so tooling stays character-agnostic:

```
docs/profiles/{character}/
├── INDEX.md                  ← Quick reference
├── CURRENT-STATE.md          ← Current psychological state snapshot
├── milestones.md             ← Key life milestones
├── identity/                 ← core, writing-voice, achievements, media-coverage
├── psychology/               ← formulation (5P), defense-mechanisms, attachment-style,
│                                growth-edges, core-wounds, diagnostics (Big Five + ICD-11),
│                                cultural-formulation, archetype (Jungian + Pia Melody)
├── relationships/            ← family, network, + cross-relationship files
├── timeline/                 ← overview, state-timeline (longitudinal ICD-11 phases)
├── darkness/traumas.md       ← Trauma documentation
├── light/strengths-hope.md   ← Resilience, sources of hope
├── evidence/conversations.md ← Key conversation evidence
└── growth/                   ← career-path (Super), competencies (Dreyfus),
                                 learning-profile (Kolb), mentoring-map (Kram)
```

Cross-relationship files (`relationships/{other-character}.md`) are **optional and per-character**, discovered dynamically via `list_relationship_files()` in `paths.py`. Mirror pairs are bidirectional. Never enumerate them statically in code.

---

## Workflow

**Primary pipeline (event-driven):**

```
MAT.integrated → PSY.refresh → CRE.recalibrate
GRO.assessed | GRO.mentored → PSY.refresh → CRE.recalibrate
```

- **MAT** ingests + classifies sources (5-stage pipeline, evidence tiers T1–T5, CRAAP). Material must be *integrated* before PSY consumes it — MAT gates block premature analysis.
- **PSY** builds/refreshes the clinical formulation from integrated material + references.
- **GRO** feeds career/competency intelligence into PSY and CRE.
- **CRE** translates the refreshed profile into platform content, gated by evidence tier + confidentiality (Rules 09, 14).
- **ORC** routes events across domains, resolves cascades, audits consistency.

**Profile build protocol:** 3-wave — Foundation → Deep Dive → Validation (Rule 05).

**Design principle:** Scripts do **deterministic gathering** (may over-flag — false positives expected); the LLM does **heuristic judgment**. Never delegate reasoning to scripts.

---

## Rules (`docs/rules/` — 15 files)

| #   | File                       | Scope                                                         |
| --- | -------------------------- | ------------------------------------------------------------- |
| 01  | profile-structure          | Required files, schemas, size limits                          |
| 02  | clinical-reference-usage   | Show-don't-tell, mandatory citation                           |
| 03  | content-creation-pipeline  | 7-stage pipeline, platform guidelines                         |
| 04  | materials-ingestion        | Source priority P1-P4, ingestion process                      |
| 05  | wave-pipeline              | 3-wave protocol (Foundation→Deep Dive→Validation)             |
| 06  | crisis-protocol            | Mental health crisis, DSM-5, risk levels                      |
| 07  | narrative-twist-protocol   | Handling revealed falsehoods                                  |
| 08  | cross-validation           | 10-dimension consistency (4 core + 6 extended), report format |
| 09  | confidentiality-protocol   | Privacy tags, content boundaries                              |
| 10  | reference-library-standard | Reference schema, scientific rigor                            |
| 11  | mat-pipeline               | MAT 5-stage pipeline, evidence tiers, CRAAP test              |
| 12  | orc-orchestration          | Event system, domain boundaries, trigger routing              |
| 13  | orc-workflow               | End-to-end workflow tracks (MAT→PSY→CRE + GRO cascades)        |
| 14  | cre-evidence-and-events    | Evidence tier permissions, CRE events, PSY→CRE translation    |
| 15  | gro-framework              | GRO domain boundaries, profile files, GRO↔PSY boundary        |

---

## Skills Catalog (`.claude/skills/`)

55 framework skills (ORC 15 · PSY 16 · CRE 9 · GRO 8 · MAT 4 · COM 3). Invoke as `{framework}:{skill}`.

> Engineer-kit utility skills (`/ck:*`) installed alongside are **not** catalogued here — they are user-invoked dev tools, discoverable via the harness skill list.

### ORC — Orchestration

| Skill                 | Purpose                                                               |
| --------------------- | --------------------------------------------------------------------- |
| `orc:bootstrap`       | Load project context (--quick/--full/--character/--lite/--intent)     |
| `orc:session-state`   | Track session state, framework domains, event queue                   |
| `orc:classify`        | Risk classification (tiny/normal/high_risk) + MAT gates               |
| `orc:intake`          | Route work type → skill chain (MAT/PSY/CRE/GRO routing)               |
| `orc:compounding`     | Extract session learnings → memory                                    |
| `orc:dream`           | Periodic memory consolidation                                         |
| `orc:decisions`       | Append-only decision records                                          |
| `orc:agent-memory`    | Per-agent calibration memory                                          |
| `orc:event-log`       | Persistent event audit logging (JSONL append + query)                 |
| `orc:domain-router`   | Route domain events to downstream skills (diff or explicit)           |
| `orc:cascade`         | Resolve multi-step event cascade chains across domains                |
| `orc:audit`           | Cross-domain event consistency verification                           |
| `orc:santa`           | Dual-reviewer quality gate — independent review, max 2 rounds         |
| `orc:council`         | 4-voice decision framework — anti-anchoring, verdict storage          |
| `orc:skill-stocktake` | Skill catalog audit — count/metadata/overlap + CE-02 conformance gate |

### PSY — Psychology

| Skill                       | Purpose                                                              |
| --------------------------- | -------------------------------------------------------------------- |
| `psy:crossref`              | Cross-character validation (10 dimensions: 4 core + 6 ext)           |
| `psy:ref-audit`             | Profile → reference accuracy check + --discover blind spots          |
| `psy:ref-scan`              | Reference → profile coverage mapping                                 |
| `psy:ref-create`            | Create new reference files with mandatory schema                     |
| `psy:profile-lite`          | Compress profiles (~95% reduction)                                   |
| `psy:wave`                  | 3-wave orchestration (Foundation→Deep Dive→Validation)               |
| `psy:crisis-assess`         | DSM-5/ICD-11 crisis assessment + risk levels                         |
| `psy:narrative-twist`       | Handle revealed falsehoods, strikethrough + cascade                  |
| `psy:hypothesis`            | Predict character behavior given hypothetical events                 |
| `psy:arc-tracker`           | Track character growth trajectories, hypothesis vs reality           |
| `psy:propagate`             | Cross-character event cascade orchestration                          |
| `psy:timeline-sync`         | Cross-character timeline date validation + fix suggestions           |
| `psy:health-check`          | Profile completeness scoring (25 files × quality)                    |
| `psy:profile-compare`       | Side-by-side dimension comparison across characters                  |
| `psy:ref-maintain`          | Reference library cleanup (orphans, outdated, duplicates)            |
| `psy:relation-intelligence` | Proactively mine dyad graph for ranked, consent-gated content angles |

### CRE — Content Creation

| Skill                  | Purpose                                                                    |
| ---------------------- | -------------------------------------------------------------------------- |
| `cre:exploring`        | 7-question exploration → CONTEXT.md                                        |
| `cre:angle-discovery`  | Proactively mine 6 frameworks for ranked, evidence-backed content angles   |
| `cre:multiplatform`    | 1→N platform-native variant generation (per-variant gated)                 |
| `cre:post-writer`      | End-to-end content creation pipeline                                       |
| `cre:prompt-leverage`  | 5-layer prompt strengthening                                               |
| `cre:privacy-guard`    | Pre-publish privacy/confidentiality scan                                   |
| `cre:repurpose`        | Adapt content across platforms (1→1)                                       |
| `cre:voice-audit`      | Audit content voice/tone consistency against writing-voice                 |
| `cre:evidence-scanner` | Per-claim evidence-tier gate (T1-T5) + Rule-09 leak; post-writer delegates |

### GRO — Growth

| Skill                   | Purpose                                                   |
| ----------------------- | --------------------------------------------------------- |
| `gro:career-path`       | Career trajectory analysis + stage mapping                |
| `gro:competency-map`    | Skills/competency assessment + gap analysis               |
| `gro:learning-profile`  | Learning style + knowledge acquisition patterns           |
| `gro:validate`          | Cross-check growth/ data consistency + date alignment     |
| `gro:mentoring-track`   | Mentoring relationship documentation + insight extraction |
| `gro:career-forecast`   | LLM-powered career projection [FORECAST — NOT FACTUAL]    |
| `gro:compare`           | Side-by-side career comparison across characters          |
| `gro:milestone-tracker` | Track career milestones actual vs planned                 |

### MAT — Materials

| Skill         | Purpose                                                             |
| ------------- | ------------------------------------------------------------------- |
| `mat:loader`  | Stage 1-2: ingest, classify, CRAAP score, frontmatter injection     |
| `mat:indexer` | Stage 3-4: contradiction detection, coverage gaps, integration gate |
| `mat:archive` | Material soft-delete/archival with audit trail (dry-run default)    |
| `mat:rescore` | Identify materials needing CRAAP re-evaluation                      |

### COM — Common

| Skill              | Purpose                                                 |
| ------------------ | ------------------------------------------------------- |
| `com:git`          | Project-aware git operations                            |
| `com:health-check` | Session health monitoring — stall/error/death detection |
| `com:rules`        | Modular rules management                                |

---

## Scripts Infrastructure

Skills share a Python utility library + 60+ supportive scripts.

| Module (`.claude/scripts/platform_lib/`) | Purpose                                        |
| ---------------------------------------- | ---------------------------------------------- |
| `paths.py`                               | Project root, character resolution, paths      |
| `clinical_terms.py`                      | 80+ regex patterns, term scanning, ref indexing |
| `markdown_parser.py`                     | Section extraction, frontmatter, dates, links  |
| `profile_stats.py`                       | File inventory, git hash cache validation      |
| `formatters.py`                          | Markdown tables, JSON output, severity badges  |
| `env_utils.py`                           | .env loading, API key resolution               |
| `csv_search.py`                          | BM25 text search over CSV data                 |
| `instinct_store.py`                      | Atomic learnings CRUD, confidence scoring, JSONL |

Run scripts with the **project-local venv** (project is self-contained):

```bash
.claude/skills/.venv/bin/python3 .claude/skills/{framework}-{skill}/scripts/{script}.py [args]
bash .claude/skills/{framework}-{skill}/scripts/{script}.sh [args]
```

---

## Operational Notices

**Subagent API retry** — If an Agent-tool result contains a transient API error (`API Error`, `JSON Parse error`, `Unexpected EOF`, `Internal Server Error`, `Service Unavailable`, `ECONNRESET`, `socket hang up`), auto-retry **once** with the identical prompt. Never retry on: `rate_limit`/`429`, `credit`/`billing`, `context_length_exceeded`, `invalid_api_key`.

**Auto-monitoring** — Auto-invoke `com:health-check` for subagents only when the user confirms monitoring OR a health Monitor already runs for the main agent. Never auto-spawn a monitor silently.

**RTK** — Token-optimized CLI proxy (60-90% savings). Hook-based: `git status` → `rtk git status` via PreToolUse. Meta commands: `rtk gain [--history]`, `rtk discover`, `rtk proxy <cmd>`.

**Self-contained** — All skills, agents, hooks, rules, scripts are local under `.claude/`. Global `~/.claude/` is runtime-only (config, cache, sessions).

---

_Updated: 2026-05-26_
