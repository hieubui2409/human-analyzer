"""Standardized scorecard emitter — renders an aggregate result to md + json.

JSON is the source of truth (machine-readable, round-trips); the markdown is a
human view derived from it. The honesty surface is deliberately prominent: the
coverage headline and the UNVERIFIED list sit at the top of the report, never
buried. Writes are fenced under docs/profiles/{char}/eval/ only (Rule 12 / EVL
zone) and a clinical (cache:never) scorecard is stamped reassess_required so a
stale risk verdict is never mistaken for a standing one.
"""
import json
from pathlib import Path

from platform_lib.formatters import markdown_table
from platform_lib.fs_guard import FenceError, assert_under
from platform_lib.paths import character_dir


def scorecard_path(character: str, rubric_id: str, suffix: str = ".md"):
    return character_dir(character) / "eval" / f"{rubric_id}{suffix}"


def _fmt(n) -> str:
    return "—" if n is None else (f"{n:g}" if isinstance(n, (int, float)) else str(n))


def _confidence(cov: float) -> str:
    return "high" if cov >= 0.8 else "medium" if cov >= 0.5 else "low"


def render_scorecard(rubric: dict, result: dict, meta: dict) -> tuple[str, dict]:
    data = _build_json(rubric, result, meta)
    return _build_md(rubric, result, data), data


def _build_json(rubric: dict, result: dict, meta: dict) -> dict:
    reassess = rubric.get("kind") == "clinical" or rubric.get("cache") == "never"
    return {
        "rubric_id": rubric.get("id"),
        "rubric_version": rubric.get("version"),
        "rubric_title": rubric.get("title"),
        "kind": rubric.get("kind"),
        "subject": rubric.get("subject"),
        "character": meta.get("character"),
        "overall": result.get("overall"),
        "verdict": result.get("verdict"),
        "verified_coverage": result.get("verified_coverage", 0.0),
        "scale": rubric.get("scale"),
        "domains": result.get("domains", []),
        "criteria": meta.get("criteria", []),
        "unverified": result.get("unverified", []),
        "below_min_tier": result.get("below_min_tier", []),
        "cache": rubric.get("cache", "allow"),
        "reassess_required": reassess,
        "judges": meta.get("judges"),
        "convergence": meta.get("convergence"),
        "normalization": meta.get("normalization"),
        "asof": meta.get("asof"),
        "updated_by": meta.get("updated_by", "evl:score"),
    }


def _frontmatter(data: dict) -> str:
    cov_pct = round(data["verified_coverage"] * 100)
    lines = [
        "---",
        f"character: {data['character']}",
        "domain: eval",
        "type: data",
        f"rubric: {data['rubric_id']}",
        f"rubric_version: {data['rubric_version']}",
        f"verdict: {data['verdict'] or 'scalar'}",
        f"overall: {_fmt(data['overall'])}",
        f"coverage: {cov_pct}",
        f"confidence: {_confidence(data['verified_coverage'])}",
        f"cache: {data['cache']}",
    ]
    if data["reassess_required"]:
        lines.append("reassess_required: true")
    lines += [f"last_updated: \"{data['asof']}\"", f"updated_by: {data['updated_by']}", "---"]
    return "\n".join(lines)


def _build_md(rubric: dict, result: dict, data: dict) -> str:
    smax = rubric["scale"]["max"]
    crits = data["criteria"]
    total = len(crits)
    n_ver = total - len(data["unverified"]) - len(data["below_min_tier"])
    cov_pct = round(data["verified_coverage"] * 100)

    out = [_frontmatter(data), "",
           f"# Scorecard — {data['rubric_title']} ({data['rubric_id']} v{data['rubric_version']})", "",
           f"**Overall: {_fmt(data['overall'])}/{_fmt(smax)} — "
           f"{data['verdict'] or '(scalar score)'}** · "
           f"Coverage: {cov_pct}% (verified {n_ver}/{total})", ""]

    if data["reassess_required"]:
        out += ["> ⚠ **cache: never** — this verdict is point-in-time; re-score every run. "
                "Not a standing assessment.", ""]

    by_id = {c.get("criterion_id"): c for c in crits}
    if data["unverified"]:
        out += [f"## ⚠ Unverified ({len(data['unverified'])}) — excluded from the score", ""]
        out += [f"- `{cid}` — {by_id.get(cid, {}).get('justification', 'no valid citation')}"
                for cid in data["unverified"]] + [""]
    if data["below_min_tier"]:
        out += [f"## ⚠ Below minimum tier ({len(data['below_min_tier'])}) — excluded", ""]
        out += [f"- `{cid}` — cited evidence weaker than the criterion's minimum tier"
                for cid in data["below_min_tier"]] + [""]

    out += ["## Domains", "",
            markdown_table(["Domain", "Weight", "Score", "Coverage"],
                           [[d["id"], _fmt(d["weight"]), _fmt(d["score"]),
                             f"{round(d['coverage'] * 100)}%"] for d in data["domains"]]), ""]

    out += ["## Criteria", ""]
    for c in crits:
        cid = c.get("criterion_id")
        if cid in data["unverified"]:
            out.append(f"- `{cid}` — **[UNVERIFIED]** — {c.get('justification', '')}")
        else:
            out.append(f"- `{cid}` — {_fmt(c.get('score'))}/{_fmt(smax)} "
                       f"[{c.get('tier') or '?'}] — {c.get('citation') or '—'} — "
                       f"{c.get('justification', '')}")
    return "\n".join(out) + "\n"


def _assert_eval_zone(path):
    """EVL only ever touches an eval/ subtree — refuse any other profile path.
    Checks the RESOLVED path so a `eval/../../x` traversal can't satisfy the marker."""
    if "eval" not in Path(path).resolve(strict=False).parts:
        raise FenceError(f"EVL refuses to write outside an eval/ subtree: {path}")
    return path


def write_scorecard(character: str, rubric: dict, result: dict, meta: dict):
    """Write {rubric-id}.md + .json under the character's eval/; snapshot any prior
    json into eval/history/. Returns the markdown path."""
    md, data = render_scorecard(rubric, result, meta)
    md_path = scorecard_path(character, rubric["id"], ".md")
    json_path = scorecard_path(character, rubric["id"], ".json")
    for p in (md_path, json_path):
        assert_under(_assert_eval_zone(p), "EVL")
    md_path.parent.mkdir(parents=True, exist_ok=True)

    if json_path.exists():
        hist = md_path.parent / "history"
        assert_under(hist, "EVL")
        hist.mkdir(exist_ok=True)
        snap = hist / f"{rubric['id']}-{data.get('asof', 'prior')}.json"
        snap.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    return md_path
