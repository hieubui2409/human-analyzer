---
name: com:health-check
description: "Monitor Claude Code session health — detect stalls, API errors, process death for main/subagent/team sessions. Use when spawning long-running subagents or teams, or when user says 'monitor health', 'health check', 'watch session'."
argument-hint: "[--target main|subagent|team|all] [--verbosity error|warn|info|debug]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "monitoring"
  position: "utility"
  dependencies: []
---

# com:health-check — Session Health Monitor

Poll-based daemon watching session JSONL mtime + content + process liveness. Each stdout line = Monitor tool notification.

## Usage Modes

### User-Invoked (main agent)

User says "monitor health", "health check", "watch session" → invoke Monitor tool:

```
Monitor({
  description: "session health monitor",
  persistent: true,
  timeout_ms: 300000,
  command: "$HOME/.claude/skills/.venv/bin/python3 $HOME/Documents/ck-marketing/.claude/skills/com-health-check/scripts/monitor-session-health.py --target main --verbosity warn --poll 30"
})
```

### LLM-Invoked (subagent/team)

ONLY when user has confirmed monitoring OR a Monitor is already running for main:

```
Monitor({
  description: "subagent health monitor",
  persistent: true,
  timeout_ms: 300000,
  command: "$HOME/.claude/skills/.venv/bin/python3 $HOME/Documents/ck-marketing/.claude/skills/com-health-check/scripts/monitor-session-health.py --target all --verbosity warn --poll 30 --team-name {TEAM_NAME}"
})
```

## Args Reference

| Flag            | Default | Purpose                                |
| --------------- | ------- | -------------------------------------- |
| `--target`      | main    | main / subagent / team / all           |
| `--soft`        | 120     | Soft stall threshold (seconds) → WARN  |
| `--hard`        | 300     | Hard stall threshold (seconds) → ERROR |
| `--verbosity`   | warn    | error / warn / info / debug            |
| `--include-429` | off     | Report 429 rate limits                 |
| `--poll`        | 30      | Poll interval (seconds)                |
| `--session-id`  | auto    | Explicit session UUID                  |
| `--team-name`   | —       | Team name for team monitoring          |

## Response Protocol

When a notification arrives, act based on severity:

| Notification                      | Action                                         |
| --------------------------------- | ---------------------------------------------- |
| `[ERROR] API_ERROR ... retryable` | Re-spawn subagent per CLAUDE.md retry protocol |
| `[ERROR] STALL ... hard`          | Alert user — session may be dead               |
| `[ERROR] DEAD ...`                | Report to user, no auto-retry                  |
| `[WARN] RATE_LIMIT 429`           | Wait 60s then retry                            |
| `[WARN] STALL ... soft`           | Log, don't act — may be thinking               |
| `[INFO] OK ...`                   | Ignore (heartbeat)                             |
