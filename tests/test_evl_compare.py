"""Tests for evl_compare — cross-character ranking on one rubric (deterministic).

Loads each character's scorecard for a rubric, ranks by raw score, and attaches
normalized z / percentile via evl_normalize. Characters with no scorecard are
reported as missing (loud), never silently dropped or scored as zero.
"""
import json

import pytest

from platform_lib import evl_compare as CMP


@pytest.fixture
def three_cards(tmp_path, monkeypatch):
    import platform_lib.paths as paths_mod
    monkeypatch.setattr(paths_mod, "PROFILES", tmp_path)
    monkeypatch.setattr(paths_mod, "CHARACTERS",
                        {"a": "a", "b": "b", "c": "c", "d": "d"})
    monkeypatch.setattr(paths_mod, "ALL_CHARS", ["a", "b", "c", "d"])
    for char, overall, verdict in [("a", 4.0, "PASS"), ("b", 2.0, "BLOCKED"), ("c", 3.0, "PASS")]:
        d = tmp_path / char / "eval"
        d.mkdir(parents=True)
        (d / "demo.json").write_text(json.dumps(
            {"overall": overall, "verdict": verdict, "verified_coverage": 1.0}), encoding="utf-8")
    # 'd' has no scorecard → should land in missing
    return tmp_path


def test_compare_ranks_by_raw_desc(three_cards):
    res = CMP.compare("demo")
    order = [r["character"] for r in res["ranked"]]
    assert order == ["a", "c", "b"]            # 4.0 > 3.0 > 2.0
    assert res["missing"] == ["d"]


def test_compare_attaches_normalized_stats(three_cards):
    res = CMP.compare("demo")
    top = res["ranked"][0]
    assert top["raw"] == 4.0
    assert top["z"] is not None                # cohort of 3 → z computable
    assert top["percentile"] == pytest.approx(100 * 2.5 / 3)


def test_compare_subset_of_characters(three_cards):
    res = CMP.compare("demo", characters=["a", "b"])
    assert [r["character"] for r in res["ranked"]] == ["a", "b"]
    assert res["missing"] == []


def test_render_comparison_table(three_cards):
    md = CMP.render_comparison(CMP.compare("demo"))
    assert "demo" in md
    for char in ("a", "b", "c"):
        assert char in md
    assert "d" in md                            # missing char surfaced in the report
