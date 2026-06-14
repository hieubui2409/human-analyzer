#!/usr/bin/env node
/**
 * pii-guard-on-write.cjs — born-time PII write-guard (PreToolUse Edit|Write|MultiEdit).
 *
 * Blocks a real-name token the moment it would be written into a SHIPPED-CLASS file (one the public
 * toolkit pack distributes), instead of only catching it at ship time. The ship-time scan_pack_pii
 * gate stays as the fail-closed backstop; this stops the leak at birth. Defense-in-depth.
 *
 * Thin shim: the judgment (is the path shipped-class? does the written text carry a forbidden token?)
 * lives in pii_guard_check.py, which reuses the same collision-free scanner token set as scan_pack_pii
 * and the same manifest/safety_filter classification. Here we only extract the written text, hand it to
 * the helper, and map its verdict to the hook protocol (block → exit 2, otherwise exit 0).
 *
 * Roster absent (consumer pack) ⇒ helper returns block:false ⇒ no-op. Fail-OPEN everywhere: any parse
 * or runtime error must never block a tool. Project-owned, ZERO ck dependency (enable/disable reads the
 * project's own .claude/framework-config.json).
 *
 * Test seam: PII_GUARD_PROFILES_DIR redirects the helper's roster dir so an integration test can drive
 * the guard with a synthetic roster (keeping the test name-free) instead of the real characters.yaml.
 *
 * @hook-class compliance
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { isHookEnabled, projectDir } = require('./lib/hook-config-utils.cjs');

// Safe-require: a missing hook-logger must degrade to no-op, never a load-time fail-closed throw.
let logHookCrash = () => {};
try {
  ({ logHookCrash } = require('./lib/hook-logger.cjs'));
} catch {
  /* logger absent → no-op */
}

function logCrash(error, site) {
  try {
    logHookCrash('pii-guard-on-write', error, { event: 'PreToolUse', site });
  } catch {
    /* logging must never throw out of a fail-open path */
  }
}

/** All text this tool call would write: Write.content, Edit.new_string, MultiEdit.edits[].new_string. */
function writtenText(toolInput) {
  if (!toolInput) return '';
  const parts = [];
  if (typeof toolInput.content === 'string') parts.push(toolInput.content);
  if (typeof toolInput.new_string === 'string') parts.push(toolInput.new_string);
  if (Array.isArray(toolInput.edits)) {
    for (const e of toolInput.edits) {
      if (e && typeof e.new_string === 'string') parts.push(e.new_string);
    }
  }
  return parts.join('\n');
}

function filePath(toolInput) {
  const ti = toolInput || {};
  return ti.file_path || ti.path || '';
}

function blockMessage(verdict) {
  const toks = (verdict.tokens || []).join(', ');
  return (
    `\x1b[33mPII WRITE-GUARD\x1b[0m: real-name token(s) would be written into a shipped-class file.\n\n` +
    `  \x1b[33mFile:\x1b[0m ${verdict.path}\n` +
    `  \x1b[33mToken(s):\x1b[0m ${toks}\n\n` +
    `  This file ships in the public toolkit pack. Real names belong ONLY in the pack-excluded\n` +
    `  corpus (docs/profiles, docs/materials, docs/graph, docs/references).\n` +
    `  Fix: use a placeholder/slug (e.g. character-a) here, or move this data into the corpus.\n`
  );
}

/**
 * Decide the guard outcome for a parsed PreToolUse payload by delegating to the python helper.
 * @param {Object} hookData - { tool_name, tool_input }
 * @returns {{block?: boolean, stderr?: string}}
 */
function run(hookData) {
  if (!isHookEnabled('pii-guard-on-write')) return {};

  const { tool_name: toolName, tool_input: toolInput } = hookData || {};
  if (toolName !== 'Edit' && toolName !== 'Write' && toolName !== 'MultiEdit') return {};

  const fp = filePath(toolInput);
  if (!fp) return {};
  const text = writtenText(toolInput);
  if (!text) return {};

  const dir = projectDir();
  let py = path.join(dir, '.claude/skills/.venv/bin/python3');
  if (!fs.existsSync(py)) py = 'python3'; // no project venv (e.g. CI): fall back to PATH python3
  const script = path.join(
    dir, '.claude/skills/_framework-shared/scripts/pii_guard_check.py');
  if (!fs.existsSync(script)) return {}; // helper not in this clone → nothing to enforce

  const argv = [script, '--path', fp];
  const profilesDir = process.env.PII_GUARD_PROFILES_DIR;
  if (profilesDir) argv.push('--profiles-dir', profilesDir);

  let out = '';
  try {
    out = execFileSync(py, argv, { input: text, timeout: 8000, encoding: 'utf8' });
  } catch (e) {
    logCrash(e, 'execFileSync'); // flaky python helper was the dominant silent failure → trace it
    return {}; // helper failure → fail-open, never block on our own error
  }

  let verdict;
  try {
    verdict = JSON.parse(out);
  } catch (e) {
    logCrash(e, 'parseVerdict');
    return {}; // unparseable → fail-open
  }
  if (verdict && verdict.block) {
    return { block: true, stderr: blockMessage(verdict) };
  }
  return {};
}

/**
 * Standalone PreToolUse CLI entry. Reads the payload from stdin, delegates to run(), maps the verdict
 * to Claude Code's protocol: block → exit 2 (+stderr), otherwise exit 0. Fail-open on any error.
 */
function main() {
  let input = '';
  try {
    input = fs.readFileSync(0, 'utf-8');
  } catch {
    process.exit(0);
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch {
    process.exit(0); // fail-open on unparseable input
  }

  let outcome;
  try {
    outcome = run(data) || {};
  } catch (e) {
    logCrash(e, 'main'); // runtime error = guard silently off → trace, still exit 0
    process.exit(0); // fail-open: a runtime error never blocks the tool
  }

  if (outcome.stderr) console.error(outcome.stderr);
  process.exit(outcome.block ? 2 : 0);
}

if (require.main === module) {
  main();
}

module.exports = { run, writtenText, filePath, blockMessage };
