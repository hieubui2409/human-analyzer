---
name: cre:angle-discovery
description: "Discover publishable content angles by proactively mining all 6 frameworks — PSY growth-edges (emotional), MAT new materials (story), GRO milestones (professional), CRE/ORC event history (distribution/timing), plus psy:relation-intelligence (relationship). Aggregates raw signals, ranks by freshness × evidence × platform-fit, tags each {source_framework, evidence_tier, primary_character, freshness, consent_status}, and emits a CONTEXT.md block for cre:post-writer. READ-ONLY, autonomous (cron/event-runnable). Use when deciding what to post next or seeding cre:exploring/post-writer. Triggers: 'angle discovery', 'find content angles', 'what should we post', 'mine angles', 'proactive ideation', 'content opportunities'."
argument-hint: "--character <slug> [--framework psy|mat|gro|cre|orc|all] [--since-days N] [--top N] [--graph-signal] [--to-context] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "cre-framework"
  position: "ideation"
  dependencies: []
---

# cre:angle-discovery — Proactive Multi-Framework Angle Mining

`cre:exploring` is **interactive** (asks the user one question at a time → CONTEXT.md).
This skill is **autonomous**: it mines signals already in the system — recent events,
profile deltas, milestones, relationship dynamics — and surfaces ranked, evidence-backed
content angles **without asking**. It can run on a cron/event trigger and feeds its top
angle straight into `cre:exploring` (to refine) or `cre:post-writer --from-context`
(to write) or `cre:multiplatform --source <angle>` (to generate N native variants).

## Determinism Split (GOLDEN RULE #4)

| Layer      | Owner                                          | Does                                                                                                                                                                                                                        |
| ---------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gather     | `aggregate-angle-signals-across-frameworks.py` | OVER-GATHER raw signals: B5 streams + PSY growth-edges + GRO milestones + MAT recent materials. Optional **`--graph-signal`** (default OFF) appends KG `latent_links` + `similar_files` semantic candidates. Deterministic. |
| Synthesize | **LLM**                                        | Read raw signals + (optionally) B9 relationship facts → write candidate angles (title, hook, framing), assign evidence_tier + platform_fit. Heuristic.                                                                      |
| Rank       | `rank-angles-by-freshness-and-evidence.py`     | Score = freshness × evidence × platform-fit × consent_factor; sort; flag speculative (T4/T5) + sink BLOCKED. Deterministic.                                                                                                 |

Scripts may over-gather (e.g. ORC session-lifecycle events) — false positives expected;
the LLM synthesis layer discards noise and keeps only signals that make a real angle.

## Usage

```bash
PY=$HOME/.claude/skills/.venv/bin/python3
SK=.claude/skills/cre-angle-discovery/scripts

# 1. gather raw signals (deterministic) — feed to the LLM
$PY $SK/aggregate-angle-signals-across-frameworks.py --character character-a --framework all --since-days 30 --json

# 2. LLM synthesizes candidate angles from the signals → angles.json
#    (each: title, hook, source_framework, primary_character, evidence_tier,
#     freshness carried from signal, platform_fit[], consent_status)
#    For the relationship slice, the LLM consults psy:relation-intelligence (B9).

# 3. rank the synthesized angles (deterministic)
$PY $SK/rank-angles-by-freshness-and-evidence.py --angles angles.json --top 5 --json
```

`--framework all` reads PSY/MAT/GRO/CRE/ORC. `--since-days` sets the freshness window
(signals older than the window decay to 0 and are dropped → no stale angles).

## Signal → Angle Lens

| Framework | Signal source (gathered)                             | Angle lens   |
| --------- | ---------------------------------------------------- | ------------ |
| PSY       | growth-edges sections, CURRENT-STATE deltas, events  | emotional    |
| MAT       | newly-touched materials, coverage gaps               | story        |
| GRO       | milestones (ACHIEVED/IN_PROGRESS), competency deltas | professional |
| CRE       | content-events history (engagement, prior posts)     | distribution |
| ORC       | cascade/timing events                                | timing       |

## Ranking & Scoring

```
score = (0.45·freshness + 0.40·evidence_strength + 0.15·platform_fit) × consent_factor
```

- `evidence_strength`: T1=1.0 T2=0.85 T3=0.55 T4=0.25 T5=0.15; no-evidence=0.30.
- `consent_factor`: OK=1.0, REVIEW=0.5, BLOCKED=0.05 (carried from B9 / Rule-09 tags).
- BLOCKED angles **sink to the bottom but are never dropped** (transparency — B9 rule).
- T4/T5-only angles flagged `speculative` (publishable but weak evidence).

## Red-Team R-cross — No Raw Event Leakage

Angle text derives **timing** from events ("milestone season", "anniversary of X") —
it NEVER embeds raw ORC event payloads, internal cascade detail, or `[CONFIDENTIAL]`
material. The deterministic gather copies only the event `reason` into `summary`; the
LLM must paraphrase, not quote internal state. Each synthesized angle still passes
`cre:evidence-scanner` + `cre:privacy-guard` downstream before any variant is written.

## CONTEXT.md Compatibility

`--to-context` writes the top angle as a `cre:exploring`-format CONTEXT.md block
(Character / Type / Angle / Platform / Tone / Clinical frame + Locked Decisions +
Profile References) so `cre:post-writer --from-context` consumes it unchanged.

## Events

On completion emits **`CRE.angle-discovered`** → `content-events.jsonl`:

```bash
$PY .claude/skills/orc-event-log/scripts/append-event-to-log.py \
  --event-type CRE.angle-discovered --source cre:angle-discovery \
  --character <slug> --reason "top=<title> framework=<fw> score=<n>"
```

## Boundaries (C3 stocktake will verify)

- **vs `cre:exploring`** — exploring = interactive user Q&A (synchronous, user-driven);
  this = autonomous signal-mining (proactive, no user input). They compose: discovery → exploring.
- **vs `psy:relation-intelligence` (B9)** — B9 is a _specialized_ angle source (cross-character
  relationship only). This skill _aggregates_ B9 + 4 other framework sources and ranks globally.
  This skill calls B9 for the relationship slice; no duplication.

## See Also

- `cre:exploring` — interactive refinement of a discovered angle.
- `cre:post-writer` — `--from-context` consumes the CONTEXT.md block.
- `cre:multiplatform` (C1) — `--source <angle>` generates N native variants.
- `psy:relation-intelligence` (B9) — relationship-angle source.
- `cre:evidence-scanner` / `cre:privacy-guard` — downstream per-variant gates.
- Rule 14 (`cre-evidence-and-events`) — CRE events + evidence-tier permissions.
