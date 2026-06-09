#!/usr/bin/env node
/**
 * track-skill-invocation.cjs (I1) - PreToolUse:Skill telemetry.
 *
 * Records every framework skill invocation (skill name + args + session) to the
 * consolidated sink (.claude/telemetry/invocations.jsonl). Always-on, non-blocking,
 * project-owned. No `require` of ck-config-utils (CAP-1 clean). Always emits
 * {continue:true} so it can never block a skill.
 *
 * Hook stdin protocol: { tool_name, tool_input: {skill, args}, session_id }.
 */
'use strict';

const { appendEvent } = require('./lib/telemetry-paths.cjs');
const { isHookEnabled } = require('./lib/hook-config-utils.cjs');

let logHookCrash = () => {};
try { ({ logHookCrash } = require('./lib/hook-logger.cjs')); } catch {}

function main(raw) {
  try {
    if (!isHookEnabled('trackSkillInvocation')) {
      process.stdout.write(JSON.stringify({ continue: true }));
      return;
    }
    const data = JSON.parse(raw || '{}');
    const input = data.tool_input || {};
    const skill = input.skill || input.name || '';
    if (skill) {
      appendEvent('invocations.jsonl', {
        ts: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
        skill,
        session: data.session_id || process.env.CK_SESSION_ID || '',
        args: typeof input.args === 'string' ? input.args.slice(0, 256) : '',
      });
    }
  } catch (e) {
    try { logHookCrash('track-skill-invocation', e, { event: 'PreToolUse' }); } catch {}
  }
  process.stdout.write(JSON.stringify({ continue: true }));
}

let buf = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (c) => {
  buf += c;
});
process.stdin.on('end', () => main(buf));
process.stdin.on('error', () => main(buf));
// If no stdin arrives (manual run), don't hang.
setTimeout(() => {
  if (!buf) main('');
}, 2000).unref?.();
