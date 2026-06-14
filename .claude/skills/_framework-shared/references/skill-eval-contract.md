# Skill Eval Contract — `evals.yaml` Schema and Checker Catalog

**Load when:** authoring or reviewing a skill's `evals.yaml`, or extending the checker set.

## Purpose

Any skill directory under `.claude/skills/` may contain an optional `evals.yaml` that
declares structural assertions about the skill's deterministic script output. The runner
`tests/golden/run_skill_evals.py` discovers these files, executes each declared check
as a boolean predicate, and exits non-zero if any check fails.

**This is not the golden value-equality runner.** `tests/golden/run_evals.py` freezes
scalar output values and diffs them (value-equality). The skill-eval runner here checks
*structural shape* — file produced, exit code, stdout key presence — without pinning
exact output values. Keep them conceptually separate.

| Runner | What it checks | Files |
|---|---|---|
| `run_evals.py` | Frozen golden values (value equality) | `tests/golden/evals.json` |
| `run_skill_evals.py` | Structural predicates (shape, existence) | `*/evals.yaml` (opt-in) |

---

## File Location

```
.claude/skills/{fw}-{skill}/evals.yaml
```

Skills without an `evals.yaml` are skipped silently (UNMAPPED is fine; not a FAIL).
Seed one file per skill only when a deterministic structural guarantee is worth
protecting. Do not backfill all skills.

---

## YAML Schema

```yaml
scenarios:
  - id: <string>              # unique, kebab-case, human-readable
    exec:                     # optional — argv for the script to run
      - "{py}"                # expands to the venv Python interpreter
      - "{repo}/.claude/skills/<fw>-<skill>/scripts/<script>.py"
      - "--flag"
    assertions:
      - id: <string>          # unique within the scenario
        check: <checker-name> # see catalog below
        # checker-specific fields (see catalog)
```

### Context placeholders in `exec` and `path` values

| Placeholder | Resolves to |
|---|---|
| `{py}` | Venv Python interpreter (same that runs the harness) |
| `{repo}` | Absolute path to the repo root |
| `{fixture}` | Absolute path to `PMC_PROJECT_ROOT` (synthetic fixture) |

---

## Checker Catalog

Each checker is a **boolean predicate** on `(exit_code, stdout, fs_state)`. Returns
`PASS` or `FAIL` with a detail string. An assertion naming an unknown checker is always
`FAIL` — misconfiguration is loud, never a silent skip.

### `file_exists`
Check that a file exists on disk.
```yaml
- id: output-produced
  check: file_exists
  path: /absolute/or/{fixture}/relative/path/to/file
```

### `file_absent`
Check that a path does NOT exist (e.g. no leaked temp file).
```yaml
- id: no-temp-leak
  check: file_absent
  path: /tmp/some-temp-file
```

### `exit_zero`
Check that the scenario's `exec` exited with code 0. Requires `exec` on the scenario.
```yaml
- id: exits-cleanly
  check: exit_zero
```

### `stdout_contains`
Check that the substring appears anywhere in stdout or stderr.
```yaml
- id: pass-verdict-printed
  check: stdout_contains
  substr: "PASS"
```

### `stdout_absent`
Check that the substring does NOT appear in stdout or stderr (no leaked secrets, no
unexpected error tokens).
```yaml
- id: no-error-token
  check: stdout_absent
  substr: "ERROR"
```

### `stdout_json`
Parse stdout as JSON and check that a dot-path key is present (and optionally equals
a value). Key presence alone is sufficient to verify structural shape.
```yaml
# key must be present and non-empty
- id: verdict-key-present
  check: stdout_json
  path: verdict

# key must equal a specific string value
- id: verdict-is-pass
  check: stdout_json
  path: verdict
  equals: "PASS"

# nested path
- id: nested-field
  check: stdout_json
  path: result.summary.count
```

---

## Verdict States

| Verdict | Meaning | Gates exit code? |
|---|---|---|
| `PASS` | Check succeeded | — |
| `FAIL` | Check failed — output doesn't match predicate | Yes (exit 1) |
| `SKIP` | Reserved for future `_gating: llm_advisory` — not currently emitted | No |
| `UNMAPPED` | Assertion has no `check` field (bare string or missing mapping) | No (unless `--strict`) |

With `--strict`, UNMAPPED also gates exit 1.

---

## Environment at Check Time

The runner sets:

```
PMC_PROJECT_ROOT = <absolute path to e2e/synthetic-project>
PYTHONPATH       = <repo>/.claude/scripts
CK_CACHE_DIR     = /tmp/ck-eval-runner-cache
```

Scripts must be deterministic under this environment. No network, no API keys.

---

## Authoring Checklist

Before adding an `evals.yaml`:

1. The skill script runs deterministically against `e2e/synthetic-project` with exit 0.
2. At least one `exit_zero` or `stdout_json` assertion is present (structural shape, not
   just "it ran").
3. Removing the expected output file (or corrupting the fixture) makes the gate exit 1.
4. The file is under 40 lines. If longer, the scenario count is too high — split or trim.
5. No plan/phase/finding codes in `id` fields — describe the invariant, not its origin.
