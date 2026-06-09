#!/usr/bin/env node
/**
 * Stop hook (I3, project-owned, CAP-1 clean). On session end, emits a one-line
 * summary to sessions.jsonl by reading the current transcript's head (for the
 * real start timestamp → duration) plus tail (recent activity). Tail-only keeps
 * it <5s on huge transcripts; skill/tool counts are an approximation over the
 * recent window, which is sufficient for dashboard trending (M1). Fail-open:
 * always emits { continue: true } so it never blocks session exit.
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { appendEvent, projectDir } = require('./lib/telemetry-paths.cjs');
const { isHookEnabled } = require('./lib/hook-config-utils.cjs');

let logHookCrash = () => {};
try { ({ logHookCrash } = require('./lib/hook-logger.cjs')); } catch {}

const TAIL_BYTES = 256 * 1024;
const TOKEN_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'];

function sessionsDir() {
  const slug = projectDir().replace(/\//g, '-');
  return path.join(os.homedir(), '.claude', 'projects', slug);
}

function resolveSessionFile(data) {
  const dir = sessionsDir();
  const sid = (data && data.session_id) || process.env.CK_SESSION_ID;
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

function firstTimestamp(p) {
  // Cheap head read: first complete line's timestamp = real session start.
  try {
    const fd = fs.openSync(p, 'r');
    try {
      const buf = Buffer.alloc(8192);
      const n = fs.readSync(fd, buf, 0, buf.length, 0);
      const line = buf.toString('utf8', 0, n).split('\n')[0];
      const rec = JSON.parse(line);
      return rec.timestamp || (rec.message && rec.message.timestamp) || null;
    } finally {
      fs.closeSync(fd);
    }
  } catch (_) {
    return null;
  }
}

function readTail(p) {
  const fd = fs.openSync(p, 'r');
  try {
    const size = fs.fstatSync(fd).size;
    const start = Math.max(0, size - TAIL_BYTES);
    const buf = Buffer.alloc(size - start);
    fs.readSync(fd, buf, 0, buf.length, start);
    return buf.toString('utf8');
  } finally {
    fs.closeSync(fd);
  }
}

function summarize(text, startTs) {
  const skills = [];
  const tools = {};
  const files = new Set();
  let subagents = 0;
  let inTok = 0;
  let outTok = 0;
  let cacheTok = 0;
  let lastTs = null;
  for (const line of text.split('\n')) {
    if (!line.trim()) continue;
    let rec;
    try { rec = JSON.parse(line); } catch (_) { continue; }
    const ts = rec.timestamp || (rec.message && rec.message.timestamp);
    if (ts) lastTs = ts;
    const msg = rec.message;
    if (!msg || typeof msg !== 'object') continue;
    if (msg.usage) {
      inTok += msg.usage.input_tokens || 0;
      outTok += msg.usage.output_tokens || 0;
      cacheTok += msg.usage.cache_read_input_tokens || 0;
    }
    if (Array.isArray(msg.content)) {
      for (const b of msg.content) {
        if (!b || b.type !== 'tool_use') continue;
        tools[b.name] = (tools[b.name] || 0) + 1;
        const inp = b.input || {};
        if (b.name === 'Skill' && inp.skill) skills.push(inp.skill);
        else if (TOKEN_TOOLS.includes(b.name) && inp.file_path) files.add(inp.file_path);
        else if (b.name === 'Task' || b.name === 'Agent') subagents += 1;
      }
    }
  }
  const start = startTs || lastTs;
  const dur = (start && lastTs) ? Math.round((new Date(lastTs) - new Date(start)) / 1000) : 0;
  return {
    skills: [...new Set(skills)],
    tools,
    files_modified: files.size,
    subagents,
    tokens: { input: inTok, output: outTok, cache_read: cacheTok },
    duration_s: dur >= 0 ? dur : 0,
  };
}

function main() {
  try {
    if (!isHookEnabled('emitSessionSummary')) {
      console.log(JSON.stringify({ continue: true }));
      return;
    }
    const data = JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
    const p = resolveSessionFile(data);
    if (p) {
      const s = summarize(readTail(p), firstTimestamp(p));
      appendEvent('sessions.jsonl', { ts: new Date().toISOString(), session: path.basename(p, '.jsonl'), ...s });
    }
  } catch (e) {
    try { logHookCrash('emit-session-summary', e, { event: 'Stop' }); } catch {}
  }
  console.log(JSON.stringify({ continue: true }));
}

if (require.main === module) main();
module.exports = { summarize };
