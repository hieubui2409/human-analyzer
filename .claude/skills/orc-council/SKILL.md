---
name: orc:council
description: "4-voice decision framework for ambiguous situations. Anti-anchoring: each subagent receives ONLY the question + role, no prior context. Voices: Advocate, Skeptic, Pragmatist, Wildcard. Verdict stored in .claude/decisions/. Triggers: 'council', 'council vote', '4 voices', 'decision framework', 'ambiguous decision'."
argument-hint: "--question <text> --category <psy|cre|gro|cross> [--character <name>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "decision"
  position: "during-work"
  dependencies: [orc-decisions]
---

# Council — 4-Voice Decision Framework

Resolve ambiguous decisions using 4 independent voices. Anti-anchoring: each subagent receives ONLY the question text + their role prompt. No prior context, no file paths, no other voices' output. Verdict stored in `.claude/decisions/`.

**Isolation model:** Subagents share no memory (Agent tool guarantee). Main agent carries session context but does NOT inject it into voice prompts. This is input-level isolation, not session-level isolation (acknowledged limitation).

## Default (No Arguments)

Show usage help.

## Flags

| Flag                                | Purpose                             |
| ----------------------------------- | ----------------------------------- |
| `--question "<text>"`               | Decision question (max 500 chars)   |
| `--category <psy\|cre\|gro\|cross>` | Domain category                     |
| `--character <name>`                | Character name or "cross" (default) |

## Voice Roles

| Voice      | Role                    | Prompt Framing                                                                                                                       |
| ---------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Advocate   | Argues FOR the proposal | "You are an advocate. Argue strongly FOR this position. Find the best evidence and reasoning to support it."                         |
| Skeptic    | Argues AGAINST          | "You are a skeptic. Argue strongly AGAINST this position. Find weaknesses, risks, and counterarguments."                             |
| Pragmatist | Most practical path     | "You are a pragmatist. Ignore theory — what's the most practical, implementable approach? Consider effort, risk, and reversibility." |
| Wildcard   | Unconventional angle    | "You are a wildcard. What angle is everyone missing? Challenge the framing of the question itself if needed."                        |

## Trigger Conditions

| Framework | When to Suggest Council                                         |
| --------- | --------------------------------------------------------------- |
| PSY       | Conflicting clinical interpretations, formulation disagreements |
| CRE       | Ambiguous content direction, voice/tone disputes                |
| GRO       | Career trajectory disputes, competency assessment disagreements |
| Cross     | Cross-character relationship framing, cross-domain conflicts    |

## Workflow

### Step 1: Prepare

Run the script to validate question, generate output path, and check for duplicate decisions:

```bash
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/orc-council/scripts/run-council-vote.py \
  prepare --question "<text>" --category <cat> --character <name>
```

Output: JSON with `question`, `output_path`, `slug`, `category`, `similar_decisions`.

**If `similar_decisions` is non-empty:** warn user that similar decisions exist. Ask via `AskUserQuestion` whether to proceed or review existing decisions first.

### Step 2: Spawn 4 Voices (Parallel)

Spawn 4 subagents in parallel via Agent tool. Each receives ONLY:

- The question text (from Step 1 output)
- Their role prompt (see Voice Roles table)

**MUST NOT include:** file paths, prior context, session history, other voices' output.

**Model:** inherit from parent (no override).

**Prompt template per voice:**

```
You are a {role}. {role_prompt}

Question: "{question}"

Provide your analysis in 200-400 words. Be specific and substantive.
End with a clear position statement.
```

### Step 3: Synthesize Verdict

After collecting all 4 responses, the main agent (NOT a script) synthesizes:

- Where voices agree and disagree
- Strongest arguments from each side
- Recommended action with confidence level
- Conditions under which the decision should be revisited

### Step 4: Format and Store

Write JSON to a temp file with all fields:

```json
{
  "question": "...",
  "category": "...",
  "character": "...",
  "advocate": "...",
  "skeptic": "...",
  "pragmatist": "...",
  "wildcard": "...",
  "synthesis": "..."
}
```

Then run tally to format and write the verdict:

```bash
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/orc-council/scripts/run-council-vote.py \
  tally --input /tmp/council-vote-XXXX.json
```

Output: verdict written to `.claude/decisions/{date}-council-{slug}.md`

### Step 5: Report

Print verdict summary with:

- File path to stored verdict
- One-line synthesis
- Recommended action

## Verdict Record Format

```markdown
---
date: { YYYY-MM-DD }
category: council
character: { character or "cross" }
status: active
title: "Council: {short title}"
domain: { psy|cre|gro|cross }
voices: [advocate, skeptic, pragmatist, wildcard]
---

# Council Verdict: {question}

## Advocate

{advocate response}

## Skeptic

{skeptic response}

## Pragmatist

{pragmatist response}

## Wildcard

{wildcard response}

## Synthesized Verdict

{LLM synthesis — written by main agent, not script}
```

## Scripts

| Script                        | Purpose                                                      |
| ----------------------------- | ------------------------------------------------------------ |
| `scripts/run-council-vote.py` | Prepare: validate + generate path. Tally: format verdict doc |

## Safety

- Anti-anchoring: voice prompts contain ONLY question text + role
- Script does formatting only — no stance counting, no heuristic analysis (GOLDEN RULE compliant)
- Synthesis written by main agent (LLM), not by script
- Verdicts are append-only — same slug gets numeric suffix, never overwritten
- Council is manual trigger only (never auto-triggered), keeping token cost controlled

## Examples

```bash
# PSY formulation question
/orc:council --question "Should Nhân vật B's formulation emphasize avoidance or anxious attachment?" --category psy --character character-b

# CRE content direction
/orc:council --question "Should Nhân vật A's LinkedIn tone shift toward technical leadership or mentoring?" --category cre --character character-a

# Cross-character relationship
/orc:council --question "Is the kết nghĩa dynamic more mentor-protégé or sibling-peer?" --category cross
```

## See Also

- `/orc:decisions` — decision storage and retrieval
- `/orc:santa` — complementary dual-reviewer quality gate for high-risk changes
- `/orc:classify` — suggests Council for ambiguous high_risk decisions
