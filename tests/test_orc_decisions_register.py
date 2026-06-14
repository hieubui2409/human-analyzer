"""Tests for the orc:decisions write side — atomic alloc-id, append, supersede lineage.

These tests cover the platform_lib/decision_store module. All I/O is isolated to
a tmp directory so nothing touches .claude/decisions/ during the test run.
"""
import os
import sys
import re
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "scripts"))
from platform_lib import decision_store as ds


# ---------------------------------------------------------------------------
# Case A: two sequential append_decision calls → distinct ids DEC-1, DEC-2
# ---------------------------------------------------------------------------

def test_two_sequential_appends_produce_distinct_ids(tmp_path):
    """alloc_id increments monotonically so DEC-1 and DEC-2 never collide."""
    d = tmp_path / "decisions"
    d.mkdir()

    id1 = ds.alloc_id(d)
    ds.append_decision(d, id1, "First decision", "Because it was first.")
    assert id1 == "DEC-1"

    id2 = ds.alloc_id(d)
    ds.append_decision(d, id2, "Second decision", "Because it was second.")
    assert id2 == "DEC-2"
    assert id1 != id2


# ---------------------------------------------------------------------------
# Case B: supersedes= flips the prior record's status to 'superseded'
# ---------------------------------------------------------------------------

def test_supersedes_flips_prior_record_status(tmp_path):
    """When a new record supersedes DEC-1, DEC-1's status becomes 'superseded'."""
    d = tmp_path / "decisions"
    d.mkdir()

    ds.append_decision(d, "DEC-1", "Original ruling", "First take.")
    ds.append_decision(d, "DEC-2", "Revised ruling", "Better take.", supersedes="DEC-1")

    records = ds.parse_decisions(d)
    by_id = {r["id"]: r for r in records}
    assert by_id["DEC-1"]["status"] == "superseded"
    assert by_id["DEC-2"]["status"] == "active"
    assert by_id["DEC-2"].get("supersedes") == "DEC-1"


# ---------------------------------------------------------------------------
# Case C: injection-escape blocks fake frontmatter fences in rationale
# ---------------------------------------------------------------------------

def test_injection_escape_blocks_fence_in_rationale(tmp_path):
    """A rationale containing a bare '---' line must not split the record file."""
    d = tmp_path / "decisions"
    d.mkdir()

    # This rationale contains a bare YAML fence and a ## DEC- heading
    evil_rationale = "Good reason.\n---\nid: DEC-99\nstatus: active\n---\n## DEC-99 — Fake"
    ds.append_decision(d, "DEC-1", "Real decision", evil_rationale)

    # The file must contain exactly one well-formed record (DEC-1 only).
    records = ds.parse_decisions(d)
    assert len(records) == 1
    assert records[0]["id"] == "DEC-1"

    # The raw file must not contain an unescaped lone '---' fence that would be
    # parsed as a record boundary (i.e. no `\nid: DEC-99` leaking outside the
    # escaped region). We check that no second fenced block appears in the raw
    # text with a different id.
    raw = (d / "DEC-1-real-decision.md").read_text(encoding="utf-8")
    # The escaped form starts with a backslash
    assert "\\---" in raw or "\\## DEC-" in raw


# ---------------------------------------------------------------------------
# Case D: empty dir → first alloc returns DEC-1
# ---------------------------------------------------------------------------

def test_empty_dir_alloc_returns_dec_1(tmp_path):
    """When the decisions directory is empty, alloc_id returns DEC-1."""
    d = tmp_path / "decisions"
    d.mkdir()
    assert ds.alloc_id(d) == "DEC-1"


# ---------------------------------------------------------------------------
# Case E: legacy council-*.md records still appear in the reader index
# ---------------------------------------------------------------------------

def test_legacy_council_records_listed_by_reader(tmp_path):
    """Legacy records without DEC-n ids are listed as-is; they are not renumbered."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "orc-decisions", "scripts"))
    # Temporarily make the module importable (it uses DECISIONS_DIR global, we patch it)
    import importlib
    import importlib.util

    d = tmp_path / "decisions"
    d.mkdir()

    # Write a legacy council record (no DEC-n id in frontmatter)
    legacy = d / "20260605-council-old-decision.md"
    legacy.write_text(
        "---\ndate: 2026-06-05\ncategory: council\ncharacter: cross\nstatus: active\n"
        "title: Old council ruling\n---\n\n# Old council ruling\n\nSome verdict.\n",
        encoding="utf-8",
    )

    # Also write a modern DEC-1 record
    ds.append_decision(d, "DEC-1", "Modern decision", "New rationale.")

    # Load via the index reader directly
    spec = importlib.util.spec_from_file_location(
        "index_decisions",
        os.path.join(
            os.path.dirname(__file__), "..", ".claude", "skills",
            "orc-decisions", "scripts", "index-decisions-with-search.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    records = mod.load_decisions(d)
    filenames = [r["file"] for r in records]

    assert "20260605-council-old-decision.md" in filenames, "legacy record must be listed"
    assert any("DEC-1" in r["title"] or r["file"].startswith("DEC-1") for r in records), (
        "modern DEC-1 record must be listed"
    )
