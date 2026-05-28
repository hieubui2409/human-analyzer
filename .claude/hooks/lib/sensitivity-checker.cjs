/**
 * sensitivity-checker.cjs - File sensitivity classification for GateGuard hook
 *
 * Reads sensitivity-config.json and classifies files by sensitivity level.
 * Pure logic module — no stdin/stdout, no exit codes (same pattern as privacy-checker.cjs).
 *
 * @module sensitivity-checker
 */

const fs = require("fs");
const path = require("path");

const CONFIG_PATH = path.join(
  __dirname,
  "../../scripts/platform_lib/sensitivity-config.json",
);

const LEVELS = {
  CRITICAL: "CRITICAL",
  HIGH: "HIGH",
  MEDIUM: "MEDIUM",
  LOW: "LOW",
  NONE: "NONE",
};

let _configCache = null;

function loadSensitivityConfig() {
  if (_configCache) return _configCache;
  try {
    _configCache = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf-8"));
  } catch (e) {
    _configCache = { zones: [], defaults: { fallback: "NONE" } };
  }
  return _configCache;
}

function normalizePath(filePath) {
  let rel = filePath.replace(/\\/g, "/");
  const projectDir =
    process.env.CLAUDE_PROJECT_DIR || process.env.PMC_PROJECT_ROOT || "";
  if (projectDir) {
    const prefix = projectDir.replace(/\\/g, "/").replace(/\/$/, "") + "/";
    if (rel.startsWith(prefix)) {
      rel = rel.slice(prefix.length);
    }
  }
  return rel.replace(/^\.\//, "");
}

function classifyFile(filePath) {
  const config = loadSensitivityConfig();
  const rel = normalizePath(filePath);

  for (const zone of config.zones) {
    if (rel.includes(zone.pattern)) {
      return {
        level: zone.level,
        zone: zone.zone,
        checks: zone.checks,
        matched: zone.pattern,
      };
    }
  }

  const defaults = config.defaults || {};
  for (const [prefix, level] of Object.entries(defaults)) {
    if (prefix === "fallback") continue;
    if (rel.includes(prefix)) {
      return { level, zone: "default", checks: [], matched: prefix };
    }
  }

  return {
    level: defaults.fallback || LEVELS.NONE,
    zone: "none",
    checks: [],
    matched: null,
  };
}

function isProtected(filePath) {
  const { level } = classifyFile(filePath);
  return level === LEVELS.CRITICAL || level === LEVELS.HIGH;
}

function isWarning(filePath) {
  const { level } = classifyFile(filePath);
  return level === LEVELS.MEDIUM;
}

module.exports = {
  loadSensitivityConfig,
  classifyFile,
  isProtected,
  isWarning,
  normalizePath,
  LEVELS,
};
