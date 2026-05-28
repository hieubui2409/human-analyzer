"""Tests for B2 event partition — 6 framework JSONL streams (Batch 5 Ph1).

Routing is deterministic by event-type prefix; query reads one stream or merges all.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

EVENTLOG = PROJECT_ROOT / ".claude" / "skills" / "orc-event-log" / "scripts"
APPEND_SCRIPT = EVENTLOG / "append-event-to-log.py"
QUERY_SCRIPT = EVENTLOG / "query-event-log-with-filters.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def streams(tmp_path):
    """Build a tmp stream map mirroring EVENT_STREAMS."""
    return {
        "PSY": tmp_path / "character-events.jsonl",
        "MAT": tmp_path / "material-events.jsonl",
        "CRE": tmp_path / "content-events.jsonl",
        "GRO": tmp_path / "growth-signals.jsonl",
        "ORC": tmp_path / "cascade-events.jsonl",
        "COM": tmp_path / "governance-audit.jsonl",
    }


@pytest.fixture
def append_mod(streams, tmp_path, monkeypatch):
    mod = _load(APPEND_SCRIPT, "append_mod")
    monkeypatch.setattr(mod, "EVENT_STREAMS", streams)
    monkeypatch.setattr(mod, "CASCADE_EVENTS", streams["ORC"])
    return mod


@pytest.fixture
def query_mod(streams, monkeypatch):
    mod = _load(QUERY_SCRIPT, "query_mod")
    monkeypatch.setattr(mod, "EVENT_STREAMS", streams)
    return mod


class TestRouting:
    def test_psy_routes_to_character_events(self, append_mod, streams):
        path, fw = append_mod.resolve_stream("PSY.refresh")
        assert fw == "PSY"
        assert path == streams["PSY"]

    def test_mat_routes_to_material_events(self, append_mod, streams):
        path, fw = append_mod.resolve_stream("MAT.integrated")
        assert path == streams["MAT"]

    def test_com_routes_to_governance_audit(self, append_mod, streams):
        path, fw = append_mod.resolve_stream("COM.privacy")
        assert path == streams["COM"]

    def test_gro_routes_to_growth_signals(self, append_mod, streams):
        path, _ = append_mod.resolve_stream("GRO.assessed")
        assert path == streams["GRO"]

    def test_unknown_prefix_fallback_cascade(self, append_mod, streams):
        path, fw = append_mod.resolve_stream("FOO.bar")
        assert fw == "FOO"
        assert path == streams["ORC"]  # CASCADE_EVENTS fallback

    def test_com_event_types_registered(self, append_mod):
        assert "COM.privacy" in append_mod.VALID_EVENT_TYPES
        assert "COM.governance" in append_mod.VALID_EVENT_TYPES

    def test_batch6_event_types_registered(self, append_mod, streams):
        # B6: cre:evidence-scanner + psy:relation-intelligence event types
        assert "CRE.evidence-checked" in append_mod.VALID_EVENT_TYPES
        assert "PSY.relation-angle-discovered" in append_mod.VALID_EVENT_TYPES
        assert append_mod.resolve_stream("CRE.evidence-checked")[0] == streams["CRE"]
        assert append_mod.resolve_stream("PSY.relation-angle-discovered")[0] == streams["PSY"]

    def test_batch7_event_types_registered(self, append_mod, streams):
        # B7: cre:angle-discovery + cre:multiplatform event types route to CRE stream
        assert "CRE.angle-discovered" in append_mod.VALID_EVENT_TYPES
        assert "CRE.published" in append_mod.VALID_EVENT_TYPES
        assert append_mod.resolve_stream("CRE.angle-discovered")[0] == streams["CRE"]
        assert append_mod.resolve_stream("CRE.published")[0] == streams["CRE"]


class TestQuery:
    def _seed(self, streams):
        streams["PSY"].write_text(
            json.dumps({"timestamp": "2026-05-02T00:00:00Z", "event": "PSY.refresh"}) + "\n",
            encoding="utf-8")
        streams["MAT"].write_text(
            json.dumps({"timestamp": "2026-05-01T00:00:00Z", "event": "MAT.integrated"}) + "\n",
            encoding="utf-8")
        streams["GRO"].write_text(
            json.dumps({"timestamp": "2026-05-03T00:00:00Z", "event": "GRO.assessed"}) + "\n",
            encoding="utf-8")

    def test_query_single_framework(self, query_mod, streams):
        self._seed(streams)
        evs = query_mod.load_events("psy")
        assert len(evs) == 1
        assert evs[0]["event"] == "PSY.refresh"

    def test_query_all_merges_sorted(self, query_mod, streams):
        self._seed(streams)
        evs = query_mod.load_events("all")
        assert len(evs) == 3
        # sorted ascending by timestamp: MAT(05-01) < PSY(05-02) < GRO(05-03)
        assert [e["event"] for e in evs] == ["MAT.integrated", "PSY.refresh", "GRO.assessed"]

    def test_query_missing_stream_returns_empty(self, query_mod, streams):
        evs = query_mod.load_events("cre")  # nothing seeded
        assert evs == []

    def test_stream_tag_added(self, query_mod, streams):
        self._seed(streams)
        evs = query_mod.load_events("mat")
        assert evs[0]["_stream"] == "material-events.jsonl"


class TestLifecycleEmitterRecordShape:
    """The Node emitter writes ORC.session.* records the Python query must read."""
    def test_query_reads_emitter_record(self, query_mod, streams):
        streams["ORC"].write_text(
            json.dumps({"timestamp": "2026-05-25T14:20:50Z",
                        "event": "ORC.session.precompact", "source": "lifecycle"}) + "\n",
            encoding="utf-8")
        evs = query_mod.load_events("orc")
        assert evs[0]["event"] == "ORC.session.precompact"
        assert evs[0]["source"] == "lifecycle"
