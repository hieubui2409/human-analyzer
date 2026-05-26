"""Isolated tests for C3 orc:skill-stocktake (Batch 9).

Deterministic gather (GR#4): catalog count + metadata gaps + CLAUDE.md reconcile
(scan), and overlap-candidate detection + new-skill usage guard (analyze). LLM
verdict (duplicate vs complementary) is out of scope. Mock skill dir, monkeypatched
SKILLS_DIR/CLAUDE_MD — never touches the real catalog.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts"))

SK = PROJECT_ROOT / ".claude" / "skills" / "orc-skill-stocktake" / "scripts"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _skill(dirp: Path, name: str, desc: str, when=False):
    d = dirp / name
    d.mkdir(parents=True)
    body = f"---\nname: {name.replace('-', ':', 1)}\ndescription: \"{desc}\"\n---\n\n# {name}\n"
    if when:
        body += "\n## When to Use\n\n- always\n"
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    return d


@pytest.fixture
def mock_catalog(tmp_path):
    skills = tmp_path / "skills"
    skills.mkdir()
    _skill(skills, "psy-alpha", "Audit references from theory to profile. Triggers: 'ref scan'.", when=True)
    _skill(skills, "psy-beta", "Audit references from profile to theory bidirectional. Triggers: 'ref audit'.")
    _skill(skills, "cre-gamma", "Write a social media post end to end pipeline. Triggers: 'write post'.")
    # a ck-origin skill that MUST be excluded from the project catalog
    _skill(skills, "cook", "ck implement feature.")
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(
        "| `psy:alpha` | x |\n| `psy:beta` | y |\n| `cre:gamma` | z |\n"
        "53 skills (orc/mat/psy/cre/gro/com) share a lib\n", encoding="utf-8")
    return {"skills": skills, "claude": claude}


@pytest.fixture
def scan_mod(mock_catalog, monkeypatch):
    mod = _load(SK / "scan-skill-catalog-metadata.py", "stk_scan")
    monkeypatch.setattr(mod, "SKILLS_DIR", mock_catalog["skills"])
    monkeypatch.setattr(mod, "CLAUDE_MD", mock_catalog["claude"])
    return mod


@pytest.fixture
def analyze_mod(mock_catalog, monkeypatch):
    mod = _load(SK / "analyze-skill-overlap-and-gaps.py", "stk_analyze")
    monkeypatch.setattr(mod, "SKILLS_DIR", mock_catalog["skills"])
    return mod


# ── Quick Scan ───────────────────────────────────────────────────────────────
class TestQuickScan:
    def test_excludes_ck_origin_skill(self, scan_mod):
        records = scan_mod.scan_catalog()
        names = {r["dir"] for r in records}
        assert "cook" not in names  # ck-origin, not project-owned
        assert {"psy-alpha", "psy-beta", "cre-gamma"} <= names

    def test_counts_per_framework(self, scan_mod):
        records = scan_mod.scan_catalog()
        psy = [r for r in records if r["framework"] == "psy"]
        assert len(psy) == 2

    def test_flags_missing_when_to_use(self, scan_mod):
        records = scan_mod.scan_catalog()
        beta = next(r for r in records if r["dir"] == "psy-beta")
        assert "missing ## When to Use" in beta["gaps"]
        alpha = next(r for r in records if r["dir"] == "psy-alpha")
        assert "missing ## When to Use" not in alpha["gaps"]  # alpha has the section

    def test_reconcile_matches_claude_md(self, scan_mod):
        rec = scan_mod.reconcile(scan_mod.scan_catalog())
        assert rec["live_count"] == 3
        assert rec["in_catalog_not_in_claude_md"] == []
        assert rec["in_claude_md_not_in_catalog"] == []

    def test_reconcile_detects_drift(self, scan_mod, mock_catalog):
        _skill(mock_catalog["skills"], "gro-delta", "New growth skill. Triggers: 'x'.")
        rec = scan_mod.reconcile(scan_mod.scan_catalog())
        assert "gro:delta" in rec["in_catalog_not_in_claude_md"]


# ── Full Stocktake overlap + usage ─────────────────────────────────────────────
class TestOverlapAndUsage:
    def test_complementary_pair_surfaced_as_candidate(self, analyze_mod):
        data = analyze_mod.gather()
        pairs = analyze_mod.overlap_pairs(data["skills"], 0.2)
        names = {(p["a"], p["b"]) for p in pairs} | {(p["b"], p["a"]) for p in pairs}
        # alpha/beta share 'audit references theory profile' tokens → candidate
        assert ("psy:alpha", "psy:beta") in names or ("psy:beta", "psy:alpha") in names

    def test_overlap_is_candidate_only_not_verdict(self, analyze_mod):
        data = analyze_mod.gather()
        for p in analyze_mod.overlap_pairs(data["skills"], 0.2):
            assert "candidate only" in p["note"]  # never auto-decides duplicate

    def test_new_skill_usage_not_meaningful(self, analyze_mod):
        # mock skills live in a tmp dir → 0 git commits → tagged NEW
        data = analyze_mod.gather()
        usage = analyze_mod.usage_table(data["skills"])
        assert all(u["is_new"] for u in usage)
        assert all("NEW" in u["usage_signal"] for u in usage)

    def test_distinct_skills_not_flagged(self, analyze_mod):
        data = analyze_mod.gather()
        pairs = analyze_mod.overlap_pairs(data["skills"], 0.5)  # high bar
        # cre-gamma (write post) shares little with psy ref skills
        flagged = {p["a"] for p in pairs} | {p["b"] for p in pairs}
        assert "cre:gamma" not in flagged
