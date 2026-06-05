---
name: cre:prompt-leverage
description: "Strengthen content prompts before execution. Add character voice constraints, clinical accuracy checks, platform formatting rules, and profile references. Transforms vague content briefs into execution-ready instructions. Use before writing content, after exploring/planning. Triggers: 'leverage prompt', 'strengthen prompt', 'improve brief', 'prep for writing'."
argument-hint: "[prompt text] [--from-context|--platform <name>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "pre-execution"
  dependencies: ["cre:exploring"]
---

# Prompt Leverage — Strengthen Content Instructions

Transform vague content briefs → execution-ready prompts with character voice, clinical accuracy, and platform constraints baked in.

## Default (No Arguments)

Read CONTEXT.md from active plan or most recent exploration. Strengthen into execution prompt.

## Flags

| Flag                | Purpose                                         |
| ------------------- | ----------------------------------------------- |
| (prompt text)       | Strengthen the given prompt directly            |
| `--from-context`    | Read from CONTEXT.md (default if no text given) |
| `--platform <name>` | Add platform-specific constraints               |

## Strengthening Layers

Apply these layers sequentially to any content prompt:

### Layer 1: Character Voice Lock

If prompt involves a specific character:

1. Read `docs/profiles/{character}/identity/writing-voice.md` (if exists)
2. Read `docs/profiles/{character}/identity/core.md` — personality traits + behavioral patterns
3. Read `docs/profiles/{character}/psychology/defense-mechanisms.md` — active defenses inform voice
4. Read `docs/profiles/{character}/psychology/archetype.md` — archetypal communication pattern
5. Extract:
   - Vocabulary tendencies (formal/casual, Vietnamese/English mix)
   - Emotional register (vulnerable, analytical, hopeful)
   - Recurring themes and metaphors
   - What the character would NEVER say
6. Append voice constraints to prompt:
   ```
   VOICE CONSTRAINTS:
   - Tone: {extracted tone}
   - Register: {formal/casual level}
   - Themes: {recurring themes}
   - Avoid: {anti-patterns}
   - Archetype: {character archetype — influences narrative stance}
   - Defense voice: {how active defenses shape expression}
   - Reference: identity/writing-voice.md, psychology/archetype.md
   ```

### Layer 2: Clinical Accuracy Guard

If prompt involves psychological content:

1. Read `docs/references/INDEX.md`
2. Identify relevant theories based on content topic
3. Read specific reference files for accuracy constraints
4. Append:
   ```
   CLINICAL CONSTRAINTS:
   - Framework: {theory name} (docs/references/{file})
   - Key terms to use correctly: {list}
   - Common misapplications to avoid: {list}
   - Accessibility note: {how to reference without jargon}
   ```

### Layer 3: Platform Formatting

Based on target platform:

| Platform  | Constraints                                                              |
| --------- | ------------------------------------------------------------------------ |
| LinkedIn  | 3000 char max, professional tone, hook in first 2 lines, no hashtag spam |
| Facebook  | Storytelling-friendly, emotional, can be longer, community tone          |
| Instagram | Caption ≤2200 chars, first line is hook, relevant hashtags               |
| TikTok    | Script format, hook in 3 seconds, conversational, under 60s              |
| YouTube   | Script with timestamps, intro hook, structured sections                  |
| Twitter/X | 280 chars or thread format, punchy, quotable                             |

Append platform rules to prompt.

### Layer 4: Profile Cross-Reference

1. Check which profile files the content references
2. List specific files to read before writing
3. Add factual constraints:
   ```
   FACTUAL CONSTRAINTS:
   - Character DOB: {date} (identity/core.md)
   - Current status: {status}
   - Key relationship: {dynamic} (relationships/family.md + cross-character files via `list_relationship_files()` + docs/graph/*.md)
   - Timeline accuracy: verify against timeline/state-timeline.md
   - Evidence tier: only cite T1-T3 evidence in public content (MAT framework)
   - Formulation: content angle informed by psychology/formulation.md 5P model
   ```

### Layer 5: Sensitivity Scan

Check prompt for sensitive topics:

- Trauma references → add handling guidelines
- Real names → add anonymization rules
- Clinical terms → add accessibility note
- Family dynamics → add privacy constraints

Append if applicable:

```
SENSITIVITY CONSTRAINTS:
- {constraint with rationale}
```

## Output Format

```markdown
# Strengthened Prompt

## Original Brief

{original prompt/context}

## Execution Prompt

{Full strengthened prompt with all layers applied}

## Pre-Read List

Files to read before executing:

1. {file path} — {why}
2. {file path} — {why}

## Quality Checklist

After writing, verify:

- [ ] Voice matches `identity/writing-voice.md`
- [ ] Clinical terms used accurately
- [ ] Platform format constraints met
- [ ] Facts match profile files
- [ ] Sensitive topics handled appropriately
```

## Integration with Exploration

If `--from-context` or no arguments:

1. Find most recent CONTEXT.md (plan dir or `plans/exploration/`)
2. Extract locked decisions
3. Apply all 5 layers based on decisions
4. Output strengthened prompt

## Safety

- READ-ONLY — never modifies profile files or content
- Only writes the strengthened prompt output (to stdout or plan dir)
- Scope: prompt preparation for human-analyzer content. Does NOT handle content creation itself.

## Examples

```bash
/cre:prompt-leverage Write a LinkedIn post about Nhân vật A mentoring Nhân vật C
/cre:prompt-leverage --from-context
/cre:prompt-leverage --platform linkedin
/cre:prompt-leverage Write about Nhân vật B's growth --platform facebook
```

## See Also

- `/cre:exploring` — produces CONTEXT.md that prompt-leverage consumes
- `/orc:classify` — risk level informs how many layers to apply
- `/orc:bootstrap` — loads profile context referenced by leverage layers
