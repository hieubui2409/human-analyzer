#!/usr/bin/env bash
# CE-02 skill-conformance gate (C3-ext) — chains the deterministic conformance
# tiers over PROJECT-OWNED skills and exits non-zero if any skill BLOCKs.
#
#   T1-T2  progressive-disclosure + description format  (audit-skill-progressive-disclosure.py)
#   T4     cross-ref integrity                          (validate-skill-crossrefs.py)
#   T5     trigger-accuracy eval (opt-in, --eval)       (skill-creator/run_eval.py, READ-ONLY)
#
# READ-ONLY: emits a verdict report; never edits SKILL.md, never applies a refactor.
# ck-origin skills are hard-excluded by the audit's Tier-0 scope guard.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"   # .claude/scripts -> .claude
PROJECT_ROOT="$(cd "$PROJECT_ROOT/.." && pwd)" # .claude -> repo root
PYTHON="${PROJECT_ROOT}/.claude/skills/.venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON="${HOME}/.claude/skills/.venv/bin/python3"
SKILLS="$PROJECT_ROOT/.claude/skills"
AUDIT="$SKILLS/orc-skill-stocktake/scripts/audit-skill-progressive-disclosure.py"
CROSSREF="$PROJECT_ROOT/.claude/scripts/validate-skill-crossrefs.py"

cd "$PROJECT_ROOT"

RUN_EVAL=0
[ "${1:-}" = "--eval" ] && RUN_EVAL=1

FAILED=0

echo "========================================"
echo "  CE-02 Skill Conformance Gate"
echo "========================================"

echo ""
echo "  [T1-T2] Progressive disclosure + description format (project-owned)..."
if "$PYTHON" "$AUDIT" "$SKILLS" --scope project-owned --strict; then
    echo "  ✓ T1-T2: 0 BLOCK"
else
    echo "  ✗ T1-T2: BLOCK present — see findings above"
    FAILED=1
fi

echo ""
echo "  [T4] Cross-reference integrity..."
if "$PYTHON" "$CROSSREF" "$SKILLS" >/tmp/conformance-crossref.out 2>&1; then
    echo "  ✓ T4: cross-refs resolve"
else
    echo "  ✗ T4: broken cross-refs"
    tail -10 /tmp/conformance-crossref.out
    FAILED=1
fi

if [ "$RUN_EVAL" = "1" ]; then
    echo ""
    echo "  [T5] Trigger-accuracy eval (opt-in)..."
    RUN_EVAL_PY="$SKILLS/skill-creator/scripts/run_eval.py"
    TESTSETS="$PROJECT_ROOT/.claude/scripts/conformance-testsets"
    if [ ! -d "$TESTSETS" ] || [ -z "$(ls -A "$TESTSETS" 2>/dev/null)" ]; then
        echo "  ⊘ T5 skipped: no testsets under conformance-testsets/ (author per-skill should/should-not sets first)"
    elif [ ! -f "$RUN_EVAL_PY" ]; then
        echo "  ⊘ T5 skipped: skill-creator/run_eval.py not present"
    else
        for ts in "$TESTSETS"/*.json; do
            skill="$(basename "$ts" .json)"
            echo "    eval: $skill"
            "$PYTHON" "$RUN_EVAL_PY" --eval-set "$ts" \
                --skill-path "$SKILLS/$skill" || FAILED=1
        done
    fi
fi

echo ""
echo "========================================"
if [ "$FAILED" = "0" ]; then
    echo "  GATE: PASS (0 BLOCK)"
    echo "========================================"
    exit 0
else
    echo "  GATE: FAIL — fix BLOCK findings before phase completion"
    echo "========================================"
    exit 1
fi
