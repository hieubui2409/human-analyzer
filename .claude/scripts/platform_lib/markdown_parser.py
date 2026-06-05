"""Markdown section parser and metadata extractor."""
import datetime as _dt
import re
from pathlib import Path
from typing import Optional

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _stringify_dates(obj):
    """YAML turns unquoted ISO dates into date objects; coerce back to ISO strings so
    downstream string comparisons (last_updated, captured_date) stay stable. Recurses
    into nested dicts/lists so craap_score / tags / references keep their structure."""
    if isinstance(obj, _dt.datetime):
        return obj.isoformat()
    if isinstance(obj, _dt.date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _stringify_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_dates(v) for v in obj]
    return obj


def extract_sections(filepath: Path, level: int = 2) -> dict[str, str]:
    """Extract markdown sections at given heading level. Returns {heading: content}."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    pattern = re.compile(rf"^{'#' * level}\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections = {}
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[heading] = text[start:end].strip()
    return sections


def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file as a (possibly nested) dict.

    Uses ``yaml.safe_load`` so nested mappings (e.g. ``craap_score:``) and block/flow
    list values (``tags: [a, b]``, multi-line ``references:``) are preserved instead of
    being flattened to empty strings. Date scalars are coerced to ISO strings for stable
    comparisons. Returns ``{}`` when the file is missing or has no frontmatter block.
    """
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    fm_match = _FRONTMATTER_RE.match(text)
    if not fm_match:
        return {}
    data = yaml.safe_load(fm_match.group(1)) or {}
    if not isinstance(data, dict):
        return {}
    return _stringify_dates(data)


def count_lines(filepath: Path) -> int:
    """Count lines in a file. Returns 0 if file doesn't exist."""
    if not filepath.exists():
        return 0
    return len(filepath.read_text(encoding="utf-8").splitlines())


def extract_dates(text: str) -> list[str]:
    """Extract date patterns from text.

    Slash dates in this corpus use the **DD/MM/YYYY** convention (Vietnamese locale),
    NOT US MM/DD — callers comparing/parsing these must assume day-first. The two-field
    `NN/YYYY` form is month/year. Returned as raw strings (no validation); use
    `parse_iso_date` for a validated date object from an ISO `YYYY-MM-DD` arg.
    """
    patterns = [
        r"\b\d{2}/\d{2}/\d{4}\b",   # DD/MM/YYYY (day-first)
        r"\b\d{4}-\d{2}-\d{2}\b",   # YYYY-MM-DD (ISO)
        r"\b\d{2}/\d{4}\b",         # MM/YYYY
        r"\b\d{2}-\d{4}\b",         # MM-YYYY
    ]
    dates = []
    for pat in patterns:
        dates.extend(re.findall(pat, text))
    return sorted(set(dates))


def parse_iso_date(raw: str) -> _dt.date:
    """Parse a CLI `--since`-style ISO date (YYYY-MM-DD) to a date. Raises ValueError if bad.

    Single source so CLI scripts stop diverging between `date.fromisoformat` and
    `datetime.strptime(...,'%Y-%m-%d')` (both accept the same input, but sharing one
    parser keeps error handling and the accepted format identical everywhere)."""
    return _dt.date.fromisoformat(raw.strip())


def extract_links(text: str) -> list[dict]:
    """Extract markdown links. Returns [{text, url}]."""
    return [{"text": m[0], "url": m[1]} for m in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)]


def extract_tags(text: str) -> list[dict]:
    """Extract privacy/status tags. Returns [{tag, line}]."""
    tags = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"\[(PRIVATE|CONFIDENTIAL:\s*[^\]]+|ANONYMIZE|UNCERTAIN|DISPUTED[^\]]*)\]", line):
            tags.append({"tag": m.group(1), "line": i})
    return tags


def find_cross_references(filepath: Path, target_names: list[str]) -> list[dict]:
    """Find mentions of target names in a file. Returns [{line, name, context}]."""
    if not filepath.exists():
        return []
    results = []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    for i, line_text in enumerate(lines, 1):
        for name in target_names:
            if name.lower() in line_text.lower():
                results.append({"line": i, "name": name, "context": line_text.strip()[:120]})
    return results


