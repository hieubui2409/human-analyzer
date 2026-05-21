---
name: psy:crossref
description: "Cross-character consistency validation — 10 dimensions (4 automated + 6 LLM judgment). Scans 2+ character profiles for timeline conflicts, relationship mismatches, contradictory facts, missing cross-references, evidential backing, developmental plausibility, cultural consistency, systemic balance, narrative coherence, and linguistic voice. Run after profile updates or periodically. Triggers: 'cross-reference', 'crossref', 'consistency check', 'validate profiles', 'check consistency', 'profile validation'."
argument-hint: "[--pair <char1> <char2>|--all|--timeline|--relationships|--extended|--report]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "validation"
  position: "post-work"
  dependencies: []
---

# Cross-Reference — Multi-Character Consistency Validation

Detect inconsistencies between character profiles. Timeline conflicts, relationship mismatches, contradictory facts.

## Default (No Arguments)

`--all` — validate all character pairs.

## Flags

| Flag                     | Purpose                                        |
| ------------------------ | ---------------------------------------------- |
| `--all`                  | All character pairs (default)                  |
| `--pair <char1> <char2>` | Validate specific pair                         |
| `--timeline`             | Timeline-only validation across all characters |
| `--relationships`        | Relationship-only validation                   |
| `--report`               | Generate formal report to plans/reports/       |
| `--extended`             | Include all 10 dimensions (default: 4 core)    |
| `--dimension <1-10>`     | Run specific dimension only                    |

## Character Pairs

| Pair         | Relationship               | Key Shared Events                                              |
| ------------ | -------------------------- | -------------------------------------------------------------- |
| Nhân vật A ↔ Nhân vật B   | Sworn brothers (kết nghĩa) | Meeting Jul 2025, kết nghĩa Sep 2025, gambling crisis Oct 2025 |
| Nhân vật A ↔ Nhân vật C | Mentor-mentee (Scholarship X)  | Interview, F15 scholarship, mentoring sessions                 |
| Nhân vật B ↔ Nhân vật C  | Connected through Nhân vật A     | Indirect — shared timeline of Nhân vật A's attention                 |

## 10 Validation Dimensions

Dimensions 1–4 have automated script support; dimensions 5–10 require LLM judgment.

### Core Dimensions (Automated)

### 1. Temporal Consistency

For shared events between characters:

- Same event → same date in both profiles?
- Sequence matches? (A before B in both?)
- Ages match DOB calculation (current_year - birth_year = stated_age ±1)?
- No phantom events (event in one profile, missing in other)?

```
Check: timeline/overview.md × timeline/overview.md
Method: Extract events mentioning other character, compare dates
Known issues: Crisis dates varied between Sep/Oct 2025 (from existing reports)
```

### 2. Relational Symmetry

Cross-references in relationships/ must be bidirectional:

- If Nhân vật A describes "kết nghĩa Sep 2025 with Nhân vật B" → Nhân vật B must have same entry
- Emotional characterization should be compatible (not contradictory)
- Family member references must align

```
Check: relationships/family.md × relationships/family.md
Method: Extract sections about each other, compare facts + framing
```

> Cross-character relationship files (e.g. `relationships/character-b.md`) are also checked for mirror pair symmetry — discovered dynamically via `list_relationship_files()`.

### 3. Psychological Consistency

Character descriptions should be compatible:

- Defense mechanisms logically stem from documented trauma
- If Nhân vật A's psychology/formulation.md says "savior complex" → Nhân vật B's relationships/ should reflect being "saved"
- Attachment styles should be complementary (anxious + avoidant → predictable dynamics)

```
Check: psychology/* × relationships/* across characters
Method: Extract psychological claims, check for contradictions
```

### 4. Factual Consistency

Hard facts must match across profiles:

- Dates of birth, ages, locations
- Event details (who was present, what happened)
- Quantitative claims (debt amounts, visit counts)
- Names and places identical across all files

```
Check: identity/core.md + timeline/overview.md + relationships/family.md across characters
Method: Extract factual claims, cross-compare
```

### Extended Dimensions (LLM Judgment)

### 5. Evidential Backing

Profile claims backed by material evidence ≥T3:

- "Avoidant attachment" claim must trace to T2+ material
- Key psychological findings → linked source in docs/materials/
- Conversation transcripts should match quoted dialogue

```
Check: profiles/ × materials/
Trigger: After MAT.integrated — new material may support or contradict claims
```

### 6. Developmental Plausibility

Growth trajectory plausible given timeline + milestones:

- Recovery claim in 2025 must follow documented intervention
- Phase transitions in state-timeline.md must have triggering events
- Growth-edges.md trajectories consistent with documented timeline

```
Check: psychology/growth-edges.md × timeline/overview.md × milestones.md
Trigger: After profile updates to growth-edges.md or milestones.md
```

### 7. Cultural Consistency

Cultural context consistent across characters from same milieu:

- Vietnamese family dynamics consistent for Tỉnh X origin
- Gender role expectations culturally appropriate
- Cultural formulation factors aligned across characters sharing same community

```
Check: psychology/cultural-formulation.md across characters
Trigger: When adding new character or updating cultural-formulation.md
```

### 8. Systemic Balance

Family system dynamics balance (parentification ↔ role reversal):

