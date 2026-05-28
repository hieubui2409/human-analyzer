# CRE Evidence & Event Protocol

Complementary to Rule 03 (Content Creation Pipeline). Defines evidence tier permissions for public content and CRE event specifications.

## Evidence Tier → Content Permissions

Materials processed through the MAT pipeline carry evidence tiers (T1-T5). Content creation MUST respect these tiers.

### Public Content Permissions

| Evidence Tier                     | Public content? | Conditions                                                 |
| --------------------------------- | --------------- | ---------------------------------------------------------- |
| **T1** (Primary self-report)      | Yes             | May quote or paraphrase. Privacy scan required.            |
| **T2** (Corroborated observation) | Yes             | May reference. Cite context, not raw observation.          |
| **T3** (Single observer)          | Qualified       | Must frame as perspective, not fact. "Theo quan sát..."    |
| **T4** (Indirect/reported)        | Restricted      | May inspire angle only. Cannot assert as fact.             |
| **T5** (Speculative/theoretical)  | No              | Internal framework only. Never surfaces in public content. |

### Content-Level Evidence Assertions

When writing public content that references events or facts:

1. **Factual claims** (dates, locations, actions) — require T1 or T2 backing
2. **Emotional framing** (what character felt) — require T1 backing or explicit "suy đoán" qualifier
3. **Relationship dynamics** — require T2+ backing from BOTH characters' materials
4. **Growth narratives** — may use T3 with qualifier: "dần dần" / "có lẽ" / "bắt đầu nhận ra"

### Unsupported Content Handling

If content angle has no material backing (T5-only or gap):

1. Flag via `orc:classify` as risk flag #12 ("MAT evidence gap")
2. Options: (a) find supporting materials via `mat:loader`, (b) reframe angle to supported territory, (c) explicitly mark as creative fiction
3. Never present unsupported content as factual reality post

## CRE Event Specifications

### CRE.recalibrate

**Trigger:** Upstream PSY or MAT change that affects content creation parameters.

| Source Event     | Impact on CRE                                                                        |
| ---------------- | ------------------------------------------------------------------------------------ |
| `MAT.integrated` | New material may provide fresh content angles or invalidate existing drafts          |
| `PSY.refresh`    | Profile update may change voice, defense state, or phase — recalibrate active drafts |
| `PSY.flag`       | Contradiction detected — halt related content until resolved                         |
| `GRO.assessed`   | Competency data changed — may affect career-angle content                            |
| `GRO.profiled`   | Learning profile changed — may affect content style/framing                          |

**Action:** When CRE.recalibrate fires:

1. Check if any active content drafts reference the updated character
2. If yes → re-run voice audit + factual alignment on affected drafts
3. If contradiction found → flag for revision before publish

### CRE.published

**Trigger:** Content successfully passes all 3 quality gates and is published to platform.

**Payload:**

```json
{
  "event": "CRE.published",
  "character": "{slug}",
  "platform": "{platform}",
  "asset_path": "assets/{platform}/{slug}/",
  "evidence_tiers_used": ["T1", "T2"],
  "clinical_refs_cited": ["attachment-theory"],
  "timestamp": "ISO-8601"
}
```

**Downstream:**

- `orc:compounding` may extract content creation learnings
- `orc:session-state` updates `content_created` array
- `psy:arc-tracker` may update character arc trajectory if content reveals growth

### CRE.privacy_cleared

**Trigger:** `cre:privacy-guard` scan passes with zero violations.

**Payload:** File path + scan timestamp. Consumed by post-writer Phase 5 gate.

### CRE.evidence-checked

**Trigger:** `cre:evidence-scanner` finishes a per-claim evidence-tier + Rule-09 scan of an asset (standalone, or via post-writer Phase 6).

**Payload:**

```json
{
  "event": "CRE.evidence-checked",
  "character": "{slug}",
  "asset_path": "assets/{platform}/{slug}/",
  "overall_verdict": "PASS|WARN|FAIL",
  "claim_count": 0,
  "fail_reasons": ["rule09_leak", "tier_T5"],
  "timestamp": "ISO-8601"
}
```

