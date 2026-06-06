# psy:wave — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've just integrated 10 interview transcripts for a new character. The profile is empty. Instead of manually editing 25 files in isolation, this skill orchestrates a structured 3-wave process: (1) Wave 1 extracts objective facts (identity, timeline, relationships) from materials. (2) Wave 2 analyzes psychology (wounds, defenses, coping, voice) with clinical backing. (3) Wave 3 validates everything (cross-character consistency, reference accuracy, cascade updates). You get a complete, validated profile at the end — not a scattered pile of half-filled files.

## 2. Core concepts (the mental model)

- **Wave model ensures completeness**: Each wave builds on the previous. Wave 1 = facts; Wave 2 = analysis; Wave 3 = consistency. Skip one, and the profile is weak.
- **Gates prevent garbage in**: After Wave 1, check: do we have enough timeline events? After Wave 2, check: are all clinical terms referenced? Wave 3 gate = psy:crossref + psy:ref-audit passing.
- **Cascade is built-in**: Wave 3 automatically runs psy:propagate, so related characters are updated symmetrically (not forgotten).

## 3. Learning path

**Full pipeline:** `psy:wave --character character-c --all` — create complete profile from scratch.

**Individual waves:** `psy:wave --character character-a --wave 1` (extract facts), then `--wave 2` (psychology), then `--wave 3` (validation).

**Check progress:** `psy:wave --character character-b --status` — see which waves are done.

**With plan context:** `psy:wave --character character-c --plan ./plans/260605-chiến-profile-build/plan.md` — tracks progress in plan file.

## 4. Use cases (each = a sample conversation)

### Use case: New character from scratch

> You: "I have materials for a new character (30 interview pages). Create a full profile."
> Skill: `psy:wave --character <name> --all`
> → Wave 1: Extracts 45 events, 8 family members, 12 relationships. Gate check: ≥N events? ✓ Proceed. → Wave 2: Identifies core wounds, defense mechanisms, triggers. Gate check: ≥5 triggers? ✓ ≥3 coping mechanisms? ✓ Proceed. → Wave 3: Runs psy:crossref (no other characters to compare yet, but structure validated). Runs psy:ref-audit (all clinical terms referenced). Outputs: complete 25-file profile + validation report.

### Use case: Major update to existing character

> You: "Character C's story evolved significantly. I have new materials (crisis event, revelation). Re-wave the profile."
> Skill: `psy:wave --character character-c --all`
> → Wave 1: Updates identity/core.md, timeline/overview.md, milestones.md with new events. Gate: all events dated? ✓ → Wave 2: Re-analyzes psychology/formulation.md in light of new crisis. Runs psy:crisis-assess (detects HIGH risk). Gate: crisis protocol applied? ✓ → Wave 3: psy:crossref checks if Character A/Character B files need updates (Character C's arc shifted). psy:propagate suggests updates. Validates. Done.

### Use case: Check wave progress

> You: "I started Wave 1 yesterday. What's the status?"
> Skill: `psy:wave --character character-a --status`
> → Wave 1: ✅ Complete (extracted 67 events, 15 relationships). Wave 2: 🔄 In Progress (psychology/formulation.md: 40% done). Wave 3: ⬜ Not Started. Blockers: "Finish psychology/formulation.md to proceed to Wave 3."

## 5. Important caveats

- **Waves are sequential, not parallel**: You can't skip Wave 1 and jump to Wave 2. Each builds on the previous.
- **Gates are non-negotiable**: If Wave 1 gate fails (too few events), wave won't proceed to Wave 2. Fix the gap first.
- **Wave 3 is mandatory**: You can't publish a profile without psy:crossref + psy:ref-audit passing (implied by Wave 3 completion).
- **Cascade updates need confirmation**: Wave 3 suggests cross-character updates but doesn't auto-apply. You confirm, then psy:propagate executes.
- **Post-wave actions required**: After Wave 3 completes, run `orc:compounding` to extract insights for memory, and update `orc:session-state` for recovery.
