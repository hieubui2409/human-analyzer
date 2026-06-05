---
name: com:git
description: "Git commit & push with conventional commit format for human-analyzer. Use when user says 'commit', 'push', 'save changes'. Smart file selection, preview, auto-rebase. Excludes .env/credentials. Never force-pushes to protected branches."
argument-hint: "--commit|--push|--sync [--auto|--all|--dry-run] [-m 'msg']"
metadata:
  author: hieubt
  version: "1.1.0"
  category: "git"
  position: "utility"
  dependencies: []
---

# Git Operations for human-analyzer

Commit, push, sync with conventional commit format. No ticket prefix required.

## Default (No Arguments)

Default: `--commit --push`. Analyze context → select files → preview → confirm → commit → push.

## Flags

| Flag       | Purpose                                 | Script                             |
| ---------- | --------------------------------------- | ---------------------------------- |
| `--commit` | Analyze + select files + commit         | `scripts/commit.sh`                |
| `--push`   | Push to remote, auto-rebase if rejected | `scripts/push-with-auto-rebase.sh` |
| `--sync`   | Pull --rebase from remote               | `scripts/sync-pull-rebase.sh`      |

## Options

| Option      | Purpose                                                    |
| ----------- | ---------------------------------------------------------- |
| `--auto`    | No confirmation — analyze + commit + push, fully automatic |
| `--all`     | Skip smart selection — commit ALL changed files            |
| `--dry-run` | Preview what would be staged/committed without executing   |
| `-m "msg"`  | Custom commit message body                                 |

## Routing (IMPORTANT — Claude executes this logic)

Parse `$ARGUMENTS`:

1. Extract flags: `--commit`, `--push`, `--sync`, `--auto`, `--all`, `--dry-run`
2. Extract `-m` value if present
3. If no flags → default to `--commit --push`
4. If `--auto --all` → follow **Auto-All Mode** (no confirm, all files)
5. If `--auto` (without `--all`) → follow **Auto Mode** (no confirm, related files only)
6. For `--push` → run `scripts/push-with-auto-rebase.sh` directly via Bash
7. For `--sync` → run `scripts/sync-pull-rebase.sh` directly via Bash
8. For `--commit` → follow **Smart Commit Flow** (with confirmation)

## Commit Message Format

Conventional commits — NO ticket prefix:

