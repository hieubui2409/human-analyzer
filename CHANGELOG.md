# Changelog

All notable changes to the **human-analyzer frameworks toolkit** are documented here.
The bundle ships 6 domain frameworks (ORC · PSY · CRE · GRO · MAT · COM) with their skills, domain
agents, and framework hooks. Tags `frameworks-v*` version the bundle as a whole.
Format: [keepachangelog.com](https://keepachangelog.com/en/1.1.0/). Versioning: [semver](https://semver.org/).

> **Release discipline.** During development, add entries under `## [Unreleased]`. On release, run
> `tools/release/release_changelog.py --release X.Y.Z` (or `--bump {patch,minor,major}`): it locks
> `[Unreleased]` → `[X.Y.Z] — <date>`, opens a fresh empty `[Unreleased]`, bumps
> `.claude/pack.manifest.yaml`, and regenerates the deterministic `docs/RELEASE-NOTES-v<ver>.md`
> catalog. The locked section becomes the GitHub Release body. Nothing here is auto-derived from git
> at build time — this file is the human-curated truth of record.

## [Unreleased]

## [1.0.0] — 2026-06-07

First public release of the clinical-grade character-profile intelligence toolkit: a privacy-safe,
byte-reproducible pack of the 6-framework system (materials → psychology → content, with growth +
orchestration), shipping zero real-character data.

### Added
- **6-framework toolkit** — ORC (orchestration), PSY (psychology), CRE (content), GRO (growth),
  MAT (materials), COM (common), wired by an event bus, with their skills, 6 domain agents, and
  6 framework hooks.
- **New-character registration flow + drift invariant** — scaffolding auto-registers a character;
  an invariant fails the suite on any roster↔profile mismatch, so the roster can never silently
  diverge from the on-disk profiles.
- **Deterministic, byte-reproducible release pack** — `build_pack.py` produces a byte-identical
  `.tar.gz` from the same source + manifest (sorted walk, fixed mtime/uid/gid), with a per-file
  SHA256 `MANIFEST.json` embedded in the archive.
- **Fail-closed whole-pack PII/secret scan** — `scan_pack_pii.py` scans the built tarball with no
  carve-out and fails the release on any real-name token or secret; it fails closed if the roster is
  present but yields no tokens.
- **Tag-triggered release CI** — pushing `frameworks-vX.Y.Z` runs the determinism gate, the PII gate,
  builds the pack, records SHA256SUMS, and publishes a GitHub Release whose body is this changelog's
  locked section.
- **Keep a Changelog lifecycle** — this `CHANGELOG.md` plus `release_changelog.py`
  (`--release`/`--bump`/`--pre-release`/`--extract`) and the `com:release` skill manage versioning.

### Changed
- **Character roster externalised (code → data)** — the roster moved out of `paths.py` into a
  pack-excluded `docs/profiles/characters.yaml`; the shipped `paths.py` carries zero names and the
  public API is unchanged.
- **Docs, tests, and tools made name-free** — shipped prose, CLI examples, and fixtures use neutral
  placeholders (`character-a`, …) that resolve positionally against the local roster; real names live
  only in the pack-excluded corpus.
- **Framework-owned pack** — the manifest ships exactly the 6 domain agents + 6 framework hooks, and
  `settings.json` is filtered at build time to wire only those hooks, leaving no dangling references.
- **Profiles standardised** to the 25-file universal nested schema across all characters; the clinical
  reference library normalised to a single canonical heading schema.
- **Knowledge graph reimplemented in plain Python** — adjacency + centrality/community/path metrics,
  replacing the heavy ML stack.

### Removed
- **Heavy graph dependencies** — `networkx`, `numpy`, `pyvis`, and `sentence-transformers` dropped in
  favour of the plain-Python knowledge graph.
- **Dead code** — orphan `platform_lib` functions, legacy flat profile files, and a retired
  hook-dispatcher / standalone profile-validator removed in favour of single sources of truth.

### Security
- **No real-character PII ships** — names, profiles, materials, graph, and references are all
  pack-excluded; enforced by a non-removable safety filter at build time and verified by the
  no-carve-out scan over the built tarball.
