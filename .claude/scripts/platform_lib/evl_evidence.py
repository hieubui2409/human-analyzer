"""Deterministic evidence gathering for the rubric scoring engine (gather, not judge).

For each criterion, glob its `evidence_hint` patterns over a character's profile,
split matched files into level-2 sections, and surface them as candidate snippets
with a `file:line` source and a best-effort tier tag. The LLM judge (a later stage)
is what actually PICKS a snippet and commits to a citation + tier; this module only
puts the options on the table. Per the design law it may over-surface — candidates
are capped and ranked (strongest tier first) so the judge sees the best first.
"""
import re

from platform_lib.evl_aggregate import VALID_TIERS
from platform_lib.markdown_parser import extract_frontmatter
from platform_lib.paths import character_dir

MAX_CANDIDATES = 8          # cap per criterion; judge needs the best few, not everything
_SNIPPET_CHARS = 600        # keep bundles lean
_CONF_TO_TIER = {"high": "T2", "medium": "T3", "low": "T4"}
_H2_RE = re.compile(r"^##\s+(.+)$")


def _tier_tag(fm: dict) -> str | None:
    """Best-effort tier for a file: explicit `evidence_tier`/`tier` is authoritative;
    a `confidence` field is a non-authoritative hint the judge must still confirm."""
    raw = fm.get("evidence_tier") or fm.get("tier")
    if raw is not None:
        s = str(raw).upper()
        s = s if s.startswith("T") else f"T{s}"
        return s if s in VALID_TIERS else None
    conf = fm.get("confidence")
    return _CONF_TO_TIER.get(str(conf).lower()) if conf else None


def _tier_num(tier) -> int:
    return int(tier[1:]) if tier in VALID_TIERS else 99


def _sections(path) -> list[tuple[str, int, str]]:
    """(heading, 1-based line, body) for each level-2 section; whole doc if none."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out, cur = [], None
    for i, line in enumerate(lines, 1):
        m = _H2_RE.match(line)
        if m:
            cur = {"title": m.group(1).strip(), "line": i, "body": []}
            out.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    if not out:
        body = re.sub(r"^---\n.*?\n---\n", "", "\n".join(lines), flags=re.DOTALL)
        return [("(document)", 1, body.strip())] if body.strip() else []
    return [(s["title"], s["line"], "\n".join(s["body"]).strip()) for s in out]


def _candidates_from_file(path, relpath: str, character: str) -> list[dict]:
    tier = _tier_tag(extract_frontmatter(path))
    out = []
    for title, line, body in _sections(path):
        if not body:
            continue
        text = body[:_SNIPPET_CHARS] + ("…" if len(body) > _SNIPPET_CHARS else "")
        out.append({"text": text, "source": f"{relpath}:{line}", "tier": tier,
                    "section": title, "character": character})
    return out


def gather_for_criterion(character: str, criterion: dict) -> list[dict]:
    """Candidate evidence for one criterion, ranked strongest-tier-first, capped."""
    cdir = character_dir(character)
    seen, cands = set(), []
    for pattern in criterion.get("evidence_hint", []):
        for path in sorted(cdir.glob(pattern)):
            if not path.is_file() or path.suffix != ".md" or path in seen:
                continue
            seen.add(path)
            cands += _candidates_from_file(path, path.relative_to(cdir).as_posix(), character)
    cands.sort(key=lambda e: (_tier_num(e["tier"]), e["source"]))
    return cands[:MAX_CANDIDATES]


def gather_for_rubric(character: str, rubric: dict) -> dict:
    """{criterion_id: [evidence]} for every criterion in a single-subject rubric."""
    return {c["id"]: gather_for_criterion(character, c)
            for d in rubric["domains"] for c in d["criteria"]}


def gather_for_dyad(pair: tuple, rubric: dict) -> dict:
    """{criterion_id: [evidence]} pooled from BOTH characters, re-ranked.

    Each side is independently capped at MAX_CANDIDATES then concatenated (no final
    truncation) so a partner with many sections can never crowd the other out of the
    bundle — a dyad criterion needs evidence from both characters to be judgeable.
    """
    out = {}
    for d in rubric["domains"]:
        for c in d["criteria"]:
            merged = gather_for_criterion(pair[0], c) + gather_for_criterion(pair[1], c)
            merged.sort(key=lambda e: (_tier_num(e["tier"]), e["character"], e["source"]))
            out[c["id"]] = merged
    return out
