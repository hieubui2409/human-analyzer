---
name: psy:ref-audit
description: "Audit clinical psychology references bidirectionally: profile→ref accuracy, ref→ref cross-linkage, and discover missing theories in profiles/materials/refs. Mostly HEURISTIC — scripts gather candidates, LLM judges clinical relevance. Use after profile updates, periodically, or when adding new references. Triggers: 'audit refs', 'check clinical accuracy', 'ref audit', 'psychology check', 'validate references', 'missing theories', 'cross-ref check'."
argument-hint: "[--character <name>|--all|--term <term>|--discover|--cross-ref|--report]"
metadata:
  author: hieubt
  version: "2.0.0"
  category: "validation"
  position: "post-work"
  dependencies: []
---

# Reference Audit — Bidirectional Clinical Validation

Audit clinical references in ALL directions. Scripts do deterministic gathering; LLM does heuristic judgment.

## Detection Directions

| Direction                | What it finds                                                                                  | Method                             |
| ------------------------ | ---------------------------------------------------------------------------------------------- | ---------------------------------- |
| Profile → Ref            | Clinical terms in profiles without matching ref file                                           | Script gathers + LLM judges        |
| Ref → Ref                | Reference files mentioning theories without their own ref                                      | Script gathers + LLM judges        |
| Profile → Ref (implicit) | Psychology-related PHRASES in profiles not using formal terms but describing clinical concepts | PURE HEURISTIC — LLM reads context |
| Ref → Profile            | Theories in ref library that SHOULD appear in profiles but don't                               | Script maps + LLM assesses fit     |

## Flags

| Flag                 | Purpose                                                          |
| -------------------- | ---------------------------------------------------------------- |
| `--all`              | Audit all 3 characters (default)                                 |
| `--character <name>` | Audit one character                                              |
| `--deep`             | Add behavioral cluster scan alongside clinical terms             |
| `--term <term>`      | Search specific term across all profiles                         |
| `--discover`         | Bidirectional blind spot detection (profiles + materials + refs) |
| `--cross-ref`        | Inter-reference linkage audit (ref↔ref)                          |
| `--report`           | Save report to plans/reports/                                    |

## Workflow: Default Audit (--all / --character)

### Step 1: Build Reference Index (script)

Run `scripts/build-reference-index.py` → JSON map of `{theory → file, category, key_terms[]}`

### Step 2: Scan Profiles (script + heuristic)

1. Run `scripts/scan-clinical-terms.py --character <name>` → candidate term list with line + context
2. With `--deep`: also run `scripts/scan-clinical-terms.py --character <name> --deep` → adds behavioral cluster hits (theories described as behavior without formal terms). Behavioral hits tagged `source: behavioral` vs clinical hits `source: clinical`.
3. **HEURISTIC PHASE:** LLM reviews each candidate:
   - Is this term used in CLINICAL context or everyday language?
   - Example: "attachment to his hometown" = casual. "anxious attachment pattern" = clinical
   - "phủ nhận" in Vietnamese could be casual denial or clinical Denial defense mechanism — read 2-3 surrounding sentences to judge
4. For confirmed clinical terms, check against ref index

### Step 3: Classify (heuristic)

| Classification | Meaning                                                | Action                                |
| -------------- | ------------------------------------------------------ | ------------------------------------- |
| ACCURATE       | Term used correctly, ref exists                        | None                                  |
| UNREFERENCED   | Clinical term, no ref file exists                      | Suggest psy:ref-create                |
| MISAPPLIED     | Ref exists but term used in wrong context              | Suggest correction                    |
| INFORMAL       | Colloquial use, acceptable for content                 | Note only                             |
| IMPLICIT       | Profile describes clinical concept without formal term | Suggest adding formal term + ref link |

**IMPLICIT is the key heuristic category.** Examples:

- Profile says "Nhân vật A luôn cố gắng cứu mọi người xung quanh" → implicitly describes Savior Complex without naming it
- Profile says "Nhân vật B sợ bị bỏ rơi nên luôn chiều theo" → implicitly describes anxious attachment + fawn response
- Profile says "Nhân vật C lặp lại pattern bị bỏ rơi" → implicitly describes repetition compulsion

### Step 4: Generate Report

