"""Comprehensive test suite for com:health-check monitor."""
import importlib.util
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


core = _load_module("core", "monitor-session-health-core.py")
targets = _load_module("targets", "monitor-session-health-targets.py")

ErrorClass = core.ErrorClass
Severity = core.Severity
HealthEvent = core.HealthEvent
SessionPaths = core.SessionPaths
MonitorConfig = core.MonitorConfig


# ---------------------------------------------------------------------------
# Unit Tests: read_last_jsonl_line
# ---------------------------------------------------------------------------
class TestReadLastJsonlLine:
    def test_normal_file(self):
        result = core.read_last_jsonl_line(FIXTURES_DIR / "session-normal.jsonl")
        assert result is not None
        assert result["type"] == "assistant"
        assert result["uuid"] == "r1"

    def test_empty_file(self):
        result = core.read_last_jsonl_line(FIXTURES_DIR / "session-empty.jsonl")
        assert result is None

    def test_truncated_last_line(self):
        result = core.read_last_jsonl_line(FIXTURES_DIR / "session-truncated.jsonl")
        assert result is not None
        assert result["type"] == "user"

    def test_single_line(self):
        result = core.read_last_jsonl_line(FIXTURES_DIR / "session-429-rate-limit.jsonl")
        assert result is not None
        assert result["type"] == "assistant"

    def test_missing_file(self):
        result = core.read_last_jsonl_line(Path("/nonexistent/file.jsonl"))
        assert result is None

    def test_none_path(self):
        result = core.read_last_jsonl_line(None)
        assert result is None


# ---------------------------------------------------------------------------
# Unit Tests: extract_error_text
# ---------------------------------------------------------------------------
class TestExtractErrorText:
    def test_toolUseResult_location(self):
        line = json.loads((FIXTURES_DIR / "session-api-error.jsonl").read_text().strip().split("\n")[-1])
        texts = core.extract_error_text(line)
        assert any("API Error" in t for t in texts)

    def test_message_content_location(self):
        line = json.loads((FIXTURES_DIR / "session-api-error-in-message.jsonl").read_text().strip().split("\n")[-1])
        texts = core.extract_error_text(line)
        assert any("Internal Server Error" in t for t in texts)

    def test_normal_content(self):
        line = json.loads((FIXTURES_DIR / "session-normal.jsonl").read_text().strip().split("\n")[-1])
        texts = core.extract_error_text(line)
        assert all("Error" not in t for t in texts)

    def test_empty_dict(self):
        assert core.extract_error_text({}) == []


# ---------------------------------------------------------------------------
# Unit Tests: classify_error
# ---------------------------------------------------------------------------
class TestClassifyError:
    def test_api_error_retryable(self):
        assert core.classify_error(["API Error: JSON Parse error"]) == ErrorClass.RETRYABLE

    def test_unexpected_eof_retryable(self):
        assert core.classify_error(["Unexpected EOF"]) == ErrorClass.RETRYABLE

    def test_econnreset_retryable(self):
        assert core.classify_error(["ECONNRESET"]) == ErrorClass.RETRYABLE

    def test_socket_hangup_retryable(self):
        assert core.classify_error(["socket hang up"]) == ErrorClass.RETRYABLE

    def test_internal_server_error_retryable(self):
        assert core.classify_error(["Internal Server Error"]) == ErrorClass.RETRYABLE

    def test_service_unavailable_retryable(self):
        assert core.classify_error(["Service Unavailable"]) == ErrorClass.RETRYABLE

    def test_429_time_retryable_when_enabled(self):
        assert core.classify_error(["429 Too Many Requests"], include_429=True) == ErrorClass.TIME_RETRYABLE

    def test_429_ignored_when_disabled(self):
        assert core.classify_error(["429 Too Many Requests"], include_429=False) == ErrorClass.NONE

    def test_rate_limit_time_retryable(self):
        assert core.classify_error(["Rate limit exceeded"], include_429=True) == ErrorClass.TIME_RETRYABLE

    def test_context_length_non_retryable(self):
        assert core.classify_error(["context_length_exceeded"]) == ErrorClass.NON_RETRYABLE

    def test_invalid_api_key_non_retryable(self):
        assert core.classify_error(["invalid_api_key"]) == ErrorClass.NON_RETRYABLE

    def test_billing_non_retryable(self):
        assert core.classify_error(["billing error"]) == ErrorClass.NON_RETRYABLE

    def test_credit_non_retryable(self):
        assert core.classify_error(["credit exhausted"]) == ErrorClass.NON_RETRYABLE

    def test_normal_content_no_error(self):
        assert core.classify_error(["hello world"]) == ErrorClass.NONE

    def test_empty_text_no_error(self):
        assert core.classify_error([""]) == ErrorClass.NONE

    def test_non_retryable_takes_priority(self):
        """Non-retryable checked before retryable."""
        assert core.classify_error(["API Error and invalid_api_key"]) == ErrorClass.NON_RETRYABLE


