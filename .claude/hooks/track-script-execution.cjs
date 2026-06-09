#!/usr/bin/env node
/**
 * PostToolUse:Bash hook (I2, project-owned, CAP-1 clean — no ck-config-utils require).
 *
 * Records skill-script invocations to hook-telemetry.jsonl (separate sink from
 * I4's script-telemetry.jsonl to avoid a write race). Filters out non-skill Bash
 * (git, ls, grep…) — only logs commands that run a `.claude/skills/.../scripts/*.py|sh`.
 * Coarse exit inference from tool_response (no reliable exit code in hook input).
 * Fail-open + fast: always emits { continue: true }, never blocks the Bash call.
 */
'use strict';

const fs = require('fs');
const { appendEvent } = require('./lib/telemetry-paths.cjs');
const { isHookEnabled } = require('./lib/hook-config-utils.cjs');

let logHookCrash = () => {};
try { ({ logHookCrash } = require('./lib/hook-logger.cjs')); } catch {}

// Capture the skill-relative script path: skills/<skill>/scripts/<file>.py|sh
const SCRIPT_RE = /\.claude\/skills\/([^\s/]+\/scripts\/[^\s]+\.(?:py|sh))/;

function inferExit(resp, stderr) {
  if (resp && typeof resp === 'object' && (resp.interrupted || resp.is_error)) return 1;
  if (/\b(Traceback|Error|Exception|exit code [1-9])\b/i.test(stderr)) return 1;
  return 0;
}

function main() {
  try {
    if (!isHookEnabled('trackScriptExecution')) {
      console.log(JSON.stringify({ continue: true }));
      return;
    }
    const data = JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
    const cmd = (data.tool_input && data.tool_input.command) || '';
    const m = cmd.match(SCRIPT_RE);
    if (m) {
      const resp = data.tool_response;
      const stderr = (resp && typeof resp === 'object' && (resp.stderr || '')) || '';
      appendEvent('hook-telemetry.jsonl', {
        ts: new Date().toISOString(),
        source: 'hook:bash',
        script: m[1],
        exit: inferExit(resp, stderr),
        command: cmd.slice(0, 200),
      });
    }
    console.log(JSON.stringify({ continue: true }));
  } catch (e) {
    try { logHookCrash('track-script-execution', e, { event: 'PostToolUse' }); } catch {}
    console.log(JSON.stringify({ continue: true }));
  }
}

if (require.main === module) main();
module.exports = { SCRIPT_RE, inferExit };
