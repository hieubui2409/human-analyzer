---
name: evl:score
description: "EVL generic rubric scoring engine — score a character against any versioned rubric (psychometric/decision/clinical/dyad) producing an evidence-cited scorecard + verdict. Scripts gather evidence + aggregate; the LLM judges each criterion and cites a MAT tier. Triggers: 'evl score', 'score character against rubric', 'run rubric', 'evaluate character'."
argument-hint: "score <character> against <rubric> [--rubric <id>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "scoring-engine"
  dependencies: []
---

# evl:score — Generic Rubric Scoring Engine (EVL Framework)

Score a character against a versioned, evidence-cited rubric. This is the engine the other
EVL skills specialize; it handles all four rubric `kind`s (psychometric / decision / clinical /
dyad) by reading the rubric's own config — there is no per-kind forked logic.

**Design law:** the script gathers candidate evidence + does the weighted aggregation; the
**LLM judges each criterion** and must cite a MAT evidence tier (T1–T5). An uncited criterion is
`[UNVERIFIED]` — excluded from the score, counted, never a silent pass.

## Default (No Arguments)

Ask for the character + rubric id, then run the workflow below.

## Flags

| Flag | Purpose |
|------|---------|
| `--character <name>` | Character to score (resolved dynamically via `paths.py`) |
| `--rubric <id>` | Rubric id or path under `docs/rubrics/` |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Re-run ignoring any cached scorecard (clinical rubrics force this) |

## Workflow (LLM-executed)

### Step 1 — Validate + gather (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-score/scripts/run_score.py gather --character <name> --rubric <id>
```

`run_score.py gather` calls `evl_schema.load_and_validate` (rejects a malformed rubric loudly)
then `evl_evidence.gather_for_rubric` — emitting a per-criterion evidence bundle (candidate
snippets with `file:line` + best-effort tier). The script only SURFACES candidates.

### Step 2 — Judge each criterion (LLM, Agent tool, input-isolated)

For each criterion, spawn a judge **Agent** that sees ONLY that criterion + its evidence bundle
(never sibling verdicts — isolation prevents cross-contamination). The judge returns a
`CriterionScore`: `{criterion_id, score, citation, tier, justification, verdict}`. It MUST cite
one evidence item by source + tier or return `verdict: UNVERIFIED`. The judge prompt contract is
`platform_lib/evl_judge.py:JUDGE_SYSTEM`.

### Step 3 — Multi-judge convergence for high-stakes (script math)

If the rubric is `high_stakes` (`min_judges >= 2`, e.g. clinical/role-fit), spawn N independent
judges per criterion, then collapse with the deterministic math:

```python
from platform_lib.evl_convergence import converge, required_judges
converge(criterion_verdicts, scale=rubric["scale"])   # converged consensus OR DIVERGED
```

`DIVERGED` ⇒ `manual_review_required` — the engine never auto-picks a winner.

### Step 4 — Finalize (deterministic, script)

Write the collected scores to a JSON file, then:

```bash
$PY .claude/skills/evl-score/scripts/run_score.py finalize \
    --character <name> --rubric <id> --scores scores.json --asof <YYYY-MM-DD>
```

`finalize` runs `evl_aggregate.aggregate` (weighted roll-up, excludes uncited) and
`evl_scorecard.write_scorecard` → `docs/profiles/{char}/eval/{rubric-id}.md` + `.json`.

### Step 5 — Emit EVL.scored

After a successful write, emit `EVL.scored` (see `orc:event-log`) so CRE may pick up the
scorecard as a content angle. Clinical (`cache: never`) scorecards are stamped
`reassess_required` and must not be reused as a standing verdict.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_score.py gather` | Validate rubric + emit per-criterion evidence bundle |
| `scripts/run_score.py finalize` | Aggregate judge scores + write the scorecard |

## Safety

- Writes ONLY under `docs/profiles/{char}/eval/` (fs_guard EVL zone) + reads profiles/rubrics.
- Never invents a score: uncited ⇒ UNVERIFIED; garbage judge reply ⇒ ERROR (both loud, counted).
- No network in the script path; real judging uses the Agent tool (human-reviewed for high-stakes).
- No hardcoded character names — resolved via `paths.resolve_character`.

## Events

- **Emits:** `EVL.scored` (after a scorecard is written).
- **Consumes (via rescore):** `PSY.refresh`, `GRO.assessed` → re-score when the profile changes.

## Examples

```bash
/evl:score --character character-a --rubric psychometric-big-five
/evl:score --character character-b --rubric clinical-risk-safety --rescore
/evl:score --character character-a --rubric role-casting-fit --json
```

## Schema Validation (C7)

Rubrics are validated by `platform_lib/evl_schema.py` against `.claude/schemas/evl-rubric.schema.json`
(the single shared Draft-7 engine, `schema_validator.validate_instance`) plus loader invariants
(weight sums, high-stakes judge floor, clinical rails, threshold coverage, anchor endpoints).

## See Also

- `evl:standardize` — psychometric battery preset · `evl:fit` — role decision · `evl:compatibility` — dyad
- `evl:compare` — cross-character ranking · `evl:track` — score over time · `evl:validate` — rubric structural check
- `evl:rubric-import` — external framework → canonical rubric
- `docs/rules/17-evl-framework.md` — EVL domain rules
