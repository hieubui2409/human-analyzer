# human-analyzer — framework toolkit

A **character-profile intelligence toolkit** for storytelling and content creation, packaged as a set
of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills. It models a subject as a deep,
evidence-backed psychological profile and turns that profile into platform-native content — all driven
by deterministic scripts + LLM judgment, wired together by an event bus.

> This is the **public toolkit**. It ships with **no real-person profiles** — the character corpus is
> private by design. Bring your own subjects: the tooling is character-agnostic and resolves them
> dynamically from `docs/profiles/characters.yaml` (absent here; create your own).

## The six frameworks

| Framework | Domain | Purpose |
| --- | --- | --- |
| **MAT** | Materials | Evidence ingestion, tiers (T1–T5), CRAAP scoring |
| **PSY** | Psychology | Clinical profiling, 5P formulation, references |
| **CRE** | Content | Platform-native content creation |
| **GRO** | Growth | Career + competency intelligence |
| **ORC** | Orchestration | Event routing, cascades, domain boundaries |
| **COM** | Common | Git, health-check, rules, analytics, release |

Pipeline: `MAT (input) → PSY (analysis) → CRE (output)`, with `GRO` feeding PSY/CRE and `ORC`
coordinating. See [`CLAUDE.md`](./CLAUDE.md) for the architecture, rules, and skill catalog, and
[`docs/`](./docs/) for the rule files + navigation maps.

## Quick start

```bash
# 1. install the Python deps the skills use
python -m pip install "pyyaml>=6.0,<7" "jsonschema>=4.0,<5" "pytest>=7,<9"

# 2. run the deterministic gates (no API key, no network)
PYTHONPATH=.claude/scripts python -m pytest tests/ -q -m "not gemini"

# 3. build the distributable pack
python .claude/skills/_framework-shared/scripts/build_pack.py
```

With no character roster present, corpus-dependent tests skip cleanly — the toolkit still imports,
compiles, and builds.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). The one hard rule: **never commit real-person profiles,
PII, or proprietary tooling** — CI fails closed on it.

## License

[MIT](./LICENSE).
