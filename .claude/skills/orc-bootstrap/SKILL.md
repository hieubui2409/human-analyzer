---
name: orc:bootstrap
description: "Bootstrap project context for ck-marketing sessions. Systematically load character profiles, active arcs, recent git changes, and session state. Use at session start, when switching focus between characters, or when context feels stale. Triggers: 'bootstrap', 'load context', 'refresh context', 'catch me up'."
argument-hint: "[--full|--character <name>|--recent|--quick|--lite|--intent <task>]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "workflow"
  position: "session-start"
  dependencies: ["orc:session-state"]
---

# Project Context Bootstrap

Systematically load ck-marketing context into session. Prevents context drift across 3 complex character profiles + clinical references + GRO growth domain.

## Default (No Arguments)

`--quick` — load INDEX.md for all characters + recent git changes + session state.

## Flags

| Flag                 | Purpose                                                        |
| -------------------- | -------------------------------------------------------------- |
| `--quick`            | INDEX.md × 3 characters + recent changes (default)             |
| `--full`             | All profile files for all characters                           |
| `--character <name>` | Deep-load one character's full profile                         |
| `--recent`           | Git log + diff of last 7 days only                             |
| `--lite`             | Use psy:profile-lite cached summaries (~400 lines vs ~7400)    |
| `--intent <task>`    | Task-aware loading — only load files relevant to stated intent |

## Character Name Resolution

Resolve `<name>` argument to directory:

| Input                                 | Directory           |
| ------------------------------------- | ------------------- |
| `hieu`, `hiếu`, `character-a`      | `character-a`    |
| `hoa`, `hòa`, `character-b`        | `character-b`    |
| `chien`, `chiến`, `character-c` | `character-c` |

## Workflow

### --quick (Default)

1. Read `.claude/session-state/state.json` — print mode/phase/branch
2. For each character in `docs/profiles/{character-a,character-b,character-c}`:
   - Read `INDEX.md`
3. Run `git log --oneline -15` — show recent commits
4. Run `git diff --stat HEAD~5` — show recent file changes
5. If session state has `profiles_touched` → highlight which characters were active
6. Print bootstrap summary:
   ```
   ## Context Loaded
   Characters: Nhân vật A (INDEX), Nhân vật B (INDEX), Nhân vật C (INDEX)
   Session: {mode} / {phase} on {branch}
   Recent: {N} commits, {M} files changed
   Active profiles: {profiles_touched or "none yet"}
   ```

### --full

1. Read session state
2. For each character directory in `docs/profiles/`:
   - Read ALL .md files in nested universal structure:
     - Root: INDEX.md → CURRENT-STATE.md → milestones.md
     - identity/: core.md → writing-voice.md → achievements.md → media-coverage.md
     - psychology/: core-wounds.md → defense-mechanisms.md → attachment-style.md → growth-edges.md → formulation.md → diagnostics.md → cultural-formulation.md → archetype.md
     - relationships/: family.md + cross-character files (discovered via `list_relationship_files()`)
     - timeline/: overview.md → state-timeline.md
     - darkness/: traumas.md
     - light/: strengths-hope.md
     - evidence/: conversations.md
   - Skip files that don't exist
3. Read `docs/references/INDEX.md` (clinical theory index)
4. Read `docs/graph/relational-dynamics.md` (cross-character dynamics)
5. Read `docs/rules/` (13 modular rule files)
6. Read `docs/growth/` files if present (GRO domain: competency maps, career forecasts, learning profiles, mentoring tracks)
7. Run recent git log
8. Print summary with file count per character

### --character `<name>`

