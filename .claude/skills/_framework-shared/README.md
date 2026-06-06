# _framework-shared — project-owned cross-skill shared resources

Shared resources used by MORE THAN ONE framework skill (the cross-skill analogue of a single skill's
`references/`). Mirrors the `_shared/` convention, but project-owned (the 6 frameworks), distinct from the
ck-synced `_shared/`. The leading `_` keeps it out of skill enumeration (it is not a skill).

| Reference | Loaded by |
| --- | --- |
| `references/gates-and-anti-rationalization.md` | every turn (self-decision GATEs) |
| `references/verdict-cache-contract.md` | psy:crossref · cre:voice-audit · psy:propagate |
| `references/skill-doc-spine-template.md` | anyone authoring skill docs |

## `scripts/` — shared release/PII machinery

Cross-cutting executables (not a single skill's helpers): the deterministic pack build/scan, the
anonymizer, and the Keep a Changelog release lifecycle. Invoked by CI (`.github/workflows/`) and by the
`com:release` skill; imported by `mat:indexer` / `cre:privacy-guard` (for `pii_tokens`). Name-free — they
load real names at runtime from the pack-excluded corpus.

| Script | Role |
| --- | --- |
| `build_pack.py` | Deterministic, byte-reproducible pack tarball + embedded SHA256 manifest |
| `scan_pack_pii.py` | Fail-closed whole-pack PII/secret gate (no carve-out) |
| `safety_filter.py` | Non-removable include backstop (drops secrets/runtime/real-character PII) |
| `pii_tokens.py` | Shared PII token source (loads the pack-excluded roster; zero hardcoded names) |
| `mask_doc_names.py` | Doc-prose name masker (de-naming migration, run per-need) |
| `release_notes.py` | Deterministic RELEASE-NOTES catalog generator |
| `release.py` | Keep a Changelog lifecycle (`--extract`/`--release`/`--bump`/`--pre-release`) |
| `install.sh` | Consumer pack installer |
