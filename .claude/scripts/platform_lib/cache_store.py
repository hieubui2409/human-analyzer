#!/usr/bin/env python3
"""cache_store — the shared content-addressed cache primitive.

ONE home for the cache mechanics that were re-implemented three times in-repo (KG cache content-hash,
profile-lite invalidation, instinct_store atomic write): content-hash keying + a CACHE_VERSION stamp +
atomic read-modify-write. `verdict_cache` and any future cache build on this; nobody re-rolls it.

Determinism + safety:
- `content_hash(text)` = sha256 of the UTF-8 body → reflects the body AS ON DISK (working tree), so an
  uncommitted edit changes the key (no stale-tree hit — the bug PSY-07 fixed for profile-lite).
- A `cache_version` mismatch is a FULL MISS (the safe direction: re-judge everything).
- Committed stores carry NO timestamp in entries → byte-stable for identical content (no commit churn).
- Writes are atomic (tmp + os.replace) so a crash mid-write never corrupts the store.
- The store keeps only caller-supplied values; it judges nothing (script-vs-LLM split).
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

from . import paths

CACHE_VERSION = "1"


def content_hash(text: str) -> str:
    """16-hex content fingerprint of `text` (sha256 of its UTF-8 bytes)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class CacheStore:
    """A single JSON cache file under the committed or runtime cache subtree.

    Schema: {"cache_version": "<v>", "entries": {"<key>": <value>}}. Values are opaque to the store.
    A version mismatch on load yields an empty store (full miss)."""

    def __init__(self, name: str, *, committed: bool = True, cache_version: str = CACHE_VERSION):
        self.name = name
        self.cache_version = cache_version
        base = paths.committed_cache_dir(name) if committed else paths.runtime_cache_dir(name)
        self.path = base / "cache.json"
        self._entries: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._entries = {}
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._entries = {}  # corrupt → full miss (safe)
            return
        if data.get("cache_version") != self.cache_version:
            self._entries = {}  # version bump → full miss (safe)
            return
        ent = data.get("entries")
        self._entries = ent if isinstance(ent, dict) else {}

    def get(self, key: str) -> Optional[Any]:
        """The cached value for `key`, or None on miss."""
        return self._entries.get(key)

    def put(self, key: str, value: Any) -> None:
        """Insert/replace `key` → `value` and persist atomically."""
        self._entries[key] = value
        self._flush()

    def put_many(self, items: dict[str, Any]) -> None:
        """Batch insert + one atomic write (collapses N writes; no mid-loop forgetting surface)."""
        self._entries.update(items)
        self._flush()

    def prune(self, live_keys: set[str]) -> int:
        """Drop entries whose key is not in `live_keys` (GC for deleted nodes). Returns count removed."""
        stale = [k for k in self._entries if k not in live_keys]
        for k in stale:
            del self._entries[k]
        if stale:
            self._flush()
        return len(stale)

    def _flush(self) -> None:
        payload = {"cache_version": self.cache_version, "entries": self._entries}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(tmp, self.path)  # atomic
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
