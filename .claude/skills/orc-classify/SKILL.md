---
name: orc:classify
description: "Classify task risk level and determine workflow ceremony before implementation. Use when starting content creation, profile updates, arc development, or asset production. Outputs mode (tiny/normal/high_risk), required ceremony, proof strategy. Should run BEFORE /ck:plan or any implementation work."
argument-hint: "[task description] [--auto] [--show]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "pre-planning"
  dependencies: []
---

# Risk Classification for Content Projects

Classify every task before implementation. Outputs risk mode, ceremony steps, and proof requirements. Writes classification to `.claude/session-state/state.json`.

## Default (No Arguments)

`AskUserQuestion` — ask user to describe the task, then classify.

## Flags

| Flag         | Purpose                                                            |
| ------------ | ------------------------------------------------------------------ |
| (positional) | Task description text                                              |
| `--auto`     | Auto-classify from git diff + branch name, skip user prompt        |
| `--show`     | Show current classification from state.json without re-classifying |

## Workflow

### Step 1: Gather Task Context

If `--auto`:

- Run `git diff --stat` to detect changed files
- Infer scope from file paths (profiles/, assets/, docs/)

If `--show`:

- Read `.claude/session-state/state.json`
- Print current classification and exit

Otherwise:

- Use `$ARGUMENTS` as task description
- If empty, `AskUserQuestion` with header "Task Classification"

### Step 2: Hard Gate Check

If task touches ANY hard gate → **high_risk** immediately.

| Gate                           | Detection                                                                                                          | Trigger                         |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| Cross-character consistency    | Files in 2+ profile directories simultaneously                                                                     | Changing relationship dynamics  |
| Clinical reference compliance  | Files in `docs/references/` + `docs/profiles/*/psychology/`                                                        | Psychological framework changes |
| Timeline continuity            | `timeline/state-timeline.md` + `relationships/family.md` + cross-character files (via `list_relationship_files()`) | Backdating or reordering events |
| Public content with real names | Assets referencing real people outside the 3 main characters                                                       | Legal/privacy risk              |
| MAT evidence conflict          | `mat:indexer` found HIGH/CRITICAL contradiction                                                                    | Material-profile mismatch       |

### Step 3: Count Risk Flags

| #   | Flag                         | Signal                                                             |
| --- | ---------------------------- | ------------------------------------------------------------------ |
| 1   | Profile psychology/ edit     | Modifying formulation, defense mechanisms, attachment, diagnostics |
| 2   | Profile darkness/ edit       | Modifying trauma documentation                                     |
| 3   | Multi-platform content       | Content targeting 3+ platforms simultaneously                      |
| 4   | New character arc            | Introducing new narrative arc or major character development       |
| 5   | Clinical terminology         | Content referencing specific clinical/psychological terms          |
| 6   | Cross-character references   | Content mentioning relationship dynamics between characters        |
| 7   | Historical accuracy          | Content about real events that must be factually accurate          |
| 8   | Sensitive topic              | Content about trauma, self-harm, family conflict                   |
| 9   | Asset with AI-generated face | Image prompts that could produce recognizable faces                |
| 10  | Viral/public-facing          | Content designed for wide distribution (not just personal network) |
| 11  | Writing voice consistency    | Content that must match established writing-voice.md patterns      |
| 12  | MAT evidence gap             | Content about topics with no material backing (T5-only)            |

### Step 4: Classify

| Condition               | Mode        |
| ----------------------- | ----------- |
| Any hard gate triggered | `high_risk` |
| 4+ flags                | `high_risk` |
| 2-3 flags               | `normal`    |
| 0-1 flags               | `tiny`      |

### Step 5: Output Classification

```
## Classification Result

**Mode:** {mode}
**Hard gates:** {list or "none"}
**Flags ({count}):** {list}

### Required Ceremony

{ceremony steps}

### Proof Strategy

| Check | Required | How |
|-------|----------|-----|
{proof rows}

### Harness Delta Reminder

After completing this task, check:
- [ ] Profile files consistent across characters?
- [ ] Clinical references accurate?
- [ ] Content matches `identity/writing-voice.md`?
- [ ] Timeline entries added if needed?
```

#### Ceremony by Mode

**tiny:**

1. Implement directly
2. Quick self-review for tone/accuracy

**normal:**

1. `/ck:plan` or outline approach
2. Implement per plan
3. Cross-reference with relevant profile files
4. Review for clinical accuracy if psychological content

**high_risk:**

1. `orc:bootstrap --full` — load ALL relevant character context
2. `orc:decisions --review` — check past decisions for this character/topic to avoid re-litigating
3. `/ck:plan` — detailed plan with profile cross-references
4. Read ALL relevant profile files before starting
5. Implement per plan phases
6. Cross-character consistency check
7. Clinical reference verification
8. Tone/voice review against `identity/writing-voice.md`

