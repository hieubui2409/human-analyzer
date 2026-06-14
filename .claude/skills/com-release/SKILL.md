---
name: com:release
description: "Cut a versioned release of the frameworks pack via the Keep a Changelog lifecycle. Use when the user says 'cut a release', 'release vX.Y.Z', 'bump version', 'ship the pack'. Interviews the user, locks [Unreleased] → [X.Y.Z], bumps the manifest; the tag push that fires release CI is owner-owned."
argument-hint: "--release X.Y.Z | --bump patch|minor|major [--pre-release rc.N] [--apply] [--push]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "release"
  position: "utility"
  dependencies: []
---

# Release Operations for human-analyzer

Cut a versioned release of the 7-framework pack. The human-curated `CHANGELOG.md` (Keep a Changelog,
with an `[Unreleased]` section) is the truth of record; this skill performs the deterministic
release-cut and hands the owner the tag push that fires release CI.

## INTERVIEW FIRST (mandatory)

Never run a release-cut blind. Before any `--apply`, use `AskUserQuestion` to confirm:

1. **Version** — explicit (`--release X.Y.Z`) or computed (`--bump patch|minor|major` from the manifest).
   Show the resulting version string.
2. **Pre-release?** — stable, or a pre-release label (`--pre-release rc.1` → `X.Y.Z-rc.1`, published as a
   GitHub prerelease).
3. **Review the `[Unreleased]` content** that will be locked — read it back; if it is thin or empty,
   stop and ask the user to fill it (the cut refuses an empty `[Unreleased]`).
4. **Push now or hand off?** — the tag push is **owner-owned**. Default is dry-run; only add `--apply`
   (and `--push`) when the owner explicitly says go.

## What a release-cut does

`.claude/skills/_framework-shared/scripts/release.py` (deterministic, no git-at-build-time):

1. Lock `## [Unreleased]` → `## [X.Y.Z] — <date>`; open a fresh empty `[Unreleased]`.
2. Bump `.claude/pack.manifest.yaml` `version:`.
3. Assert the locked section is PII-clean (a real-name leak aborts).
4. Print the exact `git commit && git tag frameworks-v<ver> && git push` commands (or run them with `--push`).

Pushing the `frameworks-v<ver>` tag fires `.github/workflows/frameworks-pack-release.yml`: tag↔manifest
assertion → determinism gate → whole-pack PII/secret gate → build → SHA256SUMS → GitHub Release whose
**body is the locked CHANGELOG section**.

## Flags

| Flag | Effect |
| --- | --- |
| `--extract X.Y.Z` | Print a version's CHANGELOG section body (what CI uses as the release body). Read-only. |
| `--release X.Y.Z` | Cut a release at an explicit version. |
| `--bump patch\|minor\|major` | Cut a release at the next version computed from the manifest. |
| `--pre-release LABEL` | Append a pre-release label (e.g. `rc.1`). Published as a GitHub prerelease. |
| `--apply` | Write changes (default: dry-run preview). |
| `--push` | Owner opt-in: also create + push the tag (requires `--apply`). |

## Commands

```bash
# Preview a cut (dry-run — writes nothing):
.claude/skills/.venv/bin/python3 .claude/skills/_framework-shared/scripts/release.py --bump minor

# Apply locally, then hand the printed tag commands to the owner:
.claude/skills/.venv/bin/python3 .claude/skills/_framework-shared/scripts/release.py --release 1.1.0 --apply

# Owner go: apply + tag + push (fires CI):
.claude/skills/.venv/bin/python3 .claude/skills/_framework-shared/scripts/release.py --release 1.1.0 --apply --push

# Inspect what CI will publish as the release body:
.claude/skills/.venv/bin/python3 .claude/skills/_framework-shared/scripts/release.py --extract 1.1.0
```

## What it does NOT do

- **Never auto-derives changelog content from git.** `[Unreleased]` is filled by hand/LLM during dev;
  this skill only moves and versions it. The committed `CHANGELOG.md` is reproducible.
- **Never pushes a tag without explicit owner approval.** `--push` requires `--apply` and an explicit go;
  default is dry-run. Release-to-master / re-tagging an existing version stay owner-owned.
- **Never edits a past version's section.** A cut refuses if `[X.Y.Z]` already exists.
- **Never releases an empty `[Unreleased]`.**

## See also

- Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md) · Overview: [`README.md`](./README.md)
- Lifecycle source: `.claude/skills/_framework-shared/scripts/release.py`
- Release CI: `.github/workflows/frameworks-pack-release.yml`; convention: [keepachangelog.com](https://keepachangelog.com/)
