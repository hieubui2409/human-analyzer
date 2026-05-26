"""Knowledge graph (Layer 1: frontmatter edges) — NetworkX DiGraph over the corpus.

Builds a deterministic "find related files" graph from markdown frontmatter:
profiles, materials, references, graph dyads → nodes; `character`, `cross_characters`,
`references`, `characters` fields → typed edges. In-memory, process-singleton, rebuilt
on demand. Markdown is the source of truth; the graph is derived + disposable.

Layer 1: frontmatter (confidence 0.95). Layer 2: slug-first regex body scan —
reference stems matched against body text (cites_theory) + character names matched
cross-file (cross_character), confidence 0.65-0.80. Layer 3 (embedding) extends
`_build_graph` in a later phase. No existing skill imports this yet — opt-in adoption.

Characters are resolved dynamically from the profiles directory (never hardcoded);
short-name matching uses paths.CHAR_DISPLAY for the diacritic proper-noun form.

Frontmatter is parsed with `yaml.safe_load` (NOT markdown_parser.extract_frontmatter,
which drops multi-line YAML lists — the field shape this graph depends on).
"""
from __future__ import annotations

import re
import time
import unicodedata
from collections import Counter

import networkx as nx
import yaml

from . import paths

# Module-level dir handles, monkeypatchable in tests.
PROFILES = paths.PROFILES
MATERIALS = paths.MATERIALS
REFERENCES = paths.REFERENCES
GRAPH = paths.GRAPH

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_graph_cache: nx.DiGraph | None = None
_undirected_cache: nx.Graph | None = None

# Single-token reference slugs that are also generic English homographs: even with
# repeated mentions their bare appearance is unreliable signal, so drop them entirely
# from body scanning. Multi-token and clinical-jargon single-token slugs are kept.
_SLUG_FP_BLACKLIST = frozenset({"anchoring", "deflection", "displacement"})

# Confidence tiers for Layer 2 body-text edges.
_CONF_BODY_MULTI = 0.80   # slug seen 2+ times
_CONF_BODY_SINGLE = 0.65  # slug seen once (multi-token slugs only)
_CONF_BODY_CHAR = 0.70    # character name seen in another character's file


def _parse_yaml_list(val) -> list[str]:
    """Frontmatter array → list[str]. Handles list / '[a, b]' / 'a' / None."""
    if isinstance(val, list):
        return [str(v).strip() for v in val if v is not None and str(v).strip()]
    if not val or not isinstance(val, str):
        return []
    s = val.strip()
    if s in ("[]", ""):
        return []
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [item.strip() for item in s.split(",") if item.strip()]


def _frontmatter(path) -> tuple[dict, str]:
    """(frontmatter dict, full text). yaml.safe_load preserves multi-line lists."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}, ""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        fm = None
    return (fm if isinstance(fm, dict) else {}), text


def _token_estimate(text: str) -> int:
    return int(len(text.split()) * 1.3)


def _make_fold_table() -> dict[int, str]:
    """Precomputed accented-codepoint -> ascii-base map covering Latin + Vietnamese,
    so _fold can use C-speed str.translate instead of per-char NFD over the corpus."""
    t: dict[int, str] = {}
    for cp in range(0xC0, 0x1F00):
        base = "".join(c for c in unicodedata.normalize("NFD", chr(cp))
                        if unicodedata.category(c) != "Mn")
        if base and base.isascii() and base != chr(cp):
            t[cp] = base.lower()
    t[ord("đ")] = t[ord("Đ")] = "d"
    return t


_FOLD_TABLE = _make_fold_table()


def _fold(s: str) -> str:
    """ASCII-fold + lowercase: 'Nhân vật A' -> 'bui trung hieu'. Folds Vietnamese
    diacritics so a name's accented and unaccented spellings both match one pattern."""
    return s.translate(_FOLD_TABLE).lower()


def _strip_frontmatter(text: str) -> str:
    """Body text only — drop a leading `---`…`---` frontmatter block if present."""
    m = _FM_RE.match(text)
    return text[m.end():] if m else text


_WS_HYPHEN_RE = re.compile(r"[\s\-]+")


