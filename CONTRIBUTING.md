# Contributing

Thanks for your interest! This repo is the **public framework toolkit**. Contributions to the skills,
scripts, rules, tests, and docs are welcome.

## The one hard rule — no PII, no private corpus

This repo must **never** contain:

- Real-person character profiles, materials, graph, or references (`docs/profiles/`, `docs/materials/`,
  `docs/graph/`, `docs/references/`).
- A character roster or PII token map (`characters.yaml`, `pii-tokens.yaml`).
- Real names or other personally identifying tokens in code, comments, tests, or commit messages.
- Proprietary third-party developer tooling.

CI **fails closed** on any of these (see `.github/workflows/public-ci-guard.yml`). The framework is
character-agnostic: tests use synthetic fixtures (`e2e/synthetic-project/`, `test-alpha`/`test-beta`),
never real subjects.

## Workflow

1. Fork + branch from `master`.
2. Make your change. Keep skills within their 4-doc spine (`SKILL.md` + `README.md` + `GUIDE-EN.md` +
   `GUIDE-VI.md`) and follow the patterns in [`CLAUDE.md`](./CLAUDE.md) + [`docs/rules/`](./docs/rules/).
3. Run the gates locally — they must be green:
   ```bash
   python -m pip install "pyyaml>=6.0,<7" "jsonschema>=4.0,<5" "pytest>=7,<9"
   PYTHONPATH=.claude/scripts python -m pytest tests/ -q -m "not gemini"
   PYTHONPATH=.claude/scripts python .claude/scripts/validate-all-against-schemas.py
   ```
4. Open a PR. The maintainer reviews, then cherry-picks framework-only commits into the canonical repo.

## Code conventions

- Scripts do **deterministic gathering**; the LLM does **heuristic judgment**. Don't bury reasoning in
  scripts.
- Keep code files focused (~200 lines); use kebab-case, descriptive names.
- No API keys, no network calls in tests or CI.
