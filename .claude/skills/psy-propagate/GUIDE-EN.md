# psy:propagate — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You just updated Character A's timeline/overview.md to add a new mentoring milestone with Character C. But Character C's profile also has a timeline, and he should have the same event. And Character A-Character C's relationship file should note this interaction. Instead of manually hunting through files, this skill reads the relational graph, identifies Character C as "connected to Character A," and tells you: "Update Character C's timeline/overview.md" (HIGH priority) and "Update relationships/hieu.md in Character C's profile" (HIGH priority).

## 2. Core concepts (the mental model)

- **Graph-driven**: The relational graph (`docs/graph/relational-dynamics.md`) defines which characters are connected and how (high/medium/low bond strength). This skill uses that graph to detect propagation targets.
- **Section mapping**: Different sections propagate differently. A change to relationships/family.md triggers review of connected characters' relationships/family.md and relationship/{other-char}.md files. A change to timeline/overview.md triggers timeline review.
- **Verdict inheritance (optional)**: If a change fans across characters, verdict cache can reuse the source character's verdict for unchanged neighbors (economic only, never safety). Downstream tools decide.

## 3. Learning path

**First run:** `psy:propagate --character character-a` — see all propagation targets after Character A changes.

**Specific section:** `psy:propagate --character character-b --section relationships` — narrow to one section's propagation.

**Machine output:** `psy:propagate --character character-c --json` — parse programmatically for automation.

## 4. Use cases (each = a sample conversation)

### Use case: Full-character propagation

> You: "I rewrote psychology/formulation.md for Character A (core wound explanation). What else needs updating?"
> Skill: `psy:propagate --character character-a`
> → Detected: Character B (HIGH: relationships/hieu.md may need updates reflecting new understanding), Character C (MEDIUM: timeline may be affected if Character A's wounds trigger events).

### Use case: Relationship-specific cascade

> You: "Character B's family.md now says 'father was absent,' not 'dead.' What cascades?"
> Skill: `psy:propagate --character character-b --section relationships`
> → Character A's relationships/hoa.md should note: "Character B's father absent, not deceased" (affects how Character A supports Character B). Character C: no direct relationship, skip.

### Use case: Timeline propagation

> You: "Added Oct 2025 kết nghĩa event to Character A's timeline."
> Skill: `psy:propagate --character character-a --section timeline`
> → Character B's timeline/overview.md must have matching entry (HIGH priority). Also check Character B's relationships/hieu.md for milestone mention.

## 5. Important caveats

- **Propagation is a suggestion, not an order**: The skill identifies targets, but you decide which to update. Not all cascades require action.
- **Graph determines targets**: If the relational graph doesn't list a connection, propagate won't suggest it. Update the graph if you add new relationships.
- **Cross-character files are dynamic**: The skill discovers `relationships/{other-char}.md` files dynamically. If such a file doesn't exist yet, propagate won't list it, but you may need to create it.
- **Manual validation after propagation**: After updating cascaded files, run `psy:crossref --pair {src} {target}` to confirm the update is symmetric and consistent.
