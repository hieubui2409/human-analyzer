---
name: psy:ref-scan
description: "Scan clinical reference library and find where theories apply in character profiles. When adding new references, discover enrichment opportunities across all 3 characters. Reverse of ref-audit: starts from theory → finds profile applications. Triggers: 'scan refs', 'where does this theory apply', 'reference scan', 'theory mapping', 'enrich profiles'."
argument-hint: "[--theory <name>|--new|--map|--gaps]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "validation"
  position: "utility"
  dependencies: ["psy:ref-audit"]
---

# Reference Scan — Theory-to-Profile Mapping

Start from clinical theories → find where they apply in character profiles. Discovers enrichment opportunities.

## Default (No Arguments)

`--map` — generate full theory-to-profile mapping.

## Flags

| Flag              | Purpose                                              |
| ----------------- | ---------------------------------------------------- |
| `--map`           | Full theory → profile mapping (default)              |
| `--theory <name>` | Scan one specific theory across all profiles         |
| `--new`           | Detect newly added references, scan for applications |
| `--gaps`          | Find theories with zero profile connections          |

## Workflow

### --map (Default)

1. Read `docs/references/INDEX.md` — list all 29+ theory files
2. For each theory file:
   a. Read file, extract key concepts and behavioral indicators
   b. `grep -rn` key terms across all `docs/profiles/*/`
   c. Score relevance: direct mention (3), behavioral match (2), potential fit (1)
3. Output mapping:

```markdown
## Theory-Profile Map

| Theory             | Nhân vật A            | Nhân vật B              | Nhân vật C         | Coverage  |
| ------------------ | --------------- | ---------------- | ------------- | --------- |
| Attachment Theory  | ★★★ (SOUL, REL) | ★★★ (SOUL, DARK) | ★★ (REL)      | Full      |
| Parentification    | ★★★ (SOUL)      | ★ (potential)    | ★★ (SOUL)     | Partial   |
| Defense Mechanisms | ★★ (CHAR)       | ★★ (DARK)        | ★ (potential) | Partial   |
| Savior Complex     | ★★★ (SOUL)      | —                | —             | Nhân vật A only |
| {theory}           | ...             | ...              | ...           | ...       |

★★★ = directly referenced ★★ = behavioral match ★ = potential fit — = not applicable

### Enrichment Opportunities

1. **Nhân vật B + Parentification**: Nhân vật B shows signs (caring for siblings, parentified role) but psychology/formulation.md doesn't reference this theory. Consider adding section.
2. **Nhân vật C + Defense Mechanisms**: darkness/traumas.md describes reactive behaviors that map to specific defense mechanisms. Currently unlabeled.
```

### --theory `<name>`

1. Find matching file in `docs/references/`
2. Read theory file, extract:
   - Core concept definition
   - Behavioral indicators
   - Diagnostic criteria (if applicable)
   - Vietnamese cultural context (if available)
3. Scan all 3 characters' profiles for:
   - Direct term mentions
   - Behavioral descriptions matching indicators
   - Situations where theory explains observed behavior
4. Report per-character applicability with evidence quotes

### --new

1. `git diff --name-only HEAD~10 -- docs/references/` — find recently added/modified refs
2. For each new/modified reference:
   - Run `--theory` scan for that reference
   - Flag high-relevance matches
3. Suggest profile enrichment actions

### --gaps

1. List all theories in `docs/references/`
2. For each, check if ANY profile file references it
3. Report theories with zero connections:

   ```
   ## Unused References

   These theories exist in docs/references/ but aren't referenced by any profile:

   1. docs/references/cognitive-dissonance.md — Potential fit: Nhân vật A's conflicting self-image
   2. docs/references/learned-helplessness.md — Potential fit: Nhân vật B's academic paralysis
   ```

## Safety

- READ-ONLY — never modifies profile or reference files
- Only outputs mapping reports
- Scope: theory-to-profile mapping for human-analyzer. Does NOT create or edit content.

## Examples

```bash
/psy:ref-scan                                   # full theory-profile map
/psy:ref-scan --theory "attachment theory"       # one theory across all
/psy:ref-scan --new                             # scan recently added refs
/psy:ref-scan --gaps                            # find unused theories
```

## See Also

- `/psy:ref-audit` — profile → reference direction (complementary)
- `/psy:crossref` — cross-character consistency
- `docs/references/INDEX.md` — reference library index
