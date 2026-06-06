"""KG Phase 1 — platform_lib.knowledge_graph Layer 1 (frontmatter edges).

Isolated: module-level PROFILES/MATERIALS/REFERENCES/GRAPH repointed at a tmp
fixture corpus + paths.ROOT patched so relative keys resolve. No real repo dep.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))


@pytest.fixture
def kg(monkeypatch, tmp_path):
    from platform_lib import knowledge_graph as mod
    from platform_lib import paths as paths_mod
    monkeypatch.setattr(paths_mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "PROFILES", tmp_path / "docs" / "profiles")
    monkeypatch.setattr(mod, "MATERIALS", tmp_path / "docs" / "materials")
    monkeypatch.setattr(mod, "REFERENCES", tmp_path / "docs" / "references")
    monkeypatch.setattr(mod, "GRAPH", tmp_path / "docs" / "graph")
    return mod, tmp_path


def _w(root: Path, rel: str, body: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def test_parse_yaml_list_forms():
    from platform_lib import knowledge_graph as mod
    assert mod._parse_yaml_list(["a", "b"]) == ["a", "b"]
    assert mod._parse_yaml_list("[x, y]") == ["x", "y"]
    assert mod._parse_yaml_list("solo") == ["solo"]
    assert mod._parse_yaml_list(None) == []
    assert mod._parse_yaml_list("[]") == []


def test_multiline_yaml_references_captured(kg):
    mod, root = kg
    # Multi-line YAML list — the exact shape extract_frontmatter drops.
    _w(root, "docs/profiles/alpha/psychology/formulation.md",
       "---\ncharacter: alpha\ndomain: psychology\nreferences:\n  - complex-ptsd\n  - attachment-theory\n---\nbody")
    _w(root, "docs/references/complex-ptsd.md", "# Complex PTSD")
    _w(root, "docs/references/attachment-theory.md", "# Attachment")
    G = mod.get_graph(force_rebuild=True)
    cites = [(s, d) for s, d, x in G.edges(data=True) if x["rel_type"] == "cites_theory"]
    targets = {d for _, d in cites}
    assert "docs/references/complex-ptsd.md" in targets
    assert "docs/references/attachment-theory.md" in targets  # multi-line item not dropped


def test_node_and_edge_types(kg):
    mod, root = kg
    _w(root, "docs/profiles/alpha/identity/core.md",
       "---\ncharacter: alpha\ncross_characters: [beta]\n---\nx")
    _w(root, "docs/materials/alpha/src.md", "---\ncharacter: alpha\nevidence_tier: T1\n---\nx")
    _w(root, "docs/references/savior-complex.md", "# Savior")
    _w(root, "docs/graph/alpha-beta.md", "---\ncharacters: [alpha, beta]\n---\nx")
    G = mod.get_graph(force_rebuild=True)
    stats = mod.graph_stats(G)
    assert stats["nodes_by_type"]["profile"] == 1
    assert stats["nodes_by_type"]["material"] == 1
    assert stats["nodes_by_type"]["reference"] == 1
    assert stats["nodes_by_type"]["graph_dyad"] == 1
    assert stats["nodes_by_type"]["character_hub"] == 2  # alpha + beta
    rels = stats["edges_by_type"]
    assert rels.get("belongs_to") == 2       # profile + material → alpha
    assert rels.get("cross_character") == 1  # core → beta
    assert rels.get("dyad_member") == 2      # dyad → alpha, beta


def test_index_md_skipped_in_references(kg):
    mod, root = kg
    _w(root, "docs/references/INDEX.md", "# catalog")
    _w(root, "docs/references/real-theory.md", "# theory")
    G = mod.get_graph(force_rebuild=True)
    assert "docs/references/real-theory.md" in G
    assert "docs/references/INDEX.md" not in G


def test_validate_detects_missing_reference(kg):
    mod, root = kg
    _w(root, "docs/profiles/alpha/psychology/x.md",
       "---\ncharacter: alpha\nreferences: [ghost-theory]\n---\nx")
    G = mod.get_graph(force_rebuild=True)
    issues = mod.validate_graph(G)
    miss = [i for i in issues if i["kind"] == "missing_reference"]
    assert any(i["target"] == "docs/references/ghost-theory.md" for i in miss)


def test_token_count_on_nodes(kg):
    mod, root = kg
    _w(root, "docs/profiles/alpha/identity/core.md",
       "---\ncharacter: alpha\n---\none two three four five")
    G = mod.get_graph(force_rebuild=True)
    n = G.nodes["docs/profiles/alpha/identity/core.md"]
    assert n["token_count"] > 0


def test_get_graph_singleton_and_rebuild(kg):
    mod, root = kg
    _w(root, "docs/references/a.md", "# a")
    g1 = mod.get_graph(force_rebuild=True)
    g2 = mod.get_graph()
    assert g1 is g2  # cached
    _w(root, "docs/references/b.md", "# b")
    g3 = mod.get_graph(force_rebuild=True)
    assert "docs/references/b.md" in g3


# --- Phase 2: Layer 2 body-text scanning -------------------------------------

def test_fold_strips_vietnamese_diacritics():
    from platform_lib import knowledge_graph as mod
    # Verify _fold on arbitrary Vietnamese phrases with various diacritic classes
    assert mod._fold("Đặng Hoà") == "dang hoa"
    assert mod._fold("Nguyễn Văn An") == "nguyen van an"
    assert mod._fold("Phạm Thị Bích") == "pham thi bich"


def test_body_multitoken_slug_one_mention_065(kg):
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# Complex PTSD")
    _w(root, "docs/profiles/alpha/darkness/traumas.md",
       "---\ncharacter: alpha\n---\nShe shows clear Complex PTSD patterns.")
    G = mod.get_graph(force_rebuild=True)
    e = G.get_edge_data("docs/profiles/alpha/darkness/traumas.md",
                        "docs/references/complex-ptsd.md")
    assert e["source"] == "body_text"
    assert e["rel_type"] == "cites_theory"
    assert e["confidence"] == 0.65  # multi-token, single mention
    assert e["mention_count"] == 1


def test_body_two_mentions_080(kg):
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# x")
    _w(root, "docs/profiles/alpha/darkness/t.md",
       "---\ncharacter: alpha\n---\nComplex PTSD. Later: complex-ptsd again.")
    G = mod.get_graph(force_rebuild=True)
    e = G.get_edge_data("docs/profiles/alpha/darkness/t.md",
                        "docs/references/complex-ptsd.md")
    assert e["mention_count"] == 2 and e["confidence"] == 0.80


def test_single_token_slug_needs_two_mentions(kg):
    mod, root = kg
    _w(root, "docs/references/transference.md", "# Transference")
    p = "docs/profiles/alpha/psychology/x.md"
    _w(root, p, "---\ncharacter: alpha\n---\nHe felt transference once.")
    G = mod.get_graph(force_rebuild=True)
    assert not G.has_edge(p, "docs/references/transference.md")  # 1 mention dropped
    _w(root, p, "---\ncharacter: alpha\n---\nTransference, then more transference.")
    G = mod.get_graph(force_rebuild=True)
    e = G.get_edge_data(p, "docs/references/transference.md")
    assert e["mention_count"] == 2 and e["confidence"] == 0.80


def test_frontmatter_edge_not_downgraded_by_body(kg):
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# x")
    _w(root, "docs/profiles/alpha/psychology/f.md",
       "---\ncharacter: alpha\nreferences: [complex-ptsd]\n---\nComplex PTSD complex ptsd")
    G = mod.get_graph(force_rebuild=True)
    e = G.get_edge_data("docs/profiles/alpha/psychology/f.md",
                        "docs/references/complex-ptsd.md")
    assert e["source"] == "frontmatter" and e["confidence"] == 0.95


def test_blacklisted_slug_ignored_in_body(kg):
    mod, root = kg
    _w(root, "docs/references/displacement.md", "# Displacement")
    p = "docs/profiles/alpha/psychology/d.md"
    _w(root, p, "---\ncharacter: alpha\n---\nDisplacement displacement displacement.")
    G = mod.get_graph(force_rebuild=True)
    assert not G.has_edge(p, "docs/references/displacement.md")


def test_reference_body_not_scanned_for_slugs(kg):
    # Theory files must not cite each other from prose (only character-owned files scan).
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# Complex PTSD\nrelated to Complex PTSD.")
    _w(root, "docs/references/savior-complex.md", "# Savior\nSee Complex PTSD too.")
    G = mod.get_graph(force_rebuild=True)
    assert not G.has_edge("docs/references/savior-complex.md",
                          "docs/references/complex-ptsd.md")


def test_cross_character_body_edge(kg):
    mod, root = kg
    _w(root, "docs/profiles/alpha/identity/core.md", "---\ncharacter: alpha\n---\nx")
    _w(root, "docs/profiles/beta/identity/core.md", "---\ncharacter: beta\n---\nx")
    p = "docs/profiles/alpha/relationships/network.md"
    _w(root, p, "---\ncharacter: alpha\n---\nAlpha works with beta, often beta.")
    G = mod.get_graph(force_rebuild=True)
    e = G.get_edge_data(p, "char:beta")
    assert e["rel_type"] == "cross_character"
    assert e["source"] == "body_text" and e["confidence"] == 0.70
    # own character: only the frontmatter belongs_to edge, never a body self cross-link
    assert G.get_edge_data(p, "char:alpha")["rel_type"] == "belongs_to"


def test_short_name_diacritic_no_false_positive():
    """Verify _scan_body_for_characters distinguishes a diacriticed display name from
    common Vietnamese words that fold to the same ASCII form."""
    import re as _re
    from platform_lib import knowledge_graph as mod
    # Use a synthetic display name "Bảo" — folds to "bao".
    # Common VN words "bao giờ", "bao nhiêu" fold to "bao" but must NOT trigger a match.
    chars = {"synthetic-bao": {
        "full_rx": _re.compile(r"\bsynthetic[\s\-]+bao\b"),
        "display": "Bảo", "multi": True}}
    # Common words that fold to 'bao' must not match the proper-noun display name
    assert mod._scan_body_for_characters("bao giờ bao nhiêu bao xa", "alpha", chars) == []
    assert mod._scan_body_for_characters("anh Bảo nói", "alpha", chars) == [("synthetic-bao", 1)]
    assert mod._scan_body_for_characters("anh Bảo nói", "synthetic-bao", chars) == []  # self skip


def test_stats_reports_edges_by_source(kg):
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# x")
    _w(root, "docs/profiles/alpha/darkness/t.md",
       "---\ncharacter: alpha\n---\nComplex PTSD here.")
    G = mod.get_graph(force_rebuild=True)
    s = mod.graph_stats(G)
    assert s["edges_by_source"].get("body_text", 0) >= 1
    assert s["edges_by_source"].get("frontmatter", 0) >= 1  # belongs_to alpha


# --- Phase 3a: graph_context API ---------------------------------------------

def _seed_character(root, char="alpha"):
    _w(root, f"docs/profiles/{char}/INDEX.md", f"---\ncharacter: {char}\n---\nidx")
    _w(root, f"docs/profiles/{char}/CURRENT-STATE.md", f"---\ncharacter: {char}\n---\nnow")
    _w(root, f"docs/profiles/{char}/psychology/formulation.md",
       f"---\ncharacter: {char}\nreferences: [complex-ptsd]\n---\nbody")
    _w(root, "docs/references/complex-ptsd.md", "# Complex PTSD")
    _w(root, f"docs/materials/{char}/src.md",
       f"---\ncharacter: {char}\nevidence_tier: T1\n---\nx")


def test_graph_context_character_query(kg):
    mod, root = kg
    _seed_character(root)
    mod.get_graph(force_rebuild=True)
    r = mod.graph_context("alpha")
    assert r["entity"] == "char:alpha"
    assert "docs/profiles/alpha/INDEX.md" in r["files"]
    assert "docs/profiles/alpha/psychology/formulation.md" in r["files"]
    assert r["token_estimate"] > 0 and r["node_count"] > 0


def test_graph_context_unknown_entity(kg):
    mod, root = kg
    _w(root, "docs/references/a.md", "# a")
    mod.get_graph(force_rebuild=True)
    r = mod.graph_context("nobody")
    assert r["files"] == [] and r["token_estimate"] == 0
    assert r["summary"] == "Entity not found"


def test_graph_context_node_types_filter(kg):
    mod, root = kg
    _seed_character(root)
    mod.get_graph(force_rebuild=True)
    r = mod.graph_context("alpha", node_types=["reference"])
    G = mod.get_graph()
    assert r["files"] and all(G.nodes[f]["type"] == "reference" for f in r["files"])
    assert "docs/references/complex-ptsd.md" in r["files"]


def test_graph_context_hops_clamped_to_three(kg):
    mod, root = kg
    _seed_character(root)
    mod.get_graph(force_rebuild=True)
    assert set(mod.graph_context("alpha", hops=5)["files"]) == \
           set(mod.graph_context("alpha", hops=3)["files"])


def test_resolve_entity_forms(kg):
    mod, root = kg
    _seed_character(root)
    G = mod.get_graph(force_rebuild=True)
    assert mod._resolve_entity("alpha", G) == "char:alpha"
    assert mod._resolve_entity("char:alpha", G) == "char:alpha"
    assert mod._resolve_entity("complex-ptsd", G) == "docs/references/complex-ptsd.md"
    assert mod._resolve_entity("docs/profiles/alpha/INDEX.md", G) == "docs/profiles/alpha/INDEX.md"
    assert mod._resolve_entity("ghost", G) is None


def test_graph_context_hub_files_first(kg):
    mod, root = kg
    _seed_character(root)
    mod.get_graph(force_rebuild=True)
    r = mod.graph_context("alpha", hops=1)
    assert r["files"][0].rsplit("/", 1)[-1] in ("INDEX.md", "CURRENT-STATE.md")


def test_graph_context_owning_character_ranked_first(kg):
    mod, root = kg
    _seed_character(root, "alpha")
    _seed_character(root, "beta")
    # link the two so beta files enter alpha's ego subgraph
    _w(root, "docs/profiles/alpha/relationships/beta.md",
       "---\ncharacter: alpha\ncross_characters: [beta]\n---\nx")
    mod.get_graph(force_rebuild=True)
    files = mod.graph_context("alpha")["files"]
    beta = [i for i, f in enumerate(files) if f.startswith("docs/profiles/beta/")]
    if beta:  # alpha's own INDEX must precede any beta profile
        assert files.index("docs/profiles/alpha/INDEX.md") < min(beta)


def test_graph_context_max_files_cap(kg):
    mod, root = kg
    for i in range(8):
        _w(root, f"docs/profiles/alpha/psychology/f{i}.md", "---\ncharacter: alpha\n---\nx")
    mod.get_graph(force_rebuild=True)
    assert len(mod.graph_context("alpha", max_files=3)["files"]) == 3


# test_undirected_projection_invalidated_on_rebuild — DELETED: _undirected() removed
# when knowledge_graph was minimized (networkx + embedding modules removed). The
# undirected-projection cache is no longer part of the public API.

# test_embedding_layer_is_firm_only — DELETED: knowledge_graph_embeddings module
# was deleted in the KG minimization. Layer-3 (embedding edges) no longer exists.
