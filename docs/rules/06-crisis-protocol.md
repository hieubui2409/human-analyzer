# Crisis Documentation Protocol

Rules for documenting mental health crises, trauma, and sensitive psychological states in character profiles.

## Trigger Conditions

Apply this protocol when source materials indicate:

- Severe depression (MDD symptoms)
- PTSD or C-PTSD indicators
- Suicidal ideation (passive or active)
- Self-harm behaviors
- Acute crisis events (breakup, abandonment, financial collapse)

## Clinical Framework Application

### DSM-5 for Major Depressive Disorder (MDD)

Assess the 9 diagnostic criteria. Document:

- Which criteria are met (with evidence from materials)
- Duration (>2 weeks for diagnosis)
- Severity classification

### ICD-11 for Complex PTSD (C-PTSD)

Assess PTSD core symptoms + Disturbances in Self-Organization (DSO):

- Re-experiencing, avoidance, hyperarousal (PTSD core)
- Affect dysregulation, negative self-concept, disturbed relationships (DSO)

### Suicidal Ideation Classification

**Strictly differentiate:**

| Type    | Definition                                 | Documentation Required           |
| ------- | ------------------------------------------ | -------------------------------- |
| Passive | Wishing to disappear, not wanting to exist | Note in darkness/traumas.md      |
| Active  | Intent + plan                              | Risk level HIGH, safety contract |

### Sensory Triggers

Document if applicable:

- Olfactory triggers (bypass thalamus → amygdala direct response)
- Visual, auditory, or situational triggers
- Link to relevant reference: `docs/references/olfactory-ptsd.md`

## Vietnamese Cultural Context

Apply the concept of **"Nhịn"** (endurance/suppression) for Vietnamese characters:

- Treat emotional suppression as adaptive coping, not necessarily pathology
- Document cultural factors that influence expression of distress
- See `docs/references/vietnamese-cultural-context.md`

## Mandatory Documentation

Every crisis-related profile update MUST include:

### 1. Risk Level Classification

| Level    | Criteria                                         |
| -------- | ------------------------------------------------ |
| HIGH     | Active SI, plan, access to means                 |
| MODERATE | Passive SI, significant distress, limited coping |
| LOW      | Distress present, adequate coping, no SI         |

### 2. Protective Factors

List internal and external factors preventing harm:

- Internal: resilience traits, future goals, self-awareness
- External: support network, mentors, financial stability, safe environment

### 3. Safety Contracts

If applicable, document any verbal/written agreements about safety.

### 4. Trigger Warnings

Add to affected files:

```markdown
> **Trigger Warning**: [Type — e.g., Suicidal Ideation, Self-Harm, Abuse]
```

## File-Specific Rules

| File                       | Crisis content requirements                            |
| -------------------------- | ------------------------------------------------------ |
| darkness/traumas.md        | Primary location for trauma + crisis docs              |
| light/strengths-hope.md    | Protective factors MUST be documented if SI present    |
| timeline/overview.md       | Crisis events with exact dates                         |
| INDEX.md                   | Current status tag: `CRISIS` / `RECOVERING` / `STABLE` |
| psychology/core-wounds.md  | Coping mechanisms updated                              |
| timeline/state-timeline.md | Phase updated to `crisis` / `stabilizing`              |

## Confidentiality

- Crisis details involving third parties → `[PRIVATE]` tag
- Never surface raw crisis documentation in social media content
- See `09-confidentiality-protocol.md` for full privacy rules
