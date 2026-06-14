"""decision_store — concurrency-safe write primitives for the orc:decisions register.

alloc_id / append_decision / parse_decisions / register_lock for the orc:decisions
skill. Concurrent agents in team-mode call these without colliding on DEC-n ids.
One file per record; lock covers only the alloc+write pair. Injection-escape
neutralises leading '---'/'## DEC-' anchors in caller prose. fcntl.flock (POSIX,
guarded) — degrades to warn-once no-op on non-POSIX.
"""
import contextlib, datetime as dt, re, sys
from pathlib import Path
from typing import Optional
import yaml

DECISION_ID_RE = re.compile(r"^DEC-\d+$")
_INJ_FENCE_RE = re.compile(r"(?m)^(---+\s*)$")
_INJ_DEC_HEADING_RE = re.compile(r"(?m)^(##\s+DEC-)")
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_LOCK_FILENAME = ".decisions.lock"
_warned_degraded = False


class DecisionError(ValueError):
    """Raised on grammar/shape/uniqueness violations."""


def _escape_rationale(text: str) -> str:
    return _INJ_DEC_HEADING_RE.sub(r"\\\1", _INJ_FENCE_RE.sub(r"\\\1", text or ""))

def _sanitize_field(text: str) -> str:
    flat = re.sub(r"[\r\n]+", " ", text or "").strip()
    return _INJ_DEC_HEADING_RE.sub(r"\\\1", _INJ_FENCE_RE.sub(r"\\\1", flat))

def _flock(fh, op: str) -> bool:
    try:
        import fcntl  # POSIX only; not available on Windows
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX if op == "ex" else fcntl.LOCK_UN)
        return True
    except (ImportError, OSError):
        return False

def _warn_degraded_once() -> None:
    global _warned_degraded
    if _warned_degraded:
        return
    _warned_degraded = True
    sys.stderr.write(
        "[decision_store] warning: file lock unavailable — concurrent agents may "
        "collide on ids. Single-writer use is unaffected.\n"
    )

@contextlib.contextmanager
def register_lock(decisions_dir: Path):
    """Best-effort exclusive flock. Degrades to warn-once no-op on non-POSIX.

    Serialises alloc_id + append_decision, closing the TOCTOU window where two
    agents could scan the same max-id before either writes its new file.
    """
    lock_path = Path(decisions_dir) / _LOCK_FILENAME
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "w")
    locked = _flock(fh, "ex")
    if not locked:
        _warn_degraded_once()
    try:
        yield
    finally:
        if locked:
            _flock(fh, "un")
        fh.close()

def _read_fm_id(f: Path) -> Optional[int]:
    text = f.read_text(encoding="utf-8")
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    try:
        data = yaml.safe_load(fm_match.group(1)) or {}
        raw_id = str(data.get("id", "")).strip()
    except yaml.YAMLError:
        m = re.search(r"^id:\s*(DEC-\d+)\s*$", fm_match.group(1), re.MULTILINE)
        raw_id = m.group(1) if m else ""
    m = re.match(r"^DEC-(\d+)$", raw_id)
    return int(m.group(1)) if m else None

def alloc_id(decisions_dir: Path) -> str:
    """Next free DEC-n = max(existing) + 1, or DEC-1 on empty dir.

    Corrupt-but-id-bearing files still reserve their number so a repair
    can never collide with an id allocated in the meantime.
    """
    used = [n for f in Path(decisions_dir).glob("*.md") if (n := _read_fm_id(f)) is not None]
    return f"DEC-{(max(used) + 1) if used else 1}"

