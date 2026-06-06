# Changelog

All notable changes to the human-analyzer frameworks toolkit. Format follows [Keep a Changelog](https://keepachangelog.com/); this project adheres to semantic versioning.

## [1.0.0] - 2026-06-06

### Added
- First official release of the 6-framework toolkit: 59 skills, 6 domain agents, 6 framework hooks, 33 platform-lib modules, 16 rules, 11 schemas.
- New-character registration flow + roster↔profile drift invariant.
- Deterministic, byte-reproducible release pack with a fail-closed whole-pack PII/secret scan.
- `tools/release/generate_changelog.py` — deterministic, PII-clean catalog generator.

### Changed
- Character roster externalised from `paths.py` to a pack-excluded `characters.yaml` (public `paths.py` API unchanged).
- Pack manifest narrowed to framework-owned agents/hooks; `settings.json` filtered at build time to wire only framework hooks (no dangling references).

### Security
- No real-character PII (names, profiles, materials, graph, references) ships in the pack; verified by a no-carve-out scan over the built tarball.

See `docs/RELEASE-NOTES-v1.0.0.md` for the exhaustive catalog.
