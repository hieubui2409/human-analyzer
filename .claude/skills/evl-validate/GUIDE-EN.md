# evl:validate — Guide

The structural honesty gate: prove a rubric or a finished scorecard is trustworthy before anything acts on it.

## 1. What this skill does for you

You have a rubric you just authored, or a scorecard that came back from the scoring engine. Before you score characters against that rubric — or before CRE consumes that scorecard — you want to know: is this structurally sound? Are the weights right? Are criterion ids consistent? Is every score in bounds and correctly aggregated?

`evl:validate` answers those questions with a deterministic, algebraic report. No LLM judgment, no network, no side effects. It either prints PASS or shows you exactly what is broken and where.

## 2. Core concepts (the mental model)

- **Two modes, one script.** RUBRIC mode validates the rubric file itself. SCORECARD mode validates a finished scorecard against its rubric. The same `--rubric` flag appears in both — it is always required context.
- **Shape vs. invariants.** Rubric validation has two layers: JSON-Schema Draft-7 (shape: enums, required keys, types, ranges) and cross-field invariants the schema cannot express (weight sums, judge floor, clinical rails, threshold coverage, anchor endpoints). Shape errors short-circuit the invariant pass.
- **UNMAPPED is loud, not always fatal.** A criterion id in the scorecard that does not exist in the rubric is UNMAPPED — a loud finding printed in the table. It is non-fatal by default (the rubric may have been revised after scoring). Add `--strict` to make UNMAPPED a hard FAIL.
- **Exit code is the gate.** Exit 0 means all checks are PASS or SKIP. Non-zero means at least one FAIL — a CI step can use this directly.
- **Read-only, always.** The script never writes anything. All remediation is manual.

## 3. Learning path

1. Run `--all` and read the output: each rubric prints PASS or a list of errors. This is the fastest way to confirm the rubric library is coherent.
2. After scoring a character, run SCORECARD mode on the resulting JSON. Compare the checker table row by row — `aggregate_math_correct` is the most revealing; a mismatch there means the stored scores were edited post-aggregation.
3. Try `--strict` on a scorecard from an older rubric version: UNMAPPED rows become FAIL, surfacing criterion ids that have drifted out of sync.
4. Pipe `--json` into `jq` for programmatic filtering: `jq '.checks[] | select(.status=="FAIL")'`.

## 4. Use cases (each = a sample conversation)

### Use case: Gate a new rubric before first use

> "evl:validate --rubric role-casting-fit"

The skill runs `evl_schema.validate_rubric`. If the domain weights do not sum to 1.0, or a criterion is missing an interior anchor point, the error is printed with the exact field path. Fix → re-run → PASS → safe to score.

### Use case: Verify a scorecard before publishing to CRE

> "evl:validate --scorecard docs/profiles/character-a/eval/psychometric-big-five.json --rubric psychometric-big-five"

The checker registry runs seven proofs. If `aggregate_math_correct` is FAIL, the stored `overall` value does not reproduce from the raw criterion scores — the scorecard was likely hand-edited after finalization and must be re-generated before CRE trusts it.

### Use case: Bulk rubric audit before a library release

> "evl:validate --all --json | jq '.rubrics[] | select(.valid==false)'"

Returns only invalid rubrics, each with its error list. Useful before shipping a new rubric batch to confirm no regressions.

### Use case: Strict check after rubric revision

> "evl:validate --scorecard <path> --rubric <revised-id> --strict"

After adding a criterion to a rubric, existing scorecards will have UNMAPPED rows for the new id. `--strict` surfaces these as FAIL — the scorecard must be re-scored to include the new criterion before it is considered current.

## 5. Important caveats

- RUBRIC mode catches structural problems; it cannot catch a rubric that is structurally valid but substantively wrong (e.g., badly calibrated anchors). Substantive review is always heuristic — LLM judgment, not this script.
- `aggregate_math_correct` recomputes aggregation from scratch using `evl_aggregate.aggregate`. If the rubric was revised between scoring and validation, the recomputation uses the new rubric — the mismatch will FAIL even if the original scorecard was correct. Always validate against the same rubric version used for scoring.
- `--all` is non-recursive: it reads only top-level `docs/rubrics/*.yaml`. Drafts or imports nested in subdirectories are not checked unless explicitly passed via `--rubric <path>`.
- `--json` output structure: `{mode, verdict, rubrics: [{id, valid, errors}]}` for RUBRIC mode; `{mode, verdict, checks: [{check, status, detail}]}` for SCORECARD mode. The top-level `verdict` is always `"PASS"` or `"FAIL"`.
