"""Score-over-time tracking: snapshot diff + deterministic event attribution.

diff_scorecards compares two scorecard JSON snapshots (the current one and a prior
from eval/history/). attribute_changes joins profile-change events to a time window
by (character, timestamp) — a purely deterministic join, no inference. Narrating WHY
a score moved is the skill's LLM job; this script only lays the facts side by side.
"""
import json

from platform_lib.paths import CHARACTER_EVENTS, GROWTH_SIGNALS, MATERIAL_EVENTS
from platform_lib.evl_scorecard import scorecard_path


def _delta(a, b):
    """b - a, or None when either side is missing (a gap is not a zero change)."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return b - a
    return None


def diff_scorecards(prev: dict, curr: dict) -> dict:
    prev_dom = {d["id"]: d.get("score") for d in prev.get("domains", [])}
    domains = [{"id": d["id"], "prev": prev_dom.get(d["id"]), "curr": d.get("score"),
                "delta": _delta(prev_dom.get(d["id"]), d.get("score"))}
               for d in curr.get("domains", [])]
    pv, cv = prev.get("verdict"), curr.get("verdict")
    return {
        "overall_delta": _delta(prev.get("overall"), curr.get("overall")),
        "coverage_delta": _delta(prev.get("verified_coverage"), curr.get("verified_coverage")),
        "verdict_change": (pv, cv) if pv != cv else None,
        "domains": domains,
    }


def load_current(character: str, rubric_id: str) -> dict | None:
    p = scorecard_path(character, rubric_id, ".json")
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def load_history(character: str, rubric_id: str) -> list[dict]:
    """Prior snapshots from eval/history/, chronological by snapshot filename."""
    hist = scorecard_path(character, rubric_id, ".json").parent / "history"
    if not hist.is_dir():
        return []
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(hist.glob(f"{rubric_id}-*.json"))]


def attribute_changes(character: str, since_ts: str, event_paths=None) -> list[dict]:
    """Profile-change events at/after `since_ts` (ISO-Z string compare) potentially
    explaining a score delta. Deterministic join only — returns raw records for a
    human/LLM to correlate; it never infers causation.

    Character filtering is best-effort: the live event streams do NOT tag every record
    with a `character`, so a record is included when it has no character field (a
    repo-wide event in the window) OR its character matches. Filtering out untagged
    records would silently return nothing — the anti-pattern this engine forbids.
    Defaults to the PSY/GRO/MAT streams that drive a rescore; a missing log is skipped.
    """
    paths = event_paths if event_paths is not None else [
        CHARACTER_EVENTS, GROWTH_SIGNALS, MATERIAL_EVENTS]
    out = []
    for path in paths:
        if not path or not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (rec.get("timestamp") or "") < since_ts:
                continue
            rec_char = rec.get("character")
            if rec_char is None or rec_char == character:
                out.append(rec)
    out.sort(key=lambda r: r.get("timestamp", ""))
    return out
