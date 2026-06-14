#!/usr/bin/env node
/**
 * gateguard-profile-protect.cjs - Block edits to sensitive profile files
 *
 * PreToolUse hook on Edit|Write. Classifies file sensitivity via
 * sensitivity-checker.cjs, blocks CRITICAL/HIGH until session-state
 * approval is written. Logs all actions to the consolidated telemetry sink
 * (telemetry-paths.cjs → .claude/telemetry/gateguard-audit.jsonl).
 *
 * Project-owned, ZERO ck dependency: enable/disable reads the project's
 * .claude/framework-config.json via hook-config-utils.cjs (not ck .ck.json).
 *
 * Approval flow:
 * 1. LLM calls Edit on sensitive file → BLOCKED (exit 2)
 * 2. LLM performs required checks from block message
 * 3. LLM asks user via AskUserQuestion (if requireUserApproval=true)
 * 4. LLM writes approval: echo '{"path":true}' > .claude/session-state/gateguard-approved.json
 * 5. LLM retries Edit → APPROVED (exit 0), entry removed
 *
 * @hook-class compliance
 */

const fs = require("fs");
const path = require("path");

const { classifyFile, LEVELS } = require("./lib/sensitivity-checker.cjs");
const { isHookEnabled } = require("./lib/hook-config-utils.cjs");
const { sinkPath } = require("./lib/telemetry-paths.cjs");
const {
  extractWriteTargets,
  hasResidualWrite,
} = require("./lib/bash-write-targets.cjs");

// Safe-require: a missing hook-logger (e.g. not yet projected to the public pack) must
// degrade to no-op logging at module load, NEVER a fail-closed `Cannot find module` throw.
let logHookCrash = () => {};
try {
  ({ logHookCrash } = require("./lib/hook-logger.cjs"));
} catch {
  /* logger absent → silent no-op; the guard must still load + run */
}

function logCrash(error, site) {
  try {
    logHookCrash("gateguard-profile-protect", error, { event: "PreToolUse", site });
  } catch {
    /* logging must never throw out of a fail-open path */
  }
}

const PROJECT_DIR =
  process.env.CLAUDE_PROJECT_DIR ||
  process.env.PMC_PROJECT_ROOT ||
  process.cwd();
const APPROVAL_PATH = path.join(
  PROJECT_DIR,
  ".claude",
  "session-state",
  "gateguard-approved.json",
);
// Consolidated observability sink: .claude/telemetry/gateguard-audit.jsonl
const AUDIT_LOG_PATH = sinkPath("gateguard-audit.jsonl");
const FRAMEWORK_CONFIG_PATH = path.join(
  PROJECT_DIR,
  ".claude",
  "framework-config.json",
);

function loadFrameworkConfig() {
  try {
    return JSON.parse(fs.readFileSync(FRAMEWORK_CONFIG_PATH, "utf-8"));
  } catch (e) {
    logCrash(e, "loadFrameworkConfig"); // trace a corrupt config (was the dominant silent failure)
    return {};
  }
}

function getRequireUserApproval() {
  const config = loadFrameworkConfig();
  const val = config?.gateguard?.requireUserApproval;
  return val !== false; // default true
}

function readApprovals() {
  try {
    return JSON.parse(fs.readFileSync(APPROVAL_PATH, "utf-8"));
  } catch (e) {
    // ENOENT (no approvals yet) is normal — only trace genuine read/parse corruption.
    if (e && e.code !== "ENOENT") logCrash(e, "readApprovals");
    return {};
  }
}

