"""Integration tests for gateguard sensitivity gating.

gateguard-profile-protect.cjs is registered natively as a PreToolUse(Edit|Write)
hook and exposes a standalone CLI entry (stdin → run() → exit 2 block / exit 0).
These tests pipe Edit/Write/Read JSON to it and assert block/warn/pass behavior.
privacy-block and scout-block are ck-owned hooks with their own native entries —
out of scope here.

Character-agnostic: the profile paths are built from the live roster (paths.ALL_CHARS),
never a hardcoded real slug. Skips when the roster is empty (toolkit-only pack).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
HOOK_PATH = PROJECT_DIR / ".claude" / "hooks" / "gateguard-profile-protect.cjs"
sys.path.insert(0, str(PROJECT_DIR / ".claude" / "scripts"))
from platform_lib.paths import ALL_CHARS

pytestmark = pytest.mark.skipif(not ALL_CHARS, reason="no character roster — toolkit-only pack")

_CHAR = ALL_CHARS[0] if ALL_CHARS else "x"  # any real slug; gating keys off the path zone, not identity
# Throwaway audit sink so blocking-test audit writes never touch the real tracked
# .claude/telemetry/gateguard-audit.jsonl (CK_TELEMETRY_DIR honored by the hook).
_ISO_TELEMETRY = tempfile.mkdtemp(prefix="ck-gateguard-telemetry-")


def run_hook(tool_name: str, file_path: str, env_override: dict | None = None,
             project_dir: Path | None = None) -> subprocess.CompletedProcess:
    """Run the gateguard hook. project_dir redirects CLAUDE_PROJECT_DIR (approval file);
    audit writes are isolated to a throwaway sink unless env_override sets CK_TELEMETRY_DIR."""
    stdin_data = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": file_path}})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir or PROJECT_DIR),
           "CK_TELEMETRY_DIR": _ISO_TELEMETRY}
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["node", str(HOOK_PATH)],
        input=stdin_data, capture_output=True, text=True, env=env,
    )


class TestHookBlocking:
    def test_blocks_critical(self):
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/darkness/traumas.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_blocks_high(self):
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/psychology/formulation.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_warns_medium(self):
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/relationships/family.md")
        assert r.returncode == 0
        assert "GATEGUARD WARN" in r.stderr

    def test_passes_low(self):
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/identity/core.md")
        assert r.returncode == 0
        assert "GATEGUARD" not in r.stderr

    def test_ignores_read_tool(self):
        r = run_hook("Read", f"docs/profiles/{_CHAR}/darkness/traumas.md")
        assert r.returncode == 0
        assert "GATEGUARD" not in r.stderr

    def test_blocks_write_tool(self):
        r = run_hook("Write", f"docs/profiles/{_CHAR}/psychology/diagnostics.md")
        assert r.returncode == 2
        assert "GATEGUARD BLOCK" in r.stderr

    def test_block_message_contains_checks(self):
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/darkness/traumas.md")
        assert "Required checks" in r.stderr
        assert "PSY-darkness" in r.stderr


class TestApprovalFlow:
    def test_approval_bypasses_block(self, tmp_path):
        # Isolated: approval file lives under the tmp project dir, not the real repo.
        approval_path = tmp_path / ".claude" / "session-state" / "gateguard-approved.json"
        rel_path = f"docs/profiles/{_CHAR}/darkness/traumas.md"
        approval_path.parent.mkdir(parents=True, exist_ok=True)
        approval_path.write_text(json.dumps({rel_path: True}))

        r = run_hook("Edit", rel_path, project_dir=tmp_path)
        assert r.returncode == 0
        assert "approved" in r.stderr.lower()

        # Approval is single-use: the consumed entry is removed; when it was the
        # last entry the file itself is deleted.
        if approval_path.exists():
            assert rel_path not in json.loads(approval_path.read_text())


class TestAuditLog:
    def test_audit_log_written_on_block(self, tmp_path):
        # Isolated: CK_TELEMETRY_DIR redirects the audit sink to tmp, never the real
        # tracked .claude/telemetry/gateguard-audit.jsonl.
        sink = tmp_path / "telemetry"
        audit_path = sink / "gateguard-audit.jsonl"

        run_hook("Edit", f"docs/profiles/{_CHAR}/darkness/traumas.md",
                 env_override={"CK_TELEMETRY_DIR": str(sink)})

        assert audit_path.exists()
        last_line = audit_path.read_text().strip().split("\n")[-1]
        entry = json.loads(last_line)
        assert entry["action"] == "blocked"
        assert entry["level"] == "CRITICAL"


class TestHookDisabled:
    def test_passes_when_disabled(self, tmp_path):
        # gateguard reads PROJECT framework-config.json (not ck .ck.json).
        # Isolated tmp project dir with the hook toggled off → hook passes (exit 0).
        cfg_dir = tmp_path / ".claude"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        (cfg_dir / "framework-config.json").write_text(
            json.dumps({"hooks": {"gateguard-profile-protect": False}})
        )
        r = run_hook("Edit", f"docs/profiles/{_CHAR}/darkness/traumas.md",
                     project_dir=tmp_path)
        assert r.returncode == 0


class TestNodeSensitivityChecker:
    def test_classify_file_from_node(self):
        js = (
            "const { classifyFile } = require('./.claude/hooks/lib/sensitivity-checker.cjs');\n"
            f"const r = classifyFile('docs/profiles/{_CHAR}/darkness/traumas.md');\n"
            "console.log(JSON.stringify(r));"
        )
        result = subprocess.run(
            ["node", "-e", js],
            capture_output=True, text=True, cwd=str(PROJECT_DIR),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["level"] == "CRITICAL"
        assert data["zone"] == "PSY-darkness"
