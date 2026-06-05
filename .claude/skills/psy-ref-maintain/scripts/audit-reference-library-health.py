"""Audit clinical reference library health: citation counts, orphans, index gaps, schema issues."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib.paths import PROFILES, REFERENCES
from platform_lib.clinical_terms import REFERENCE_REQUIRED_SECTIONS
from platform_lib.errors import emit_error  # noqa: F401 — used for IO/decode errors

REQUIRED_SECTIONS = REFERENCE_REQUIRED_SECTIONS

INDEX_FILE = REFERENCES / "INDEX.md"


def load_index_entries() -> set[str]:
    """Extract theory names/filenames listed in INDEX.md."""
    if not INDEX_FILE.exists():
        return set()
    text = INDEX_FILE.read_text(encoding="utf-8")
    # Match markdown links like [name](file.md) or plain filenames
    links = set(re.findall(r'\[([^\]]+)\]\([^)]+\)', text))
    filenames = set(re.findall(r'[\w-]+\.md', text))
    return links | filenames


def count_citations(theory_name: str, theory_stem: str) -> int:
    """Count how many times a theory is cited across all profile files."""
    count = 0
    patterns = [
        theory_name.lower(),
        theory_stem.lower().replace("-", " "),
        theory_stem.lower().replace("-", "_"),
    ]
    for char_dir in PROFILES.iterdir():
        if not char_dir.is_dir():
            continue
        for md_file in char_dir.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8").lower()
                for pat in patterns:
                    if len(pat) > 4 and pat in text:
                        count += 1
                        break
            except (OSError, UnicodeError) as exc:
                emit_error("io", str(exc), {"file": str(md_file)})
    return count


def check_schema(text: str) -> list[str]:
    """Return list of missing required sections."""
    text_lower = text.lower()
    missing = []
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in text_lower:
            missing.append(sec)
    return missing


def classify_status(citations: int, in_index: bool, schema_issues: list[str]) -> str:
    if citations >= 3:
        base = "ACTIVE"
    elif citations >= 1:
        base = "USED"
    else:
        base = "ORPHAN"
    if not in_index:
        return f"{base}+NOT_INDEXED"
    if schema_issues:
        return f"{base}+SCHEMA_BREACH"
    return base


def main():
    parser = argparse.ArgumentParser(description="Audit clinical reference library health")
    parser.add_argument("--orphans-only", action="store_true",
                        help="Show only zero-citation orphans")
    parser.add_argument("--gaps-only", action="store_true",
                        help="Show only index/schema issues")
    parser.add_argument("--json", dest="json_out", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not REFERENCES.exists():
        print(f"ERROR: references directory not found at {REFERENCES}")
        sys.exit(1)

    index_entries = load_index_entries()
    ref_files = sorted(f for f in REFERENCES.glob("*.md") if f.name != "INDEX.md")

    if not ref_files:
        print("No reference files found in docs/references/")
        return

    records = []
    for ref_file in ref_files:
        text = ref_file.read_text(encoding="utf-8")
        stem = ref_file.stem
        # Extract theory name from first H1 heading or stem
        h1_match = re.search(r'^#\s+(.+)', text, re.MULTILINE)
        theory_name = h1_match.group(1).strip() if h1_match else stem.replace("-", " ").title()

        citations = count_citations(theory_name, stem)
        in_index = (ref_file.name in index_entries or
                    theory_name in index_entries or
                    stem in index_entries)
        schema_issues = check_schema(text)
        status = classify_status(citations, in_index, schema_issues)

        records.append({
            "file": ref_file.name,
            "theory_name": theory_name,
            "citations": citations,
            "in_index": in_index,
            "schema_issues": schema_issues,
            "status": status,
        })

    # Apply filters
    display_records = records
    if args.orphans_only:
        display_records = [r for r in records if r["citations"] == 0]
    elif args.gaps_only:
        display_records = [r for r in records if not r["in_index"] or r["schema_issues"]]

    if args.json_out:
        print(json.dumps(display_records, indent=2, ensure_ascii=False))
        return

    # Stats
    total = len(records)
    active = sum(1 for r in records if r["citations"] >= 3)
    used = sum(1 for r in records if 1 <= r["citations"] < 3)
    orphans = sum(1 for r in records if r["citations"] == 0)
    not_indexed = sum(1 for r in records if not r["in_index"])
    schema_breaches = sum(1 for r in records if r["schema_issues"])

    print(f"\n{'='*70}")
    print("  Reference Library Health Report")
    print(f"{'='*70}")
    print(f"  Total: {total} | Active(3+): {active} | Used(1-2): {used} | Orphans: {orphans}")
    print(f"  Not indexed: {not_indexed} | Schema issues: {schema_breaches}")
    print()

    if not display_records:
        print("  No issues found matching the filters.")
        return

    print(f"  {'File':<40s} {'Citations':<10s} {'Index':<8s} {'Status'}")
    print(f"  {'-'*40} {'-'*10} {'-'*8} {'-'*25}")
    for r in sorted(display_records, key=lambda x: x["citations"]):
        index_mark = "✓" if r["in_index"] else "✗"
        print(f"  {r['file'][:38]:<40s} {r['citations']:<10d} {index_mark:<8s} {r['status']}")

    # Schema detail
    breach_records = [r for r in display_records if r["schema_issues"]]
    if breach_records and not args.orphans_only:
        print(f"\n  Schema Issues Detail:")
        for r in breach_records:
            print(f"    {r['file']}: missing → {', '.join(r['schema_issues'])}")

    # Recommended actions
    print(f"\n  Recommended Actions:")
    action_n = 1
    orphan_list = [r["file"] for r in records if r["citations"] == 0]
    if orphan_list:
        print(f"  {action_n}. Review {len(orphan_list)} orphaned theories — consider archiving or adding citations")
        action_n += 1
    unindexed = [r["file"] for r in records if not r["in_index"]]
    if unindexed:
        print(f"  {action_n}. Add to INDEX.md: {', '.join(unindexed[:5])}"
              + (f" (+{len(unindexed)-5} more)" if len(unindexed) > 5 else ""))
        action_n += 1
    if breach_records:
        print(f"  {action_n}. Fix schema in {len(breach_records)} files — add missing sections")

    # Overall health score
    citation_pct = round((active + used) / total * 100) if total else 0
    index_pct = round((total - not_indexed) / total * 100) if total else 0
    schema_pct = round((total - schema_breaches) / total * 100) if total else 0
    overall_pct = round((citation_pct + index_pct + schema_pct) / 3)
    print(f"\n  Health Score:")
    print(f"    Citation coverage:  {citation_pct}%")
    print(f"    Index completeness: {index_pct}%")
    print(f"    Schema compliance:  {schema_pct}%")
    print(f"    Overall:            {overall_pct}%")


if __name__ == "__main__":
    main()
