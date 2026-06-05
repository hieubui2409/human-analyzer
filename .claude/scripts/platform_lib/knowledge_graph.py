"""Knowledge graph (Layer 1+2: frontmatter + body-scan edges) — plain Python adjacency
over the markdown corpus. No networkx/numpy/pyvis dependency.

Builds a deterministic "find related files" graph from markdown frontmatter:
profiles, materials, references, graph dyads → nodes; `character`, `cross_characters`,
`references`, `characters` fields → typed edges. In-memory, process-singleton, rebuilt
on demand. Markdown is the source of truth; the graph is derived + disposable.

Layer 1: frontmatter (confidence 0.95). Layer 2: slug-first regex body scan —
reference stems matched against body text (cites_theory) + character names matched
cross-file (cross_character), confidence 0.65-0.80. No Layer 3 (embedding removed).

Characters are resolved dynamically from the profiles directory (never hardcoded);
short-name matching uses paths.CHAR_DISPLAY for the diacritic proper-noun form.

Frontmatter is parsed with `yaml.safe_load` (NOT markdown_parser.extract_frontmatter,
which drops multi-line YAML lists — the field shape this graph depends on).
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import yaml

from . import paths

# Module-level dir handles, monkeypatchable in tests.
PROFILES = paths.PROFILES
MATERIALS = paths.MATERIALS
REFERENCES = paths.REFERENCES
GRAPH = paths.GRAPH

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_graph_cache: "Graph | None" = None

# Single-token reference slugs that are also generic English homographs: even with
# repeated mentions their bare appearance is unreliable signal, so drop them entirely
# from body scanning. Multi-token and clinical-jargon single-token slugs are kept.
_SLUG_FP_BLACKLIST = frozenset({"anchoring", "deflection", "displacement"})

# Confidence tiers for Layer 2 body-text edges.
_CONF_BODY_MULTI = 0.80   # slug seen 2+ times
_CONF_BODY_SINGLE = 0.65  # slug seen once (multi-token slugs only)
_CONF_BODY_CHAR = 0.70    # character name seen in another character's file


# ---------------------------------------------------------------------------
# Plain-Python graph structure (replaces networkx DiGraph)
# ---------------------------------------------------------------------------

@dataclass
class Graph:
    """Directed adjacency graph. Edges stored as adjacency dict for fast lookup.
    nodes: {node_id -> attrs dict}
    adj:   {src -> {dst -> edge_attrs dict}}   (directed)
    """
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    adj: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)

    def add_node(self, node: str, **attrs) -> None:
        if node not in self.nodes:
            self.nodes[node] = {}
            self.adj[node] = {}
        self.nodes[node].update(attrs)

    def add_edge(self, src: str, dst: str, **attrs) -> None:
        if src not in self.nodes:
            self.nodes[src] = {}
            self.adj[src] = {}
        if dst not in self.nodes:
            self.nodes[dst] = {}
            self.adj[dst] = {}
        self.adj[src][dst] = attrs

    def has_edge(self, src: str, dst: str) -> bool:
        return dst in self.adj.get(src, {})

    def number_of_nodes(self) -> int:
        return len(self.nodes)

    def number_of_edges(self) -> int:
        return sum(len(dsts) for dsts in self.adj.values())

    def edges(self, data: bool = False):
        """Yield (src, dst) or (src, dst, attrs) tuples."""
        for src, dsts in self.adj.items():
            for dst, attrs in dsts.items():
                yield (src, dst, attrs) if data else (src, dst)

    def out_edges(self, node: str, data: bool = False):
        for dst, attrs in self.adj.get(node, {}).items():
            yield (node, dst, attrs) if data else (node, dst)

    def degree(self, node: str) -> int:
        """Total in+out degree."""
        out = len(self.adj.get(node, {}))
        in_ = sum(1 for dsts in self.adj.values() if node in dsts)
        return out + in_

    def neighbors_undirected(self, node: str) -> set[str]:
        """All nodes connected to `node` in either direction."""
        result: set[str] = set(self.adj.get(node, {}).keys())
        for src, dsts in self.adj.items():
            if node in dsts:
                result.add(src)
        return result

    def get_edge_data(self, src: str, dst: str) -> dict | None:
        """Return edge attrs dict for (src, dst) or None if absent (mirrors networkx API)."""
        return self.adj.get(src, {}).get(dst)

    def __contains__(self, node: str) -> bool:
        """Support `node in G` membership test (mirrors networkx DiGraph)."""
        return node in self.nodes


# ---------------------------------------------------------------------------
# BFS ego-subgraph (replaces nx.ego_graph + nx.single_source_shortest_path_length)
# ---------------------------------------------------------------------------

def _bfs_ego(G: Graph, root: str, radius: int) -> tuple[Graph, dict[str, int]]:
    """BFS over the undirected projection of G within `radius` hops.
    Returns (ego_subgraph, {node: shortest_distance})."""
    visited: dict[str, int] = {root: 0}
    queue = [root]
    while queue:
        cur = queue.pop(0)
        cur_dist = visited[cur]
        if cur_dist >= radius:
            continue
        for nb in G.neighbors_undirected(cur):
            if nb not in visited:
                visited[nb] = cur_dist + 1
                queue.append(nb)

    ego = Graph()
    for n in visited:
        ego.add_node(n, **G.nodes.get(n, {}))
    # Copy directed edges within the ego subgraph
    for src in visited:
        for dst, attrs in G.adj.get(src, {}).items():
            if dst in visited:
                ego.add_edge(src, dst, **attrs)
    return ego, visited


# ---------------------------------------------------------------------------
# Frontmatter + body parsing helpers
# ---------------------------------------------------------------------------

def _parse_yaml_list(val) -> list[str]:
    """Frontmatter array -> list[str]. Handles list / '[a, b]' / 'a' / None."""
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
    """Body text only -- drop a leading ---...--- frontmatter block if present."""
    m = _FM_RE.match(text)
    return text[m.end():] if m else text


_WS_HYPHEN_RE = re.compile(r"[\s\-]+")


def _build_slug_patterns() -> tuple[re.Pattern | None, dict[str, tuple[str, bool]]]:
    """(combined_rx, {slug: (ref_node, is_single_token)}). One alternation regex over
    all reference stems -> a single findall per body instead of 71 separate scans. Built
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
    (dynamic -- never a hardcoded character list). Diacritic short name from
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
    as the diacritic proper noun (case-sensitive) to avoid folding FPs."""
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


def _add_char_hub(G: Graph, char: str) -> None:
    G.add_node(f"char:{char}", type="character_hub", label=char)


def _add_body_edges(G: Graph, rel: str, body: str, slug_patterns, chars, owning: str) -> None:
    """Layer 2 edges for one file. Frontmatter edges (added first) win -- an existing
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


