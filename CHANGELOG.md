# Changelog

All notable changes to the **human-analyzer frameworks toolkit** are documented here.
The bundle ships 6 domain frameworks (ORC · PSY · CRE · GRO · MAT · COM) with their skills, domain
agents, and framework hooks. Tags `frameworks-v*` version the bundle as a whole.
Format: [keepachangelog.com](https://keepachangelog.com/en/1.1.0/). Versioning: [semver](https://semver.org/).

> **Release discipline.** During development, add entries under `## [Unreleased]`. On release, run
> `.claude/skills/_framework-shared/scripts/release.py --release X.Y.Z` (or `--bump {patch,minor,major}`): it locks
> `[Unreleased]` → `[X.Y.Z] — <date>`, opens a fresh empty `[Unreleased]`, bumps
> `.claude/pack.manifest.yaml`, and regenerates the deterministic `docs/RELEASE-NOTES-v<ver>.md`
> catalog. The locked section becomes the GitHub Release body. Nothing here is auto-derived from git
> at build time — this file is the human-curated truth of record.

## [Unreleased]

### Fixed
- **`roster_io` is now importable as a package submodule** — its `paths` import uses the dual
  package/top-level form, so the `platform_lib` import sweep (and any `platform_lib.roster_io` import)
  no longer fails with `No module named 'paths'`.

## [1.0.0-rc.1] — 2026-06-07

First public **release candidate** of the clinical-grade character-profile intelligence toolkit: a
privacy-safe, byte-reproducible pack of a coordinated 6-framework system that turns source materials into
evidence-backed psychological profiles and platform-native content — shipping **zero real-character data**.

### The system we ship

A whole ecosystem, not a loose script bag — six domain frameworks wired by an event bus
(`MAT → PSY → CRE`, with `GRO` and `ORC` cross-cutting), backed by a shared Python toolkit and a
deterministic, PII-safe packaging pipeline. The release tarball is byte-reproducible and passes a
fail-closed, no-carve-out whole-pack PII/secret scan.

- **6 domain frameworks · 60 skills** — ORC orchestration (17), PSY psychology (16), CRE content (10),
  GRO growth (8), MAT materials (4), COM common (5). Each is invoked as `{framework}:{skill}`; the
  frameworks own disjoint data locations and communicate through events, never cross-domain writes.
- **6 framework-owned domain agents** — `material-analyst` (MAT ingest/CRAAP), `psychologist` (PSY
  clinical formulation), `content-strategist` (CRE platform content), `growth-analyst` (GRO career/
  competency), `profile-manager` (profile CRUD/health), `cross-validator` (multi-character consistency).
- **6 framework hooks** — profile-drift detection, profile-write gate-guard, framework-signal
  observation, profile-edit reminder, knowledge-graph rebuild, and the compact-digest writer. The
  manifest ships exactly these; `settings.json` is filtered at build time to wire only them.
- **33 `platform_lib` modules · 16 rules · 9 schemas** — the shared utility library (paths/character
  resolution, clinical-term scanning, markdown parsing, telemetry, instinct store, …), the modular
  rulebook, and the validation schemas that keep the 25-file profile structure character-agnostic.
- **Deterministic PII-safe release machinery** — `build_pack` (byte-identical tarball + per-file SHA256
  `MANIFEST.json`), `scan_pack_pii` (fail-closed whole-pack gate), `safety_filter` (non-removable
  secret/PII drop), the doc/token anonymizer, and the Keep a Changelog release lifecycle.

The exhaustive per-item catalog (every skill/agent/hook/lib/rule/schema with its purpose) is generated
from the live tree into `docs/RELEASE-NOTES-v<ver>.md` at release-cut time.

### Added
- **6-framework toolkit** — ORC (orchestration), PSY (psychology), CRE (content), GRO (growth),
  MAT (materials), COM (common), wired by an event bus, with their 60 skills, 6 domain agents, and
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
- **Tag-triggered release CI** — pushing `frameworks-vX.Y.Z` runs the tag↔manifest assertion, the
  determinism gate, the PII gate, builds the pack, records SHA256SUMS, and publishes a GitHub Release
  whose body is this changelog's locked section (`-` in the tag marks it a prerelease).
- **Keep a Changelog lifecycle** — this `CHANGELOG.md` plus `release.py`
  (`--release`/`--bump`/`--pre-release`/`--extract`) and the `com:release` skill manage versioning;
  `release_notes.py` regenerates the exhaustive catalog from the live tree.

### Changed
- **Character roster externalised (code → data)** — the roster moved out of `paths.py` into a
  pack-excluded `docs/profiles/characters.yaml`; the shipped `paths.py` carries zero names and the
  public API is unchanged (positional `character-a`, … placeholders resolve against the local roster).
- **Docs, tests, and tooling made name-free** — shipped prose, CLI examples, and fixtures use neutral
  placeholders; real names (display, full, romanised slug) and org/location extras live only in the
  pack-excluded corpus (`docs/profiles/characters.yaml` + `docs/profiles/pii-tokens.yaml`).
- **Release/PII machinery consolidated** — the pack build, whole-pack scan, anonymizer, and release
  lifecycle moved into `.claude/skills/_framework-shared/scripts/`; the standalone `tools/` tree was
  removed so there is a single home for shared, framework-owned engineering.
- **Profiles standardised** to the 25-file universal nested schema across all characters; the clinical
  reference library normalised to a single canonical heading schema.
- **Knowledge graph reimplemented in plain Python** — adjacency + centrality/community/path metrics,
  replacing the heavy ML stack.

### Removed
- **Standalone `tools/` tree** — its pack/anonymize/release machinery relocated under
  `_framework-shared/scripts/`; nothing was lost, only re-homed.
- **Heavy graph dependencies** — `networkx`, `numpy`, `pyvis`, and `sentence-transformers` dropped in
  favour of the plain-Python knowledge graph.
- **Dead code** — orphan `platform_lib` functions, legacy flat profile files, and a retired
  hook-dispatcher / standalone profile-validator removed in favour of single sources of truth.

### Security
- **No real-character PII ships** — names, profiles, materials, graph, and references are all
  pack-excluded; enforced by a non-removable safety filter at build time and verified by the
  no-carve-out scan over the built tarball.
