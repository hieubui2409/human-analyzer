# orc:bootstrap — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Starting work on a complex, multi-character project means carrying ~7,400 lines of profile data in your mind. That's inefficient and error-prone. Bootstrap lets you load exactly the context you need—from a quick 5-minute INDEX scan to a deep 30-minute full-profile immersion. You control the depth.

## 2. Core concepts (the mental model)

**Context depth is a spectrum.** Quick (INDEX only) is fastest for a reminder. Full profiles take time but give clinical precision. Lite profiles (~400 lines total) split the difference. Intent-aware loading is smart: if you're writing LinkedIn content, you don't need timeline details, just writing-voice.

**Reading order matters.** Profiles are loaded in priority order—formulation first (most clinically dense), then defense mechanisms, then relationships. This ensures you absorb the highest-signal content early.

**Session state travels.** Bootstrap reads and reports your current session state (mode, phase, which characters you've touched). This helps you resume without losing context.

## 3. Learning path

**First run:** `orc:bootstrap --quick` — 2-3 minutes, get oriented on all 3 characters at a glance.

**Deep dive:** `orc:bootstrap --full` — 15-30 minutes, load everything. Do this before high-risk changes.

**Character focus:** `orc:bootstrap --character hiếu` — 5-10 minutes, all files for Nhân vật A only.

**Speed run:** `orc:bootstrap --lite` — 3 minutes, compressed summaries of all 3 characters.

**Task-aware:** `orc:bootstrap --intent "write LinkedIn post about Nhân vật B"` — loads only files relevant to that task.

## 4. Use cases (each = a sample conversation)

### Use case: Quick orientation at session start

> You: "Bootstrap, give me a quick overview"
>
> Skill: Loads INDEX.md for all 3 characters, shows git log of last 15 commits, prints session state (mode, phase, which profiles touched). 3 minutes. You're oriented.

### Use case: Deep load before high-risk profile edit

> You: "I'm about to update Nhân vật B's formulation. Load everything for her."
>
> Skill: Runs `--character character-b`, loads all files in her directory (psychology/, relationships/, timeline/, darkness/, light/), checks related theory files in references/, and shows Nhân vật B-specific git history. You're fully informed before editing.

### Use case: Lite profiles for token efficiency

> You: "I'm running low on context. Give me lite mode."
>
> Skill: Loads cached lite profiles for all 3 characters (~120-150 lines each, total ~400 lines). Much smaller than full profiles (~7400), enough for most work.

### Use case: Task-aware load to skip irrelevant files

> You: "I'm writing about Nhân vật A's writing style. Load only what's relevant."
>
> Skill: Detects "writing" keyword, loads only `identity/writing-voice.md`, skips timeline/relationships/darkness, saves tokens. Prints what was loaded and what was skipped.

### Use case: Check what changed recently

> You: "What happened in the last week?"
>
> Skill: Runs `--recent`, shows git commits and file changes from the last 7 days, filtered to profile/content/plan changes. Quick way to see what work was done.

## 5. Important caveats

- **Bootstrap is read-only.** It never modifies files. It only gathers context for you.
- **Full mode is token-heavy.** All 25 profile files × 3 characters is ~7,400 lines. Use lite or intent-aware modes to be efficient.
- **Lite profiles are summaries.** They compress ~2,500 lines per character to ~150. Useful for quick work, but not clinical-grade detail.
- **Intent-aware has limits.** If your task is ambiguous ("work on profiles"), it may load more than necessary. Be specific: "write post", "update timeline", "clinical analysis".
- **Git history is advisory.** Bootstrap shows recent commits, but doesn't execute git operations. Use `/com:git` for actual git work.
