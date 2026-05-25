---
name: orc:santa
description: "Dual-reviewer quality gate for high-risk changes. Two independent subagents review with input-level isolation (each sees only target + pre-check report, never the other's output). Both must pass → SHIP. Any fail → fix + re-review (max 2 rounds, then escalate). Triggers: 'santa review', 'dual review', 'quality gate', 'santa method'."
argument-hint: "--review <target> --framework <psy|cre|gro|mat> [--scope full|changes|ref] [--auto]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "quality"
  position: "post-work"
  dependencies: [orc-classify]
---

# Santa Method — Dual-Reviewer Quality Gate

Two independent reviewers examine content/profile changes. Input-level isolation: each reviewer receives ONLY target files + pre-check report, never the other's findings. Both pass → SHIP. Any fail → fix all issues → re-review with fresh agents. Max 2 rounds, then escalate to user.

**Isolation model:** Subagents share no memory (Agent tool guarantee). Main agent carries session context but does NOT inject it into reviewer prompts. Round 2 uses fresh agents with clean prompts — same pre-check report, no round 1 findings. This is input-level isolation, not session-level isolation.

## Default (No Arguments)

Show usage help.

## Flags

| Flag                               | Purpose                                            |
| ---------------------------------- | -------------------------------------------------- |
| `--review <target>`                | Target file or directory to review                 |
| `--framework <psy\|cre\|gro\|mat>` | Domain framework for reviewer pair selection       |
| `--scope <full\|changes\|ref>`     | Scope mode (default: `ref`)                        |
| `--auto`                           | Auto-triggered by orc:classify (skip user confirm) |

## Scope Modes

| Mode      | Description                            | Token Cost | Recommended For         |
| --------- | -------------------------------------- | ---------- | ----------------------- |
| `full`    | All files in target directory          | HIGH       | Initial profile review  |
| `changes` | Only git-changed files in target       | LOW        | cre:post-writer output  |
| `ref`     | Changed files + cross-referenced files | MEDIUM     | Default, most workflows |

## Workflow

### Step 1: Deterministic Pre-Checks

Run the script to gather file inventory, schema validation, word counts, date validation, and cross-references:

```bash
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/orc-santa/scripts/run-santa-review.py \
  --target <target> --framework <framework> --scope <scope> --round <1|2>
```

Output: JSON report with file list, schema status, word counts, cross-refs.

### Step 2: Spawn Reviewer A (Domain-Specific)

Spawn via Agent tool. Reviewer A prompt includes ONLY:

- The target file contents (read from pre-check file list)
- The pre-check JSON report
- Domain-specific review instructions (see Reviewer Prompts below)

**MUST NOT include:** Reviewer B's output, session history, or any other context.

### Step 3: Spawn Reviewer B (Consistency Checker)

Spawn via Agent tool IN PARALLEL with Reviewer A. Reviewer B prompt includes ONLY:

- The target file contents (same as Reviewer A)
- The pre-check JSON report
- Consistency-focused review instructions (see Reviewer Prompts below)

**MUST NOT include:** Reviewer A's output, session history, or any other context.

### Step 4: Collect Verdicts

Both reviewers return one of:

- **PASS** — no issues found
- **FAIL** — issues listed with severity and file:line references

### Step 5: Decision

| Reviewer A | Reviewer B | Action                            |
| ---------- | ---------- | --------------------------------- |
| PASS       | PASS       | Print "SHIP ✅" — review complete |
| FAIL       | any        | Merge all issues → fix cycle      |
| any        | FAIL       | Merge all issues → fix cycle      |

### Step 6: Fix Cycle (if any FAIL)

1. Merge unique issues from both reviewers into numbered list
2. Present fix list to user (or auto-apply if `--auto`)
3. Apply fixes to target files
4. Re-run pre-checks with `--round 2`
5. Spawn NEW Reviewer A' + B' (fresh agents, no round 1 context)

### Step 7: Round 2 Escalation (if still FAIL)

If round 2 produces any FAIL, escalate via `AskUserQuestion`:

**Show:**

1. Numbered issue list from both reviewers (round 2)
2. LLM recommendation: one of "ship with caveats" / "fix manually" / "abandon"

