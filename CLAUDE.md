# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

---

## Project Purpose

Character profile documentation for storytelling and content creation.

---

## Directory Structure

```
docs/
├── profiles/           ← Character psychological and historical profiles
│   ├── character-a/
│   ├── character-b/
│   └── character-c/
├── materials/          ← Research materials, source docs
│   ├── character-a/
│   ├── character-b/
│   └── character-c/
├── references/         ← Clinical Psychology Theory Library (62 theories)
└── rules/              ← Modular rules (10 files: profile, clinical, content, materials, etc.)
plans/
├── 260331-1820-chien-support-reveal/ ← Nhân vật C support reveal plan
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

## Character Profiles

### Nhân vật A (`docs/profiles/character-a/`)

| File              | Content                               |
| ----------------- | ------------------------------------- |
| INDEX.md          | Quick reference                       |
| IDENTITY.md       | Basic info, education, career, family |
| SOUL.md           | Inner wounds, coping, Savior Complex  |
| CHARACTERISTIC.md | Personality, behavioral patterns      |
| TIMELINE.md       | Events 1997-2026                      |
| RELATIONSHIPS.md  | Family tree, relationship with Nhân vật B    |
| DARKNESS.md       | Trauma documentation                  |
| LIGHT.md          | Sources of hope                       |
| MILESTONES.md     | Key milestones                        |
| ACHIEVEMENTS.md   | Academic, scholarships, awards        |
| MEDIA-COVERAGE.md | Press timeline                        |
| WRITING-VOICE.md  | Tone, themes                          |
| INSPIRATION.md    | Transformation arc                    |

### Nhân vật B (`docs/profiles/character-b/`)

| File              | Content                            |
| ----------------- | ---------------------------------- |
| INDEX.md          | Quick reference                    |
| IDENTITY.md       | Basic info (DOB: 18/02/2008)       |
| SOUL.md           | Inner wounds, psychological traits |
| CHARACTERISTIC.md | Personality, behavioral patterns   |
| TIMELINE.md       | Events 2008-2025                   |
| RELATIONSHIPS.md  | Family, relationship with Nhân vật A     |
| DARKNESS.md       | Trauma, self-destructive behaviors |
| LIGHT.md          | Sources of hope, growth signs      |
| MILESTONES.md     | Key milestones                     |
| CONVERSATION.md   | Messenger conversations (OCR)      |

### Nhân vật C (`docs/profiles/character-c/`)

| File              | Content                             |
| ----------------- | ----------------------------------- |
| INDEX.md          | Quick reference                     |
| IDENTITY.md       | Basic info, education, family       |
| SOUL.md           | Inner wounds, psychological traits  |
| CHARACTERISTIC.md | Personality, behavioral patterns    |
| TIMELINE.md       | Events 2007-2026                    |
| RELATIONSHIPS.md  | Family tree, relationship with Nhân vật A |
| DARKNESS.md       | Trauma documentation                |
| LIGHT.md          | Sources of hope, growth signs       |
| MILESTONES.md     | Key milestones                      |

### Research Materials (`docs/materials/`)

- `character-a/` - Source materials and logs for Nhân vật A
- `character-b/` - Source materials and logs for Nhân vật B
- `character-c/` - Source materials, news, and letters for Nhân vật C

### Clinical Reference Library (`docs/references/`)

- `INDEX.md` - Master index of 62 clinical psychological theories (Attachment, Defense Mechanisms, Clinical Intervention, etc.)
- Focus: Ensuring clinical-grade character analysis without exposing raw psychiatric terms in social media content. Mapped to character actions and communication styles.

---

## Key Facts

**Nhân vật A**: Born 24/09/1997, Senior AI Engineer at VinSmart Future (06/2026~), prev. One Mount Group (08/2020-05/2026)
**Nhân vật B**: Born 18/02/2008, Grade 12 student, Tỉnh X
**Nhân vật C**: Born 14/05/2007, IT-E6 student at ĐHBK Hà Nội, Scholarship X F15 scholar
**Relationship (Nhân vật A - Nhân vật B)**: Sworn brothers (kết nghĩa) since 09/2025, 11-year age gap
**Relationship (Nhân vật A - Nhân vật C)**: Mentor - Mentee (Scholarship X interviewer)

---

## Rules (`docs/rules/`)

| #   | File                       | Scope                                             |
| --- | -------------------------- | ------------------------------------------------- |
| 01  | profile-structure          | Required files, schemas, size limits              |
| 02  | clinical-reference-usage   | Show-don't-tell, mandatory citation               |
| 03  | content-creation-pipeline  | 7-stage pipeline, platform guidelines             |
| 04  | materials-ingestion        | Source priority P1-P4, ingestion process          |
| 05  | wave-pipeline              | 3-wave protocol (Foundation→Deep Dive→Validation) |
| 06  | crisis-protocol            | Mental health crisis, DSM-5, risk levels          |
| 07  | narrative-twist-protocol   | Handling revealed falsehoods                      |
| 08  | cross-validation           | 4-dimension consistency, report format            |
| 09  | confidentiality-protocol   | Privacy tags, content boundaries                  |
| 10  | reference-library-standard | Reference schema, scientific rigor                |

---

## Lucas Skills (`.claude/skills/lucas-*`)

Project-specific skills for character profile management and content creation.

| Skill                   | Purpose                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `lucas:bootstrap`       | Load project context (--quick/--full/--character/--lite/--intent) |
| `lucas:session-state`   | Track session mode, phase, profiles touched                       |
| `lucas:classify`        | Risk classification (tiny/normal/high_risk)                       |
| `lucas:intake`          | Route work type → skill chain                                     |
| `lucas:exploring`       | 7-question exploration → CONTEXT.md                               |
| `lucas:post-writer`     | End-to-end content creation pipeline                              |
| `lucas:prompt-leverage` | 5-layer prompt strengthening                                      |
| `lucas:crossref`        | Cross-character validation (4 dimensions)                         |
| `lucas:ref-audit`       | Profile → reference accuracy check + --discover blind spots       |
| `lucas:ref-scan`        | Reference → profile coverage mapping                              |
| `lucas:ref-create`      | Create new reference files with mandatory schema                  |
| `lucas:materials`       | Smart material loading + extraction + --ingest pipeline           |
| `lucas:profile-lite`    | Compress profiles (~95% reduction)                                |
| `lucas:compounding`     | Extract session learnings → memory                                |
| `lucas:dream`           | Periodic memory consolidation                                     |
| `lucas:decisions`       | Append-only decision records                                      |
| `lucas:agent-memory`    | Per-agent calibration memory                                      |
| `lucas:git`             | Project-aware git operations                                      |
| `lucas:wave`            | 3-wave orchestration (Foundation→Deep Dive→Validation)            |
| `lucas:crisis-assess`   | DSM-5/ICD-11 crisis assessment + risk levels                      |
| `lucas:narrative-twist` | Handle revealed falsehoods, strikethrough + cascade               |
| `lucas:privacy-guard`   | Pre-publish privacy/confidentiality scan                          |
| `lucas:hypothesis`      | Predict character behavior given hypothetical events              |
| `lucas:repurpose`       | Adapt content across platforms                                    |
| `lucas:voice-audit`     | Audit content voice/tone consistency against WRITING-VOICE.md     |
| `lucas:arc-tracker`     | Track character growth trajectories, hypothesis vs reality        |

---

## Scripts Infrastructure

26 lucas skills share a Python utility library and 50+ supportive scripts.

### Shared Library (`.claude/scripts/lucas_lib/`)

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
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/lucas-{skill}/scripts/{script}.py [args]

# Shell scripts
bash .claude/skills/lucas-{skill}/scripts/{script}.sh [args]
```

### Design Principle

Scripts do **DETERMINISTIC GATHERING**; LLM does **HEURISTIC JUDGMENT**. Scripts may over-flag (false positives expected) — better to over-gather than miss genuine findings.

---

_Updated: 2026-05-16_