# ---------------------------------------------------------------------------
# Unit Tests: check_process_liveness
# ---------------------------------------------------------------------------
class TestCheckProcessLiveness:
    def test_own_pid_alive(self):
        assert core.check_process_liveness(os.getpid()) is True

    def test_nonexistent_pid_dead(self):
        assert core.check_process_liveness(999999) is False

    def test_permission_error_treated_as_alive(self):
        with patch("os.kill", side_effect=PermissionError):
            assert core.check_process_liveness(1) is True


# ---------------------------------------------------------------------------
# Unit Tests: check_file_freshness
# ---------------------------------------------------------------------------
class TestCheckFileFreshness:
    def test_fresh_file_ok(self, tmp_path):
        f = tmp_path / "fresh.jsonl"
        f.write_text("{}")
        result = core.check_file_freshness(f, soft=120, hard=300)
        assert result is None

    def test_soft_threshold_warn(self, tmp_path):
        f = tmp_path / "stale.jsonl"
        f.write_text("{}")
        os.utime(f, (time.time() - 150, time.time() - 150))
        result = core.check_file_freshness(f, soft=120, hard=300)
        assert result is not None
        assert result.severity == Severity.WARN
        assert result.category == "STALL"

    def test_hard_threshold_error(self, tmp_path):
        f = tmp_path / "very-stale.jsonl"
        f.write_text("{}")
        os.utime(f, (time.time() - 350, time.time() - 350))
        result = core.check_file_freshness(f, soft=120, hard=300)
        assert result is not None
        assert result.severity == Severity.ERROR
        assert result.category == "STALL"

    def test_custom_thresholds(self, tmp_path):
        f = tmp_path / "custom.jsonl"
        f.write_text("{}")
        os.utime(f, (time.time() - 70, time.time() - 70))
        result = core.check_file_freshness(f, soft=60, hard=180)
        assert result is not None
        assert result.severity == Severity.WARN

    def test_missing_file(self):
        result = core.check_file_freshness(Path("/nonexistent"), soft=120, hard=300)
        assert result is None

    def test_none_path(self):
        result = core.check_file_freshness(None, soft=120, hard=300)
        assert result is None


# ---------------------------------------------------------------------------
# Unit Tests: emit + format_event
# ---------------------------------------------------------------------------
class TestEmit:
    def test_output_format(self):
        event = HealthEvent(Severity.ERROR, "API_ERROR", "main-agent", "test message")
        formatted = core.format_event(event)
        assert "[ERROR]" in formatted
        assert "API_ERROR" in formatted
        assert "main-agent" in formatted
        assert "test message" in formatted

    def test_error_verbosity_shows_error_only(self, capsys):
        error_ev = HealthEvent(Severity.ERROR, "X", "t", "m")
        warn_ev = HealthEvent(Severity.WARN, "X", "t", "m")
        info_ev = HealthEvent(Severity.INFO, "X", "t", "m")
        assert core.emit(error_ev, Severity.ERROR) is True
        assert core.emit(warn_ev, Severity.ERROR) is False
        assert core.emit(info_ev, Severity.ERROR) is False

    def test_warn_verbosity_shows_error_and_warn(self):
        error_ev = HealthEvent(Severity.ERROR, "X", "t", "m")
        warn_ev = HealthEvent(Severity.WARN, "X", "t", "m")
        info_ev = HealthEvent(Severity.INFO, "X", "t", "m")
        assert core.emit(error_ev, Severity.WARN) is True
        assert core.emit(warn_ev, Severity.WARN) is True
        assert core.emit(info_ev, Severity.WARN) is False

    def test_info_verbosity_shows_info(self):
        info_ev = HealthEvent(Severity.INFO, "X", "t", "m")
        debug_ev = HealthEvent(Severity.DEBUG, "X", "t", "m")
        assert core.emit(info_ev, Severity.INFO) is True
        assert core.emit(debug_ev, Severity.INFO) is False

    def test_debug_verbosity_shows_all(self):
        debug_ev = HealthEvent(Severity.DEBUG, "X", "t", "m")
        assert core.emit(debug_ev, Severity.DEBUG) is True

    def test_stdout_flush(self, capsys):
        event = HealthEvent(Severity.ERROR, "TEST", "t", "flush check")
        core.emit(event, Severity.ERROR)
        captured = capsys.readouterr()
        assert "flush check" in captured.out


