"""Shared JSON Schema Draft-7 validation engine (C7).

GOLDEN RULE #4: deterministic gather + validate. Maps a file to its authoritative
Draft-7 schema by path/domain, parses frontmatter (YAML, nesting-preserving),
coerces date objects to ISO strings, and returns STRUCTURED violations
{file, field, rule, value}. No LLM, no heuristic — pure contract enforcement.

Consumed by validate-all-against-schemas.py (CI), psy:health-check, gro:validate,
orc:audit, and KG-06 (shared harness, no fork). The YAML schemas
(universal-profile-schema.yaml / material-schema.yaml) are now non-authoritative docs;
these .schema.json files are the source of truth.

Schema selection (by path):
  materials/**/*.md                       → material-frontmatter
  profiles/**/growth/competencies.md      → growth-competency
  profiles/**/growth/career-path.md       → growth-career-path
  profiles/**/psychology/formulation.md   → psychology-formulation
  profiles/**/psychology/diagnostics.md   → diagnostics
  profiles/**/*.md (other)                → profile-frontmatter
  session-state/*.jsonl (per line)        → event-jsonl
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, RefResolver

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# cache loaded validators by schema filename
_VALIDATOR_CACHE: dict[str, Draft7Validator] = {}


def _load_validator(schema_name: str) -> Draft7Validator:
    if schema_name in _VALIDATOR_CACHE:
        return _VALIDATOR_CACHE[schema_name]
    schema_path = SCHEMAS_DIR / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    # resolver lets allOf $ref reach sibling schema files (base profile schema)
    resolver = RefResolver(base_uri=schema_path.resolve().as_uri(), referrer=schema,
                           handlers={"file": lambda uri: json.loads(Path(uri[7:]).read_text("utf-8"))})
    validator = Draft7Validator(schema, resolver=resolver)
    _VALIDATOR_CACHE[schema_name] = validator
    return validator


def schema_for(path: Path) -> str | None:
    """Pick the authoritative schema for a file by its path. None = not covered."""
    s = path.as_posix()
    if path.suffix == ".jsonl":
        return "event-jsonl.schema.json"
    if "/materials/" in s and path.suffix == ".md":
        # INDEX.md is a per-character navigation catalog, not a CRAAP-scored source
        # material — exclude from material-frontmatter validation (like profile INDEX).
        if path.name == "INDEX.md":
            return None
        return "material-frontmatter.schema.json"
    if "/profiles/" in s and path.suffix == ".md":
        if path.parent.name == "growth":
            if path.stem == "competencies":
                return "growth-competency.schema.json"
            if path.stem == "career-path":
                return "growth-career-path.schema.json"
        if path.parent.name == "psychology":
            if path.stem == "formulation":
                return "psychology-formulation.schema.json"
            if path.stem == "diagnostics":
                return "diagnostics.schema.json"
        return "profile-frontmatter.schema.json"
    return None


def _stringify_dates(obj):
    """YAML turns unquoted ISO dates into date objects; coerce back to ISO strings
    so 'pattern' date constraints validate (and nested dicts/lists recurse)."""
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()[:10] if isinstance(obj, _dt.date) and not isinstance(obj, _dt.datetime) else obj.isoformat()
    if isinstance(obj, dict):
        return {k: _stringify_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_dates(v) for v in obj]
    return obj


def parse_frontmatter(path: Path) -> dict | None:
    """YAML frontmatter as a nested dict (preserves craap_score etc.). None if absent."""
    m = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    data = yaml.safe_load(m.group(1)) or {}
    return _stringify_dates(data)


def _violations(validator: Draft7Validator, instance: dict, file: str) -> list[dict]:
    out = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        field = ".".join(str(p) for p in err.path) or (
            err.message.split("'")[1] if "'" in err.message else "<root>")
        out.append({"file": file, "field": field, "rule": err.validator,
                    "value": err.instance if not isinstance(err.instance, dict) else "<object>",
                    "message": err.message})
    return out


def validate_file(path: Path) -> dict:
    """Validate one file against its schema. Returns {file, schema, status, violations}."""
    path = Path(path)
    schema_name = schema_for(path)
    if schema_name is None:
        return {"file": str(path), "schema": None, "status": "SKIP", "violations": []}
    validator = _load_validator(schema_name)

    if path.suffix == ".jsonl":
        violations = []
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                violations.append({"file": str(path), "field": f"line {i}", "rule": "json",
                                   "value": line[:40], "message": str(e)})
                continue
            for v in _violations(validator, rec, str(path)):
                v["field"] = f"line {i}:{v['field']}"
                violations.append(v)
    else:
        fm = parse_frontmatter(path)
        if fm is None:
            return {"file": str(path), "schema": schema_name, "status": "FAIL",
                    "violations": [{"file": str(path), "field": "<frontmatter>",
                                    "rule": "required", "value": None,
                                    "message": "no YAML frontmatter block"}]}
        violations = _violations(validator, fm, str(path))

    return {"file": str(path), "schema": schema_name,
            "status": "PASS" if not violations else "FAIL", "violations": violations}


def validate_paths(paths: list[Path]) -> list[dict]:
    """Validate many files; .jsonl handled per-line. Returns per-file results."""
    return [validate_file(p) for p in paths]
