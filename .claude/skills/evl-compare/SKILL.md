---
name: "evl:compare"
description: "EVL cross-character comparison — rank characters against each other on the same rubric using already-written scorecards. Purely deterministic: no LLM judging. Missing scorecards are surfaced loud, never dropped. Run evl:score first to produce the scorecards this skill reads. Triggers: 'evl compare', 'rank characters on rubric', 'compare characters', 'cross-character ranking'."
argument-hint: "compare --rubric-id <id> [--characters a,b,c] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "comparison"
  dependencies: []
---

# evl:compare — Cross-Character Ranking (EVL Framework)

Rank characters against each other on one rubric, using already-written scorecards. This skill
is purely deterministic — it performs zero LLM judgment; the scores must already exist (produced
by `evl:score`).

**Design law:** there is no Agent-tool step here. The script loads scorecards, normalises scores
across the cohort, and emits a ranked markdown table. The LLM's role is to interpret the output,
not to produce it.

## Default (No Arguments)

Ask for the rubric id, then run the command below with all characters in `paths.ALL_CHARS`.

## Flags

| Flag | Purpose |
|------|---------|
| `--rubric-id <id>` | Rubric id (matches the scorecard filename under `docs/profiles/{char}/eval/`) |
| `--characters a,b,c` | Comma-separated subset (resolved via `paths.resolve_character`); default = all |
| `--json` | Machine-readable comparison result |

## Workflow (LLM-executed)

### Step 1 — Run the comparison script (deterministic)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-compare/scripts/run_compare.py --rubric-id <id>
```

The script calls `evl_compare.compare(rubric_id, characters)` then prints
`evl_compare.render_comparison(result)` as markdown (or `json.dumps(result)` with `--json`).

### Step 2 — Interpret the output (LLM)

Read the ranked table + missing list and offer commentary:
- Highlight meaningful gaps between ranks (raw score distance).
- Note the z-score and percentile columns; when the cohort is < 3, these are suppressed with a
  note — do not treat absence of z-score as an error.
- For every character listed as `missing`: remind the user to run `evl:score` for that character
  before the comparison can include them.

### Step 3 — Emit EVL.compared (optional)

If the comparison result will feed downstream content, emit `EVL.compared` to the event log
(see `orc:event-log`) so CRE may pick up the ranking as a content angle.

## What this skill reads

`docs/profiles/{char}/eval/{rubric-id}.json` for each character in the cohort. If the file is
absent, the character is listed as `missing` — loudly, never silently dropped, never imputed.

## What this skill does NOT do

- **No LLM judging:** scores pre-exist; this skill only reads and ranks them.
- **No score imputation:** a missing scorecard is a gap, not a zero.
- **No auto-running evl:score:** if scorecards are missing, stop and tell the user.
- **No z-score for tiny cohorts:** z / percentile are suppressed when cohort < 3; a note explains
  why — do not paper over this with guessed values.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_compare.py` | Load scorecards → rank → render (fully deterministic, no LLM) |

## Safety

- Reads ONLY `docs/profiles/{char}/eval/{rubric-id}.json` (EVL eval zone).
- Writes nothing — comparison is ephemeral output, not a persisted scorecard.
- No network calls.
- No hardcoded character names — roster resolved via `paths.ALL_CHARS` + `paths.resolve_character`.

## Events

- **Emits:** `EVL.compared` (optional, if ranking feeds downstream CRE work).
- **Consumes:** scorecards written by `EVL.scored` events.

## Examples

```bash
/evl:compare --rubric-id psychometric-big-five
/evl:compare --rubric-id role-casting-fit --characters character-a,character-b
/evl:compare --rubric-id clinical-risk-safety --json
```

## See Also

- `evl:score` — produces the scorecards this skill reads
- `evl:track` — score over time (single character, multiple dates)
- `evl:standardize` — psychometric battery preset · `evl:fit` — role decision · `evl:compatibility` — dyad
- `docs/rules/17-evl-framework.md` — EVL domain rules
