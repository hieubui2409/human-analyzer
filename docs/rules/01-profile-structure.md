# Profile Structure Rules

Standards for character profile files in `docs/profiles/{character}/`.

## Required Files

Every character MUST have these files:

| File              | Purpose                                             | Required                       |
| ----------------- | --------------------------------------------------- | ------------------------------ |
| INDEX.md          | Quick reference (~50-80 lines)                      | MANDATORY                      |
| IDENTITY.md       | Basic info, DOB, family, education, career          | MANDATORY                      |
| SOUL.md           | Inner wounds, coping mechanisms, psychological core | MANDATORY                      |
| CHARACTERISTIC.md | Personality traits, behavioral patterns             | MANDATORY                      |
| TIMELINE.md       | Chronological events                                | MANDATORY                      |
| RELATIONSHIPS.md  | Family tree, key relationships                      | MANDATORY                      |
| DARKNESS.md       | Trauma documentation                                | MANDATORY                      |
| LIGHT.md          | Sources of hope, growth signs                       | MANDATORY                      |
| MILESTONES.md     | Key life milestones                                 | MANDATORY                      |
| WRITING-VOICE.md  | Tone, themes, language patterns                     | Optional (Nhân vật A only currently) |
| CONVERSATION.md   | Messenger/chat transcripts                          | Optional                       |

## Section Ordering

Each file should follow consistent section order:

### INDEX.md

1. Identity summary (name, DOB, status)
2. Current situation (1-2 sentences)
3. Key relationships (bullet list)
4. Psychological snapshot (3-5 bullet points)
5. File map (links to other profile files)

### SOUL.md

1. Core wound summary
2. Attachment style + evidence
3. Defense mechanisms (list with behavioral examples)
4. Coping patterns
5. Inner conflicts
6. Clinical theory anchors (link to docs/references/)

### TIMELINE.md

1. Format: `YYYY-MM` or `YYYY-MM-DD` — event description
2. Group by life phase (early life, adolescence, recent)
3. Cross-character events MUST include other character's name
4. Uncertain dates marked with `[~approximate]`
5. Contradicted dates marked with `[DISPUTED: source A says X, source B says Y]`

### RELATIONSHIPS.md

1. Family members (one section per person)
2. Key non-family relationships (one section per person)
3. Each section: relationship nature, key events, current dynamics, psychological analysis
4. Cross-reference: "See also: docs/profiles/{other}/RELATIONSHIPS.md"

## Naming Conventions

- File names: UPPERCASE with .md extension
- Character directory: kebab-case Vietnamese name without diacritics
- Cross-references: use relative paths from project root

## Cross-Reference Format

When referencing other characters or files:

```markdown
<!-- Cross-ref: docs/profiles/character-b/TIMELINE.md — same event -->
```

## Factual Tagging

- Verified facts: no tag needed
- Uncertain: `[UNCERTAIN]`
- Disputed: `[DISPUTED: explanation]`
- From materials: `[Source: docs/materials/{file}]`

## Output Schemas

Recommended YAML-style structure for key profile files (from original system directive):

### INDEX.md

```yaml
# {Character Name}
Tagline: "{One-line summary}"
Basics:
  Name: "{Full name}"
  DOB: "{DD/MM/YYYY}"
  Location: "{Location}"
  Occupation: "{Occupation}"
Sources_Used: [{ P1 }, { P2... }]
Last_Updated: "{YYYY-MM-DD}"
```

### SOUL.md

```yaml
Core_Essence: "{Brief description}"
Root_Wound:
  Origin: "{Event}"
  Manifestation: "{Behavior}"
Inner_Conflict:
  External_Mask: "{Trait}"
  Internal_Reality: "{Trait}"
  Haunting_Question: "{Quote/Question}"
Coping_Mechanisms:
  - Strategy: "{Name}"
    Type: "{Healthy/Unhealthy}"
```

### TIMELINE.md

```yaml
Events:
  - Date: "{YYYY-MM-DD or Year}"
    Age: "{Calculated Age}"
    Event_Name: "{Short title}"
    Description: "{What happened}"
    Impact: "{Psychological or physical effect}"
    Source: "{P1/P2/P3/P4}"
```

Rule: Must strictly follow chronological order. Verify age calculations against DOB.

### DARKNESS.md

```yaml
Primary_Trauma:
  Type: "{Discrete (PTSD) or Prolonged/Inescapable (C-PTSD)}"
  Event_Link: "{Reference to Timeline event}"
  Sensory_Triggers:
    - Trigger: "{e.g., specific smell}"
      Mechanism: "{e.g., Olfactory-Amygdala direct response}"
Symptoms_&_Manifestations:
  Affect_Dysregulation: "{How they struggle to modulate emotions}"
  Negative_Self_Concept: "{Feelings of shame/worthlessness}"
  Suicidal_Ideation: "{None / Passive / Active}"
```

Rule: Link directly to clinical frameworks if trauma is severe. See `06-crisis-protocol.md`.

### LIGHT.md

```yaml
Sources_of_Hope:
  - Subject: "{Person/Passion/Belief}"
    Role: "{Why it gives them hope}"
Protective_Factors:
  - Factor: "{Internal trait or external support system}"
Growth_Milestones:
  - Milestone: "{Healing moment}"
    Date_Link: "{Timeline reference}"
```

Rule: If Suicidal Ideation present, Protective Factors MUST be documented. See `06-crisis-protocol.md`.

### RELATIONSHIPS.md

```yaml
Family_Tree:
  Parents: ["{Name - Status}"]
  Siblings: ["{Name - Status}"]
Key_Connections:
  - Name: "{Character Name}"
    Relation: "{Role/Title}"
    Dynamic: "{Healthy / Toxic / Co-dependent / Distant}"
    Impact_on_Subject: "{How this person shapes the subject's psyche}"
```

### VALIDATION-NOTES.md (Optional)

```yaml
Unresolved_Contradictions:
  - Topic: "{Fact in question}"
    Source_1_Claims: "{Detail}"
    Source_2_Claims: "{Detail}"
    Resolution_Status: "PENDING HUMAN REVIEW / MARKED UNCERTAIN"
```

Log discrepancies found during Wave 3 validation. See `08-cross-validation.md`.

## Size Guidelines

| File                | Target         | Warning threshold |
| ------------------- | -------------- | ----------------- |
| INDEX.md            | 50-80 lines    | >100 lines        |
| SOUL.md             | 200-400 lines  | >500 lines        |
| TIMELINE.md         | 150-350 lines  | >400 lines        |
| RELATIONSHIPS.md    | 200-400 lines  | >500 lines        |
| Others              | 100-300 lines  | >400 lines        |
| Total per character | 800-2500 lines | >3000 lines       |

When a file exceeds threshold → consider splitting or extracting to sub-files.
