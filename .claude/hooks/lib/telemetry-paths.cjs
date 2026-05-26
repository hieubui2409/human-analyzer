/**
 * telemetry-paths.cjs - Single source of truth for the consolidated telemetry
 * sink directory, for project-owned .cjs hooks (mirrors platform_lib/telemetry.py).
 *
 * Project-owned. No `require` of ck-config-utils (CAP-1 clean). Hooks call
 * `appendEvent(name, record)` so every JSONL sink lands in one directory
 * (.claude/telemetry/) — the dashboard + forensics parser read one place.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const MAX_SINK_BYTES = 8 * 1024 * 1024; // 8 MB, one .bak generation

function projectDir() {
  return (
    process.env.CLAUDE_PROJECT_DIR ||
    process.env.PMC_PROJECT_ROOT ||
    process.cwd()
  );
}

function telemetryDir() {
  const dir = path.join(projectDir(), '.claude', 'telemetry');
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function sinkPath(name) {
  return path.join(telemetryDir(), name);
}

function disabled() {
  return Boolean(process.env.CK_TELEMETRY_DISABLED);
}

function appendEvent(name, record) {
  if (disabled()) return;
  try {
    const p = sinkPath(name);
    try {
      const st = fs.statSync(p);
      if (st.size > MAX_SINK_BYTES) fs.renameSync(p, `${p}.bak`);
    } catch (_) {
      /* file may not exist yet */
    }
    fs.appendFileSync(p, `${JSON.stringify(record)}\n`);
  } catch (_) {
    /* telemetry must never break a hook */
  }
}

module.exports = { projectDir, telemetryDir, sinkPath, appendEvent };
