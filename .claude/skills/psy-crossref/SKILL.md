---
name: psy:crossref
description: "Cross-character consistency validation. Scans 2+ character profiles for timeline conflicts, relationship mismatches, contradictory facts, and missing cross-references. Run after profile updates or periodically. Based on patterns from existing validation reports. Triggers: 'cross-reference', 'crossref', 'consistency check', 'validate profiles', 'check consistency', 'profile validation'."
argument-hint: "[--pair <char1> <char2>|--all|--timeline|--relationships|--report]"
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

## Character Pairs

| Pair         | Relationship               | Key Shared Events                                              |
| ------------ | -------------------------- | -------------------------------------------------------------- |
| Nhân vật A ↔ Nhân vật B   | Sworn brothers (kết nghĩa) | Meeting Jul 2025, kết nghĩa Sep 2025, gambling crisis Oct 2025 |
| Nhân vật A ↔ Nhân vật C | Mentor-mentee (Scholarship X)  | Interview, F15 scholarship, mentoring sessions                 |
| Nhân vật B ↔ Nhân vật C  | Connected through Nhân vật A     | Indirect — shared timeline of Nhân vật A's attention                 |

## Validation Categories

### 1. Timeline Consistency

For shared events between characters:

- Same event → same date in both profiles?
- Sequence matches? (A before B in both?)
- No phantom events (event in one profile, missing in other)?

```
Check: TIMELINE.md × TIMELINE.md
Method: Extract events mentioning other character, compare dates
Known issues: Crisis dates varied between Sep/Oct 2025 (from existing reports)
```

### 2. Relationship Symmetry

Cross-references in RELATIONSHIPS.md must be bidirectional:

- If Nhân vật A describes "kết nghĩa Sep 2025 with Nhân vật B" → Nhân vật B must have same entry
- Emotional characterization should be compatible (not contradictory)
- Family member references must align

```
Check: RELATIONSHIPS.md × RELATIONSHIPS.md
Method: Extract sections about each other, compare facts + framing
```

### 3. Factual Consistency

Hard facts must match across profiles:

- Dates of birth, ages, locations
- Event details (who was present, what happened)
- Quantitative claims (number of visits, duration of support)

```
Check: IDENTITY.md + TIMELINE.md + RELATIONSHIPS.md across characters
Method: Extract factual claims, cross-compare
```

### 4. Psychological Consistency

Character descriptions should be compatible:

- If Nhân vật A's SOUL.md says "savior complex" → Nhân vật B's RELATIONSHIPS.md should reflect being "saved"
- Attachment styles should be complementary (anxious + avoidant → predictable dynamics)
- Defense mechanisms should be consistent with described behaviors

```
Check: SOUL.md × RELATIONSHIPS.md × CHARACTERISTIC.md across characters
Method: Extract psychological claims, check for contradictions
```

### 5. Materials Verification

Profile claims should be traceable to source materials:

- Key facts should have supporting material in docs/materials/
- Conversation transcripts should match quoted dialogue

```
Check: profiles/ × materials/
Method: Spot-check major claims against source docs
```

## Workflow

### Step 1: Load Profiles

For each character in scope:

1. Read TIMELINE.md, RELATIONSHIPS.md, IDENTITY.md, SOUL.md

### Step 2: Extract Cross-References

For each profile pair:

1. Find all mentions of the other character
2. Extract: event, date, location, details, emotional framing
3. Build comparison table

### Step 3: Compare

For each shared reference:

1. **Date match?** — same date or within acceptable range?
2. **Fact match?** — same details?
3. **Framing compatible?** — emotions/interpretations don't contradict?
4. **Bidirectional?** — event appears in both profiles?

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

- **{Event}**: Nhân vật A TIMELINE.md:L{n} says "{date1}" but Nhân vật B TIMELINE.md:L{n} says "{date2}"
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

| Script                                      | Purpose                                                               |
| ------------------------------------------- | --------------------------------------------------------------------- |
| `scripts/extract-cross-character-events.py` | Extract events mentioning other characters from all TIMELINE.md files |
| `scripts/check-bidirectional-references.py` | Verify RELATIONSHIPS.md entries are symmetric across character pairs  |

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
- `/mpc:classify` — cross-character work triggers high_risk
- `plans/reports/validation-260325-cross-reference-check.md` — previous crossref report
- `plans/reports/detect-260331-*-inconsistencies.md` — per-character inconsistency reports
