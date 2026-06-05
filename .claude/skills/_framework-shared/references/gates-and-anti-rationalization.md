# GATEs + Anti-Rationalization — load every turn

High-salience restatement of the self-decision rules in `.claude/rules/review-audit-self-decision.md`
(§1–5). The rule file remains authoritative + nuanced; these `<GATE-*>` blocks make the load-bearing
invariants unmissable. Load this file **every turn**, flagged or not.

<GATE-VERIFIED-STICKY>
A decision verified by reading source / running a test / an empirical check is LOCKED with its source note
(`verified by {file:line}` or `verified by test {name}`). An audit or red-team counter-argument ALONE does not
reverse it. Revise only when the audit brings a NEW issue the verification missed, or context changed since.
Surface a contradiction as "audit says X, but Y is verified by {source} — new data to justify a reverse?" —
never silently flip. (Rule 1.)
</GATE-VERIFIED-STICKY>

<GATE-NO-SILENT-REVERSAL>
Never silently reverse a decision the user already confirmed (thresholds, scope, library, schema, phase,
feature inclusion). Before any cut/change from an audit: trace whether the user explicitly chose it. If yes →
surface (a) the user's original decision verbatim, (b) the audit reasoning, (c) the trade-off, (d) explicit ask
"keep / change / hybrid?". Do NOT apply. Business/scope-boundary decisions are NEVER auto-reversed. Audits lean
YAGNI/minimalism — they are INPUT to the user, not orders. (Rule 3.)
</GATE-NO-SILENT-REVERSAL>

<GATE-SCOUT-FIRST>
For anything answerable by grep/read on the codebase: scout FIRST (grep, read live code, check current state),
then self-rate confidence. ≥85% → answer directly with a `path:line` citation. <85% → ask. Only ask the user
when confidence is low, two sources genuinely conflict (not a stale note already verified), an anomaly needs
human judgment, or the op is high-reversibility risk. Never ask what grep answers in 5s. (Rule 4.)
</GATE-SCOUT-FIRST>

<GATE-THREAT-MODEL>
Before applying an audit finding flagged "too narrow / too loose / risky": identify what the code actually
stores/protects, walk each flagged scenario through that lens (often "theoretically yes, practically no"),
separate real risks (fix) from abstract worries (document rationale); borderline → ask. Look for the failure
mode the reviewer MISSED — it often sits one step from what was flagged. (Rule 2.)
</GATE-THREAT-MODEL>

<GATE-NO-PLAN-REFS-IN-CODE>
Code comments + artifact names (incl. scripts, SQL, workflow YAML, commit messages, CHANGELOG-as-code) must
NOT reference plan taxonomy: phase numbers, finding codes (the backlog `BL-*`, audit labels, red-team labels),
brainstorm sections. Explain the WHY (the invariant/race/trade-off), not the origin. Plan refs belong in
`plans/…` and `STANDARDIZE.md` only — the latter is the explicit learning ledger that maps each applied idea to
its source. Allowed in code: same-codebase symbol names, stable external IDs (RFC/CVE/SQLSTATE/issue#). (Rule 5.)
</GATE-NO-PLAN-REFS-IN-CODE>

## Anti-Rationalization — shortcut → reality

| Shortcut | Reality |
|----------|---------|
| "The audit says cut it, so cut it" | If the user chose it, surface + ask. Audits are input, not orders. (GATE-NO-SILENT-REVERSAL) |
| "I'll just answer from memory" | Scout first. Grep/read live code, then answer with `file:line`. (GATE-SCOUT-FIRST) |
| "This finding sounds scary, apply it" | Walk it through the real threat model. Theoretical ≠ practical. (GATE-THREAT-MODEL) |
| "Re-verify because the red-team disagrees" | Verified is sticky. Only new data reverses it. (GATE-VERIFIED-STICKY) |
| "Reference the finding code in the comment" | Explain the invariant, not the `BL-xx`. (GATE-NO-PLAN-REFS-IN-CODE) |
| "Script can just decide the verdict" | Scripts gather deterministically; the LLM judges. Never delegate reasoning to a script. |
| "Cache the LLM verdict to save tokens, even for crisis" | Safety verdicts (crisis/twist/contradiction) are NEVER_CACHED — always re-run. |
| "Commit the gather bundle to the cache" | Committed caches store verdict LABELS only — never raw profile text (Rule 09). |