#### Proof by Mode

| Check                   | tiny     | normal      | high_risk | How                                   |
| ----------------------- | -------- | ----------- | --------- | ------------------------------------- |
| Self-review             | Required | Required    | Required  | Read output against profiles          |
| Profile cross-reference | —        | If profile  | Required  | Compare with INDEX.md                 |
| Clinical accuracy       | —        | If clinical | Required  | Check docs/references/                |
| Timeline consistency    | —        | If timeline | Required  | Verify `timeline/overview.md` entries |
| Writing voice match     | —        | Optional    | Required  | Compare `identity/writing-voice.md`   |
| Multi-character review  | —        | —           | Required  | Check all affected profiles           |

### File-Level Sensitivity (B6)

In addition to task-level classification, individual files have sensitivity levels enforced by the `gateguard-profile-protect` hook (PreToolUse on Edit|Write):

| Level    | Directories                                                                  | Hook Behavior                                        |
| -------- | ---------------------------------------------------------------------------- | ---------------------------------------------------- |
| CRITICAL | `darkness/`                                                                  | HARD block — must acknowledge checks + user approval |
| HIGH     | `psychology/` (all 8 files)                                                  | HARD block — must acknowledge checks + user approval |
| MEDIUM   | `relationships/`, `growth/`, `docs/rules/`, `docs/graph/`, `docs/materials/` | Warning only                                         |
| LOW      | `identity/`, `timeline/`, `light/`, `evidence/`                              | No gate                                              |

Task-level classification (tiny/normal/high_risk) determines ceremony; file-level sensitivity determines per-edit gates. Both systems are complementary.

See: `.claude/scripts/platform_lib/file_sensitivity.py --all` for complete mapping.

### Santa Method Gate (A1)

When classification result is `high_risk`, recommend Santa dual-review:

| Condition                        | Action                                                |
| -------------------------------- | ----------------------------------------------------- |
| high_risk + profile edit         | Suggest `orc:santa --review <target> --framework psy` |
| high_risk + content creation     | Suggest `orc:santa --review <target> --framework cre` |
| high_risk + growth edit          | Suggest `orc:santa --review <target> --framework gro` |
| high_risk + material integration | Suggest `orc:santa --review <target> --framework mat` |

Santa is RECOMMENDED for high_risk, not mandatory. User can skip with explicit acknowledgment.

### Council Decision Gate (A4)

When classification detects ambiguity (conflicting interpretations, unclear direction), suggest Council:

| Trigger         | Condition                                                      |
| --------------- | -------------------------------------------------------------- |
| PSY conflict    | 2+ valid clinical interpretations for same behavior            |
| CRE ambiguity   | Content direction unclear, multiple valid angles               |
| GRO dispute     | Career trajectory has 2+ plausible paths                       |
| Cross-character | Relationship dynamic interpretation differs between characters |

Council is SUGGESTED, never auto-triggered. User invokes manually via `/orc:council`.

### Step 6: Write to Session State

Read `.claude/session-state/state.json`, update atomically (read → modify → write-back):

```json
{
  "mode": "{classified_mode}",
  "phase": "planning"
}
```

Verify write succeeded by re-reading `mode` field after write.

### Step 7: Recommend Next Step

- **tiny:** "Ready to implement. Start creating."
- **normal:** "Run `/ck:plan` or outline your approach."
- **high_risk:** "Run `/ck:plan` to create detailed plan with profile cross-references."

## Examples

```bash
/orc:classify Write a LinkedIn post about Nhân vật A's mentoring philosophy
/orc:classify Update psychology/formulation.md for Nhân vật B with new psychological insights
/orc:classify --auto
/orc:classify --show
```

## Scripts

| Script                                       | Purpose                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------- |
| `scripts/detect-risk-flags-from-git-diff.py` | Scan git diff output for risk flag signals to seed auto-classification |

## GRO Domain Risk Notes

Growth domain files (`docs/growth/`) contain factual career and competency data — not clinical content. Risk classification applies as follows:

- Edits to `docs/growth/` are **normal** risk by default (factual career data, no clinical sensitivity)
- Exception: if growth content cross-references psychology/ profiles → escalate to `high_risk` (cross-domain consistency gate)
- Career forecasts with public-facing distribution → add flag 10 (viral/public-facing)

## Safety

- READ-ONLY classification — does not modify profiles, content, or references
- Writes only to `.claude/session-state/state.json` (session metadata)
- Scope: task risk classification and workflow routing. Does NOT implement tasks, create content, or modify profiles.

## See Also

- `/orc:session-state` — classification writes mode to state.json
- `/orc:decisions` — review past decisions before high_risk work
- `/ck:plan` — next step after classification for normal/high_risk
- `docs/profiles/*/INDEX.md` — quick reference for each character
- `docs/references/INDEX.md` — clinical theory library index
