/**
 * hook-config-utils.cjs - Project-owned hook enable/disable resolver (CAP-1).
 *
 * Replaces the ck-owned ck-config-utils.cjs `isHookEnabled` for PROJECT hooks, so
 * project hooks have ZERO dependency on ck (`.ck.json` / ck-config-utils). Reads the
 * project's own `.claude/framework-config.json`:
 *
 *   { "hooks": { "<hook-name>": false } }            // boolean form
 *   { "hooks": { "<hook-name>": { "enabled": false } } }  // object form (matches observe)
 *
 * Default ENABLED (true) when the file or key is absent. Fail-open: any read/parse
 * error returns true so a config glitch never silently disables a safety hook.
 */
'use strict';

const fs = require('fs');
const path = require('path');

function projectDir() {
  return process.env.CLAUDE_PROJECT_DIR || process.env.PMC_PROJECT_ROOT || process.cwd();
}

function isHookEnabled(hookName) {
  try {
    const cfgPath = path.join(projectDir(), '.claude', 'framework-config.json');
    const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
    const entry = (cfg.hooks || {})[hookName];
    if (entry === false) return false;
    if (entry && typeof entry === 'object') return entry.enabled !== false;
    return true; // undefined / true / non-object → enabled
  } catch (_) {
    return true; // fail-open: never disable a hook on a config error
  }
}

module.exports = { isHookEnabled, projectDir };
