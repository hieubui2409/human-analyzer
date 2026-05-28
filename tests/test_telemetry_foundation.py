"""B12 Monitoring Phase 1 — instrumentation foundation (I1 hook + I4 telemetry.py).

Isolated: redirects the telemetry sink to tmp_path and controls CK_TELEMETRY_DISABLED
explicitly per test (conftest sets it globally, so the enabled-path tests clear it).
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
I1_HOOK = PROJECT_DIR / ".claude" / "hooks" / "track-skill-invocation.cjs"
NODE = shutil.which("node")


# ── I4: platform_lib/telemetry.py ───────────────────────────────────────────

def test_disabled_is_noop(monkeypatch, tmp_path):
    import platform_lib.telemetry as t
    monkeypatch.setenv("CK_TELEMETRY_DISABLED", "1")
    monkeypatch.setattr(t, "TELEMETRY_DIR", tmp_path / "telemetry")
    t.append_event("x.jsonl", {"a": 1})
    assert not (tmp_path / "telemetry" / "x.jsonl").exists()


def test_pytest_env_disables(monkeypatch):
    import platform_lib.telemetry as t
    # PYTEST_CURRENT_TEST is set by pytest during a test → disabled even w/o the flag
    monkeypatch.delenv("CK_TELEMETRY_DISABLED", raising=False)
    assert t._disabled() is True


def test_append_event_when_enabled(monkeypatch, tmp_path):
    import platform_lib.telemetry as t
    monkeypatch.delenv("CK_TELEMETRY_DISABLED", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)  # force enabled
    monkeypatch.setattr(t, "TELEMETRY_DIR", tmp_path / "telemetry")
    t.append_event("events.jsonl", {"skill": "psy:crossref", "vn": "Hội chứng"})
    rec = json.loads((tmp_path / "telemetry" / "events.jsonl").read_text().strip())
    assert rec["skill"] == "psy:crossref" and rec["vn"] == "Hội chứng"


def test_sink_path_under_root(monkeypatch, tmp_path):
    import platform_lib.telemetry as t
    monkeypatch.setattr(t, "TELEMETRY_DIR", tmp_path / "telemetry")
    assert t.sink_path("foo.jsonl") == tmp_path / "telemetry" / "foo.jsonl"


def test_rotation_when_oversized(monkeypatch, tmp_path):
    import platform_lib.telemetry as t
    monkeypatch.delenv("CK_TELEMETRY_DISABLED", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(t, "TELEMETRY_DIR", tmp_path / "telemetry")
    monkeypatch.setattr(t, "_MAX_SINK_BYTES", 10)  # tiny threshold
    t.append_event("r.jsonl", {"pad": "x" * 50})  # first write exceeds next time
    t.append_event("r.jsonl", {"second": True})
    assert (tmp_path / "telemetry" / "r.jsonl.bak").exists()


# ── I1: track-skill-invocation.cjs (node subprocess) ─────────────────────────

def _run_i1(payload: str, env_extra: dict, tmp_path: Path):
    env = {"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin"}
    env.update(env_extra)
    return subprocess.run([NODE, str(I1_HOOK)], input=payload, capture_output=True,
                          text=True, env=env)


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_i1_records_invocation(tmp_path):
    payload = json.dumps({"tool_name": "Skill",
                          "tool_input": {"skill": "psy:crossref", "args": "--all"},
                          "session_id": "sess-1"})
    r = _run_i1(payload, {}, tmp_path)
    assert json.loads(r.stdout)["continue"] is True
    rec = json.loads((tmp_path / ".claude" / "telemetry" / "invocations.jsonl").read_text().strip())
    assert rec["skill"] == "psy:crossref" and rec["session"] == "sess-1" and rec["args"] == "--all"


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_i1_disabled_no_write(tmp_path):
    payload = json.dumps({"tool_name": "Skill", "tool_input": {"skill": "psy:crossref"}})
    r = _run_i1(payload, {"CK_TELEMETRY_DISABLED": "1"}, tmp_path)
    assert json.loads(r.stdout)["continue"] is True
    assert not (tmp_path / ".claude" / "telemetry" / "invocations.jsonl").exists()


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_i1_skips_when_no_skill(tmp_path):
    r = _run_i1(json.dumps({"tool_name": "Skill", "tool_input": {}}), {}, tmp_path)
    assert json.loads(r.stdout)["continue"] is True
    assert not (tmp_path / ".claude" / "telemetry" / "invocations.jsonl").exists()
