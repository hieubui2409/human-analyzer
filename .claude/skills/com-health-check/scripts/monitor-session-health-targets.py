"""Target-specific health check functions for main agent, subagents, and team agents."""
import importlib.util
import json
import subprocess
import time
from pathlib import Path

_core_path = Path(__file__).parent / "monitor-session-health-core.py"
_spec = importlib.util.spec_from_file_location("_core", _core_path)
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)

ErrorClass = _core.ErrorClass
Severity = _core.Severity
HealthEvent = _core.HealthEvent
SessionPaths = _core.SessionPaths
MonitorConfig = _core.MonitorConfig
read_last_jsonl_line = _core.read_last_jsonl_line
read_tail_jsonl_lines = _core.read_tail_jsonl_lines
extract_error_text = _core.extract_error_text
classify_error = _core.classify_error
check_process_liveness = _core.check_process_liveness
check_file_freshness = _core.check_file_freshness
resolve_project_slug = _core.resolve_project_slug
check_session_alive = _core.check_session_alive
is_subagent_completed = _core.is_subagent_completed


def resolve_session_paths(session_id: str | None = None, cwd: str | None = None) -> SessionPaths:
    """Auto-detect or resolve session JSONL + PID file."""
    claude_dir = Path.home() / ".claude"
    slug = resolve_project_slug(cwd)
    project_dir = claude_dir / "projects" / slug

    sp = SessionPaths(project_slug=slug)

    if session_id:
        sp.session_id = session_id
        candidate = project_dir / f"{session_id}.jsonl"
        if candidate.exists():
            sp.jsonl = candidate
    elif project_dir.exists():
        jsonls = sorted(
            [f for f in project_dir.glob("*.jsonl") if f.is_file()],
            key=lambda f: f.stat().st_mtime, reverse=True,
        )
        if jsonls:
            sp.jsonl = jsonls[0]
            sp.session_id = jsonls[0].stem

    if sp.session_id:
        sessions_dir = claude_dir / "sessions"
        if sessions_dir.exists():
            for pf in sessions_dir.glob("*.json"):
                try:
                    data = json.loads(pf.read_text())
                    if data.get("sessionId") == sp.session_id:
                        sp.pid_file = pf
                        break
                except (json.JSONDecodeError, OSError):
                    continue

    return sp


def _check_content_errors(lines: list[dict], include_429: bool, target_name: str,
                          seen_errors: set | None = None) -> list[HealthEvent]:
    """Check recent JSONL lines for error patterns with UUID dedup."""
    if seen_errors is None:
        seen_errors = set()
    events = []
    for line in lines:
        uuid = line.get("uuid", "")
        if uuid and uuid in seen_errors:
            continue
        texts = extract_error_text(line)
        err_class = classify_error(texts, include_429)
        if err_class == ErrorClass.RETRYABLE:
            if uuid:
                seen_errors.add(uuid)
            events.append(HealthEvent(Severity.ERROR, "API_ERROR", target_name,
                                      f'"{texts[0][:80]}" — retryable'))
        elif err_class == ErrorClass.TIME_RETRYABLE:
            if uuid:
                seen_errors.add(uuid)
            events.append(HealthEvent(Severity.WARN, "RATE_LIMIT", target_name,
                                      "429 detected — wait ~60s"))
        elif err_class == ErrorClass.NON_RETRYABLE:
            if uuid:
                seen_errors.add(uuid)
            events.append(HealthEvent(Severity.ERROR, "API_ERROR", target_name,
                                      f'"{texts[0][:80]}" — non-retryable'))
    if len(seen_errors) > 200:
        to_remove = len(seen_errors) - 100
        for _ in range(to_remove):
            seen_errors.pop()
    return events


def check_main_agent(sp: SessionPaths, config: MonitorConfig) -> list[HealthEvent]:
    """Full health check for main agent session."""
    events = []

    is_dead = False
    if sp.pid_file and sp.pid_file.exists():
        try:
            data = json.loads(sp.pid_file.read_text())
            pid = data.get("pid")
            if pid and not check_process_liveness(pid):
                events.append(HealthEvent(Severity.ERROR, "DEAD", "main-agent",
                                          f"process {pid} not found — session terminated"))
                is_dead = True
        except (json.JSONDecodeError, OSError):
            pass

    if not is_dead:
        stall = check_file_freshness(sp.jsonl, config.soft_threshold, config.hard_threshold)
        if stall:
            stall.target = "main-agent"
            events.append(stall)

    if sp.jsonl:
        lines = read_tail_jsonl_lines(sp.jsonl)
        if lines:
            events.extend(_check_content_errors(lines, config.include_429, "main-agent",
                                                config.seen_errors))

            if not events and config.verbosity.value <= Severity.INFO.value:
                last_line = lines[-1]
                ltype = last_line.get("type", "unknown")
                try:
                    delta = int(time.time() - sp.jsonl.stat().st_mtime)
                except OSError:
                    delta = -1
                events.append(HealthEvent(Severity.INFO, "OK", "main-agent",
                                          f"active {delta}s ago, type={ltype}"))

    return events


