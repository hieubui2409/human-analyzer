---
name: "evl:compatibility"
description: "EVL dyad rubric scoring skill — score a PAIR of characters on a dyad rubric (default: relationship-compatibility; Gottman Four Horsemen + repair + 5:1 ratio + ECR-R attachment pairing + similarity/complementarity) producing an evidence-cited scorecard + compatibility verdict. Scripts gather evidence pooled from BOTH characters; the LLM judges each criterion. Triggers: 'evl compatibility', 'score compatibility', 'rate compatibility between', 'how compatible are', 'compatibility between characters'."
argument-hint: "score compatibility between <character-a> and <character-b> [--rubric <id>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "evl-framework"
  position: "dyad"
  dependencies: []
---

# evl:compatibility — Dyad Rubric Scoring (EVL Framework)

Score a pair of characters against a versioned, evidence-cited dyad rubric. This skill wraps
the EVL engine with a dyad preset — the default rubric (`relationship-compatibility`) implements
Gottman's Four Horsemen + repair + 5:1 ratio + ECR-R attachment pairing + similarity/
complementarity.

**Design law:** the script pools candidate evidence from BOTH characters and passes it to the
engine; the **LLM judges each criterion** and must cite a MAT evidence tier (T1–T5). An uncited
criterion is `[UNVERIFIED]` — excluded from the score, counted, never a silent pass.

## Default (No Arguments)

Ask for both characters + rubric id, then run the workflow below.

## Flags

| Flag | Purpose |
|------|---------|
| `--character-a <name>` | First character in the pair (resolved via `paths.py`) |
| `--character-b <name>` | Second character in the pair (resolved via `paths.py`) |
| `--rubric <id>` | Dyad rubric id or path under `docs/rubrics/` (default: `relationship-compatibility`) |
| `--scores <json>` | Path to judge scores JSON (finalize only) |
| `--asof <YYYY-MM-DD>` | ISO date stamped on the scorecard (finalize only) |

## Workflow (LLM-executed)

### Step 1 — Validate + gather (deterministic, script)

```bash
PY=.claude/skills/.venv/bin/python3
$PY .claude/skills/evl-compatibility/scripts/run_compatibility.py gather \
    --character-a <name-a> --character-b <name-b> [--rubric <id>]
```

`gather` calls `evl_pipeline.gather_dyad_payload((char_a, char_b), rubric_path)` — validates the
rubric (must be `subject: dyad`) then calls `evl_evidence.gather_for_dyad` which independently
caps candidates from each character before merging, so neither side can crowd the other out of the
evidence bundle. Emits a per-criterion evidence bundle with `file:line` source + best-effort tier.

### Step 2 — Judge each criterion (LLM, Agent tool, input-isolated)

For each criterion, spawn a judge **Agent** that sees ONLY that criterion + its pooled evidence
bundle (never sibling verdicts — isolation prevents cross-contamination). Evidence snippets carry a
`character` field so the judge can attribute each signal to the right party. The judge returns a
`CriterionScore`: `{criterion_id, score, citation, tier, justification, verdict}`. It MUST cite one
evidence item by source + tier or return `verdict: UNVERIFIED`. The judge prompt contract is
`platform_lib/evl_judge.py:JUDGE_SYSTEM`.

### Step 3 — Finalize (deterministic, script)

Write collected scores to a JSON file, then:

```bash
$PY .claude/skills/evl-compatibility/scripts/run_compatibility.py finalize \
    --character-a <name-a> --character-b <name-b> [--rubric <id>] \
    --scores scores.json --asof <YYYY-MM-DD>
```

`finalize` calls `evl_pipeline.finalize_dyad_scorecard((char_a, char_b), rubric_path, scores,
asof=..., updated_by="evl:compatibility")`. The scorecard is written under the **first character's**
`eval/` directory with the partner slug suffixed in the filename (e.g.
`docs/profiles/{char-a}/eval/relationship-compatibility--{char-b}.{md,json}`), so one character can
hold many dyad scorecards without collision.

### Step 4 — Emit EVL.scored

After a successful write, emit `EVL.scored` (see `orc:event-log`) so CRE may pick up the
compatibility scorecard as a content angle (relational narrative, contrast post, etc.).

## Verdict Bands (relationship-compatibility)

| Band | Score range | Interpretation |
|------|-------------|----------------|
| **Incompatible** | < 2.0 | Pervasive Four Horsemen / very-low-stability attachment; high breakup risk |
| **At-Risk** | 2.0 – 3.0 | Declining ratio / inconsistent repair; active intervention needed |
| **Compatible** | 3.0 – 4.0 | Functional conflict patterns; workable with conscious effort |
| **Highly-Compatible** | ≥ 4.0 | Secure base; consistent repair; 5:1 or better; optimal pairing |

## Criteria (default rubric)

| Criterion | Weight | Evidence source |
|-----------|--------|-----------------|
| `horsemen-absence` | 0.25 | `relationships/*.md` |
| `repair-attempts` | 0.20 | `relationships/*.md` |
| `positivity-ratio` | 0.20 | `relationships/*.md` |
| `attachment-pairing` | 0.20 | `psychology/attachment-style.md`, `relationships/*.md` |
| `similarity-complementarity` | 0.15 | `relationships/*.md`, `identity/*.md` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_compatibility.py gather` | Validate rubric + emit pooled per-criterion evidence bundle |
| `scripts/run_compatibility.py finalize` | Aggregate judge scores + write the dyad scorecard |

## Safety

- Writes ONLY under `docs/profiles/{char-a}/eval/` (fs_guard EVL zone) + reads profiles/rubrics.
- Never invents a score: uncited ⇒ UNVERIFIED; garbage judge reply ⇒ ERROR (both loud, counted).
- Rubric must carry `subject: dyad` — any other kind raises immediately.
- No hardcoded character names — both are resolved via `paths.resolve_character`.

## Events

- **Emits:** `EVL.scored` (after a dyad scorecard is written).
- **Consumes (via re-score):** `PSY.refresh` (attachment style updated) → re-score when the profile changes.

## Examples

```bash
/evl:compatibility --character-a character-a --character-b character-b
/evl:compatibility --character-a character-a --character-b character-b --rubric relationship-compatibility
```

## See Also

- `evl:score` — generic single-subject engine · `evl:standardize` — psychometric battery preset · `evl:fit` — role decision
- `evl:compare` — cross-character ranking · `evl:track` — score over time · `evl:validate` — rubric structural check
- `docs/rubrics/relationship-compatibility.yaml` — the default dyad rubric (Gottman + ECR-R)
- `docs/rules/17-evl-framework.md` — EVL domain rules