- If Nhân vật A is parentified, sibling roles must reflect this
- Relationship power dynamics consistent across all involved characters
- Family roles documented in relationships/family.md align with psychology/formulation.md

```
Check: relationships/family.md × psychology/formulation.md across characters
Trigger: After any relationships/family.md update
```

### 9. Narrative Coherence

Story arcs across characters form coherent threads:

- Mentor-mentee arc (Nhân vật A↔Nhân vật C) must progress logically across timelines
- Sworn-brother arc (Nhân vật A↔Nhân vật B) events build on each other
- Arc trajectory shifts detected by psy:arc-tracker match documented events

```
Check: timeline/overview.md × milestones.md across character pairs
Trigger: After psy:arc-tracker detects trajectory shift
```

### 10. Linguistic Voice

Voice consistency when characters describe shared events:

- Same event described in compatible (not identical) tone
- Each character's voice in evidence/conversations.md matches identity/writing-voice.md
- Emotional register consistent with defense-mechanisms.md

```
Check: identity/writing-voice.md × evidence/conversations.md across characters
Trigger: Before cre:post-writer when content references shared events
```

## Workflow

### Step 1: Load Profiles

For each character in scope:

1. Read `timeline/overview.md`, `relationships/family.md`, `identity/core.md`, `psychology/formulation.md`

### Step 2: Extract Cross-References

For each profile pair:

1. Find all mentions of the other character
2. Extract: event, date, location, details, emotional framing
3. Build comparison table

### Step 3: Compare

For each shared reference:

1. **Date match?** — same date or within acceptable range? (Dim 1)
2. **Fact match?** — same details? (Dim 4)
3. **Framing compatible?** — emotions/interpretations don't contradict? (Dim 3)
4. **Bidirectional?** — event appears in both profiles? (Dim 2)
5. **Evidence-backed?** — claim traceable to T3+ material? (Dim 5, --extended)
6. **Developmentally plausible?** — growth trajectory makes sense? (Dim 6, --extended)
7. **Culturally consistent?** — cultural context matches milieu? (Dim 7, --extended)
8. **Systemically balanced?** — family dynamics align? (Dim 8, --extended)
9. **Narratively coherent?** — arc threads build logically? (Dim 9, --extended)
10. **Voice consistent?** — compatible tone for shared events? (Dim 10, --extended)

### Step 4: Classify Findings

| Severity     | Definition                      | Example                                             |
| ------------ | ------------------------------- | --------------------------------------------------- |
| **CRITICAL** | Hard fact contradiction         | Different dates for same event                      |
| **MAJOR**    | Missing bidirectional reference | Event in one profile, absent in other               |
| **MINOR**    | Framing inconsistency           | Different emotional characterization of same event  |
| **INFO**     | Enrichment opportunity          | One profile has detail the other could benefit from |

### Step 5: Output Report

```markdown
# Cross-Reference Validation Report

**Date:** {YYYY-MM-DD}
**Scope:** {pairs validated}
**Previous report:** {link to last report if exists}

## Summary

| Pair         | Critical | Major | Minor | Info | Status      |
| ------------ | -------- | ----- | ----- | ---- | ----------- |
| Nhân vật A ↔ Nhân vật B   | {n}      | {n}   | {n}   | {n}  | {pass/fail} |
| Nhân vật A ↔ Nhân vật C | {n}      | {n}   | {n}   | {n}  | {pass/fail} |
| Nhân vật B ↔ Nhân vật C  | {n}      | {n}   | {n}   | {n}  | {pass/fail} |

## Detailed Findings

### Nhân vật A ↔ Nhân vật B

#### CRITICAL

- **{Event}**: Nhân vật A timeline/overview.md:L{n} says "{date1}" but Nhân vật B timeline/overview.md:L{n} says "{date2}"
  - Materials source: {what materials say}
  - Recommended fix: {which file to update}

#### MAJOR

...

## Recommendations

1. {Priority fixes}

## Comparison with Previous Report

{If previous report exists, note resolved/new issues}
```

## Scripts

| Script                                                  | Purpose                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| `scripts/extract-cross-character-events.py`             | Extract events mentioning other characters from all timeline files |
| `scripts/check-bidirectional-references.py`             | Verify relationships entries are symmetric across character pairs  |
| `scripts/check-evidence-backing-for-claims.py`          | Dim 5: verify profile claims have ≥T3 material evidence            |
| `scripts/check-developmental-trajectory-consistency.py` | Dim 6: verify growth trajectories are plausible given timeline     |

## Safety

- READ-ONLY — never modifies profile files
- Only writes report files
- Scope: cross-character validation for ck-marketing profiles. Does NOT edit profiles or create content.

## Examples

```bash
/psy:crossref                                   # validate all pairs
/psy:crossref --pair hieu hoa                   # Nhân vật A-Nhân vật B only
/psy:crossref --timeline                        # timeline checks only
/psy:crossref --all --report                    # full + save report
```

## See Also

- `/psy:ref-audit` — clinical accuracy (complementary)
- `/orc:classify` — cross-character work triggers high_risk
- `plans/reports/validation-260325-cross-reference-check.md` — previous crossref report
- `plans/reports/detect-260331-*-inconsistencies.md` — per-character inconsistency reports
