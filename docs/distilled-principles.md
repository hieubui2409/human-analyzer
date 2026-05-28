# Distilled Principles — Cross-Domain Invariants

Principles that recur across **more than one framework**, distilled from the 15 framework rules
(`docs/rules/01`–`15`). Each cites its supporting rules (≥2, else it isn't cross-domain) + the
frameworks it spans. **These are summaries, not new rules** — the source rules remain authoritative;
if a principle and a rule ever diverge, the rule wins.

> Source = `docs/rules/*` (project framework rules) only. The `.claude/rules/*` engineering rules
> (ck-origin) are out of scope here.

---

## P1 — Evidence before claim

**Frameworks:** MAT + PSY + CRE
**Spans rules:**
- `02-clinical-reference-usage` — show-don't-tell; mandatory citation for any clinical assertion.
- `04-materials-ingestion` — source priority P1–P4 before a source counts.
- `11-mat-pipeline` — evidence tiers T1–T5 + CRAAP; material must be *integrated* before PSY reads it.
- `14-cre-evidence-and-events` — CRE output gated by the evidence tier of the claim it rests on.

**Invariant:** no statement — clinical formulation or published content — exists without a traceable,
tiered evidence source. MAT assigns the tier, PSY cites it, CRE is permitted/denied by it.

## P2 — Cross-character consistency

**Frameworks:** PSY + GRO + CRE
**Spans rules:**
- `01-profile-structure` — every character uses the same universal 25-file schema (tooling stays character-agnostic).
- `08-cross-validation` — 10-dimension consistency (4 core + 6 extended) across characters; timelines must agree.
- `15-gro-framework` — GRO career/competency data must align with PSY formulation + shared timelines.

**Invariant:** the 3 characters share one schema and one timeline space; a fact stated for one character
must not contradict another's profile, growth record, or the events both reference.

## P3 — Privacy before publish

**Frameworks:** CRE + COM + PSY
**Spans rules:**
- `09-confidentiality-protocol` — privacy tags + content boundaries define what may leave the system.
- `03-content-creation-pipeline` — the 7-stage pipeline gates each stage on confidentiality.
- `14-cre-evidence-and-events` — CRE recalibration honours both evidence tier *and* confidentiality.

**Invariant:** nothing reaches a platform until it has cleared a privacy/confidentiality scan
(`cre:privacy-guard`). Sensitive profile material is gated at the boundary, not after the fact.

## P4 — Cascade-chain integrity

**Frameworks:** ORC + PSY + CRE
**Spans rules:**
- `12-orc-orchestration` — event system + domain boundaries; domains communicate via events, not direct writes.
- `13-orc-workflow` — end-to-end tracks (MAT→PSY→CRE + GRO↗PSY+CRE) must complete without orphaned state.
- `07-narrative-twist-protocol` — a revealed falsehood cascades (strikethrough + downstream refresh).

**Invariant:** a change in one domain propagates along its defined cascade. New material refreshes the
formulation which recalibrates content; a retracted fact invalidates everything downstream of it.
No domain silently diverges from an upstream change.

## P5 — Staged rigor before integration

**Frameworks:** MAT + PSY + ORC
**Spans rules:**
- `05-wave-pipeline` — profiles built in 3 waves (Foundation → Deep Dive → Validation); no skipping to output.
- `11-mat-pipeline` — 5-stage MAT pipeline with an integration gate that blocks premature analysis.

**Invariant:** raw input is never consumed at face value. MAT gates block analysis until material is
integrated; PSY builds in validated waves. Rigor is staged, and each stage gates the next.

---

## Maintenance

Re-derive when a rule changes materially. A new principle qualifies only if ≥2 rules support it and it
spans ≥2 frameworks. Referenced from `CLAUDE.md`.
