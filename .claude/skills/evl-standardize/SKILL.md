---
name: evl:standardize
description: "EVL psychometric-battery preset — score a character against the Big Five + Dark Triad SD3 + Attachment ECR-R battery, producing an evidence-cited scorecard plus LLM-narrated quadrant mapping and Dark Triad elevation flag. Thin wrapper over evl:score with rubric defaulting to psychometric-big-five. Triggers: 'evl standardize', 'psychometric battery', 'big five score', 'standardize character', 'run psychometric battery'."
argument-hint: "standardize <character> [--rubric <id>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "psychometric"
  dependencies: []
---

# evl:standardize — Psychometric Battery Preset (EVL Framework)

Score a character against the canonical psychometric battery (Big Five OCEAN · Dark Triad SD3 ·
Attachment ECR-R) and produce a scorecard plus two LLM-narrated clinical summaries: attachment
quadrant and Dark Triad elevation flag.

**Design law:** this skill is a thin rubric preset over `evl:score` — the default rubric is
`psychometric-big-five` but any psychometric rubric id is accepted. The script gathers evidence +
does the weighted aggregation; the **LLM judges each criterion** and must cite a MAT evidence tier
(T1–T5). An uncited criterion is `[UNVERIFIED]` — excluded from the score, counted, never a
silent pass.

## Default (No Arguments)

Ask for the character, then run the workflow below with `--rubric psychometric-big-five`.

## Flags

| Flag | Purpose |
|------|---------|
| `--character <name>` | Character to score (resolved dynamically via `paths.py`) |
| `--rubric <id>` | Rubric id or path under `docs/rubrics/` (default: `psychometric-big-five`) |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Re-run ignoring any cached scorecard |

## Workflow (LLM-executed)

### Step 1 — Validate + gather (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-standardize/scripts/run_standardize.py gather \
    --character <name> [--rubric <id>]
```

`run_standardize.py gather` calls `evl_schema.load_and_validate` (rejects a malformed rubric
loudly) then `evl_evidence.gather_for_rubric` — emitting a per-criterion evidence bundle
(candidate snippets with `file:line` + best-effort tier). The script only SURFACES candidates.

### Step 2 — Judge each criterion (LLM, Agent tool, input-isolated)

For each criterion in the three blocks (Big Five · Dark Triad · Attachment), spawn a judge
**Agent** that sees ONLY that criterion + its evidence bundle (never sibling verdicts — isolation
prevents cross-contamination). The judge returns a `CriterionScore`:
`{criterion_id, score, citation, tier, justification, verdict}`. It MUST cite one evidence item
by source + tier or return `verdict: UNVERIFIED`. The judge prompt contract is
`platform_lib/evl_judge.py:JUDGE_SYSTEM`.

### Step 3 — Finalize (deterministic, script)

Write the collected scores to a JSON file, then:

```bash
$PY .claude/skills/evl-standardize/scripts/run_standardize.py finalize \
    --character <name> --scores scores.json --asof <YYYY-MM-DD> [--rubric <id>]
```

`finalize` runs `evl_aggregate.aggregate` (weighted roll-up, excludes uncited) and
`evl_scorecard.write_scorecard` → `docs/profiles/{char}/eval/{rubric-id}.md` + `.json`.
The call passes `updated_by="evl:standardize"` so the scorecard provenance is traceable.

### Step 4 — Attachment quadrant narration (LLM, post-finalize)

Using the finalized `attachment-anxiety` and `attachment-avoidance` subscale scores, map the
character onto the two-dimensional ECR-R quadrant:

| Anxiety \ Avoidance | Low (< 2.5) | High (≥ 2.5) |
|---------------------|-------------|--------------|
| **Low (< 2.5)**     | Secure      | Dismissing-Avoidant |
| **High (≥ 2.5)**    | Preoccupied | Fearful-Avoidant |

Write a brief clinical narrative (2–4 sentences) explaining the quadrant assignment with
reference to the evidence citations already in the scorecard. Place the narrative in the
`notes` section of the scorecard or as a standalone comment in the session.

### Step 5 — Dark Triad elevation flag (LLM, post-finalize)

Inspect the three Dark Triad subscale scores (`narcissism`, `machiavellianism`, `psychopathy`).
If ANY subscale score ≥ 4, set `dark_triad_elevated: true` and name the elevated trait(s).
Write a one-sentence clinical flag. If no subscale ≥ 4, write `dark_triad_elevated: false` with
a one-line summary of the subclinical profile.

### Step 6 — Normalization note

The rubric uses `normalization: z_score`. z-score normalization requires ≥ 3 characters in the
cohort. If fewer than 3 characters have a finalized scorecard for this rubric, suppress
normalization and append `[z-score suppressed: cohort < 3, raw scores shown]` to the scorecard
header.

### Step 7 — Emit EVL.scored

After a successful write, emit `EVL.scored` (see `orc:event-log`) so CRE may pick up the
psychometric scorecard as a content angle.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_standardize.py gather` | Validate rubric + emit per-criterion evidence bundle |
| `scripts/run_standardize.py finalize` | Aggregate judge scores + write the scorecard |

## Safety

- Writes ONLY under `docs/profiles/{char}/eval/` (fs_guard EVL zone) + reads profiles/rubrics.
- Never invents a score: uncited ⇒ UNVERIFIED; garbage judge reply ⇒ ERROR (both loud, counted).
- No network in the script path; real judging uses the Agent tool.
- No hardcoded character names — resolved via `paths.resolve_character`.
- Attachment quadrant and Dark Triad flag are LLM-narrated from verified scores, never from
  unverified criteria.

## Events

- **Emits:** `EVL.scored` (after a scorecard is written).
- **Consumes (via rescore):** `PSY.refresh`, `GRO.assessed` → re-score when the profile changes.

## Examples

```bash
/evl:standardize --character character-a
/evl:standardize --character character-b --rubric psychometric-big-five --json
/evl:standardize --character character-a --rescore
```

## See Also

- `evl:score` — generic engine this preset wraps
- `evl:fit` — role decision · `evl:compatibility` — dyad
- `evl:compare` — cross-character ranking · `evl:track` — score over time
- `docs/rules/17-evl-framework.md` — EVL domain rules
- `docs/rubrics/psychometric-big-five.yaml` — the default rubric for this skill
