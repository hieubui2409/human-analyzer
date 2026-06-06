# psy:narrative-twist — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Months into profiling, new materials surface: Character C's stepmother isn't a villain — she raised him lovingly, and his "maternal abandonment" narrative was Character C's misinterpretation. You need to correct this across 8+ files (timeline, psychology, relationships with Character A, etc.) without erasing the old version. This skill finds all traces, marks them clearly, and cascades the correction through related characters.

## 2. Core concepts (the mental model)

- **Preserve history**: Strikethrough shows what was believed/claimed; ⚠️ TWIST shows the truth. Future readers see both, understand the narrative evolution.
- **Cascade is mandatory**: If Character C's maternal story changes, Character A's perception of Character C changes too. The skill finds and updates cross-character files symmetrically.
- **Validation required**: After applying a twist, psy:crossref must validate that the new narrative is consistent. Don't skip this.

## 3. Learning path

**First twist:** `psy:narrative-twist --character character-c --fact "Mẹ kế bỏ rơi Character C" --truth "Mẹ kế nuôi dạy Character C từ bé" --source "P1, 2026-06-05"` — apply one twist, watch the cascade.

**Scan for twists:** `psy:narrative-twist --scan` — find contradictions in existing data.

**List twists:** `psy:narrative-twist --list` — review all TWIST markers across all profiles.

## 4. Use cases (each = a sample conversation)

### Use case: Single-character twist

> You: "Interview reveals Character B wasn't actually abandoned at 8; his father visited secretly. Update profile."
> Skill: `psy:narrative-twist --character character-b --fact "Father abandoned family when Character B was 8" --truth "Father visited secretly, maintained contact" --source "P1, new interview"`
> → Finds 3 occurrences in timeline/overview.md, psychology/core-wounds.md, darkness/traumas.md. Applies strikethrough + TWIST. Updates psychology/formulation.md (core wound recalibration). Outputs report.

### Use case: Relationship twist (cascade)

> You: "Character A and Character B's kết nghĩa date was NOT Sep 2025; it was actually Oct 2025. Also affects Character B's timeline."
> Skill: `psy:narrative-twist --character character-a --fact "Kết nghĩa with Character B: September 2025" --truth "Kết nghĩa with Character B: October 2025" --source "P1, corrected materials"`
> → Updates Character A's timeline. Automatically finds + updates Character B's timeline, relationships/hieu.md. Validates symmetry. Suggests: run psy:crossref --pair hieu hoa to confirm.

### Use case: Scan for latent twists

> You: "I suspect there are contradictions I haven't resolved. What needs twist markup?"
> Skill: `psy:narrative-twist --scan`
> → Finds: (1) Character C's mẹ kế narrative marked [DISPUTED]. (2) Character A's self-image vs Character C's description. Recommends: apply twist or resolve with additional materials.

## 5. Important caveats

- **Source is mandatory**: Every twist needs P{N} priority + date. Don't apply twists from speculation.
- **Markup, don't delete**: The old narrative stays (strikethrough). This preserves the story's evolution for future readers.
- **Cross-character validation is not optional**: A twist in one character's profile usually affects others. Run psy:crossref after applying twists.
- **Psychological reframing needed**: If twist touches core-wounds or formulation, the psychology interpretation shifts. Expect psy:ref-audit to flag changes.
