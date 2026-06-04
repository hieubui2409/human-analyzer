# Profile Structure Rules

Standards for character profile files in `docs/profiles/{character}/`.

Schema definition: `.claude/schemas/universal-profile-schema.yaml`

## Directory Layout (Universal Schema)

Every character MUST follow this nested directory structure:

```
docs/profiles/{character}/
├── INDEX.md                        ← Quick reference (~50-80 lines) [MANDATORY]
├── CURRENT-STATE.md                ← Live status snapshot [MANDATORY]
├── milestones.md                   ← Key life milestones [MANDATORY]
├── identity/
│   ├── core.md                     ← Basic info + personality traits [MANDATORY]
│   ├── writing-voice.md            ← Tone, themes, language patterns [MANDATORY]
│   ├── achievements.md             ← Academic, career, awards [Optional]
│   └── media-coverage.md           ← Press timeline [Optional]
├── psychology/
│   ├── core-wounds.md              ← Inner wounds, coping, psychological core [MANDATORY]
│   ├── defense-mechanisms.md       ← Defense patterns with behavioral examples [MANDATORY]
│   ├── attachment-style.md         ← Attachment theory mapping [MANDATORY]
│   ├── growth-edges.md             ← Growth trajectory, transformation arc [MANDATORY]
│   ├── formulation.md              ← Clinical case formulation [Optional]
│   ├── diagnostics.md              ← DSM-5/ICD-11 differential [Optional]
│   ├── cultural-formulation.md     ← Vietnamese cultural context [Optional]
│   ├── archetype.md                ← Jungian or narrative archetype [Optional]
│   └── case-studies/               ← Theory-to-character applied studies [Optional]
├── relationships/
│   ├── family.md                   ← Family tree + family dynamics [MANDATORY]
│   └── {other-character}.md        ← Per-relationship deep profiles [As needed]
├── timeline/
│   ├── overview.md                 ← Chronological events [MANDATORY]
│   └── state-timeline.md           ← Psychological state over time [MANDATORY]
├── darkness/
│   └── traumas.md                  ← Trauma documentation [MANDATORY]
├── light/
│   └── strengths-hope.md           ← Sources of hope, growth signs [MANDATORY]
├── evidence/
│   └── conversations.md            ← Messenger/chat transcripts [Optional]
└── growth/                         ← GRO domain (see rule 15-gro-framework)
    ├── career-path.md              ← Career trajectory (Super stages) [MANDATORY]
    ├── competencies.md             ← Skills inventory (Dreyfus) [MANDATORY]
    ├── learning-profile.md         ← Learning style (Kolb) [Optional]
    └── mentoring-map.md            ← Mentoring relationships (Kram) [Optional]
```

> The `growth/` subtree is owned by the GRO framework (rule 15) but is part of the
> universal profile schema (`paths.PROFILE_FILES`), so it is listed here for completeness.

## Path Migration Map

Old flat-file paths → new nested paths:

| Old Path          | New Path                   |
| ----------------- | -------------------------- |
| SOUL.md           | psychology/core-wounds.md  |
| IDENTITY.md       | identity/core.md           |
| CHARACTERISTIC.md | identity/core.md (merged)  |
| DARKNESS.md       | darkness/traumas.md        |
| LIGHT.md          | light/strengths-hope.md    |
| RELATIONSHIPS.md  | relationships/family.md    |
| TIMELINE.md       | timeline/overview.md       |
| MILESTONES.md     | milestones.md              |
| ACHIEVEMENTS.md   | identity/achievements.md   |
| WRITING-VOICE.md  | identity/writing-voice.md  |
| INSPIRATION.md    | psychology/growth-edges.md |
| CONVERSATION.md   | evidence/conversations.md  |

## Section Ordering

Each file should follow consistent section order:

### INDEX.md

1. Identity summary (name, DOB, status)
2. Current situation (1-2 sentences)
3. Key relationships (bullet list)
4. Psychological snapshot (3-5 bullet points)
5. File map (links to nested profile files)