# ---------------------------------------------------------------------------
# Unit Tests: resolve_project_slug
# ---------------------------------------------------------------------------
class TestResolveProjectSlug:
    def test_converts_path_to_slug(self):
        slug = core.resolve_project_slug("/home/user/project")
        assert slug == "-home-user-project"

    def test_keeps_leading_dash(self):
        slug = core.resolve_project_slug("/home/user/human-analyzer")
        assert slug.startswith("-")


# ---------------------------------------------------------------------------
# Integration Tests: check_main_agent
# ---------------------------------------------------------------------------
class TestMainAgentMonitoring:
    def test_healthy_session(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(verbosity=Severity.INFO)
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "OK" for e in events)

    def test_stalled_session_soft(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 150, time.time() - 150))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_main_agent(sp, config)
        assert any(e.severity.name == "WARN" and e.category == "STALL" for e in events)

    def test_stalled_session_hard(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 350, time.time() - 350))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_main_agent(sp, config)
        assert any(e.severity.name == "ERROR" and e.category == "STALL" for e in events)

    def test_api_error_detection(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-api-error.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "API_ERROR" and "retryable" in e.message for e in events)

    def test_api_error_in_message_content(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-api-error-in-message.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "API_ERROR" for e in events)

    def test_dead_process(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-normal.jsonl", jsonl)
        pid_file = tmp_path / "pid.json"
        pid_file.write_text('{"pid": 999999, "sessionId": "test"}')
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)

    def test_non_retryable_error(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-non-retryable.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any("non-retryable" in e.message for e in events)

    def test_rate_limit_with_flag(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-429-rate-limit.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(include_429=True)
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "RATE_LIMIT" for e in events)


# ---------------------------------------------------------------------------
# Integration Tests: subagent monitoring
# ---------------------------------------------------------------------------
class TestSubagentMonitoring:
    def test_discovers_subagent_files(self, tmp_path):
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        (subdir / "agent-abc.jsonl").write_text('{"type":"assistant"}\n')
        (subdir / "agent-xyz.jsonl").write_text('{"type":"assistant"}\n')
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")
        files = targets.discover_subagent_files(sp)
        assert len(files) == 2

    def test_subagent_api_error(self, tmp_path):
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "session-api-error.jsonl", subdir / "agent-broken.jsonl")
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")
        config = MonitorConfig()
        events = targets.check_subagents(sp, config)
        assert any(e.category == "API_ERROR" for e in events)

    def test_subagent_stall(self, tmp_path):
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-slow.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", f)
        os.utime(f, (time.time() - 150, time.time() - 150))
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_subagents(sp, config)
        assert any(e.category == "STALL" for e in events)

    def test_no_subagents_silent(self, tmp_path):
        sp = SessionPaths(jsonl=tmp_path / "test.jsonl", session_id="test")
        (tmp_path / "test.jsonl").write_text("{}\n")
        config = MonitorConfig()
        events = targets.check_subagents(sp, config)
        assert len(events) == 0