**Options:**

- Fix manually — user addresses remaining issues
- Override ship — proceed despite unresolved issues
- Abandon — discard changes

User picks action. Round 3 never auto-runs.

## Reviewer Prompts

### PSY Framework

**Reviewer A (Clinical Accuracy):**

> Review these files for clinical accuracy. Check: DSM-5/ICD-11 codes are valid and properly cited, 5P formulation sections are internally consistent (Presenting/Predisposing/Precipitating/Perpetuating/Protective), defense mechanism hierarchy follows Mature→Neurotic→Immature ordering, attachment pattern descriptions match established theory. For each issue: state file path, line reference, issue description, severity (critical/warning).

**Reviewer B (Cross-Character Consistency):**

> Review these files for cross-character consistency. Check: timeline dates match across characters who share events, relationship dynamics are bidirectional (if A says X about B, B's file reflects it), no contradictory factual claims across characters, clinical terms used consistently. For each issue: state file path, line reference, issue description, severity (critical/warning).

### CRE Framework

**Reviewer A (Voice/Tone Authenticity):**

> Review this content for voice authenticity. Check: writing patterns match the character's writing-voice.md, tone is consistent with character psychology (not artificially cheerful for a character with depressive features), no clinical jargon leaks into public content, emotional register appropriate for platform. For each issue: state file path, line reference, issue description, severity (critical/warning).

**Reviewer B (Profile→Content Alignment):**

> Review this content for profile alignment. Check: biographical facts match identity/core.md, emotional framing matches formulation.md characterization, relationship dynamics match graph/ and relationships/ files, no fabricated events or relationships. For each issue: state file path, line reference, issue description, severity (critical/warning).

### GRO Framework

**Reviewer A (Career Data Accuracy):**

> Review these growth files for data accuracy. Check: career dates are realistic and ordered, Dreyfus competency levels are valid (1-7 scale), Kolb learning style is consistent across assessments, mentor/mentee relationships are documented with evidence. For each issue: state file path, line reference, issue description, severity (critical/warning).

**Reviewer B (Timeline Consistency):**

> Review these growth files for timeline consistency. Check: career progression dates align with identity/core.md birth date and education, no future dates beyond current date, milestone dates ordered chronologically, career transitions have plausible gaps. For each issue: state file path, line reference, issue description, severity (critical/warning).

### MAT Framework

**Reviewer A (Evidence Tier Compliance):**

> Review these material files for evidence tier compliance. Check: CRAAP scores present and realistic (each dimension 1-5; total = sum of 5 dimensions, max 25), evidence tier assignment (T1-T5) matches CRAAP total, processing status frontmatter complete, source attribution present. For each issue: state file path, line reference, issue description, severity (critical/warning).

**Reviewer B (Contradiction Detector):**

> Review these material files for contradictions. Check: no conflicting claims between materials for same character, dates consistent across sources, quotes attributed correctly, no duplicate materials with different metadata. For each issue: state file path, line reference, issue description, severity (critical/warning).

## Scripts

| Script                        | Purpose                                                                  |
| ----------------------------- | ------------------------------------------------------------------------ |
| `scripts/run-santa-review.py` | Deterministic pre-checks: file inventory, schema, word count, cross-refs |

```bash
# Pre-check a PSY profile
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/orc-santa/scripts/run-santa-review.py \
  --target docs/profiles/character-a/ --framework psy --scope ref --round 1

# Pre-check CRE content (changes only)
$HOME/.claude/skills/.venv/bin/python3 .claude/skills/orc-santa/scripts/run-santa-review.py \
  --target assets/facebook/260524-post/ --framework cre --scope changes --round 1
```

## Safety

- Max 2 review rounds enforced at script level (`--round` accepts only 1 or 2)
- Escalation after round 2 — never auto-runs round 3
- Input-level isolation: reviewer prompts contain no session context or other reviewer's output
- Token cost: 2 subagents per round (4 max for 2 rounds) — only triggered on high_risk

## See Also

- `/orc:classify` — triggers Santa on high_risk classification
- `/orc:council` — complementary 4-voice decision framework for ambiguous situations
- `/cre:post-writer` — Phase 7 quality checklist references Santa for high_risk content
