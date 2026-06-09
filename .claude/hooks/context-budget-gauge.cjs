#!/usr/bin/env node
/**
 * UserPromptSubmit hook: context-budget gauge (project-owned, CAP-1 clean — no
 * ck-config-utils require). Estimates current context usage from the session
 * transcript's latest `message.usage`, projects current + estimated-next-work,
 * emits a reading to context-gauge.jsonl, and surfaces a two-tier reminder:
 * WARN at projected ≥70%, FORCE-isolate at ≥85%. Fail-open, fast (tail read only).
 *
 * Window defaults to 200000 (override CK_CONTEXT_WINDOW, e.g. 1000000 for 1M).
 * Next-work estimate defaults to 25000 (override CK_CONTEXT_NEXT_EST). Enable flag
 * read from project framework-config.json (default on).
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { appendEvent, projectDir } = require('./lib/telemetry-paths.cjs');
const { isHookEnabled } = require('./lib/hook-config-utils.cjs');

let logHookCrash = () => {};
try { ({ logHookCrash } = require('./lib/hook-logger.cjs')); } catch {}

const WINDOW = parseInt(process.env.CK_CONTEXT_WINDOW || '200000', 10);
const NEXT_EST = parseInt(process.env.CK_CONTEXT_NEXT_EST || '25000', 10);
const WARN = 0.70;
const FORCE = 0.85;
const TAIL_BYTES = 128 * 1024;

// Single shared toggle resolver (camelCase key, fail-open default-true).
function isEnabled() {
  return isHookEnabled('contextBudgetGauge');
}

function resolveTranscript(data) {
  if (data.transcript_path && fs.existsSync(data.transcript_path)) return data.transcript_path;
  const dir = path.join(os.homedir(), '.claude', 'projects', projectDir().replace(/\//g, '-'));
  const sid = data.session_id || process.env.CK_SESSION_ID;
  if (sid) {
    const p = path.join(dir, `${sid}.jsonl`);
    if (fs.existsSync(p)) return p;
  }
  try {
    const files = fs.readdirSync(dir)
      .filter((f) => f.endsWith('.jsonl'))
      .map((f) => ({ f, m: fs.statSync(path.join(dir, f)).mtimeMs }))
      .sort((a, b) => b.m - a.m);
    return files.length ? path.join(dir, files[0].f) : null;
  } catch (_) {
    return null;
  }
}

function currentContextTokens(p) {
  let text;
  try {
    const fd = fs.openSync(p, 'r');
    try {
      const size = fs.fstatSync(fd).size;
      const start = Math.max(0, size - TAIL_BYTES);
      const buf = Buffer.alloc(size - start);
      fs.readSync(fd, buf, 0, buf.length, start);
      text = buf.toString('utf8');
    } finally {
      fs.closeSync(fd);
    }
  } catch (_) {
    return 0;
  }
  let last = 0;
  for (const line of text.split('\n')) {
    if (!line.trim()) continue;
    let rec;
    try { rec = JSON.parse(line); } catch (_) { continue; }
    const u = rec.message && rec.message.usage;
    if (u) last = (u.input_tokens || 0) + (u.cache_read_input_tokens || 0) + (u.cache_creation_input_tokens || 0);
  }
  return last;
}

function gauge(current) {
  const pct = current / WINDOW;
  const projected = (current + NEXT_EST) / WINDOW;
  let tier = null;
  if (projected >= FORCE) tier = 'force';
  else if (projected >= WARN) tier = 'warn';
  return { pct: +pct.toFixed(3), projected: +projected.toFixed(3), tier };
}

function main() {
  try {
    if (!isEnabled()) { console.log(JSON.stringify({ continue: true })); return; }
    const data = JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
    const p = resolveTranscript(data);
    const current = p ? currentContextTokens(p) : 0;
    const g = gauge(current);
    appendEvent('context-gauge.jsonl', {
      ts: new Date().toISOString(), current, window: WINDOW, pct: g.pct, projected: g.projected,
    });
    const result = { continue: true };
    if (g.tier === 'force') {
      result.additionalContext =
        `\n\n[Context Budget] ~${Math.round(g.pct * 100)}% used (projected ${Math.round(g.projected * 100)}% ≥ 85%). ` +
        `Strongly consider isolating remaining work into subagents or compacting before continuing.`;
    } else if (g.tier === 'warn') {
      result.additionalContext =
        `\n\n[Context Budget] ~${Math.round(g.pct * 100)}% used (projected ${Math.round(g.projected * 100)}% ≥ 70%). ` +
        `Consider delegating heavy work to subagents soon.`;
    }
    console.log(JSON.stringify(result));
  } catch (e) {
    try { logHookCrash('context-budget-gauge', e, { event: 'UserPromptSubmit' }); } catch {}
    console.log(JSON.stringify({ continue: true }));
  }
}

if (require.main === module) main();
module.exports = { gauge, currentContextTokens };
