# orc:cascade — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

When you change a profile or ingest new material, multiple domains need to react. Material integrated (MAT) → profile refreshed (PSY) → content recalibrated (CRE) → voice audited. That's a cascade. Without visibility, you don't know what work downstream has been triggered. Cascade maps the full chain for you.

## 2. Core concepts (the mental model)

**Events trigger downstream skills.** Each domain (MAT, PSY, CRE, GRO) emits events when work completes. Those events trigger downstream skills in other domains. Cascade follows that trigger chain.

**Chains can be deep.** Material integrated → PSY.refresh → CRE.recalibrate → privacy-guard. That's 3 hops. Cascade shows all of them.

**Circular references are possible.** If PSY.refresh triggers GRO.assessed, which triggers PSY.refresh again, you have a loop. Cascade detects it and stops.

**Max-depth prevents runaway.** By default, cascade stops at depth 5. You can raise it, but deep chains are usually a sign of misconfigured routing.

## 3. Learning path

**First run:** `orc:cascade --trigger MAT.integrated` — see what happens after material ingestion.

**Explore other triggers:** Try `PSY.refresh`, `CRE.recalibrate`, `GRO.assessed` to understand routing.

**Check for loops:** `orc:cascade --trigger PSY.refresh --max-depth 10` — if it stops before 10, there's no loop.

**JSON mode:** `orc:cascade --trigger MAT.integrated --json` — structured output for parsing.

## 4. Use cases (each = a sample conversation)

### Use case: Understand cascade after material ingestion

> You: "I just ingested a new transcript. What cascades from that?"
>
> Skill: Runs `orc:cascade --trigger MAT.integrated`, outputs:
> - Depth 0: MAT.integrated
> - Depth 1: PSY.refresh (psy:crossref, psy:ref-audit)
> - Depth 2: CRE.recalibrate (cre:voice-audit)
> - Depth 3: (none)
>
> You see: PSY must refresh, then CRE must audit voice. Plan accordingly.

### Use case: Check for circular cascades

> You: "Does changing PSY profiles cause infinite loops?"
>
> Skill: Runs `orc:cascade --trigger PSY.refresh --max-depth 10`, outputs chain without hitting the limit. You confirm: no loops, safe to make the change.

### Use case: Plan impact before high-risk change

> You: "If I update the growth domain, what domains react?"
>
> Skill: Runs `orc:cascade --trigger GRO.assessed`, shows which PSY, CRE skills get triggered downstream. You factor that into your planning.

## 5. Important caveats

- **Cascade is planning, not execution.** It maps the chain but doesn't run anything.
- **Routing is deterministic.** The cascade chain is hardcoded in EVENT_ROUTING; it doesn't change based on content.
- **Max-depth is a safety valve.** If you hit depth 5, there's a loop or deeply chained cascade. Check the routing config.
- **Event names matter.** `MAT.integrated` cascades differently than `MAT.archived`. Use the exact event name.
