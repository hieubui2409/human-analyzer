---
name: com:skill-analytics
description: "Observability + analytics for the project's framework skills and scripts. Static infrastructure health (SKILL.md parseable, scripts syntactically valid, platform_lib fan-in), import dependency graph (critical/unused modules, cycles), and skill cascade/interaction topology (event chains, hubs, orphans). Reads the consolidated telemetry sink (.claude/telemetry/) for usage + perf when present. Deterministic gather only — never edits skills. Distinct from orc:audit (event consistency) and orc:skill-stocktake (catalog necessity). Use to check skill/script health before a release, find broken scripts, map dependencies, or surface unused/critical modules. Triggers: 'skill health', 'skill analytics', 'dependency graph', 'script health', 'which scripts are broken', 'platform_lib usage', 'cascade graph', 'unused modules'."
argument-hint: "[--health | --deps | --cascade | --all] [--json] [--format md|json] [--perf] [--framework mat|psy|cre|gro|orc|com] [--dot] [--orphans] [--critical]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "com-framework"
  position: "maintenance"
  dependencies: []
---

# com:skill-analytics — Skill & Script Observability

Deterministic, read-only observability for the 6 framework domains' skills + scripts +
`platform_lib`. Three lenses (infrastructure health, dependency graph, cascade topology)
plus optional usage/perf from the consolidated telemetry sink. Scope = project framework
skills only (`mat-/psy-/cre-/gro-/orc-/com-`), never ck skills.

## When to Use

- Before a release or after adding/editing scripts — confirm nothing is structurally broken.
- To locate a syntax-broken script across 56 skills fast (`--health`).
- To see which `platform_lib` modules are critical (high fan-in) or unused (`--deps`).
- To map how skills wire together via framework events (`--cascade`).
- NOT for event-consistency auditing → that is `orc:audit`.
- NOT for catalog overlap/necessity → that is `orc:skill-stocktake`.
- NOT for CE-02 progressive-disclosure conformance → that is `orc:skill-stocktake --ce02`.

## Subcommands

| Flag         | Item   | Does                                                                          |
| ------------ | ------ | ----------------------------------------------------------------------------- |
| `--health`   | S2     | SKILL.md parseable + script syntax (ast/`bash -n`) + platform_lib fan-in + perf |
| `--deps`     | P3     | Import dependency graph; flag critical (≥20 fan-in), unused, circular modules  |
| `--cascade`  | P4     | Skill interaction topology from SKILL.md event refs; hubs + orphans            |
| `--all`      | —      | Run all three sequentially                                                     |

```bash
PY=.claude/skills/.venv/bin/python3
S=.claude/skills/com-skill-analytics/scripts
$PY $S/check-skill-and-lib-health.py [--perf] [--framework psy] [--json]
$PY $S/build-dependency-graph.py [--critical] [--dot] [--json]
$PY $S/build-cascade-graph.py [--orphans] [--dot] [--json]
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
