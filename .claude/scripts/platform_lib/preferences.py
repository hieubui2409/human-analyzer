#!/usr/bin/env python3
"""preferences — read/write per-project engagement knobs (deterministic writer).

`.claude/cache/runtime/preferences.yaml` records project defaults so a skill does not re-ask the same
stylistic question each run. DEFAULTS only: a per-invocation flag still wins over the stored preference.

Closed enums + hard-coded defaults: a missing file, a missing key, an out-of-range value, or corrupt YAML
all resolve to the documented default and NEVER crash the caller. The writer (`--set KEY=VALUE`, repeatable)
validates against the closed enum and does a load→merge→save so it preserves every other committed key — an
unknown key OR an out-of-enum value exits non-zero, writing NOTHING (no silent typo no-op).

Separate from `.claude/framework-config.json` (structural wiring) — this is user-tunable behavior only.

Knobs (all optional in the file):
  crossref_rigor        light | standard | deep   (default standard) — how hard psy:crossref challenges the
                        LLM-judgment dimensions (depth of probing, not verbosity). Advisory: read LLM-side.
  cre_action_prompting  minimal | standard | proactive (default standard) — how many next-step suggestions
                        CRE skills offer at turn boundaries. Advisory: read LLM-side.
  humanize_strictness   high | balanced | conservative (default balanced) — how aggressively the
                        humanizer_patterns scanner flags AI-tells. The lib stays preference-agnostic (takes an
                        explicit `strictness` arg); cre:humanize + the CRE gates resolve this knob and pass it in.
This module only stores closed-enum values; it judges nothing (script-vs-LLM split).
"""

import argparse
import sys
from pathlib import Path

import yaml

if __package__ in (None, ""):
    import sys as _sys
    _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    from platform_lib import paths
else:
    from . import paths

DEFAULTS = {
    "crossref_rigor": "standard",
    "cre_action_prompting": "standard",
    "humanize_strictness": "balanced",
}
ENUMS = {
    "crossref_rigor": ["light", "standard", "deep"],
    "cre_action_prompting": ["minimal", "standard", "proactive"],
    "humanize_strictness": ["high", "balanced", "conservative"],
}


def _store_path() -> Path:
    return paths.runtime_cache_dir("preferences") / "preferences.yaml"


def load() -> dict:
    """Every knob resolved to its stored value or its default. Never raises."""
    resolved = dict(DEFAULTS)
    p = _store_path()
    if p.exists():
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            data = {}
        for k, v in data.items():
            if k in ENUMS and v in ENUMS[k]:
                resolved[k] = v
    return resolved


def _save(committed: dict) -> None:
    p = _store_path()
    p.write_text(yaml.safe_dump(committed, sort_keys=True, allow_unicode=True), encoding="utf-8")


def set_key(assignment: str) -> None:
    """Apply one `KEY=VALUE` via load→merge→save. Raises ValueError on unknown key / out-of-enum value
    (writing nothing)."""
    if "=" not in assignment:
        raise ValueError(f"expected KEY=VALUE, got {assignment!r}")
    key, value = assignment.split("=", 1)  # first '=' only
    key, value = key.strip(), value.strip()
    if key not in ENUMS:
        raise ValueError(f"unknown key {key!r}; known: {sorted(ENUMS)}")
    if value not in ENUMS[key]:
        raise ValueError(f"{value!r} not allowed for {key!r}; allowed: {ENUMS[key]}")
    # Merge over the committed file (NOT the defaults) so other keys survive.
    p = _store_path()
    committed = {}
    if p.exists():
        try:
            committed = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            committed = {}
    committed[key] = value
    _save(committed)


def main() -> int:
    ap = argparse.ArgumentParser(description="Read/write per-project engagement knobs.")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="set a knob (repeatable); validates closed enum, preserves other keys")
    ap.add_argument("--json", action="store_true", help="print resolved knobs as JSON")
    args = ap.parse_args()

    if args.set:
        for a in args.set:
            try:
                set_key(a)
            except ValueError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2  # write nothing on bad input
        print("ok: " + ", ".join(args.set))
        return 0

    resolved = load()
    if args.json:
        import json
        print(json.dumps(resolved, ensure_ascii=False, indent=2))
    else:
        for k, v in sorted(resolved.items()):
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
