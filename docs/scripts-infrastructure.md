# Scripts Infrastructure

Skills share a Python utility library + 60+ supportive scripts.

| Module (`.claude/scripts/platform_lib/`) | Purpose                                                         |
| ---------------------------------------- | --------------------------------------------------------------- |
| `paths.py`                               | Project root, character resolution, paths                       |
| `clinical_terms.py`                      | 80+ regex patterns, term scanning, ref indexing                 |
| `markdown_parser.py`                     | Section extraction, frontmatter, dates, links                   |
| `profile_stats.py`                       | File inventory, git hash cache validation                       |
| `formatters.py`                          | Markdown tables, JSON output, severity badges                   |
| `env_utils.py`                           | .env loading, API key resolution                                |
| `csv_search.py`                          | BM25 text search over CSV data                                  |
| `instinct_store.py`                      | Atomic learnings CRUD, confidence scoring, JSONL                |
| `telemetry.py`                           | Consolidated sink root + auto script-metrics + crash excepthook |
| `errors.py`                              | Structured error emission (errors.jsonl) over telemetry         |

Run scripts with the **project-local venv** (project is self-contained):

```bash
.claude/skills/.venv/bin/python3 .claude/skills/{framework}-{skill}/scripts/{script}.py [args]
bash .claude/skills/{framework}-{skill}/scripts/{script}.sh [args]
```

**Windows:** `.claude\skills\.venv\Scripts\python.exe .claude\skills\{framework}-{skill}\scripts\{script}.py`

**Design principle:** scripts do **deterministic gathering** (may over-flag — false positives expected); the LLM does **heuristic judgment**. Never delegate reasoning to scripts.
