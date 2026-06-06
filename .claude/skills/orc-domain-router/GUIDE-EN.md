# orc:domain-router — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

When you change a profile or ingest material, you're not just editing one file—you're triggering downstream work in other domains. Domain-router shows you the complete chain of what should execute next, so you can plan the full impact before starting.

## 2. Core concepts (the mental model)

**Events route to skills.** Each domain change (MAT, PSY, CRE, GRO) emits an event. That event triggers downstream skills. Router maps the chain.

**Routing is deterministic.** Rules are hardcoded: if MAT.integrated, then psy:crossref runs. If PSY.refresh, then cre:voice-audit runs. No randomness, no guessing.

**From-diff detection.** Router can infer which domains changed by looking at git diffs (profile/ = PSY, assets/ = CRE, docs/growth/ = GRO, etc.).

## 3. Learning path

**First run:** `orc:domain-router --from-diff` — see what changed and what should run.

**Explicit event:** `orc:domain-router --event MAT.integrated` — trace routing from one event.

**JSON mode:** `orc:domain-router --from-diff --json` — structured output for parsing.

**Dry-run:** `orc:domain-router --from-diff --dry-run` — plan without executing.

## 4. Use cases (each = a sample conversation)

### Use case: See routing after profile changes

> You: "I edited Character B's psychology files. What cascades from that?"
>
> Skill: Detects psychology/ change → PSY.refresh event → psy:crossref, psy:ref-audit run. Then those emit PSY.refresh downstream → CRE.recalibrate → cre:voice-audit runs. You see the full chain.

### Use case: Trace routing for explicit event

> You: "If MAT.integrated fires, what should run?"
>
> Skill: Maps EVENT_ROUTING: MAT.integrated → psy:ref-audit, psy:crossref. You see: material integration requires PSY skills to validate against profiles.

## 5. Important caveats

- **Routing shows recommendations, not guarantees.** You still need to actually run the skills.
- **Hardcoded rules mean no flexibility.** If routing doesn't match your workflow, that's a system design issue, not a skill issue.
- **From-diff is heuristic.** It infers from file paths; ambiguous changes may route to the wrong domain.
