---
name: "evl:fit"
description: "EVL role / casting-fit decision engine — score a character against the role-casting-fit rubric (or any decision rubric) and produce an evidence-cited CAST / CONDITIONAL / NO verdict. Spawns min_judges input-isolated judge agents per criterion; converges via evl_convergence; a RED safety-clearance flag hard-blocks casting regardless of overall score. Triggers: 'evl fit', 'casting fit', 'role fit', 'can character play role', 'cast decision'."
argument-hint: "fit <character> [--rubric <id>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "role-decision"
  dependencies: []
---

# evl:fit — Role / Casting-Fit Decision Engine (EVL Framework)

Preset specialization of `evl:score` for **role and casting decisions**. The rubric defaults to
`role-casting-fit` — a `kind: decision`, `high_stakes: true`, `min_judges: 2` rubric — but
`--rubric` accepts any decision rubric whose `target_profile` field points to an alternate role spec.

**Design law:** the script gathers candidate evidence + does the weighted aggregation; the
**LLM judges each criterion** and must cite a MAT evidence tier (T1–T5). An uncited criterion is
`[UNVERIFIED]` — excluded from the score, counted, never a silent pass.

## Verdict Bands

The `role-casting-fit` rubric maps weighted-mean scores (0–5 scale) to three contiguous bands:

| Band | Score range | Meaning |
|------|-------------|---------|
| **CAST** | ≥ 4.0 | Strong fit — character is ready for the role |
| **CONDITIONAL** | 3.0 – < 4.0 | Partial fit — casting possible with named conditions |
| **NO** | < 3.0 | Insufficient fit — role not suitable at this time |

These bands are determined by `evl_aggregate` from the rubric's `verdict_thresholds` — the LLM does
not pick the band; it judges criteria scores that feed the deterministic roll-up.

## Safety Veto (CRITICAL)

The rubric's `red_flags` list names criteria whose **RED score is a hard block**. For
`role-casting-fit` the gating criterion is `safety-clearance`.

- A score of 0 on `safety-clearance` means one or more severe risk flags are present
  (violence, untreated illness, active substance use, ethical violations, high psychopathy or
  Machiavellianism in a trust role).
- The overall weighted-mean score **does not matter** in this case: even a CAST-range aggregate is
  overridden to **NO** when `safety-clearance` is in `red_flags` and the judge returns a RED score.
- **This veto is enforced by the LLM** reading the rubric's `red_flags` field — not by the
  aggregation math. The LLM must surface the veto explicitly in the verdict rationale.

## Default (No Arguments)

Ask for the character + optionally a custom rubric id, then run the workflow below.

## Flags

| Flag | Purpose |
|------|---------|
| `--character <name>` | Character to score (resolved dynamically via `paths.py`) |
| `--rubric <id>` | Decision rubric id; defaults to `role-casting-fit` |
| `--json` | Machine-readable scorecard summary |
| `--rescore` | Re-run ignoring any cached scorecard |

## Workflow (LLM-executed)

### Step 1 — Validate + gather (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-fit/scripts/run_fit.py gather --character <name> [--rubric <id>]
```

`run_fit.py gather` calls `evl_schema.load_and_validate` then `evl_evidence.gather_for_rubric`,
emitting a per-criterion evidence bundle (candidate snippets with `file:line` + best-effort tier).
The script only SURFACES candidates; the LLM judges from them.

Check the bundle for the `target_profile` field — it identifies the role spec this scoring round
is anchored to. Swap the rubric (via `--rubric`) to score against a different role.

### Step 2 — Spawn input-isolated judge agents (LLM, Agent tool)

Because `high_stakes: true` and `min_judges: 2`, spawn **exactly `required_judges(rubric)`**
independent judges per criterion. Each judge sees ONLY:

- The criterion definition (id, text, anchors, weight, min_tier)
- Its evidence bundle (candidate snippets with file:line, tier)
- The rubric's `target_profile` reference (role context only — not sibling verdicts)

No judge sees another judge's verdict or score. Each returns a `CriterionScore`:
`{criterion_id, score, citation, tier, justification, verdict}`.

The judge prompt contract is `platform_lib/evl_judge.py:JUDGE_SYSTEM`. The judge MUST cite one
evidence item by source + tier or return `verdict: UNVERIFIED`.

**Safety veto check:** after collecting all judge scores, the LLM must inspect
`safety-clearance` scores before proceeding to convergence. If any judge returns a RED
(score = 0) on `safety-clearance`, the LLM must surface a veto note and set the final
scorecard verdict to NO regardless of aggregate.

### Step 3 — Multi-judge convergence (script math)

Collapse the per-criterion judge sets with the deterministic math:

```python
from platform_lib.evl_convergence import converge, required_judges
converge(criterion_verdicts, scale=rubric["scale"])   # converged consensus OR DIVERGED
```

`DIVERGED` ⇒ `manual_review_required` — the engine never auto-picks a winner. Flag for human
review before proceeding to finalize.

### Step 4 — Finalize (deterministic, script)

```bash
$PY .claude/skills/evl-fit/scripts/run_fit.py finalize \
    --character <name> [--rubric <id>] --scores scores.json --asof <YYYY-MM-DD>
```

`finalize` runs `evl_aggregate.aggregate` (weighted roll-up, excludes uncited) and
`evl_scorecard.write_scorecard` → `docs/profiles/{char}/eval/{rubric-id}.md` + `.json`.
`updated_by` is set to `"evl:fit"` for provenance tracking.

### Step 5 — Emit EVL.scored

After a successful write, emit `EVL.scored` (see `orc:event-log`) so CRE may pick up the
scorecard as a content angle. Decision scorecards are `cache: allow` — they may be reused
until the profile changes substantially; then re-run with `--rescore`.

## target_profile and Rubric Swapping

The `target_profile` field in the rubric names the role spec the criteria are anchored to (e.g.
a trauma-informed therapist reference under `docs/references/role-profiles/`). To score fit for
a different role, provide a custom rubric that points `target_profile` at the alternate spec
and pass it via `--rubric`. The engine and script are role-agnostic.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_fit.py gather` | Validate rubric + emit per-criterion evidence bundle |
| `scripts/run_fit.py finalize` | Aggregate judge scores + write the scorecard |

## Safety

- Writes ONLY under `docs/profiles/{char}/eval/` (fs_guard EVL zone) + reads profiles/rubrics.
- Never invents a score: uncited ⇒ UNVERIFIED; garbage judge reply ⇒ ERROR (both loud, counted).
- No network in the script path; real judging uses the Agent tool with human review for high-stakes.
- No hardcoded character names — resolved via `paths.resolve_character`.

## Events

- **Emits:** `EVL.scored` (after a scorecard is written).
- **Consumes (via rescore):** `PSY.refresh`, `GRO.assessed` → re-score when the profile changes.

## Examples

```bash
/evl:fit --character character-a
/evl:fit --character character-b --json
/evl:fit --character character-a --rubric custom-role-spec --rescore
```

## See Also

- `evl:score` — generic engine this skill wraps
- `evl:standardize` — psychometric battery preset · `evl:compatibility` — dyad
- `evl:compare` — cross-character ranking · `evl:track` — score over time
- `docs/rules/17-evl-framework.md` — EVL domain rules
