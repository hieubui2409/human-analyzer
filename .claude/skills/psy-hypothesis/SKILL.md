---
name: psy:hypothesis
description: "Predict character behavior given hypothetical events using SOUL/DARKNESS/LIGHT/CHARACTERISTIC patterns + clinical reference theories. Use for arc planning, content ideation, and character development scenarios. Triggers: 'what would happen if', 'predict', 'hypothesis', 'character prediction', 'behavior forecast', 'arc planning', 'what if', 'scenario analysis'."
argument-hint: "--character <name> --scenario '<event description>' [--depth shallow|deep|clinical]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "analysis"
  position: "arc-planning"
  dependencies: ["orc:bootstrap", "psy:ref-audit"]
---

# Character Behavior Hypothesis

Predict how a character would respond to hypothetical events based on their psychological profile.

## When to Use

- Planning future story arcs
- Content ideation: "What post would Nhân vật B write if X happened?"
- Pre-emptive crisis assessment: "If Nhân vật C fails the exam, what's the risk?"
- Exploring character growth trajectories
- Understanding relationship dynamics under stress

## Flags

| Flag                              | Purpose                                           |
| --------------------------------- | ------------------------------------------------- |
| `--character <name>`              | Target character (required)                       |
| `--scenario '<desc>'`             | Hypothetical event (required)                     |
| `--depth shallow\|deep\|clinical` | Analysis depth (default: deep)                    |
| `--multi`                         | Multi-character: analyze impact on all characters |

## Workflow

### Step 1: Load Character Profile

Load via `orc:bootstrap --intent "psychology"`:

- `psychology/formulation.md` (core wounds, coping mechanisms, inner conflicts)
- `darkness/traumas.md` (triggers, trauma patterns)
- `light/strengths-hope.md` (protective factors, growth edges)
- `psychology/defense-mechanisms.md` (behavioral patterns)
- `relationships/family.md` (dynamics with others)
- `relationships/{other-character}.md` — cross-character files discovered via `list_relationship_files()`

### Step 2: Map Scenario to Existing Patterns

Analyze the hypothetical event against:

1. **Trigger matching**: Does this scenario activate known triggers from `darkness/traumas.md`?
2. **Coping prediction**: Which coping mechanisms from `psychology/formulation.md` would activate?
3. **Defense mechanism**: Which defense patterns from `psychology/defense-mechanisms.md` would engage?
4. **Attachment response**: How would attachment style (from references) shape reaction?

### Step 3: Generate Behavioral Prediction

#### --depth shallow

Quick response: 3-5 bullet points of predicted behaviors.

#### --depth deep (default)

Structured analysis:

```markdown
## Hypothesis: {character} faces {scenario}

### Immediate Response (0-24h)

- **Emotional state**: {predicted emotion + intensity}
- **Primary defense**: {mechanism from `psychology/formulation.md`}
- **Behavioral manifestation**: {observable actions}
- **Clinical parallel**: {reference theory link}

### Short-term Adaptation (1-7 days)

- **Coping strategy**: {healthy/unhealthy from profile}
- **Support-seeking**: {who they'd turn to, based on RELATIONSHIPS}
- **Risk indicators**: {flags from DARKNESS patterns}

### Long-term Trajectory (weeks-months)

- **Growth potential**: {based on `light/strengths-hope.md` growth edges}
- **Regression risk**: {based on `darkness/traumas.md` patterns}
- **Relationship impact**: {on key relationships}

### Clinical Rationale

- {Theory 1}: {how it predicts this response} → [link](../../references/{theory}.md)
- {Theory 2}: {supporting pattern} → [link](../../references/{theory}.md)

### Confidence Level

- HIGH: prediction aligns with ≥3 established profile patterns
- MEDIUM: prediction aligns with 1-2 patterns, some uncertainty
- LOW: novel scenario, limited profile data to support prediction
```

#### --depth clinical

Full clinical analysis: adds DSM-5/ICD-11 implications, risk level assessment, recommended interventions, and cultural context factors.

### Step 4: --multi (Cross-Character Impact)

If --multi flag:

1. Predict primary character's response (steps 2-3)
2. For each related character in `relationships/family.md`:
   - How would they perceive/react to primary's response?
   - Would this trigger THEIR patterns?
   - What relationship dynamic shifts would occur?
3. Map cascading effects

## Output Format

```markdown
## Character Hypothesis Report

Character: {name}
Scenario: {description}
Depth: {shallow|deep|clinical}
Date: {YYYY-MM-DD}

{analysis per depth level}

### Disclaimer

This is a behavioral prediction based on documented psychological patterns,
NOT a real clinical assessment. Predictions inform storytelling and arc planning.
```

## Example Scenarios

- "What if Nhân vật B's father returns after 10 years?"
- "What if Nhân vật C gets the Scholarship X scholarship fully funded?"
- "What if Nhân vật A burns out from carrying too many mentees?"
- "What if Nhân vật B and Nhân vật C meet each other?"

## Scripts

| Script                                                   | Purpose                                                                |
| -------------------------------------------------------- | ---------------------------------------------------------------------- |
| `scripts/extract-character-psychology-for-hypothesis.py` | Extract SOUL/DARKNESS/LIGHT patterns from profile for hypothesis input |

## Safety

- Predictions are NARRATIVE TOOLS, not clinical diagnoses
- Always caveat predictions with confidence level
- If scenario involves crisis → recommend running `psy:crisis-assess` for proper documentation
- Scope: behavioral prediction for storytelling. Does NOT create content, modify profiles, or provide real clinical advice.

## See Also

psy:arc-tracker, psy:crossref, psy:profile-lite
