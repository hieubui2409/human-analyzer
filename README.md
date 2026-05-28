# Character Profile Intelligence System

A clinical-grade documentation system that turns deep, evidence-backed psychological profiles of characters into platform-native content. Designed to **scale from a handful of characters to many** — tooling is character-agnostic and resolves subjects dynamically.

> **For Claude Code / LLM agents:** read [`CLAUDE.md`](./CLAUDE.md) (architecture + rules + workflow) and the rule files under [`.claude/rules/`](./.claude/rules/). This README is the human onboarding entry point.

---

## What it does

1. **Ingest** raw source material (transcripts, interviews, logs, articles) and score it for evidence quality.
2. **Analyze** it into a structured clinical profile — case formulation, defenses, attachment, trauma, strengths, timeline, growth.
3. **Generate** platform content (Facebook, LinkedIn, blog, …) that is faithful to the profile, gated by evidence tier and confidentiality.

Everything is event-driven: ingesting new material cascades into a profile refresh, which cascades into content recalibration.

---

## Architecture at a glance

Four domain frameworks + one orchestrator + one common toolkit:

```
MAT (Input) → PSY (Analysis) → CRE (Output)
                  ↑ ORC (Orchestration) ↑
            GRO (Growth) ↗ PSY + CRE
```

| Framework | Role                                  | Lives in                                            |
| --------- | ------------------------------------- | --------------------------------------------------- |
| **MAT**   | Materials — ingest, tier, CRAAP score | `docs/materials/`                                   |
| **PSY**   | Psychology — clinical 5P profiling    | `docs/profiles/`, `docs/references/`, `docs/graph/` |
| **CRE**   | Content — platform-native creation    | `assets/`                                           |
| **GRO**   | Growth — career + competency intel    | `docs/profiles/*/growth/`                           |
| **ORC**   | Orchestration — event routing, audits | `.claude/`                                          |
| **COM**   | Common — git, health-check, rules     | `.claude/`                                          |

The end-to-end workflow, event contracts, and domain boundaries are specified in [`CLAUDE.md`](./CLAUDE.md) and the rule files.

---

## Repository layout

```
docs/
├── profiles/{character}/   Character profiles — 25-file universal nested schema
├── materials/{character}/  Source material with evidence tiers (T1–T5) + CRAAP scores
├── references/             Clinical theory library (60+ theories)
├── graph/                  Cross-character relational dynamics
└── rules/                  15 modular rule files
assets/{platform}/          Content packages, one folder per published piece
plans/                      Implementation plans + validation reports
.claude/                    Skills, agents, hooks, scripts (self-contained)
```

Each character profile follows an identical 25-file structure (identity / psychology / relationships / timeline / darkness / light / evidence / growth) so analysis and validation tooling works for any character. See the schema in [`CLAUDE.md`](./CLAUDE.md).

---

## Characters

Currently 3 characters; the system is built to grow. Profiles live under `docs/profiles/{slug}/` — start from each character's `INDEX.md`.

| Slug                | Profile entry point                        |
| ------------------- | ------------------------------------------ |
| `character-a`    | `docs/profiles/character-a/INDEX.md`    |
| `character-b`    | `docs/profiles/character-b/INDEX.md`    |
| `character-c` | `docs/profiles/character-c/INDEX.md` |

Cross-character relationship dynamics are captured per-character in `relationships/` and aggregated in `docs/graph/`.

---

## Skills

55 framework skills, invoked as `{framework}:{skill}` (e.g. `orc:bootstrap`, `psy:crossref`, `cre:post-writer`):

| Framework | Count | Examples                                                       |
| --------- | ----- | -------------------------------------------------------------- |
| ORC       | 15    | `bootstrap`, `intake`, `cascade`, `audit`, `council`           |
| PSY       | 16    | `crossref`, `crisis-assess`, `arc-tracker`, `health-check`     |
| CRE       | 9     | `post-writer`, `multiplatform`, `privacy-guard`, `voice-audit` |
| GRO       | 8     | `career-path`, `competency-map`, `mentoring-track`             |
| MAT       | 4     | `loader`, `indexer`, `archive`, `rescore`                      |
| COM       | 3     | `git`, `health-check`, `rules`                                 |

The full catalog with per-skill descriptions is in [`CLAUDE.md`](./CLAUDE.md).

> ClaudeKit engineer-kit utility skills (`/ck:*`) are installed for development workflows (plan, cook, scout, review, …). They are invoked on demand and are not part of the character-profile domain.

---

## Getting started

1. **Orient an LLM agent:** open [`CLAUDE.md`](./CLAUDE.md). It is the single source of truth for architecture, rules, and workflow.
2. **Read the guides** under `docs/`:
   - `docs/getting-started.md`
   - `docs/framework-overview.md`
   - `docs/quick-reference.md`
   - `docs/user-manual-mat.md`, `docs/user-manual-psy.md`, `docs/user-manual-cre.md`
3. **Run skill scripts** with the project-local virtualenv (the project is self-contained):

   ```bash
   .claude/skills/.venv/bin/python3 .claude/skills/{framework}-{skill}/scripts/{script}.py [args]
   ```

---

## Conventions

- **Profiles:** 25-file universal nested schema per character (Rule 01).
- **Evidence:** every clinical claim is backed by tiered material (T1–T5) and CRAAP-scored (Rules 10, 11); show-don't-tell — never expose raw psychiatric terms in published content (Rule 02).
- **Confidentiality:** privacy tags + content boundaries gate what reaches published content (Rule 09).
- **Assets:** one folder per piece — `assets/{platform}/{YYMMDD}-{slug}/` with `post.txt`, `image-prompts.txt`, `images/`, `README.txt`.
- **Design principle:** scripts gather deterministically; the LLM judges. Scripts may over-flag by design.

---

## Documentation

| Topic                    | File                         |
| ------------------------ | ---------------------------- |
| LLM context (start here) | `CLAUDE.md`                  |
| Engineering rules        | `.claude/rules/`             |
| Framework overview       | `docs/framework-overview.md` |
| Getting started          | `docs/getting-started.md`    |
| Quick reference          | `docs/quick-reference.md`    |
| Domain rules (15)        | `docs/rules/`                |
| Clinical theory library  | `docs/references/INDEX.md`   |
