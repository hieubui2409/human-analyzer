---
name: psy:profile-compare
description: "Side-by-side character profile comparison — extract a specific dimension (e.g. defense-mechanisms, attachment-style) from 2+ characters and output a structured comparison table. Triggers: 'compare profiles', 'side by side', 'compare dimensions', 'compare characters', 'profile comparison'."
argument-hint: "--dimension <section-name> [--characters <char1,char2>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "analysis"
  dependencies: []
---

# psy:profile-compare — Side-by-Side Profile Comparison

Extract a specific profile dimension from multiple characters and render a structured comparison table for clinical analysis.

## Default (No Arguments)

Prompt for dimension and characters to compare.

## Flags

| Flag                       | Purpose                                    |
| -------------------------- | ------------------------------------------ |
| `--dimension <name>`       | Profile section to compare (required)      |
| `--characters <c1,c2,...>` | Characters to compare (default: all three) |
| `--json`                   | Output as JSON                             |

## Available Dimensions

Maps to profile file paths under `docs/profiles/{character}/`:

| Dimension arg          | File Path                                                                         |
| ---------------------- | --------------------------------------------------------------------------------- |
| `defense-mechanisms`   | `psychology/defense-mechanisms.md`                                                |
| `attachment-style`     | `psychology/attachment-style.md`                                                  |
| `core-wounds`          | `psychology/core-wounds.md`                                                       |
| `formulation`          | `psychology/formulation.md`                                                       |
| `diagnostics`          | `psychology/diagnostics.md`                                                       |
| `archetype`            | `psychology/archetype.md`                                                         |
| `growth-edges`         | `psychology/growth-edges.md`                                                      |
| `cultural-formulation` | `psychology/cultural-formulation.md`                                              |
| `traumas`              | `darkness/traumas.md`                                                             |
| `strengths-hope`       | `light/strengths-hope.md`                                                         |
| `family`               | `relationships/family.md`                                                         |
| `relationships/<char>` | `relationships/{other-character}.md` — discovered via `list_relationship_files()` |
| `timeline`             | `timeline/overview.md`                                                            |
| `writing-voice`        | `identity/writing-voice.md`                                                       |

## Workflow

### Step 1: Extract Sections

1. Run `scripts/extract-dimension-for-comparison.py --dimension <name> --characters <slugs>`
2. For each character: read the corresponding file
3. Extract top-level H2 sections and their content summaries

### Step 2: Build Comparison Table

Render side-by-side markdown table with key findings per character.

### Step 3: Output

```
## Profile Comparison: {dimension}

**Characters:** {char1} | {char2} [| char3]
**Date:** {YYYY-MM-DD}

### {Dimension Title}

| Aspect             | Nhân vật A                      | Nhân vật B                      | Nhân vật C                    |
|--------------------|--------------------------|--------------------------|--------------------------|
| Primary pattern    | {extracted}               | {extracted}               | {extracted}              |
| Secondary pattern  | {extracted}               | {extracted}               | {extracted}              |
| Key dynamic        | {extracted}               | {extracted}               | {extracted}              |
...

### Clinical Observations

- **Contrast:** {notable differences}
- **Overlap:** {shared patterns}
- **Interaction dynamic:** {how these patterns interact between characters}

### Source Files

| Character | File | Lines |
|-----------|------|-------|
| Nhân vật A | psychology/defense-mechanisms.md | {n} |
...
```

## Scripts

| Script                                        | Purpose                                         |
| --------------------------------------------- | ----------------------------------------------- |
| `scripts/extract-dimension-for-comparison.py` | Read dimension files, extract sections, compare |

## Safety

- READ-ONLY — never modifies profile files
- Domain boundary: `docs/profiles/` only

## Examples

```bash
/psy:profile-compare --dimension defense-mechanisms
/psy:profile-compare --dimension attachment-style --characters hieu,hoa
/psy:profile-compare --dimension core-wounds --characters hieu,hoa,chien
/psy:profile-compare --dimension diagnostics --json
```

## See Also

- `psy:crossref` — consistency validation between character pairs
- `psy:health-check` — completeness before comparing
- `psy:ref-audit` — clinical accuracy of the sections being compared