# ---------------------------------------------------------------------------
# Integration Tests: team monitoring
# ---------------------------------------------------------------------------
class TestTeamMonitoring:
    def test_parses_team_config(self, tmp_path):
        teams_dir = tmp_path / ".claude" / "teams" / "test-team"
        teams_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "team-config.json", teams_dir / "config.json")
        config_data = json.loads((teams_dir / "config.json").read_text())
        assert len(config_data["members"]) == 2
        assert config_data["members"][1]["backendType"] == "tmux"

    def test_missing_team_config(self):
        sp = SessionPaths(project_slug="-test-slug")
        config = MonitorConfig(team_name="nonexistent-team-xyz")
        with patch.object(Path, "home", return_value=Path("/tmp/fake-home-missing")):
            events = targets.check_team_agents(sp, config)
        assert any(e.category == "TEAM" and "config not found" in e.message for e in events)

    def test_resolves_team_jsonl_by_metadata(self, tmp_path):
        project_dir = tmp_path / ".claude" / "projects" / "-test-slug"
        project_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "team-agent-attachment.jsonl", project_dir / "team-session.jsonl")
        with patch.object(Path, "home", return_value=tmp_path):
            result = targets.resolve_team_member_jsonl("-test-slug", "test-team", "test-scout")
        assert result is not None
        assert result.name == "team-session.jsonl"

    def test_team_member_no_jsonl_found(self, tmp_path):
        project_dir = tmp_path / ".claude" / "projects" / "-test-slug"
        project_dir.mkdir(parents=True)
        teams_dir = tmp_path / ".claude" / "teams" / "test-team"
        teams_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "team-config.json", teams_dir / "config.json")
        sp = SessionPaths(project_slug="-test-slug")
        config = MonitorConfig(team_name="test-team")
        with patch.object(Path, "home", return_value=tmp_path):
            events = targets.check_team_agents(sp, config)
        assert any("no JSONL found" in e.message for e in events)

    def test_no_team_name_returns_empty(self):
        sp = SessionPaths()
        config = MonitorConfig(team_name="")
        events = targets.check_team_agents(sp, config)
        assert len(events) == 0


# ---------------------------------------------------------------------------
# Integration Tests: lockfile
# ---------------------------------------------------------------------------
class TestLockfile:
    def _load_cli(self):
        return _load_module("cli", "monitor-session-health.py")

    def test_creates_lockfile_on_start(self):
        cli = self._load_cli()
        lock = cli.create_lockfile("test-lock-create", "main")
        try:
            assert lock.exists()
            assert lock.read_text().strip() == str(os.getpid())
        finally:
            lock.unlink(missing_ok=True)

    def test_rejects_if_lockfile_active(self):
        cli = self._load_cli()
        lock_path = Path(f"/tmp/claude-health-test-lock-reject-main.lock")
        lock_path.write_text(str(os.getpid()))
        try:
            with pytest.raises(SystemExit):
                cli.create_lockfile("test-lock-reject", "main")
        finally:
            lock_path.unlink(missing_ok=True)

    def test_cleans_stale_lockfile(self):
        cli = self._load_cli()
        lock_path = Path(f"/tmp/claude-health-test-lock-stale-main.lock")
        lock_path.write_text("999999")
        try:
            lock = cli.create_lockfile("test-lock-stale", "main")
            assert lock.exists()
            assert lock.read_text().strip() == str(os.getpid())
        finally:
            lock_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------
class TestEdgeCases:
    def test_missing_jsonl_file(self):
        sp = SessionPaths(jsonl=Path("/nonexistent.jsonl"), session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "API_ERROR" for e in events)

    def test_empty_jsonl_file(self, tmp_path):
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        sp = SessionPaths(jsonl=f, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "API_ERROR" for e in events)

    def test_truncated_jsonl(self, tmp_path):
        f = tmp_path / "truncated.jsonl"
        shutil.copy(FIXTURES_DIR / "session-truncated.jsonl", f)
        result = core.read_last_jsonl_line(f)
        assert result is not None
        assert result["type"] == "user"

    def test_missing_pid_file(self, tmp_path):
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test", pid_file=None)
        config = MonitorConfig(verbosity=Severity.INFO)
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "DEAD" for e in events)
        assert any(e.category == "OK" for e in events)

    def test_concurrent_subagent_appear(self, tmp_path):
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")

        assert len(targets.discover_subagent_files(sp)) == 0
        (subdir / "agent-new.jsonl").write_text('{"type":"assistant"}\n')
        assert len(targets.discover_subagent_files(sp)) == 1


# ---------------------------------------------------------------------------
# Unit Tests: read_tail_jsonl_lines
# ---------------------------------------------------------------------------
class TestReadTailJsonlLines:
    def test_returns_all_lines(self):
        result = core.read_tail_jsonl_lines(FIXTURES_DIR / "session-normal.jsonl")
        assert len(result) == 3
        assert result[0]["type"] == "attachment"
        assert result[-1]["type"] == "assistant"

    def test_empty_file(self):
        result = core.read_tail_jsonl_lines(FIXTURES_DIR / "session-empty.jsonl")
        assert result == []

    def test_missing_file(self):
        result = core.read_tail_jsonl_lines(Path("/nonexistent/file.jsonl"))
        assert result == []

    def test_none_path(self):
        result = core.read_tail_jsonl_lines(None)
        assert result == []

    def test_skips_corrupt_lines(self):
        result = core.read_tail_jsonl_lines(FIXTURES_DIR / "session-truncated.jsonl")
        assert all(isinstance(r, dict) for r in result)