def _build_slug_patterns() -> tuple[re.Pattern | None, dict[str, tuple[str, bool]]]:
    """(combined_rx, {slug: (ref_node, is_single_token)}). One alternation regex over
    all reference stems → a single findall per body instead of 71 separate scans. Built
    per rebuild (not module-level) so refs added mid-session are picked up. Longest slugs
    first so 'complex-ptsd' wins over a bare 'complex' prefix. Hyphens match flexible
    whitespace/hyphen so the slug catches 'Complex PTSD'."""
    meta: dict[str, tuple[str, bool]] = {}
    if not REFERENCES.exists():
        return None, meta
    slugs = [f.stem for f in REFERENCES.glob("*.md")
             if f.name != "INDEX.md" and f.stem not in _SLUG_FP_BLACKLIST]
    alts = []
    for slug in sorted(slugs, key=len, reverse=True):
        meta[slug] = (f"docs/references/{slug}.md", "-" not in slug)
        alts.append(re.escape(slug).replace(r"\-", r"[\s\-]"))
    rx = re.compile(r"\b(" + "|".join(alts) + r")\b", re.IGNORECASE) if alts else None
    return rx, meta


def _scan_body_references(body: str, slug_index) -> list[tuple[str, float, int]]:
    """(ref_node, confidence, mention_count) for each reference slug found in body.
    Single-token slugs require 2+ mentions (FP guard); multi-token: 1 mention = 0.65."""
    rx, meta = slug_index
    if rx is None:
        return []
    counts: dict[str, int] = {}
    for m in rx.findall(body):
        key = _WS_HYPHEN_RE.sub("-", m.strip().lower())
        counts[key] = counts.get(key, 0) + 1
    hits = []
    for slug, n in counts.items():
        info = meta.get(slug)
        if not info:
            continue
        ref_node, single = info
        if single and n < 2:
            continue
        conf = _CONF_BODY_MULTI if n >= 2 else _CONF_BODY_SINGLE
        hits.append((ref_node, conf, n))
    return hits


def _corpus_characters() -> dict[str, dict]:
    """char_slug -> {folded_full_rx, display}. Derived from profile subdirectories
    (dynamic — never a hardcoded character list). Diacritic short name from
    paths.CHAR_DISPLAY, falling back to the capitalized last slug token."""
    chars: dict[str, dict] = {}
    if not PROFILES.exists():
        return chars
    for d in sorted(PROFILES.iterdir()):
        if not d.is_dir():
            continue
        slug = d.name
        tokens = slug.split("-")
        full_rx = re.compile(r"\b" + r"[\s\-]+".join(map(re.escape, tokens)) + r"\b")
        display = paths.CHAR_DISPLAY.get(slug) or tokens[-1].capitalize()
        chars[slug] = {"full_rx": full_rx, "display": display, "multi": len(tokens) > 1}
    return chars


def _owning_char(rel: str) -> str:
    """Character that owns a profile/material file, from its path. '' for refs/graph."""
    for base in ("docs/profiles/", "docs/materials/"):
        if rel.startswith(base):
            return rel[len(base):].split("/", 1)[0]
    return ""


def _scan_body_for_characters(body: str, owning: str, chars: dict) -> list[tuple[str, int]]:
    """(char_slug, mention_count) for OTHER characters named in this file's body.
    Full name matched on ASCII-folded body (accent-insensitive); short name matched
    as the diacritic proper noun (case-sensitive) to avoid folding 'hóa'→'Nhân vật B' FPs."""
    folded = _fold(body)
    hits = []
    for slug, meta in chars.items():
        if slug == owning:
            continue
        n = len(meta["full_rx"].findall(folded))
        if meta["multi"]:
            n += len(re.findall(rf"\b{re.escape(meta['display'])}\b", body))
        if n:
            hits.append((slug, n))
    return hits


def _add_char_hub(G: nx.DiGraph, char: str) -> None:
    G.add_node(f"char:{char}", type="character_hub", label=char)


def _add_body_edges(G, rel, body, slug_patterns, chars, owning) -> None:
    """Layer 2 edges for one file. Frontmatter edges (added first) win — an existing
    (rel, dst) edge is never downgraded to a lower-confidence body edge."""
    for ref_node, conf, n in _scan_body_references(body, slug_patterns):
        if G.has_edge(rel, ref_node):
            continue
        G.add_edge(rel, ref_node, rel_type="cites_theory", confidence=conf,
                   source="body_text", mention_count=n)
    for slug, n in _scan_body_for_characters(body, owning, chars):
        dst = f"char:{slug}"
        if G.has_edge(rel, dst):
            continue
        _add_char_hub(G, slug)
        G.add_edge(rel, dst, rel_type="cross_character", confidence=_CONF_BODY_CHAR,
                   source="body_text", mention_count=n)


