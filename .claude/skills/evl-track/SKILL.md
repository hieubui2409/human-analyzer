---
name: "evl:track"
description: "EVL score-over-time tracker — show how a character's rubric score changed between the current scorecard and the latest historical snapshot, listing deterministic profile-change events in the window so the LLM can narrate why the score moved. Triggers: 'evl track', 'track score over time', 'score delta', 'how did score change'."
argument-hint: "track <character> on <rubric> [--since <ISO-Z>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "tracking"
  dependencies: []
---

# evl:track — Score-Over-Time Tracker (EVL Framework)

Show how a character's score on a rubric evolved between the current scorecard and
the latest historical snapshot. Purely deterministic — no LLM judging, no inference.

**Design law:** the script produces facts (numeric deltas, verdict change, profile-change
events in the time window); the **LLM narrates why** the score moved. Causal attribution
is the LLM's job reading the diff + event list, never the script's.

## Default (No Arguments)

Ask for the character + rubric id, then run the workflow below.

## Flags

| Flag | Purpose |
|------|---------|
| `--character <name>` | Character to track (resolved dynamically via `paths.py`) |
| `--rubric-id <id>` | Rubric id whose scorecard history is inspected |
| `--since <ISO-Z>` | Restrict profile-change events to this timestamp or later (default: all history) |
| `--json` | Machine-readable diff summary |

## Workflow (LLM-executed)

### Step 1 — Run the tracker (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-track/scripts/run_track.py \
    --character <name> --rubric-id <id> [--since <ISO-Z>] [--json]
```

The script calls `evl_tracker.load_current` (current scorecard JSON),
`evl_tracker.load_history` (chronological snapshots — takes the last as `prev`),
`evl_tracker.diff_scorecards(prev, curr)` (overall / domain / verdict / coverage deltas,
None-safe), and `evl_tracker.attribute_changes(character, since_ts)` (profile-change events
from PSY / GRO / MAT streams that overlap the time window). It prints a markdown summary or
`--json` object. If there is no history snapshot it reports that plainly — there is nothing
to diff on a first run.

### Step 2 — Narrate (LLM)

Read the diff output. For each non-null delta and each event in the window, form a causal
hypothesis grounded in the evidence:

- **Domain delta > 0 with a matching MAT or PSY event** — the new material or profile
  update plausibly raised the score; cite the event's `event_type` + `timestamp`.
- **Domain delta < 0** — consider whether a criterion was reclassified, evidence
  was revised, or a coverage drop explains the fall.
- **Verdict change** — state the transition (e.g. `MODERATE → HIGH`) and flag whether
  the rubric treats it as clinically significant.
- **No events in window** — note the score moved without a recorded profile change;
  a rescore with identical evidence may indicate a judge disagreement or rubric version
  change.

Never invent a causal link the events don't support. If the evidence is ambiguous, say so.

### Step 3 — Emit EVL.tracked (optional)

If the diff surfaces a clinically significant verdict change or a coverage drop ≥ 10%,
emit `EVL.tracked` via `orc:event-log` so downstream skills can react.

## Script

| Script | Purpose |
|--------|---------|
| `scripts/run_track.py` | Load scorecard + history → diff → event join → print |

## Safety

- Reads ONLY under `docs/profiles/{char}/eval/` + telemetry event files. Never writes.
- No network. No scoring heuristic. No causal inference.
- No hardcoded character names — resolved via `paths.resolve_character`.

## Events

- **Emits:** `EVL.tracked` (on significant verdict / coverage change).
- **Consumes:** scorecard files written by `evl:score`; event streams written by PSY / GRO / MAT.

## Examples

```bash
/evl:track --character character-a --rubric-id psychometric-big-five
/evl:track --character character-b --rubric-id clinical-risk-safety --since 2025-01-01T00:00:00Z
/evl:track --character character-a --rubric-id role-casting-fit --json
```

## See Also

- `evl:score` — run or re-run a scorecard · `evl:compare` — cross-character ranking
- `evl:validate` — rubric structural check · `evl:standardize` — psychometric battery preset
- `docs/rules/17-evl-framework.md` — EVL domain rules
