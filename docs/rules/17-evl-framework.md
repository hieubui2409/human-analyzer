---
title: EVL Framework — Rubric Scoring & Evidence-Cited Verdicts
version: "1.0"
created: "2026-06-14"
---

# Rule 17: EVL Framework — Rubric Scoring & Evidence-Cited Verdicts

## Overview

EVL (Evaluation) is a generic, versioned, evidence-cited **rubric scoring engine**. It consumes a character's existing profile (MAT materials + PSY clinical profile + GRO growth — **never CRE**) and scores the character against pluggable rubrics, emitting a standardized scorecard + verdict. Two layers ride the same engine: decision/fit rubrics (casting, role-fit, suitability) and standardized psychometric/clinical batteries (Big Five, Dark Triad, attachment, DSM-5/ICD-11 severity).

**Design law (non-negotiable):** scripts do deterministic gathering + weighted aggregation only; the LLM does per-criterion judgment. Every criterion score MUST cite a MAT evidence tier (T1–T5); an uncited score is `[UNVERIFIED]` — excluded from the roll-up, counted, never a silent pass.

## Domain Boundaries

| Domain | Writes to                                          | Reads from                                                                     |
| ------ | ------------------------------------------------- | ------------------------------------------------------------------------------ |
| EVL    | `docs/profiles/{char}/eval/`, `docs/rubrics/`     | `docs/profiles/` (identity/, psychology/, growth/, relationships/ — read-only), `docs/materials/` |

**Hard rule**: EVL never writes to psychology/, identity/, growth/, relationships/, or any non-eval profile directory. It reads them, cites them, and writes only its own scorecards + the shared rubric library. CRE is never an input.

## Rubric Library (`docs/rubrics/`)

Rubrics are shared, versioned, character-agnostic files validated by `.claude/schemas/evl-rubric.schema.json` (the single shared Draft-7 engine) plus loader invariants. Four reference rubrics ship as exemplars:

| Rubric                          | Kind          | Notable config                                                       |
| ------------------------------- | ------------- | ------------------------------------------------------------------- |
| `psychometric-big-five.yaml`    | psychometric  | Big Five + Dark Triad (SD3) + Attachment (ECR-R); z-score normalize |
| `role-casting-fit.yaml`         | decision      | `target_profile` + `red_flags`; CAST / CONDITIONAL / NO verdict     |
| `clinical-risk-safety.yaml`     | clinical      | high-stakes, `min_judges: 2`, tri-state verdict, `cache: never`     |
| `relationship-compatibility.yaml` | dyad        | `subject: dyad`; Gottman + attachment pairing                       |

External frameworks are converted to canonical drafts under `docs/rubrics/imported/` by `evl:rubric-import` (human-reviewed before use).

## Result Files (`docs/profiles/{char}/eval/`)

Each scoring run writes `{rubric-id}.md` (human) + `{rubric-id}.json` (machine source of truth); prior runs snapshot to `eval/history/`. JSON is authoritative; markdown is derived.

### Scorecard frontmatter

```yaml
---
character: { char-slug }
domain: eval
type: data
rubric: { rubric-id }
rubric_version: "X.Y.Z"
verdict: { scalar|band-label }
overall: { number }
coverage: { 0-100 }
confidence: high|medium|low
cache: allow|never
last_updated: "YYYY-MM-DD"
updated_by: evl:{skill}
---
```

## EVL ↔ Other Domain Boundary

| EVL owns (evaluation)                         | Other domains own                                  |
| --------------------------------------------- | -------------------------------------------------- |
| Rubric definitions + versions                 | The profile facts EVL scores (MAT/PSY/GRO)         |
| Per-criterion scores + tier citations         | The source evidence those citations point at (MAT) |
| Aggregated verdicts + cross-character ranking | Content angles derived from a verdict (CRE)        |

Cross-reference is encouraged; cross-write is forbidden. EVL emits `EVL.scored`; CRE may subscribe.

## Evidence Requirements

Every criterion score must cite a MAT evidence tier (T1–T5):

| Evidence Tier | EVL Usage                                                  |
| ------------- | --------------------------------------------------------- |
| T1 (Primary)  | Direct first-person material grounding the score          |
| T2 (Secondary)| Corroborated assessment / clinical observation            |
| T3 (Tertiary) | Single-source or social-signal grounding                  |
| T4 (Contextual)| Third-party / reported grounding                         |
| T5 (Auxiliary)| Inference/metadata only — typically below a rubric's floor |

A criterion citing a tier weaker than its `min_tier` is excluded (`below_min_tier`); an uncited criterion is `[UNVERIFIED]`. Both are loud and counted — never a silent pass.

## EVL Events

| Event         | Trigger                              | Downstream                                                  |
| ------------- | ------------------------------------ | ---------------------------------------------------------- |
| `EVL.scored`  | A scorecard was written              | → `CRE.recalibrate` (a verdict is a new content angle)     |
| `EVL.rescore` | A profile changed; re-score is due   | → `evl:score --rescore` → `EVL.scored`                     |

`PSY.refresh` and `GRO.assessed` both emit `EVL.rescore`. A `docs/profiles/*/eval/` change classifies to `EVL.scored` (announcing a scorecard), never a rescore — keeping the cascade acyclic.

## EVL → Other Domain Cascades

```
PSY.refresh ──→ EVL.rescore ──→ EVL.scored ──→ CRE.recalibrate
GRO.assessed ─→ EVL.rescore ──→ EVL.scored ──→ CRE.recalibrate
EVL is a forward-only sink: it feeds CRE and never back-edges to PSY/GRO.
```

## Honesty Contract (the rigor rails)

- **Uncited ⇒ UNVERIFIED**, excluded + counted; coverage% headlines every scorecard.
- **High-stakes rubrics (clinical, role-fit) run ≥2 input-isolated judges → convergence.** A disagreement is `DIVERGED` + `manual_review_required`, never auto-averaged.
- **Clinical rubrics are `cache: never`** and stamped `reassess_required` — a stale risk verdict is never reused.
- **A malformed rubric or tampered scorecard fails `evl:validate`** and cannot be scored / trusted.

## Skills

| Skill              | Purpose                                                      |
| ------------------ | ----------------------------------------------------------- |
| evl:score          | Generic rubric scoring engine (all four kinds)              |
| evl:standardize    | Psychometric battery preset (Big Five + Dark Triad + attachment) |
| evl:fit            | Role / casting-fit decision (CAST / CONDITIONAL / NO + veto) |
| evl:compatibility  | Dyad compatibility scoring                                  |
| evl:compare        | Cross-character ranking on one rubric                       |
| evl:track          | Score-over-time diff + event attribution                   |
| evl:validate       | Rubric + scorecard structural checker                      |
| evl:rubric-import  | External framework → canonical rubric draft                |

## See Also

- `docs/rules/12-orc-orchestration.md` — event system and domain boundaries
- `docs/rules/14-cre-evidence-and-events.md` — EVL.scored → CRE recalibrate trigger
- `docs/rules/15-gro-framework.md` — sibling framework (GRO assessment feeds EVL.rescore)
- `docs/rules/01-profile-structure.md` — universal profile schema
- `.claude/skills/_framework-shared/references/evl-operating-guide.md` — skill→trigger→GUIDE routing
