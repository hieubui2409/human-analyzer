"""Output formatting: markdown tables, JSON, summary blocks."""
import json
import sys
from typing import Optional


def markdown_table(headers: list[str], rows: list[list[str]], align: Optional[list[str]] = None) -> str:
    """Generate a markdown table. align: list of 'l', 'r', 'c' per column."""
    if not rows:
        return f"| {' | '.join(headers)} |\n| {' | '.join(['---'] * len(headers))} |\n| _(empty)_ |"
    widths = [max(len(h), max((len(str(r[i])) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = []
    for i, w in enumerate(widths):
        a = (align[i] if align and i < len(align) else "l")
        if a == "r":
            sep.append("-" * (w - 1) + ":")
        elif a == "c":
            sep.append(":" + "-" * (w - 2) + ":")
        else:
            sep.append("-" * w)
    lines = [
        "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |")
    return "\n".join(lines)


def json_output(data, pretty: bool = True) -> str:
    """Format data as JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2 if pretty else None, default=str)


def summary_block(title: str, items: dict[str, str]) -> str:
    """Format a key-value summary block."""
    lines = [f"## {title}", ""]
    max_key = max(len(k) for k in items) if items else 0
    for k, v in items.items():
        lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)


def severity_badge(severity: str) -> str:
    """Return severity indicator."""
    badges = {"HIGH": "[!!!]", "MEDIUM": "[!!]", "LOW": "[!]", "INFO": "[i]", "CRITICAL": "[XXX]"}
    return badges.get(severity.upper(), f"[{severity}]")


def print_table(headers: list[str], rows: list[list[str]], align: Optional[list[str]] = None):
    """Print markdown table to stdout."""
    print(markdown_table(headers, rows, align))


def print_json(data, pretty: bool = True):
    """Print JSON to stdout."""
    print(json_output(data, pretty))


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)
