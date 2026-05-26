"""Isolated tests for B10 B3/C5 units — orc:observe emitter + compact-digest + the 2 project hooks.

No shared state: each test redirects the module's output paths to tmp_path (Python units) or runs
the hook as a node subprocess with CLAUDE_PROJECT_DIR pointed at a sandbox. The hooks must fail-open
(always { continue: true }) and carry NO ck-config-utils dependency (CAP-1).
"""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SK = PROJECT_ROOT / ".claude" / "skills"
HOOKS = PROJECT_ROOT / ".claude" / "hooks"
EMIT = SK / "orc-observe" / "scripts" / "emit-framework-observation-signal.py"
DIGEST = SK / "orc-session-state" / "scripts" / "write-framework-delta-compact-digest.py"
OBSERVE_HOOK = HOOKS / "observe-framework-signal.cjs"
COMPACT_HOOK = HOOKS / "write-framework-delta-compact-digest.cjs"
NODE = shutil.which("node")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── B3 emitter (Python unit) ──────────────────────────────────────────────────

def test_emit_valid_signal_appends(tmp_path):
    mod = _load(EMIT, "emit_obs")
    mod.OBSERVATIONS = tmp_path / "observations.jsonl"
    rec = mod.emit("psy", "defense-pattern", {"character": "hoa"}, "test")
    assert rec["framework"] == "psy" and rec["signal"] == "defense-pattern"
    lines = (tmp_path / "observations.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["payload"]["character"] == "hoa"


def test_emit_rejects_unknown_framework(tmp_path):
    mod = _load(EMIT, "emit_obs2")
    mod.OBSERVATIONS = tmp_path / "o.jsonl"
    with pytest.raises(ValueError):
        mod.emit("xxx", "defense-pattern", {}, "t")
    assert not (tmp_path / "o.jsonl").exists()  # no write on rejection


def test_emit_rejects_unknown_signal_and_oversized(tmp_path):
    mod = _load(EMIT, "emit_obs3")
    mod.OBSERVATIONS = tmp_path / "o.jsonl"
    with pytest.raises(ValueError):
        mod.emit("psy", "not-a-signal", {}, "t")
    with pytest.raises(ValueError):
        mod.emit("psy", "core-wound", {"big": "x" * 3000}, "t")  # > 2 KB cap


# ── C5 compact-digest (Python unit) ─────────────────────────────────────────────

def test_digest_bounded_and_has_all_frameworks(tmp_path, monkeypatch):
    mod = _load(DIGEST, "digest_mod")
    # redirect every stream + outputs into the sandbox
    psy = tmp_path / "character-events.jsonl"
    psy.write_text("\n".join(
        json.dumps({"ts": f"t{i}", "event_type": "PSY.refresh", "source": "psy:wave"})
        for i in range(20)) + "\n", encoding="utf-8")
    mod.FRAMEWORK_STREAMS = {
        "PSY": (psy, "wave findings"),
        "MAT": (tmp_path / "mat.jsonl", "materials"),
        "CRE": (tmp_path / "cre.jsonl", "content"),
        "GRO": (tmp_path / "gro.jsonl", "growth"),
        "ORC": (tmp_path / "orc.jsonl", "events"),
        "COM": (tmp_path / "com.jsonl", "governance"),
    }
    mod.OBSERVATIONS = tmp_path / "observations.jsonl"
    d = mod.build_digest(top_n=5, max_bytes=8000)
    assert set(d["frameworks"]) == {"PSY", "MAT", "CRE", "GRO", "ORC", "COM"}
    assert d["frameworks"]["PSY"]["count"] == 5  # top-N capped from 20
    assert len(json.dumps(d).encode("utf-8")) <= 8000


def test_digest_byte_cap_truncates(tmp_path):
    mod = _load(DIGEST, "digest_mod2")
    big = tmp_path / "psy.jsonl"
    big.write_text("\n".join(
        json.dumps({"ts": f"t{i}", "event_type": "PSY.refresh",
                    "reason": "x" * 200, "source": "s"}) for i in range(10)) + "\n",
        encoding="utf-8")
    mod.FRAMEWORK_STREAMS = {"PSY": (big, "c")}
    mod.OBSERVATIONS = tmp_path / "none.jsonl"
    d = mod.build_digest(top_n=10, max_bytes=600)
    assert d.get("truncated") is True
    assert len(json.dumps(d).encode("utf-8")) <= 600 or d["top_n"] == 1


# ── Project hooks (node subprocess) — fail-open + CAP-1 ─────────────────────────

@pytest.mark.skipif(NODE is None, reason="node not available")
def test_observe_hook_routes_profile_edit(tmp_path):
    payload = json.dumps({"tool_name": "Edit",
                          "tool_input": {"file_path": "docs/profiles/hoa/psychology/formulation.md"}})
    r = subprocess.run([NODE, str(OBSERVE_HOOK)], input=payload, capture_output=True,
                       text=True, env={"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert json.loads(r.stdout)["continue"] is True
    obs = tmp_path / ".claude" / "telemetry" / "observations.jsonl"
    rec = json.loads(obs.read_text().strip())
    assert rec["framework"] == "psy" and rec["signal"] == "profile-touched"


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_observe_hook_skips_non_framework_path(tmp_path):
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "README.md"}})
    r = subprocess.run([NODE, str(OBSERVE_HOOK)], input=payload, capture_output=True,
                       text=True, env={"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert json.loads(r.stdout)["continue"] is True
    assert not (tmp_path / ".claude" / "telemetry" / "observations.jsonl").exists()


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_compact_hook_failopen_when_script_missing(tmp_path):
    # sandbox has no script → hook must still emit continue:true (never block compaction)
    r = subprocess.run([NODE, str(COMPACT_HOOK)], input="{}", capture_output=True,
                       text=True, env={"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert json.loads(r.stdout)["continue"] is True


def test_new_hooks_have_no_ck_config_utils_require():
    for hook in (OBSERVE_HOOK, COMPACT_HOOK):
        src = hook.read_text(encoding="utf-8")
        # no require() of ck-config-utils (mentions in comments are fine)
        import re
        assert not re.search(r"require\([\"'][^\"']*ck-config-utils", src), hook.name