```
<type>(<scope>): <brief description>

- file1: description
- file2: description
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `style`, `content`, `assets`

Scopes (inferred from changed files):

- `profile` — docs/profiles/ changes
- `assets` — assets/ changes (posts, images, scripts)
- `refs` — docs/references/ changes
- `materials` — docs/materials/ changes
- `plans` — plans/ changes
- `config` — .claude/ changes

Examples:

```
docs(profile): update Nhân vật B psychology/formulation.md with attachment theory analysis
content(assets): add LinkedIn post on mentoring philosophy
feat(config): add orc-classify skill for risk classification
```

## Auto Mode (--auto)

**Fully automatic: analyze → commit → push. No user confirmation needed.**

Claude performs these steps without stopping for approval:

### Step 1: Gather context

```bash
git status --short
git diff --stat
```

### Step 2: Analyze & select related files

Only include files **directly related** to:

- Current session work (files Claude created/modified during this conversation)
- ALWAYS exclude: `.env*`, `credentials*`, `*.key`, `*.pem`, IDE configs (`.vscode/`, `.idea/`)

### Step 3: Generate commit message

Conventional commit format from diffs.

### Step 4: Execute (NO confirmation)

```bash
export LUCAS_FILES="<selected files>"
export LUCAS_COMMIT_MSG="<generated message>"
bash scripts/commit.sh
```

### Step 5: Push with auto-rebase

```bash
bash scripts/push-with-auto-rebase.sh
```

If push rejected → auto-rebase → retry push (max 1).
If rebase conflict → abort rebase → **report to user** (only case that stops).

### Step 6: Report result

Print summary: commit hash, files committed, push status. One-liner if clean.

## Auto-All Mode (--auto --all)

**Most aggressive: commit ALL changes, no confirmation.**

### Step 1: Stage everything

```bash
export LUCAS_STAGE_ALL=true
```

(Still excludes `.env*`, `credentials*`, `*.key`, `*.pem` via commit.sh safety)

### Step 2: Generate commit message

Analyze all staged files, generate conventional commit message.

### Step 3: Commit

```bash
export LUCAS_STAGE_ALL=true
export LUCAS_COMMIT_MSG="<generated message>"
bash scripts/commit.sh
```

`commit.sh` runs `prettier --write --ignore-unknown` on staged files just before committing (replaces the old per-edit PostToolUse prettier hook, so working edits no longer trigger constant table/markdown reflow). Non-fatal — skips if prettier is unavailable. Set `LUCAS_SKIP_FORMAT=true` to bypass.

### Step 4: Push with auto-fix

```bash
bash scripts/push-with-auto-rebase.sh
```

If push rejected → auto-rebase → retry.
If rebase conflict → abort rebase → **report to user**.

### Step 5: Report result

Print summary: commit hash, file count, push status.

## Smart Commit Flow (--commit without --auto)

**Claude MUST follow these steps. Do NOT delegate to shell script for file selection.**

### Step 1: Gather context

```bash
git status --short
git diff --stat
git diff --cached --stat
```

### Step 2: Analyze & select files

Using current session context (recent messages, branch name), determine which changed files are **related to the current work**. Consider:

- Files modified during this session
- Files matching the content/feature scope
- Exclude files unrelated to current work (IDE config, etc.)
- ALWAYS exclude: `.env*`, `credentials*`, `*.key`, `*.pem`

### Step 3: Generate commit message

Analyze selected files' diffs to determine change type and scope. Format per **Commit Message Format** above.

### Step 4: Preview & confirm (MANDATORY)

Use `AskUserQuestion` to show the user:

- **Commit message** (full text)
- **Files to commit** (list)
- **Files excluded** (list, if any changed files were skipped)

Options:

- "Confirm commit" — proceed with commit
- "Edit selection" — user provides feedback on which files to add/remove
- "Commit all changes" — switch to --all mode (stage everything)
- (Other — user types custom feedback)

### Step 5: Execute commit

Only after user confirms:

```bash
export LUCAS_FILES="<selected files>"
export LUCAS_COMMIT_MSG="<generated message>"
bash scripts/commit.sh
```

## All Mode (--commit --all)

Skip smart selection. Stage everything. But still:

1. Run `git status --short` to see all changes
2. Generate commit message
3. **Preview & confirm via AskUserQuestion** (same as Step 4 above)
4. Execute: `bash scripts/commit.sh` with `LUCAS_STAGE_ALL=true`

## Push with Auto-Rebase

1. `git push origin <branch>`
2. If rejected (non-fast-forward):
   a. `git pull --rebase origin <branch>`
   b. If conflict → `git rebase --abort` → report to user
   c. If clean → retry push (max 1 retry)
3. If still fails → report error

## Safety

- NEVER force push
- NEVER push to master directly (warn user first)
- NEVER commit `.env`, `credentials`, `*.key`, `*.pem`
- Abort rebase on conflict (don't auto-resolve)
- Default mode: ALWAYS preview and ask user before committing
- Auto mode: skip confirmation but still apply safety exclusions

## Scripts

| Script                             | Purpose                                                |
| ---------------------------------- | ------------------------------------------------------ |
| `scripts/commit.sh`                | Stage and commit files with conventional commit format |
| `scripts/push-with-auto-rebase.sh` | Push with conflict-detected auto-rebase logic          |
| `scripts/sync-pull-rebase.sh`      | Pull --rebase with conflict detection + abort safety   |
| `scripts/ck-git-dispatcher.sh`     | CLI dispatcher for multi-flag invocation               |

## Environment

| Variable           | Default                  | Purpose                   |
| ------------------ | ------------------------ | ------------------------- |
| `PROJECT_DIR`      | Git root (auto-detected) | Working directory         |
| `LUCAS_COMMIT_MSG` | —                        | Full commit message       |
| `LUCAS_FILES`      | —                        | Space-separated file list |
| `LUCAS_STAGE_ALL`  | `false`                  | Stage all changes         |
| `LUCAS_DRY_RUN`    | `false`                  | Preview without executing |

## Examples

```bash
/com:git                              # smart select + preview + commit + push
/com:git --auto                       # auto: commit related + push (no confirm)
/com:git --commit                     # smart select + preview + commit only
/com:git --commit --auto              # auto commit only (no push, no confirm)
/com:git --auto --all                 # auto commit ALL + push
/com:git --commit --all               # stage all + preview + commit
/com:git --commit -m "add new post"   # custom msg + preview
/com:git --push                       # push only
/com:git --sync                       # pull --rebase
/com:git --dry-run                    # preview what would be committed
```

## See Also

- `/orc:session-state` — check what was modified this session
- `/orc:classify` — classify before committing (high_risk may need review first)
- `/com:docs --backup` — backup docs to external git repo after committing
