# E2E run log — 6 frameworks on the synthetic fixture

Fixture: `e2e/synthetic-project/` (synthetic chars: test-alpha, test-beta — no real PII). Deterministic legs only (no API key). Generated: 2026-06-05T00:00:00Z.

**17/17 steps exit 0.**

| Framework | Feature | Status | Output head |
|---|---|---|---|
| PSY | health-check · completeness | FINDINGS | ✗ File count assertion FAIL: 42/50 files present |
| PSY | crossref · timeline (dim 1) | OK | [ |
| PSY | crossref · bidirectional refs | OK | [ |
| PSY | crossref · extract events | OK | { |
| PSY | timeline-sync | OK | ====================================================================== |
| GRO | validate growth | FINDINGS | ✗ File Count: Expected 8 growth files, missing 8: test-alpha/growth/career-path.md, test-alpha/growth/competencies.md, t |
| GRO | competency gather | OK | ====================================================================== |
| MAT | indexer · coverage gaps | OK | ====================================================================== |
| MAT | indexer · stale materials | OK | ====================================================================== |
| MAT | loader · inventory | OK | ====================================================================== |
| MAT | loader · dup detection | OK | ## Duplicate Material Detection |
| CRE | humanize · scan ai-tells | FINDINGS | Scan: /home/user/human-analyzer/eval/fixtures/ai-slop-sample-vi.md  (strictness=balanced, files=1) |
| CRE | privacy-guard · scan assets | OK | | Severity | File | Line | Violation | Context | |
| CRE | privacy-guard · confidential names | OK | ## Confidential Names Extracted from Profiles |
| LIB | verdict_cache · crisis is never-cached | OK | {"hit": false, "verdict": null, "never_cached": true} |
| LIB | verdict_cache · store+hit a verdict | OK | {"stored": true, "check": "evidential_backing", "ids": ["n1"]} |
| LIB | preferences · read knobs | OK | { |

---

## Raw output

### [PSY] health-check · completeness
`FINDINGS`
```
✗ File count assertion FAIL: 42/50 files present
    Missing: test-alpha/growth/career-path.md
    Missing: test-alpha/growth/competencies.md
    Missing: test-alpha/growth/learning-profile.md
    Missing: test-alpha/growth/mentoring-map.md
    Missing: test-beta/growth/career-path.md
    Missing: test-beta/growth/competencies.md
    Missing: test-beta/growth/learning-profile.md
    Missing: test-beta/growth/mentoring-map.md

======================================================================
  Profile Health Report
======================================================================

  Character    Score    Present    Missing  Grade
  ------------ -------- ---------- -------- -----
  test-alpha   41/100   21/25       4        F

  ─────────────────────────────────────────────────────
```

### [PSY] crossref · timeline (dim 1)
`OK`
```
[
  {
    "slug": "test-alpha",
    "character": "test-alpha",
    "type": "BEFORE_DOB",
    "file": "timeline/overview.md",
    "line": 17,
    "detail": "Date 2000 is before DOB 2026-01-01 (01-15: Born in Hà Nội)"
  },
  {
    "slug": "test-alpha",
    "character": "test-alpha",
    "type": "BEFORE_DOB",
    "file": "timeline/overview.md",
    "line": 18,
    "detail": "Date 09/2018 is before DOB 2026-01-01 (University enrollment at HUST)"
  },
  {
    "slug": "test-alpha",
    "character": "test-alpha",
    "type": "BEFORE_DOB",
    "file": "timeline/overview.md",
    "line": 19,
    "detail": "Date 06/2022 is before DOB 2026-01-01 (Graduation — first in family to complete university)"
  },
  {
    "slug": "test-alpha",
    "character": "test-alpha",
    "type": "BEFORE_DOB",
    "file"
```

### [PSY] crossref · bidirectional refs
`OK`
```
[
  {
    "file": "timeline/overview.md",
    "char1": "test-alpha",
    "char2": "test-beta",
    "char1_mentions_char2": false,
    "char2_mentions_char1": false,
    "bidirectional": false,
    "char1_ref_count": 0,
    "char2_ref_count": 0
  },
  {
    "file": "relationships/family.md",
    "char1": "test-alpha",
    "char2": "test-beta",
    "char1_mentions_char2": true,
    "char2_mentions_char1": true,
    "bidirectional": true,
    "char1_ref_count": 1,
    "char2_ref_count": 1
  },
  {
    "file": "relationships/{mirror}",
    "char1": "test-alpha",
    "char2": "test-beta",
    "char1_mentions_char2": false,
    "char2_mentions_char1": false,
    "bidirectional": false,
    "char1_ref_count": 0,
    "char2_ref_count": 0,
    "detail": "test-alpha/relationships/test-beta.md ↔ test
```

### [PSY] crossref · extract events
`OK`
```
{
  "test-alpha-test-beta": []
}
```

### [PSY] timeline-sync
`OK`
```
======================================================================
  Timeline Sync Report
======================================================================
  Scope: test-alpha, test-beta

  Event                               Status     Details
  ----------------------------------- ---------- ------------------------------

  Summary: 0 MATCH | 0 MISMATCH | 0 MISSING
  All shared events consistent.
```

### [GRO] validate growth
`FINDINGS`
```
✗ File Count: Expected 8 growth files, missing 8: test-alpha/growth/career-path.md, test-alpha/growth/competencies.md, test-alpha/growth/learning-profile.md, test-alpha/growth/mentoring-map.md, test-beta/growth/career-path.md, test-beta/growth/competencies.md, test-beta/growth/learning-profile.md, test-beta/growth/mentoring-map.md

======================================================================
  GRO Validation Report
======================================================================

  Character    Pass   Warn   Fail   Score
  ------------ ------ ------ ------ -----
  test-alpha   3      0      4      43/100

  ────────────────────────────────────────────────────────────
  test-alpha — Findings
  ────────────────────────────────────────────────────────────

  #    Check        
```

### [GRO] competency gather
`OK`
```
======================================================================
  test-alpha (test-alpha) — Competency Data Gathering
======================================================================

  [growth/competencies.md]
  MISSING — file does not exist

  [Achievements — Skill-relevant]
    - ## Award: Best Intern
    - ## Scholarship: Merit-Based Tuition Waiver

  [Materials — Skill Keywords]
  Matching files: 3

======================================================================
  Summary: 1 characters gathered
  Next: LLM assesses skill distribution, strengths, gaps
======================================================================
```

### [MAT] indexer · coverage gaps
`OK`
```
======================================================================
  test-alpha (test-alpha) — 1 covered | 7 sparse | 17 empty
======================================================================
  Section                                  Mats  Tiers        Status  
  ---------------------------------------- ----- ------------ --------
  ✗ INDEX.md                               0     —            empty   
  ~ CURRENT-STATE.md                       1     T3           sparse  
  ✗ milestones.md                          0     —            empty   
  ✓ identity/core.md                       3     T1,T2,T3     covered 
  ✗ identity/writing-voice.md              0     —            empty   
  ✗ identity/achievements.md               0     —            empty   
  ✗ identity/media-coverage.md
```

### [MAT] indexer · stale materials
`OK`
```
======================================================================
  test-alpha (test-alpha) — 2 stale materials (>7 days)
======================================================================
  File                                     Status         Updated      Days 
  ---------------------------------------- -------------- ------------ -----
  transcript-t1-raw.md                     raw            2025-01-15   506  
  conversation-t3-contradict.md            extracted      2025-03-10   452  

  TOTAL: 2 stale materials
```

### [MAT] loader · inventory
`OK`
```
======================================================================
  test-alpha (test-alpha) — 3 materials
======================================================================
  File                                     Type             Tier Status       FM  
  ---------------------------------------- ---------------- ---- ------------ ----
  conversation-t3-contradict.md            conversation_log T3   extracted    ✓   
  document-t2-complete.md                  document         T2   integrated   ✓   
  transcript-t1-raw.md                     interview        T1   raw          ✓   

  TOTAL: 3 materials across 1 character(s)
```

### [MAT] loader · dup detection
`OK`
```
## Duplicate Material Detection

Scanned: /home/user/human-analyzer/e2e/synthetic-project/docs/materials
Filtered to: test-alpha

No duplicate pairs found.
```

### [CRE] humanize · scan ai-tells
`FINDINGS`
```
Scan: /home/user/human-analyzer/eval/fixtures/ai-slop-sample-vi.md  (strictness=balanced, files=1)
  Findings: 15

  • /home/user/human-analyzer/eval/fixtures/ai-slop-sample-vi.md  (15)
      [high  ] formulaic_opener   @0     Trong thế giới ngày nay
      [high  ] filler_phrase      @25    không thể phủ nhận rằng
      [high  ] filler_phrase      @59    đáng chú ý là
      [medium] filler_phrase      @85    Điều này cho phép
      [low   ] filler_phrase      @112   tận dụng
      [medium] filler_phrase      @121   dữ liệu tươi
      [medium] filler_phrase      @134   một cách hiệu
      [medium] filler_phrase      @152   nhằm mục đích
      [low   ] filler_phrase      @194   mạnh mẽ
      [low   ] filler_phrase      @205   toàn diện
      [medium] filler_phrase      @216   Nó đóng vai trò
```

### [CRE] privacy-guard · scan assets
`OK`
```
| Severity | File | Line | Violation | Context |
| --- | --- | --- | --- | --- |
| _(empty)_ |
[OK] 1 files scanned, 0 violations — CRITICAL=0 HIGH=0 MEDIUM=0 LOW=0
```

### [CRE] privacy-guard · confidential names
`OK`
```
## Confidential Names Extracted from Profiles

These names MUST NOT appear unredacted in assets/:


**0 tag(s) found** across 2 character(s).


**No [CONFIDENTIAL: name] tags found.** Either profiles are clean or tags not yet applied.
```

### [LIB] verdict_cache · crisis is never-cached
`OK`
```
{"hit": false, "verdict": null, "never_cached": true}
```

### [LIB] verdict_cache · store+hit a verdict
`OK`
```
{"stored": true, "check": "evidential_backing", "ids": ["n1"]}
```

### [LIB] preferences · read knobs
`OK`
```
{
  "crossref_rigor": "standard",
  "cre_action_prompting": "standard",
  "humanize_strictness": "balanced"
}
```