def discover_subagent_files(sp: SessionPaths) -> list[Path]:
    """Find all subagent JSONL files for current session."""
    if not sp.jsonl:
        return []
    subdir = sp.jsonl.parent / sp.session_id / "subagents"
    if not subdir.exists():
        alt = subdir.parent / "subagents"
        return sorted(alt.glob("agent-*.jsonl")) if alt.exists() else []
    return sorted(subdir.glob("agent-*.jsonl"))


def check_subagents(sp: SessionPaths, config: MonitorConfig) -> list[HealthEvent]:
    """Health check for active subagents only.

    Layer 1: parent session dead (no session file or PID dead) → skip all.
    Layer 2: per-subagent — skip if clean exit (end_turn) or error exit (API error patterns).
    """
    parent_alive = check_session_alive(sp.session_id)
    if parent_alive is False:
        return []

    events = []
    for f in discover_subagent_files(sp):
        agent_name = f.stem
        if is_subagent_completed(f, config.hard_threshold):
            continue

        stall = check_file_freshness(f, config.soft_threshold, config.hard_threshold)
        if stall:
            stall.target = agent_name
            events.append(stall)

        lines = read_tail_jsonl_lines(f)
        if lines:
            events.extend(_check_content_errors(lines, config.include_429, agent_name,
                                                config.seen_errors))
    return events


def resolve_team_member_jsonl(slug: str, team_name: str, member_name: str) -> Path | None:
    """Scan JSONL files to find one matching team+member in attachment line."""
    project_dir = Path.home() / ".claude" / "projects" / slug
    if not project_dir.exists():
        return None

    for jsonl_path in project_dir.glob("*.jsonl"):
        try:
            with open(jsonl_path, "rb") as f:
                head = f.read(4096).decode("utf-8", errors="replace")
            for line in head.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if (data.get("type") == "attachment"
                            and data.get("teamName") == team_name
                            and data.get("agentName") == member_name):
                        return jsonl_path
                except json.JSONDecodeError:
                    continue
        except OSError:
            continue
    return None


def check_team_process(team_name: str, member_name: str) -> int | None:
    """Find team agent PID via pgrep (no PID file for team agents)."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"agent-name {member_name}.*team-name {team_name}"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split("\n")[0])
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass
    return None


def check_team_agents(sp: SessionPaths, config: MonitorConfig) -> list[HealthEvent]:
    """Health check for team agents via config + JSONL scan."""
    events = []
    if not config.team_name:
        return events

    config_path = Path.home() / ".claude" / "teams" / config.team_name / "config.json"
    if not config_path.exists():
        events.append(HealthEvent(Severity.WARN, "TEAM", "team",
                                  f"config not found: {config_path}"))
        return events

    try:
        team_config = json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        events.append(HealthEvent(Severity.WARN, "TEAM", "team", "failed to parse team config"))
        return events

    for member in team_config.get("members", []):
        name = member.get("name", "unknown")
        jsonl = resolve_team_member_jsonl(sp.project_slug, config.team_name, name)

        if not jsonl:
            events.append(HealthEvent(Severity.WARN, "TEAM", name,
                                      "no JSONL found — may not be started"))
            continue

        if is_subagent_completed(jsonl, config.hard_threshold):
            continue

        stall = check_file_freshness(jsonl, config.soft_threshold, config.hard_threshold)
        if stall:
            stall.target = f"team:{name}"
            events.append(stall)

        lines = read_tail_jsonl_lines(jsonl)
        if lines:
            events.extend(_check_content_errors(lines, config.include_429, f"team:{name}",
                                                config.seen_errors))

        pid = check_team_process(config.team_name, name)
        if pid is None and jsonl:
            events.append(HealthEvent(Severity.WARN, "TEAM", f"team:{name}",
                                      "process not found via pgrep — may have exited"))

    return events
