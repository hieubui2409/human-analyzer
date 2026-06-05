# psy:timeline-sync — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You updated Nhân vật A's timeline with "kết nghĩa Sep 2025." But Nhân vật B's timeline still says "kết nghĩa Aug 2025" (or is missing the entry). Before you run psy:crossref, this skill catches date mismatches: extracts all events from all timelines, finds events mentioning other characters, cross-checks dates. Output: "MISMATCH: kết nghĩa date differs (Nhân vật A: Sep, Nhân vật B: Aug). Suggested fix: align to Sep 2025 (Nhân vật A has P1 material evidence)."

## 2. Core concepts (the mental model)

- **Event extraction**: Deterministic. Regex finds date + event text. Handles "Sep 2025", "2025-09", "September", variations.
- **Cross-character matching**: If Nhân vật A's timeline mentions "met Nhân vật B" and Nhân vật B's mentions "met Nhân vật A," the skill pairs them.
- **Mismatch classification**: Date differ → MISMATCH (priority HIGH). Event in one, missing in other → MISMATCH. Date within 1 month → MATCH (acceptable variation, cultural or vague memory).
- **Suggested fixes**: Based on which character's timeline has material evidence (P1 > P2 > implicit). If both have materials, ask user.

## 3. Learning path

**All characters:** `psy:timeline-sync --all` — full cross-character check.

**One character:** `psy:timeline-sync --character hieu` — Nhân vật A's timeline only (no cross-check).

**JSON output:** `psy:timeline-sync --json` — structured for automation.

## 4. Use cases (each = a sample conversation)

### Use case: Post-update sync check

> You: "I updated Nhân vật C's milestones.md with 'Scholarship X scholarship awarded Jun 2025.' Did I miss updating others?"
> Skill: `psy:timeline-sync --all`
> → Cross-check found: Nhân vật A's timeline has "Nhân vật C awarded Jun 2025" (from materials), Nhân vật C's milestones.md has "Jun 2025" (matches ✓). But Nhân vật B's timeline is missing this event entirely (Nhân vật B connected via Nhân vật A). Recommendation: add to Nhân vật B's timeline/overview.md for completeness.

### Use case: Date alignment check

> You: "Kết nghĩa ceremony: Nhân vật A says Sep 2025, but I'm not sure if Nhân vật B matches."
> Skill: `psy:timeline-sync --pair hieu hoa`
> → MISMATCH: Nhân vật A timeline/overview.md: "Sep 2025" (line 42). Nhân vật B timeline/overview.md: "Aug 2025" (line 18). Materials confirm Sep 2025 (P1). Recommendation: update Nhân vật B's date to Sep 2025.

### Use case: Pre-crossref validation

> You: "Before running psy:crossref, should I check timeline sync?"
> Skill: `psy:timeline-sync --all`
> → Output: 15 shared events, 14 matched, 1 mismatch. Recommendation: fix 1 mismatch, then run psy:crossref.

## 5. Important caveats

- **Fuzzy matching within ±1 month is acceptable**: Cultural memory, intentional vagueness (character remembers "summer" not exact date) → +/- 1 month OK. Beyond that → flag.
- **Missing events are flagged but not errors**: If Nhân vật B's timeline doesn't mention an Nhân vật A-Nhân vật B event, it's a gap, not necessarily wrong (Nhân vật B might not consider it significant). Manual review needed.
- **Material evidence guides suggestions**: If both have different dates, material evidence (P1 sources) tips recommendation. If both vague → ask user.
- **Single-character check doesn't find mismatches**: `--character hieu` only checks Nhân vật A's timeline. No cross-comparison. Use `--all` or `--pair` for mismatches.
- **Not a consistency checker**: This checks DATES only. Psychological consistency, relationship dynamics, narrative coherence → that's psy:crossref.