**Routing:** prefix `CRE.*` → `content-events.jsonl`.

**Downstream:**

- A `FAIL` blocks `cre:post-writer` output until claims are fixed (no auto re-draft — logged only, pass@k is a WATCH pattern).
- On a `FAIL` caused by a **Rule-09 leak**, the scanner ALSO emits `COM.governance` → `governance-audit.jsonl` (cross-framework governance trail).
- `cre:evidence-scanner` is the single source of tier-permission logic (`platform_lib/evidence_tier_permissions.py`); post-writer delegates, holds no duplicate.

### CRE.angle-discovered

**Trigger:** `cre:angle-discovery` (B7) finishes mining the 6 frameworks and ranks content angles for a character.

**Payload:**

```json
{
  "event": "CRE.angle-discovered",
  "character": "{slug}",
  "source": "cre:angle-discovery",
  "reason": "top={angle title} framework={psy|mat|gro|cre|orc} score={0-1}",
  "timestamp": "ISO-8601"
}
```

**Routing:** prefix `CRE.*` → `content-events.jsonl`.

**Downstream:**

- The ranked angles feed `cre:exploring` (interactive refinement) or `cre:post-writer --from-context` or `cre:multiplatform --source <angle>`.
- Angle `reason` carries only a paraphrased title/framework/score — never a raw ORC event payload or `[CONFIDENTIAL]` material (red-team R-cross).
- A discovered angle still passes `cre:evidence-scanner` + `cre:privacy-guard` before any variant is written.
- `CRE.published` (already specified above) fires per native variant `cre:multiplatform` writes after all per-variant gates pass.

## PSY → CRE Translation Rules

How psychological profile data translates into content creation:

### Formulation → Content Angle

The 5P formulation (`psychology/formulation.md`) maps to content:

| Formulation P     | Content Translation                               |
| ----------------- | ------------------------------------------------- |
| **Presenting**    | Current struggles → vulnerability/reality content |
| **Predisposing**  | Backstory → narrative arc content                 |
| **Precipitating** | Recent triggers → timely/relevant hooks           |
| **Perpetuating**  | Ongoing patterns → analytical/insight content     |
| **Protective**    | Sources of hope → inspirational/growth content    |

### Defense Mechanisms → Voice Filter

Active defenses (`psychology/defense-mechanisms.md`) constrain HOW character expresses:

| Defense             | Voice Effect                                                           |
| ------------------- | ---------------------------------------------------------------------- |
| Intellectualization | Analytical framing, insight-through-analysis, measured vulnerability   |
| Denial              | Cannot acknowledge denied truth directly — use metaphor                |
| Acting Out          | Raw, impulsive expression — edit for coherence while preserving energy |
| Sublimation         | Transform pain into purpose — natural content voice                    |
| Suppression         | Controlled vulnerability — "measured confession" style                 |

### Archetype → Narrative Stance

Character archetype (`psychology/archetype.md`) influences narrative position:

| Archetype                    | Natural Content Stance                        |
| ---------------------------- | --------------------------------------------- |
| Wounded Healer (Nhân vật A)        | Teacher who teaches from scars, not textbooks |
| Lost Child / Trickster (Nhân vật B) | Survivor who finds humor in darkness          |
| Orphan / Seeker (Nhân vật C)      | Questioner searching for belonging            |

## Cross-Character Content Rules

When content involves multiple characters (cross-character dynamics):

1. Read `docs/graph/{dyad}.md` for documented interaction patterns
2. Verify power dynamics are accurately represented (not flattened)
3. Respect each character's defense mechanisms — one character's vulnerability doesn't override another's
4. Both characters' evidence must support shared events (T2+ for cross-character claims)
5. Run `psy:crossref` validation if content asserts relational change or development

## See Also

- `docs/rules/03-content-creation-pipeline.md` — full pipeline, platform guidelines, output standards
- `docs/rules/09-confidentiality-protocol.md` — privacy tags and content boundaries
- `docs/rules/11-mat-pipeline.md` — evidence tier definitions
- `docs/rules/12-orc-orchestration.md` — event system and domain boundaries
