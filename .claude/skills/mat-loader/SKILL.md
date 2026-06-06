---
name: mat:loader
description: "MAT framework material loader — ingest, classify, frontmatter, and normalize source materials into docs/materials/. Replaces mat:materials with MAT-compliant pipeline (5-stage, evidence tiers, CRAAP test, processing states). Triggers: 'load materials', 'ingest material', 'new source', 'mat load'."
argument-hint: "[--list|--character <name>|--file <path>|--ingest <path>|--extract <topic>|--new|--status]"
metadata:
  author: hieubt
  version: "2.0.0"
  category: "mat-framework"
  position: "pipeline-stage-1-2"
  dependencies: []
  replaces: "mat:materials"
---

# mat:loader — Material Loading & Ingestion (MAT Framework)

Load, classify, and normalize source materials into `docs/materials/` with MAT-compliant frontmatter.

## MAT Pipeline Position

```
[Stage 1: Ingestion] → [Stage 2: Classification] → Stage 3 → Stage 4 → Stage 5
     mat:loader              mat:loader            mat:indexer  (manual)  (auto)
```

mat:loader owns Stages 1-2: receiving raw materials and assigning frontmatter.

## Default (No Arguments)

`--list` — show available materials per character with processing status.

## Flags

| Flag                 | Purpose                                                     |
| -------------------- | ----------------------------------------------------------- |
| `--list`             | Inventory all materials per character with status (default) |
| `--character <name>` | List + summarize one character's materials                  |
| `--file <path>`      | Load and summarize specific file                            |
| `--ingest <path>`    | Full MAT pipeline Stage 1-2: classify→frontmatter→normalize |
| `--extract <topic>`  | Search materials for specific topic/fact                    |
| `--new`              | Materials added since last session                          |
| `--status`           | Show processing_status breakdown across all materials       |

## Materials Directory Structure

```
docs/materials/
├── character-a/    — transcripts, clinical notes, personal logs
├── character-b/    — conversation logs, family context
└── character-c/ — interview transcripts, letters, news articles
```

## MAT-Compliant Frontmatter Schema

Every material file MUST have this frontmatter (authoritative contract: `.claude/schemas/material-frontmatter.schema.json`):

```yaml
---
# --- Required fields ---
material_id: CHAR_SLUG_MAT_NNN         # unique ID pattern: [A-Z0-9_]+_MAT_[0-9]+
character: character-a              # kebab-case character slug
material_type: conversation_log        # conversation_log|letter|interview|news_article|
                                       # screenshot|clinical_note|observation|document
title: "Human-readable title"
source_category: primary               # primary|secondary|tertiary|contextual|auxiliary
source_reliability: high               # high|medium|low
source_creator: unknown                # who created the source
captured_date: YYYY-MM-DD             # ISO date when material was captured
processing_status: raw                 # raw|extracted|analyzed|validated|integrated|archived
confidentiality: private               # public|shared|private|restricted
last_updated: YYYY-MM-DD
updated_by: mat:loader

# --- Optional fields (common) ---
evidence_tier: T1                      # T1-T5 — derived from source_category; set by LLM
craap_score:
  currency: 1-5
  relevance: 1-5
  authority: 1-5
  accuracy: 1-5
  purpose: 1-5
  total: 5-25
content_tags: []                       # kebab-case topic tags
psychology_constructs: []              # construct slugs from docs/references/
references: []                         # reference slugs
cross_characters: []                   # other character slugs mentioned
---
```

**Key distinctions from older docs:**
- Date key is `captured_date` (not `date_created` or `date_range`)
- Confidentiality values are `public|shared|private|restricted` (not `internal|confidential`)
- No `privacy_flags` or `tags` top-level keys — use `content_tags` for tags
- `source_category` values are plain words (`primary`…`auxiliary`), not `P1-primary` codes
- Evidence tier is **derived from source_category** by the LLM/code; CRAAP is a quality gate, not tier source

## Workflow: --ingest `<path>` (MAT Stage 1-2)

### Stage 1: Ingestion

1. Read the file at `<path>`
2. Detect document type from content patterns:

   | Type         | Detection Signal                                     |
   | ------------ | ---------------------------------------------------- |
   | transcript   | Timestamps, speaker labels, dialogue format          |
   | letter       | "Kính gửi", epistolary format, recipient header      |
   | conversation | Messenger-style, short messages, emoji, timestamps   |
   | clinical     | Medical/psychological terminology, assessment tables |
   | news         | Article structure, publication metadata, byline      |
   | interview    | Q&A format, interviewer/interviewee labels           |
   | document     | Official records, certificates, forms                |
   | media        | Image descriptions, video transcripts                |

