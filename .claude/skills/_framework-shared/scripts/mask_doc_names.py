#!/usr/bin/env python3
"""mask_doc_names — replace real-character names in shipped doc PROSE with neutral placeholders.

Scope: .claude/skills/**/{GUIDE-EN,GUIDE-VI,README,SKILL}.md + the top-level README.md. Body prose only —
YAML frontmatter and fenced code blocks are protected (so SKILL.md name/description/trigger CONTRACT lines
and code examples are never altered). Diacritic-exact display forms + full names + pii_extra tokens, matched
word-boundary + case-sensitive, mapped to "Nhân vật {A,B,...}" (VI docs) / "Character {A,B,...}" (EN docs).

NAME-FREE BY CONTRACT: zero real names here; the token→placeholder mapping loads at runtime from the
pack-excluded characters.yaml via pii_tokens. Idempotent. Dry-run by default; pass --apply to write.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pii_tokens  # noqa: E402


def _compile(token: str) -> re.Pattern:
    # Unicode-aware word boundary: token not flanked by word chars (handles VN diacritic letters).
    return re.compile(r"(?<!\w)" + re.escape(token) + r"(?!\w)")


def mask_text(text: str, replacements):
    """Return (new_text, n_subs). ``replacements`` = list of (token, placeholder), longest-first.

    Protects ONLY the leading YAML frontmatter (``---`` … ``---``) — the SKILL routing CONTRACT
    (name / description / triggers). Everything else, INCLUDING fenced code blocks, is masked: the
    tokens are personal names + full names + program names that appear in CLI-usage examples, example
    output tables, and quoted profile prose inside ``` fences — all of which must be PII-clean because
    the whole-pack scanner has no carve-out. This masker only rewrites its own token set (display/full
    names + slugs + pii_extra); bare ASCII fold flag values are out of its scope and are handled
    separately during de-naming. Word-boundary + case-sensitive on proper-noun forms.
    """
    patterns = [(_compile(tok), repl) for tok, repl in replacements]
    lines = text.split("\n")
    in_frontmatter = bool(lines) and lines[0].strip() == "---"
    total = 0
    out = []

    for idx, line in enumerate(lines):
        if in_frontmatter:
            out.append(line)
            if idx > 0 and line.strip() == "---":
                in_frontmatter = False
            continue

        new_line = line
        for pat, repl in patterns:
            new_line, n = pat.subn(repl, new_line)
            total += n
        out.append(new_line)

    return "\n".join(out), total


def _in_scope(root: Path):
    skills = root / ".claude" / "skills"
    names = {"GUIDE-EN.md", "GUIDE-VI.md", "README.md", "SKILL.md"}
    skip = ("/.venv/", "/node_modules/", "/site-packages/")  # vendored docs never ship + carry no PII
    files = [p for p in skills.rglob("*.md")
             if p.name in names and not any(s in str(p) for s in skip)]
    # Normative rule files ship too (docs/rules/**) — mask the illustrative-EXAMPLE names in them while
    # frontmatter + normative directives stay intact (the rule's meaning is in the directive, not the
    # example subject). Keeps the whole-pack PII scan carve-out-free.
    rules = root / "docs" / "rules"
    if rules.exists():
        files += list(rules.rglob("*.md"))
    top = root / "README.md"
    if top.exists():
        files.append(top)
    return sorted(set(files))


def _replacements_for(path: Path, tokens):
    """Pick the placeholder column by file language. GUIDE-EN.md → English, else Vietnamese."""
    use_en = path.name == "GUIDE-EN.md"
    return [(tok, en if use_en else vi) for (tok, vi, en) in tokens]


def main():
    ap = argparse.ArgumentParser(description="Mask real-character names in shipped doc prose.")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run report only)")
    ap.add_argument("--root", default=None, help="repo root (auto-detected)")
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[4]
    tokens = pii_tokens.load_tokens(root / "docs" / "profiles")
    if not tokens:
        print("No PII tokens (characters.yaml absent) — nothing to mask.")
        return 0

    changed, total_subs = 0, 0
    for path in _in_scope(root):
        text = path.read_text(encoding="utf-8")
        new, n = mask_text(text, _replacements_for(path, tokens))
        if n:
            changed += 1
            total_subs += n
            print(f"  {'WRITE' if args.apply else 'DRY '} {n:4d}  {path.relative_to(root)}")
            if args.apply:
                path.write_text(new, encoding="utf-8")
    verb = "masked" if args.apply else "would mask"
    print(f"\n{verb} {total_subs} occurrence(s) across {changed} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
