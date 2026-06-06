# orc:classify — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Not all work is equally risky. Editing Character A's timeline is straightforward. Updating Character B's formulation with new psychology is riskier—it affects clinical consistency. Changing cross-character relationship framing is riskiest. Classify tells you upfront: "this is high_risk, so plan accordingly." It saves you from discovering problems late.

## 2. Core concepts (the mental model)

**Three risk modes:** tiny (quick, low-friction), normal (moderate care needed), high_risk (full ceremony required). Each mode has different ceremony steps and proof strategy.

**Hard gates trigger high_risk immediately.** If you're changing cross-character consistency, clinical references, timeline, or public content with real names, it's high_risk before counting flags.

**Flags accumulate.** Even without hard gates, 4+ flags = high_risk. Examples: profile psychology edit + sensitivity topic + cross-character reference = 3 flags = normal. Add one more, it becomes high_risk.

**Ceremony is proportional.** Tiny = quick self-review. Normal = outline + cross-reference. High_risk = full bootstrap + plan + profile review + clinical check.

## 3. Learning path

**First run:** `orc:classify "write a LinkedIn post about Character A"` — tiny mode. Quick, no ceremony needed.

**Normal task:** `orc:classify "update Character B's psychology/attachment-style.md"` — normal mode. Requires outline + cross-reference check.

**High-risk task:** `orc:classify "add new relationship between Character A and Character C"` — high_risk mode. Full ceremony.

**Auto-mode:** `orc:classify --auto` — let it infer from git diff.

**Check current:** `orc:classify --show` — see what mode you're currently in.

## 4. Use cases (each = a sample conversation)

### Use case: Quick classification for simple task

> You: "Classify: write a quick post about Character A's mentoring philosophy"
>
> Skill: Detects "write post" → Content Creation work type. Counts flags: writing-voice consistency (flag 11). Total: 1 flag = tiny mode. Output: "Tiny mode. Quick self-review for tone/accuracy. Ready to implement."

### Use case: Normal-mode task with ceremony

> You: "Classify: update Character B's timeline with a new milestone"
>
> Skill: Detects "update timeline" → Profile Update. Counts flags: timeline continuity (hard gate — triggers high_risk). Output: "High_risk mode. Required ceremony: bootstrap full, plan, cross-reference timeline across characters, clinical check."

### Use case: Auto-classify from recent git changes

> You: "Classify --auto"
>
> Skill: Reads git diff, sees changes in psychology/ + relationships/, detects multi-character files. Counts: profile psychology edit (flag 1) + cross-character references (flag 6) = 2 flags = normal mode. Output: "Normal mode. Run outline + cross-reference check."

### Use case: Check current classification

> You: "Show me the current classification"
>
> Skill: Reads state.json, shows mode, phase, and ceremony steps already assigned in this session.

## 5. Important caveats

- **Classification is advisory.** It recommends ceremony, but you decide if you'll follow it. If you skip recommended steps on high_risk and something breaks, that's on you.
- **Auto-mode is heuristic.** It infers from git diff and branch name, which may miss context. If unsure, describe the task explicitly.
- **Ceremony is not guarantee of correctness.** High_risk ceremony (full bootstrap, clinical review, cross-ref check) reduces risk, but doesn't eliminate it.
- **Re-classify if scope changes.** If you start with "quick post" but add cross-character content midway, re-run classify. It's fast.
