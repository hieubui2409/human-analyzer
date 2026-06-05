# psy:relation-intelligence — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You want to write content about Nhân vật A and Nhân vật B's sworn-brother bond. Instead of staring at the blank screen, this skill mines their relationship graph: extracts facts from both profiles (meetings, events, quotes, GRO milestones), ranks them by evidence tier (P1 materials = highest, implicit psychology = lower), checks for confidentiality tags (PRIVATE, CONFIDENTIAL, ANONYMIZE), and proposes angles: "The kết nghĩa ceremony as a turning point" (HIGH evidence, coherence 0.9, consent OPEN) vs "Nhân vật B's vulnerability during gambling crisis" (MEDIUM evidence, concern about crisis boundaries, consent REVIEW). You get ranked angles ready for cre:post-writer, not raw facts.

## 2. Core concepts (the mental model)

- **Three-layer filtering**: (1) Extract facts with evidence tiers. (2) Check confidentiality tags + crisis markers. (3) LLM synthesizes angles; script ranks them.
- **Consent is fail-closed**: Any BLOCKED fact (PRIVATE tag or crisis marker) taints the angle. Blocked angles sink to bottom of rank, flagged ⛔, never silently dropped.
- **primary_character semantics**: Each angle has a POV character (most narrative centrality). cre:post-writer loads ONLY that character's voice; other character appears as described by the main one (Rule A2: voice authenticity).
- **Trauma boundary**: darkness/traumas.md is structurally NEVER read into angle facts. Existence noted as metadata, but detail excluded. Safety gate.

## 3. Learning path

**One dyad:** `psy:relation-intelligence --dyad hieu hoa` — see ranked angles for sworn brothers.

**All dyads:** `psy:relation-intelligence --all` — mine all pairs at once.

**Override POV:** `psy:relation-intelligence --dyad hoa chien --character hoa` — Nhân vật B's perspective on Nhân vật C mentoring.

**With graph signals:** `psy:relation-intelligence --dyad hieu chien --graph-signal` — enrich with KG if available.

## 4. Use cases (each = a sample conversation)

### Use case: Dyadic angle mining

> You: "What content angles exist between Nhân vật A and Nhân vật B?"
> Skill: `psy:relation-intelligence --dyad hieu hoa`
> → Output:
> - ★★★ **"The Kết Nghĩa Turning Point"** | primary: Nhân vật A | consent: OPEN | coherence: 0.92 | evidence: P1 materials + both timelines
> - ★★★ **"Supporting Through Crisis"** | primary: Nhân vật B | consent: REVIEW (mentions gambling, needs sensitivity gate) | coherence: 0.85
> - ★★ **"Unequal Sacrifice"** | primary: Nhân vật A | consent: OPEN | coherence: 0.78 | note: Nhân vật A gives more than receives
> → cre:post-writer loads top OPEN angle first.

### Use case: Cross-character mentoring angle

> You: "What's the content story around Nhân vật A mentoring Nhân vật C?"
> Skill: `psy:relation-intelligence --dyad hieu chien`
> → Top angles: "F15 Scholarship Journey" (Nhân vật C's POV, celebrates milestone), "Mentor's Burden" (Nhân vật A's POV, notes exhaustion risk). Both OPEN for publishing.

### Use case: All dyads at once

> You: "What content angles exist across all three characters?"
> Skill: `psy:relation-intelligence --all --json`
> → JSON: list all 3 dyads × ranked angles. Script processes for downstream automation (angle selection, voice routing, etc.).

## 5. Important caveats

- **Primary character hint is overrideable**: The skill suggests Nhân vật A as "primary" (more edges), but you can set `--character hoa` to flip perspective. Changes which voice loads in cre:post-writer.
- **REVIEW angles need decision**: Angles marked REVIEW have borderline consent issues. Before publishing, confirm: is this publishable, or should we anonymize/reframe?
- **Trauma boundary is strict**: darkness/traumas.md is never parsed for angle facts. If an angle seems to leak trauma detail, investigate — likely a bug or data in wrong file.
- **Evidence tiers inform ranking, not gates**: P1 evidence ranks higher, but a P3 angle can be published if consent is OPEN. Tier is confidence signal, not approval gate.
- **Graph signals are optional enhancement**: KG (knowledge graph) enriches edges if available; without it, skill uses relationship files directly. Both paths work.
