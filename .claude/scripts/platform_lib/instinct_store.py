"""Instinct store — atomic learnings with confidence scoring and JSONL persistence.

Shared module for orc:compounding (capture), orc:dream (lifecycle), orc:agent-memory (display).
"""

import argparse
import json
import math
import os
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from platform_lib.paths import ROOT, INSTINCTS
from platform_lib.formatters import json_output

INSTINCT_FILE = INSTINCTS

AGENT_CATEGORY_MAP = {
    "psychologist": ["psychology", "clinical"],
    "content-strategist": ["writing", "audience"],
    "growth-analyst": ["growth"],
}

VALID_CATEGORIES = ["psychology", "writing", "audience", "clinical", "growth", "process"]
VALID_STATUSES = ["active", "archived"]


def _disp(text, width=140):
    """Truncate stored full text for one-line display (storage stays full — LIB-14)."""
    text = str(text)
    return text if len(text) <= width else text[:width - 1].rstrip() + "…"


def create_instinct(text, category, confidence=0.5, source_session="", tags=None):
    """Create instinct dict with unique ID and defaults."""
    now = datetime.now(timezone.utc)
    pinned = category == "process"
    return {
        "id": f"instinct-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}-{token_hex(3)}",
        # Store the FULL text — truncating here made two learnings that share the first
        # 140 chars dedup as identical in find_similar(). Truncation is a display concern.
        "text": text.strip(),
        "category": category,
        "confidence": round(min(max(confidence, 0.0), 1.0), 4),
        "evidence_count": 1,
        "last_reinforced": now.isoformat(),
        "created_at": now.isoformat(),
        "source_session": source_session,
        "tags": tags or [],
        "status": "active",
        "pinned": pinned,
    }


def append_instinct(instinct):
    """Append single instinct to JSONL file."""
    INSTINCT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INSTINCT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(instinct, ensure_ascii=False, default=str) + "\n")


