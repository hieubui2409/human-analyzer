---
title: MAT Pipeline — Materials Standardization Framework
version: "1.0"
created: "2026-05-17"
---

# Rule 11: MAT Pipeline — Materials Standardization Framework

## Overview

The MAT (Materials) framework standardizes how raw materials enter the system, get analyzed, and integrate into psychological profiles. Every material follows the same pipeline regardless of source type.

## 5-Stage Pipeline

```
┌─────────────────────────────────────────────────────┐
│ Stage 1: INGESTION & PREPROCESSING                   │
│   Input: Raw materials (chat logs, letters, PDFs)    │
│   → Normalize formats (UTF-8, line endings)          │
│   → Create material ID & YAML frontmatter skeleton   │
│   → Tag confidentiality level                        │
│   → Assign source category (primary→auxiliary)       │
│   Output: docs/materials/{character}/{file}.md       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ Stage 2: OCR & TRANSCRIPTION (if needed)             │
│   → Images/scans: OCR extraction                     │
│   → Audio: Speech-to-text transcription              │
│   → Handwritten: AI-powered HTR                      │
│   → LLM grammar/spelling correction                  │
│   → Confidence scoring per section                   │
│   Output: processing_status → "extracted"            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ Stage 3: EXTRACTION & STRUCTURING                    │
│   → Parse into sections (metadata, content)          │
│   → Extract key entities (dates, names, locations)   │
│   → Identify psychological constructs (LLM)          │
│   → Map to clinical reference library                │
│   → Flag potential contradictions                    │
│   Output: processing_status → "analyzed"             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ Stage 4: VALIDATION & CROSS-REFERENCE                │
│   → Compare against existing profile data            │
│   → Contradiction detection with severity scoring    │
│   → CRAAP test for source reliability                │
│   → Cross-validate with other materials              │
│   Output: processing_status → "validated"            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ Stage 5: INTEGRATION                                 │
│   → Merge findings into profile sections             │
│   → Update cross-reference links                     │
│   → Trigger PSY.refresh event (→ ORC orchestration)  │
│   → Archive processed material                       │
│   Output: processing_status → "integrated"           │
└─────────────────────────────────────────────────────┘
```

## Evidence Tiers

| Tier | Category   | Confidence | Weight | Examples                                       |
| ---- | ---------- | ---------- | ------ | ---------------------------------------------- |
| 1    | Primary    | High       | 1.0    | Direct testimony, interviews, personal letters |
| 2    | Secondary  | High       | 0.9    | Professional assessments, clinical evaluations |
| 3    | Tertiary   | Medium     | 0.7    | News articles, social media, messenger logs    |
| 4    | Contextual | Med-Low    | 0.5    | Third-party accounts, family testimony         |
| 5    | Auxiliary  | Low        | 0.3    | Inference from metadata, timestamps            |

## CRAAP Test

Every material MUST be assessed on 5 dimensions:

1. **Currency** — When was the material created/captured? Older ≠ less valuable (historical context matters)
2. **Relevance** — Direct connection to which profile sections?
3. **Authority** — Creator's credentials and proximity to subject
4. **Accuracy** — Can claims be cross-referenced? Internal consistency?
5. **Purpose** — Clinical note vs. social media post vs. personal reflection

**Scoring scale (canonical):** Each dimension is scored **1-5**. The `craap_score` frontmatter is a nested mapping holding all 5 dimensions plus `total`, where `total` = sum of the 5 dimensions (range 5-25). CRAAP is a **quality gate** — it does NOT determine the evidence tier. Evidence tier (T1-T5) is derived from `source_category` (primary→T1, secondary→T2, tertiary→T3, contextual→T4, auxiliary→T5); CRAAP total is an orthogonal quality score used for integration gating (threshold ≥ 15/25).

```yaml
craap_score:
  currency: 5
  relevance: 3
  authority: 3
  accuracy: 3
  purpose: 3
  total: 17
```

## Processing States

```
raw → extracted → analyzed → validated → integrated → archived
 │                                                        │
 └── Material enters system                               └── Superseded or fully merged
```

State transitions are one-directional. A material cannot move backward.

## Contradiction Detection

When new material contradicts existing profile data:

1. **Flag** — Record in `contradiction_flags` frontmatter field
2. **Severity** — Rate: low (minor detail), medium (behavioral pattern), high (core trait), critical (safety-relevant)
3. **Resolution** — Options: newer-supersedes, context-dependent, coexist-as-complexity, requires-investigation
4. **Event** — Trigger `MAT.contradiction` event → ORC orchestration handles downstream

## Material Types

| Type             | Typical Tier | Description                           |
| ---------------- | ------------ | ------------------------------------- |
| conversation_log | 3            | Messenger, chat, SMS transcripts      |
| letter           | 1            | Personal letters, emails              |
| interview        | 1-2          | Structured or unstructured interviews |
| news_article     | 3            | Press coverage, media reports         |
| screenshot       | 3-4          | Screen captures of social media, apps |
| clinical_note    | 2            | Professional assessments, evaluations |
| observation      | 4            | Third-party behavioral observations   |
| document         | 2-3          | Official documents, certificates      |

## Directory Structure

```
docs/materials/{character}/
├── raw/                    ← Unprocessed source files
├── analyzed/               ← LLM-analyzed materials with full frontmatter
└── archive/                ← Fully integrated, read-only
```

## Skills

| Skill         | Purpose                                                 |
| ------------- | ------------------------------------------------------- |
| `mat:loader`  | Load, classify, and prepare materials for analysis      |
| `mat:indexer` | Index materials, detect duplicates, find contradictions |

## Integration with PSY & CRE

- **MAT → PSY**: When material reaches "integrated" status, triggers `PSY.refresh` for affected profile sections
- **MAT → CRE**: Contradiction detection triggers `CRE.recalibrate` if voice/tone assumptions change
- **Domain boundary**: MAT ONLY writes to `docs/materials/`. Profile updates go through PSY framework.
