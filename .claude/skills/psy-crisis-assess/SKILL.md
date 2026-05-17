---
name: psy:crisis-assess
description: "Assess and document mental health crisis indicators in character profiles using clinical frameworks (DSM-5, ICD-11). Use when source materials indicate trauma, severe depression, suicidal ideation, or acute crisis events. Triggers: 'crisis', 'risk assessment', 'DSM-5', 'suicidal', 'depression assessment', 'mental health check', 'protective factors'. Also auto-triggered by psy:wave Wave 2 when crisis indicators detected."
argument-hint: "[--character <name>|--quick|--full|--update]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "clinical"
  position: "wave-2-supplement"
  dependencies: ["mpc:bootstrap", "psy:ref-audit"]
---

# Crisis Assessment Protocol

Implement `docs/rules/06-crisis-protocol.md` — structured clinical crisis documentation.

## When to Use

- Source materials indicate trauma, severe depression, PTSD, suicidal ideation
- During Wave 2 when crisis indicators detected
- Periodic review of characters with known crisis history
- After integrating new crisis-related materials

## Flags

| Flag                 | Purpose                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `--character <name>` | Assess specific character                                            |
| `--quick`            | Keywords only — skips behavioral cluster scan (faster but less safe) |
| `--full`             | Complete DSM-5 MDD + ICD-11 C-PTSD assessment                        |
| `--update`           | Update existing crisis documentation with new data                   |

**Default = deep mode** (keywords + behavioral clusters). Use `--quick` only when speed matters more than safety.

## Assessment Workflow

### Step 1: Load Context

1. Read character's DARKNESS.md + SOUL.md + TIMELINE.md
2. Read recent materials (last added) for crisis indicators
3. Load relevant references: `major-depressive-disorder.md`, `complex-ptsd.md`, `suicidal-ideation.md`

### Step 2: Crisis Keyword + Behavioral Cluster Scan (default deep mode)

1. Run `scripts/scan-crisis-keywords-in-profile.py --character <name>` → keyword hits + behavioral cluster hits
2. Default **deep mode**: scans both explicit crisis keywords (24 patterns) AND behavioral clusters for crisis-adjacent theories (suicidal-ideation, existential-void, complex-ptsd, somatization, flight-response)
3. With `--quick`: keyword scan only (skips behavioral clusters — faster but may miss metaphorical/implicit crisis indicators)
4. If 0 total hits from both passes: **LLM MUST independently re-read DARKNESS.md + SOUL.md** for implicit crisis indicators not caught by regex

### Step 3: DSM-5 MDD Checklist (--full)

Assess the 9 diagnostic criteria with evidence from materials:

| #   | Criterion                                      | Present? | Evidence      |
| --- | ---------------------------------------------- | -------- | ------------- |
| 1   | Depressed mood (most of day, nearly every day) | Y/N      | {quote/event} |
| 2   | Diminished interest/pleasure                   | Y/N      | {quote/event} |
| 3   | Weight/appetite change                         | Y/N      | {evidence}    |
| 4   | Insomnia or hypersomnia                        | Y/N      | {evidence}    |
| 5   | Psychomotor agitation/retardation              | Y/N      | {evidence}    |
| 6   | Fatigue/loss of energy                         | Y/N      | {evidence}    |
| 7   | Feelings of worthlessness/guilt                | Y/N      | {quote/event} |
| 8   | Diminished concentration                       | Y/N      | {evidence}    |
| 9   | Recurrent thoughts of death/SI                 | Y/N      | {evidence}    |

**MDD threshold:** ≥5 of 9 criteria, duration >2 weeks.

### Step 4: ICD-11 C-PTSD Check (if applicable)

**PTSD Core:**

- Re-experiencing (flashbacks, nightmares)
- Avoidance (of reminders)
- Hyperarousal (startle, hypervigilance)

**Disturbances in Self-Organization (DSO):**

- Affect dysregulation
- Negative self-concept
- Disturbed relationships

### Step 5: Suicidal Ideation Classification

**Strictly differentiate:**

| Type    | Definition                                 | Indicators                                             |
| ------- | ------------------------------------------ | ------------------------------------------------------ |
| None    | No SI                                      | No death wishes, engaged with future                   |
| Passive | Wishing to disappear, not wanting to exist | "Muốn biến mất", "Không muốn sống" without plan        |
| Active  | Intent + plan + potential means            | Specific method mentioned, timeline, goodbye behaviors |

### Step 6: Risk Level Classification

| Level    | Criteria                                         | Required Action                                         |
| -------- | ------------------------------------------------ | ------------------------------------------------------- |
| HIGH     | Active SI, plan, access to means, recent attempt | Safety contract, immediate documentation, flag in INDEX |
| MODERATE | Passive SI, significant distress, limited coping | Document in DARKNESS, update protective factors         |
| LOW      | Distress present, adequate coping, no SI         | Monitor, document coping strategies                     |

### Step 7: Protective Factors Inventory

Document ALL factors preventing harm:

**Internal:**

- Resilience traits, self-awareness
- Future goals, academic/career motivation
- Religious/spiritual beliefs

**External:**

- Support network (list specific people)
- Mentors, safe relationships
- Financial stability/prospects
- Safe environment, no access to means

### Step 8: Vietnamese Cultural Context

Apply "Nhịn" (endurance/suppression) assessment:

- Is emotional suppression adaptive or maladaptive in this context?
- Cultural factors influencing expression of distress
- Family dynamics affecting help-seeking behavior
- See `docs/references/vietnamese-cultural-context.md`

### Step 9: Documentation Output

Update profile files:

**DARKNESS.md:**

```markdown
## Crisis Assessment [{date}]

- **Risk Level**: HIGH / MODERATE / LOW
- **DSM-5 MDD**: {N}/9 criteria met, duration {X}
- **C-PTSD**: Present / Absent / Partial
- **SI Classification**: None / Passive / Active
- **Key Triggers**: {list}
  > **Trigger Warning**: {type}
```

**LIGHT.md:**

```markdown
## Protective Factors [{date}]

- **Internal**: {list}
- **External**: {list}
- **Safety Contract**: {yes/no, date if applicable}
```

**INDEX.md:**
Update status tag: `CRISIS` / `RECOVERING` / `STABLE`

**TIMELINE.md:**
Add crisis event entries with exact dates.

## --quick (Rapid Assessment)

Skip full DSM-5 checklist. Output:

1. Risk Level (HIGH/MOD/LOW) with 1-line rationale
2. Top 3 protective factors
3. SI classification
4. Recommended action

## Safety

- This skill documents clinical patterns for CHARACTER PROFILES, not real clinical diagnosis
- Never diagnose a real person — this is for narrative/storytelling documentation
- All clinical frameworks applied for CHARACTER ANALYSIS accuracy
- After HIGH risk assessment, update `mpc:session-state` with crisis event for session recovery
- After any assessment, run `psy:ref-audit --character <name>` to verify clinical terms used correctly
- Scope: crisis documentation in character profiles. Does NOT provide real clinical advice.

## See Also

cre:privacy-guard, psy:wave, mpc:classify
