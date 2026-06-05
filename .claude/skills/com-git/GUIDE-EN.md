# com:git — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've edited docs, created features, or fixed bugs. Now you want to save those changes to git without thinking about which files matter. com:git reads your edits, picks the related ones, shows you a preview, commits with a professional message, and pushes — all in one command.

## 2. Core concepts (the mental model)

**Smart file selection:** Commit groups files by scope (profile, assets, refs, materials). Not everything you touched goes in — only files related to your current work. Secrets always excluded.

**Preview before action:** Default mode stops and asks "is this right?" before committing. You can edit, confirm, or add more files.

**Automatic rebase:** If someone pushed while you were working, `--push` auto-rebases and retries. If rebase conflicts, it stops and asks for your help.

**Conventional commits:** Messages follow the pattern `type(scope): description` — clean git history, easy to parse.

## 3. Learning path

**First run:** `com:git` (default) — see the preview, say "yes" to commit, watch it push.

**Next:** Try `com:git --auto` when you trust the file selection; skips confirmation, goes straight to commit + push.

**As you grow:** Use `--dry-run` to preview without executing; `--commit --all` to stage everything; `--sync` to pull before pushing (safety-first workflow).

## 4. Use cases (each = a sample conversation)

### Use case: Commit changes from this session

> You: "commit my work"
> Skill: Reads git status, detects 3 .md files changed in docs/profiles/. Generates message `docs(profile): update character psychology notes`. Shows preview, waits for confirmation, commits + pushes.

### Use case: Auto-commit and push (no interruption)

> You: "auto commit"
> Skill: `com:git --auto`. Same steps but SKIPS the preview question. Commits related files + pushes. Useful when you're confident.

### Use case: Dry-run to see what would happen

> You: "what would you commit?"
> Skill: `com:git --dry-run`. Shows the message and file list, but does NOT stage or commit. Lets you verify before running the real thing.

### Use case: Custom commit message

> You: "commit with message 'add new character sketch'"
> Skill: `com:git -m "add new character sketch"`. Uses your message instead of auto-generating. Still previews, still asks for confirmation.

### Use case: Commit everything

> You: "commit all my changes"
> Skill: `com:git --commit --all`. Stages all changed files (except secrets), generates message, shows preview, confirms, commits.

## 5. Important caveats

**Secrets are auto-excluded.** You cannot commit `.env`, `credentials.json`, or key files — the skill rejects them. This is a safety feature.

**Preview is default.** If you say `--commit` (without `--auto`), you WILL be asked to confirm. The skill never commits without showing you first.

**Rebase conflicts need you.** If pull --rebase hits a conflict, the skill aborts the rebase and reports it. You must resolve manually and retry the push.

**Protected branches.** If your remote has branch protection rules (e.g., main), the skill won't force-push. It respects the rules.

**Whitespace cleanup.** The skill runs prettier on staged files before committing (non-fatal — if prettier is missing, it skips). This keeps formatting consistent.
