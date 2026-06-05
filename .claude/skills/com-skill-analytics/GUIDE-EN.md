# com:skill-analytics — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You have 58 framework skills spread across 6 domains. Some are heavily used, some are broken, some cost tokens. Before a release, after adding a script, or when tracking down a weird error, you want a quick health snapshot: which skills are broken? What depends on what? Which platforms haven't posted in weeks? How reliable are subagents? com:skill-analytics gives you 11 different lenses to answer these questions.

## 2. Core concepts (the mental model)

**11 observability lenses:** Each lens answers one question — infrastructure health (S2), dependency graph (P3), skill interaction (P4), usage patterns (S1), coverage gaps (S4), content cadence (M5), unified dashboard (M1), memory health (M6), subagent reliability (M3), forensics (P1), workflow chains (S5).

**Determinism split:** Scripts gather (syntax, imports, metrics). LLM judges (is this unused module dead or deferred? Is an orphan skill intentional?). Scripts over-flag; humans filter.

**Read-only observability:** Gathers telemetry, counts, structure. Never modifies code. Use for diagnosis, not treatment.

**Scope = project frameworks only:** Watches mat, psy, cre, gro, orc, com skills. Ignores ck (user-invoked developer tools).

## 3. Learning path

**First run:** `com:skill-analytics --health`. Scans all skills for syntax errors, broken imports, perf issues. Takes 30s. Good baseline.

**Next:** Try `--dashboard`. Gets all 11 lenses at once, produces a color-coded traffic-light table. One page, whole project health.

**As you grow:** Use `--deps` to map critical modules; `--coverage` to find trigger overlaps; `--reliability` to track subagent failures over time; `--forensics --all-sessions` to reconstruct what happened in past sessions.

## 4. Use cases (each = a sample conversation)

### Use case: Find a broken script fast

> You: "which skill is broken?"
> Skill: `com:skill-analytics --health`. Scans syntax with `ast`, bash `-n`, imports. Reports `psy:crossref/scripts/validate.py — SyntaxError: line 42`. You fix it, run again.

### Use case: One-glance project health

> You: "give me the health dashboard"
> Skill: `com:skill-analytics --dashboard`. Produces a traffic-light summary: green=healthy, yellow=warnings, red=broken. Shows health, coverage, memory, reliability, content per skill. One page, decision-ready.

### Use case: Map dependencies and find critical modules

> You: "which modules are critical?"
> Skill: `com:skill-analytics --deps --critical`. Builds import graph, flags modules with ≥20 fan-in. Reports: `platform_lib/telemetry.py — 23 importers — CRITICAL`. You know that one is essential.

### Use case: Track subagent reliability over time

> You: "how reliable are subagents?"
> Skill: `com:skill-analytics --reliability --days 30`. Scans error logs, counts success/api_error/timeout per agent type. Reports: `researcher — 87% success, 10% timeout, 3% api_error`. Trends show if something's degrading.

### Use case: Find unused or low-value skills

> You: "what skills do we never use?"
> Skill: `com:skill-analytics --usage --tokens`. Counts invocations per skill + token cost. Reports: `gro:career-path — 2 invocations, 850 tokens/call — candidate for decommission?`. LLM then decides if it's truly dead or just deferred.

### Use case: Audit content pipeline health

> You: "are we posting regularly?"
> Skill: `com:skill-analytics --content --since 2026-04-01`. Counts posts per platform, detects last-post date, cadence gaps. Reports: `facebook — last post 2026-05-10, 3 posts in 30 days, cadence OK | linkedin — no posts since 2026-03-15 — INACTIVE`.

## 5. Important caveats

**Over-flagging by design.** A module reported "unused" (0 direct importers) might still be live via `__init__.py` auto-import. The script only reports the raw count; the LLM interprets.

**This is diagnosis, not treatment.** Health-check flags a broken script; you fix it. Workflow-chains shows deviations from routing docs; you decide if they're intentional or drift.

**Forensics need transcripts.** `--forensics` reconstructs sessions from JSONL transcript files. If a session has no transcript, forensics is incomplete.

**Scope is frameworks, not ck.** If you ask for `--deps` on the whole project and wonder why ck skills are missing, that's by design. This watches the 58 project skills, not 200+ ck skills.

**Memory health checks are dry-run by default.** Use `--memory --fix` to see what would be cleaned; `--memory --fix --apply` to actually write. Never auto-deletes without `--apply`.