1. Resolve name to directory
2. Read ALL .md files in `docs/profiles/{resolved}/`
3. Read related materials in `docs/materials/{resolved}/` (list only, don't read all)
4. Check `docs/references/INDEX.md` for theories referenced in psychology/formulation.md
5. Run `git log --oneline -10 -- docs/profiles/{resolved}/` — character-specific history
6. Print character-focused summary

### --recent

1. `git log --oneline --since="7 days ago"` — commits
2. `git diff --stat HEAD~20` — changed files (capped at 20 commits)
3. Filter to show:
   - Profile changes (docs/profiles/)
   - Content changes (assets/)
   - Plan changes (plans/)
   - Harness changes (.claude/)
4. If session state exists, overlay with state.json data
5. Print recent activity summary

### --lite

1. Read session state
2. For each character, load from `.claude/profile-cache/{slug}-lite.md`
   - If cache missing or stale → auto-run `psy:profile-lite --character <name>` to generate
3. Lite profiles provide ~120-150 lines per character (vs ~700-1000 full)
4. Total context: ~400 lines for all 3 characters (vs ~7400 full)
5. Run recent git log
6. Print summary noting "lite mode" for transparency

### --intent `<task>`

Task-aware selective loading. Only reads files relevant to the stated task.

Intent-to-file mapping:

| Intent keywords                   | Files loaded per character               |
| --------------------------------- | ---------------------------------------- |
| "write post", "content", "create" | WRITING-VOICE + SOUL + CHARACTERISTIC    |
| "update timeline", "add event"    | TIMELINE + RELATIONSHIPS                 |
| "psychology", "clinical", "soul"  | SOUL + DARKNESS + LIGHT + refs/INDEX     |
| "relationship", "cross-character" | RELATIONSHIPS × all characters           |
| "profile update"                  | INDEX + target files mentioned in intent |
| "audit", "validate"               | All files (falls back to --full)         |

Workflow:

1. Parse intent text → extract keywords
2. Match to file mapping above
3. Resolve character from intent (or ask if ambiguous)
4. Load only mapped files + session state
5. Print what was loaded and what was skipped:
   ```
   ## Intent-Based Load: "write LinkedIn post about Nhân vật B"
   Loaded: Nhân vật B (WRITING-VOICE, SOUL, CHARACTERISTIC) — 660 lines
   Skipped: TIMELINE, RELATIONSHIPS, DARKNESS, LIGHT, MILESTONES — 1527 lines saved
   Also loaded: session state, recent git log
   ```

## Reading Priority Order

When loading profiles, read in this order (most important first):

1. `INDEX.md` — quick reference, always first
2. `psychology/formulation.md` — 5 Ps case formulation, most clinically dense
3. `psychology/defense-mechanisms.md` — defense hierarchy
4. `psychology/attachment-style.md` — attachment patterns
5. `relationships/family.md` + cross-character files (via `list_relationship_files()`) — character dynamics
6. `identity/writing-voice.md` — tone/style (Nhân vật A only)
7. `identity/core.md` — basic facts + personality traits
8. `timeline/state-timeline.md` — longitudinal ICD-11 phases
9. `psychology/archetype.md` — Jungian/Pia Melody mapping
10. `darkness/traumas.md` — trauma (only when relevant)
11. `light/strengths-hope.md` — hope sources
12. `milestones.md` — key moments
13. `psychology/diagnostics.md` — Big Five + ICD-11 scores
14. `psychology/cultural-formulation.md` — cultural context

## Scripts

| Script                                               | Purpose                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------- |
| `scripts/load-project-context-fast-summary.sh`       | Generate fast summary of project context for quick bootstrap        |
| `scripts/validate-profile-lite-cache-by-git-hash.py` | Check if profile-lite cache is still valid against current git hash |

## Safety

- This skill is READ-ONLY — never modifies any files
- Does NOT handle sensitive data beyond what's in git
- Scope: ck-marketing project context loading. Does NOT handle code implementation, content creation, or analysis.

## Examples

```bash
/orc:bootstrap                          # quick: INDEX × 3 + recent
/orc:bootstrap --full                   # deep: all profiles + refs
/orc:bootstrap --character hòa          # deep-load Nhân vật B only
/orc:bootstrap --character chien        # deep-load Nhân vật C only
/orc:bootstrap --recent                 # last 7 days activity
/orc:bootstrap --lite                   # lite profiles × 3 (~400 lines)
/orc:bootstrap --intent "write LinkedIn post about Nhân vật B"  # task-aware
```

## See Also

- `/orc:session-state` — state loaded during bootstrap
- `/orc:classify` — run after bootstrap to classify next task
- `/cre:exploring` — structured exploration after context loaded