# ---------------------------------------------------------------------------
# Integration Tests: buried error detection (the key fix)
# ---------------------------------------------------------------------------
class TestBuriedErrorDetection:
    def test_error_buried_under_normal_lines(self, tmp_path):
        """Error followed by ai-title/queue-operation/attachment must still be detected."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-error-then-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "API_ERROR" and "retryable" in e.message for e in events)

    def test_uuid_dedup_across_polls(self, tmp_path):
        """Same error UUID should not be reported twice across poll cycles."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-error-then-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        events1 = targets.check_main_agent(sp, config)
        assert any(e.category == "API_ERROR" for e in events1)
        events2 = targets.check_main_agent(sp, config)
        assert not any(e.category == "API_ERROR" for e in events2)

    def test_new_error_after_dedup(self, tmp_path):
        """A new error with different UUID should be reported even after dedup."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-error-then-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig()
        targets.check_main_agent(sp, config)
        with open(jsonl, "a") as f:
            f.write('{"type":"assistant","uuid":"r2","timestamp":"2026-05-19T03:01:00.000Z",'
                    '"toolUseResult":{"content":[{"type":"text","text":"API Error: ECONNRESET"}]}}\n')
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "API_ERROR" for e in events)

    def test_separate_configs_no_cross_contamination(self, tmp_path):
        """Different MonitorConfig instances have independent seen_errors sets."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-error-then-normal.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config1 = MonitorConfig()
        config2 = MonitorConfig()
        targets.check_main_agent(sp, config1)
        events = targets.check_main_agent(sp, config2)
        assert any(e.category == "API_ERROR" for e in events)

    def test_subagent_buried_error(self, tmp_path):
        """Subagent error buried under normal lines should also be detected."""
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "session-error-then-normal.jsonl",
                    subdir / "agent-broken.jsonl")
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")
        config = MonitorConfig()
        events = targets.check_subagents(sp, config)
        assert any(e.category == "API_ERROR" for e in events)


# ---------------------------------------------------------------------------
# Unit Tests: check_session_alive
# ---------------------------------------------------------------------------
class TestCheckSessionAlive:
    def test_no_session_file_returns_none(self, tmp_path):
        with patch.object(Path, "home", return_value=tmp_path):
            result = core.check_session_alive("nonexistent-session-id")
        assert result is None

    def test_no_sessions_dir_returns_none(self, tmp_path):
        with patch.object(Path, "home", return_value=tmp_path):
            result = core.check_session_alive("any-id")
        assert result is None

    def test_alive_session(self, tmp_path):
        sessions = tmp_path / ".claude" / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "1234.json").write_text(json.dumps({
            "pid": os.getpid(), "sessionId": "alive-session"
        }))
        with patch.object(Path, "home", return_value=tmp_path):
            result = core.check_session_alive("alive-session")
        assert result is True

    def test_dead_session(self, tmp_path):
        sessions = tmp_path / ".claude" / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "1234.json").write_text(json.dumps({
            "pid": 999999, "sessionId": "dead-session"
        }))
        with patch.object(Path, "home", return_value=tmp_path):
            result = core.check_session_alive("dead-session")
        assert result is False

    def test_no_pid_returns_none(self, tmp_path):
        sessions = tmp_path / ".claude" / "sessions"
        sessions.mkdir(parents=True)
        (sessions / "1234.json").write_text(json.dumps({
            "sessionId": "no-pid-session"
        }))
        with patch.object(Path, "home", return_value=tmp_path):
            result = core.check_session_alive("no-pid-session")
        assert result is None


