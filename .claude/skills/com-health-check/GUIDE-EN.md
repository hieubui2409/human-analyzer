# com:health-check — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've started a long task — maybe spawned a researcher agent or a team. You want to know if things are still running, or if something broke silently. com:health-check watches in the background and tells you the moment something goes wrong (stall, API error, process died). No surprises at the end.

## 2. Core concepts (the mental model)

**Polling:** Every 30 seconds (default), it checks: is the session JSONL file fresh? Is the process still alive? Did an error just happen?

**Stall detection:** If no output for > 120s (soft), warns you. If > 300s (hard), raises an error. Gives the session time to think, but flags real hangs.

**Target-specific:** You can watch just the main agent, just subagents, or a team. Each has its own liveness logic.

**Reactive, not preventive:** It detects failures but doesn't fix them. You get the alert, you decide what to do.

## 3. Learning path

**First run:** Spawn a task and run `com:health-check --target main` in another window. Watch heartbeat messages (OK, every few polls).

**Next:** Try with a subagent: `com:health-check --target subagent --verbosity warn`. Gets quieter, only alerts when something's wrong.

**As you grow:** Use `--hard 600` if your tasks are known slow; use `--include-429` if you want to catch rate limits; use `--all` if you're running a full team.

## 4. Use cases (each = a sample conversation)

### Use case: Monitor the main agent while working

> You: "monitor health while I work"
> Skill: `com:health-check --target main`. Runs in background, polls every 30s. You see `[INFO] OK ...` heartbeats. If a stall happens, you get `[WARN] STALL ... soft` or `[ERROR] STALL ... hard`.

### Use case: Watch subagents after delegating work

> You: "watch the subagent I just spawned"
> Skill: `com:health-check --target subagent --verbosity warn`. Monitors subagent processes. If one dies or returns an error, you see `[ERROR] API_ERROR ...` or `[ERROR] DEAD ...`.

### Use case: Catch stalls early with custom thresholds

> You: "monitor with early warning — stall me at 60 seconds"
> Skill: `com:health-check --soft 60 --hard 120`. Warns after 1 minute, errors after 2. Good for interactive tasks where hang time is unacceptable.

### Use case: Monitor a team session

> You: "watch the team I spawned"
> Skill: `com:health-check --target team --team-name my-team`. Tracks all agents in the team; reports per-agent failures.

### Use case: Verbose debug mode for hard-to-diagnose issues

> You: "give me detailed health info for debugging"
> Skill: `com:health-check --verbosity debug`. Prints internal state: session ID, last-modified timestamp, process status. Helps when you need to reconstruct what happened.

## 5. Important caveats

**Heartbeats are OK.** The `[INFO] OK ...` messages are expected; they mean "still running, no issues". Don't treat them as a problem.

**Soft stalls are warnings, not errors.** A soft stall means the LLM might be thinking or waiting for user input. Not an automatic fail.

**Rate limits (429) are off by default.** If you want to see 429 errors as alerts, add `--include-429`. Without it, they're silently logged.

**This is passive.** Health-check does not retry, does not fix, does not intervene. It reports; you act.

**Poll interval trade-off.** Lower `--poll` (e.g., 5s) gives faster alerts but burns CPU. Higher (e.g., 60s) is cheaper but slower to notice. Default 30s is a middle ground.
