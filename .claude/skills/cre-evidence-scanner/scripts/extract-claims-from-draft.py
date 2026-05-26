"""Extract atomic claims from a content draft (deterministic gather layer).

GOLDEN RULE #4: this script ONLY segments text into atomic claim units and
tags each with its line + character span. It does NOT judge whether a claim is
supported — that is the LLM adjudication layer (see SKILL.md).

Segmentation (validate Q1):
  - sentence-level by default (terminators . ! ? … and hard newlines),
  - clause-level split for compound sentences joined by Vietnamese
    connectives "nhưng" / "và" / "vì" / "nên" / "mà" (each clause = a claim),
  - markdown noise stripped (headings, bullets, links, bold/italic markers),
  - empty / pure-punctuation / hashtag-only / url-only lines dropped.

Output: JSON list of {claim, line, span:[start,end]} on stdout.
READ-ONLY. Vietnamese diacritics preserved (C8 unicode safety).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Sentence terminators (keep Vietnamese ellipsis …)
_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
# Clause connectives — split a sentence into separately-checkable claims.
_CLAUSE_SPLIT = re.compile(r"\s+(?:nhưng|và|vì|nên|mà)\s+", re.IGNORECASE)
# Markdown / formatting noise to strip before segmentation.
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_MD_MARKS = re.compile(r"[*_`>#]+")
_URL = re.compile(r"https?://\S+")
_HASHTAG_LINE = re.compile(r"^[\s#@\w/-]*$")  # hashtag/handle-only line


def _clean_line(line: str) -> str:
    line = _MD_LINK.sub(r"\1", line)        # keep link text, drop url
    line = _URL.sub("", line)
    line = _MD_MARKS.sub("", line)
    line = re.sub(r"^\s*[-•*]\s+", "", line)  # bullet leader
    return line.strip()


def _is_claim_worthy(text: str) -> bool:
    """Drop empty, punctuation-only, hashtag-only, or too-short fragments."""
    t = text.strip()
    if len(t) < 8:
        return False
    if not re.search(r"\w", t, re.UNICODE):
        return False
    if t.startswith("#") or all(w.startswith("#") for w in t.split()):
        return False
    return True


def extract_claims(text: str) -> list[dict]:
    """Segment draft text into atomic claims with line + span metadata."""
    claims = []
    offset = 0  # running char offset into the original text
    for lineno, raw_line in enumerate(text.splitlines(keepends=True), 1):
        line_start = offset
        offset += len(raw_line)

        cleaned = _clean_line(raw_line)
        if not cleaned or _HASHTAG_LINE.match(cleaned):
            continue

        # sentence then clause segmentation
        for sentence in _SENT_SPLIT.split(cleaned):
            for clause in _CLAUSE_SPLIT.split(sentence):
                clause = clause.strip()
                if not _is_claim_worthy(clause):
                    continue
                # span: locate clause within the original raw line (best-effort)
                idx = raw_line.find(clause[:20].strip()) if clause else -1
                span_start = line_start + (idx if idx >= 0 else 0)
                claims.append({
                    "claim": clause,
                    "line": lineno,
                    "span": [span_start, span_start + len(clause)],
                })
    return claims


def read_draft(asset_dir: Path) -> tuple[str, Path] | None:
    """Locate post.txt or post.md inside an asset dir; return (text, path)."""
    for name in ("post.txt", "post.md"):
        f = asset_dir / name
        if f.exists():
            try:
                return f.read_text(encoding="utf-8"), f
            except (OSError, UnicodeDecodeError):
                return None
    return None


def main():
    ap = argparse.ArgumentParser(description="Extract atomic claims from a draft (deterministic).")
    ap.add_argument("asset_dir", help="Asset dir containing post.txt|post.md")
    ap.add_argument("--json", action="store_true", help="JSON output (default)")
    args = ap.parse_args()

    asset_dir = Path(args.asset_dir)
    loaded = read_draft(asset_dir)
    if loaded is None:
        print(json.dumps({"error": f"no post.txt|post.md in {asset_dir}"}, ensure_ascii=False))
        sys.exit(1)

    text, path = loaded
    claims = extract_claims(text)
    out = {"asset_dir": str(asset_dir), "draft": str(path), "claim_count": len(claims), "claims": claims}
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
