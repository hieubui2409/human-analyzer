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
    mod._graph_cache = None
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
    assert mod._fold("Nhân vật A") == "bui trung hieu"
    assert mod._fold("Đặng Hoà") == "dang hoa"


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
    import re as _re
    from platform_lib import knowledge_graph as mod
    chars = {"character-b": {
        "full_rx": _re.compile(r"\bhoang[\s\-]+cong[\s\-]+hoa\b"),
        "display": "Nhân vật B", "multi": True}}
    # 'hóa' (common VN word) folds to 'hoa' but must NOT match the proper-noun short name.
    assert mod._scan_body_for_characters("văn hóa biến hóa hợp lý", "alpha", chars) == []
    assert mod._scan_body_for_characters("anh Nhân vật B nói", "alpha", chars) == [("character-b", 1)]
    assert mod._scan_body_for_characters("anh Nhân vật B nói", "character-b", chars) == []  # self skip


def test_stats_reports_edges_by_source(kg):
    mod, root = kg
    _w(root, "docs/references/complex-ptsd.md", "# x")
    _w(root, "docs/profiles/alpha/darkness/t.md",
       "---\ncharacter: alpha\n---\nComplex PTSD here.")
    G = mod.get_graph(force_rebuild=True)
    s = mod.graph_stats(G)
    assert s["edges_by_source"].get("body_text", 0) >= 1
    assert s["edges_by_source"].get("frontmatter", 0) >= 1  # belongs_to alpha