def load_instincts(status=None):
    """Load instincts from JSONL, optionally filtered by status.

    Skips malformed lines with stderr warning. Warns if count > 200.
    """
    if not INSTINCT_FILE.exists():
        return []
    results = []
    with open(INSTINCT_FILE, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                inst = json.loads(line)
            except json.JSONDecodeError:
                print(f"WARNING: malformed JSONL line {line_num}, skipping", file=sys.stderr)
                continue
            if status is None or inst.get("status") == status:
                results.append(inst)
    if len(results) > 200:
        print(f"WARNING: {len(results)} instincts loaded (>200) — consider running orc:dream", file=sys.stderr)
    return results


def _atomic_rewrite(instincts):
    """Rewrite entire JSONL atomically via temp file + os.replace."""
    INSTINCT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(INSTINCT_FILE.parent), suffix=".tmp", prefix="instincts-"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for inst in instincts:
                f.write(json.dumps(inst, ensure_ascii=False, default=str) + "\n")
        os.replace(tmp_path, str(INSTINCT_FILE))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def reinforce(instinct_id, boost=0.15):
    """Reinforce instinct confidence: conf_new = conf_old + (1 - conf_old) * boost.

    Raises KeyError if ID not found. Raises ValueError if instinct is archived.
    """
    all_instincts = load_instincts()
    found = None
    for inst in all_instincts:
        if inst["id"] == instinct_id:
            found = inst
            break
    if found is None:
        raise KeyError(f"Instinct not found: {instinct_id}")
    if found.get("status") != "active":
        raise ValueError(f"Cannot reinforce non-active instinct: {instinct_id}")
    old_conf = found["confidence"]
    found["confidence"] = round(old_conf + (1 - old_conf) * boost, 4)
    found["evidence_count"] = found.get("evidence_count", 1) + 1
    found["last_reinforced"] = datetime.now(timezone.utc).isoformat()
    _atomic_rewrite(all_instincts)
    return found


def apply_decay(lambda_=0.05):
    """Apply exponential decay to all active, non-pinned instincts.

    conf_decayed = conf * e^(-lambda * days_since_reinforcement)
    Returns list of decayed instincts (those whose confidence changed).
    """
    all_instincts = load_instincts()
    now = datetime.now(timezone.utc)
    decayed = []
    for inst in all_instincts:
        if inst.get("status") != "active" or inst.get("pinned", False):
            continue
        last = datetime.fromisoformat(inst["last_reinforced"])
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        days = (now - last).total_seconds() / 86400
        if days < 0.5:
            continue
        old_conf = inst["confidence"]
        new_conf = round(old_conf * math.exp(-lambda_ * days), 4)
        if abs(new_conf - old_conf) > 0.001:
            inst["confidence"] = new_conf
            decayed.append(inst)
    if decayed:
        _atomic_rewrite(all_instincts)
    return decayed


def archive_stale(conf_threshold=0.4, days_threshold=30):
    """Archive instincts below confidence threshold and unreinforced for N days.

    Pinned instincts (process category) are exempt.
    """
    all_instincts = load_instincts()
    now = datetime.now(timezone.utc)
    archived = []
    for inst in all_instincts:
        if inst.get("status") != "active" or inst.get("pinned", False):
            continue
        last = datetime.fromisoformat(inst["last_reinforced"])
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        days = (now - last).total_seconds() / 86400
        if inst["confidence"] < conf_threshold and days >= days_threshold:
            inst["status"] = "archived"
            archived.append(inst)
    if archived:
        _atomic_rewrite(all_instincts)
    return archived


def find_similar(text, threshold=0.85):
    """Find similar instincts using Jaccard token overlap.

    Returns list of (instinct, similarity) tuples above threshold.
    """
    query_tokens = set(text.lower().split())
    if not query_tokens:
        return []
    active = load_instincts(status="active")
    results = []
    for inst in active:
        inst_tokens = set(inst["text"].lower().split())
        if not inst_tokens:
            continue
        intersection = len(query_tokens & inst_tokens)
        union = len(query_tokens | inst_tokens)
        similarity = intersection / union if union > 0 else 0
        if similarity >= threshold:
            results.append((inst, round(similarity, 3)))
    return sorted(results, key=lambda x: x[1], reverse=True)


def get_promotion_candidates(conf_min=0.80, evidence_min=3):
    """Get instincts eligible for promotion to persistent knowledge."""
    active = load_instincts(status="active")
    return [
        inst for inst in active
        if inst["confidence"] >= conf_min and inst.get("evidence_count", 1) >= evidence_min
    ]


_IMMUTABLE_FIELDS = frozenset(["id", "created_at"])


def update_instinct(instinct_id, **fields):
    """Update instinct fields by ID. Raises KeyError if not found, ValueError for immutable fields."""
    blocked = _IMMUTABLE_FIELDS & fields.keys()
    if blocked:
        raise ValueError(f"Cannot update immutable fields: {blocked}")
    all_instincts = load_instincts()
    found = None
    for inst in all_instincts:
        if inst["id"] == instinct_id:
            found = inst
            break
    if found is None:
        raise KeyError(f"Instinct not found: {instinct_id}")
    for k, v in fields.items():
        found[k] = v
    _atomic_rewrite(all_instincts)
    return found


def get_agent_categories(agent_name):
    """Lookup categories for an agent from AGENT_CATEGORY_MAP."""
    return AGENT_CATEGORY_MAP.get(agent_name, [])


def _stats():
    """Compute summary statistics."""
    all_inst = load_instincts()
    active = [i for i in all_inst if i.get("status") == "active"]
    archived = [i for i in all_inst if i.get("status") == "archived"]
    cats = Counter(i["category"] for i in active)
    avg_conf = sum(i["confidence"] for i in active) / len(active) if active else 0
    pinned_count = sum(1 for i in active if i.get("pinned", False))
    promo = get_promotion_candidates()
    return {
        "total_active": len(active),
        "total_archived": len(archived),
        "by_category": dict(cats),
        "avg_confidence": round(avg_conf, 3),
        "promotion_ready": len(promo),
        "pinned": pinned_count,
    }


def main():
    parser = argparse.ArgumentParser(description="Instinct store CLI")
    parser.add_argument("--stats", action="store_true", help="Show instinct statistics")
    parser.add_argument("--list", action="store_true", help="List active instincts")
    parser.add_argument("--promote-candidates", action="store_true", help="Show promotion candidates")
    parser.add_argument("--decay", action="store_true", help="Apply decay to all instincts")
    args = parser.parse_args()

    if args.stats:
        print(json_output(_stats()))
    elif args.list:
        active = load_instincts(status="active")
        for inst in sorted(active, key=lambda x: x["confidence"], reverse=True):
            pin = " [PINNED]" if inst.get("pinned") else ""
            print(f"[{inst['confidence']:.2f}] {inst['category']:12s} {_disp(inst['text'])}{pin}")
    elif args.promote_candidates:
        candidates = get_promotion_candidates()
        if not candidates:
            print("No promotion candidates (need conf >= 0.80 + evidence >= 3)")
        else:
            for c in candidates:
                print(f"[{c['confidence']:.2f} {c['evidence_count']}x] {c['category']}: {_disp(c['text'])}")
    elif args.decay:
        decayed = apply_decay()
        print(f"Decay applied: {len(decayed)} instincts updated")
        for d in decayed:
            print(f"  [{d['confidence']:.2f}] {_disp(d['text'])}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
