---
name: orc:intake
description: "Classify incoming work type and route to the optimal skill chain. Determines if task is content creation, profile update, arc development, research, or maintenance — then suggests the right sequence of mpc/ck skills. Use at start of any new task. Triggers: 'intake', 'new task', 'what should I do', 'route this', 'start task'. Complements orc:classify (risk) with workflow routing."
argument-hint: "[task description] [--auto]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "pre-planning"
  dependencies: ["orc:classify"]
---

# Intake — Work Type Classification & Routing

Classify what KIND of work this is and route to the right skill chain. Complements `orc:classify` which assesses risk LEVEL.

| Skill          | Answers                 |
| -------------- | ----------------------- |
| `orc:classify` | How risky is this?      |
| `orc:intake`   | What workflow for this? |

## Default (No Arguments)

`AskUserQuestion` — ask user to describe the task, then classify + route.

## Flags

| Flag         | Purpose                                            |
| ------------ | -------------------------------------------------- |
| (positional) | Task description text                              |
| `--auto`     | Auto-classify from git diff + context, skip prompt |

## Work Types

### 1. Content Creation

**Signals:** "write a post", "create content", "LinkedIn/Facebook/Instagram", "script"
**Files involved:** `assets/` directory

**Route:**

```
orc:bootstrap → cre:exploring → orc:classify → cre:prompt-leverage → ck:plan (if normal+) → cre:post-writer → cre:privacy-guard → cre:voice-audit → orc:compounding
```

### 2. Profile Update (PSY Track)

**Signals:** "update psychology", "add to timeline", "edit formulation", "new relationship info", "update defense mechanisms"
**Files involved:** `docs/profiles/*/psychology/`, `docs/profiles/*/timeline/`, etc.

**Route:**

```
orc:bootstrap --character <name> → orc:classify → ck:plan (if high_risk) → profile editing → psy:ref-audit → psy:crossref → orc:compounding
```

**PSY Domain:** psychology/ (formulation, defense-mechanisms, attachment-style, diagnostics, cultural-formulation, archetype), timeline/ (state-timeline), darkness/, light/

### 3. Arc Development

**Signals:** "new storyline", "character arc", "narrative progression", "what happens next"
**Files involved:** `docs/profiles/` + `assets/` + `plans/`

**Route:**

```
orc:bootstrap --full → cre:exploring → orc:classify → ck:plan → phased implementation → psy:ref-audit → psy:crossref → orc:compounding → orc:decisions
```

### 4. Research

**Signals:** "look into", "research", "find out about", "clinical theory", "reference"
**Files involved:** `docs/references/` + `docs/materials/`

**Route:**

```
orc:bootstrap --quick → research execution → orc:compounding (if insights found)
```

### 5. Material Ingestion (MAT Track)

**Signals:** "new transcript", "received letter", "new evidence", "ingest material", "new source"
**Files involved:** `docs/materials/`

**Route:**

```
orc:bootstrap --quick → mat:loader --ingest <path> → mat:indexer --character <name> → orc:classify → cre:privacy-guard → suggest profile updates → orc:session-state
```

**MAT Pipeline:** mat:loader (Stage 1-2) → mat:indexer (Stage 3-4) → auto-emit MAT.integrated → PSY.refresh

### 6. Consistency Audit

**Signals:** "validate profiles", "consistency check", "run audit", "cross-check", "review accuracy"
**Files involved:** `docs/profiles/` + `docs/references/`

**Route:**

```
orc:bootstrap --full → psy:crossref --all → psy:ref-audit --discover --cross-ref → cre:voice-audit → report
```

### 7. Reference Management

**Signals:** "create reference", "new theory", "missing ref", "add to reference library"
**Files involved:** `docs/references/`

**Route:**

```
psy:ref-audit --discover → psy:ref-create <theory> → psy:ref-scan --new → update profile links
```

### 8. Maintenance

**Signals:** "clean up", "organize", "fix inconsistency", "update docs", "archive"
**Files involved:** various

**Route:**

```
orc:dream (if memory) → direct execution → orc:session-state --archive (if session end)
```

### 9. Multi-Platform Campaign

**Signals:** "campaign", "across platforms", "multi-channel", "launch"
**Files involved:** `assets/` multiple platform dirs

**Route:**

```
orc:bootstrap → cre:exploring → orc:classify (likely high_risk) → ck:plan → cre:post-writer (per platform) → cre:repurpose → cre:privacy-guard → cre:voice-audit → orc:compounding
```

## Classification Logic

### Step 1: Parse Intent

From task description, extract:

- **Action verb:** write, update, create, research, fix, organize, plan
- **Object:** post, profile, arc, theory, content, memory
- **Character:** Nhân vật A, Nhân vật B, Nhân vật C, or none
- **Platform:** LinkedIn, Facebook, Instagram, TikTok, YouTube, Twitter, or none
- **Scope:** single file, single character, cross-character, multi-platform

### Step 2: Match to Work Type

| Action + Object combination                     | Work Type            |
| ----------------------------------------------- | -------------------- |
| write/create + post/content/script              | Content Creation     |
| update/edit/add + profile/SOUL/TIMELINE         | Profile Update       |
| develop/plan + arc/storyline/narrative          | Arc Development      |
| research/find/look + theory/reference           | Research             |
| ingest/receive/new + transcript/letter/material | Material Ingestion   |
| validate/audit/check + consistency/accuracy     | Consistency Audit    |
| create/add + reference/theory/ref               | Reference Management |
| clean/fix/organize + docs/memory/archive        | Maintenance          |
| campaign/launch + multi-platform                | Multi-Platform       |

### Step 3: Output

```
## Intake Result

**Work type:** {type}
**Character:** {name or "none"}
**Platform:** {platform or "N/A"}
**Scope:** {single/cross-character/multi-platform}

### Recommended Workflow

{numbered skill chain}

### Auto-run orc:classify?

Risk classification is recommended. Run now?
```

## Auto Mode

`--auto`:

1. Read session state for current context
2. `git diff --stat` for recent changes
3. Infer work type from changed files + branch name
4. Output classification + route without user input
5. Suggest next skill to run

## Integration

After intake completes:

- Update session state: `phase` → `"exploring"` or `"planning"`
- If `--auto` and work type is clear → auto-run `orc:classify`

## Scripts

| Script                                                | Purpose                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| `scripts/classify-work-type-from-task-description.py` | Parse task description text and match to work type categories |

## Safety

- READ-ONLY — never modifies files
- Only outputs classification and routing suggestion
- User decides which skills to actually run
- Scope: work classification for ck-marketing. Does NOT handle execution.

## Examples

```bash
/orc:intake Write a LinkedIn post about Nhân vật A's mentoring journey
/orc:intake Update Nhân vật B's psychology/formulation.md with new attachment analysis
/orc:intake --auto
/orc:intake Research parentification theory for Nhân vật C's profile
```

## See Also

- `/orc:classify` — risk level (complements intake's workflow routing)
- `/cre:exploring` — often the next step after intake for content work
- `/orc:bootstrap` — context loading recommended by most routes
