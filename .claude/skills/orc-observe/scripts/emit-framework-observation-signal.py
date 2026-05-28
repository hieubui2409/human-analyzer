"""Emit a cross-framework observation SIGNAL to the project observation stream (B3).

GOLDEN RULE #4: deterministic append only. This validates + records a signal; it does
NOT decide what to observe — the calling skill (LLM) makes that judgment, this script just
persists it. Distinct from orc:event-log domain events (the cascade bus): observation
signals are passive telemetry (defense-pattern noticed, voice drift, low-CRAAP source),
written to a separate `.claude/telemetry/observations.jsonl` so they never trip cascades.

Per-framework signal vocabulary (ECC § B3) — extend deliberately, not ad-hoc:
  psy: core-wound | defense-pattern | attachment-shift | profile-touched
  mat: low-craap | contradiction | new-source | material-touched
  cre: voice-drift | evidence-violation | angle-found | content-touched
  gro: milestone | phase-transition | competency-delta | growth-touched
  orc: cascade-interrupt | routing-decision | session-event
  com: pii-match | governance-flag | commit

Usage:
  emit-framework-observation-signal.py --framework psy --signal defense-pattern \
      --payload '{"character":"hoa","note":"intellectualization in conflict"}' \
      [--source skill-name] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from platform_lib import paths  # noqa: E402
from platform_lib.errors import emit_error  # noqa: E402

OBSERVATIONS = paths.OBSERVATIONS

SIGNALS = {
    "psy": {"core-wound", "defense-pattern", "attachment-shift", "profile-touched"},
    "mat": {"low-craap", "contradiction", "new-source", "material-touched"},
    "cre": {"voice-drift", "evidence-violation", "angle-found", "content-touched"},
    "gro": {"milestone", "phase-transition", "competency-delta", "growth-touched"},
    "orc": {"cascade-interrupt", "routing-decision", "session-event"},
    "com": {"pii-match", "governance-flag", "commit"},
}
MAX_PAYLOAD_BYTES = 2048  # bounded — no signal flood / oversized payload


def emit(framework: str, signal: str, payload: dict, source: str) -> dict:
    fw = framework.lower()
    if fw not in SIGNALS:
        raise ValueError(f"unknown framework '{framework}' (expected {sorted(SIGNALS)})")
    if signal not in SIGNALS[fw]:
        raise ValueError(f"unknown {fw} signal '{signal}' (expected {sorted(SIGNALS[fw])})")
    raw = json.dumps(payload, ensure_ascii=False)
    if len(raw.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise ValueError(f"payload {len(raw)} bytes > {MAX_PAYLOAD_BYTES} cap")
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "framework": fw,
        "signal": signal,
        "source": source or "manual",
        "payload": payload,
    }
    OBSERVATIONS.parent.mkdir(parents=True, exist_ok=True)
    with OBSERVATIONS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description="Emit a framework observation signal (B3, deterministic append).")
    ap.add_argument("--framework", required=True)
    ap.add_argument("--signal", required=True)
    ap.add_argument("--payload", default="{}", help="JSON object")
    ap.add_argument("--source", default="manual")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        payload = json.loads(args.payload)
        if not isinstance(payload, dict):
            raise ValueError("--payload must be a JSON object")
        rec = emit(args.framework, args.signal, payload, args.source)
    except (ValueError, json.JSONDecodeError) as e:
        emit_error("validation", str(e))
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    if args.json:
        print(json.dumps(rec, ensure_ascii=False))
    else:
        print(f"✓ observation: {rec['framework']}/{rec['signal']} ← {rec['source']}")


if __name__ == "__main__":
    main()
