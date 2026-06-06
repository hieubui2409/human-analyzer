# com:release — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've recorded a batch of changes under `## [Unreleased]` in `CHANGELOG.md` and the pack is ready to
ship. com:release turns that into a versioned release: it locks `[Unreleased]` into `[X.Y.Z] — <date>`,
opens a fresh `[Unreleased]`, bumps the manifest, regenerates the deterministic RELEASE-NOTES catalog,
and hands you the exact tag-push commands that fire release CI.

## 2. Core concepts (the mental model)

**The changelog is hand-curated, not git-derived.** During development you (or an LLM) write entries
under `[Unreleased]`. Nothing reads `git log` at build time, so the committed `CHANGELOG.md` is
reproducible — running the tooling later never mutates it.

**Lock = move, not generate.** A release-cut renames the `[Unreleased]` heading to `[X.Y.Z] — <date>`
and inserts a fresh empty `[Unreleased]` above it. The content you wrote becomes the version's body.

**Two artifacts, two roles.** `CHANGELOG.md` = the human "what changed" (curated). `RELEASE-NOTES-v<ver>.md`
= the deterministic "what shipped" catalog (every skill/agent/hook, auto-enumerated). The locked
changelog section also becomes the GitHub Release body.

**The tag is the trigger.** Pushing `frameworks-v<ver>` fires `frameworks-pack-release.yml` (tag↔manifest
check → determinism gate → PII gate → build → SHA256 → GitHub Release). The push is **owner-owned**.

## 3. Learning path

**Preview first:** `release.py --bump minor` (dry-run) — see the version, the lock, and the git
commands, writing nothing.

**Apply locally:** add `--apply` — it writes CHANGELOG/manifest/notes and prints the tag commands for you
to run.

**Owner go:** add `--push` (with `--apply`) only when the owner explicitly approves — it tags + pushes,
firing CI.

**Inspect the release body:** `--extract X.Y.Z` prints exactly what CI will publish as the GitHub Release
body.

## 4. Use cases (each = a sample conversation)

### Use case: Preview the next minor release

> You: "what would a minor release look like?"
> Skill: Interviews to confirm minor (e.g. 1.0.0 → 1.1.0), reads back the `[Unreleased]` content, runs
> `release.py --bump minor` (dry-run), shows the lock + the git commands. Writes nothing.

### Use case: Cut an explicit release locally

> You: "cut release 1.1.0"
> Skill: Confirms version + reviews `[Unreleased]`, then `--release 1.1.0 --apply`. Locks the changelog,
> bumps the manifest, regenerates notes, and prints `git tag frameworks-v1.1.0 && git push …` for the owner.

### Use case: Release candidate

> You: "make an rc for 1.2.0"
> Skill: `--release 1.2.0 --pre-release rc.1` → version `1.2.0-rc.1`, published as a GitHub prerelease.

### Use case: See the release body CI will publish

> You: "show the release notes for 1.1.0"
> Skill: `--extract 1.1.0` — prints the section body, PII-checked.

## 5. Important caveats

**The push is owner-owned.** Default is dry-run. `--push` requires `--apply` AND explicit owner approval.
Release-to-master and re-tagging an existing version are never done automatically.

**Empty `[Unreleased]` is refused.** If nothing is recorded, the cut aborts — fill the changelog first.

**A version is cut once.** Re-cutting an existing `[X.Y.Z]` is refused; the tool never edits a past section.

**PII gate.** The locked section and the regenerated notes are scanned for real-name tokens; a leak aborts
the cut. The committed `CHANGELOG.md` is also gated PII-clean by the test suite.

**Determinism.** RELEASE-NOTES takes an explicit date and sorts every list — same tree + version + date ⇒
byte-identical output, so the CI determinism gate stays green.
