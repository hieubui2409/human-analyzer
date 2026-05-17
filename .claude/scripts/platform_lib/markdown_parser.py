"""Markdown section parser and metadata extractor."""
import re
from pathlib import Path
from typing import Optional


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


def extract_frontmatter(filepath: Path) -> dict[str, str]:
    """Extract YAML-like frontmatter from markdown file."""
    if not filepath.exists():
        return {}
    text = filepath.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return {}
    result = {}
    for line in fm_match.group(1).splitlines():
        kv = line.split(":", 1)
        if len(kv) == 2:
            result[kv[0].strip()] = kv[1].strip().strip('"').strip("'")
    return result


def count_lines(filepath: Path) -> int:
    """Count lines in a file. Returns 0 if file doesn't exist."""
    if not filepath.exists():
        return 0
    return len(filepath.read_text(encoding="utf-8").splitlines())


def extract_dates(text: str) -> list[str]:
    """Extract date patterns from text (DD/MM/YYYY, YYYY-MM-DD, MM/YYYY)."""
    patterns = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{2}/\d{4}\b",
        r"\b\d{2}-\d{4}\b",
    ]
    dates = []
    for pat in patterns:
        dates.extend(re.findall(pat, text))
    return sorted(set(dates))


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
    """Parse TIMELINE.md → list of {date, event, section}."""
    sections = extract_sections(filepath, level=2)
    events = []
    date_pattern = re.compile(r"[-•*]\s*\*?\*?(\d{2}/\d{2}/\d{4}|\d{2}/\d{4}|\d{4})\*?\*?\s*[-:–]?\s*(.*)")
    for section_name, content in sections.items():
        for line in content.splitlines():
            m = date_pattern.match(line.strip())
            if m:
                events.append({
                    "date": m.group(1),
                    "event": m.group(2).strip(),
                    "section": section_name,
                })
    return events


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
