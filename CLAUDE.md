# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

## Project Purpose

Character profile documentation for storytelling and content creation.

---

## Framework Architecture

Five integrated frameworks with event-driven orchestration:

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                    ↑ ORC (Orchestration) ↑
              GRO (Growth) ↗ PSY + CRE
```

| Framework | Domain           | Directory                                             | Purpose                            |
| --------- | ---------------- | ----------------------------------------------------- | ---------------------------------- |
| **MAT**   | Materials        | `docs/materials/`                                     | Evidence ingestion, tiers, CRAAP   |
| **PSY**   | Psychology       | `docs/profiles/` + `docs/references/` + `docs/graph/` | Clinical profiling, 5P formulation |
| **CRE**   | Content          | `assets/`                                             | Platform content creation          |
| **GRO**   | Growth           | `docs/profiles/*/growth/`                             | Career + intelligence growth       |
| **ORC**   | Orchestration    | `.claude/`                                            | Event routing, domain coordination |
| **COM**   | Common utilities | `.claude/`                                            | Git, health-check, rules           |

Event flow: `MAT.integrated` → `PSY.refresh` → `CRE.recalibrate`
GRO events: `GRO.assessed` / `GRO.mentored` → `PSY.refresh` → `CRE.recalibrate`

---

## Directory Structure

```
docs/
├── profiles/           ← Character profiles (universal nested structure)
│   ├── character-a/
│   ├── character-b/
│   └── character-c/
├── materials/          ← MAT framework: source materials with evidence tiers
│   ├── character-a/
│   ├── character-b/
│   └── character-c/
├── references/         ← Clinical Psychology Theory Library (62 theories)
├── graph/              ← Cross-character relational dynamics
└── rules/              ← Modular rules (14 files)
plans/
├── reports/            ← Validation reports
└── templates/          ← Plan templates
assets/
├── facebook/           ← Facebook posts & media
├── instagram/          ← Instagram posts & stories
├── tiktok/             ← TikTok content
├── youtube/            ← YouTube thumbnails, scripts
├── twitter/            ← Twitter/X posts
└── linkedin/           ← LinkedIn articles
```

### Assets Naming Convention

```
assets/{platform}/{YYMMDD}-{slug}/
├── post.txt            ← Main content
├── image-prompts.txt   ← AI image generation prompts
├── images/             ← Generated/final images
└── README.txt          ← Package summary
```

---

## Character Profiles — Universal Nested Structure

Each character has **25 universal files** in a standardized nested structure, plus **optional per-character cross-relationship files** discovered dynamically via `list_relationship_files()` in `paths.py`:

```
docs/profiles/{character}/
├── INDEX.md                          ← Quick reference
├── CURRENT-STATE.md                  ← Current psychological state snapshot
├── milestones.md                     ← Key life milestones
├── identity/
│   ├── core.md                       ← Basic info, education, career, family
│   ├── writing-voice.md              ← Tone, themes (Nhân vật A has richest)
│   ├── achievements.md               ← Academic, scholarships, awards
│   └── media-coverage.md             ← Press timeline
├── psychology/
│   ├── formulation.md                ← 5 Ps case formulation (clinical core)
│   ├── defense-mechanisms.md         ← Defense hierarchy: Mature→Neurotic→Immature
│   ├── attachment-style.md           ← Attachment patterns + relationship dynamics
│   ├── growth-edges.md               ← Active growth areas + therapeutic windows
│   ├── core-wounds.md                ← Core wound patterns
│   ├── diagnostics.md                ← Big Five + ICD-11 dimensional scores
│   ├── cultural-formulation.md       ← Cultural context factors
│   └── archetype.md                  ← Jungian + Pia Melody mapping
├── relationships/
│   ├── family.md                     ← Family tree, key relationships
│   ├── {other-character}.md          ← Cross-relationship file (optional, per character)
│   └── network.md                    ← Extended network (Nhân vật A only)
├── timeline/
│   ├── overview.md                   ← Timeline summary
│   └── state-timeline.md            ← Longitudinal ICD-11 phases with severity
├── darkness/
│   └── traumas.md                    ← Trauma documentation
├── light/
│   └── strengths-hope.md            ← Sources of hope, resilience
├── evidence/
│   └── conversations.md             ← Key conversation evidence
└── growth/
    ├── career-path.md               ← Career history, trajectory (Super's model)
    ├── competencies.md              ← Skill inventory (Dreyfus 7-level)
    ├── learning-profile.md          ← Cognitive style (Kolb's model)
    └── mentoring-map.md             ← Mentor/mentee relationships (Kram's model)
```

Cross-relationship files per character: Nhân vật A (3: character-b.md, character-c.md, network.md), Nhân vật B (2: character-a.md, character-c.md), Nhân vật C (2: character-a.md, character-b.md). Mirror pairs are bidirectional.

**Characters:** Nhân vật A (`character-a`), Nhân vật B (`character-b`), Nhân vật C (`character-c`)

### Research Materials — MAT Framework (`docs/materials/`)

Materials with MAT-compliant frontmatter (evidence tiers T1-T5, CRAAP scores, processing status).

- `character-a/` — Transcripts, clinical notes, personal logs
- `character-b/` — Conversation logs, family context
- `character-c/` — Interview transcripts, letters, news articles

### Clinical Reference Library (`docs/references/`)

- `INDEX.md` — Master index of 62 clinical psychological theories
- Focus: Clinical-grade character analysis without exposing raw psychiatric terms in content

### Cross-Character Graph (`docs/graph/`)

- `relational-dynamics.md` — Cross-character relationship dynamics, attachment interactions

---

## Key Facts

**Nhân vật A**: Born 24/09/1997, Senior AI Engineer at VinSmart Future (06/2026~), prev. One Mount Group (08/2020-05/2026)
**Nhân vật B**: Born 18/02/2008, Grade 12 student, Tỉnh X
**Nhân vật C**: Born 14/05/2007, IT-E6 student at ĐHBK Hà Nội, Scholarship X F15 scholar
**Relationship (Nhân vật A - Nhân vật B)**: Sworn brothers (kết nghĩa) since 09/2025, 11-year age gap
**Relationship (Nhân vật A - Nhân vật C)**: Mentor - Mentee (Scholarship X interviewer)

---

## Rules (`docs/rules/`)

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
| 12  | orc-orchestration          | Event system, domain boundaries, trigger routing (5 domains)  |
| 13  | orc-workflow               | End-to-end workflow tracks (MAT→PSY→CRE + GRO cascades)       |
| 14  | cre-evidence-and-events    | Evidence tier permissions, CRE events, PSY→CRE translation    |
| 15  | gro-framework              | GRO domain boundaries, profile files, GRO↔PSY boundary        |

---

## Skills (`.claude/skills/`)

### ORC — Orchestration Skills

| Skill               | Purpose                                                           |
| ------------------- | ----------------------------------------------------------------- |
| `orc:bootstrap`     | Load project context (--quick/--full/--character/--lite/--intent) |
| `orc:session-state` | Track session state, framework domains, event queue               |
| `orc:classify`      | Risk classification (tiny/normal/high_risk) + MAT gates           |
| `orc:intake`        | Route work type → skill chain (MAT/PSY/CRE/GRO routing)           |
| `orc:compounding`   | Extract session learnings → memory                                |
| `orc:dream`         | Periodic memory consolidation                                     |
| `orc:decisions`     | Append-only decision records                                      |
| `orc:agent-memory`  | Per-agent calibration memory                                      |
| `orc:event-log`     | Persistent event audit logging (JSONL append + query)             |
| `orc:domain-router` | Route domain events to downstream skills (diff or explicit)       |
| `orc:cascade`       | Resolve multi-step event cascade chains across domains            |
| `orc:audit`         | Cross-domain event consistency verification                       |
| `orc:santa`         | Dual-reviewer quality gate — independent review, max 2 rounds     |
| `orc:council`       | 4-voice decision framework — anti-anchoring, verdict storage      |

### COM — Common Skills

| Skill              | Purpose                                                 |
| ------------------ | ------------------------------------------------------- |
| `com:git`          | Project-aware git operations                            |
| `com:health-check` | Session health monitoring — stall/error/death detection |
| `com:kit-cleanup`  | Project cleanup utilities                               |
| `com:rules`        | Modular rules management                                |

### MAT — Material Framework Skills

| Skill         | Purpose                                                             |
| ------------- | ------------------------------------------------------------------- |
| `mat:loader`  | Stage 1-2: ingest, classify, CRAAP score, frontmatter injection     |
| `mat:indexer` | Stage 3-4: contradiction detection, coverage gaps, integration gate |
| `mat:archive` | Material soft-delete/archival with audit trail (dry-run default)    |
| `mat:rescore` | Identify materials needing CRAAP re-evaluation                      |

### PSY — Psychology Framework Skills

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

### CRE — Content Creation Skills

| Skill                  | Purpose                                                                    |
| ---------------------- | -------------------------------------------------------------------------- |
| `cre:exploring`        | 7-question exploration → CONTEXT.md                                        |
| `cre:post-writer`      | End-to-end content creation pipeline                                       |
| `cre:prompt-leverage`  | 5-layer prompt strengthening                                               |
| `cre:privacy-guard`    | Pre-publish privacy/confidentiality scan                                   |
| `cre:repurpose`        | Adapt content across platforms                                             |
| `cre:voice-audit`      | Audit content voice/tone consistency against WRITING-VOICE.md              |
| `cre:evidence-scanner` | Per-claim evidence-tier gate (T1-T5) + Rule-09 leak; post-writer delegates |

### GRO — Growth Framework Skills

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

---

## Scripts Infrastructure

53 skills (orc/mat/psy/cre/gro/com) share a Python utility library and 60+ supportive scripts.

### Shared Library (`.claude/scripts/platform_lib/`)

| Module               | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `paths.py`           | Project root, character name resolution, paths   |
| `clinical_terms.py`  | 80+ regex patterns, term scanning, ref indexing  |
| `markdown_parser.py` | Section extraction, frontmatter, dates, links    |
| `profile_stats.py`   | File inventory, git hash cache validation        |
| `formatters.py`      | Markdown tables, JSON output, severity badges    |
| `env_utils.py`       | .env loading, API key resolution (standardized)  |
| `csv_search.py`      | BM25 text search over CSV data                   |
| `instinct_store.py`  | Atomic learnings CRUD, confidence scoring, JSONL |

### Running Scripts

```bash
# Python scripts (use project venv)
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/{framework}-{skill}/scripts/{script}.py [args]

# Shell scripts
bash .claude/skills/{framework}-{skill}/scripts/{script}.sh [args]
```

### Design Principle

Scripts do **DETERMINISTIC GATHERING**; LLM does **HEURISTIC JUDGMENT**. Scripts may over-flag (false positives expected) — better to over-gather than miss genuine findings.

---

## Subagent API Error Retry

When a subagent (Agent tool) returns output containing API error patterns, **auto-retry once** with the same prompt.

**Retry patterns** (case-insensitive match on tool result):

- `API Error`, `JSON Parse error`, `Unexpected EOF`
- `Internal Server Error`, `Service Unavailable`, `ECONNRESET`, `socket hang up`

**Never retry** if result contains: `rate_limit`, `Rate limit`, `429`, `credit`, `billing`, `context_length_exceeded`, `invalid_api_key`

**Protocol:**

1. Detect error pattern in Agent tool result
2. Log: `"⚠️ Subagent API error — retrying (attempt 2/2)..."`
3. Re-spawn Agent with identical prompt
4. If retry also fails → report error to user, stop

---

## Auto-Monitoring Policy

LLM should auto-invoke `com:health-check` for subagents/team agents ONLY when:

1. User explicitly confirms monitoring, OR
2. A health-check Monitor is already running for the main agent

Never auto-spawn health monitor without user awareness.

---

## RTK (Token Optimization)

Token-optimized CLI proxy (60-90% savings on dev operations). Hook-based — `git status` automatically becomes `rtk git status` via PreToolUse hook.

Meta commands (use directly): `rtk gain`, `rtk gain --history`, `rtk discover`, `rtk proxy <cmd>`

---

## Infrastructure Note

This project is fully self-contained. All skills, agents, hooks, rules, and scripts are local under `.claude/`.
Global `~/.claude/` has been stripped to runtime-only (config, cache, sessions only).
Backup: `~/.claude-backup-260522.tar.gz`

---

_Updated: 2026-05-23_
