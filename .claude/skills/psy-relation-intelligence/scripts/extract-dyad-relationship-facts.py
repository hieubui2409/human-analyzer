"""Extract publishable relationship facts from a character dyad (gather layer).

GOLDEN RULE #4: this script ONLY gathers deterministic facts from the dyad
graph + relationship files + GRO mentoring milestones, scans Rule-09 consent
tags, and attaches backing-material evidence tiers. It does NOT decide which
facts make a compelling angle -- that is the LLM synthesis layer (see SKILL.md).

Read sources (READ-ONLY):
  - docs/graph/{dyad}.md            (matched by frontmatter `characters`, robust)
  - relationships/{other}.md        (both directions, via list_relationship_files)
  - growth/mentoring-map.md         (GRO milestones, for mentor-mentee dyads)
  - materials/{char}/*.md           (backing evidence tiers, over-gather)

EXCLUSION (red-team R2): darkness/traumas.md content is NEVER read into a fact
payload -- only its existence is noted as metadata. Trauma detail must not leak
into a content angle.

Consent (red-team R2 / OQ#6 A): a fact whose source line carries a Rule-09 tag
([PRIVATE]/[CONFIDENTIAL]/[ANONYMIZE]) is marked consent_status=BLOCKED.

Output: JSON {dyad, primary_character_hint, traumas_present, facts:[...]} on stdout.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import (
    GRAPH, MATERIALS, resolve_character, character_dir, CHAR_DISPLAY,
    list_relationship_files,
)
from platform_lib.materials_classifier import SOURCE_TO_TIER
from platform_lib.markdown_parser import (
    extract_frontmatter,
    extract_sections, extract_tags, extract_timeline_events, extract_milestones,
)
from platform_lib.errors import emit_error

def _fold_ascii(s: str) -> str:
    """Strip diacritics and lowercase — so Vietnamese 'chết' matches ASCII pattern 'chet'."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


# Graph sections worth mining for publishable facts (exclude clinical-only sections).
PUBLISHABLE_SECTIONS = {
    "Relationship Timeline", "Growth Interface", "Communication Patterns",
    "Power Dynamics", "Prognosis",
}
_STOP = {"nay", "do", "cua", "voi", "cho", "cac", "mot", "nhung", "duoc", "la", "va"}

# Deterministic crisis/self-harm markers (VN + EN). A graph dyad legitimately
# records crisis episodes; surfacing them in a content angle without explicit
# consent is a Rule-09 / Rule-06 violation. Gathering matches is deterministic;
# the BLOCKED verdict forces an LLM/human look (fail-closed, never silent OK).
_CRISIS_RE = re.compile(
    r"tu\s*tu|tu\s*sat|tu\s*hai|chet|cat\s*tay|ket\s*lieu|tram\s*cam|"
    r"suicid|self[- ]?harm|kill\s*(my|him|her)self|overdose|crisis",
    re.IGNORECASE,
)


def _yaml_frontmatter(path: Path) -> dict | None:
    """Full YAML frontmatter (list-aware) via materials_classifier parser."""
    return extract_frontmatter(path)


def find_dyad_graph(slug_a: str, slug_b: str) -> Path | None:
    """Match a graph file by its frontmatter `characters` set (order-independent)."""
    if not GRAPH.exists():
        return None
    want = {slug_a, slug_b}
    for f in sorted(GRAPH.glob("*.md")):
        fm = _yaml_frontmatter(f) or {}
        chars = fm.get("characters")
        if isinstance(chars, list) and want.issubset(set(chars)):
            return f
    return None


def _consent_for_line(line_text: str) -> str:
    """BLOCKED if a Rule-09 tag OR a crisis/self-harm marker is present (fail-closed).
    Crisis regex runs on both raw and diacritic-folded text so Vietnamese accented words
    (e.g. 'chết' → 'chet') are caught even when the corpus uses proper Unicode spelling."""
    if extract_tags(line_text) or _CRISIS_RE.search(line_text) or _CRISIS_RE.search(_fold_ascii(line_text)):
        return "BLOCKED"
    return "OK"


def extract_graph_facts(graph_path: Path) -> list[dict]:
    """Pull events + dynamic statements from publishable graph sections."""
    facts = []
    text = graph_path.read_text(encoding="utf-8")
    # Timeline events (dated)
    for ev in extract_timeline_events(graph_path):
        facts.append({
            "kind": "timeline_event", "section": ev["section"],
            "date": ev["date"], "text": ev["event"],
            "consent_status": _consent_for_line(ev["event"]),
            "source": graph_path.name,
        })
    # Section-level dynamic statements (first non-empty lines of publishable level-2 sections).
    # extract_sections at level=2 returns level-2 names ("Relationship Timeline", etc.) which
    # match PUBLISHABLE_SECTIONS directly. Using level=3 returned sub-section names that never
    # matched, making the gate a dead no-op (always passed everything through).
    sections = extract_sections(graph_path, level=2)
    for name, content in sections.items():
        base = name.split("(")[0].strip()
        if base not in PUBLISHABLE_SECTIONS:
            continue
        for line in content.splitlines():
            s = line.strip(" -*|")
            if len(s) > 25 and not s.startswith("#") and "|" not in line:
                facts.append({
                    "kind": "dynamic", "section": name, "date": None, "text": s[:200],
                    "consent_status": _consent_for_line(line), "source": graph_path.name,
                })
                break  # one representative statement per section
    return facts


