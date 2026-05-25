#!/usr/bin/env node
/**
 * gateguard-profile-protect.cjs - Block edits to sensitive profile files
 *
 * PreToolUse hook on Edit|Write. Classifies file sensitivity via
 * sensitivity-checker.cjs, blocks CRITICAL/HIGH until session-state
 * approval is written. Logs all actions to JSONL audit trail.
 *
 * Approval flow:
 * 1. LLM calls Edit on sensitive file → BLOCKED (exit 2)
 * 2. LLM performs required checks from block message
 * 3. LLM asks user via AskUserQuestion (if requireUserApproval=true)
 * 4. LLM writes approval: echo '{"path":true}' > .claude/session-state/gateguard-approved.json
 * 5. LLM retries Edit → APPROVED (exit 0), entry removed
 */

const fs = require("fs");
const path = require("path");

const { classifyFile, LEVELS } = require("./lib/sensitivity-checker.cjs");
const { isHookEnabled } = require("./lib/ck-config-utils.cjs");

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
const AUDIT_LOG_PATH = path.join(
  PROJECT_DIR,
  ".claude",
  "logs",
  "gateguard-audit.jsonl",
);
const FRAMEWORK_CONFIG_PATH = path.join(
  PROJECT_DIR,
  ".claude",
  "framework-config.json",
);

function loadFrameworkConfig() {
  try {
    return JSON.parse(fs.readFileSync(FRAMEWORK_CONFIG_PATH, "utf-8"));
  } catch {
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
  } catch {
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
 * Decide gateguard outcome for a parsed PreToolUse payload.
 * Pure of stdin/process.exit (but keeps audit-log + approval-state side effects,
 * which are the hook's single source of truth) so hook-dispatcher.cjs can compose it.
 * @param {Object} hookData - { tool_name, tool_input }
 * @returns {{block?: boolean, stderr?: string}}
 */
function run(hookData) {
  if (!isHookEnabled("gateguard-profile-protect")) return {};

  const { tool_name: toolName, tool_input: toolInput } = hookData || {};

  if (toolName !== "Edit" && toolName !== "Write") return {};

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

  // CRITICAL or HIGH — check approval
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

  // Not approved — block
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

// Composed exclusively by hook-dispatcher.cjs — no standalone CLI entry.
module.exports = { run, normalizePath, formatBlockMessage, formatWarning };
