# orc:decisions — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Three months ago, you decided Character B's core issue was avoidance, not anxious attachment. Now you're about to frame her differently in a new arc. Without a decision log, you might not remember why you chose that direction or whether you've reconsidered since. Decisions keeps a searchable record so you never lose the reasoning behind settled choices.

Each new decision gets a monotonic id (`DEC-1`, `DEC-2`, …) allocated atomically — if two agents record decisions at the same time, they cannot get the same id. When a decision supersedes an older one, the older record's status flips to `superseded` automatically so the history stays intact and the chain is traceable.

## 2. Core concepts (the mental model)

**Decisions are append-only.** Once recorded, they stay. You can mark them superseded if context changes, but you keep the history.

**Supersede chains.** When a ruling is revised, the new record carries `supersedes: DEC-n` and the old record's status is flipped to `superseded`. The `--list` output shows the lineage column so you can see which record retired which.

**Categories matter.** Arc decisions (where the story goes), interpretation decisions (how to read behavior), content decisions (angle choice), relationship decisions (how characters relate), clinical decisions (which framework applies).

**Rationale is key.** Recording not just the decision but WHY — which profiles informed it, which theories, what alternatives were rejected — makes it useful for future reference.

## 3. Learning path

**First decision:** After resolving a debate, `orc:decisions --record`. Describe what was decided, alternatives considered, and rationale. The skill allocates `DEC-1` and writes the file.

**Supersede a prior ruling:** `orc:decisions --record` again; when asked if it supersedes a prior decision, enter the id (e.g. `DEC-1`). The new record becomes `DEC-2`, and `DEC-1` is automatically marked superseded.

**Search decisions:** `orc:decisions --search "avoidance"` to find past decisions about avoidance patterns.

**Review character:** `orc:decisions --review` for a specific character to see all decisions about them.

**List recent:** `orc:decisions --list` to see what's been decided lately (with lineage column).

## 4. Use cases (each = a sample conversation)

### Use case: Record a major interpretation decision

> You: "I've decided Character B's avoidance is rooted in attachment anxiety, not pure avoidance. Record this."
>
> Skill: Interactive prompt gathers: What was decided? Character B's core issue = anxious-avoidant attachment. Alternatives? Pure avoidance (rejected because relationships matter to her), secure attachment (rejected because she shows avoidance triggers). Rationale? Psychology/formulation.md + defense-mechanisms.md show both patterns. Impact? Affects how we frame her arc. Allocates DEC-1, stores to decision log.

### Use case: Supersede an outdated ruling

> You: "We now have more evidence — Character B is actually secure-attached at work, anxious at home. Update the record."
>
> Skill: Records new decision as DEC-2, sets `supersedes: DEC-1`. DEC-1 status flips to superseded. List output shows `DEC-1 | superseded | superseded_by DEC-2`.

### Use case: Search for related decisions

> You: "Have we already decided about Character B and attachment before?"
>
> Skill: Searches decision log for "attachment" + "Character B". Finds 2 past decisions. Shows: date, id, decision, status (active/superseded). You review and decide: keep using old decision or create new one with updated reasoning.

### Use case: Review all decisions for a character

> You: "Show me everything we've decided about Character C."
>
> Skill: Lists all decisions mentioning Character C. Shows arc decisions (career path, storyline), relationship decisions (dynamic with Character A), clinical decisions (diagnostic interpretations). You spot potential conflicts or see the overall direction clearly.

## 5. Important caveats

- **Decisions are reference, not law.** If context changes (new evidence, character arc evolves), old decisions can be superseded. Record the change as a new decision.
- **Rationale quality matters.** Vague reasoning ("it felt right") is less useful than specific reasoning ("formulation.md section 2 + defense-mechanisms.md show both patterns").
- **Don't record everything.** Small tactical choices ("this scene has dialogue") don't need recording. Record major arc/interpretation/content decisions.
- **Search is keyword-based.** Searching for "attachment" won't find "anxious-avoidant" unless you used that exact phrase. Be thorough when recording.