### psychology/core-wounds.md

1. Core wound summary
2. Attachment style + evidence (link to psychology/attachment-style.md)
3. Defense mechanisms overview (link to psychology/defense-mechanisms.md)
4. Coping patterns
5. Inner conflicts
6. Clinical theory anchors (link to docs/references/)

### timeline/overview.md

1. Format: `YYYY-MM` or `YYYY-MM-DD` — event description
2. Group by life phase (early life, adolescence, recent)
3. Cross-character events MUST include other character's name
4. Uncertain dates marked with `[~approximate]`
5. Contradicted dates marked with `[DISPUTED: source A says X, source B says Y]`

### relationships/family.md

1. Family members (one section per person)
2. Key non-family relationships (one section per person)
3. Each section: relationship nature, key events, current dynamics, psychological analysis
4. Cross-reference: "See also: docs/profiles/{other}/relationships/family.md"

## Naming Conventions

- Directory files: kebab-case with .md extension (subdirectories and files)
- Root profile files (INDEX.md, CURRENT-STATE.md, milestones.md): UPPERCASE for backward compat
- Character directory: kebab-case Vietnamese name without diacritics
- Cross-references: use relative paths from project root

## Cross-Reference Format

When referencing other characters or files:

```markdown
<!-- Cross-ref: docs/profiles/character-b/timeline/overview.md — same event -->
```

## Factual Tagging

- Verified facts: no tag needed
- Uncertain: `[UNCERTAIN]`
- Disputed: `[DISPUTED: explanation]`
- From materials: `[Source: docs/materials/{file}]`

## Output Schemas

Recommended YAML-style structure for key profile files.
Full schema: `.claude/schemas/universal-profile-schema.yaml`

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

### psychology/core-wounds.md

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

### timeline/overview.md

```yaml
Events:
  - Date: "{YYYY-MM-DD or Year}"
    Age: "{Calculated Age}"
    Event_Name: "{Short title}"
    Description: "{What happened}"
    Impact: "{Psychological or physical effect}"
    Source: "{Tier 1-5}"
```

Rule: Must strictly follow chronological order. Verify age calculations against DOB.

### darkness/traumas.md

```yaml
Primary_Trauma:
  Type: "{Discrete (PTSD) or Prolonged/Inescapable (C-PTSD)}"
  Event_Link: "{Reference to timeline/overview.md event}"
  Sensory_Triggers:
    - Trigger: "{e.g., specific smell}"
      Mechanism: "{e.g., Olfactory-Amygdala direct response}"
Symptoms_&_Manifestations:
  Affect_Dysregulation: "{How they struggle to modulate emotions}"
  Negative_Self_Concept: "{Feelings of shame/worthlessness}"
  Suicidal_Ideation: "{None / Passive / Active}"
```

Rule: Link directly to clinical frameworks if trauma is severe. See `06-crisis-protocol.md`.

### light/strengths-hope.md

```yaml
Sources_of_Hope:
  - Subject: "{Person/Passion/Belief}"
    Role: "{Why it gives them hope}"
Protective_Factors:
  - Factor: "{Internal trait or external support system}"
Growth_Milestones:
  - Milestone: "{Healing moment}"
    Date_Link: "{timeline/overview.md reference}"
```

Rule: If Suicidal Ideation present, Protective Factors MUST be documented. See `06-crisis-protocol.md`.

### relationships/family.md

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

| File                   | Target         | Warning threshold |
| ---------------------- | -------------- | ----------------- |
| INDEX.md               | 50-80 lines    | >100 lines        |
| psychology/core-wounds | 200-400 lines  | >500 lines        |
| timeline/overview      | 150-350 lines  | >400 lines        |
| relationships/family   | 200-400 lines  | >500 lines        |
| Others                 | 100-300 lines  | >400 lines        |
| Total per character    | 800-2500 lines | >3000 lines       |

When a file exceeds threshold → consider splitting or extracting to sub-files.
