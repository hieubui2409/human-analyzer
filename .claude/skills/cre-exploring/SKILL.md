---
name: cre:exploring
description: "Structured exploration before content planning. Ask one question at a time to lock decisions — character focus, angle, platform, tone, clinical framing. Outputs CONTEXT.md in plan directory. Use before planning content, arc development, or profile updates. Triggers: 'explore', 'figure out', 'what should we write about', 'explore angle', 'content idea'."
argument-hint: "[topic] [--resume|--reset]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "pre-planning"
  dependencies: []
---

# Structured Exploration

Turn fuzzy content intent → locked decisions via sequential questions. One question at a time, each building on previous answers.

## Default (No Arguments)

Start fresh exploration. Ask user for initial topic/intent.

## Flags

| Flag       | Purpose                                     |
| ---------- | ------------------------------------------- |
| (topic)    | Start exploration with given topic          |
| `--resume` | Resume from existing CONTEXT.md in plan dir |
| `--reset`  | Discard current exploration, start fresh    |

## Decision Sequence

Ask ONE question at a time. Wait for answer before next question.

### Q1: Character Focus

```
Which character is this about?
- Nhân vật A (Nhân vật A)
- Nhân vật B (Nhân vật B)
- Nhân vật C (Nhân vật C)
- Cross-character (relationship dynamic)
- None (general topic)
```

After answer → read relevant INDEX.md for context.

### Q2: Content Type

```
What type of work?
- Social media post (LinkedIn/Facebook/Instagram/TikTok/Twitter)
- Long-form content (blog/article/YouTube script)
- Profile update (psychology/, identity/, timeline/, relationships/)
- Arc development (new storyline or character progression)
- Research (clinical theory, background material)
```

### Q3: Angle / Theme

Based on character + type, suggest 3-4 angles:

For character content, derive angles from:

- Recent `timeline/state-timeline.md` events and phase transitions
- Unresolved `darkness/traumas.md` themes
- Growth signals in `light/strengths-hope.md` and `psychology/growth-edges.md`
- Relationship dynamics in `relationships/family.md`, cross-character files (discovered via `list_relationship_files()`), and `docs/graph/*.md`
- Defense mechanism patterns in `psychology/defense-mechanisms.md`
- Clinical formulation insights in `psychology/formulation.md` (5P model)
- MAT materials with evidence tier T1-T2 (highest reliability source angles)

```
What angle?
- [Derived from profile] ...
- [Derived from profile] ...
- [Derived from profile] ...
- Custom angle (describe)
```

### Q4: Platform & Format (if content)

```
Target platform?
- LinkedIn (professional, vulnerability + insight)
- Facebook (community, storytelling)
- Instagram (visual + caption)
- TikTok (short-form, hook-driven)
- YouTube (long-form, narrative)
- Twitter/X (thread or single)
```

### Q5: Tone & Voice

```
Tone direction?
- Raw/vulnerable (first-person confessional)
- Reflective (looking back with wisdom)
- Educational (teaching through experience)
- Inspirational (hope-forward)
- Analytical (clinical lens, third-person)
```

After answer → cross-reference `identity/writing-voice.md` if Nhân vật A content, or `psychology/archetype.md` for Nhân vật B/Nhân vật C tone inference.

### Q6: Clinical Framing (if psychological content)

Only ask if content involves psychological themes:

```
Should we anchor to a clinical framework?
- Yes — suggest relevant theory from docs/references/
- Light touch — reference without naming theory
- No — keep it accessible, no clinical framing
```

If yes → read `docs/references/INDEX.md`, suggest 2-3 relevant theories.

### Q7: Constraints & Sensitivities

```
Any constraints?
- Real names to avoid or anonymize
- Topics to handle carefully
- Platform-specific restrictions
- Timeline accuracy requirements
- None
```

## Output: CONTEXT.md

After all decisions locked, write `CONTEXT.md`:

```markdown
# Exploration Context

**Date:** {YYYY-MM-DD}
**Character:** {name}
**Type:** {content type}
**Angle:** {chosen angle}
**Platform:** {platform}
**Tone:** {tone}
**Clinical frame:** {framework or "none"}

## Locked Decisions

1. {Q1 answer with rationale}
2. {Q2 answer}
3. {Q3 answer}
4. {Q4 answer}
5. {Q5 answer}
6. {Q6 answer if applicable}
7. {Q7 answer if applicable}

## Profile References

- {list of profile files to read during creation}
- {clinical references if applicable}

## Constraints

- {any constraints identified}

## Next Step

Run `/orc:classify` to assess risk, then `/ck:plan` or implement directly.
```

### Output Location

- If active plan exists (from session state) → write to `{plan_dir}/CONTEXT.md`
- If no plan → write to `plans/exploration/CONTEXT-{YYYYMMDD-HHmm}.md`

## Resume Flow

`--resume`:

1. Find most recent CONTEXT.md (plan dir or `plans/exploration/`)
2. Read locked decisions
3. Resume from first unanswered question
4. If all answered → print summary, suggest next step

## Integration with Session State

After completing exploration:

- Update `.claude/session-state/state.json`:
  - `phase` → `"exploring"` during, `"planning"` after
  - `decisions` → append key decisions made

## Scripts

| Script                                                 | Purpose                                                             |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| `scripts/extract-context-decisions-from-context-md.py` | Parse CONTEXT.md and extract locked decisions for downstream skills |

## Safety

- READ-ONLY for profile files — only writes CONTEXT.md
- Never skips questions — each decision must be explicitly locked
- Always shows summary before finalizing
- Scope: content exploration for ck-marketing. Does NOT handle implementation or content creation.

## Examples

```bash
/cre:exploring                                    # start fresh
/cre:exploring LinkedIn post about Nhân vật B's growth  # start with topic
/cre:exploring --resume                           # continue previous
/cre:exploring --reset                            # discard + restart
```

## See Also

- `/orc:classify` — risk classify after exploration
- `/orc:bootstrap` — load context before exploring
- `/ck:plan` — plan after decisions are locked
- `/cre:prompt-leverage` — strengthen prompt after planning
