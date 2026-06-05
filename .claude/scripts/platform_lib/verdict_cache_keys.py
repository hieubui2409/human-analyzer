#!/usr/bin/env python3
"""verdict_cache_keys — deterministic cache-key grammar for re-runnable LLM verdicts.

Pure + deterministic (no I/O, no clock). Owns the key grammar only; `verdict_cache` owns the store.

Key grammar:  ``check | scope_key | hashes | lang | dep_hash``
  - single-node check: scope_key = node_id, hashes = content_hash(body)
  - pair check:        scope_key = the two ids SORTED + joined, hashes = the two content_hashes in the
                       same sorted order → the pair is unordered ((A,B) == (B,A)).
  - dep-bearing check: stamps dep_hash = ``dep:<hash(dep_text)>`` so a change in a PARENT artifact (e.g.
                       a character's CURRENT-STATE) invalidates a child verdict even when the child body
                       is byte-identical.

Safety:
  - NEVER_CACHED checks (crisis_assess, narrative_twist, contradiction) have NO key — a safety verdict
    against a profile/approved artifact MUST re-run every time. compute_key refuses them.
  - A `CACHE_VERSION` (shared with cache_store) means a key-grammar/semantics change is a full miss.
  - The hash is content_hash of the body AS ON DISK (working tree) → an uncommitted edit changes the key
    (no stale-tree hit — the class of bug the profile-lite cache fixed for git-hash-only validity).
"""

import hashlib
from typing import Dict, List, Optional

from .cache_store import content_hash

# Safety-critical verdicts that must ALWAYS re-run — never keyed, never cached.
NEVER_CACHED = frozenset({"crisis_assess", "narrative_twist", "contradiction"})

# Checks keyed on an unordered SORTED id pair (e.g. cross-character consistency dimensions).
PAIR_CHECKS = frozenset({"relationship_consistency", "timeline_pair", "linguistic_voice_pair"})


def _body_hash(node_id: str, bodies: Dict[str, str]) -> str:
    """content_hash of the node's body, or a stable 'missing' sentinel (always-miss, safe)."""
    body = bodies.get(node_id)
    return content_hash(body) if isinstance(body, str) else "missing"


def dep_segment(dep_text: str) -> str:
    """The dep_hash segment: ``dep:<8hex>`` of the parent dependency text, or empty when none."""
    if not dep_text:
        return ""
    return "dep:" + hashlib.sha256(dep_text.encode("utf-8")).hexdigest()[:8]


def compute_key(check: str, node_ids: List[str], bodies: Dict[str, str],
                lang: str = "vi", dep_text: str = "") -> str:
    """Compose the deterministic cache key for `check` over `node_ids`.

    `bodies` maps node_id → its current on-disk section text. Refuses NEVER_CACHED checks.
    Pair checks require exactly 2 ids (sorted); single-node checks require exactly 1."""
    if check in NEVER_CACHED:
        raise ValueError(f"{check!r} is never cached (safety verdict) — no key")

    if check in PAIR_CHECKS:
        if len(node_ids) != 2:
            raise ValueError(f"{check!r} is a pair check; got {len(node_ids)} ids")
        a, b = sorted(node_ids)
        scope_key = f"{a}+{b}"
        hashes = f"{_body_hash(a, bodies)}+{_body_hash(b, bodies)}"
    else:
        if len(node_ids) != 1:
            raise ValueError(f"{check!r} is a single-node check; got {len(node_ids)} ids")
        nid = node_ids[0]
        scope_key = nid
        hashes = _body_hash(nid, bodies)

    return f"{check}|{scope_key}|{hashes}|{lang}|{dep_segment(dep_text)}"


def key_node_ids(key: str) -> List[str]:
    """The node ids a key references (1 single, 2 for a '+'-joined pair) — for GC, no per-check knowledge."""
    parts = key.split("|")
    if len(parts) < 2:
        return []
    scope = parts[1]
    return scope.split("+") if "+" in scope else [scope]
