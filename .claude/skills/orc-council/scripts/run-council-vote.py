#!/usr/bin/env python3
"""Council vote: prepare questions and format verdict documents for 4-voice decision framework."""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import DECISIONS
from platform_lib.formatters import print_json
from platform_lib.errors import emit_error

CATEGORIES = ("psy", "cre", "gro", "cross")
VOICES = ("advocate", "skeptic", "pragmatist", "wildcard")


def slugify(text: str, max_words: int = 5) -> str:
    """Convert text to kebab-case slug."""
    words = re.sub(r"[^\w\s-]", "", text.lower()).split()
    return "-".join(words[:max_words])


def find_similar_decisions(question: str) -> list[str]:
    """Grep existing decisions for similar topic keywords."""
    if not DECISIONS.exists():
        return []
    keywords = [w.lower() for w in question.split() if len(w) > 3][:5]
    similar = []
    for f in sorted(DECISIONS.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue
        matches = sum(1 for k in keywords if k in content)
        if matches >= 2:
            similar.append(f.name)
    return similar


def prepare(question: str, category: str, character: str = "") -> dict:
    """Validate question, generate slug and output path."""
    question = question.strip()
    if not question:
        print(json.dumps({"error": "Question cannot be empty"}), file=sys.stderr)
        sys.exit(1)
    if len(question) > 500:
        print(json.dumps({"error": f"Question too long ({len(question)} chars, max 500)"}), file=sys.stderr)
        sys.exit(1)

    slug = slugify(question)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}-council-{slug}.md"
    output_path = str(DECISIONS / filename)

    DECISIONS.mkdir(parents=True, exist_ok=True)

    # Dedup check
    similar = find_similar_decisions(question)

    result = {
        "question": question,
        "category": category,
        "character": character,
        "slug": slug,
        "output_path": output_path,
        "similar_decisions": similar,
    }
    return result


def format_verdict(data: dict) -> str:
    """Format verdict markdown from JSON data. Pure formatting — no heuristic analysis."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = data.get("question", "Untitled")[:80]
    category = data.get("category", "cross")
    character = data.get("character", "cross")

    lines = [
        "---",
        f"date: {date_str}",
        f"category: council",
        f"character: {character}",
        f"status: active",
        f"title: \"Council: {title}\"",
        f"domain: {category}",
        f"voices: [advocate, skeptic, pragmatist, wildcard]",
        "---",
        "",
        f"# Council Verdict: {data['question']}",
        "",
    ]

    for voice in VOICES:
        lines.append(f"## {voice.capitalize()}")
        lines.append("")
        lines.append(data.get(voice, "(no response)"))
        lines.append("")

    lines.append("## Synthesized Verdict")
    lines.append("")
    lines.append(data.get("synthesis", "(no synthesis provided)"))
    lines.append("")

    return "\n".join(lines)


def tally(input_path: str) -> str:
    """Read JSON input, format verdict, write to output path."""
    ip = Path(input_path)
    if not ip.exists():
        print(json.dumps({"error": f"Input file not found: {input_path}"}), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(ip.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        emit_error("parse", str(e), {"input": str(ip)})
        print(json.dumps({"error": f"Failed to read input JSON: {e}"}), file=sys.stderr)
        sys.exit(1)

    required = ["question", "category"] + list(VOICES) + ["synthesis"]
    missing = [k for k in required if k not in data]
    if missing:
        print(json.dumps({"error": f"Missing required fields: {missing}"}), file=sys.stderr)
        sys.exit(1)

    verdict_md = format_verdict(data)

    slug = slugify(data["question"])
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}-council-{slug}.md"
    output_path = DECISIONS / filename

    # Avoid overwriting existing verdicts
    if output_path.exists():
        counter = 2
        while True:
            alt = DECISIONS / f"{date_str}-council-{slug}-{counter}.md"
            if not alt.exists():
                output_path = alt
                break
            counter += 1

    DECISIONS.mkdir(parents=True, exist_ok=True)
    output_path.write_text(verdict_md, encoding="utf-8")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Council vote: prepare questions and format verdict documents"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    prep = sub.add_parser("prepare", help="Validate question, generate output path, check dedup")
    prep.add_argument("--question", required=True, help="Decision question (max 500 chars)")
    prep.add_argument("--category", required=True, choices=CATEGORIES, help="Domain category")
    prep.add_argument("--character", default="cross", help="Character name or 'cross'")

    tal = sub.add_parser("tally", help="Format verdict document from JSON input")
    tal.add_argument("--input", required=True, help="Path to JSON file with voice responses + synthesis")

    args = parser.parse_args()

    if args.mode == "prepare":
        result = prepare(args.question, args.category, args.character)
        print_json(result)
    elif args.mode == "tally":
        output_path = tally(args.input)
        print_json({"status": "ok", "output_path": output_path})


if __name__ == "__main__":
    main()