```markdown
# Reference Audit Report — {scope}

**Date:** {YYYY-MM-DD} | **Refs available:** {N}

## Summary

| Character | Accurate | Unreferenced | Misapplied | Informal | Implicit |
| --------- | -------- | ------------ | ---------- | -------- | -------- |

## Detailed Findings

### {Character}

#### IMPLICIT Concepts (heuristic detection)

- (SOUL.md:L{n}): "{context}" → implicitly describes **{theory}**
  - Ref exists: {yes/no} | Action: {add formal term / create ref / link}
```

## Workflow: --discover (Bidirectional Blind Spots)

Scan ALL directions for missing theories. This is MOSTLY HEURISTIC.

### Direction 1: Materials → Ref gaps

1. Run `scripts/scan-clinical-terms-in-materials.py` → candidates
2. LLM judges: clinical or casual? New theory or variant of existing?

### Direction 2: Ref → Ref gaps (NEW)

1. Run `scripts/scan-reference-cross-links.py` → find theories mentioned INSIDE ref files that don't have own ref file
2. Example: `savior-complex.md` discusses "co-dependency patterns" → check if `co-dependency.md` exists
3. Example: `parentification.md` mentions "role reversal" → check if `role-reversal.md` exists
4. LLM judges: does the mentioned concept warrant its own ref file, or is it adequately covered as subsection?

### Direction 3: Profile → Ref implicit gaps (PURE HEURISTIC)

1. LLM reads each character's SOUL.md + DARKNESS.md + LIGHT.md carefully
2. Identify psychology-related DESCRIPTIONS that don't use formal terms:
   - Behavioral patterns that map to known theories
   - Coping strategies that match clinical defense mechanisms
   - Relationship dynamics that reflect attachment styles
   - Vietnamese cultural expressions of clinical concepts
3. For each implicit concept: does it already have a ref? Should it?

### Output

```markdown
## Bidirectional Discovery Report

### New Theories Needed (from all directions)

| Source | Term/Concept | Direction | Found in | Ref exists? | Action |
| ------ | ------------ | --------- | -------- | ----------- | ------ |

### Ref → Ref Missing Links

| Reference A | Mentions | Ref B exists? | Action |
| ----------- | -------- | ------------- | ------ |

### Profile Implicit Concepts (heuristic)

| Character | File:Line | Description | Maps to theory | Ref exists? |
| --------- | --------- | ----------- | -------------- | ----------- |
```

## Workflow: --cross-ref (Inter-Reference Audit)

1. Run `scripts/scan-reference-cross-links.py` → linkage inventory
2. For each ref file, check:
   - Which OTHER theories it mentions (by name or concept)
   - Are mentions markdown links or plain text?
   - Are there LOGICALLY related theories not mentioned at all?
3. LLM assesses "missing" category — clinically, should these be linked?
4. Report: linked, mentioned-only, missing-but-should-exist

## Scripts

| Script                                        | Phase     | Purpose                                                   |
| --------------------------------------------- | --------- | --------------------------------------------------------- |
| `scripts/build-reference-index.py`            | Gathering | Parse INDEX.md → JSON theory map                          |
| `scripts/scan-clinical-terms.py`              | Gathering | Grep profiles for clinical terms (+ behavioral w/ --deep) |
| `scripts/scan-clinical-terms-in-materials.py` | Gathering | Grep materials/assets for terms                           |
| `scripts/scan-reference-cross-links.py`       | Gathering | Check ref↔ref linkage                                     |

**Scripts do GATHERING only. LLM does all JUDGMENT.** Scripts may over-flag (false positives expected) — that's by design. Better to over-gather than miss genuine clinical concepts.

## Safety

- READ-ONLY — never modifies profiles, references, or content
- Writes only to stdout or plans/reports/ (with --report)
- Scope: bidirectional clinical accuracy validation. Does NOT create refs, edit profiles, or generate content.

## Examples

```bash
/psy:ref-audit                    # default: all chars, all directions
/psy:ref-audit --character hòa    # one character
/psy:ref-audit --discover         # bidirectional blind spot scan
/psy:ref-audit --cross-ref        # ref↔ref linkage only
/psy:ref-audit --term "repetition compulsion"  # specific term
/psy:ref-audit --discover --cross-ref --report  # full audit + save
```

## See Also

- `/psy:ref-scan` — reverse direction: theory → where it applies in profiles
- `/psy:ref-create` — create new ref files for discovered gaps
- `/psy:crossref` — cross-character consistency (different dimension)
