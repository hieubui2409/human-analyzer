"""External evaluation framework → canonical rubric draft (offline, deterministic).

The script does STRUCTURE only: parse an external framework (markdown / json / yaml /
freeform text) into a loose criteria list, then scaffold a canonical rubric skeleton.
It NEVER invents a weight or an anchor (that would be score-theater) and NEVER drops a
source line it cannot classify — both surface in `_import_gaps`. The semantic mapping
(which external criterion → which canonical anchors/weights) is an input-isolated LLM
sub-agent's job; its proposal is passed back in via `mapping` and re-validated. A draft
with gaps fails schema validation by construction, so it cannot be scored until filled.

No network here: a URL's text is fetched by the skill and handed in as `text`.
"""
import json
import re

import yaml

from platform_lib import paths
from platform_lib.fs_guard import assert_under

_ITEM_RE = re.compile(r"^(#{2,6}|[-*]|\d+\.)\s+(.*)$")


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "x"


def _parse_md(text: str) -> dict:
    title, criteria, unclassified = None, [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# ") and title is None:
            title = line[2:].strip()
            continue
        m = _ITEM_RE.match(line)
        if m:
            criteria.append({"text": m.group(2).strip()})
        else:
            unclassified.append(line)
    return {"title": title, "criteria": criteria, "unclassified": unclassified}


def _normalize_struct(data) -> dict:
    if isinstance(data, list):
        items, title = data, None
    elif isinstance(data, dict):
        items, title = (data.get("criteria") or data.get("items") or []), data.get("title")
    else:
        items, title = [], None
    crits = []
    for it in items:
        if isinstance(it, str):
            crits.append({"text": it})
        elif isinstance(it, dict):
            t = it.get("text") or it.get("name") or it.get("title")
            if t:
                crits.append({"text": str(t)})
    return {"title": title, "criteria": crits, "unclassified": []}


def parse_external(text: str, fmt: str = "md") -> dict:
    """Loose {title, criteria:[{text}], unclassified:[str]} from external text."""
    fmt = (fmt or "md").lower()
    if fmt == "json":
        return _normalize_struct(json.loads(text))
    if fmt == "yaml":
        return _normalize_struct(yaml.safe_load(text))
    if fmt == "freeform":
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return {"title": None, "criteria": [{"text": ln} for ln in lines], "unclassified": []}
    return _parse_md(text)


def scaffold_canonical(parsed: dict, meta: dict) -> dict:
    """Canonical skeleton with TODO placeholders — nothing invented."""
    criteria = [{
        "id": _slug(c["text"])[:48],
        "text": c["text"].strip(),
        "weight": None,        # NEVER invented — a human/agent must author
        "anchors": {},         # NEVER invented
        "evidence_hint": [],
        "min_tier": None,
    } for c in parsed.get("criteria", [])]
    return {
        "id": meta.get("id") or _slug(parsed.get("title") or "imported-rubric"),
        "version": "0.0.0",                       # draft sentinel (semver-shaped)
        "title": parsed.get("title") or meta.get("title") or "Imported Rubric",
        "kind": meta.get("kind", "decision"),
        "subject": meta.get("subject", "single"),
        "verdict": "scalar",
        "cache": "allow",
        "normalization": "none",
        "min_judges": 1,
        "scale": {"min": 0, "max": 5},
        "aggregate": "weighted_mean",
        "status": "draft",
        "needs_human_review": True,
        "domains": [{"id": "imported", "weight": 1.0, "criteria": criteria}],
        "_unclassified": list(parsed.get("unclassified", [])),
        "_source": meta.get("source"),
    }


def _apply_mapping(rubric: dict, mapping: dict) -> None:
    for d in rubric["domains"]:
        for c in d["criteria"]:
            proposal = mapping.get(c["id"])
            if not proposal:
                continue
            for field in ("weight", "anchors", "evidence_hint", "min_tier"):
                if field in proposal:
                    c[field] = proposal[field]


def _detect_gaps(rubric: dict) -> list[str]:
    gaps = []
    for d in rubric["domains"]:
        for c in d["criteria"]:
            miss = []
            if c.get("weight") is None:
                miss.append("weight")
            if len(c.get("anchors") or {}) < 2:
                miss.append("anchors")
            if not c.get("min_tier"):
                miss.append("min_tier")
            if not c.get("evidence_hint"):
                miss.append("evidence_hint")
            if miss:
                gaps.append(f"criterion '{c['id']}': needs {', '.join(miss)}")
    for u in rubric.get("_unclassified", []):
        gaps.append(f"unclassified source (not dropped): {u[:80]!r}")
    return gaps


def import_rubric(text: str, meta: dict, mapping: dict = None, fmt: str = "md") -> tuple[dict, list]:
    """Parse + scaffold (+ apply an agent mapping) → (draft rubric, gaps)."""
    rubric = scaffold_canonical(parse_external(text, fmt), meta)
    if mapping:
        _apply_mapping(rubric, mapping)
    rubric["_import_gaps"] = _detect_gaps(rubric)
    return rubric, rubric["_import_gaps"]


def write_draft(rubric: dict, name: str):
    """Write the draft to docs/rubrics/imported/<name>.yaml (EVL-fenced)."""
    path = paths.RUBRICS / "imported" / f"{_slug(name)}.yaml"
    assert_under(path, "EVL")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(rubric, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
