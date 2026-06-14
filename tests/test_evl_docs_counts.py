"""Docs-count reconcile guard for the EVL framework addition.

Locks the two distinct "frameworks" semantics so a future edit can't silently drift:
the TOTAL counts moved to 7 frameworks / 68 skills, while the "cre:angle-discovery
mines 6 frameworks" strings are a DIFFERENT semantic (what CRE sources) and must stay
6 until that is a deliberate CRE decision.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _read(rel):
    return (REPO / rel).read_text(encoding="utf-8")


# --- total-count reconcile (7 frameworks / 68 skills) -----------------------

def test_modules_total_is_68_across_7():
    text = _read("docs/MODULES.md")
    assert "68 project-owned skills" in text and "across 7 frameworks" in text
    assert "EVL 8 = 68" in text
    assert "## EVL — Evaluation (8)" in text


def test_claude_md_lists_evl_and_68():
    text = _read("CLAUDE.md")
    assert "68 framework skills" in text and "·EVL 8" in text
    assert "**EVL** | Evaluation" in text
    assert "17-evl-framework.md" in text


def test_no_stale_total_counts():
    for rel in ("CLAUDE.md", "docs/MODULES.md", ".claude/skills/_framework-shared/README.md"):
        text = _read(rel)
        assert "60 framework skills" not in text, rel
        assert "60 project-owned skills" not in text, rel
        assert "= 60" not in text, rel
        assert "across 6 frameworks" not in text, rel


# --- new reference docs exist ------------------------------------------------

def test_evl_framework_rule_doc_exists():
    p = REPO / "docs" / "rules" / "17-evl-framework.md"
    assert p.exists() and "EVL Framework" in p.read_text(encoding="utf-8")


def test_evl_operating_guide_exists():
    p = REPO / ".claude" / "skills" / "_framework-shared" / "references" / "evl-operating-guide.md"
    text = p.read_text(encoding="utf-8")
    for skill in ("evl:score", "evl:standardize", "evl:fit", "evl:compatibility",
                  "evl:compare", "evl:track", "evl:validate", "evl:rubric-import"):
        assert skill in text, skill


# --- CRE-angle-mining "6 frameworks" deliberately preserved -----------------

def test_cre_angle_mining_strings_unchanged():
    # These describe what cre:angle-discovery SOURCES, not the total framework count.
    # Flipping them to 7 is a CRE behavior decision, not a count reconcile.
    assert "Mine 6 frameworks" in _read("docs/MODULES.md")
    assert "mining the 6 frameworks" in _read("docs/rules/14-cre-evidence-and-events.md")
    assert "mining all 6 frameworks" in _read(
        ".claude/skills/_framework-shared/references/cre-operating-guide.md")
