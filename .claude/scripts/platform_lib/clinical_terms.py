"""Clinical term detection patterns and reference index builder."""
import re
from pathlib import Path
from typing import Optional

# Canonical reference-file H2 sections per docs/rules/10-reference-library-standard.md
# (matched as case-insensitive substrings, since headings carry a numeric prefix like
# "## 1. Định nghĩa (Definition)"). Single source so ref-create and ref-maintain validate
# against the same schema instead of two divergent (and both wrong) section lists.
REFERENCE_REQUIRED_SECTIONS = ["Định nghĩa", "Nguồn gốc", "Cơ chế", "Case Study"]

CLINICAL_PATTERNS = [
    r"\battachment\s+(style|theory|pattern|anxious|avoidant|disorganized|secure)\b",
    r"\b(anxious|avoidant|disorganized|secure)\s+attachment\b",
    r"\bparentification\b",
    r"\b(emotional|instrumental)\s+parentification\b",
    r"\badultification\b",
    r"\bco-?dependenc[ey]\b",
    r"\benmeshment\b",
    r"\btriangulation\b",
    r"\bscapegoat(ing)?\b",
    r"\bgolden\s+child\b",
    r"\bnarciss(ism|istic)\b",
    r"\bborderline\b",
    r"\bdissociat(ion|ive)\b",
    r"\bsomatiz(ation|ing)\b",
    r"\bintellectualiz(ation|ing)\b",
    r"\bration(alization|alizing)\b",
    r"\bprojection\b",
    r"\bsplitting\b",
    r"\brepression\b",
    r"\bsublimation\b",
    r"\bdenial\b",
    r"\breaction\s+formation\b",
    r"\bundoing\b",
    r"\bisolation\s+of\s+affect\b",
    r"\bcompartmentaliz(ation|ing)\b",
    r"\bidentification\s+with\s+(the\s+)?aggressor\b",
    r"\bSavior\s+Complex\b",
    r"\bMessiah\s+Complex\b",
    r"\bWhite\s+Knight\s+Syndrome\b",
    r"\brescue\s+fantasy\b",
    r"\btrauma\s+bond(ing)?\b",
    r"\bcomplex\s+(PTSD|C-?PTSD|trauma)\b",
    r"\b(PTSD|C-?PTSD|MDD|GAD|BPD|DID)\b",
    r"\bDSM-?5\b",
    r"\bICD-?11\b",
    r"\bsuicid(al|e|ality)\b",
    r"\bself-?harm(ing)?\b",
    r"\bideation\b",
    r"\bactive\s+SI\b",
    r"\bpassive\s+SI\b",
    r"\bindividuation\b",
    r"\bseparation-?individuation\b",
    r"\bobject\s+(constancy|relations)\b",
    r"\btransference\b",
    r"\bcounter-?transference\b",
    r"\bfalse\s+self\b",
    r"\btrue\s+self\b",
    r"\bwinnicott(ian)?\b",
    r"\bgrey\s+rock\b",
    r"\bno\s+contact\b",
    r"\blow\s+contact\b",
    r"\bhypervigilance\b",
    r"\bhyperarousal\b",
    r"\bemotional\s+(dysregulation|flooding|numbing)\b",
    r"\bavoidance\s+(coping|behavior|strategy)\b",
    r"\brumination\b",
    r"\bcatastrophizing\b",
    r"\bmaladaptive\s+(coping|schema|pattern)\b",
    r"\brep(etition|eated)\s+compulsion\b",
    r"\blearned\s+helplessness\b",
    r"\bfawn(ing)?\s+response\b",
    r"\bfreeze\s+response\b",
    r"\bfight[\s-]or[\s-]flight\b",
    r"\b(secure|anxious|avoidant|fearful)\s+base\b",
    r"\binternal\s+working\s+model\b",
    r"\bmentaliz(ation|ing)\b",
    r"\baffect\s+regulation\b",
    r"\bwindow\s+of\s+tolerance\b",
    r"\b(adverse\s+)?childhood\s+experience\b",
    r"\bACE\s+score\b",
    r"\bresilience\s+factor\b",
    r"\bprotective\s+factor\b",
    r"\bpost[\s-]traumatic\s+growth\b",
    r"\bself[\s-]?efficacy\b",
    r"\bself[\s-]?compassion\b",
    r"\bcognitive\s+(distortion|restructuring|reappraisal)\b",
    r"\bcore\s+belief\b",
    r"\bschema\s+(therapy|mode)\b",
    r"\binner\s+(child|critic|parent)\b",
    r"\breparenting\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CLINICAL_PATTERNS]


def scan_file_for_clinical_terms(filepath: Path) -> list[dict]:
    """Scan a file for clinical terms. Returns list of {line, term, pattern, context}."""
    results = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return results
    for i, line_text in enumerate(lines, 1):
        for pat in COMPILED_PATTERNS:
            for match in pat.finditer(line_text):
                ctx_start = max(0, match.start() - 40)
                ctx_end = min(len(line_text), match.end() + 40)
                results.append({
                    "line": i,
                    "term": match.group(),
                    "pattern": pat.pattern,
                    "context": line_text[ctx_start:ctx_end].strip(),
                })
    return results


def build_reference_index(references_dir: Path) -> dict[str, dict]:
    """Parse docs/references/INDEX.md → {theory_name: {file, category, key_terms}}."""
    index_file = references_dir / "INDEX.md"
    if not index_file.exists():
        return {}
    index = {}
    current_category = "Uncategorized"
    for line in index_file.read_text(encoding="utf-8").splitlines():
        cat_match = re.match(r"^#{2,3}\s+(.+)", line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            continue
        link_match = re.match(r"^-\s+\[(.+?)\]\((.+?\.md)\)", line)
        if link_match:
            name = link_match.group(1).strip()
            filename = link_match.group(2).strip()
            key_terms = extract_key_terms_from_name(name)
            index[name] = {
                "file": filename,
                "category": current_category,
                "key_terms": key_terms,
            }
    return index


def extract_key_terms_from_name(theory_name: str) -> list[str]:
    """Derive searchable key terms from theory name."""
    terms = [theory_name.lower()]
    words = re.split(r"[\s\-/()]+", theory_name.lower())
    terms.extend(w for w in words if len(w) > 3)
    abbrev_map = {
        "ptsd": ["ptsd", "post-traumatic stress"],
        "c-ptsd": ["c-ptsd", "complex ptsd", "complex trauma"],
        "mdd": ["mdd", "major depressive"],
        "ace": ["ace", "adverse childhood"],
        "dsm": ["dsm-5", "dsm5"],
    }
    for abbr, expansions in abbrev_map.items():
        if abbr in theory_name.lower():
            terms.extend(expansions)
    return list(set(terms))

