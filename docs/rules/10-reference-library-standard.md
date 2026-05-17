# Reference Library Standard

Standards for creating, maintaining, and using clinical psychological theory files in `docs/references/`.

## NGUYÊN TẮC TỐI THƯỢNG (Mandatory Clinical Referencing)

Three absolute rules for all psychological analysis in this project:

### 1. Trích dẫn bắt buộc (Mandatory Citation)

Every psychological finding, defense mechanism, behavior pattern, and trauma indicator in profiles MUST be linked to `docs/references/` via specific Markdown link.

```markdown
[Hội chứng Cứu rỗi](../../references/savior-complex.md)
```

No "armchair psychology" — every analysis must have a theory backing it.

### 2. Xóa "vùng mù" lý thuyết (Eliminate Blind Spots)

When a character's psychological state or behavior appears irrational but no existing theory in the library covers it:

1. **MUST** create the new theory file in `docs/references/` FIRST
2. **THEN** link it to the character profile
3. Never analyze a behavior without a theory anchor

### 3. Tính khoa học tuyệt đối (Scientific Rigor)

Every theory file MUST cite authoritative evidence-based sources:

- DSM-5, ICD-11 diagnostic criteria
- Freudian psychoanalysis, Adler's individual psychology
- Bowlby/Main attachment theory
- Peer-reviewed psychiatric research
- No unsourced speculation

## Reference File Schema

Every file in `docs/references/` MUST follow this structure:

```markdown
# {Tên Học thuyết (Tiếng Việt & Tiếng Anh)}

> **Định nghĩa ngắn (TL;DR)**: "{1-2 sentence core meaning}"

## 1. Định nghĩa (Definition)

- Core clinical concept
- **Nguồn trích dẫn (Mandatory)**: DSM-5, ICD-11, authoritative source + link

## 2. Nguồn gốc (Origin)

- Root causes, environments, conditions that produce this pattern

## 3. Cơ chế (Mechanism)

- How it works: psychological mechanism or clinical symptoms

## 4. Case Study áp dụng vào Dự án

### {Character Name}

- **Bối cảnh / Triggers**: Events in profile that activate this
- **Biểu hiện thực tế**: Observable character behaviors
- **Phân tích lâm sàng**: Why the behavior maps to the theory
```

## Index Maintenance

`docs/references/INDEX.md` MUST be updated whenever:

- A new reference file is created
- A reference file is significantly modified
- Character applicability changes

Index organization: grouped by category (Disorders, Attachment, Defense Mechanisms, Cultural Context, Interventions).

## Naming Conventions

- File names: kebab-case English name of the theory
- Examples: `savior-complex.md`, `anxious-attachment.md`, `complex-ptsd.md`
- Vietnamese names go in the file title, not the filename

## Bidirectional Validation

### Profile → References (ref-audit direction)

Every clinical term in profiles should trace to a reference file:

- `psy:ref-audit` scans profiles for clinical terms
- Classifies: ACCURATE, UNREFERENCED, MISAPPLIED, INFORMAL

### References → Profiles (ref-scan direction)

Every reference file should be applied to at least one character:

- `psy:ref-scan` maps theories to profile applications
- Flags orphaned theories (in library but never referenced)
- Flags gaps (theories that should apply but aren't linked)

## Vietnamese Cultural Adaptation

Every reference MUST include a section on how the theory manifests in Vietnamese family/cultural context:

- "Nhịn" (endurance) as cultural coping
- Filial piety dynamics
- Face-saving behaviors
- Collective vs. individual identity

## Accessible Language Mapping

Each reference SHOULD include a clinical → colloquial translation table for use in social media content. See `02-clinical-reference-usage.md` for the master mapping table.
