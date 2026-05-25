"""Integration tests for gateguard sensitivity gating (Batch 2 A3) via the
consolidated hook-dispatcher (Batch 5 B1).

The sub-hooks no longer have standalone CLI entries — they are composed by
hook-dispatcher.cjs. These tests pipe Edit/Write/Read JSON to the dispatcher and
assert the gateguard behavior (block/warn/pass) plus privacy/scout regression.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
HOOK_PATH = PROJECT_DIR / ".claude" / "hooks" / "hook-dispatcher.cjs"
AUDIT_LOG_DIR = PROJECT_DIR / ".claude" / "logs"


def run_hook(tool_name: str, file_path: str, env_override: dict | None = None) -> subprocess.CompletedProcess:
    stdin_data = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": file_path}})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(PROJECT_DIR)}
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["node", str(HOOK_PATH)],
        input=stdin_data, capture_output=True, text=True, env=env,
    )


class TestHookBlocking:
    def test_blocks_critical(self):
        r = run_hook("Edit", "docs/profiles/character-a/darkness/traumas.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_blocks_high(self):
        r = run_hook("Edit", "docs/profiles/character-a/psychology/formulation.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_warns_medium(self):
        r = run_hook("Edit", "docs/profiles/character-a/relationships/family.md")
        assert r.returncode == 0
        assert "GATEGUARD WARN" in r.stderr

    def test_passes_low(self):
        r = run_hook("Edit", "docs/profiles/character-a/identity/core.md")
        assert r.returncode == 0
        assert "GATEGUARD" not in r.stderr

    def test_ignores_read_tool(self):
        r = run_hook("Read", "docs/profiles/character-a/darkness/traumas.md")
        assert r.returncode == 0
        assert "GATEGUARD" not in r.stderr

    def test_blocks_write_tool(self):
        r = run_hook("Write", "docs/profiles/character-a/psychology/diagnostics.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_block_message_contains_checks(self):
        r = run_hook("Edit", "docs/profiles/character-a/darkness/traumas.md")
        assert "Required checks" in r.stderr
        assert "PSY-darkness" in r.stderr


class TestApprovalFlow:
    def test_approval_bypasses_block(self):
        approval_path = PROJECT_DIR / ".claude" / "session-state" / "gateguard-approved.json"
        rel_path = "docs/profiles/character-a/darkness/traumas.md"
        try:
            approval_path.parent.mkdir(parents=True, exist_ok=True)
            approval_path.write_text(json.dumps({rel_path: True}))

            r = run_hook("Edit", rel_path)
            assert r.returncode == 0
            assert "approved" in r.stderr.lower()

            if approval_path.exists():
                remaining = json.loads(approval_path.read_text())
                assert rel_path not in remaining
        finally:
            if approval_path.exists():
                approval_path.unlink()


class TestAuditLog:
    def test_audit_log_written_on_block(self):
        audit_path = AUDIT_LOG_DIR / "gateguard-audit.jsonl"
        if audit_path.exists():
            before_size = audit_path.stat().st_size
        else:
            before_size = 0

        run_hook("Edit", "docs/profiles/character-a/darkness/traumas.md")

        assert audit_path.exists()
        assert audit_path.stat().st_size > before_size
        last_line = audit_path.read_text().strip().split("\n")[-1]
        entry = json.loads(last_line)
        assert entry["action"] == "blocked"
        assert entry["level"] == "CRITICAL"


class TestHookDisabled:
    def test_passes_when_disabled(self):
        ck_config_path = PROJECT_DIR / ".claude" / ".ck.json"
        backup = None
        if ck_config_path.exists():
            backup = ck_config_path.read_text()

        try:
            if ck_config_path.exists():
                config = json.loads(ck_config_path.read_text())
            else:
                config = {}
            config.setdefault("hooks", {})["gateguard-profile-protect"] = False
            ck_config_path.write_text(json.dumps(config))

            r = run_hook("Edit", "docs/profiles/character-a/darkness/traumas.md")
            assert r.returncode == 0
        finally:
            if backup is not None:
                ck_config_path.write_text(backup)
            elif ck_config_path.exists():
                ck_config_path.unlink()


class TestNodeSensitivityChecker:
    def test_classify_file_from_node(self):
        result = subprocess.run(
            ["node", "-e", """
const { classifyFile } = require('./.claude/hooks/lib/sensitivity-checker.cjs');
const r = classifyFile('docs/profiles/character-a/darkness/traumas.md');
console.log(JSON.stringify(r));
"""],
            capture_output=True, text=True, cwd=str(PROJECT_DIR),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["level"] == "CRITICAL"
        assert data["zone"] == "PSY-darkness"


class TestRegressionExistingHooks:
    """privacy + scout still block through the consolidated dispatcher."""

    def test_privacy_block_still_works(self):
        r = run_hook("Edit", ".env")
        assert r.returncode == 2
        assert "PRIVACY BLOCK" in r.stderr

    def test_scout_block_still_works(self):
        r = run_hook("Read", "node_modules/package/index.js")
        assert r.returncode == 2
