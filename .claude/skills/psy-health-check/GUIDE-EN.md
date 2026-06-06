# psy:health-check — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have three character profiles spanning 25 files each. Some files are thick and rich; others are stubs or missing. Before you run psy:crossref or start creating content, you want to know: Which characters have solid, complete profiles? Which ones are thin and need work first?

## 2. Core concepts (the mental model)

- **25 universal files**: Every character has the same profile structure (INDEX.md, CURRENT-STATE.md, identity/, psychology/, relationships/, timeline/, darkness/, light/, evidence/, growth/). Missing even one is a gap.
- **Per-file scoring**: Scores aren't subjective (good vs bad writing). They're mechanical: Is the file there? How many lines? Are expected H2 sections present?
- **Category averages**: Psychology, identity, relationships, timeline, etc. — you see both per-file and per-category health, so you know which domains are weak.

## 3. Learning path

**First run:** `psy:health-check --character character-a` — see what one character's profile looks like.

**Full scan:** `psy:health-check --all` — see all three. Spot gaps across the corpus.

**Prioritize:** `psy:health-check --all --gaps-only` — show only files <80, so you know where to focus psy:wave.

## 4. Use cases (each = a sample conversation)

### Use case: Pre-crossref check

> You: "Character A and Character B profiles look done. Ready for cross-validation?"
> Skill: `psy:health-check --character character-a --character character-b`
> → Character A: 87/100, Character B: 72/100. psychology/formulation.md thin (35 lines). Recommend: expand before running psy:crossref.

### Use case: Identify missing files

> You: "I'm about to start Wave 2 on Character C. What do I need to fill first?"
> Skill: `psy:health-check --character character-c --gaps-only`
> → psychology/archetype.md missing (0/100). identity/media-coverage.md: 10 lines (10/100). Start here.

### Use case: Category-level audit

> You: "Which character needs the most work on relationships?"
> Skill: `psy:health-check --json | jq '.categories.relationships'`
> → Character B's relationships category: 65/100 (relationships/family.md = 80, relationships/hieu.md = 50). Character B-Character C relationship file missing.

## 5. Important caveats

- **Completeness ≠ quality**: A file with 100 lines scores higher than a 40-line file, even if the short one is tightly written and good. Use your judgment.
- **Cross-character files matter**: psy:health-check counts `relationships/{other-character}.md` files dynamically. If Character B-Character A file exists, it counts toward Character B's score.
- **Thin is a flag, not a failure**: A 50-line file scores ~50/100. That's not bad; it's "review and expand if needed." Not every file needs 200 lines.
- **Run before major validation**: Always run psy:health-check before psy:crossref. Thin profiles make crossref less useful (less data to compare).
