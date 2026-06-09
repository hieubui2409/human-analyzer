/**
 * bash-write-targets.cjs — extract LITERAL file-write targets from a Bash command.
 *
 * Best-effort speed-bump for the common "LLM tidies up with a literal redirect" case,
 * NOT a security boundary. Only literal path tokens are returned; anything behind a
 * variable ($VAR), command substitution $(...), quotes, heredoc body, or an inline
 * interpreter (python -c / node -e) is deliberately NOT resolved — those are reported
 * via `residual` so the caller can log (never silently swallow) the unguarded write.
 *
 * Pure logic module: requires only Node builtins (no `path` needed). FOSS-clean — safe
 * to project into the public pack. Over-extraction of non-path tokens is harmless: the
 * caller classifies each by sensitivity, and a non-profile token resolves to NONE.
 *
 * @module bash-write-targets
 */
'use strict';

// Split on statement separators that START a new command context. Intentionally NOT
// splitting on a single pipe `|` so `>|` (clobber) and `cmd | tee file` stay intact.
function splitSegments(command) {
  return command.split(/\s*(?:&&|\|\||;|\n)\s*/).filter((s) => s && s.trim().length > 0);
}

function tokenize(s) {
  return s.trim().split(/\s+/).filter(Boolean);
}

// A literal path token = no shell expansion, no flag, no quote-wrapped (which could hide a var).
function isLiteralPath(t) {
  if (!t) return false;
  if (t.startsWith('-')) return false; // flag
  if (/[$`]/.test(t)) return false; // $VAR / `cmd` / $(...)
  if (/^["']/.test(t)) return false; // quoted → treat as non-literal (residual)
  return true;
}

// Strip a fully-literal surrounding quote (`"docs/x.md"` → `docs/x.md`); leave it quoted if
// the inner content still carries an expansion ($ / backtick), so it stays a residual.
function unquote(t) {
  const m = /^(['"])(.*)\1$/.exec(t || '');
  return m && !/[$`]/.test(m[2]) ? m[2] : t;
}

// Redirect operators that write a file: > >> >| &> &>> N> N>>. Ordered so `>|` and `&>`
// are tried before the bare `>` alternative. The target char-class excludes `&` so an
// fd-dup like `2>&1` captures nothing. The fd prefix is bounded (`{0,3}`) so a pathological
// long digit run can't drive O(N²) backtracking in this synchronous PreToolUse path.
const REDIRECT_RE = /(?:>\||&>>?|[0-9]{0,3}>>?)\s*([^\s|&;<>(){}'"$`]+)/g;

// A redirect to a fully-literal QUOTED path (no $ / backtick inside) — common in LLM output
// (`echo x > "docs/profiles/.../t.md"`). The inner path is returned unquoted.
const QUOTED_REDIRECT_RE = /(?:>\||&>>?|[0-9]{0,3}>>?)\s*(['"])([^'"$`]+)\1/g;

function redirectTargets(seg) {
  const out = [];
  REDIRECT_RE.lastIndex = 0;
  let m;
  while ((m = REDIRECT_RE.exec(seg))) {
    if (m[1]) out.push(m[1]);
  }
  QUOTED_REDIRECT_RE.lastIndex = 0;
  while ((m = QUOTED_REDIRECT_RE.exec(seg))) {
    if (m[2]) out.push(m[2]);
  }
  return out;
}

// tee [-a] FILE...  (stop at a pipe — those are downstream commands, not tee args)
function teeTargets(seg) {
  const m = seg.match(/\btee\b\s+([^|]*)/);
  if (!m) return [];
  return tokenize(m[1]).map(unquote).filter((t) => !t.startsWith('-') && isLiteralPath(t));
}

// sed -i / perl -i in-place edit. Over-extract every path-ish literal token after the
// command (the `s/x/y/` script token resolves to NONE, so including it is harmless).
function inPlaceTargets(seg) {
  if (!/\b(?:sed|perl)\b/.test(seg)) return [];
  if (!/(?:^|\s)(?:-i\S*|--in-place\S*)(?:\s|=|$)/.test(seg)) return []; // -i or --in-place
  return tokenize(seg)
    .map(unquote)
    .filter((t) => !/^(?:sed|perl)$/.test(t) && !t.startsWith('-') && isLiteralPath(t) && /[/.]/.test(t));
}

// dd of=FILE (bare or quoted)
function ddTargets(seg) {
  const out = [];
  const re = /\bof=(?:(['"])([^'"$`]+)\1|([^\s|&;<>'"$`]+))/g;
  let m;
  while ((m = re.exec(seg))) out.push(m[2] || m[3]);
  return out;
}

// cp/mv SRC... DST → the last arg is the write destination.
function cpMvTarget(seg) {
  const m = seg.match(/\b(?:cp|mv)\b\s+(.*)$/);
  if (!m) return [];
  const toks = tokenize(m[1]).filter((t) => !t.startsWith('-'));
  if (toks.length < 2) return [];
  const dst = unquote(toks[toks.length - 1]);
  return isLiteralPath(dst) ? [dst] : [];
}

/**
 * Extract literal write targets from a Bash command.
 * @param {string} command
 * @returns {string[]} de-duplicated literal path tokens (may over-include non-profile tokens)
 */
function extractWriteTargets(command) {
  if (!command || typeof command !== 'string') return [];
  const out = [];
  for (const seg of splitSegments(command)) {
    out.push(...redirectTargets(seg));
    out.push(...teeTargets(seg));
    out.push(...inPlaceTargets(seg));
    out.push(...ddTargets(seg));
    out.push(...cpMvTarget(seg));
  }
  return [...new Set(out.filter(isLiteralPath))];
}

/**
 * Did the command contain a write construct we could NOT resolve to a literal path?
 * (redirect into $VAR / quote / subshell, or an inline interpreter able to open a file).
 * Lets the caller emit a residual-log marker instead of silently allowing it.
 * @param {string} command
 * @returns {boolean}
 */
function hasResidualWrite(command) {
  if (!command || typeof command !== 'string') return false;
  for (const seg of splitSegments(command)) {
    if (/(?:>\||&>>?|[0-9]{0,3}>>?)\s*[$(`]/.test(seg)) return true; // redirect → bare $VAR / $(...) / `cmd`
    if (/(?:>\||&>>?|[0-9]{0,3}>>?)\s*["'][^"']*[$`]/.test(seg)) return true; // redirect → quoted w/ expansion
    if (/\b(?:python3?|node|perl|ruby)\b[^|;]*\s-(?:c|e)\b/.test(seg)) return true; // inline interpreter
  }
  return false;
}

module.exports = { extractWriteTargets, hasResidualWrite, splitSegments, isLiteralPath };