# ---------------------------------------------------------------------------
# Unit Tests: is_subagent_completed
# ---------------------------------------------------------------------------
class TestIsSubagentCompleted:
    def _write_jsonl(self, path, lines):
        with open(path, "w") as f:
            for l in lines:
                f.write(json.dumps(l) + "\n")

    def test_fresh_file_not_completed(self, tmp_path):
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn"}}
        ])
        assert core.is_subagent_completed(f, 300) is False

    def test_stale_clean_exit_end_turn(self, tmp_path):
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is True

    def test_stale_clean_exit_stop_sequence(self, tmp_path):
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "result"}], "stop_reason": "stop_sequence"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is True

    def test_stale_pending_tool_use_not_completed(self, tmp_path):
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "let me check"},
                {"type": "tool_use", "id": "t1", "name": "Read", "input": {}}
            ], "stop_reason": "tool_use"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is False

    def test_stale_error_last_line_completed(self, tmp_path):
        """Signal 2: API error as last line + stale → completed (crashed)."""
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"type": "user", "message": {"content": [{"type": "text", "text": "do task"}]}},
            {"uuid": "e1", "type": "assistant", "message": {"content": [{"type": "text", "text": "API Error: JSON Parse error: Unexpected EOF"}], "stop_reason": "end_turn"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is True

    def test_error_in_middle_clean_end_completed(self, tmp_path):
        """Error in middle but clean end_turn at end → completed via Signal 1."""
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"uuid": "e1", "type": "assistant", "message": {"content": [{"type": "text", "text": "API Error: Unexpected EOF"}], "stop_reason": "end_turn"}},
            {"type": "user", "message": {"content": [{"type": "text", "text": "retry"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "OK done"}], "stop_reason": "end_turn"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is True

    def test_error_in_middle_pending_tool_not_completed(self, tmp_path):
        """Error recovered but agent still working (pending tool_use) → NOT completed."""
        f = tmp_path / "agent.jsonl"
        self._write_jsonl(f, [
            {"uuid": "e1", "type": "assistant", "message": {"content": [{"type": "text", "text": "API Error: Unexpected EOF"}], "stop_reason": "end_turn"}},
            {"type": "user", "message": {"content": [{"type": "text", "text": "retry"}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "retrying..."},
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}
            ], "stop_reason": "tool_use"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is False

    def test_nonexistent_file(self):
        assert core.is_subagent_completed(Path("/nonexistent.jsonl"), 300) is False

    def test_none_path(self):
        assert core.is_subagent_completed(None, 300) is False

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        os.utime(f, (time.time() - 600, time.time() - 600))
        assert core.is_subagent_completed(f, 300) is False


# ---------------------------------------------------------------------------
# Integration: check_subagents with parent session liveness
# ---------------------------------------------------------------------------
class TestSubagentParentLiveness:
    def _write_jsonl(self, path, lines):
        with open(path, "w") as f:
            for l in lines:
                f.write(json.dumps(l) + "\n")

    def test_dead_parent_skips_all_subagents(self, tmp_path):
        """Layer 1: parent dead → skip all subagents, no events."""
        subdir = tmp_path / "dead-session" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-abc.jsonl"
        f.write_text('{"type":"assistant"}\n')
        os.utime(f, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=tmp_path / "dead-session.jsonl", session_id="dead-session")
        (tmp_path / "dead-session.jsonl").write_text("{}\n")

        sessions_dir = tmp_path / ".claude" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "999.json").write_text(json.dumps({
            "pid": 999999, "sessionId": "dead-session"
        }))
        config = MonitorConfig()
        with patch.object(Path, "home", return_value=tmp_path):
            events = targets.check_subagents(sp, config)
        assert len(events) == 0

    def test_alive_parent_completed_subagent_skipped(self, tmp_path):
        """Layer 2: parent alive, subagent completed (end_turn) → skip."""
        subdir = tmp_path / "live-session" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-done.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=tmp_path / "live-session.jsonl", session_id="live-session")
        (tmp_path / "live-session.jsonl").write_text("{}\n")

        sessions_dir = tmp_path / ".claude" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "pid.json").write_text(json.dumps({
            "pid": os.getpid(), "sessionId": "live-session"
        }))
        config = MonitorConfig()
        with patch.object(Path, "home", return_value=tmp_path):
            events = targets.check_subagents(sp, config)
        assert len(events) == 0

    def test_alive_parent_active_subagent_monitored(self, tmp_path):
        """Layer 2: parent alive, subagent stalled (pending tool_use) → still monitored."""
        subdir = tmp_path / "live-session" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-stuck.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "working..."},
                {"type": "tool_use", "id": "t1", "name": "Read", "input": {}}
            ], "stop_reason": "tool_use"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=tmp_path / "live-session.jsonl", session_id="live-session")
        (tmp_path / "live-session.jsonl").write_text("{}\n")

        sessions_dir = tmp_path / ".claude" / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "pid.json").write_text(json.dumps({
            "pid": os.getpid(), "sessionId": "live-session"
        }))
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        with patch.object(Path, "home", return_value=tmp_path):
            events = targets.check_subagents(sp, config)
        assert any(e.category == "STALL" for e in events)

    def test_no_session_file_falls_through(self, tmp_path):
        """Layer 1: no session file (None) → falls through to Layer 2 per-agent check."""
        subdir = tmp_path / "orphan-session" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-old.jsonl"
        self._write_jsonl(f, [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn"}}
        ])
        os.utime(f, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=tmp_path / "orphan-session.jsonl", session_id="orphan-session")
        (tmp_path / "orphan-session.jsonl").write_text("{}\n")
        config = MonitorConfig()
        with patch.object(Path, "home", return_value=tmp_path):
            events = targets.check_subagents(sp, config)
        assert len(events) == 0


