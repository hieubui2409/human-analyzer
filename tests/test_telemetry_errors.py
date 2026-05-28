"""B12 Monitoring I6 — platform_lib.errors structured emission + telemetry excepthook.

In-process the sink is always disabled (conftest sets CK_TELEMETRY_DISABLED and
telemetry._disabled() also trips on PYTEST_CURRENT_TEST), so the WRITE path is
exercised via subprocess with a clean env pointed at a tmp CK_TELEMETRY_DIR. This
both verifies real behavior and proves the disabled-gate keeps pytest side-effect
free (GOLDEN RULE #3).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".claude" / "scripts"


def _run(code: str, telemetry_dir: Path, *, disabled: bool = False) -> subprocess.CompletedProcess:
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(telemetry_dir),  # keep any home-derived path off the real tree
        "CK_TELEMETRY_DIR": str(telemetry_dir),
    }
    if disabled:
        env["CK_TELEMETRY_DISABLED"] = "1"
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)


_PRELUDE = f"import sys; sys.path.insert(0, {str(SCRIPTS)!r})\n"


def test_emit_error_writes_structured_record(tmp_path):
    _run(_PRELUDE + (
        "from platform_lib.errors import emit_error\n"
        "emit_error('parse', 'bad json line', {'file': 'x.md'})\n"
    ), tmp_path)
    rec = json.loads((tmp_path / "errors.jsonl").read_text(encoding="utf-8").strip())
    assert rec["category"] == "parse"
    assert rec["message"] == "bad json line"
    assert rec["context"] == {"file": "x.md"}
    assert "ts" in rec and "script" in rec


def test_emit_error_truncates_long_message(tmp_path):
    _run(_PRELUDE + (
        "from platform_lib.errors import emit_error\n"
        "emit_error('io', 'x' * 500)\n"
    ), tmp_path)
    rec = json.loads((tmp_path / "errors.jsonl").read_text(encoding="utf-8").strip())
    assert len(rec["message"]) == 200


def test_emit_error_noop_when_disabled(tmp_path):
    _run(_PRELUDE + (
        "from platform_lib.errors import emit_error\n"
        "emit_error('parse', 'should not persist')\n"
    ), tmp_path, disabled=True)
    assert not (tmp_path / "errors.jsonl").exists()


def test_excepthook_auto_captures_unhandled_crash(tmp_path):
    # Importing platform_lib triggers telemetry auto-import → excepthook install.
    _run(_PRELUDE + (
        "from platform_lib import paths\n"
        "raise ValueError('boom from test')\n"
    ), tmp_path)
    rec = json.loads((tmp_path / "errors.jsonl").read_text(encoding="utf-8").strip())
    assert rec["category"] == "unhandled"
    assert "ValueError" in rec["message"] and "boom from test" in rec["message"]
    assert "frame" in rec["context"]