def _file_node_type(rel: str) -> str | None:
    """Node type implied by a markdown file's location (None if outside the graph corpus)."""
    if rel.startswith("docs/profiles/"):
        return "profile"
    if rel.startswith("docs/materials/"):
        return "material"
    if rel.startswith("docs/references/"):
        return "reference"
    if rel.startswith("docs/graph/"):
        return "graph_dyad"
    return None


def _scan_one(G: Graph, f, node_type: str, slug_patterns, chars) -> None:
    """Add one markdown file's node + its Layer 1 (frontmatter) and Layer 2 (body) edges."""
    rel = str(f.relative_to(paths.ROOT))
    fm, text = _frontmatter(f)
    attrs: dict[str, Any] = {"type": node_type, "file": rel, "token_count": _token_estimate(text)}
    if node_type == "profile":
        attrs.update(character=fm.get("character", ""), domain=fm.get("domain", ""))
    elif node_type == "material":
        attrs.update(character=fm.get("character", ""), evidence_tier=fm.get("evidence_tier", ""))
    elif node_type == "reference":
        attrs["slug"] = f.stem
    G.add_node(rel, **attrs)

    if node_type == "graph_dyad":
        for c in (_parse_yaml_list(fm.get("characters"))
                  or _parse_yaml_list(fm.get("cross_characters"))):
            _add_char_hub(G, c)
            G.add_edge(rel, f"char:{c}", rel_type="dyad_member", confidence=0.95,
                       source="frontmatter")
        _add_body_edges(G, rel, _strip_frontmatter(text), slug_patterns, chars, "")
    else:
        char = fm.get("character", "")
        if char and node_type in ("profile", "material"):
            _add_char_hub(G, char)
            G.add_edge(rel, f"char:{char}", rel_type="belongs_to", confidence=0.95,
                       source="frontmatter")
        for cc in _parse_yaml_list(fm.get("cross_characters")):
            _add_char_hub(G, cc)
            G.add_edge(rel, f"char:{cc}", rel_type="cross_character", confidence=0.95,
                       source="frontmatter")
        if node_type in ("profile", "material"):  # Layer 2: scan character-owned bodies
            _add_body_edges(G, rel, _strip_frontmatter(text), slug_patterns,
                            chars, _owning_char(rel))
    for ref in _parse_yaml_list(fm.get("references")):
        G.add_edge(rel, f"docs/references/{ref}.md", rel_type="cites_theory",
                   confidence=0.95, source="frontmatter")


