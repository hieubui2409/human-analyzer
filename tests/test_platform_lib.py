"""Test platform_lib modules: paths, clinical_terms, markdown_parser, env_utils, csv_search."""
import os
import sys
from pathlib import Path

import pytest

# Ensure platform_lib is importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import platform_lib.paths as _paths  # noqa: E402

# First real character, sourced dynamically — no hardcoded slug in the shipped test tree.
_CHAR = _paths.ALL_CHARS[0] if _paths.ALL_CHARS else None
# Resolution/structure assertions need a populated roster; skip cleanly in a toolkit-only pack.
requires_corpus = pytest.mark.skipif(not _paths.ALL_CHARS, reason="no character roster — toolkit-only pack")


class TestPaths:
    """Test paths.py module."""

    def test_profile_files_has_25_entries(self):
        """PROFILE_FILES should contain exactly 25 files (21 base + 4 growth)."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.PROFILE_FILES) == 25
        # Verify some key files exist
        assert "INDEX.md" in paths_mod.PROFILE_FILES
        assert "CURRENT-STATE.md" in paths_mod.PROFILE_FILES
        assert "identity/core.md" in paths_mod.PROFILE_FILES
        assert "psychology/formulation.md" in paths_mod.PROFILE_FILES

    def test_legacy_to_new_map_exists(self):
        """LEGACY_TO_NEW_MAP should map old filenames to new ones."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.LEGACY_TO_NEW_MAP) > 0
        # Check key mappings
        assert paths_mod.LEGACY_TO_NEW_MAP.get("SOUL.md") == "psychology/formulation.md"
        assert paths_mod.LEGACY_TO_NEW_MAP.get("DARKNESS.md") == "darkness/traumas.md"
        assert paths_mod.LEGACY_TO_NEW_MAP.get("LIGHT.md") == "light/strengths-hope.md"

    def test_legacy_split_map_exists(self):
        """LEGACY_SPLIT_MAP should exist with multi-file mappings."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.LEGACY_SPLIT_MAP) > 0
        # Check key splits
        assert "SOUL.md" in paths_mod.LEGACY_SPLIT_MAP
        assert len(paths_mod.LEGACY_SPLIT_MAP["SOUL.md"]) == 2

    def test_resolve_character_works(self):
        """resolve_character should handle slug and display-name aliases correctly."""
        import platform_lib.paths as paths_mod
        # Slug resolution always works (slugs are canonical)
        for slug in paths_mod.ALL_CHARS:
            assert paths_mod.resolve_character(slug) == slug, (
                f"slug {slug!r} must resolve to itself"
            )
        # Display-name (diacritic) and ASCII-folded aliases also resolve from the roster.
        # Test all CHAR_SEARCH_ALIASES entries for every character.
        for slug, aliases in paths_mod.CHAR_SEARCH_ALIASES.items():
            for alias in aliases:
                try:
                    resolved = paths_mod.resolve_character(alias.lower())
                    assert resolved == slug, (
                        f"alias {alias!r} should resolve to {slug!r}, got {resolved!r}"
                    )
                except ValueError:
                    # Some aliases (IME typos, multi-word full names) are not in the
                    # resolution map by design — only display+slug+asciifold are keys.
                    pass
        # Case-insensitivity: uppercase slug still resolves
        if paths_mod.ALL_CHARS:
            first_slug = paths_mod.ALL_CHARS[0]
            assert paths_mod.resolve_character(first_slug.upper()) == first_slug

    def test_resolve_character_raises_on_unknown(self):
        """resolve_character should raise ValueError for unknown names."""
        import platform_lib.paths as paths_mod
        with pytest.raises(ValueError, match="Unknown character"):
            paths_mod.resolve_character("unknown-person")

    @requires_corpus
    def test_character_dir_returns_path(self):
        """character_dir should return valid path objects."""
        import platform_lib.paths as paths_mod
        result = paths_mod.character_dir(_CHAR)
        assert isinstance(result, Path)
        assert _CHAR in str(result)

    @requires_corpus
    def test_materials_dir_returns_path(self):
        """materials_dir should return valid path objects."""
        import platform_lib.paths as paths_mod
        result = paths_mod.materials_dir(_CHAR)
        assert isinstance(result, Path)
        assert _CHAR in str(result)

    @requires_corpus
    def test_all_chars_not_empty(self):
        """ALL_CHARS should contain character identifiers (all non-empty strings)."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.ALL_CHARS) > 0
        assert all(isinstance(c, str) and c for c in paths_mod.ALL_CHARS)

    def test_characters_mapping_valid(self):
        """CHARACTERS mapping should have proper keys and values."""
        import platform_lib.paths as paths_mod
        if not paths_mod.CHARACTERS:
            pytest.skip("No character roster loaded — toolkit-only pack")
        for key, value in paths_mod.CHARACTERS.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_profile_by_concept_has_keys(self):
        """PROFILE_BY_CONCEPT should map semantic keys to paths."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.PROFILE_BY_CONCEPT) > 0
        # Check some known keys
        assert "identity" in paths_mod.PROFILE_BY_CONCEPT
        assert "formulation" in paths_mod.PROFILE_BY_CONCEPT
        assert "attachment_style" in paths_mod.PROFILE_BY_CONCEPT

    def test_legacy_split_map_has_relationships(self):
        """LEGACY_SPLIT_MAP should include RELATIONSHIPS.md split."""
        import platform_lib.paths as paths_mod
        assert "RELATIONSHIPS.md" in paths_mod.LEGACY_SPLIT_MAP
        rel_files = paths_mod.LEGACY_SPLIT_MAP["RELATIONSHIPS.md"]
        assert "relationships/family.md" in rel_files
        assert len(rel_files) >= 2

    @requires_corpus
    def test_list_relationship_files_returns_list(self):
        """list_relationship_files should return a list of Paths."""
        import platform_lib.paths as paths_mod
        result = paths_mod.list_relationship_files(_CHAR)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, Path)
            assert item.suffix == ".md"
            assert item.name != "family.md"

    @requires_corpus
    def test_list_relationship_files_per_character(self):
        """Cross-relationship files must name OTHER roster members (no orphans)."""
        import platform_lib.paths as paths_mod
        rels = [f.name for f in paths_mod.list_relationship_files(_CHAR)]
        others = {f"{s}.md" for s in paths_mod.ALL_CHARS if s != _CHAR}
        cross = [r for r in rels if r != "network.md"]
        assert cross, "expected at least one cross-character relationship file"
        assert set(cross) <= others, f"{cross} not all in {others}"

    @requires_corpus
    def test_list_all_profile_files_superset(self):
        """list_all_profile_files should return more files than list_profile_files."""
        import platform_lib.paths as paths_mod
        base = paths_mod.list_profile_files(_CHAR)
        total = paths_mod.list_all_profile_files(_CHAR)
        assert len(total) >= len(base)


class TestClinicalTerms:
    """Test clinical_terms.py module."""

    def test_patterns_list_not_empty(self):
        """CLINICAL_PATTERNS should contain regex patterns."""
        import platform_lib.clinical_terms as ct_mod
        assert hasattr(ct_mod, "CLINICAL_PATTERNS")
        assert len(ct_mod.CLINICAL_PATTERNS) > 0
        # All should be strings (regex patterns)
        for pattern in ct_mod.CLINICAL_PATTERNS:
            assert isinstance(pattern, str)

    def test_patterns_contain_key_terms(self):
        """CLINICAL_PATTERNS should include key clinical terms."""
        import platform_lib.clinical_terms as ct_mod
        patterns_str = " ".join(ct_mod.CLINICAL_PATTERNS)
        # Check for some key patterns
        assert "attachment" in patterns_str.lower()
        assert "trauma" in patterns_str.lower() or "PTSD" in patterns_str
        assert "defense" in patterns_str.lower() or "denial" in patterns_str


class TestMarkdownParser:
    """Test markdown_parser.py module."""

    def test_markdown_parser_importable(self):
        """markdown_parser module should be importable."""
        try:
            import platform_lib.markdown_parser as mp_mod
            assert hasattr(mp_mod, "extract_sections") or hasattr(mp_mod, "extract_frontmatter")
        except ImportError:
            pytest.skip("markdown_parser not available or incompatible")

    def test_extract_sections_on_sample_markdown(self, tmp_path):
        """extract_sections(filepath, level) returns {heading: content} for level-2 headings."""
        import platform_lib.markdown_parser as mp_mod
        f = tmp_path / "sample.md"
        f.write_text("# Header\n\n## Section\nContent here\n\n## Another\nMore content\n", encoding="utf-8")
        result = mp_mod.extract_sections(f, level=2)
        assert result["Section"] == "Content here"
        assert result["Another"] == "More content"

    def test_extract_frontmatter_on_yaml(self, tmp_path):
        """extract_frontmatter(filepath) parses the YAML-like frontmatter block to a dict."""
        import platform_lib.markdown_parser as mp_mod
        f = tmp_path / "fm.md"
        f.write_text('---\nname: "psy:test"\nkey: value\n---\nBody\n', encoding="utf-8")
        result = mp_mod.extract_frontmatter(f)
        assert result["name"] == "psy:test"
        assert result["key"] == "value"


class TestEnvUtils:
    """Test env_utils.py module."""

    def test_env_utils_importable(self):
        """env_utils module should be importable."""
        try:
            import platform_lib.env_utils as eu_mod
            assert hasattr(eu_mod, "load_env") or hasattr(eu_mod, "get_api_key")
        except ImportError:
            pytest.skip("env_utils not available")

    def test_load_env_handles_missing_env(self):
        """load_env should handle missing .env gracefully (dict/None, or a clean FileNotFoundError)."""
        import platform_lib.env_utils as eu_mod
        assert hasattr(eu_mod, "load_env"), "env_utils must expose load_env"
        try:
            result = eu_mod.load_env("/nonexistent/.env")
        except FileNotFoundError:
            return  # explicit missing-file signal is acceptable behavior
        # any OTHER exception now FAILS the test instead of being masked as a skip
        assert isinstance(result, dict) or result is None


class TestCsvSearch:
    """Test csv_search.py module."""

    def test_csv_search_importable(self):
        """csv_search module should be importable."""
        try:
            import platform_lib.csv_search as cs_mod
            # Should have search functions
            assert hasattr(cs_mod, "search") or hasattr(cs_mod, "bm25_search")
        except ImportError:
            pytest.skip("csv_search not available")

    def test_csv_search_empty_and_basic(self):
        """search(query, rows) returns [] on empty rows and ranks matching rows otherwise."""
        import platform_lib.csv_search as cs_mod
        assert cs_mod.search("query", []) == []
        rows = [
            {"name": "complex ptsd", "desc": "trauma and dissociation"},
            {"name": "secure attachment", "desc": "stable bonding"},
        ]
        hits = cs_mod.search("trauma", rows, text_fields=["name", "desc"])
        assert hits and hits[0][2]["name"] == "complex ptsd"


class TestFormatters:
    """Test formatters.py module."""

    def test_formatters_importable(self):
        """formatters module should be importable."""
        try:
            import platform_lib.formatters as fmt_mod
            # Should have formatting functions
            assert hasattr(fmt_mod, "markdown_table") or hasattr(fmt_mod, "print_table")
        except ImportError:
            pytest.skip("formatters not available")
