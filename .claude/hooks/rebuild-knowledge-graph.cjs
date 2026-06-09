#!/usr/bin/env node
/**
 * Project-owned SessionStart warm-up for the knowledge graph.
 *
 * Spawns a detached venv-python process that calls get_graph(), so the first skill query of
 * the session hits a warm, already-rebuilt cache instead of paying the build cost inline.
 * Fire-and-forget: it never blocks session start and never fails it (any error is swallowed).
 * The lazy rebuild inside get_graph() remains the source of truth — this is only a head-start.
 *
 * Deliberately self-contained: requires no ck config utilities (project/ck boundary, CAP-1).
 */
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const { isHookEnabled } = require("./lib/hook-config-utils.cjs");

let logHookCrash = () => {};
try { ({ logHookCrash } = require("./lib/hook-logger.cjs")); } catch {}

try {
  if (!isHookEnabled("rebuildKnowledgeGraph")) {
    process.stdout.write(JSON.stringify({ continue: true }));
    process.exit(0);
  }
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const py = path.join(projectDir, ".claude", "skills", ".venv", "bin", "python3");
  const scripts = path.join(projectDir, ".claude", "scripts");
  if (fs.existsSync(py)) {
    const child = spawn(
      py,
      ["-c", "from platform_lib.knowledge_graph import get_graph; get_graph()"],
      { cwd: scripts, env: { ...process.env, PYTHONPATH: scripts }, detached: true, stdio: "ignore" }
    );
    child.unref(); // let it outlive this hook process
  }
} catch (e) {
  /* warm-up is best-effort — a missing venv or spawn error must not break session start */
  try { logHookCrash("rebuild-knowledge-graph", e, { event: "SessionStart" }); } catch {}
}

process.stdout.write(JSON.stringify({ continue: true }));
