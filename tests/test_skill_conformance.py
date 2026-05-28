"""Isolated tests for C3-ext CE-02 conformance audit (Batch 9, Phase 4).

Deterministic gather (GR#4): per-skill progressive-disclosure verdict
(KEEP | ENHANCE-CE02 | REFACTOR-PD | BLOCK) from line counts, references
structure, description + section presence. LLM adjudication of wording is out of
scope. Mock skill dir under tmp_path — never touches the real catalog. The ck-origin
scope guard is asserted (a `name: ck:` skill must be excluded).
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


audit = _load(SK / "audit-skill-progressive-disclosure.py", "pd_audit")


def _skill(skills: Path, name: str, *, body_lines: int = 10, desc="Audit things. Use when auditing.",
           when=True, scope_decl=True, refs=None, ck=False):
    d = skills / name
    d.mkdir(parents=True)
    fm_name = "ck:tool" if ck else name.replace("-", ":", 1)
    lines = [f"# {name}", ""]
    if when:
        lines += ["## When to Use", "", "- always", ""]
    if scope_decl:
        lines += ["Handles X, does not handle Y.", ""]
    lines += ["See references/ for detail.", ""]
    lines += [f"filler line {i}" for i in range(body_lines)]
    body = f"---\nname: {fm_name}\ndescription: \"{desc}\"\n---\n\n" + "\n".join(lines) + "\n"
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    for rname, rlines in (refs or {}).items():
        rd = d / "references"
        rd.mkdir(exist_ok=True)
        (rd / rname).write_text("\n".join(f"r{i}" for i in range(rlines)) + "\n", encoding="utf-8")
    return d


@pytest.fixture
def catalog(tmp_path):
    s = tmp_path / "skills"
    s.mkdir()
    # KEEP: small, has When-to-Use + trigger desc + scope decl + anti-pattern
    keep = _skill(s, "orc-clean", body_lines=20)
    (keep / "SKILL.md").write_text(
        (keep / "SKILL.md").read_text() + "\n## Anti-patterns\n\n- none\n", encoding="utf-8")
    # ENHANCE-CE02: small but missing When-to-Use (WARN only, no refactor trigger)
    _skill(s, "psy-warn", body_lines=20, when=False)
    # REFACTOR-PD: entry 201-300 lines, no references/
    _skill(s, "cre-mid", body_lines=230)
    # BLOCK: entry > 300 lines
    _skill(s, "gro-huge", body_lines=320)
    # BLOCK: reference file > 300 lines (PD-2)
    _skill(s, "mat-bigref", body_lines=20, refs={"big.md": 350})
    # orphan: no SKILL.md
    (s / "com-orphan").mkdir()
    # ck-origin: project prefix but name: ck: → must be excluded
    _skill(s, "orc-foreign", body_lines=20, ck=True)
    return s


def _verdict(s, name):
    rec = audit.audit_skill(s / name)
    return rec["verdict"], rec


def test_keep(catalog):
    v, rec = _verdict(catalog, "orc-clean")
    assert v == "KEEP", rec["findings"]


def test_enhance_on_missing_when_to_use(catalog):
    v, rec = _verdict(catalog, "psy-warn")
    assert v == "ENHANCE-CE02"
    assert any(c == "WU-1" for _, c, _ in rec["findings"])


def test_refactor_pd_201_300(catalog):
    v, rec = _verdict(catalog, "cre-mid")
    assert v == "REFACTOR-PD"
    assert any(s == "WARN" and c == "PD-1" for s, c, _ in rec["findings"])


def test_block_entry_over_300(catalog):
    v, rec = _verdict(catalog, "gro-huge")
    assert v == "BLOCK"
    assert any(s == "FAIL" and c == "PD-1" for s, c, _ in rec["findings"])


def test_block_reference_over_300(catalog):
    v, rec = _verdict(catalog, "mat-bigref")
    assert v == "BLOCK"
    assert any(s == "FAIL" and c == "PD-2" for s, c, _ in rec["findings"])


def test_ck_origin_excluded(catalog):
    rec = audit.audit_skill(catalog / "orc-foreign")
    assert rec["ck_excluded"] is True


def test_collect_routes_orphan_and_excludes_ck(catalog):
    records, excluded, orphans = audit.collect(catalog, "project-owned")
    names = {r["dir"] for r in records}
    assert "com-orphan" in orphans
    assert "orc-foreign" in excluded
    assert "com-orphan" not in names
    # real skills present, zero of them silently dropped
    assert {"orc-clean", "psy-warn", "cre-mid", "gro-huge", "mat-bigref"} <= names


def test_no_block_means_strict_clean(catalog):
    # remove the two BLOCK fixtures → strict gate should see 0 BLOCK
    import shutil
    shutil.rmtree(catalog / "gro-huge")
    shutil.rmtree(catalog / "mat-bigref")
    records, _, _ = audit.collect(catalog, "project-owned")
    assert all(r["verdict"] != "BLOCK" for r in records)
