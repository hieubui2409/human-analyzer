"""Tests for evl_import — external framework → canonical draft (offline, no-invention).

The importer scaffolds structure only; it NEVER invents a weight or an anchor and
NEVER drops a source criterion it cannot classify — both surface loudly in
_import_gaps. A gap-laden draft must FAIL evl_schema validation so it can never be
scored until a human/agent fills it.
"""
from platform_lib import evl_import as IMP
from platform_lib import evl_schema


_MD = """# External Framework
## Leadership
## Communication
- Teamwork
Some prose that cannot be classified as a discrete criterion.
"""


def _meta(**kw):
    base = {"id": "ext-framework", "title": "External Framework", "kind": "decision",
            "source": "pasted text"}
    base.update(kw)
    return base


def test_parse_md_splits_criteria_and_unclassified():
    parsed = IMP.parse_external(_MD, "md")
    texts = [c["text"] for c in parsed["criteria"]]
    assert texts == ["Leadership", "Communication", "Teamwork"]
    assert any("prose" in u for u in parsed["unclassified"])


def test_import_keeps_all_three_criteria():
    rubric, gaps = IMP.import_rubric(_MD, _meta(), fmt="md")
    crits = [c["id"] for d in rubric["domains"] for c in d["criteria"]]
    assert len(crits) == 3


def test_import_never_invents_weight_or_anchors():
    rubric, gaps = IMP.import_rubric(_MD, _meta(), fmt="md")
    for d in rubric["domains"]:
        for c in d["criteria"]:
            assert c["weight"] is None            # placeholder, not invented
            assert c["anchors"] == {}             # placeholder, not invented
    assert gaps, "gaps must be reported"


def test_unclassified_text_is_surfaced_not_dropped():
    _, gaps = IMP.import_rubric(_MD, _meta(), fmt="md")
    assert any("prose" in g or "unclassified" in g.lower() for g in gaps)


def test_draft_is_marked_for_review():
    rubric, _ = IMP.import_rubric(_MD, _meta(), fmt="md")
    assert rubric["status"] == "draft" and rubric["needs_human_review"] is True


def test_gap_draft_fails_validation_so_it_cannot_score():
    rubric, _ = IMP.import_rubric(_MD, _meta(), fmt="md")
    errs = evl_schema.validate_rubric(rubric)
    assert errs, "a placeholder-laden draft MUST fail schema validation (blocked from scoring)"


def test_agent_mapping_fills_gaps():
    mapping = {
        "leadership": {"weight": 0.5, "min_tier": "T2", "evidence_hint": ["x.md"],
                       "anchors": {"0": "none", "2": "some", "5": "strong"}},
        "communication": {"weight": 0.5, "min_tier": "T2", "evidence_hint": ["y.md"],
                          "anchors": {"0": "none", "2": "some", "5": "clear"}},
    }
    rubric, gaps = IMP.import_rubric(_MD, _meta(), mapping=mapping, fmt="md")
    by_id = {c["id"]: c for d in rubric["domains"] for c in d["criteria"]}
    assert by_id["leadership"]["weight"] == 0.5
    # teamwork still unmapped → still a gap
    assert any("teamwork" in g.lower() for g in gaps)


def test_parse_json_input():
    parsed = IMP.parse_external('{"title": "J", "criteria": [{"text": "Focus"}]}', "json")
    assert parsed["criteria"][0]["text"] == "Focus"


def test_write_draft_lands_in_imported(monkeypatch, tmp_path):
    import platform_lib.paths as paths_mod
    import platform_lib.fs_guard as fsg
    monkeypatch.setattr(paths_mod, "RUBRICS", tmp_path)
    monkeypatch.setitem(fsg.FRAMEWORK_WRITE_ROOTS, "EVL", [tmp_path])
    rubric, _ = IMP.import_rubric(_MD, _meta(), fmt="md")
    out = IMP.write_draft(rubric, "ext-framework")
    assert out.exists() and out.parent.name == "imported" and out.suffix == ".yaml"
