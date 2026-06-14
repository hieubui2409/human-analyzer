---
name: "evl:validate"
description: "EVL deterministic structural checker — validate rubric shape + cross-field invariants (RUBRIC mode: --rubric <id|path> or --all) or validate a finished scorecard against its rubric (SCORECARD mode: --scorecard <json> --rubric <id|path> [--strict]). Blocks a malformed rubric or a tampered scorecard from being trusted. Triggers: 'evl validate', 'validate rubric', 'check scorecard', 'evl check'."
argument-hint: "(--rubric <id|path> | --all) | (--scorecard <json> --rubric <id|path> [--strict]) [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "validation"
  dependencies: []
---

# evl:validate — Structural Honesty Gate (EVL Framework)

Deterministic structural checker for EVL rubrics and scorecards. This gate blocks
a malformed rubric or a tampered scorecard from being trusted anywhere downstream.
No LLM judgment runs here — every check is algebraic.

**Design law:** the script calls `platform_lib` and prints; it never reasons about
content. An UNMAPPED criterion is loud but non-fatal unless `--strict`. An unknown
checker name is always FAIL — a misconfigured gate is never a silent pass.

## Default (No Arguments)

Validate all rubrics in `docs/rubrics/` — equivalent to `--all`.

## Modes

### RUBRIC mode

Validate the rubric's own shape (JSON-Schema Draft-7) + cross-field invariants:
weight sums, high-stakes judge floor, clinical rails, threshold coverage, anchor
endpoints, and tier vocabulary.

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-validate/scripts/run_validate.py --rubric <id|path>
$PY .claude/skills/evl-validate/scripts/run_validate.py --all
```

`--all` discovers every `docs/rubrics/*.yaml` via `evl_schema.list_rubrics` and
runs `evl_schema.validate_rubric` on each, printing all errors with rubric id
prefix. Exits non-zero if any rubric is invalid.

### SCORECARD mode

Load a finished scorecard JSON + its rubric and run
`evl_structural.run_structural(scorecard, rubric, strict)` — the full checker
registry (rubric_schema_valid · criteria_mapped · every_criterion_cited ·
weight_sum_unity · aggregate_math_correct · score_in_bounds ·
verdict_thresholds_cover_range). Prints a verdict table (PASS / FAIL / SKIP /
UNMAPPED per checker) and a final PASS / FAIL summary.

```bash
$PY .claude/skills/evl-validate/scripts/run_validate.py \
    --scorecard docs/profiles/character-a/eval/psychometric-big-five.json \
    --rubric psychometric-big-five
$PY .claude/skills/evl-validate/scripts/run_validate.py \
    --scorecard <path> --rubric <id> --strict  # UNMAPPED → FAIL
```

## Flags

| Flag | Purpose |
|------|---------|
| `--rubric <id\|path>` | Rubric to validate (id resolved under `docs/rubrics/`) |
| `--all` | Validate every `docs/rubrics/*.yaml` (RUBRIC mode) |
| `--scorecard <path>` | Scorecard JSON to validate (requires `--rubric`) |
| `--strict` | Treat UNMAPPED criteria as FAIL (default: loud but non-fatal) |
| `--json` | Machine-readable output |

## Checker Registry (SCORECARD mode)

| Checker | What it proves |
|---------|----------------|
| `rubric_schema_valid` | Rubric passes shape + invariants |
| `criteria_mapped` | Every scorecard criterion id matches the rubric |
| `every_criterion_cited` | No scored criterion lacks a citation + valid tier |
| `weight_sum_unity` | Domain and criterion weights each sum to 1.0 |
| `aggregate_math_correct` | Stored domain + overall scores reproduce from raw scores |
| `score_in_bounds` | Every score is within `[scale.min, scale.max]` |
| `verdict_thresholds_cover_range` | Verdict bands tile the full scale with no gap |

## Workflow Position

Run `evl:validate` in two natural checkpoints:

1. **After authoring or importing a rubric** — RUBRIC mode catches a broken rubric
   before any character is scored against it.
2. **Before consuming a scorecard** — SCORECARD mode catches a tampered or
   truncated scorecard before it feeds CRE or an external consumer.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_validate.py` | Thin arg → platform_lib → print. No heuristics. |

## Safety

- READ-ONLY in both modes — never writes any file.
- Reads only `docs/rubrics/` (rubric) and the explicit `--scorecard` path.
- No network, no Agent step; purely deterministic.
- Exit code 0 = all PASS (or SKIP); non-zero = any FAIL.

## Events

- **Emits:** none (read-only audit gate).
- **Consumed by:** `evl:score` calls `evl_schema.load_and_validate` internally;
  running `evl:validate` beforehand gives an explicit report rather than a raised
  exception mid-score.

## Examples

```bash
/evl:validate --all                                      # check every rubric
/evl:validate --rubric psychometric-big-five             # single rubric
/evl:validate --rubric docs/rubrics/clinical-risk-safety.yaml
/evl:validate --scorecard docs/profiles/character-a/eval/psychometric-big-five.json \
              --rubric psychometric-big-five
/evl:validate --scorecard <path> --rubric <id> --strict  # UNMAPPED = FAIL
/evl:validate --all --json                               # machine output
```

## See Also

- `evl:score` — scoring engine; calls the same `evl_schema.load_and_validate` gate
- `evl:standardize` · `evl:fit` · `evl:compatibility` — specialized scoring wrappers
- `evl:compare` · `evl:track` — cross-character ranking + time-series
- `docs/rules/17-evl-framework.md` — EVL domain rules
