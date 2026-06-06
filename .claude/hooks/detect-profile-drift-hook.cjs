#!/usr/bin/env node
/**
 * PostToolUse:Edit hook (M4, project-owned, CAP-1 clean). After a docs/profiles/
 * .md edit, runs the deterministic M4 drift check on the edited file and surfaces
 * broken links / implausible dates as a NON-blocking reminder (additionalContext).
 * Early-returns at zero cost for any non-profile edit. Fail-open: never blocks.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { projectDir } = require('./lib/telemetry-paths.cjs');

function filePath(data) {
  const ti = data.tool_input || {};
  return ti.file_path || ti.path || process.env.CLAUDE_FILE_PATH || '';
}

function main() {
  try {
    const data = JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
    const fp = filePath(data).replace(/\\/g, '/');
    if (!fp || !/docs\/profiles\//.test(fp) || !fp.endsWith('.md')) {
      console.log(JSON.stringify({ continue: true }));
      return;
    }
    const dir = projectDir();
    let py = path.join(dir, '.claude/skills/.venv/bin/python3');
    if (!fs.existsSync(py)) py = 'python3'; // no project venv (e.g. CI): fall back to PATH python3
    const script = path.join(dir, '.claude/skills/com-skill-analytics/scripts/detect-profile-drift.py');
    let out = '';
    try {
      out = execFileSync(py, [script, '--file', fp, '--json'], { timeout: 8000, encoding: 'utf8' });
    } catch (e) {
      out = (e && e.stdout) || ''; // RED exit still carries JSON on stdout
    }
    const result = { continue: true };
    try {
      const d = JSON.parse(out);
      if (d.issue_count > 0) {
        const bl = (d.broken_links || []).length;
        const id = (d.implausible_dates || []).length;
        result.additionalContext =
          `\n\n[Profile Drift] ${path.basename(fp)}: ${bl} broken link(s), ${id} implausible date(s) — ` +
          `run detect-profile-drift.py --file "${fp}" for detail.`;
      }
    } catch (_) {
      /* unparseable → stay quiet */
    }
    console.log(JSON.stringify(result));
  } catch (_) {
    console.log(JSON.stringify({ continue: true }));
  }
}

if (require.main === module) main();
module.exports = { filePath };
