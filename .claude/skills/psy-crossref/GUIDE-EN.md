# psy:crossref — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You updated Character A's profile with a new event, but forgot to update Character B's story — they're sworn brothers, so the event affects both. Or you notice Character A says he met Character B in July 2025, but Character B's timeline says June. This skill catches those breaks: it reads all profiles, finds every mention of the other character, and checks that dates match, emotions are compatible, and details don't contradict.

## 2. Core concepts (the mental model)

- **Deterministic + LLM split**: Dimensions 1–4 (dates, family refs, psychology links, hard facts) run script-based checks. Dimensions 5–10 (evidence backing, narrative coherence, voice consistency) need human judgment — the LLM does that.
- **Verdict cache**: The 6 LLM dimensions reuse cached verdicts if the profile section hasn't changed (verified by content hash). This saves tokens. Crisis verdicts are never cached (always re-run).
- **Severity matters**: A date mismatch is CRITICAL (one of them is wrong). A different emotional tone is MINOR (both feelings valid, just framed differently).

## 3. Learning path

**First run:** `psy:crossref --pair hieu hoa` — check just the sworn brothers, see the format.

**Expand:** `psy:crossref --all --extended` — run all pairs, all 10 dimensions. Expect a rich report.

**Iterate:** Fix issues in profiles, then `psy:crossref --fresh` to clear cache and re-check.

## 4. Use cases (each = a sample conversation)

### Use case: Quick timeline check (you just added a date)

> You: "I added Oct 2025 to Character A's timeline for the gambling crisis. Does Character B agree?"
> Skill: `psy:crossref --timeline --pair hieu hoa`
> → Finds Character B's timeline says Sep 2025. CRITICAL mismatch. You fix one of them, re-run.

### Use case: Full validation (major profile update)

> You: "I rewrote Character A's psychology/formulation.md and added new relationships. Are there any breaks?"
> Skill: `psy:crossref --all --extended --report`
> → Runs all pairs, all 10 dimensions. Finds: (1) Character A now claims intense savior complex, but Character C's profile says Character A is "withdrawn mentor". Check coherence. (2) Timeline consistent. → Saves detailed report.

### Use case: Cross-character cascade (one character changed, others didn't)

> You: "Character B's psychology file now mentions 'anxious attachment'. Does this affect Character A and Character C's relationship files?"
> Skill: `psy:crossref --pair hoa hieu --extended` + `psy:crossref --pair hoa chien --extended`
> → Checks if Character A/Character C describe Character B's behavior in ways consistent with anxious attachment. May need updates.

### Use case: Evidence backing (clinical terms must have sources)

> You: "I used the term 'complex-PTSD' in Character C's profile. Is that backed by materials?"
> Skill: `psy:crossref --dimension 5 --character character-c`
> → Dimension 5 (Evidential Backing) checks: does Character C's profile claim ≥T3 material evidence? Flags if not.

## 5. Important caveats

- **Not a fixer**: This skill reports problems; you decide what to fix. Different emotional framings of the same event (Character A: "brave," Character B: "reckless") are valid — not an error.
- **Requires full profiles**: If a character file is empty or very thin, crossref can't find enough detail to validate. Run `psy:health-check` first to fill gaps.
- **Cache only helps if unchanged**: If you re-edit a profile section, the cache invalidates. `--fresh` forces re-judgment if you want to verify.
- **Crisis/narrative-twist never cached**: By design. If a profile hints at suicide risk or a revealed falsehood, the skill always re-runs that check (no token shortcut).
