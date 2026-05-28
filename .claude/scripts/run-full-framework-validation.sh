#!/usr/bin/env bash
# Master validation script — runs all framework scripts and reports results.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON="${HOME}/.claude/skills/.venv/bin/python3"
SKILLS="$PROJECT_ROOT/.claude/skills"

cd "$PROJECT_ROOT"

PASSED=0
FAILED=0
TOTAL=0
RESULTS=()

run_check() {
    local framework="$1"
    local name="$2"
    shift 2
    TOTAL=$((TOTAL + 1))
    local output
    if output=$("$@" 2>&1); then
        PASSED=$((PASSED + 1))
        RESULTS+=("✓ ${framework} | ${name}")
    else
        FAILED=$((FAILED + 1))
        RESULTS+=("✗ ${framework} | ${name}")
        echo "  FAILED: $name"
        echo "$output" | tail -5
    fi
}

echo "========================================"
echo "  Framework Validation — Full Pipeline"
echo "========================================"
echo ""

# MAT — Materials Framework
echo "  [MAT] Running materials validation..."
run_check "MAT" "inventory-materials" \
    "$PYTHON" "$SKILLS/mat-loader/scripts/inventory-materials-with-frontmatter-status.py" --json
run_check "MAT" "validate-frontmatter" \
    "$PYTHON" "$SKILLS/mat-loader/scripts/validate-material-frontmatter-against-schema.py" --json
run_check "MAT" "find-stale-materials" \
    "$PYTHON" "$SKILLS/mat-indexer/scripts/find-stale-materials-by-processing-status.py" --json
run_check "MAT" "detect-contradictions" \
    "$PYTHON" "$SKILLS/mat-indexer/scripts/detect-contradictions-materials-vs-profiles.py" --json
run_check "MAT" "coverage-gaps" \
    "$PYTHON" "$SKILLS/mat-indexer/scripts/analyze-evidence-coverage-gaps-per-profile-section.py" --json
run_check "MAT" "craap-template" \
    "$PYTHON" "$SKILLS/mat-loader/scripts/generate-craap-score-template-for-material.py" \
    "docs/materials/character-a/gemini-analysis-job-change-vsf-052026.md" --json

# PSY — Psychology Framework
echo "  [PSY] Running profile validation..."
run_check "PSY" "validate-all-profiles" \
    "$PYTHON" "$SKILLS/psy-crossref/scripts/validate-all-profiles-against-schema.py" --json
run_check "PSY" "ref-create-template" \
    "$PYTHON" "$SKILLS/psy-ref-create/scripts/generate-reference-file-template.py" "Test Theory"

# CRE — Content Creation Framework
echo "  [CRE] Running content validation..."
run_check "CRE" "psy-to-cre-translation" \
    "$PYTHON" "$SKILLS/cre-post-writer/scripts/extract-psy-to-cre-translation-context.py" --json

# Find a real asset dir for CRE checks
ASSET_DIR=$(find assets/facebook -name "post.txt" -type f 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo "")
if [ -n "$ASSET_DIR" ]; then
    run_check "CRE" "evidence-tier-check" \
        "$PYTHON" "$SKILLS/cre-evidence-scanner/scripts/map-claims-to-evidence-tiers.py" "$ASSET_DIR" --json
    run_check "CRE" "voice-consistency" \
        "$PYTHON" "$SKILLS/cre-voice-audit/scripts/check-voice-consistency-against-defense-profile.py" \
        "$ASSET_DIR" --character character-a --json
else
    echo "  (skipping CRE asset checks — no post.txt found)"
fi

# MPC — Orchestration
echo "  [MPC] Running event routing..."
run_check "MPC" "detect-state-changes" \
    "$PYTHON" "$SKILLS/orc-session-state/scripts/detect-domain-state-changes-from-git-diff.py" --ref HEAD~1 --json
run_check "MPC" "task-routing-mat" \
    "$PYTHON" "$SKILLS/orc-intake/scripts/route-task-to-framework-domain.py" "load new chat log" --json
run_check "MPC" "task-routing-psy" \
    "$PYTHON" "$SKILLS/orc-intake/scripts/route-task-to-framework-domain.py" "update profile" --json
run_check "MPC" "task-routing-cre" \
    "$PYTHON" "$SKILLS/orc-intake/scripts/route-task-to-framework-domain.py" "write post" --json

# Summary
echo ""
echo "========================================"
echo "  Results Summary"
echo "========================================"
for r in "${RESULTS[@]}"; do
    echo "  $r"
done
echo ""
echo "  TOTAL: $TOTAL | PASSED: $PASSED | FAILED: $FAILED"
echo "========================================"

if [ "$FAILED" -gt 0 ]; then
    exit 1
else
    echo "  ALL CHECKS PASSED"
    exit 0
fi
