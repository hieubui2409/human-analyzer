#!/usr/bin/env node
/**
 * PostToolUse hook: profile-edit reminders (project-owned, no ck dependency).
 *
 * Fires after Edit/Write on docs/profiles/*.md and surfaces two reminders:
 *   1. Consistency: suggest psy:crossref --pair + psy:ref-audit --character.
 *   2. Size guard: warn if the profile file exceeds the 300-line limit
 *      (docs/rules/01-profile-structure.md).
 *
 * Standalone: reads hook data from stdin, no ck-config-utils gate. Fail-open —
 * always emits { continue: true } so an error never blocks the edit.
 *
 * @hook-class nudge
 */

const fs = require("fs");
const { isHookEnabled } = require("./lib/hook-config-utils.cjs");

let logHookCrash = () => {};
try { ({ logHookCrash } = require("./lib/hook-logger.cjs")); } catch {}

const PROFILE_PATH_RE = /docs\/profiles\//;
const MARKDOWN_RE = /\.md$/;
const SIZE_LIMIT = 300;

function resolveFilePath(hookData) {
  const toolInput = hookData.tool_input || {};
  return (
    toolInput.file_path || toolInput.path || process.env.CLAUDE_FILE_PATH || ""
  );
}

function buildReminder(filePath) {
  if (!PROFILE_PATH_RE.test(filePath) || !MARKDOWN_RE.test(filePath)) return "";

  const character = (filePath.match(/profiles\/([^/]+)/) || [])[1] || "?";
  const fileName = filePath.split("/").pop();
  const lines = [
    `⚠️ Profile edited: ${character}/${fileName} — consider running psy:crossref --pair and psy:ref-audit --character to validate consistency.`,
  ];

  try {
    const lineCount = fs.readFileSync(filePath, "utf8").split("\n").length;
    if (lineCount > SIZE_LIMIT) {
      lines.push(
        `⚠️ PROFILE SIZE WARNING: ${fileName} is ${lineCount} lines (limit: ${SIZE_LIMIT}). Consider splitting per docs/rules/01-profile-structure.md.`,
      );
    }
  } catch (e) {
    // file unreadable (e.g. deleted) — skip size check
  }

  return lines.join("\n");
}

function main() {
  try {
    if (!isHookEnabled("profileEditReminder")) {
      console.log(JSON.stringify({ continue: true }));
      return;
    }
    const stdin = fs.readFileSync(0, "utf8");
    const hookData = JSON.parse(stdin || "{}");
    const reminder = buildReminder(resolveFilePath(hookData));

    const result = { continue: true };
    if (reminder)
      result.additionalContext = `\n\n[Profile Reminder]\n${reminder}`;
    console.log(JSON.stringify(result));
  } catch (e) {
    try { logHookCrash("profile-edit-reminder", e, { event: "PostToolUse" }); } catch {}
    console.log(JSON.stringify({ continue: true }));
  }
}

main();
