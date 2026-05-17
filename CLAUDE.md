# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

## Project Purpose

Character profile documentation for storytelling and content creation.

---

## Framework Architecture

Four integrated frameworks with event-driven orchestration:

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                    ↑ MPC (Orchestration) ↑
```

| Framework | Domain             | Directory                                             | Purpose                            |
| --------- | ------------------ | ----------------------------------------------------- | ---------------------------------- |
| **MAT**   | Materials          | `docs/materials/`                                     | Evidence ingestion, tiers, CRAAP   |
| **PSY**   | Psychology         | `docs/profiles/` + `docs/references/` + `docs/graph/` | Clinical profiling, 5P formulation |
| **CRE**   | Content            | `assets/`                                             | Platform content creation          |
| **MPC**   | Meta-orchestration | `.claude/`                                            | Event routing, domain coordination |

Event flow: `MAT.integrated` → `PSY.refresh` → `CRE.recalibrate`

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

Each character has **21 files** in a standardized nested structure (same for all 3 characters):

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
│   └── family.md                     ← Family tree, key relationships
├── timeline/
│   ├── overview.md                   ← Timeline summary
│   └── state-timeline.md            ← Longitudinal ICD-11 phases with severity
├── darkness/
│   └── traumas.md                    ← Trauma documentation
├── light/
│   └── strengths-hope.md            ← Sources of hope, resilience
└── evidence/
    └── conversations.md             ← Key conversation evidence
```

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

| #   | File                       | Scope                                                      |
| --- | -------------------------- | ---------------------------------------------------------- |
| 01  | profile-structure          | Required files, schemas, size limits                       |
| 02  | clinical-reference-usage   | Show-don't-tell, mandatory citation                        |
| 03  | content-creation-pipeline  | 7-stage pipeline, platform guidelines                      |
| 04  | materials-ingestion        | Source priority P1-P4, ingestion process                   |
| 05  | wave-pipeline              | 3-wave protocol (Foundation→Deep Dive→Validation)          |
| 06  | crisis-protocol            | Mental health crisis, DSM-5, risk levels                   |
| 07  | narrative-twist-protocol   | Handling revealed falsehoods                               |
| 08  | cross-validation           | 4-dimension consistency, report format                     |
| 09  | confidentiality-protocol   | Privacy tags, content boundaries                           |
| 10  | reference-library-standard | Reference schema, scientific rigor                         |
| 11  | mat-pipeline               | MAT 5-stage pipeline, evidence tiers, CRAAP test           |
| 12  | mpc-orchestration          | Event system, domain boundaries, trigger routing           |
| 13  | mpc-workflow               | End-to-end workflow tracks (MAT→PSY→CRE)                   |
| 14  | cre-evidence-and-events    | Evidence tier permissions, CRE events, PSY→CRE translation |

---

## Skills (`.claude/skills/`)

### MPC — Orchestration Skills

| Skill               | Purpose                                                           |
| ------------------- | ----------------------------------------------------------------- |
| `mpc:bootstrap`     | Load project context (--quick/--full/--character/--lite/--intent) |
| `mpc:session-state` | Track session state, framework domains, event queue               |
| `mpc:classify`      | Risk classification (tiny/normal/high_risk) + MAT gates           |
| `mpc:intake`        | Route work type → skill chain (MAT/PSY/CRE routing)               |
| `mpc:compounding`   | Extract session learnings → memory                                |
| `mpc:dream`         | Periodic memory consolidation                                     |
| `mpc:decisions`     | Append-only decision records                                      |
| `mpc:agent-memory`  | Per-agent calibration memory                                      |

### COM — Common Skills

| Skill     | Purpose                      |
| --------- | ---------------------------- |
| `com:git` | Project-aware git operations |

### MAT — Material Framework Skills

| Skill           | Purpose                                                             |
| --------------- | ------------------------------------------------------------------- |
| `mat:loader`    | Stage 1-2: ingest, classify, CRAAP score, frontmatter injection     |
| `mat:indexer`   | Stage 3-4: contradiction detection, coverage gaps, integration gate |
| `mat:materials` | Legacy material loading (use mat:loader for new ingestions)         |

### PSY — Psychology Framework Skills

| Skill                 | Purpose                                                     |
| --------------------- | ----------------------------------------------------------- |
| `psy:crossref`        | Cross-character validation (4 dimensions)                   |
| `psy:ref-audit`       | Profile → reference accuracy check + --discover blind spots |
| `psy:ref-scan`        | Reference → profile coverage mapping                        |
| `psy:ref-create`      | Create new reference files with mandatory schema            |
| `psy:profile-lite`    | Compress profiles (~95% reduction)                          |
| `psy:wave`            | 3-wave orchestration (Foundation→Deep Dive→Validation)      |
| `psy:crisis-assess`   | DSM-5/ICD-11 crisis assessment + risk levels                |
| `psy:narrative-twist` | Handle revealed falsehoods, strikethrough + cascade         |
| `psy:hypothesis`      | Predict character behavior given hypothetical events        |
| `psy:arc-tracker`     | Track character growth trajectories, hypothesis vs reality  |

### CRE — Content Creation Skills

| Skill                 | Purpose                                                       |
| --------------------- | ------------------------------------------------------------- |
| `cre:exploring`       | 7-question exploration → CONTEXT.md                           |
| `cre:post-writer`     | End-to-end content creation pipeline                          |
| `cre:prompt-leverage` | 5-layer prompt strengthening                                  |
| `cre:privacy-guard`   | Pre-publish privacy/confidentiality scan                      |
| `cre:repurpose`       | Adapt content across platforms                                |
| `cre:voice-audit`     | Audit content voice/tone consistency against WRITING-VOICE.md |

---

## Scripts Infrastructure

26 skills (mpc/mat/psy/cre/com) share a Python utility library and 50+ supportive scripts.

### Shared Library (`.claude/scripts/platform_lib/`)

| Module               | Purpose                                         |
| -------------------- | ----------------------------------------------- |
| `paths.py`           | Project root, character name resolution, paths  |
| `clinical_terms.py`  | 80+ regex patterns, term scanning, ref indexing |
| `markdown_parser.py` | Section extraction, frontmatter, dates, links   |
| `profile_stats.py`   | File inventory, git hash cache validation       |
| `formatters.py`      | Markdown tables, JSON output, severity badges   |

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

_Updated: 2026-05-18_
