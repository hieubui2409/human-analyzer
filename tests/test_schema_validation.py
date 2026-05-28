"""Isolated tests for C7 Draft-7 schema validation (Batch 9).

Deterministic contract enforcement (GR#4): mock-data profiles PASS, known-bad
frontmatter FAILs with the precise offending field, schema selection by path,
INDEX/jsonl handling. Uses tmp fixtures + mock-data — never touches real docs/.
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts"))

from platform_lib import schema_validator as sv  # noqa: E402

MOCK = PROJECT_ROOT / "tests" / "mock-data" / "profiles"


# ── schema selection by path ──────────────────────────────────────────────────
class TestSchemaSelection:
    def test_profile_md_selects_profile_schema(self):
        assert sv.schema_for(Path("docs/profiles/x/identity/core.md")) == "profile-frontmatter.schema.json"

    def test_growth_competency_selects_specialized(self):
        assert sv.schema_for(Path("docs/profiles/x/growth/competencies.md")) == "growth-competency.schema.json"

    def test_growth_career_selects_specialized(self):
        assert sv.schema_for(Path("docs/profiles/x/growth/career-path.md")) == "growth-career-path.schema.json"

    def test_formulation_selects_specialized(self):
        assert sv.schema_for(Path("docs/profiles/x/psychology/formulation.md")) == "psychology-formulation.schema.json"

    def test_diagnostics_selects_specialized(self):
        assert sv.schema_for(Path("docs/profiles/x/psychology/diagnostics.md")) == "diagnostics.schema.json"

    def test_material_md_selects_material_schema(self):
        assert sv.schema_for(Path("docs/materials/x/foo.md")) == "material-frontmatter.schema.json"

    def test_material_index_is_excluded(self):
        assert sv.schema_for(Path("docs/materials/x/INDEX.md")) is None

    def test_jsonl_selects_event_schema(self):
        assert sv.schema_for(Path(".claude/session-state/content-events.jsonl")) == "event-jsonl.schema.json"

    def test_unknown_path_skips(self):
        assert sv.schema_for(Path("README.md")) is None


# ── mock-data corpus passes day one ─────────────────────────────────────────────
class TestMockCorpusPasses:
    def test_all_mock_profiles_pass(self):
        results = [sv.validate_file(f) for f in sorted(MOCK.rglob("*.md"))]
        failures = [r for r in results if r["status"] == "FAIL"]
        assert failures == [], f"mock profiles must all pass: {failures}"


# ── known-bad fixtures FAIL with precise field ──────────────────────────────────
def _write_profile(tmp_path, body):
    p = tmp_path / "profiles" / "x" / "identity" / "core.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


class TestKnownBadFails:
    def test_missing_required_field(self, tmp_path):
        p = _write_profile(tmp_path, "---\ndomain: identity\ntype: narrative\ntags: []\n"
                            "references: []\ncross_characters: []\nlast_updated: 2026-01-01\n"
                            "updated_by: t\nconfidence: high\n---\nbody\n")
        r = sv.validate_file(p)
        assert r["status"] == "FAIL"
        assert any(v["field"] == "character" for v in r["violations"])

    def test_bad_enum_domain(self, tmp_path):
        p = _write_profile(tmp_path, "---\ncharacter: x\ndomain: nonsense\ntype: narrative\n"
                            "tags: []\nreferences: []\ncross_characters: []\n"
                            "last_updated: 2026-01-01\nupdated_by: t\nconfidence: high\n---\nb\n")
        r = sv.validate_file(p)
        assert r["status"] == "FAIL"
        assert any(v["field"] == "domain" and v["rule"] == "enum" for v in r["violations"])

    def test_bad_date_format(self, tmp_path):
        p = _write_profile(tmp_path, "---\ncharacter: x\ndomain: identity\ntype: narrative\n"
                            "tags: []\nreferences: []\ncross_characters: []\n"
                            "last_updated: 01-01-2026\nupdated_by: t\nconfidence: high\n---\nb\n")
        r = sv.validate_file(p)
        assert any(v["field"] == "last_updated" and v["rule"] == "pattern" for v in r["violations"])

    def test_no_frontmatter_fails(self, tmp_path):
        p = _write_profile(tmp_path, "# just a heading\n\nno frontmatter here\n")
        r = sv.validate_file(p)
        assert r["status"] == "FAIL"

    def test_growth_wrong_domain_fails(self, tmp_path):
        p = tmp_path / "profiles" / "x" / "growth" / "competencies.md"
        p.parent.mkdir(parents=True)
        p.write_text("---\ncharacter: x\ndomain: identity\ntype: data\ntags: []\n"
                     "references: []\ncross_characters: []\nlast_updated: 2026-01-01\n"
                     "updated_by: t\nconfidence: high\n---\nb\n", encoding="utf-8")
        r = sv.validate_file(p)
        assert r["status"] == "FAIL"  # domain must be 'growth' (const)


# ── event jsonl per-line validation ─────────────────────────────────────────────
class TestEventJsonl:
    def test_valid_event_line_passes(self, tmp_path):
        jl = tmp_path / "content-events.jsonl"
        jl.write_text('{"timestamp":"2026-05-25T18:49:51Z","event":"CRE.published","source":"x"}\n',
                      encoding="utf-8")
        assert sv.validate_file(jl)["status"] == "PASS"

    def test_bad_event_prefix_fails(self, tmp_path):
        jl = tmp_path / "content-events.jsonl"
        jl.write_text('{"timestamp":"2026-05-25T18:49:51Z","event":"lowercase.bad"}\n', encoding="utf-8")
        r = sv.validate_file(jl)
        assert r["status"] == "FAIL"

    def test_malformed_json_line_reported(self, tmp_path):
        jl = tmp_path / "content-events.jsonl"
        jl.write_text('{not json}\n', encoding="utf-8")
        r = sv.validate_file(jl)
        assert r["status"] == "FAIL"
        assert any(v["rule"] == "json" for v in r["violations"])
