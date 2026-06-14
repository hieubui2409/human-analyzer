# evl:track — Guide

Score-over-time tracker: see how a character's rubric score shifted between runs and what profile changes coincided.

## 1. What this skill does for you

You give it a character and a rubric id; it loads the current scorecard, finds the latest historical
snapshot, and computes the deltas — overall score, per-domain scores, verdict, and coverage. It also
pulls any profile-change events (PSY / GRO / MAT) from the requested time window and lays them next
to the diff so you can see what changed in the profile around the same time the score moved.

The script is deliberately dumb about causation: it joins facts by timestamp, nothing more. You (or
the LLM reading the output) decide whether a domain drop and a trauma-file update are actually related.

## 2. Core concepts (the mental model)

- **Current scorecard** — the live `.json` file under `docs/profiles/{char}/eval/` written by the
  last `evl:score` run.
- **History snapshot** — a prior `.json` copy in `eval/history/` (written automatically by `evl:score`
  before it overwrites the live file). The tracker takes the chronologically last snapshot as `prev`.
- **diff_scorecards** — None-safe arithmetic diff: `overall_delta`, `coverage_delta`, per-domain
  `delta`, and `verdict_change` (a `(prev, curr)` tuple when the verdict string changed, else `None`).
- **attribute_changes** — deterministic timestamp join: returns every event record in the PSY / GRO /
  MAT telemetry streams whose `character` matches and whose `timestamp` ≥ `--since`. No inference.
- **No-history case** — if `load_history` returns an empty list the script says so clearly and exits
  cleanly. A first scoring run has nothing to compare against.

## 3. Learning path

1. Run `evl:score` twice on the same character + rubric (the second run archives the first to `history/`).
2. Run `evl:track` and read the markdown summary — observe how `overall_delta` and domain deltas appear.
3. Pass `--since` with the timestamp of the first score run; confirm the relevant PSY / MAT events appear
   in the event list.
4. Pass `--json` and pipe the output into a script that watches for verdict regressions.

## 4. Use cases (each = a sample conversation)

### Use case: Check whether a new interview changed the Big Five assessment

> "Track character-a on psychometric-big-five since last month."

The skill loads the current scorecard and the previous snapshot, diffs them, then pulls any
MAT / PSY events since the given date. You see that the `Openness` domain rose by 0.4 points
and a new T2 interview transcript was ingested the day before the rescore — a plausible but
unconfirmed link for you to investigate.

### Use case: Audit a verdict regression

> "Did character-b's clinical risk score get worse?"

The diff shows `verdict_change: ("PASS", "PASS_WITH_RISK")` and `overall_delta: -0.6`. Two
PSY refresh events appear in the window — a `psychology/core-wounds.md` update and a new
trauma entry. The script does not assert causation; you read both events and decide whether
the clinical update justifies a full rescore with `evl:score --rescore`.

## 5. Important caveats

- The tracker needs at least two scoring runs to have a diff. On a first run, prompt the user to
  run `evl:score` once more after evidence is updated, then track.
- `--since` filters the **event list** only — the scorecard diff always covers current vs. latest
  snapshot regardless of the since date.
- A `None` delta in the output means one side was missing (e.g. a domain added in the rubric
  after the last snapshot). This is not a zero change — treat it as a gap, not an improvement.
- The script reads telemetry JSONL files line by line; a malformed line is skipped silently (not
  an error), matching the design of the other telemetry consumers in this codebase.