def extract_timeline_events(filepath: Path) -> list[dict]:
    """Parse timeline → list of {date, event, section}. Handles bullet and table formats."""
    sections = extract_sections(filepath, level=2)
    events = []
    bullet_pat = re.compile(r"[-•*]\s*\*?\*?(\d{2}/\d{2}/\d{4}|\d{2}/\d{4}|\d{4})\*?\*?\s*[-:–]?\s*(.*)")
    table_pat = re.compile(r"\|\s*\*?\*?(\d{2}/\d{2}/\d{4}|\d{2}/\d{4}|\d{4})\*?\*?\s*\|\s*(.*?)\s*\|")
    for section_name, content in sections.items():
        for line in content.splitlines():
            stripped = line.strip()
            m = bullet_pat.match(stripped) or table_pat.search(stripped)
            if m:
                events.append({
                    "date": m.group(1),
                    "event": m.group(2).strip().rstrip("|").strip(),
                    "section": section_name,
                })
    return events


def parse_table_rows(text: str) -> list[list[str]]:
    """Split markdown table rows into trimmed cell lists (deterministic gather).

    One row per line containing at least two ``|`` delimiters. The outer leading/trailing
    pipe is stripped, each cell is trimmed, and separator rows (``| --- | --- |``) are
    dropped. Cells are returned verbatim with NO column-count assumption — callers map
    columns themselves (tables in this corpus range from 3 to 5 columns). This replaces
    the divergent fixed-3-group ``re.search`` parsers that silently truncated wide tables.
    """
    rows: list[list[str]] = []
    for line in text.splitlines():
        s = line.strip()
        if s.count("|") < 2:
            continue
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        cells = [c.strip() for c in s.split("|")]
        # separator row: every (non-empty) cell is only dashes/colons/spaces
        if cells and all(c and set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells)
    return rows


def parse_dreyfus_skills(text: str) -> list[dict]:
    """Extract Dreyfus competency rows from a markdown table → ``[{name, level}]``.

    A skill row has a name cell (col 1) plus a Dreyfus level cell (col 2) whose leading
    token is a 1-7 digit (e.g. ``5 — Expert``). Only the 2nd column is inspected for the
    level so that textual-level tables (``Basic``) and evidence cells that merely *start*
    with a number (``1 năm tại …``) are NOT mis-read as Dreyfus scores. Header/separator
    rows are skipped. Single canonical parser shared by gro:competency-map / gro:compare /
    gro:career-forecast so they can no longer disagree on skill count / average level.
    """
    skills: list[dict] = []
    for cells in parse_table_rows(text):
        if len(cells) < 2:
            continue
        name = cells[0].strip().strip("*").strip()
        m = re.match(r"\*{0,2}\s*([1-7])\b", cells[1])
        if not m or len(name) <= 1:
            continue
        if name.lower() in {"kỹ năng", "skill", "competency", "name", "field"}:
            continue
        skills.append({"name": name, "level": int(m.group(1))})
    return skills


def extract_milestones(filepath: Path) -> list[dict]:
    """Parse MILESTONES.md → list of {milestone, status, date, evidence}."""
    if not filepath.exists():
        return []
    milestones = []
    current = None
    for line in filepath.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^#{2,3}\s+(.+)", line)
        if heading:
            if current:
                milestones.append(current)
            current = {"milestone": heading.group(1).strip(), "status": "UNKNOWN", "date": "", "evidence": ""}
            continue
        if current:
            status_m = re.search(r"(ACHIEVED|IN_PROGRESS|NOT_STARTED|REGRESSED)", line, re.IGNORECASE)
            if status_m:
                current["status"] = status_m.group(1).upper()
            date_m = re.search(r"(\d{2}/\d{2}/\d{4}|\d{2}/\d{4})", line)
            if date_m:
                current["date"] = date_m.group(1)
    if current:
        milestones.append(current)
    return milestones
