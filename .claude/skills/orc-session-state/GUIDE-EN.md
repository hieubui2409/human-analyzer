# orc:session-state — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You resume a session from hours or days ago. What were you working on? Which profiles did you touch? What mode was the work (tiny/normal/high_risk)? Session state remembers. It also tracks pending domain events, active ingestions in MAT, and which character you were focused on. This lets you pick up mid-project without re-reading everything.

## 2. Core concepts (the mental model)

**Persistent JSON state.** `.claude/session-state/state.json` holds all session metadata. Hooks auto-update it as work happens (on SessionStart, Stop, and when domain events fire).

**Framework-aware tracking.** Session state tracks which domains are active (MAT/PSY/CRE/GRO), which characters were touched, pending events, and active pipelines.

**Archive for history.** When you `--archive`, current state is saved to timestamped markdown. Useful for looking back at what you accomplished.

## 3. Learning path

**First run:** `orc:session-state --show` — see current state.

**At session end:** `orc:session-state --archive` — save progress before stopping.

**Before `/compact`:** `orc:session-state --compact-digest` — write bounded summary so framework context survives compression.

**If corrupted:** `orc:session-state --reset` — clear state (keeps archives).

## 4. Use cases (each = a sample conversation)

### Use case: Check session progress

> You: "What's the current session state?"
>
> Skill: Shows: Mode=normal, Phase=creating, Branch=claude/features/character-b-psychology, Profiles touched=[character-b], Content created=[assets/linkedin/260605-post/], Decisions=[Character B attachment decision], Harness delta=3 files. You see: focused on Character B, creating content, normal risk, 3 harness changes.

### Use case: Archive session before stopping

> You: "Archive the session, I'm stopping."
>
> Skill: Saves current state to `.claude/session-state/archive/260605-1430.md`, resets state.json to defaults. Session history preserved; next session starts fresh.

### Use case: Write compact digest before `/compact`

> You: "Save a compact digest before compressing context."
>
> Skill: Runs `--compact-digest`, writes `.claude/session-state/compact-digest.json` with top-5 recent events per domain. On resume, `orc:bootstrap` re-injects this so framework context survives compression.

## 5. Important caveats

- **State is additive metadata.** Changes to state.json don't modify profiles; they're notes about what happened.
- **Archives are read-only.** Old archives help you understand history; they don't auto-restore.
- **Hooks auto-update state.** You rarely need to manually update state; hooks handle most updates.
- **Compact digest has size cap.** Stays ≤8 KB so it doesn't defeat context compression.
