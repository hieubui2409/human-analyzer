---
name: psy:narrative-twist
description: "Handle revealed falsehoods and narrative corrections in character profiles. Apply strikethrough, ⚠️ TWIST markers, and cascade updates across all affected files + cross-character profiles. Use when new source data invalidates a previously established fact. Triggers: 'twist', 'revelation', 'falsehood revealed', 'story changed', 'narrative correction', 'invalidated fact'."
argument-hint: "[--character <name> --fact '<old fact>' --truth '<new truth>' --source '<source>'|--scan|--list]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "wave-2-supplement"
  dependencies: ["psy:crossref"]
---

# Narrative Twist Handler

Implement `docs/rules/07-narrative-twist-protocol.md` — manage revealed falsehoods in profiles.

## When to Use

- New source data invalidates a previously established "fact"
- A character's public story is revealed to be fabricated
- A relationship's true nature is disclosed
- Auto-triggered by `psy:wave` Wave 2 when contradictions detected

## Flags

| Flag                 | Purpose                                           |
| -------------------- | ------------------------------------------------- |
| `--character <name>` | Target character                                  |
| `--fact '<old>'`     | The invalidated fact (quoted)                     |
| `--truth '<new>'`    | The revealed truth (quoted)                       |
| `--source '<src>'`   | Source info: priority level + date                |
| `--scan`             | Scan all profiles for potential unresolved twists |
| `--list`             | List all existing TWIST markers across profiles   |

## Twist Application Workflow

### Step 1: Identify Scope

Given the old fact and new truth:

1. Grep all profile files for the old fact (exact + fuzzy match)
2. List every file containing the invalidated information
3. Identify cross-character files affected

### Step 2: Apply Strikethrough + Marker

In each affected file, replace old fact:

```markdown
~~{old fact}~~
⚠️ TWIST: {new truth} [Source: P{N}, {date}]
```

**Rules:**

- Do NOT delete old narrative
- Strikethrough preserves history
- TWIST marker immediately follows
- Source and date are mandatory

### Step 3: Update Timeline

Add entries showing BOTH perspectives:

- When the character believed/presented the old narrative
- When the truth was revealed
- Who revealed it and how

### Step 4: Cascade Updates

Check ALL profile files for the affected character:

| File                                 | What to check                                                      |
| ------------------------------------ | ------------------------------------------------------------------ |
| INDEX.md                             | Summary reflects new truth                                         |
| `identity/core.md`                   | Facts corrected                                                    |
| `psychology/formulation.md`          | Psychological analysis updated if twist affects core wound         |
| `psychology/defense-mechanisms.md`   | Behavioral patterns adjusted                                       |
| `timeline/overview.md`               | Event history includes both old belief and revelation              |
| `relationships/family.md`            | Relationship nature corrected                                      |
| `relationships/{other-character}.md` | Cross-character files — discovered via `list_relationship_files()` |
| `darkness/traumas.md`                | Trauma updated if twist reveals new wound                          |
| `light/strengths-hope.md`            | Protective factors adjusted if twist changes them                  |
| `milestones.md`                      | Revelation added as milestone if significant                       |

### Step 5: Cross-Character Impact

For each other character affected:

1. Update their `relationships/family.md`
2. Add timeline entry for when THEY learned the truth
3. Document psychological impact on them
4. Run `psy:crossref --pair {char1} {char2}` to validate symmetry

### Step 6: Confidentiality Check

If twist involves private information:

- Add `[PRIVATE]` tag to twist details
- Check `docs/rules/09-confidentiality-protocol.md` for disclosure rules
- Ensure twist details don't leak into content marked Public/Persona

### Step 7: Report

Output summary:

```
## Twist Applied: {short description}
Character: {name}
Old narrative: {old fact}
New truth: {new truth}
Source: P{N}, {date}
Files modified: {count} ({list})
Cross-character updates: {list}
Confidentiality: {public/private}
```

## --scan (Detect Potential Twists)

Scan all profiles for:

1. `[DISPUTED]` tags that might be resolved by new materials
2. `[UNCERTAIN]` facts that need verification
3. Contradictions between characters' versions of same event
4. Existing ⚠️ TWIST markers for completeness check

Output list of potential twist candidates.

## --list (Show Existing Twists)

Grep all profiles for `⚠️ TWIST` markers. Output:

```
## Existing Narrative Twists
1. [Nhân vật C] Mẹ kế narrative → abandoned at 11 (timeline/overview.md:L45)
2. [Nhân vật C] Huyền = mentor only → mentor + lover (relationships/family.md:L120)
...
```

## Safety

- NEVER delete old narrative — strikethrough only
- ALWAYS preserve source attribution
- Cross-character updates are MANDATORY, not optional
- `psy:crossref` validation after twist is MANDATORY — do not report success until crossref confirms symmetry
- Update `mpc:session-state` with twist event for session recovery
- Run `psy:ref-audit --character <name>` if twist affects SOUL/DARKNESS (clinical terms may need re-validation)
- Scope: narrative twist management in profiles. Does NOT create content or modify references.

## See Also

psy:crossref, psy:wave, cre:privacy-guard
