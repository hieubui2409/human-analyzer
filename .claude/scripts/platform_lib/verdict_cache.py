#!/usr/bin/env python3
"""verdict_cache — re-runnable LLM-verdict cache for heuristic skills (crossref, voice-audit).

The SCRIPT half of the incremental-judgment optimization: it owns the key (verdict_cache_keys), the
hit/miss verdict, the store (cache_store), and the deleted-node GC. The LLM produces the verdict; this
module only keys, stamps, and compares it — it judges nothing (script-vs-LLM split). A miss is ALWAYS
safe (re-judge), so the gate never depends on a hit.

Confidentiality (Rule 09): a stored verdict is a LABEL only — `{label, score?, confidence?, ref?, note?}`
of SCALARS, total serialized size capped. It MUST NOT carry raw profile text. `record()` enforces that
structurally, so an accidental gather-bundle dump (raw clinical excerpts) cannot land in the committed
cache. This is why the committed cache is safe to commit.

Storage: `cache/committed/verdicts/cache.json` (content-addressed; stable for identical content).
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from .cache_store import CacheStore
from . import verdict_cache_keys as keys

# A stored verdict is a small label — scalar values only, bounded size. NOT an excerpt.
_ALLOWED_VERDICT_KEYS = frozenset({"label", "score", "confidence", "ref", "note", "dimension"})
_MAX_VERDICT_CHARS = 512


def _validate_verdict(verdict: Dict[str, Any]) -> None:
    if not isinstance(verdict, dict) or not verdict:
        raise ValueError("verdict must be a non-empty dict of scalar labels")
    bad = set(verdict) - _ALLOWED_VERDICT_KEYS
    if bad:
        raise ValueError(f"verdict keys {sorted(bad)} not allowed; use {sorted(_ALLOWED_VERDICT_KEYS)} "
                         f"(labels only — no raw profile text, Rule 09)")
    for k, v in verdict.items():
        if not isinstance(v, (str, int, float, bool)):
            raise ValueError(f"verdict[{k!r}] must be scalar (label/score), got {type(v).__name__}")
    if len(json.dumps(verdict, ensure_ascii=False)) > _MAX_VERDICT_CHARS:
        raise ValueError(f"verdict exceeds {_MAX_VERDICT_CHARS} chars — store a label, not an excerpt (Rule 09)")


class VerdictCache:
    def __init__(self, *, committed: bool = True):
        self.store = CacheStore("verdicts", committed=committed)

    def lookup(self, check: str, node_ids: List[str], bodies: Dict[str, str],
               lang: str = "vi", dep_text: str = "", fresh: bool = False) -> Optional[Dict[str, Any]]:
        """Cached verdict for (check, nodes) at the nodes' current on-disk content, or None on miss.
        NEVER_CACHED checks and `fresh=True` always miss (force re-judge)."""
        if fresh or check in keys.NEVER_CACHED:
            return None
        key = keys.compute_key(check, node_ids, bodies, lang, dep_text)
        return self.store.get(key)

    def record(self, check: str, node_ids: List[str], bodies: Dict[str, str], verdict: Dict[str, Any],
               lang: str = "vi", dep_text: str = "") -> bool:
        """Persist the LLM `verdict` (label only). Refuses NEVER_CACHED. Returns True if stored."""
        if check in keys.NEVER_CACHED:
            return False
        _validate_verdict(verdict)
        key = keys.compute_key(check, node_ids, bodies, lang, dep_text)
        self.store.put(key, verdict)
        return True

    def prune_to(self, live_node_ids: set) -> int:
        """GC entries whose referenced nodes are all gone (deleted-node cleanup)."""
        live = {k for k in self.store._entries
                if all(nid in live_node_ids for nid in keys.key_node_ids(k))}
        return self.store.prune(live)


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-runnable LLM-verdict cache (label-only, Rule-09 safe).")
    ap.add_argument("--check", required=True)
    ap.add_argument("--ids", required=True, help="comma-separated node ids")
    ap.add_argument("--bodies-file", required=True, help="JSON file mapping id -> current section text")
    ap.add_argument("--lang", default="vi")
    ap.add_argument("--dep-text", default="")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--store", help="JSON verdict label to record (omit to lookup only)")
    args = ap.parse_args()

    node_ids = [s for s in args.ids.split(",") if s]
    bodies = json.loads(open(args.bodies_file, encoding="utf-8").read())
    vc = VerdictCache()

    if args.store:
        ok = vc.record(args.check, node_ids, bodies, json.loads(args.store), args.lang, args.dep_text)
        print(json.dumps({"stored": ok, "check": args.check, "ids": node_ids}, ensure_ascii=False))
        return 0
    hit = vc.lookup(args.check, node_ids, bodies, args.lang, args.dep_text, fresh=args.fresh)
    print(json.dumps({"hit": hit is not None, "verdict": hit, "never_cached": args.check in keys.NEVER_CACHED},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