def _build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    slug_patterns = _build_slug_patterns()
    chars = _corpus_characters()
    for base, node_type in ((PROFILES, "profile"), (MATERIALS, "material"),
                            (REFERENCES, "reference")):
        if not base.exists():
            continue
        for f in sorted(base.rglob("*.md")):
            if node_type == "reference" and f.name == "INDEX.md":
                continue
            rel = str(f.relative_to(paths.ROOT))
            fm, text = _frontmatter(f)
            attrs = {"type": node_type, "file": rel, "token_count": _token_estimate(text)}
            if node_type == "profile":
                attrs.update(character=fm.get("character", ""), domain=fm.get("domain", ""))
            elif node_type == "material":
                attrs.update(character=fm.get("character", ""),
                             evidence_tier=fm.get("evidence_tier", ""))
            elif node_type == "reference":
                attrs["slug"] = f.stem
            G.add_node(rel, **attrs)

            char = fm.get("character", "")
            if char and node_type in ("profile", "material"):
                _add_char_hub(G, char)
                G.add_edge(rel, f"char:{char}", rel_type="belongs_to",
                           confidence=0.95, source="frontmatter")
            for cc in _parse_yaml_list(fm.get("cross_characters")):
                _add_char_hub(G, cc)
                G.add_edge(rel, f"char:{cc}", rel_type="cross_character",
                           confidence=0.95, source="frontmatter")
            for ref in _parse_yaml_list(fm.get("references")):
                G.add_edge(rel, f"docs/references/{ref}.md", rel_type="cites_theory",
                           confidence=0.95, source="frontmatter")

            # Layer 2: scan body text of character-owned files (not theory references).
            if node_type in ("profile", "material"):
                _add_body_edges(G, rel, _strip_frontmatter(text), slug_patterns,
                                chars, _owning_char(rel))

    if GRAPH.exists():
        for f in sorted(GRAPH.rglob("*.md")):
            rel = str(f.relative_to(paths.ROOT))
            fm, text = _frontmatter(f)
            G.add_node(rel, type="graph_dyad", file=rel, token_count=_token_estimate(text))
            dyad_chars = _parse_yaml_list(fm.get("characters")) or _parse_yaml_list(fm.get("cross_characters"))
            for c in dyad_chars:
                _add_char_hub(G, c)
                G.add_edge(rel, f"char:{c}", rel_type="dyad_member",
                           confidence=0.95, source="frontmatter")
            # Dyad files have no owning character — scan body for all characters.
            _add_body_edges(G, rel, _strip_frontmatter(text), slug_patterns, chars, "")
            for ref in _parse_yaml_list(fm.get("references")):
                G.add_edge(rel, f"docs/references/{ref}.md", rel_type="cites_theory",
                           confidence=0.95, source="frontmatter")
    return G


def get_graph(force_rebuild: bool = False) -> nx.DiGraph:
    """Process-singleton DiGraph. Rebuild on demand (rebuild is sub-second)."""
    global _graph_cache, _undirected_cache
    if _graph_cache is None or force_rebuild:
        _graph_cache = _build_graph()
        _undirected_cache = None  # invalidate projection alongside the directed graph
    return _graph_cache


def _undirected() -> nx.Graph:
    """Cached undirected projection — edges are meaningful both ways for ego queries,
    and to_undirected() is too costly to repeat per call."""
    global _undirected_cache
    if _undirected_cache is None:
        _undirected_cache = get_graph().to_undirected(as_view=False)
    return _undirected_cache


def build_timed() -> tuple[nx.DiGraph, float]:
    """(graph, build_ms) — for benchmarking; always rebuilds."""
    t0 = time.perf_counter()
    G = _build_graph()
    return G, (time.perf_counter() - t0) * 1000


def graph_stats(G: nx.DiGraph | None = None) -> dict:
    G = G or get_graph()
    nodes_by_type: dict[str, int] = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "unknown")
        nodes_by_type[t] = nodes_by_type.get(t, 0) + 1
    edges_by_type: dict[str, int] = {}
    edges_by_source: dict[str, int] = {}
    for _, _, d in G.edges(data=True):
        r = d.get("rel_type", "unknown")
        edges_by_type[r] = edges_by_type.get(r, 0) + 1
        s = d.get("source", "unknown")
        edges_by_source[s] = edges_by_source.get(s, 0) + 1
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "nodes_by_type": dict(sorted(nodes_by_type.items(), key=lambda kv: -kv[1])),
        "edges_by_type": dict(sorted(edges_by_type.items(), key=lambda kv: -kv[1])),
        "edges_by_source": dict(sorted(edges_by_source.items(), key=lambda kv: -kv[1])),
    }


