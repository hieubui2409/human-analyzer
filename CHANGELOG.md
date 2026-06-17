# Changelog

All notable changes to the **human-analyzer frameworks toolkit** are documented here.
The bundle ships 7 domain frameworks (ORC · PSY · CRE · GRO · MAT · COM · EVL) with their skills, domain
agents, and framework hooks. Tags `frameworks-v*` version the bundle as a whole.
Format: [keepachangelog.com](https://keepachangelog.com/en/1.1.0/). Versioning: [semver](https://semver.org/).

> **Release discipline.** During development, add entries under `## [Unreleased]`. On release, run
> `.claude/skills/_framework-shared/scripts/release.py --release X.Y.Z` (or `--bump {patch,minor,major}`): it locks
> `[Unreleased]` → `[X.Y.Z] — <date>`, opens a fresh empty `[Unreleased]`, and bumps
> `.claude/pack.manifest.yaml`. The locked section becomes the GitHub Release body. Nothing here is
> auto-derived from git at build time — this file is the human-curated truth of record.

## [Unreleased]
### Added
- **Bilingual 3D showcase site (`showcase/`).** A standalone, dependency-free static site — a stdlib-Python
  generator (`showcase/build.py`) assembles hand-authored EN/VI partials into a multipage docs site plus one
  portable single-file, with a Three.js network hero and a shadcn-inspired token system. 20 guides cover all
  7 frameworks, 68 skills, the event pipeline, gates, privacy, rubrics, subagents, internals, and distribution;
  honest-telemetry panels embed real stdout captured on the synthetic e2e fixture (no character corpus).
- **GitHub Pages deploy (`.github/workflows/pages.yml`).** A guarded workflow (runs only on the public toolkit
  repo) builds `showcase/` and deploys it to the repo's own GitHub Pages. Manifest globs project `showcase/**/*`
  + the workflow into the public mirror.

## [1.4.0] — 2026-06-14
### Added
- **EVL — 7th domain framework (evidence-cited rubric scoring engine).** Consumes MAT/PSY/GRO
  profiles and scores a character against pluggable, versioned rubrics → standardized scorecard +
  verdict. Engine modules under `platform_lib/evl_*.py` do deterministic gathering + weighted
  aggregation only; the LLM does per-criterion judgment. Every criterion cites a MAT evidence tier
  (T1–T5); an uncited score is reported `[UNVERIFIED]` (counted, never a silent pass). High-stakes
  rubrics use ≥2 independent judges → convergence (a divergence routes to manual review, never an
  auto-average). Ships 8 skills (`evl:score · standardize · fit · compatibility · compare · track ·
  validate · rubric-import`), 4 reference rubrics (Big Five+Dark Triad+attachment, role/casting fit,
  clinical risk & safety, relationship compatibility), and a rubric-importer agent. Event wiring:
  `PSY.refresh` / `GRO.assessed` → `EVL.rescore` → `EVL.scored` → `CRE.recalibrate` (acyclic; EVL is
  a forward-only sink — content may consume eval verdicts, eval never consumes content).
- **Decision register write side (`orc:decisions`).** Atomic allocated IDs + lock-serialised append +
  supersede lineage, so concurrent agents can record decisions without clobbering each other.
- **Three-class hook taxonomy.** Every hook carries `@hook-class telemetry|nudge|compliance`; an
  invariant gate asserts telemetry/nudge hooks never block a tool call.
- **Structural skill-eval gate** (`tests/golden/run_skill_evals.py`) — boolean checks of a skill's
  exit code / stdout / filesystem effect against the synthetic fixture, wired into CI.
- **Context-footprint gate.** Per-skill authored-size baseline + GATE-token co-presence check
  (every referenced `GATE-*` resolves to a full-prose definition).

### Changed
- `safety_filter` drops `.claude/decisions/` from the projected pack (the register holds
  character-tagged records).
- Red-team/validate discipline now applies the evidence bar **bidirectionally** — the plan's own
  settled open-decisions must cite `file:line` or carry `[UNVERIFIED]`, symmetric with findings.

## [1.3.0] — 2026-06-09
### Added
- **Bash write-guard speed-bump (gateguard).** A new `tool_name === "Bash"` branch catches naive
  LITERAL write-redirects into a sensitive profile path (`echo >`, `tee`, `sed -i`, `dd of=`, `cp`/`mv`,
  quoted targets) via the new `lib/bash-write-targets.cjs`. Explicitly a best-effort speed-bump, NOT a
  security boundary — non-literal writes (`$VAR`, `$(...)`, heredoc, inline interpreters) fail-open and
  are logged as `residual-allow` rather than silently allowed. Registered as a project-owned PreToolUse
  Bash group (no `_origin`); the CK Bash groups are untouched.
- **MultiEdit coverage** for `gateguard-profile-protect` + `pii-guard-on-write` + the PostToolUse
  telemetry matchers — MultiEdit to a CRITICAL/HIGH profile is now blocked/observed like Edit/Write.
- **Four more project hooks + two libs now ship** in the pack (`context-budget-gauge`,
  `emit-session-summary`, `track-script-execution`, `track-skill-invocation`, `lib/hook-logger.cjs`,
  `lib/bash-write-targets.cjs`) — the FOSS-clean project-owned set was previously incomplete in public.
- **`foss-pack-verify.cjs`** — a private drift gate that walks each shipped hook's require + non-require
  config-load closure (incl. `sensitivity-config.json`), asserts no CK lib is reachable, and asserts
  every telemetry/crash write-sink is gitignored in public. Kept private (not shipped).
- **`docs/scripts-infrastructure.md` now ships** — `CLAUDE.md` (shipped) points to it, so it belongs in
  the pack; it was created in 1.2.3 but never added to the manifest.

### Changed
- **Fail-open guards now leave a trace instead of going silently off.** `gateguard` + `pii-guard` (and
  the project hooks) route their outer catch AND the inner swallow-sites (corrupt config, flaky python
  helper, unparseable verdict) through a safe-required `hook-logger` — a missing logger degrades to a
  no-op (never fail-closed), and a chronically-crashing guard now surfaces in `.claude/hooks/.logs/`.
- **Every project hook is now disableable via `framework-config.json`** with a camelCase key, routed
  through one shared `lib/hook-config-utils.cjs::isHookEnabled` resolver (3 bespoke inline togglers
  unified; all 11 keys seeded). Public `.gitignore` now covers `.claude/hooks/.logs/`.
- **`.claude/hooks/docs/README.md` rewritten** into a full 28-hook audit table + FOSS-projection
  reference + guard-gap coverage matrix (with the non-negotiable Bash speed-bump caveat) + toggle-key
  reference.

### Fixed
- **`scan_pack_pii` framework-hook allow-list** updated to register the six newly-shipped hook/lib
  basenames — the independent ship-time backstop (intentionally not manifest-derived) was rejecting them
  as "non-framework hook must not ship".

## [1.2.3] — 2026-06-08
### Changed
- **`CLAUDE.md` minimalized (280 → 66 lines).** Restructured to a lean entry + a load-on-demand pointer
  index, mirroring the skill-folder pattern (entry `SKILL.md` + on-demand refs). Keeps only the
  every-turn essentials — purpose, architecture + event pipeline, operational notices. The 60-skill
  catalog (already auto-injected by the harness and grouped in `docs/MODULES.md`), the directory/profile
  schema (`docs/rules/01`), workflow tracks (`docs/rules/13`), and scripts infrastructure now load on
  demand. Nothing dropped — every moved section has a verified home.

### Added
- **`docs/scripts-infrastructure.md`** — extracted the `platform_lib/` module table + venv run commands
  from `CLAUDE.md` (the one moved section with no pre-existing home).

## [1.2.2] — 2026-06-08
### Removed
- **Per-version `RELEASE-NOTES-v<ver>.md` catalog + its generator.** The shipped `README.md` is the
  toolkit inventory and `CHANGELOG.md` is the release narrative (and the GitHub Release body), so the
  third artifact was pure duplication. Removing it also fixes two latent defects it carried: every
  release tarball shipped the single manifest-pinned `v1.0.0` notes regardless of its own version, and
  the catalog's "Highlights" block was hardcoded to the v1.0.0 feature set on every version.
- **Seven stale internal docs.** Removed `framework-overview.md`, `getting-started.md`,
  `quick-reference.md`, and `user-manual-{cre,mat,mpc,psy}.md` — superseded by the detailed bilingual
  `README.md`, the per-skill `GUIDE-EN/VI` docs, and the framework operating-guides. Several embedded
  real-character names as worked examples (kept them pack-excluded) and used the retired "MPC" framework
  name. The current navigation docs (`knowledge-architecture.md`, `MODULES.md`, `distilled-principles.md`)
  remain.

## [1.2.1] — 2026-06-08
### Changed
- **Relicensed MIT → AGPL-3.0.** Network/SaaS use of a modified version must release its full source
  under AGPL-3.0, deterring closed-source commercialization while keeping the toolkit open-source.
- **`LICENSE` + `CONTRIBUTING.md` now ship in the pack** (added to `pack.manifest.yaml`) and are shared
  single-source files synced from the canonical repo to the public mirror; the README links both.

## [1.2.0] — 2026-06-08
### Added
- **Toolkit-only deployment support** — `paths.find_project_root` now accepts
  `.claude/skills/_framework-shared` as a root marker alongside `docs/profiles`, so `platform_lib`
  resolves in a corpus-absent deployment (the public repo / a consumer pack). The test suite degrades
  cleanly there: corpus-coupled assertions and node-hook tests skip when their artifact is absent
  instead of failing.

### Changed
- **PII token registry** — registered collision-free third-party identifiers; documented why
  collision-prone bare given names are handled by context analysis rather than a literal token gate.

## [1.1.0] — 2026-06-07

### Added
- **Born-time PII write-guard** — a `PreToolUse Edit|Write|MultiEdit` hook (`pii-guard-on-write.cjs`)
  blocks a real-name token the moment it would be written into a shipped-class file, instead of only
  catching it at ship time. The judgment lives in `pii_guard_check.py`: a path is shipped-class iff it
  matches a manifest include glob and is not `safety_filter`-dropped (the pack-excluded corpus is
  dropped, so profile/material writes pass), and the written text is matched against the same
  collision-free scanner token set the ship scan uses (word-boundary, case-sensitive). Roster absent
  (consumer pack) ⇒ no-op; fail-open on any error. Framework-owned: ships and protects toolkit clones.

### Changed
- **`scan_pack_pii` is now a fail-closed backstop, not the only PII defense** — the born-time guard
  stops leaks at write; the whole-pack ship scan remains the no-carve-out final ratchet. Defense-in-depth.
- **Release-notes catalog counts are derived** — the "domain agents + framework hooks" line is computed
  from the live catalog instead of a hardcoded number, so adding a framework hook never drifts the prose.

## [1.0.1] — 2026-06-07

### Fixed
- **Release CI marks stable tags as full releases** — the prerelease flag is now derived from the
  semver suffix (after the `frameworks-v` prefix), not from the whole tag, which always contained the
  prefix `-`. Stable `frameworks-vX.Y.Z` publishes as a full release; only `…-rc.N` is a prerelease.
- **Reproducibility claim scoped to the build toolchain** — the changelog and release-notes no longer
  call the `.tar.gz` "byte-reproducible" across environments; the packed content (inner tar) is
  byte-identical everywhere, the archive is byte-identical within one toolchain (CI determinism-gated),
  and `SHA256SUMS` is the canonical reference.

## [1.0.0] — 2026-06-07

First public release of the clinical-grade character-profile intelligence toolkit: a privacy-safe,
reproducible pack of a coordinated 6-framework system that turns source materials into
evidence-backed psychological profiles and platform-native content — shipping **zero real-character data**.

### The system we ship

A whole ecosystem, not a loose script bag — six domain frameworks wired by an event bus
(`MAT → PSY → CRE`, with `GRO` and `ORC` cross-cutting), backed by a shared Python toolkit and a
deterministic, PII-safe packaging pipeline. The release tarball is reproducible within the build
toolchain (CI determinism-gated) and passes a fail-closed, no-carve-out whole-pack PII/secret scan.

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
- **Deterministic PII-safe release machinery** — `build_pack` (reproducible tarball + per-file SHA256
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
- **Deterministic release pack** — from the same source + manifest, `build_pack.py` produces a
  byte-identical tarball within one toolchain (sorted walk, fixed mtime/uid/gid; the packed content is
  byte-identical across environments, only the gzip framing varies by zlib), with a per-file SHA256
  `MANIFEST.json` embedded in the archive and a CI determinism gate over the build.
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

### Fixed
- **`roster_io` is now importable as a package submodule** — its `paths` import uses the dual
  package/top-level form, so the `platform_lib` import sweep (and any `platform_lib.roster_io` import)
  no longer fails with `No module named 'paths'`.
- **Project-script matrix and the profile-drift hook run without the project venv** — both hard-coded
  the venv interpreter and broke wherever it is absent (e.g. CI); they now fall back to the running
  interpreter / `python3` on `PATH`.

### Security
- **No real-character PII ships** — names, profiles, materials, graph, and references are all
  pack-excluded; enforced by a non-removable safety filter at build time and verified by the
  no-carve-out scan over the built tarball.

### CI
- **The framework gates now also run on push to `master`** — both `frameworks CI` and the
  `cross-framework bug_class gate` trigger on `master` pushes (not only pull request / manual dispatch),
  so a change that reaches `master` outside a PR is still gated.

## [1.0.0-rc.1] — 2026-06-07

_First public release candidate; superseded by [1.0.0] (same content plus the post-RC fixes listed there)._
