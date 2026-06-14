"""Gather raw content-angle SIGNALS from all source frameworks (deterministic, READ-ONLY).

GOLDEN RULE #4 split:
  - SCRIPT (here): over-gather raw signals from B5 event streams (date-filtered)
    + PSY growth-edges + GRO milestones + MAT recent materials. Each signal is
    tagged {source_framework, signal_type, character, summary, timestamp, freshness}.
    Pure reads + arithmetic. No angle quality judgment.
  - LLM (downstream): SYNTHESIZES candidate angles from these signals (title, hook,
    framing) -- then rank-angles-by-freshness-and-evidence.py scores them.

Freshness = recency decay over a window: 1.0 today -> 0.0 at/after --since-days.
Older-than-window signals are dropped (stale -> no stale angles, plan risk row).

Framework -> angle TYPE (the lens the signal feeds):
  PSY->emotional  MAT->story  GRO->professional  CRE->distribution  ORC->timing  EVL->evaluative

Usage:
  aggregate-angle-signals-across-frameworks.py --character <c>
      [--framework psy|mat|gro|cre|orc|evl|all] [--since-days 30] [--json]
READ-ONLY across every framework.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths
from platform_lib.markdown_parser import extract_sections, extract_milestones

# framework -> the angle lens its signals feed
FRAMEWORK_ANGLE = {
    "PSY": "emotional",
    "MAT": "story",
    "GRO": "professional",
    "CRE": "distribution",
    "ORC": "timing",
    # EVL emits EVL.scored when a scorecard is (re)written; an eval verdict/benchmark is a
    # legitimate content-angle source (eval→CRE is allowed; CRE→eval is not). The LLM synthesis
    # layer decides whether a given verdict makes a real, publishable angle.
    "EVL": "evaluative",
    # COM (governance/audit) is intentionally NOT a content-angle source — privacy scans, commit
    # logs and rule-compliance are not publishable angles. It is excluded from _frameworks() too.
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def freshness(ts: datetime, since_days: int, now: datetime | None = None) -> float:
    """Linear recency decay: 1.0 at now -> 0.0 at since_days old. Clamped [0,1]."""
    now = now or _now()
    age_days = (now - ts).total_seconds() / 86400.0
    if age_days <= 0:
        return 1.0
    if age_days >= since_days:
        return 0.0
    return round(1.0 - age_days / since_days, 4)


def _parse_ts(raw: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def _read_stream(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def event_signals(frameworks: list[str], character: str, since_days: int,
                  now: datetime | None = None) -> list[dict]:
    """One raw signal per recent B5 event in the selected framework streams.
    Red-team R-cross: summary derives from event reason, never raw payload."""
    now = now or _now()
    signals = []
    for fw in frameworks:
        stream = paths.EVENT_STREAMS.get(fw)
        if not stream:
            continue
        for ev in _read_stream(stream):
            if character and ev.get("character") not in (None, "", character):
                continue
            ts = _parse_ts(ev.get("timestamp", ""))
            if ts is None:
                continue
            fr = freshness(ts, since_days, now)
            if fr <= 0:
                continue
            signals.append({
                "source_framework": fw,
                "signal_type": FRAMEWORK_ANGLE.get(fw, "timing"),
                "character": ev.get("character") or character,
                "summary": ev.get("reason") or ev.get("event", ""),
                "origin": ev.get("event", ""),
                "timestamp": ev.get("timestamp", ""),
                "freshness": fr,
            })
    return signals


def _file_freshness(fp: Path, since_days: int, now: datetime | None = None) -> float:
    now = now or _now()
    if not fp.exists():
        return 0.0
    ts = datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc)
    return freshness(ts, since_days, now)


def psy_state_signals(character: str, since_days: int, now=None) -> list[dict]:
    """PSY growth-edges section headers -> emotional angle candidates."""
    fp = paths.character_dir(character) / "psychology" / "growth-edges.md"
    fr = _file_freshness(fp, since_days, now)
    if fr <= 0:
        return []
    return [{
        "source_framework": "PSY", "signal_type": "emotional", "character": character,
        "summary": head, "origin": "growth-edges.md",
        "timestamp": "", "freshness": fr,
    } for head in extract_sections(fp).keys()]


def gro_milestone_signals(character: str, since_days: int, now=None) -> list[dict]:
    """GRO milestones (ACHIEVED / IN_PROGRESS) -> professional angle candidates."""
    fp = paths.character_dir(character) / "milestones.md"
    fr = _file_freshness(fp, since_days, now)
    if fr <= 0:
        return []
    out = []
    for ms in extract_milestones(fp):
        if ms.get("status") not in ("ACHIEVED", "IN_PROGRESS"):
            continue
        out.append({
            "source_framework": "GRO", "signal_type": "professional", "character": character,
            "summary": ms["milestone"], "origin": "milestones.md",
            "timestamp": ms.get("date", ""), "freshness": fr,
        })
    return out


def mat_story_signals(character: str, since_days: int, now=None) -> list[dict]:
    """Recently-touched MAT materials -> story angle candidates."""
    mdir = paths.materials_dir(character)
    if not mdir.exists():
        return []
    out = []
    for fp in sorted(mdir.rglob("*.md")):
        fr = _file_freshness(fp, since_days, now)
        if fr <= 0:
            continue
        out.append({
            "source_framework": "MAT", "signal_type": "story", "character": character,
            "summary": fp.stem.replace("-", " "), "origin": fp.name,
            "timestamp": "", "freshness": fr,
        })
    return out


def aggregate(character: str, frameworks: list[str], since_days: int,
              now: datetime | None = None) -> list[dict]:
    char = paths.resolve_character(character)
    signals = event_signals(frameworks, char, since_days, now)
    if "PSY" in frameworks:
        signals += psy_state_signals(char, since_days, now)
    if "GRO" in frameworks:
        signals += gro_milestone_signals(char, since_days, now)
    if "MAT" in frameworks:
        signals += mat_story_signals(char, since_days, now)
    signals.sort(key=lambda s: -s["freshness"])
    return signals


def _frameworks(arg: str) -> list[str]:
    if arg == "all":
        return ["PSY", "MAT", "GRO", "CRE", "ORC", "EVL"]
    return [arg.upper()]


def main():
    ap = argparse.ArgumentParser(description="Gather raw angle signals across frameworks (READ-ONLY).")
    ap.add_argument("--character", required=True)
    ap.add_argument("--framework", default="all",
                    choices=["psy", "mat", "gro", "cre", "orc", "evl", "all"])
    ap.add_argument("--since-days", type=int, default=30, help="Freshness window (default 30)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    signals = aggregate(args.character, _frameworks(args.framework), args.since_days)
    out = {"character": paths.resolve_character(args.character),
           "framework": args.framework, "since_days": args.since_days,
           "signal_count": len(signals), "signals": signals}
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"{len(signals)} signals (window {args.since_days}d) for "
              f"{out['character']}:")
        for s in signals:
            print(f"  [{s['freshness']:.2f}] {s['source_framework']:>3}/{s['signal_type']:<12} "
                  f"{s['summary'][:54]}")


if __name__ == "__main__":
    main()
