"""Knowledge graph (Layer 1: frontmatter edges) — NetworkX DiGraph over the corpus.

Builds a deterministic "find related files" graph from markdown frontmatter:
profiles, materials, references, graph dyads → nodes; `character`, `cross_characters`,
`references`, `characters` fields → typed edges. In-memory, process-singleton, rebuilt
on demand. Markdown is the source of truth; the graph is derived + disposable.

Layer 1 only (frontmatter, confidence 0.95). Layer 2 (slug-regex body scan) and
Layer 3 (embedding) extend `_build_graph` in later phases. No existing skill imports
this yet — opt-in adoption.

Frontmatter is parsed with `yaml.safe_load` (NOT markdown_parser.extract_frontmatter,
which drops multi-line YAML lists — the field shape this graph depends on).
"""
from __future__ import annotations

import re
import time

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


def _add_char_hub(G: nx.DiGraph, char: str) -> None:
    G.add_node(f"char:{char}", type="character_hub", label=char)


def _build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
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

    if GRAPH.exists():
        for f in sorted(GRAPH.rglob("*.md")):
            rel = str(f.relative_to(paths.ROOT))
            fm, text = _frontmatter(f)
            G.add_node(rel, type="graph_dyad", file=rel, token_count=_token_estimate(text))
            chars = _parse_yaml_list(fm.get("characters")) or _parse_yaml_list(fm.get("cross_characters"))
            for c in chars:
                _add_char_hub(G, c)
                G.add_edge(rel, f"char:{c}", rel_type="dyad_member",
                           confidence=0.95, source="frontmatter")
            for ref in _parse_yaml_list(fm.get("references")):
                G.add_edge(rel, f"docs/references/{ref}.md", rel_type="cites_theory",
                           confidence=0.95, source="frontmatter")
    return G


def get_graph(force_rebuild: bool = False) -> nx.DiGraph:
    """Process-singleton DiGraph. Rebuild on demand (rebuild is sub-second)."""
    global _graph_cache
    if _graph_cache is None or force_rebuild:
        _graph_cache = _build_graph()
    return _graph_cache


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
    for _, _, d in G.edges(data=True):
        r = d.get("rel_type", "unknown")
        edges_by_type[r] = edges_by_type.get(r, 0) + 1
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "nodes_by_type": dict(sorted(nodes_by_type.items(), key=lambda kv: -kv[1])),
        "edges_by_type": dict(sorted(edges_by_type.items(), key=lambda kv: -kv[1])),
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