# ---------------------------------------------------------------------------
# Integration: DEAD main agent still reports API errors
# ---------------------------------------------------------------------------
class TestDeadMainAgentErrors:
    def test_dead_plus_api_error_both_reported(self, tmp_path):
        """DEAD + API errors in tail → both events emitted."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-api-error.jsonl", jsonl)
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": 999999, "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)
        assert any(e.category == "API_ERROR" for e in events)

    def test_dead_no_stall(self, tmp_path):
        """DEAD process → no STALL event (redundant)."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": 999999, "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)
        assert not any(e.category == "STALL" for e in events)

    def test_alive_process_still_shows_stall(self, tmp_path):
        """Alive process + stale JSONL → STALL event (not suppressed)."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": os.getpid(), "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "DEAD" for e in events)
        assert any(e.category == "STALL" for e in events)


# ---------------------------------------------------------------------------
# Progressive tail reader
# ---------------------------------------------------------------------------
class TestProgressiveTailReader:
    def test_large_last_line(self, tmp_path):
        """Lines > 8KB should still be read via progressive sizing."""
        f = tmp_path / "large.jsonl"
        large_text = "x" * 20000
        lines = [
            json.dumps({"type": "user", "uuid": "u1", "message": {"content": [{"type": "text", "text": "hi"}]}}),
            json.dumps({"type": "assistant", "uuid": "a1", "message": {"content": [{"type": "text", "text": large_text}], "stop_reason": "end_turn"}}),
        ]
        f.write_text("\n".join(lines) + "\n")
        result = core.read_last_jsonl_line(f)
        assert result is not None
        assert result["uuid"] == "a1"

    def test_progressive_tail_lines(self, tmp_path):
        """read_tail_jsonl_lines should also handle large lines."""
        f = tmp_path / "large.jsonl"
        large_text = "y" * 15000
        lines = [
            json.dumps({"type": "assistant", "uuid": "a1", "message": {"content": [{"type": "text", "text": large_text}], "stop_reason": "end_turn"}}),
        ]
        f.write_text("\n".join(lines) + "\n")
        result = core.read_tail_jsonl_lines(f)
        assert len(result) == 1
        assert result[0]["uuid"] == "a1"


# ---------------------------------------------------------------------------
# Unit Tests: is_waiting_for_user
# ---------------------------------------------------------------------------
class TestIsWaitingForUser:
    def test_askuser_pending(self):
        """AskUserQuestion tool_use pending → True."""
        result = core.is_waiting_for_user(FIXTURES_DIR / "session-waiting-askuser.jsonl")
        assert result is True

    def test_endturn_clean(self):
        """end_turn without tool_use → True."""
        result = core.is_waiting_for_user(FIXTURES_DIR / "session-waiting-endturn.jsonl")
        assert result is True

    def test_bash_tooluse_not_waiting(self):
        """Non-interactive tool_use (Bash) → False."""
        result = core.is_waiting_for_user(FIXTURES_DIR / "session-waiting-bash-tooluse.jsonl")
        assert result is False

    def test_empty_file(self):
        result = core.is_waiting_for_user(FIXTURES_DIR / "session-empty.jsonl")
        assert result is False

    def test_missing_file(self):
        result = core.is_waiting_for_user(Path("/nonexistent.jsonl"))
        assert result is False

    def test_none_path(self):
        result = core.is_waiting_for_user(None)
        assert result is False

    def test_normal_session_not_waiting(self):
        """Normal assistant message without stop_reason field → False."""
        result = core.is_waiting_for_user(FIXTURES_DIR / "session-normal.jsonl")
        assert result is False


# ---------------------------------------------------------------------------
# Integration Tests: stall suppression when waiting for user
# ---------------------------------------------------------------------------
class TestStallSuppression:
    def test_stall_suppressed_when_askuser(self, tmp_path):
        """Stale file with AskUserQuestion pending → no STALL, emit WAITING heartbeat."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-askuser.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300, verbosity=Severity.INFO)
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "STALL" for e in events)
        assert any(e.category == "WAITING" for e in events)

    def test_stall_suppressed_when_endturn(self, tmp_path):
        """Stale file with clean end_turn → no STALL, emit WAITING heartbeat."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-endturn.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300, verbosity=Severity.INFO)
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "STALL" for e in events)
        assert any(e.category == "WAITING" for e in events)

    def test_stall_fires_for_bash_tooluse(self, tmp_path):
        """Stale file with non-interactive tool_use → STALL fires normally."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-bash-tooluse.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "STALL" for e in events)
        assert not any(e.category == "WAITING" for e in events)

    def test_heartbeat_respects_interval(self, tmp_path):
        """Second poll within heartbeat_interval → no WAITING event."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-endturn.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300,
                               verbosity=Severity.INFO, heartbeat_interval=3600)
        # First poll → heartbeat emitted
        events1 = targets.check_main_agent(sp, config)
        assert any(e.category == "WAITING" for e in events1)
        # Second poll immediately → no heartbeat (within interval)
        events2 = targets.check_main_agent(sp, config)
        assert not any(e.category == "WAITING" for e in events2)

    def test_waiting_state_resets(self, tmp_path):
        """After user responds (not waiting), wait_detected_ts resets."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-endturn.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300, verbosity=Severity.INFO)
        targets.check_main_agent(sp, config)
        assert config.wait_detected_ts > 0
        # Now replace with non-waiting content
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        targets.check_main_agent(sp, config)
        assert config.wait_detected_ts == 0

    def test_dead_still_detected_when_waiting(self, tmp_path):
        """DEAD detection works even if JSONL shows waiting state."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-waiting-endturn.jsonl", jsonl)
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": 999999, "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig()
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)


# ---------------------------------------------------------------------------
# Integration Tests: --check filter
# ---------------------------------------------------------------------------
class TestCheckFilter:
    def test_check_error_skips_stall(self, tmp_path):
        """--check error → no STALL events even when file is stale."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300, checks="error")
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "STALL" for e in events)

    def test_check_stall_skips_error(self, tmp_path):
        """--check stall → no API_ERROR events."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-api-error.jsonl", jsonl)
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(checks="stall")
        events = targets.check_main_agent(sp, config)
        assert not any(e.category == "API_ERROR" for e in events)

    def test_check_error_still_detects_dead(self, tmp_path):
        """--check error → DEAD detection still works."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-normal.jsonl", jsonl)
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": 999999, "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig(checks="error")
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)

    def test_check_stall_still_detects_dead(self, tmp_path):
        """--check stall → DEAD detection still works."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-normal.jsonl", jsonl)
        pid_file = tmp_path / "pid.json"
        pid_file.write_text(json.dumps({"pid": 999999, "sessionId": "test"}))
        sp = SessionPaths(jsonl=jsonl, pid_file=pid_file, session_id="test")
        config = MonitorConfig(checks="stall")
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "DEAD" for e in events)

    def test_check_all_default(self, tmp_path):
        """--check all (default) → both stall and error detected."""
        jsonl = tmp_path / "session.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", jsonl)
        os.utime(jsonl, (time.time() - 600, time.time() - 600))
        sp = SessionPaths(jsonl=jsonl, session_id="test")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300)
        assert config.checks == "all"
        events = targets.check_main_agent(sp, config)
        assert any(e.category == "STALL" for e in events)

    def test_subagent_check_filter(self, tmp_path):
        """--check error on subagents → no STALL for stale subagent."""
        subdir = tmp_path / "test-uuid" / "subagents"
        subdir.mkdir(parents=True)
        f = subdir / "agent-slow.jsonl"
        shutil.copy(FIXTURES_DIR / "session-stale.jsonl", f)
        os.utime(f, (time.time() - 150, time.time() - 150))
        sp = SessionPaths(jsonl=tmp_path / "test-uuid.jsonl", session_id="test-uuid")
        (tmp_path / "test-uuid.jsonl").write_text("{}\n")
        config = MonitorConfig(soft_threshold=120, hard_threshold=300, checks="error")
        events = targets.check_subagents(sp, config)
        assert not any(e.category == "STALL" for e in events)