def _corpus_md_files() -> list:
    """All markdown files that become graph nodes (profiles, materials, references, dyads),
    excluding the references INDEX. Sorted for deterministic builds."""
    out = []
    for base, ntype in ((PROFILES, "profile"), (MATERIALS, "material"),
                        (REFERENCES, "reference")):
        if base.exists():
            for f in sorted(base.rglob("*.md")):
                if ntype == "reference" and f.name == "INDEX.md":
                    continue
                out.append(f)
    if GRAPH.exists():
        out.extend(sorted(GRAPH.rglob("*.md")))
    return out


def _build_graph() -> Graph:
    G = Graph()
    slug_patterns = _build_slug_patterns()
    chars = _corpus_characters()
    for f in _corpus_md_files():
        rel = str(f.relative_to(paths.ROOT))
        ntype = _file_node_type(rel)
        if ntype is not None:
            _scan_one(G, f, ntype, slug_patterns, chars)
    return G


def get_graph(force_rebuild: bool = False) -> Graph:
    """Process-singleton plain adjacency graph. Small corpus (~200 nodes) -> always
    builds fresh in <1s; module-level memo is invalidated by force_rebuild.
    The heavy disk-cache/incremental-rebuild machinery has been removed (was tied
    to networkx serialization and the now-deleted embedding layer)."""
    global _graph_cache
    if _graph_cache is not None and not force_rebuild:
        return _graph_cache
    _graph_cache = _build_graph()
    return _graph_cache


def graph_stats(G: "Graph | None" = None) -> dict:
    """Return node/edge counts by type. `embedding_layer` key removed."""
    G = G or get_graph()
    nodes_by_type: dict[str, int] = {}
    for _, d in G.nodes.items():
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


def validate_graph(G: "Graph | None" = None) -> list[dict]:
    """Deterministic consistency issues: missing edge targets, orphan file nodes."""
    G = G or get_graph()
    issues = []
    for src, dst, d in G.edges(data=True):
        # add_edge auto-creates a bare placeholder node for a missing target, so a
        # broken cites_theory shows up as a target node lacking a "type" attribute.
        if d.get("rel_type") == "cites_theory" and not G.nodes[dst].get("type"):
            issues.append({"kind": "missing_reference", "from": src, "target": dst})
    for n, d in G.nodes.items():
        if d.get("type") in ("profile", "material") and G.degree(n) == 0:
            issues.append({"kind": "orphan", "node": n})
    return issues


# --- graph_context: the consumer-facing "find related files" API -------------

_TYPE_PRIORITY = {"profile": 0, "reference": 1, "material": 2, "graph_dyad": 3}
_TIER_RANK = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4}
_HUB_FILES = ("INDEX.md", "CURRENT-STATE.md")


def _resolve_entity(entity: str, G: Graph) -> str | None:
    """User input -> graph node key. Accepts a node key, character slug, or file path."""
    if entity in G.nodes:
        return entity
    hub = f"char:{entity}"
    if hub in G.nodes:
        return hub
    for cand in (f"{entity}.md", f"docs/references/{entity}.md"):
        if cand in G.nodes:
            return cand
    return None


def _priority_key(node: str, attrs: dict, dist: int, center: str | None) -> tuple:
    """Sort key. When querying a character, that character's own files + cited theory
    references group ahead of other characters' files. Then: 1-hop before far; type
    (profile<ref<material<dyad); INDEX/CURRENT-STATE float up; materials by tier."""
    t = attrs.get("type")
    if center is None:
        group = 0
    elif t == "reference":
        group = 0  # cited theories are character-agnostic -- keep them prominent
    else:
        group = 0 if _owning_char(node) == center else 1
    far = 1 if dist > 1 else 0
    type_rank = _TYPE_PRIORITY.get(t, 5)
    hub_boost = 0 if node.rsplit("/", 1)[-1] in _HUB_FILES else 1
    tier = _TIER_RANK.get(attrs.get("evidence_tier", ""), 9)
    return (group, far, type_rank, hub_boost, tier, node)


def graph_context(entity: str, hops: int = 2, node_types=None,
                  max_files: int = 50) -> dict:
    """Primary cross-file discovery API for LLM skills -- replaces glob/grep for
    relationship queries. Returns priority-ordered markdown paths within `hops` of
    `entity` plus a token-budget estimate. Unknown entity -> empty result (no raise).
    hops is clamped to [1, 3]; max_files caps the (post-sort) list."""
    G = get_graph()
    root = _resolve_entity(entity, G)
    if root is None:
        return {"entity": entity, "files": [], "summary": "Entity not found",
                "token_estimate": 0, "node_count": 0, "edge_count": 0}
    radius = min(max(hops, 1), 3)
    center = root[len("char:"):] if root.startswith("char:") else None
    ego, dist = _bfs_ego(G, root, radius)
    allowed = set(node_types) if node_types else None

    candidates = []
    for n, a in ego.nodes.items():
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
