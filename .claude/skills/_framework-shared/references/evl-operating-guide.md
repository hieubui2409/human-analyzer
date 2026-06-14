# EVL Operating Guide

Load only the row relevant to the active task — except `gates-and-anti-rationalization.md`, loaded every turn.

| Skill ID | Primary Trigger | When to Use | GUIDE-EN.md |
|----------|-----------------|-------------|------------|
| `evl:score` | score character against rubric | Generic rubric scoring engine — gather evidence, LLM judges each criterion with a MAT-tier citation, aggregate to an evidence-cited scorecard + verdict | ../../evl-score/GUIDE-EN.md |
| `evl:standardize` | psychometric battery | Score the Big Five + Dark Triad (SD3) + Attachment (ECR-R) battery; LLM narrates the attachment quadrant + Dark-Triad elevation flag (preset over evl:score) | ../../evl-standardize/GUIDE-EN.md |
| `evl:fit` | casting fit / role fit | Role / casting-fit decision against a target profile — CAST / CONDITIONAL / NO with a RED safety-flag veto; high-stakes ⇒ ≥2 input-isolated judges + convergence | ../../evl-fit/GUIDE-EN.md |
| `evl:compatibility` | compatibility between | Dyad compatibility for a pair — Gottman Four Horsemen + repair + 5:1 ratio + attachment pairing; evidence pooled from both characters | ../../evl-compatibility/GUIDE-EN.md |
| `evl:compare` | rank characters on rubric | Cross-character ranking on one rubric from already-written scorecards (raw + z-score + percentile); missing scorecards surfaced, never dropped | ../../evl-compare/GUIDE-EN.md |
| `evl:track` | track score over time | Diff a character's current scorecard vs the latest snapshot + list profile-change events in the window for the LLM to narrate the delta | ../../evl-track/GUIDE-EN.md |
| `evl:validate` | validate rubric / check scorecard | Deterministic structural checker — rubric shape + invariants, or a finished scorecard against its rubric (blocks malformed/tampered artifacts) | ../../evl-validate/GUIDE-EN.md |
| `evl:rubric-import` | import rubric | Ingest an external evaluation framework (file/text/URL) → canonical rubric draft under docs/rubrics/imported/; semantic mapping via the evl-rubric-importer sub-agent | ../../evl-rubric-import/GUIDE-EN.md |

## Design law (applies to every EVL skill)

- **Scripts gather + aggregate; the LLM judges.** Per-criterion scoring is never done by a script.
- **Every score cites a MAT evidence tier (T1–T5).** Uncited ⇒ `[UNVERIFIED]` — excluded, counted, never a silent pass.
- **High-stakes rubrics (clinical, role-fit) run ≥2 input-isolated judges → convergence.** `DIVERGED` ⇒ manual review.
- **EVL writes only under `docs/profiles/{char}/eval/` + authors rubrics under `docs/rubrics/`** (Rule 12 boundary).
- **EVL emits `EVL.scored` (forward to CRE); it never consumes CRE.** Clinical rubrics are `cache: never`.