def extract_relationship_facts(slug: str, other_slug: str) -> list[dict]:
    """Pull narrative facts from {slug}/relationships/{other}.md if present."""
    facts = []
    for relf in list_relationship_files(slug):
        fm = _yaml_frontmatter(relf) or {}
        cross = fm.get("cross_characters") or []
        if other_slug not in cross and other_slug not in relf.stem:
            continue
        for name, content in extract_sections(relf, level=2).items():
            for line in content.splitlines():
                s = line.strip(" -*")
                if len(s) > 25 and not s.startswith("#"):
                    facts.append({
                        "kind": "relationship", "section": name, "date": None,
                        "text": s[:200], "consent_status": _consent_for_line(line),
                        "source": f"{slug}/relationships/{relf.name}",
                    })
                    break
    return facts


def extract_mentoring_facts(slug: str, other_slug: str) -> list[dict]:
    """GRO mentoring milestones referencing the other character."""
    mfile = character_dir(slug) / "growth" / "mentoring-map.md"
    if not mfile.exists():
        return []
    facts = []
    other_disp = CHAR_DISPLAY.get(other_slug, other_slug).lower()
    for ms in extract_milestones(mfile):
        blob = f"{ms['milestone']} {ms.get('evidence','')}".lower()
        if other_disp in blob or other_slug in blob:
            facts.append({
                "kind": "mentoring_milestone", "section": "mentoring-map",
                "date": ms.get("date") or None, "text": ms["milestone"][:200],
                "status": ms.get("status"), "consent_status": "OK",
                "source": f"{slug}/growth/mentoring-map.md",
            })
    return facts


def _keywords(text: str) -> set[str]:
    return {w.lower().strip(".,!?:;\"'()") for w in text.split()
            if len(w) > 3 and w.lower() not in _STOP}


def gather_backing_materials(facts: list[dict], slugs: list[str]) -> None:
    """Attach best (lowest-tier) backing material per fact by keyword overlap. Mutates facts."""
    pool = []
    for slug in slugs:
        mdir = MATERIALS / slug
        if not mdir.exists():
            continue
        for fpath in sorted(mdir.rglob("*.md")):
            fm = extract_frontmatter(fpath)
            if not fm:
                continue
            pool.append({
                "file": fpath.name,
                "tier": SOURCE_TO_TIER.get(fm.get("source_category", ""), 5),
                "confidentiality": fm.get("confidentiality", "private"),
                "_kw": _keywords(f"{fm.get('title', fpath.stem)} {fm.get('content_tags','')}"),
            })
    for fact in facts:
        fkw = _keywords(fact["text"])
        cands = [m for m in pool if fkw & m["_kw"]]
        if cands:
            best = min(cands, key=lambda m: m["tier"])
            fact["evidence_tier"] = best["tier"]
            fact["backing_material"] = best["file"]
            if best["confidentiality"] in ("private", "restricted") and fact["consent_status"] == "OK":
                fact["consent_status"] = "REVIEW"
        else:
            fact["evidence_tier"] = None
            fact["backing_material"] = None


def traumas_present(slugs: list[str]) -> dict:
    """Note ONLY existence of darkness/traumas.md (never read content) -- R2."""
    return {slug: (character_dir(slug) / "darkness" / "traumas.md").exists() for slug in slugs}


def primary_character_hint(facts: list[dict], slugs: list[str]) -> str:
    """Narrative centrality: char whose display name appears most across facts (OQ#3 A)."""
    counts = {s: 0 for s in slugs}
    for fact in facts:
        low = fact["text"].lower()
        for s in slugs:
            if CHAR_DISPLAY.get(s, s).lower() in low:
                counts[s] += 1
    return max(counts, key=counts.get) if any(counts.values()) else slugs[0]


def build(slug_a: str, slug_b: str) -> dict:
    graph = find_dyad_graph(slug_a, slug_b)
    facts = []
    if graph:
        facts += extract_graph_facts(graph)
    facts += extract_relationship_facts(slug_a, slug_b)
    facts += extract_relationship_facts(slug_b, slug_a)
    facts += extract_mentoring_facts(slug_a, slug_b)
    facts += extract_mentoring_facts(slug_b, slug_a)

    gather_backing_materials(facts, [slug_a, slug_b])
    for i, fact in enumerate(facts):
        fact["fact_id"] = f"F{i+1}"
    return {
        "dyad": [slug_a, slug_b],
        "graph_file": graph.name if graph else None,
        "primary_character_hint": primary_character_hint(facts, [slug_a, slug_b]),
        "traumas_present": traumas_present([slug_a, slug_b]),
        "fact_count": len(facts),
        "facts": facts,
    }


def main():
    ap = argparse.ArgumentParser(description="Extract dyad relationship facts (deterministic gather).")
    ap.add_argument("char_a", help="First character (alias or slug)")
    ap.add_argument("char_b", help="Second character (alias or slug)")
    ap.add_argument("--json", action="store_true", help="JSON output (default)")
    args = ap.parse_args()
    try:
        a, b = resolve_character(args.char_a), resolve_character(args.char_b)
    except ValueError as e:
        emit_error("validation", str(e), {"char_a": args.char_a, "char_b": args.char_b})
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(build(a, b), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