def validate_graph(G: nx.DiGraph | None = None) -> list[dict]:
    """Deterministic consistency issues: missing edge targets, orphan file nodes."""
    G = G or get_graph()
    issues = []
    for src, dst, d in G.edges(data=True):
        # add_edge auto-creates a bare placeholder node for a missing target, so a
        # broken cites_theory shows up as a target node lacking a "type" attribute.
        if d.get("rel_type") == "cites_theory" and not G.nodes[dst].get("type"):
            issues.append({"kind": "missing_reference", "from": src, "target": dst})
    for n, d in G.nodes(data=True):
        if d.get("type") in ("profile", "material") and G.degree(n) == 0:
            issues.append({"kind": "orphan", "node": n})
    return issues


# --- graph_context: the consumer-facing "find related files" API -------------

_TYPE_PRIORITY = {"profile": 0, "reference": 1, "material": 2, "graph_dyad": 3}
_TIER_RANK = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4}
_HUB_FILES = ("INDEX.md", "CURRENT-STATE.md")


def _resolve_entity(entity: str, G: nx.DiGraph) -> str | None:
    """User input → graph node key. Accepts a node key, character slug, or file path."""
    if entity in G:
        return entity
    hub = f"char:{entity}"
    if hub in G:
        return hub
    for cand in (f"{entity}.md", f"docs/references/{entity}.md"):
        if cand in G:
            return cand
    return None


def _priority_key(node: str, attrs: dict, dist: int, center: str | None) -> tuple:
    """Sort key. When querying a character, that character's own files + cited theory
    references group ahead of other characters' files (dense cross_character edges
    otherwise crowd them out under max_files). Then: 1-hop before far; type
    (profile<ref<material<dyad); INDEX/CURRENT-STATE float up; materials by tier."""
    t = attrs.get("type")
    if center is None:
        group = 0
    elif t == "reference":
        group = 0  # cited theories are character-agnostic — keep them prominent
    else:
        group = 0 if _owning_char(node) == center else 1
    far = 1 if dist > 1 else 0
    type_rank = _TYPE_PRIORITY.get(t, 5)
    hub_boost = 0 if node.rsplit("/", 1)[-1] in _HUB_FILES else 1
    tier = _TIER_RANK.get(attrs.get("evidence_tier", ""), 9)
    return (group, far, type_rank, hub_boost, tier, node)


def graph_context(entity: str, hops: int = 2, node_types=None,
                  max_files: int = 50) -> dict:
    """Primary cross-file discovery API for LLM skills — replaces glob/grep for
    relationship queries. Returns priority-ordered markdown paths within `hops` of
    `entity` plus a token-budget estimate. Unknown entity → empty result (no raise).
    hops is clamped to [1, 3]; max_files caps the (post-sort) list."""
    G = get_graph()
    root = _resolve_entity(entity, G)
    if root is None:
        return {"entity": entity, "files": [], "summary": "Entity not found",
                "token_estimate": 0, "node_count": 0, "edge_count": 0}
    radius = min(max(hops, 1), 3)
    center = root[len("char:"):] if root.startswith("char:") else None
    ego = nx.ego_graph(_undirected(), root, radius=radius)
    dist = nx.single_source_shortest_path_length(ego, root, cutoff=radius)
    allowed = set(node_types) if node_types else None

    candidates = []
    for n, a in ego.nodes(data=True):
        t = a.get("type")
        if t is None or t == "character_hub":  # synthetic hubs are not files
            continue
        if allowed and t not in allowed:
            continue
        candidates.append((n, a, dist.get(n, radius)))
    candidates.sort(key=lambda c: _priority_key(c[0], c[1], c[2], center))

    files = [n for n, _, _ in candidates][:max_files]
    token_estimate = sum(ego.nodes[n].get("token_count", 500) for n in files)
    breakdown = Counter(ego.nodes[n].get("type") for n in files)
    parts = ", ".join(f"{v} {k}{'s' if v != 1 else ''}" for k, v in breakdown.most_common())
    return {
        "entity": root,
        "files": files,
        "summary": f"{len(files)} files within {radius} hops ({parts})" if files
                   else f"No files within {radius} hops",
        "token_estimate": token_estimate,
        "node_count": ego.number_of_nodes(),
        "edge_count": ego.number_of_edges(),
    }
