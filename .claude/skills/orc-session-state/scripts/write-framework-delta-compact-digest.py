"""Strategic compact-digest — bounded per-framework delta written before /compact (C5).

GOLDEN RULE #4: deterministic gather only. Reads the B5 framework event streams + the B3
observation stream, keeps the top-N most-recent records per framework, and writes a bounded
digest to `.claude/session-state/compact-digest.json`. orc:bootstrap re-injects this digest
after compaction so the framework-delta context survives the boundary.

Project-owned replacement for ck's PreCompact marker — does NOT touch write-compact-marker.cjs.
The companion PreCompact hook (write-framework-delta-compact-digest.cjs) runs this automatically;
`orc:session-state --compact-digest` runs it manually.

Usage:
  write-framework-delta-compact-digest.py [--top-n 5] [--max-bytes 8000] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from platform_lib import paths  # noqa: E402

DIGEST = paths.SESSION_STATE / "compact-digest.json"  # session STATE, stays
OBSERVATIONS = paths.OBSERVATIONS  # consolidated telemetry sink

# Per-framework "keep" stream + the delta categories each contributes (ECC § C5).
FRAMEWORK_STREAMS = {
    "PSY": (paths.CHARACTER_EVENTS, "wave findings + formulation changes"),
    "MAT": (paths.MATERIAL_EVENTS, "materials ingested + tier assignments"),
    "CRE": (paths.CONTENT_EVENTS, "published pieces + voice-audit results"),
    "GRO": (paths.GROWTH_SIGNALS, "competency deltas + milestones"),
    "ORC": (paths.CASCADE_EVENTS, "event-log summary + routing decisions"),
    "COM": (paths.GOVERNANCE_AUDIT, "privacy/governance events"),
}
DEFAULT_TOP_N = 5
DEFAULT_MAX_BYTES = 8000  # bounded so the digest never defeats compaction


def _tail_jsonl(path: Path, n: int) -> list[dict]:
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
    return out[-n:]


def build_digest(top_n: int, max_bytes: int) -> dict:
    frameworks = {}
    for fw, (stream, category) in FRAMEWORK_STREAMS.items():
        recs = _tail_jsonl(stream, top_n)
        frameworks[fw] = {
            "category": category,
            "count": len(recs),
            # keep a compact pointer per record, not the full payload
            "recent": [
                {k: r.get(k) for k in ("ts", "event_type", "source", "character", "reason") if r.get(k)}
                for r in recs
            ],
        }
    observations = _tail_jsonl(OBSERVATIONS, top_n)
    digest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "top_n": top_n,
        "frameworks": frameworks,
        "observations": [
            {k: o.get(k) for k in ("ts", "framework", "signal", "source") if o.get(k)}
            for o in observations
        ],
    }
    # Enforce the byte cap: shrink top_n progressively if oversized.
    raw = json.dumps(digest, ensure_ascii=False)
    while len(raw.encode("utf-8")) > max_bytes and top_n > 1:
        top_n -= 1
        for fw in frameworks:
            frameworks[fw]["recent"] = frameworks[fw]["recent"][-top_n:]
        digest["observations"] = digest["observations"][-top_n:]
        digest["top_n"] = top_n
        digest["truncated"] = True
        raw = json.dumps(digest, ensure_ascii=False)
    return digest


def main() -> None:
    ap = argparse.ArgumentParser(description="Write a bounded per-framework compact-digest (C5).")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    digest = build_digest(args.top_n, args.max_bytes)
    DIGEST.parent.mkdir(parents=True, exist_ok=True)
    DIGEST.write_text(json.dumps(digest, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.json:
        print(json.dumps(digest, ensure_ascii=False))
    else:
        total = sum(f["count"] for f in digest["frameworks"].values())
        print(f"✓ compact-digest: {total} events across 7 frameworks + "
              f"{len(digest['observations'])} observations → {DIGEST.name} "
              f"({len(json.dumps(digest).encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
