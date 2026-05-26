---
name: com:skill-analytics
description: "Observe and analyze the project's framework skills + scripts across six read-only lenses: infrastructure health, import dependency graph, skill cascade topology, usage analytics + per-skill token attribution, SKILL.md context-budget + trigger-overlap + coverage gaps, and content-pipeline health. Deterministic gather only — never edits skills; distinct from orc:audit (event consistency) and orc:skill-stocktake (catalog necessity). Use for pre-release skill/script health, finding broken scripts, mapping dependencies, spotting unused or token-costly skills, or surfacing content gaps. Triggers: 'skill health', 'skill analytics', 'dependency graph', 'platform_lib usage', 'cascade graph', 'skill usage', 'token usage per skill', 'context budget', 'content pipeline', 'posts per platform'."
argument-hint: "[--health | --deps | --cascade | --usage | --coverage | --content | --all] [--json] [--format md|json] [--perf] [--tokens] [--days N] [--top N] [--framework mat|psy|cre|gro|orc|com] [--dot] [--orphans] [--critical] [--budget-only] [--gaps-only] [--decommission] [--platform NAME] [--since YYYY-MM-DD]"
metadata:
  author: hieubt
  version: "1.1.0"
  category: "com-framework"
  position: "maintenance"
  dependencies: []
---

# com:skill-analytics — Skill & Script Observability

Deterministic, read-only observability for the 6 framework domains' skills + scripts +
`platform_lib`. Six lenses (infrastructure health, dependency graph, cascade topology,
usage analytics, coverage/budget, content pipeline) over static structure + the
consolidated telemetry sink. Scope = project framework skills only
(`mat-/psy-/cre-/gro-/orc-/com-`), never ck skills.

## When to Use

- Before a release or after adding/editing scripts — confirm nothing is structurally broken.
- To locate a syntax-broken script across 56 skills fast (`--health`).
- To see which `platform_lib` modules are critical (high fan-in) or unused (`--deps`).
- To map how skills wire together via framework events (`--cascade`).
- To see which skills are actually used and what they cost in tokens (`--usage --tokens`).
- To find SKILL.md context-budget hogs, overlapping triggers, or decommission candidates (`--coverage`).
- To check content cadence — posts per platform, inactive platforms (`--content`).
- NOT for event-consistency auditing → that is `orc:audit`.
- NOT for catalog overlap/necessity → that is `orc:skill-stocktake`.
- NOT for CE-02 progressive-disclosure conformance → that is `orc:skill-stocktake --ce02`.

## Subcommands

| Flag         | Item   | Does                                                                          |
| ------------ | ------ | ----------------------------------------------------------------------------- |
| `--health`   | S2     | SKILL.md parseable + script syntax (ast/`bash -n`) + platform_lib fan-in + perf |
| `--deps`     | P3     | Import dependency graph; flag critical (≥20 fan-in), unused, circular modules  |
| `--cascade`  | P4     | Skill interaction topology from SKILL.md event refs; hubs + orphans            |
| `--usage`    | S1     | Invocation counts (invocations.jsonl) + per-skill token attribution (session JSONL); never-used list |
| `--coverage` | S4     | SKILL.md context budget (tokens), trigger-keyword overlap, routing/catalog gaps, decommission list |
| `--content`  | M5     | Posts per platform from assets/; last-post date, cadence, inactive platforms   |
| `--all`      | —      | Run all six sequentially                                                       |

```bash
PY=.claude/skills/.venv/bin/python3
S=.claude/skills/com-skill-analytics/scripts
$PY $S/check-skill-and-lib-health.py [--perf] [--framework psy] [--json]
$PY $S/build-dependency-graph.py [--critical] [--dot] [--json]
$PY $S/build-cascade-graph.py [--orphans] [--dot] [--json]
$PY $S/scan-skill-usage-and-tokens.py [--days 30] [--tokens] [--top 20] [--framework psy] [--json]
$PY $S/analyze-skill-coverage-and-budget.py [--budget-only] [--gaps-only] [--decommission] [--json]
$PY $S/scan-content-pipeline-health.py [--platform facebook] [--since 2026-01-01] [--json]
```

## Determinism Split (GOLDEN RULE #4)

| Layer  | Owner  | Does                                                                       |
| ------ | ------ | -------------------------------------------------------------------------- |
| Script | gather | Parse with `ast`, count importers, extract event tokens, read telemetry    |
| LLM    | judge  | Decide if an "unused" module is dead vs deferred, if an orphan is intended  |

A module reported `unused` (0 direct importers) may still be live via the
`platform_lib/__init__.py` auto-import (e.g. `telemetry`) — the LLM interprets, the
script only reports the raw count.

## Output

`--format md` (default) prints tables; `--json` emits structured data for the dashboard
(M1) to compose; `--dot` (deps/cascade) emits graphviz. Health exits non-zero if any skill
is BROKEN (CI signal).

## Anti-Patterns

- Do NOT treat a `--health` BROKEN flag as a verdict to delete a skill — it means a syntax
  error to fix, not a skill to retire.
- Do NOT use this to judge skill *necessity* or *overlap* (that is `orc:skill-stocktake`).
- Do NOT scan ck skills — scope is the 6 project frameworks; ck is out of bounds.
- Do NOT have scripts decide refactors — they gather; the LLM adjudicates.
- Do NOT read raw telemetry for behavioral signals here — observation signals belong to
  `orc:observe`; this skill reads only invocation/perf metrics.
