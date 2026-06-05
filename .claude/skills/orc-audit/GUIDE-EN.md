# orc:audit — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

Events route between domains. But as code evolves, declarations can drift: a SKILL.md says "emits PSY.refresh" but the routing table doesn't expect it, or vice versa. Audit finds these inconsistencies: "PSY.refresh is declared in routing but not loggable," "MAT.integrated is emitted but not routed." It's a consistency check for the event system.

## 2. Core concepts (the mental model)

**6 consistency invariants:** routable ⊆ loggable (all events that route must be loggable), emits ⊆ routable (emitted targets must exist), path-map ⊆ routable (domain path rules must target valid events), etc.

**Hard violations vs advisories.** Violations (C1-C4) are errors. Advisories (C5-C6) are design notes.

**Read-only.** Audit reports findings; fixes are manual.

## 3. Learning path

**First run:** `orc:audit --domain all` — check all domains for consistency.

**Filter to domain:** `orc:audit --domain psy` — PSY events only.

**See suggestions:** `orc:audit --fix-suggestions` — get hints for fixing violations.

**JSON output:** `orc:audit --json` — structured report for parsing.

## 4. Use cases (each = a sample conversation)

### Use case: Check event consistency before release

> You: "Audit all events before shipping."
>
> Skill: Scans EVENT_ROUTING, SKILL.md tables, Python registries. Reports: "C1 violation: ORC.routed declared in SKILL.md ## Events but not in loggable registry." You fix: add ORC.routed to loggable types.

### Use case: Debug routing mismatch

> You: "PSY.refresh isn't cascading. Check audit."
>
> Skill: Reports: "C5 advisory: PSY.refresh is routable but not documented in rules-12." You verify: rules-12 was updated but event-routing wasn't. Fix routing table.

### Use case: Check specific domain

> You: "Any inconsistencies in CRE events?"
>
> Skill: Scans CRE event declarations only. Reports: "C4 violation: cre:privacy-guard declares COM.privacy event but not in loggable." You add COM.privacy to loggable registry.

## 5. Important caveats

- **Audit is advisory.** Violations are reported; you decide if they're actually problems.
- **Advisories are informational.** C5 (not documented) doesn't break anything, just notes incomplete documentation.
- **Scope: event declarations only.** This doesn't audit skill logic, just event consistency.
- **Fix suggestions are hints.** Review before applying; some may need context you have but the script doesn't.
