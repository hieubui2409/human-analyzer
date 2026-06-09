#!/usr/bin/env node
/**
 * PreCompact hook: write the framework-delta compact-digest before /compact (C5, project-owned).
 *
 * Runs the project digest script (orc-session-state/scripts/write-framework-delta-compact-digest.py)
 * which snapshots a bounded per-framework delta to .claude/session-state/compact-digest.json.
 * orc:bootstrap re-injects that digest after compaction so framework context survives the boundary.
 *
 * Standalone: NO require of ck-config-utils (CAP-1); does NOT touch ck write-compact-marker.cjs
 * (both PreCompact hooks run independently). Reads its enable flag from project framework-config.json.
 * Fail-open — a digest error must never block compaction.
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { isHookEnabled } = require("./lib/hook-config-utils.cjs");

let logHookCrash = () => {};
try { ({ logHookCrash } = require("./lib/hook-logger.cjs")); } catch {}

const PROJECT_DIR =
  process.env.CLAUDE_PROJECT_DIR || process.env.PMC_PROJECT_ROOT || process.cwd();
const SCRIPT = path.join(
  PROJECT_DIR,
  ".claude",
  "skills",
  "orc-session-state",
  "scripts",
  "write-framework-delta-compact-digest.py",
);

function venvPython() {
  const local = path.join(PROJECT_DIR, ".claude", "skills", ".venv", "bin", "python3");
  if (fs.existsSync(local)) return local;
  return path.join(process.env.HOME || "", ".claude", "skills", ".venv", "bin", "python3");
}

// Single shared toggle resolver (camelCase key, fail-open default-true).
function isEnabled() {
  return isHookEnabled("compactDigest");
}

function main() {
  try {
    if (isEnabled() && fs.existsSync(SCRIPT)) {
      try {
        execFileSync(venvPython(), [SCRIPT], {
          cwd: PROJECT_DIR,
          timeout: 5000,
          stdio: "ignore",
        });
      } catch {
        // digest failure must never block compaction — fail-open
      }
    }
  } catch (e) {
    // a digest error must never block compaction — fail-open, but leave a trace
    try { logHookCrash("write-framework-delta-compact-digest", e, { event: "PreCompact" }); } catch {}
  }
  console.log(JSON.stringify({ continue: true }));
}

if (require.main === module) main();
module.exports = { isEnabled, venvPython };