3. Detect character from content (names, pronouns, context clues)
4. Detect date range from timestamps/references in content

### Stage 2: Classification

1. Assign `source_category` per evidence hierarchy:
   - P1: Direct statement by character (self-report, personal letter)
   - P2: Documentary evidence (news, official records)
   - P3: Conversational context (messenger logs, group chats)
   - P4: Analytical interpretation (clinical notes, interviewer observations)
   - P5: Auxiliary (secondary sources, hearsay)

2. Assign `evidence_tier`:
   - T1: Primary self-report — highest reliability
   - T2: Corroborated observation — cross-verified
   - T3: Single observer — needs corroboration
   - T4: Indirect/reported — limited reliability
   - T5: Speculative/theoretical — framework only

3. Run CRAAP test scoring (1-5 per dimension):
   - Currency: How recent is the information?
   - Relevance: How relevant to character profile?
   - Authority: Who is the source? How credible?
   - Accuracy: Can facts be verified?
   - Purpose: Why was this document created?

4. Scan for confidentiality flags per `docs/rules/09-confidentiality-protocol.md`
5. Set `processing_status: raw`
6. Inject frontmatter into file
7. Move file to `docs/materials/{character}/` with standardized name

### Output

```
## MAT Ingestion Report: {filename}

**Type:** {material_type}
**Source:** {source_category} — {reason}
**Evidence Tier:** {evidence_tier}
**Character:** {character}
**Date Range:** {date_range}
**CRAAP Score:** {total}/25

### Frontmatter Injected ✓
### File Moved → docs/materials/{character}/{new_name}

### Key Facts Extracted
| # | Fact | Line | Tier | Confidence | Profile Target |
|---|------|------|------|------------|----------------|

### Contradictions Detected
| Material says | Profile says | File | Severity |
|--------------|-------------|------|----------|

### Next Step
→ Run `mat:indexer` for cross-reference validation (Stage 3)
```

## Workflow: --list (Default)

1. Run `scripts/inventory-materials-with-frontmatter-status.py`
2. For each file: name, type, tier, status, lines, modified date
3. Group by character, color-code by processing_status

## Workflow: --status

Show processing pipeline status:

```
## MAT Pipeline Status

| Status     | Count | Files                    |
|-----------|-------|--------------------------|
| raw        | 5     | file1.md, file2.md, ...  |
| extracted  | 12    |                          |
| analyzed   | 8     |                          |
| validated  | 15    |                          |
| integrated | 3     |                          |
| archived   | 0     |                          |

Bottleneck: 5 files stuck at 'raw' — run mat:loader --ingest to process
```

## Scripts

| Script                                                            | Purpose                                         |
| ----------------------------------------------------------------- | ----------------------------------------------- |
| `scripts/inventory-materials-with-frontmatter-status.py`         | Inventory with MAT frontmatter + status parsing |
| `scripts/inventory-materials-with-type-detection.py`             | Inventory with file type detection              |
| `scripts/validate-material-frontmatter-against-schema.py`        | Validate frontmatter against schema             |
| `scripts/generate-craap-score-template-for-material.py`          | Generate CRAAP scoring template for a file      |
| `scripts/detect-duplicate-materials-by-size-and-content-hash.py` | Detect duplicate files by hash                  |

## Safety

- READ-ONLY for --list, --character, --file, --extract, --new, --status
- WRITE for --ingest: injects frontmatter, moves files (material files only)
- Never modifies profile files or reference files
- Domain boundary: `docs/materials/` only

## Examples

```bash
/mat:loader                                    # list all with status
/mat:loader --character character-c                  # Nhân vật C's materials
/mat:loader --ingest ~/new-transcript.md       # full Stage 1-2
/mat:loader --extract "gambling"               # search topic
/mat:loader --status                           # pipeline status
```

## See Also

- `mat:indexer` — Stage 3-4: contradiction detection + cross-reference
- `orc:bootstrap` — context loading (materials complement profiles)
- `orc:intake` — workflow routing (material ingestion route)
- `.claude/schemas/material-schema.yaml` — full frontmatter schema
- `docs/rules/11-mat-pipeline.md` — pipeline documentation
