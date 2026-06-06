# cre:evidence-scanner — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You've written a post: "My mentorship with Character C transformed his approach to risk." Before publishing, you want to know: Is this claim backed by evidence? Did I accidentally leak something private? This skill extracts that claim, finds evidence materials (T1-T5), judges "mentorship transformation" as PASS (supported by T1 session notes) or WARN (tertiary interpretation), and flags any `[CONFIDENTIAL]` tags. One clean verdict per claim.

## 2. Core concepts (the mental model)

**Three-layer pipeline:**

1. **Extract (deterministic):** Script segments content into atomic claims (VN-aware tokenization). One claim per sentence/idea.
2. **Gather (deterministic):** Script collects candidate materials by keyword/entity overlap, assigns tiers, detects privacy tags. Over-gathers; false positives expected.
3. **Adjudicate (heuristic):** LLM reads candidates and decides "does this material actually support the claim?" (CiteAudit Reasoner). Finalize PASS/WARN/FAIL.

**Verdict policy (FAIL-CLOSED):**
- T1/T2 evidence → PASS
- T3 (tertiary) → WARN (can be published, but flag for caution)
- T4/T5 (weak) → FAIL (not publishable without explicit qualification)
- Privacy leak (raw DSM code, `[CONFIDENTIAL]`, clinical term) → FAIL
- No evidence found → WARN (never silent PASS)

**Single source of truth:** `evidence_tier_permissions.py` lives once; imported by both this skill and `cre:post-writer`. Zero duplication.

## 3. Learning path

**First run:** Scan a published post:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-evidence-scanner/scripts/map-claims-to-evidence-tiers.py \
  assets/linkedin/260526-mentorship --json
```
You'll see a table: Claim | Evidence tier | Verdict. Read a WARN claim — it means the backing material is T3 (tertiary, less reliable), but it's still publishable.

**As you grow:** Try `--strict` to convert all T3→FAIL (zero tolerance). Good for research papers; relaxed for personal storytelling where the author is T1 source.

**Standard flow:** `cre:post-writer` calls this automatically in Phase 6. For published assets, you can re-run it as a periodic audit.

## 4. Use cases (each = a sample conversation)

### Use case: Pre-publish validation

> **You:** "I wrote a LinkedIn post about Character A's career pivot. Before I hit publish, check it."
>
> **Skill:** `--asset assets/linkedin/260526-pivot` → extracts 8 claims, maps to materials, returns verdicts. 6 PASS, 2 WARN (tertiary interpretation of growth signals).
>
> **You:** Review the WARN claims, decide if you want to qualify them or rewrite.

### Use case: Batch audit with strict mode

> **You:** "I need to audit 10 published posts. Flag anything that's not T1-T2."
>
> **Skill:** Loop `--asset` over each dir with `--strict`. Any T3 → FAIL, exit 1.
>
> **You:** Fix FAILs, re-run to confirm.

### Use case: Privacy leak detection

> **You:** "Before repurposing, check if this post leaked anything private."
>
> **Skill:** `--asset` → runs privacy-tag scan as part of evidence check. Flags `[CONFIDENTIAL: Hoà]` on line 12 as FAIL.
>
> **You:** Remove the tag or redact the claim, re-run.

### Use case: Per-variant gate in multiplatform

> **You:** Running `cre:multiplatform`, each variant is auto-checked via this scanner before publish-ready write.
>
> **Skill:** If any variant has a FAIL, that variant is HELD (not written), reported. Other platforms still ship.

## 5. Important caveats

- **Over-gathers on purpose:** Script collects many weak materials; LLM prunes. False positives expected — that's safe (better to ask than miss).
- **T3 is subjective:** Tertiary evidence (interpretation, synthesis) lives in a gray zone. `--strict` treats it as unpublishable; default mode says "publishable but flag it."
- **No silent PASS:** If no evidence found, verdict is WARN, not silent PASS. Author must make a choice.
- **Privacy is binary:** Any leak → FAIL. No negotiation.
- **Clinical terms:** Detects raw DSM/ICD codes and clinical vocabulary. Rule 02 "show-don't-tell" means paraphrase, not quote clinical terms.

## See also

- [`SKILL.md`](./SKILL.md) for technical contract
- `cre:post-writer` (Phase 6 delegate)
- `cre:privacy-guard` — complementary; this is per-claim tier; privacy-guard is asset-wide PII
- Rule 09 (confidentiality), Rule 02 (clinical reference), Rule 14 (CRE evidence)
