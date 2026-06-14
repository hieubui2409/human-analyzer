# evl:compare — Guide

Rank characters against each other on one rubric using already-written scorecards.

## 1. What this skill does for you

You give it a rubric id (and optionally a character subset); it gives you back a ranked table —
each character's raw score, peer-relative z-score, percentile, and verdict, plus a loud list of
anyone whose scorecard is missing. There is no LLM judgment step: the scores already exist and
the script reads them deterministically.

## 2. Core concepts (the mental model)

- **Scorecard** — the JSON file at `docs/profiles/{char}/eval/{rubric-id}.json` written by
  `evl:score`. This skill reads it; it never writes one.
- **Raw score** — the weighted overall from the scorecard, on whichever scale the rubric defines
  (e.g. 0–5). Rankings are always by raw score descending.
- **z-score + percentile** — peer-relative normalization across the cohort, computed by
  `evl_normalize.normalize_cohort`. Suppressed when the cohort is < 3 characters (not enough
  data to normalize meaningfully); a note in the output explains the suppression.
- **Missing** — a character with no scorecard for this rubric. Listed separately, loudly. Never
  imputed as zero, never silently excluded.
- **No LLM judgment** — unlike `evl:score`, there is no Agent-tool judge step here. The numbers
  already exist; this skill only reads and ranks them.

## 3. Learning path

1. Score at least two characters on the same rubric with `evl:score`, producing their `.json`
   scorecard files.
2. Run `evl:compare --rubric-id <id>` and read the ranked table.
3. Add a third character's scorecard so the z-score and percentile columns become meaningful.
4. Try `--json` to see the raw comparison dict (useful for downstream scripting or CRE content).

## 4. Use cases (each = a sample conversation)

### Use case: Rank all characters on the Big Five

> "Compare all characters on psychometric-big-five."

The skill loads each character's `eval/psychometric-big-five.json`, ranks by raw overall, and
prints a table with z-score + percentile. Anyone without a scorecard appears in the `missing`
block with a reminder to run `evl:score` first.

### Use case: Narrow comparison on a role-fit rubric

> "Compare character-a and character-b on role-casting-fit."

The skill resolves the two names dynamically via `paths.resolve_character`, loads only those two
scorecards, and ranks them. Because the cohort is 2 (< 3), z-score and percentile are suppressed
with a note — raw scores are the only reliable comparison signal at that size.

### Use case: Machine-readable output for CRE

> "Give me the JSON comparison of all characters on clinical-risk-safety."

With `--json`, the script emits the raw `compare()` dict (ranked list + missing list) so a CRE
skill or downstream script can parse the result without screen-scraping the markdown table.

## 5. Important caveats

- Run `evl:score` for each character before comparing — this skill does not auto-invoke the scorer.
- z-score / percentile are suppressed for cohorts < 3; this is correct behavior, not a bug.
- Missing scorecards are always surfaced — never treat a missing row as "score = 0".
- The script is offline and writes nothing; comparison output is ephemeral.
- Verdict strings in the table come directly from the scorecard; this skill never re-derives them.
