#!/usr/bin/env node
/**
 * PostToolUse hook: automatic cross-framework observation (B3, project-owned, no ck dependency).
 *
 * Fires after Edit/Write. Maps the edited path to its framework (docs/profiles → psy,
 * docs/materials → mat, assets → cre, docs/profiles/.../growth → gro, .claude → orc) and
 * appends a deterministic `{fw}-touched` signal to the project observation stream
 * (.claude/session-state/observations.jsonl). This is the AUTOMATIC baseline trail; the
 * orc:observe skill records the LLM-judged semantic signals on top.
 *
 * Standalone: reads hook data from stdin, NO require of ck-config-utils (CAP-1). Reads its
 * enable flag from project framework-config.json. Fail-open + fast (<50ms, no subprocess) —
 * always emits { continue: true } so an error never blocks the edit.
 */

const fs = require("fs");
const path = require("path");

const PROJECT_DIR =
  process.env.CLAUDE_PROJECT_DIR || process.env.PMC_PROJECT_ROOT || process.cwd();
const OBSERVATIONS = path.join(PROJECT_DIR, ".claude", "session-state", "observations.jsonl");
const CONFIG = path.join(PROJECT_DIR, ".claude", "framework-config.json");

// Ordered: first match wins (growth is more specific than the profile root).
const FRAMEWORK_ROUTES = [
  [/docs\/profiles\/[^/]+\/growth\//, "gro", "growth-touched"],
  [/docs\/profiles\//, "psy", "profile-touched"],
  [/docs\/materials\//, "mat", "material-touched"],
  [/(^|\/)assets\//, "cre", "content-touched"],
  [/docs\/graph\//, "psy", "profile-touched"],
];

function isEnabled() {
  try {
    const cfg = JSON.parse(fs.readFileSync(CONFIG, "utf8"));
    // default on; only an explicit false disables.
    return cfg?.hooks?.observeFrameworkSignal?.enabled !== false;
  } catch {
    return true; // fail-open: missing/broken config never disables
  }
}

function resolveFilePath(hookData) {
  const ti = hookData.tool_input || {};
  return ti.file_path || ti.path || process.env.CLAUDE_FILE_PATH || "";
}

function classify(filePath) {
  const norm = filePath.replace(/\\/g, "/");
  for (const [re, fw, signal] of FRAMEWORK_ROUTES) {
    if (re.test(norm)) return { fw, signal };
  }
  return null;
}

function main() {
  try {
    if (!isEnabled()) {
      console.log(JSON.stringify({ continue: true }));
      return;
    }
    const hookData = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
    const filePath = resolveFilePath(hookData);
    const hit = filePath ? classify(filePath) : null;
    if (hit) {
      const rec = {
        ts: new Date().toISOString(),
        framework: hit.fw,
        signal: hit.signal,
        source: "observe-framework-signal.cjs",
        payload: { file: filePath, tool: hookData.tool_name || "" },
      };
      try {
        fs.mkdirSync(path.dirname(OBSERVATIONS), { recursive: true });
        fs.appendFileSync(OBSERVATIONS, JSON.stringify(rec) + "\n");
      } catch {
        // append failed (e.g. read-only fs) — fail-open, never block
      }
    }
    console.log(JSON.stringify({ continue: true }));
  } catch {
    console.log(JSON.stringify({ continue: true }));
  }
}

if (require.main === module) main();
module.exports = { classify, isEnabled };
