"""B12 Monitoring P6/P7 hooks — I2 (track-script-execution), I3 (emit-session-summary),
M4 (detect-profile-drift-hook). Each .cjs hook is driven via a real `node` subprocess
with mock stdin + an isolated CK_TELEMETRY_DIR, so sink writes never touch the repo.
Skipped automatically if node is unavailable.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _run_hook(name: str, stdin_obj: dict, env_extra: dict) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), **env_extra}
    return subprocess.run(
        [NODE, str(HOOKS / name)],
        input=json.dumps(stdin_obj), capture_output=True, text=True, env=env,
    )


# --- I2: track-script-execution -----------------------------------------------

def test_i2_logs_skill_script(tmp_path):
    out = _run_hook("track-script-execution.cjs",
                    {"tool_input": {"command": "python3 .claude/skills/psy-crossref/scripts/run.py --json"},
                     "tool_response": {"stderr": ""}},
                    {"CK_TELEMETRY_DIR": str(tmp_path)})
    assert json.loads(out.stdout)["continue"] is True
    rec = json.loads((tmp_path / "hook-telemetry.jsonl").read_text().strip())
    assert rec["script"] == "psy-crossref/scripts/run.py"
    assert rec["exit"] == 0


def test_i2_infers_error_exit(tmp_path):
    _run_hook("track-script-execution.cjs",
              {"tool_input": {"command": "python3 .claude/skills/mat-loader/scripts/x.py"},
               "tool_response": {"stderr": "Traceback (most recent call last): ValueError"}},
              {"CK_TELEMETRY_DIR": str(tmp_path)})
    rec = json.loads((tmp_path / "hook-telemetry.jsonl").read_text().strip())
    assert rec["exit"] == 1


def test_i2_skips_non_skill_command(tmp_path):
    _run_hook("track-script-execution.cjs",
              {"tool_input": {"command": "git status"}},
              {"CK_TELEMETRY_DIR": str(tmp_path)})
    assert not (tmp_path / "hook-telemetry.jsonl").exists()


def test_i2_noop_when_disabled(tmp_path):
    _run_hook("track-script-execution.cjs",
              {"tool_input": {"command": "python3 .claude/skills/com-git/scripts/x.py"}},
              {"CK_TELEMETRY_DIR": str(tmp_path), "CK_TELEMETRY_DISABLED": "1"})
    assert not (tmp_path / "hook-telemetry.jsonl").exists()


# --- I3: emit-session-summary --------------------------------------------------

def test_i3_emits_session_summary(tmp_path):
    proj = "/tmp/ckproj"
    slug = proj.replace("/", "-")
    home = tmp_path / "home"
    sess_dir = home / ".claude" / "projects" / slug
    sess_dir.mkdir(parents=True)
    (sess_dir / "sess1.jsonl").write_text("\n".join([
        json.dumps({"timestamp": "2026-05-26T10:00:00Z",
                    "message": {"content": [{"type": "tool_use", "name": "Skill",
                                             "input": {"skill": "com:git"}}]}}),
        json.dumps({"message": {"usage": {"input_tokens": 100, "output_tokens": 50}}}),
        json.dumps({"message": {"content": [{"type": "tool_use", "name": "Edit",
                                             "input": {"file_path": "/x/a.py"}}]}}),
        json.dumps({"timestamp": "2026-05-26T10:30:00Z",
                    "message": {"content": [{"type": "tool_use", "name": "Task", "input": {}}]}}),
    ]) + "\n", encoding="utf-8")
    tel = tmp_path / "tel"
    out = _run_hook("emit-session-summary.cjs", {"session_id": "sess1"},
                    {"HOME": str(home), "CLAUDE_PROJECT_DIR": proj, "CK_TELEMETRY_DIR": str(tel),
                     "CK_SESSION_ID": "sess1"})
    assert json.loads(out.stdout)["continue"] is True
    rec = json.loads((tel / "sessions.jsonl").read_text().strip())
    assert rec["session"] == "sess1"
    assert rec["skills"] == ["com:git"]
    assert rec["files_modified"] == 1
    assert rec["subagents"] == 1
    assert rec["tokens"]["input"] == 100
    assert rec["duration_s"] == 1800


def test_i3_noop_when_disabled(tmp_path):
    proj = "/tmp/ckproj2"
    slug = proj.replace("/", "-")
    home = tmp_path / "home"
    sess_dir = home / ".claude" / "projects" / slug
    sess_dir.mkdir(parents=True)
    (sess_dir / "s.jsonl").write_text(
        json.dumps({"message": {"usage": {"input_tokens": 1, "output_tokens": 1}}}) + "\n",
        encoding="utf-8")
    tel = tmp_path / "tel"
    _run_hook("emit-session-summary.cjs", {"session_id": "s"},
              {"HOME": str(home), "CLAUDE_PROJECT_DIR": proj, "CK_TELEMETRY_DIR": str(tel),
               "CK_SESSION_ID": "s", "CK_TELEMETRY_DISABLED": "1"})
    assert not (tel / "sessions.jsonl").exists()


# --- M4: detect-profile-drift-hook (integration, real script, read-only) -------

def test_m4_hook_early_returns_non_profile(tmp_path):
    out = _run_hook("detect-profile-drift-hook.cjs",
                    {"tool_input": {"file_path": "README.md"}},
                    {"CLAUDE_PROJECT_DIR": str(ROOT)})
    result = json.loads(out.stdout)
    assert result["continue"] is True
    assert "additionalContext" not in result


def test_m4_hook_reports_drift_on_profile(tmp_path):
    # Self-contained: a file whose path contains docs/profiles/ (so the hook's
    # path guard matches) with a deliberately broken internal link. Uses the real
    # script via CLAUDE_PROJECT_DIR=ROOT but an external target file.
    target = tmp_path / "docs" / "profiles" / "tchar" / "identity" / "core.md"
    target.parent.mkdir(parents=True)
    target.write_text("Has a [bad](./does-not-exist.md) link.", encoding="utf-8")
    out = _run_hook("detect-profile-drift-hook.cjs",
                    {"tool_input": {"file_path": str(target)}},
                    {"CLAUDE_PROJECT_DIR": str(ROOT)})
    result = json.loads(out.stdout)
    assert result["continue"] is True
    assert "Profile Drift" in result.get("additionalContext", "")


# --- context-budget-gauge (UserPromptSubmit, 70/85 tiers) ----------------------

def _gauge(tmp_path, input_tokens, **env):
    transcript = tmp_path / "t.jsonl"
    transcript.write_text(
        json.dumps({"message": {"usage": {"input_tokens": input_tokens}}}) + "\n",
        encoding="utf-8")
    return _run_hook("context-budget-gauge.cjs",
                     {"transcript_path": str(transcript)},
                     {"CK_TELEMETRY_DIR": str(tmp_path / "tel"),
                      "CK_CONTEXT_WINDOW": "200000", "CK_CONTEXT_NEXT_EST": "25000",
                      **env})


def test_gauge_force_tier(tmp_path):
    out = _gauge(tmp_path, 180000)
    r = json.loads(out.stdout)
    assert "85%" in r["additionalContext"]
    rec = json.loads((tmp_path / "tel" / "context-gauge.jsonl").read_text().strip())
    assert rec["pct"] == 0.9


def test_gauge_warn_tier(tmp_path):
    out = _gauge(tmp_path, 130000)
    r = json.loads(out.stdout)
    assert "70%" in r["additionalContext"] and "85%" not in r["additionalContext"]


def test_gauge_quiet_when_low(tmp_path):
    out = _gauge(tmp_path, 50000)
    r = json.loads(out.stdout)
    assert "additionalContext" not in r


def test_gauge_noop_when_disabled(tmp_path):
    _gauge(tmp_path, 180000, CK_TELEMETRY_DISABLED="1")
    assert not (tmp_path / "tel" / "context-gauge.jsonl").exists()
