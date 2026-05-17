---
name: psy:ref-create
description: "Create new clinical psychological theory reference files in docs/references/ following mandatory schema. Use when a character behavior needs theoretical backing but no existing reference covers it (NGUYÊN TẮC TỐI THƯỢNG rule 2: eliminate blind spots). Triggers: 'new reference', 'create theory', 'add reference', 'new theory', 'blind spot', 'missing theory', 'ref create'."
argument-hint: "<theory-name> [--character <name>|--quick|--from-behavior '<description>']"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "clinical"
  position: "reference-authoring"
  dependencies: ["psy:ref-audit", "psy:ref-scan"]
---

# Reference File Creator

Implement `docs/rules/10-reference-library-standard.md` — scaffold and populate new theory files.

## When to Use

- Character behavior identified but no theory in library covers it
- `psy:ref-audit` flags UNREFERENCED clinical terms
- `psy:ref-audit --discover` finds new terms in materials
- Wave 2 analysis reveals patterns needing theoretical backing

## Flags

| Flag                       | Purpose                                                    |
| -------------------------- | ---------------------------------------------------------- |
| `<theory-name>`            | Name of theory to create (English, kebab-case)             |
| `--character <name>`       | Pre-fill case study for this character                     |
| `--quick`                  | Minimal scaffold — definition + mechanism only             |
| `--from-behavior '<desc>'` | Reverse-engineer: describe behavior → find matching theory |

## Workflow

### Standard Creation

1. **Research phase**: Search for the theory in authoritative sources:
   - DSM-5, ICD-11 criteria
   - Peer-reviewed psychological literature
   - Established psychoanalytic frameworks (Freud, Adler, Bowlby, Main)

2. **Scaffold file** at `docs/references/{theory-name}.md`:

```markdown
# {Tên Học thuyết (Tiếng Việt & Tiếng Anh)}

> **Định nghĩa ngắn (TL;DR)**: "{1-2 sentence core meaning}"

## 1. Định nghĩa (Definition)

- {Core clinical concept}
- **Nguồn trích dẫn (Mandatory)**: {DSM-5/ICD-11/Author, with citation}

## 2. Nguồn gốc (Origin)

- {Root causes, environments, conditions}

## 3. Cơ chế (Mechanism)

- {How it works: psychological mechanism or clinical symptoms}

## 4. Bối cảnh Văn hóa Việt Nam (Vietnamese Cultural Context)

- {How this theory manifests in Vietnamese family dynamics}
- {Cultural factors: "Nhịn", filial piety, face-saving}

## 5. Ngôn ngữ đại chúng (Accessible Language Mapping)

| Thuật ngữ lâm sàng | Ngôn ngữ MXH            |
| ------------------ | ----------------------- |
| {clinical term}    | {colloquial Vietnamese} |

## 6. Case Study áp dụng vào Dự án

### {Character Name}

- **Bối cảnh / Triggers**: {Events in profile}
- **Biểu hiện thực tế**: {Observable behaviors}
- **Phân tích lâm sàng**: {Why behavior maps to theory}
```

3. **Update INDEX**: Add entry to `docs/references/INDEX.md` in correct category
4. **Link in profile**: Add reference link in character's SOUL.md/DARKNESS.md where applicable
5. **Verify**: Run `psy:ref-scan --theory {name}` to confirm linkage

### --from-behavior (Reverse Engineering)

1. User describes a behavior pattern observed in character
2. Search existing references for matches:
   - If match found → suggest linking instead of creating
   - If no match → propose theory name + research
3. Ask user to confirm before creating
4. Proceed with standard creation

### --quick (Minimal)

Create file with sections 1-3 only. Mark sections 4-6 as `[TODO]`.

## Naming Convention

- Filename: kebab-case English name
- Examples: `identity-fusion.md`, `benevolence-fatigue.md`, `sincere-misbelief.md`
- Vietnamese name goes in file title, not filename

## Validation

After creation:

1. Verify file matches mandatory schema (all sections present)
2. Verify at least one authoritative citation
3. Verify INDEX.md updated
4. Verify at least one profile links to this reference

## Safety

- Every theory MUST have scientific backing — no speculative theories without citation
- This skill creates reference files, does NOT modify profiles (linking is separate step)
- Scope: reference file creation. Does NOT handle content creation, profile updates, or validation.

## See Also

psy:ref-audit, psy:ref-scan
