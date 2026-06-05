# Verdict cache contract — re-runnable LLM judgments (load when running crossref / voice-audit / propagate)

The token-efficiency layer for heuristic skills. A re-judge of an UNCHANGED profile section issues ZERO LLM
calls; only changed sections are re-judged. The script keys + stores; the LLM judges. A miss is always safe.

## Mechanism
- `platform_lib/verdict_cache.py` (built on `cache_store.py`): keys a verdict on
  `check | node | content_hash(section-as-on-disk) | lang | dep_hash`. Content-hash reflects the WORKING TREE,
  so an uncommitted edit invalidates the entry (no stale-tree hit).
- Stored value = a verdict LABEL only (`{label, score?, confidence?, ref?, note?}`, scalars, ≤512 chars). Raw
  profile text is structurally rejected → the committed cache carries NO clinical PII (Rule 09 safe).

## LLM orchestration loop (per dimension / per asset)
1. Gather the section(s) deterministically (existing gather scripts).
2. `verdict_cache.lookup(check, ids, bodies, lang)` — on HIT, reuse the cached label; **skip re-judging**.
3. On MISS, judge as normal, then `verdict_cache.record(check, ids, bodies, label)`.
4. `--fresh` forces a full miss everywhere (re-judge all) — honor it on every cache-consuming skill.

## NEVER_CACHED (safety — always re-run)
`crisis_assess`, `narrative_twist`, `contradiction`. `lookup` always misses, `record` refuses. A safety verdict
against a profile or an approved artifact must be re-derived every time.

## Cross-scope inheritance (psy:propagate)
When a change fans across the dyad graph, `psy:propagate` passes the SOURCE verdict as `inherited_context` to
unchanged neighbours and rolls up "N of M neighbours carry the flag" — an ECONOMIC gate only (never a safety
decision). Unchanged neighbours roll up instead of re-judging cold.

## CLI (for manual / orchestration use)
```
verdict_cache.py --check <dim> --ids a,b --bodies-file sections.json [--lang vi] [--fresh] [--store '<json label>']
```

## Consumers
- `psy:crossref` — per-dimension verdicts (the 6 LLM-judgment dimensions; the 4 deterministic ones stay script).
- `cre:voice-audit` — per-asset voice/tone verdict.
- `psy:propagate` — inheritance/rollup.