def parse_decisions(decisions_dir: Path) -> list[dict]:
    """All records sorted by filename. Legacy records (no DEC-n id) → id=None, never renumbered."""
    decisions_dir = Path(decisions_dir)
    if not decisions_dir.exists():
        return []
    records = []
    for f in sorted(decisions_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm: dict = {}
        fm_match = _FRONTMATTER_RE.match(text)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError:
                pass
        raw_id = str(fm.get("id", "")).strip()
        records.append({
            "id": raw_id if DECISION_ID_RE.match(raw_id) else None,
            "file": f.name,
            "date": str(fm.get("date", "")).strip(),
            "character": str(fm.get("character", "")).strip(),
            "category": str(fm.get("category", "")).strip(),
            "status": str(fm.get("status", "active")).strip() or "active",
            "title": str(fm.get("title", f.stem)).strip(),
            "supersedes": str(fm.get("supersedes", "")).strip(),
            "path": str(f),
        })
    return records

def _slug(title: str) -> str:
    s = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")[:40] or "decision"

def _render_record(dec_id, title, rationale, date, character, affects, supersedes) -> str:
    fm_lines = [f"id: {dec_id}", "status: active", f"date: {date}"]
    if character:
        fm_lines.append(f"character: {character}")
    if affects:
        fm_lines.append(f"affects: {affects}")
    if supersedes:
        fm_lines.append(f"supersedes: {supersedes}")
    return f"---\n{chr(10).join(fm_lines)}\n---\n\n## {dec_id} — {title}\n\n{rationale.strip()}\n"
def append_decision(
    decisions_dir: Path,
    dec_id: str,
    title: str,
    rationale: str,
    *,
    character: str = "",
    affects: str = "",
    supersedes: str = "",
    date: Optional[str] = None,
) -> Path:
    """Validate + write one decision file. NOT self-locking — wrap in register_lock().

    supersedes flip happens AFTER successful write so a failed write never retires a
    live ruling. Raises DecisionError on malformed id, duplicate, or dangling ref.
    """
    dec_id = dec_id.strip()
    if not DECISION_ID_RE.match(dec_id):
        raise DecisionError(f"id {dec_id!r} does not match {DECISION_ID_RE.pattern}")
    if not title.strip():
        raise DecisionError("a decision needs a non-empty title")
    if not rationale.strip():
        raise DecisionError("a decision needs a non-empty rationale")
    if supersedes and not DECISION_ID_RE.match(supersedes.strip()):
        raise DecisionError(f"supersedes {supersedes!r} is not a valid decision id")
    decisions_dir = Path(decisions_dir)
    decisions_dir.mkdir(parents=True, exist_ok=True)
    existing = parse_decisions(decisions_dir)
    existing_ids = {r["id"] for r in existing if r["id"]}
    if dec_id in existing_ids:
        raise DecisionError(f"{dec_id} already exists; use alloc_id + supersedes= to retire")
    if supersedes and supersedes not in existing_ids:
        raise DecisionError(f"supersedes {supersedes} but that id is not in the register")
    record_text = _render_record(
        dec_id, _sanitize_field(title), _escape_rationale(rationale),
        date or dt.date.today().isoformat(),
        _sanitize_field(character), _sanitize_field(affects), supersedes.strip(),
    )
    out_path = decisions_dir / f"{dec_id}-{_slug(title)}.md"
    out_path.write_text(record_text, encoding="utf-8")
    if supersedes:
        _supersede_in_place(decisions_dir, supersedes.strip())
    return out_path
def _supersede_in_place(decisions_dir: Path, dec_id: str) -> bool:
    """Flip an existing record's status: to 'superseded' — touches only that one line."""
    for f in Path(decisions_dir).glob("*.md"):
        text = f.read_text(encoding="utf-8")
        fm_match = _FRONTMATTER_RE.match(text)
        if not fm_match:
            continue
        try:
            data = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError:
            continue
        if str(data.get("id", "")).strip() != dec_id:
            continue
        new_fm, n = re.subn(
            r"^status:\s*\S+\s*$", "status: superseded",
            fm_match.group(1), count=1, flags=re.MULTILINE,
        )
        if n == 0:
            return False  # no status: line (hand-edited record — leave untouched)
        f.write_text(f"---\n{new_fm}\n---{text[fm_match.end():]}", encoding="utf-8")
        return True
    return False
