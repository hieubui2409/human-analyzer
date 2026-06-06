# orc:graph — Guide

> For the operator. Vietnamese: [`GUIDE-VI.md`](./GUIDE-VI.md).

## 1. What this skill does for you

You're exploring Character B's profile and want to understand: which theories apply to her? which other characters interact with her? which materials mention her? Graph queries the knowledge graph (derived from markdown) and shows all connected files. It's like a file search engine for relationships.

## 2. Core concepts (the mental model)

**Knowledge graph = markdown-derived adjacency.** Files and their explicit links form nodes and edges. Not exhaustive (misses text-mentions), but fast and queryable.

**Hops = distance.** 1 hop = Character B's own files. 2 hops = files that cite Character B + files Character B cites.

**Graph is disposable.** Rebuilt lazily; always in sync with markdown because it's derived fresh.

## 3. Learning path

**Query a character:** `orc:graph query character-a --hops 2` — Character A and related files.

**Query a theory:** `orc:graph query savior-complex --hops 1 --types profile` — which profiles cite this theory.

**Check health:** `orc:graph stats` — how many nodes/edges, by type.

**Validate:** `orc:graph validate` — find orphans, missing refs.

## 4. Use cases (each = a sample conversation)

### Use case: Find related files for a character

> You: "Show me everything related to Character B."
>
> Skill: Queries graph: Character B (1 hop) = her 25 profile files. Character B (2 hops) = theories she cites + characters she's linked to + materials mentioning her. You see the full relationship web.

### Use case: Find which profiles cite a theory

> You: "Which characters reference attachment theory?"
>
> Skill: Queries: theory node "attachment-style" → inbound edges from profiles. Shows: Character B, Character A, Character C all cite it. You know which profiles to review for consistency.

### Use case: Graph health check

> You: "Is the knowledge graph healthy?"
>
> Skill: Stats: 127 nodes, 234 edges, 8 orphans (unreachable files), 2 missing refs (files cite deleted theories). You know: mostly healthy, but 8 orphans need investigation.

## 5. Important caveats

- **Graph is advisory, not exhaustive.** Text-scan scripts (psy:ref-scan) are authoritative for "is this theory used anywhere."
- **Graph misses Vietnamese prose.** Theory mentioned in Vietnamese comment? Graph won't see it. Use text-scan for completeness.
- **1 hop ≠ all files.** At hops=1, you only get one character's own files. Increase hops to reach relationships.
- **Rebuild is automatic.** If markdown changed, graph re-derives on next query. No manual sync needed.