function writeApprovals(approvals) {
  const dir = path.dirname(APPROVAL_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (Object.keys(approvals).length === 0) {
    try {
      fs.unlinkSync(APPROVAL_PATH);
    } catch {}
  } else {
    fs.writeFileSync(APPROVAL_PATH, JSON.stringify(approvals, null, 2));
  }
}

function auditLog(entry) {
  const dir = path.dirname(AUDIT_LOG_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const line = JSON.stringify({ ts: new Date().toISOString(), ...entry });
  fs.appendFileSync(AUDIT_LOG_PATH, line + "\n");
}

function normalizePath(filePath) {
  let rel = filePath.replace(/\\/g, "/");
  const prefix = PROJECT_DIR.replace(/\\/g, "/").replace(/\/$/, "") + "/";
  if (rel.startsWith(prefix)) rel = rel.slice(prefix.length);
  return rel.replace(/^\.\//, "");
}

function formatBlockMessage(rel, classification, requireApproval) {
  const checksText = classification.checks
    .map((c, i) => `  ${i + 1}. ${c}`)
    .join("\n");

  const approvalStep = requireApproval
    ? `  1. AskUserQuestion to confirm with user
  2. Write approval: echo '{"${rel}":true}' > .claude/session-state/gateguard-approved.json
  3. Retry the Edit`
    : `  1. Write approval: echo '{"${rel}":true}' > .claude/session-state/gateguard-approved.json
  2. Retry the Edit`;

  return `
\x1b[33mGATEGUARD BLOCK\x1b[0m: Sensitive file requires pre-checks

  \x1b[33mFile:\x1b[0m ${rel}
  \x1b[33mLevel:\x1b[0m ${classification.level} (${classification.zone})

  Required checks before editing:
${checksText}

  After completing checks, approve via:
${approvalStep}
`;
}

function formatWarning(rel, classification) {
  return `\x1b[33mGATEGUARD WARN\x1b[0m: ${classification.level} file (${classification.zone}) — ${rel}`;
}

/**
 * Approval check + verdict for a path already classified CRITICAL/HIGH. Shared by the
 * path-based (Edit/Write/MultiEdit) and the Bash-redirect branches so both honor the
 * same single approval/audit flow.
 */
function resolveSensitive(rel, classification, toolName) {
  const approvals = readApprovals();
  if (approvals[rel]) {
    delete approvals[rel];
    writeApprovals(approvals);
    auditLog({
      file: rel,
      level: classification.level,
      zone: classification.zone,
      action: "approved",
      tool: toolName,
    });
    return { stderr: `\x1b[32m✓\x1b[0m GateGuard: approved edit to ${rel}` };
  }
  const requireApproval = getRequireUserApproval();
  auditLog({
    file: rel,
    level: classification.level,
    zone: classification.zone,
    action: "blocked",
    tool: toolName,
  });
  return {
    block: true,
    stderr: formatBlockMessage(rel, classification, requireApproval),
  };
}

/**
 * Bash branch — best-effort speed-bump for LITERAL write-redirects into a sensitive
 * profile path (echo>, tee, sed -i, dd of=, cp/mv). NOT a security boundary: any write
 * behind a variable / subshell / heredoc / inline interpreter is unguarded by design and
 * only logged (residual-allow), never blocked. Blocks the FIRST CRITICAL/HIGH literal
 * target found; fail-open otherwise.
 */
function runBash(toolInput) {
  const command = toolInput && toolInput.command;
  if (!command) return {};

  for (const target of extractWriteTargets(command)) {
    const rel = normalizePath(target);
    const classification = classifyFile(rel);
    if (
      classification.level === LEVELS.CRITICAL ||
      classification.level === LEVELS.HIGH
    ) {
      return resolveSensitive(rel, classification, "Bash");
    }
  }

  // No literal sensitive target. If an unresolved write construct slipped past the literal
  // scan, leave a residual trace (the speed-bump is bypassed by design — never silent).
  if (hasResidualWrite(command)) {
    auditLog({
      file: null,
      action: "residual-allow",
      tool: "Bash",
      note: "non-literal write construct (var/subshell/interpreter) — not a security boundary",
    });
  }
  return {};
}

/**
 * Decide gateguard outcome for a parsed PreToolUse payload.
 * Pure of stdin/process.exit (but keeps audit-log + approval-state side effects,
 * which are the hook's single source of truth); the CLI shim below maps its
 * verdict to exit codes, and unit tests call it directly.
 * @param {Object} hookData - { tool_name, tool_input }
 * @returns {{block?: boolean, stderr?: string}}
 */
function run(hookData) {
  if (!isHookEnabled("gateguard-profile-protect")) return {};

  const { tool_name: toolName, tool_input: toolInput } = hookData || {};

  // Bash is path-blind: scan the command for literal write-redirects (best-effort).
  if (toolName === "Bash") return runBash(toolInput);

  // gateguard classifies by path — MultiEdit exposes file_path at the same key as
  // Edit/Write, so the same path-based block applies (pii-guard handles its content).
  if (toolName !== "Edit" && toolName !== "Write" && toolName !== "MultiEdit") return {};

  const filePath = toolInput && toolInput.file_path;
  if (!filePath) return {};

  const rel = normalizePath(filePath);
  const classification = classifyFile(rel);

  if (
    classification.level === LEVELS.NONE ||
    classification.level === LEVELS.LOW
  ) {
    return {};
  }

  if (classification.level === LEVELS.MEDIUM) {
    auditLog({
      file: rel,
      level: classification.level,
      zone: classification.zone,
      action: "warned",
      tool: toolName,
    });
    return { stderr: formatWarning(rel, classification) };
  }

  // CRITICAL or HIGH — shared approval/block flow.
  return resolveSensitive(rel, classification, toolName);
}

/**
 * Standalone PreToolUse CLI entry (native settings.json registration).
 * Reads the hook payload from stdin once, delegates to run(), then maps the
 * verdict to Claude Code's hook protocol: block → exit 2 (+stderr), non-blocking
 * stderr → print + exit 0. Fail-open everywhere — a parse/runtime error must
 * never block the tool.
 */
function main() {
  let input = "";
  try {
    input = fs.readFileSync(0, "utf-8");
  } catch {
    process.exit(0);
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch {
    process.exit(0); // fail-open on unparseable input (not a guard crash — empty/garbled stdin)
  }

  let out;
  try {
    out = run(data) || {};
  } catch (e) {
    logCrash(e, "main"); // a runtime error here = guard silently off → leave a trace, still exit 0
    process.exit(0); // fail-open: a runtime error never blocks the tool
  }

  if (out.stderr) console.error(out.stderr);
  process.exit(out.block ? 2 : 0);
}

if (require.main === module) {
  main();
}

module.exports = { run, normalizePath, formatBlockMessage, formatWarning };
